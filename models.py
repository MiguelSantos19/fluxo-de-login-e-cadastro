#models.py
from sqlalchemy import Column,Integer,String,Float,Boolean,ForeignKey#import novo
from database import Base,engine,SessionLocal
#novo import sql puro para add uma nova coluna
from sqlalchemy import text#
from auth import *
from sqlalchemy.orm import relationship

#tabela de produtos
class Produto(Base):
    __tablename__="produtos"
    id=Column(Integer,primary_key=True,index=True)
    nome=Column(String,nullable=False)
    preco=Column(Float,nullable=False)
    quantidade=Column(Integer,nullable=False)
    imagem=Column(String,nullable=True)

#models.py
class Usuario(Base):
    __tablename__="usuarios"
    id=Column(Integer,primary_key=True,index=True)
    nome=Column(String(50))
    email=Column(String(100),unique=True)
    senha=Column(String(200))#senha será salva com hash jwt
    is_admin=Column(Boolean,default=False)#novo campo
    #relação de tabelas
    pedidos=relationship("Pedido",back_populates="usuario")
#criar banco e tabelas
#Base.metadata.create_all(bind=engine)


#criar banco e tabelas
'''
Base.metadata.create_all(bind=engine)

nome="Calça"
preco=125.55
quantidade=20
imagem="sem foto"
novo=Produto(nome=nome,preco=preco,quantidade=quantidade,
             imagem=imagem)

db=SessionLocal()

db.add(novo)
db.commit()
'''
#comentar após criar os dados
'''
nome="Calça"
preco=125.55
quantidade=20
imagem="sem foto"
novo=Produto(nome=nome,preco=preco,quantidade=quantidade,
             imagem=imagem)
db=SessionLocal()
db.add(novo)
db.commit()
'''

#tabelas novas
class Pedido(Base):
    __tablename__="pedidos"
    id=Column(Integer,primary_key=True,index=True)
    usuario_id=Column(Integer,ForeignKey("usuarios.id"))
    total=Column(Float,default=0.0)
    #relação de tabelas
    usuario=relationship("Usuario",back_populates="pedidos")
    itens=relationship("ItemPedido",back_populates="pedido")
class ItemPedido(Base):
    __tablename__="itens_pedido"
    id=Column(Integer,primary_key=True,index=True)
    pedido_id=Column(Integer,ForeignKey("pedidos.id"))
    produto_id=Column(Integer,ForeignKey("produtos.id"))
    quantidade=Column(Integer)
    preco_unitario=Column(Float)
    #relação de tabelas
    pedido=relationship("Pedido",back_populates="itens")

#criar banco e tabelas
#Base.metadata.create_all(bind=engine)


#user admin
# with engine.connect() as conexao:
#     conexao.execute(text("""
# ALTER TABLE usuarios ADD COLUMN is_admin BOOLEAN DEFAULT 0 """))
# db=SessionLocal()
# admin=Usuario(nome="admin",email="admin@loja.com",
#             senha=gerar_hash_senha("123456"),is_admin=True)
# db.add(admin)
# db.commit()