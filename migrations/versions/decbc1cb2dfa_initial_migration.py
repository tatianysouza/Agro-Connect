"""Initial migration

Revision ID: decbc1cb2dfa
Revises: 
Create Date: 2024-08-27 17:49:48.315390

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'decbc1cb2dfa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('usuarios',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('telefone', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('senha', sa.String(length=60), nullable=False),
    sa.Column('endereco', sa.String(length=100), nullable=False),
    sa.Column('image_file', sa.String(length=20), nullable=False),
    sa.Column('data_criacao', sa.DateTime(), nullable=True),
    sa.Column('tipo_usuario', sa.Enum('PRODUTOR', 'COMPRADOR', name='tipousuario'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('pedidos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_comprador', sa.Integer(), nullable=False),
    sa.Column('id_produtor', sa.Integer(), nullable=False),
    sa.Column('data_pedido', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Enum('Pendente', 'Concluído', 'Cancelado', name='status_enum'), nullable=False),
    sa.Column('total', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['id_comprador'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['id_produtor'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('produtos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=False),
    sa.Column('descricao', sa.Text(), nullable=False),
    sa.Column('image_file', sa.String(length=20), nullable=False),
    sa.Column('preco', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('quantidade', sa.Integer(), nullable=False),
    sa.Column('unidade_medida', sa.String(length=5), nullable=False),
    sa.Column('date_posted', sa.DateTime(), nullable=False),
    sa.Column('id_produtor', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_produtor'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('avaliacoes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_produto', sa.Integer(), nullable=False),
    sa.Column('id_comprador', sa.Integer(), nullable=False),
    sa.Column('nota', sa.Integer(), nullable=False),
    sa.Column('comentario', sa.Text(), nullable=False),
    sa.Column('data_avaliacao', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id_comprador'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['id_produto'], ['produtos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('itens_pedido',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_pedido', sa.Integer(), nullable=False),
    sa.Column('id_produto', sa.Integer(), nullable=False),
    sa.Column('quantidade', sa.Integer(), nullable=False),
    sa.Column('preco_unitario', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('total', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['id_pedido'], ['pedidos.id'], ),
    sa.ForeignKeyConstraint(['id_produto'], ['produtos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('itens_pedido')
    op.drop_table('avaliacoes')
    op.drop_table('produtos')
    op.drop_table('pedidos')
    op.drop_table('usuarios')
    # ### end Alembic commands ###
