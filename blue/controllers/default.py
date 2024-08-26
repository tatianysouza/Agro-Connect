from blue import app, db, login_manager
from flask import Flask, render_template, url_for, flash, redirect, session
from flask_login import current_user, login_user, logout_user, login_required
from ..forms import RegistrationForm, LoginForm, ProductForm
from ..models.tables import db, bcrypt, User, Product



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
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(product)
        db.session.commit()
        flash('Your product has been posted!', 'success')
        return redirect(url_for('home'))
    return render_template('dashboard.html', form=form)

# Rota para logout de usuário
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)  # Remove 'user_id' da sessão se estiver presente
    return redirect(url_for('home'))