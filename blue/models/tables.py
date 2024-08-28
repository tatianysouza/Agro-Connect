from blue import db
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import enum


class StatusPedido(enum.Enum):
    PENDENTE = "Pendente"
    CONFIRMADO = "Confirmado"
    ENVIADO = "Enviado"
    CANCELADO = "Cancelado"

class TipoUsuario(enum.Enum):
    PRODUTOR = "Produtor"
    COMPRADOR = "Comprador"

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(100), nullable=False, default='a')
    image_file = db.Column(db.String(255), nullable=False, default='default.jpg')
    data_criacao = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    tipo_usuario = db.Column(db.Enum(TipoUsuario), nullable=False, default=TipoUsuario.PRODUTOR)

    # Relacionamentos
    produtos = db.relationship('Produto', back_populates='produtor')
    
    pedidos_como_comprador = db.relationship("Pedido", foreign_keys='Pedido.id_comprador', back_populates="comprador")
    
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Produto(db.Model):
    __tablename__ = "produtos"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(50), nullable=False, default='default.jpg')
    preco = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    unidade_medida = db.Column(db.String(5), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    id_produtor = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    produtor = db.relationship('Usuario', back_populates='produtos')
    
    def __repr__(self):
        return f"Product('{self.nome}', '{self.date_posted}')"


class Pedido(db.Model):
    __tablename__ = "pedidos"
    
    id = db.Column(db.Integer, primary_key=True)
    id_comprador = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_pedido = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    status = db.Column(db.Enum(StatusPedido), default=StatusPedido.PENDENTE)
    total = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)
    
    itens = db.relationship("ItemPedido", backref="pedido")
    comprador = db.relationship('Usuario', foreign_keys=[id_comprador], back_populates="pedidos_como_comprador")


class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    id_produto = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)
    total = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)
    
    #pedido = db.relationship('Pedido', foreign_keys=[id_pedido])

    produto = db.relationship('Produto', foreign_keys=[id_produto], backref="itens")

class Avaliacao(db.Model):
    __tablename__ = 'avaliacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    id_produto = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    id_comprador = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=False)
    data_avaliacao = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    produto = relationship("Produto", backref="avaliacoes")
    comprador = relationship("Usuario", backref="avaliacoes")
