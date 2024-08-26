from flask import Flask, render_template, url_for, flash, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import os
from forms import RegistrationForm, LoginForm, ProductForm
from models import db, bcrypt, User, Product
from flask_wtf.csrf import CSRFProtect

# Inicializar o aplicativo Flask
app = Flask(__name__)
app.config.from_object('config.Config')

# Inicializar as extensões
db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
# Configurar a página de login
login_manager.login_view = 'login'

# Função para carregar o usuário
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rota para a página inicial
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)

# Rota para registro de usuário
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
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
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

# Rota para o dashboard de publicação de produtos
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role != 'vendor':
        flash('Access denied. You must be a seller to access this page.', 'danger')
        return redirect(url_for('home'))

    form = ProductForm()
    if form.validate_on_submit():
        # Lidar com o upload de imagem
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            user_folder = os.path.join('static/images', current_user.username)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            image_path = os.path.join(user_folder, filename)
            form.image.data.save(image_path)
            product = Product(title=form.title.data, content=form.content.data, author=current_user, image_file=filename)
        else:
            product = Product(title=form.title.data, content=form.content.data, author=current_user)
        
        db.session.add(product)
        db.session.commit()
        flash('Your product has been posted!', 'success')
        return redirect(url_for('home'))
    return render_template('dashboard.html', form=form)

# Rota para a página de produtos do vendedor
@app.route('/my_products')
@login_required
def my_products():
    if current_user.role != 'vendor':
        flash('Access denied. You must be a seller to access this page.', 'danger')
        return redirect(url_for('home'))
    
    products = Product.query.filter_by(author=current_user).all()
    return render_template('my_products.html', products=products)

# Rota para deletar produtos do vendedor
@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
@csrf.exempt  # Opcional: Exclui essa rota da proteção CSRF se não estiver funcionando
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.author != current_user:
        flash('You are not authorized to delete this product.', 'danger')
        return redirect(url_for('home'))

    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted.', 'success')
    return redirect(url_for('my_products'))

# Rota para logout de usuário
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)  # Remove 'user_id' da sessão se estiver presente
    return redirect(url_for('home'))

# Inicializar o banco de dados e iniciar o aplicativo
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
