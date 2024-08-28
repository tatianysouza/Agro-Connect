from blue import app, db, login_manager, bcrypt, csrf
from flask import Flask, render_template, url_for, flash, redirect, session, send_from_directory, request
from flask_login import current_user, login_user, logout_user, login_required
import os
import time
from werkzeug.utils import secure_filename
from ..forms import RegistrationForm, LoginForm, CadastroProdutoForm
from ..models.tables import db, Usuario, Produto, TipoUsuario, StatusPedido, Pedido, ItemPedido
from datetime import datetime, timezone
from ..models.tables import TipoUsuario, db, Usuario, Produto

@app.context_processor
def inject_user_type():
    return {
        'tipo_usuario': current_user.tipo_usuario if current_user.is_authenticated else None,
        'TipoUsuario': TipoUsuario
    }

@app.context_processor
def inject_status_pagamento():
    return dict(StatusPedido=StatusPedido)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
def home():
    products = Produto.query.all()
    return render_template('home.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        
        if form.image_file.data and allowed_file(form.image_file.data.filename):
            imagem_nome = secure_filename(form.image_file.data.filename)
            timestamp = time.time()
            imagem_nome = f"{timestamp}-{imagem_nome}"
            imagens_path = os.path.join(app.config['UPLOAD_PATH'], imagem_nome)
            form.image_file.data.save(imagens_path)
            imagem_relativa = imagem_nome
        else:
            imagem_relativa = 'default.jpg'
            
        user = Usuario(
            username=form.username.data,
            email=form.email.data,
            senha=hashed_password,
            telefone=form.telefone.data,
            endereco=form.endereco.data,
            image_file=imagem_relativa,
            tipo_usuario=form.tipo_usuario.data
        )

        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.senha, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/cadastrar_produto', methods=['GET', 'POST'])
@login_required
def cadastrar_produto():
    if current_user.tipo_usuario != TipoUsuario.PRODUTOR:
        flash('Access denied. You must be a seller to access this page.', 'danger')
        return redirect(url_for('home'))
    
    form = CadastroProdutoForm()
    if form.validate_on_submit():
        if not os.path.exists(app.config['UPLOAD_PATH']):
            os.makedirs(app.config['UPLOAD_PATH'])
        
        if form.imagens.data and allowed_file(form.imagens.data.filename):
            imagem_nome = secure_filename(form.imagens.data.filename)
            timestamp = time.time()
            imagem_nome = f"{imagem_nome}-{timestamp}"
            imagens_path = os.path.join(app.config['UPLOAD_PATH'], imagem_nome)
            form.imagens.data.save(imagens_path)
        else:
            imagem_nome = 'default.jpg'
        
        product = Produto(
            nome=form.nome.data,
            descricao=form.descricao.data,
            image_file=imagem_nome,
            preco=form.preco.data,
            quantidade=form.quantidade.data,
            unidade_medida="Kg",
            id_produtor=current_user.id,
            date_posted=datetime.now(timezone.utc)
        )
        
        db.session.add(product)
        db.session.commit()

        flash(f'Produto {form.nome.data} cadastrado com sucesso!', 'success')
        return redirect(url_for('home'))
    return render_template('new_product.html', form=form)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
@csrf.exempt
def delete_product(product_id):
    product = Produto.query.get_or_404(product_id)
    if product.produtor != current_user:
        flash('You are not authorized to delete this product.', 'danger')
        return redirect(url_for('home'))

    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted.', 'success')
    return redirect(url_for('my_products'))

@app.route('/my_products')
@login_required
def my_products():
    if current_user.tipo_usuario != TipoUsuario.PRODUTOR:
        flash('Access denied. You must be a seller to access this page.', 'danger')
        return redirect(url_for('home'))
    
    products = Produto.query.filter_by(produtor=current_user).all()
    return render_template('my_products.html', products=products)

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = Produto.query.get_or_404(product_id)
    
    return render_template('product_detail.html', product=product)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('home'))

    cart = session['cart']
    
    if request.method == 'POST':
        total = sum(float(item['price']) * int(item['quantity']) for item in cart.values())
        
        pedido = Pedido(
            id_comprador=current_user.id,
            data_pedido=datetime.now(timezone.utc),
            status=StatusPedido.PENDENTE,
            total=total,
        )
        
        db.session.add(pedido)
        db.session.flush()
        
        for item_id, item in cart.items():
            item_pedido = ItemPedido(
                id_pedido=pedido.id,
                id_produto=item_id,
                quantidade=int(item['quantity']),
                preco_unitario=float(item['price']),
                total=float(item['price']) * int(item['quantity'])
            )
            db.session.add(item_pedido)
        
        db.session.commit()
        
        session.pop('cart', None)
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('home'))
    
    total = sum(float(item['price']) * int(item['quantity']) for item in cart.values())
    return render_template('checkout.html', cart=cart, total=total)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Produto.query.get_or_404(product_id)
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        print("Carrinho!")
        cart[str(product_id)] = {
            'name': product.nome,
            'price': float(product.preco),
            'quantity': 1
        }
    
    session.modified = True
    flash(f'Added {product.nome} to cart!', 'success')
    return redirect(url_for('home'))

@app.route('/perfil')
@login_required
def perfil():
    user = current_user
    
    compras = Pedido.query.filter_by(id_comprador=current_user.id).all()
    itens_pedido_produtor = ItemPedido.query.join(Produto).filter(Produto.id_produtor == user.id).all()
    vendas = set(item_pedido.pedido for item_pedido in itens_pedido_produtor)

    
    return render_template('perfil.html', user=user, compras=compras, vendas=vendas)

@app.route('/aprovar_pagamento/<int:item_id>', methods=['POST'])
@login_required
def aprovar_pagamento(item_id):
    item = ItemPedido.query.get_or_404(item_id)
    if item.pedido.status == StatusPedido.CONFIRMADO:
        flash('O pagamento já foi aprovado.', 'info')
        return redirect(url_for('perfil'))

    item.pedido.status = StatusPedido.CONFIRMADO
    
    for item in item.pedido.itens:
        produto = Produto.query.get(item.id_produto)
        if produto:
            produto.quantidade -= item.quantidade
            db.session.add(produto)
    
    db.session.commit()
    
    flash('Pagamento aprovado com sucesso!', 'success')
    return redirect(url_for('perfil'))