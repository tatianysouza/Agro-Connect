from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DecimalField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange

from .models.tables import Usuario,TipoUsuario

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[(TipoUsuario.PRODUTOR.value, 'Produtor'), (TipoUsuario.COMPRADOR.value, 'Comprador')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Usuario.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CadastroProdutoForm(FlaskForm):
    nome = StringField('Nome do Produto', validators=[DataRequired(), Length(min=2, max=100)])
    descricao = TextAreaField('Descrição', validators=[DataRequired(), Length(min=10, max=500)])
    preco = DecimalField('Preço', validators=[DataRequired(), NumberRange(min=0)], places=2)
    quantidade = IntegerField('Quantidade Disponível', validators=[DataRequired(), NumberRange(min=1)])
    unidade_medida = SelectField('Unidade de Medida', choices=[('kg', 'Kg'), ('litro', 'Litro'), ('unidade', 'Unidade')], validators=[DataRequired()])
    imagens = FileField('Imagens do Produto', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Somente imagens são permitidas!')])
    submit = SubmitField('Cadastrar Produto')
