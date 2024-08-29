from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DecimalField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange

from .models.tables import Usuario,TipoUsuario

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)],
                           render_kw={"placeholder": "Nome do usuario"})
    
    telefone = StringField('Telefone', 
                           validators=[Length(max=20)],
                           render_kw={"placeholder": "Número do telefone"})
    
    email = StringField('Email', 
                        validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Insira seu E-mail"})
    
    senha = PasswordField('Senha', 
                          validators=[DataRequired()],
                          render_kw={"placeholder": "Insira sua senha"})
    
    confirmar_senha = PasswordField('Confirme sua senha', 
                                    validators=[DataRequired(), EqualTo('senha')],
                                    render_kw={"placeholder": "Confirme sua senha"})
    
    endereco = StringField('Endereço', 
                           validators=[DataRequired(), Length(max=100)],
                           render_kw={"placeholder": "Endereço"})
    
    image_file = FileField('Atualizar Imagem de Perfil', 
                           validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    
    tipo_usuario = SelectField('Tipo de Usuário', 
                               choices=[(tipo.name, tipo.value) for tipo in TipoUsuario], 
                               validators=[DataRequired()])
    
    submit = SubmitField('Registrar')
    
    def validate_username(self, username):
        user = Usuario.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Esse nome de usuário já está em uso. Por favor, escolha outro.')
    
    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Esse email já está em uso. Por favor, escolha outro.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Informe seu email"})
    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={"placeholder": "Informe sua senha"})
    remember = BooleanField('Manter-se registrado')
    submit = SubmitField('Login')

class CadastroProdutoForm(FlaskForm):
    nome = StringField('Nome do Produto', validators=[DataRequired(), Length(min=2, max=100)],
                       render_kw={"placeholder": "Nome do produto"})
    descricao = TextAreaField('Descrição', validators=[DataRequired(), Length(min=10, max=500)],
                              render_kw={"placeholder": "Descrição do produto"})
    preco = DecimalField('Preço', validators=[DataRequired(), NumberRange(min=0)], places=2,
                         render_kw={"placeholder": "Preço do Produto"})
    quantidade = IntegerField('Quantidade Disponível', validators=[DataRequired(), NumberRange(min=1)], render_kw={"placeholder": "Quantidade disponível"})
    unidade_medida = SelectField('Unidade de Medida', choices=[('kg', 'Kg'), ('litro', 'Litro'), ('unidade', 'Unidade')], validators=[DataRequired()], render_kw={"placeholder": "Unidade de Medida"})
    imagens = FileField('Imagens do Produto', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Somente imagens são permitidas!')])
    submit = SubmitField('Cadastrar Produto')

class AdicionarAoCarrinhoForm(FlaskForm):
    quantidade = IntegerField('Quantidade', validators=[
        DataRequired(message="Campo obrigatório."),
        NumberRange(min=1, message="A quantidade deve ser no mínimo 1.")
    ])
    submit = SubmitField('Adicionar ao Carrinho')