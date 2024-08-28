from blue import app, db, login_manager, bcrypt
from flask import Flask, render_template, url_for, flash, redirect, session
from flask_login import current_user, login_user, logout_user, login_required
import os
from werkzeug.utils import secure_filename
from ..forms import RegistrationForm, LoginForm, CadastroProdutoForm
from ..models.tables import db, Usuario, Produto
from datetime import datetime, timezone
from ..models.tables import TipoUsuario, db, Usuario, Produto


# Função para carregar o usuário
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rota para a página inicial
@app.route('/')
def home():
    products = Produto.query.all()
    return render_template('home.html', products=products)

# Rota para registro de usuário
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        tipo_usuario = form.role.data
        user = Usuario(username=form.username.data, email=form.email.data, senha=hashed_password, tipo_usuario=tipo_usuario)
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# Rota para login de usuário
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

# Rota para o dashboard de publicação de produtos
@app.route('/cadastrar_produto', methods=['GET', 'POST'])
@login_required
def cadastrar_produto():
    form = CadastroProdutoForm()
    if form.validate_on_submit():
        if not os.path.exists(app.config['UPLOAD_PATH']):
            os.makedirs(app.config['UPLOAD_PATH'])
        
        if form.imagens.data and allowed_file(form.imagens.data.filename):
            imagem_nome = secure_filename(form.imagens.data.filename)
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
        return redirect(url_for('home'))  # Redireciona para a página inicial após o cadastro
    return render_template('new_product.html', form=form)

# Rota para logout de usuário
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)  # Remove 'user_id' da sessão se estiver presente
    return redirect(url_for('home'))