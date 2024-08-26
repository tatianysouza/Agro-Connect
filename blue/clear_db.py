from app_blue import app, db
from models import User, Product

# Configurar o contexto da aplicação
with app.app_context():
    # Deletar todos os registros
    User.query.delete()
    Product.query.delete()
    db.session.commit()

    print("Banco de dados limpo com sucesso!")

# Código para apagar oque tem no banco
#python clear_db.py 