#aula21 rotas api com templetes adicionar imagem, padrão mvc continuação.
###############################

#uvicorn main:app --reload

#controller.py
from fastapi import APIRouter,Request,Form,UploadFile,File,Depends,HTTPException,Query
import requests,math
#APIRouter=rota api para o front,
#requests=Requisição http,
# Form=Formulário para criar e editar,
# UploadFile=Upload da foto,
# File=Função para gravar caminho da imagem,
# Depends=dependência do banco de dados sqlite
#pip install python-multipart
from fastapi.responses import HTMLResponse,RedirectResponse
#HTMLResponse=resposta do html get,post,put,delete,
#RedirectResponse=redirecionar a respota para o front 'index.html'
from fastapi.templating import Jinja2Templates
#Jinja2Templates=responsável por renderizar o front-end
import os, shutil
#os=funções de sistema,
#shutil=salva e puxa diretórios do sistema 'caminho das imagens'
from sqlalchemy.orm import Session
#Session=modelagem do ORM models
from database import get_db, SessionLocal
#get_db=ingeção do SessionLocal na api
from models import Produto,Usuario,ItemPedido,Pedido
#Produto=modelagem, nome,preco,quantidade,imagem
router=APIRouter()#rotas
templates=Jinja2Templates(directory="templates")#front-end
#pasta para salvar imagens
UPLOAD_DIR="static/uploads"
#caminho para o os
os.makedirs(UPLOAD_DIR,exist_ok=True)
#rota para página inicial listar produtos

#novos import's
#controller.py
#funções de CRUD criar atualizar e deletar
#criar produto

@router.get("/",response_class=HTMLResponse)
async def listar(request:Request,
                 db:Session=Depends(get_db)):
    produtos=db.query(Produto).all()#puxar produtos do banco de dados
    return templates.TemplateResponse("index.html",{
        "request":request,"produtos":produtos
    })

#Rota detalhe do produto
@router.get("/produto/{id_produto}",
            response_class=HTMLResponse)
async def detalhe(request:Request,id_produto:int,
                  db:Session=Depends(get_db)):
    produto=db.query(Produto).filter(Produto.id==id_produto).first()
    return templates.TemplateResponse("produto.html",{
        "request":request,"produto":produto
    })

async def criar_produto(
        nome:str=Form(...),
        preco:float=Form(...),
        quantidade:int=Form(...),
        imagem:UploadFile=File(...),
        db:Session=Depends(get_db)
):
    #caminho para salvar a imagem
    caminho=os.path.join(UPLOAD_DIR,imagem.filename)
    with open(caminho,"wb") as arquivo:
        shutil.copyfileobj(imagem.file,arquivo)
    novo=Produto(
        nome=nome,preco=preco,quantidade=quantidade,
        imagem=imagem.filename
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

#rota para criar item novo
@router.get("/novo",response_class=HTMLResponse)
async def form_novo(request:Request):
    return templates.TemplateResponse("novo.html",{
        "request":request
    })
#criar o produto post
@router.post("/novo")
async def criar(
        nome:str=Form(...),
        preco:float=Form(...),
        quantidade:int=Form(...),
        imagem:UploadFile=File(...),
        db:Session=Depends(get_db)):
    await criar_produto(nome,preco,quantidade,imagem,db)
    return RedirectResponse("/",status_code=303)




#função atualizar
async def atualizar_produto(
        id:int,
        nome:str=Form(...),
        preco:float=Form(...),
        quantidade:int=Form(...),
        imagem:UploadFile=File(...),
        db:Session=Depends(get_db)
):
    #busca produto pelo id
    produto=db.query(Produto).filter(Produto.id==id).first()
    if not produto:
        return None
    produto.nome=nome
    produto.preco=preco
    produto.quantidade=quantidade
    #if para imagem
    if imagem and imagem.filename !="":
        #caminho para salvar a imagem
        caminho=os.path.join(UPLOAD_DIR,imagem.filename)
        with open(caminho,"wb") as arquivo:
            shutil.copyfileobj(imagem.file,arquivo)
        produto.imagem=imagem.filename
    db.commit()
    db.refresh(produto)
    return produto 

#editar produto
@router.get("/editar/{id}",response_class=HTMLResponse)
async def form_editar(
        id:int,
        request:Request,
        db:Session=Depends(get_db)):
    #Query produto por id
    produto=db.query(Produto).filter(Produto.id==id).first()
    return templates.TemplateResponse("editar.html",{
        "request":request, "produto":produto
    })
#rota post
@router.post("/editar/{id}")
async def editar(
        id:int,
        nome:str=Form(...),
        preco:float=Form(...),
        quantidade:int=Form(...),
        imagem:UploadFile=File(...),
        db:Session=Depends(get_db)):
    await atualizar_produto(id,nome,preco,quantidade,imagem,db)
    return RedirectResponse("/", status_code=303)

#função deletar produto
async def deletar_produto(id:int,
        db:Session=Depends(get_db)):
    produto=db.query(Produto).filter(Produto.id==id).first()
    if produto:
        db.delete(produto)
        db.commit()
    return produto
#rota para deletar
@router.get("/deletar/{id}")
async def deletar(id:int,db:Session=Depends(get_db)):
    await deletar_produto(id,db)
    return RedirectResponse("/",status_code=303)



#controller.py
#novo import
from auth import gerar_hash_senha,vericar_senha,criar_token,verificar_token

#######################################################
#######################################################
#rotas da api para autenticação de usuário
#cadastro de usuário
@router.get("/register",response_class=HTMLResponse)
def pagina_cadastro(request:Request):
    return templates.TemplateResponse("register.html",
                    {"request":request})
@router.post("/register")
def cadastrar_usuario(
    request:Request,nome:str=Form(...),
    email:str=Form(...), senha:str=Form(...),
    db:Session=Depends(get_db)
):
    usuario=db.query(Usuario).filter(Usuario.email==email).first()
    if usuario:
        return {"mensagem":"E-mail já cadastrado!"}
    senha_hash=gerar_hash_senha(senha)
    novo_usuario=Usuario(nome=nome,email=email,senha=senha_hash)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return RedirectResponse(url="/",status_code=303)

#####################
#login do usuário
@router.get("/login",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("login.html",{
        "request":request
    })
'''
#post do login
@router.post("/login")
def login(request:Request,email:str=Form(...),
          senha:str=Form(...),db:Session=Depends(get_db)):
    usuario=db.query(Usuario).filter(Usuario.email==email).first()
    if not usuario or not vericar_senha(senha,usuario.senha):
        return {"mensagem":"Credenciais inválidas"}
    token=criar_token({"sub":usuario.email})
    response=RedirectResponse(url="/dashboard",status_code=303)
    response.set_cookie(key="token",value=token,httponly=True)
    return response'''
#página protegida do usuário logado (dashboard)
@router.get("/dashboard",response_class=HTMLResponse)
def dashboard(request:Request):
    token=request.cookies.get("token")
    if not token or not verificar_token(token):
        return RedirectResponse(url="/",status_code=303)
    return templates.TemplateResponse("dashboard.html",
                    {"request":request})
#novo login



#post do login
@router.post("/login")
def login(request:Request,email:str=Form(...),
          senha:str=Form(...),db:Session=Depends(get_db)):
   
    usuario=db.query(Usuario).filter(Usuario.email==email).first()
    if not usuario or not vericar_senha(senha,usuario.senha):
        return {"mensagem":"Credenciais inválidas"}
   
    #criar o token no campo is_admin
    token=criar_token({"sub":usuario.email,
                       "is_admin":usuario.is_admin})
    #verificar se o user é admin e direcionar a rota
    if usuario.is_admin:
        destino="/admin"
    else:
        destino="/me/painel"
    response=RedirectResponse(url=destino,status_code=303)
    response.set_cookie(key="token",value=token,httponly=True)
    return response

#rota admin crud nos produtos
@router.get("/admin",response_class=HTMLResponse)
def pagina_admin(request:Request,db:Session=Depends(get_db)):
    #token do admin
    token=request.cookies.get("token")
    payload=verificar_token(token)
    if not payload or not payload.get("is_admin"):
        return RedirectResponse(url="/",status_code=303)
    produtos=db.query(Produto).all()
    return templates.TemplateResponse("admin.html",{
        "request":request,"produtos":produtos
    })
#rota criar produto
@router.post("/admin/produto")
def criar_produto(request:Request,nome:str=Form(...),
    preco:float=Form(...),quantidade:int=Form(...),
    imagem:UploadFile=File(...),db:Session=Depends(get_db)
):
    caminho_arquivo=f"{UPLOAD_DIR}/{imagem.filename}"
    with open(caminho_arquivo,"wb") as arquivo:
        shutil.copyfileobj(imagem.file,arquivo)
    novo_produto=Produto(
        nome=nome,preco=preco,quantidade=quantidade,
        imagem=imagem.filename
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return RedirectResponse(url="/admin",status_code=303)

#deletar produto
@router.post("/admin/produto/deletar/{id}")
def deletar_produto(id:int,db:Session=Depends(get_db)):
    produto=db.query(Produto).filter(Produto.id==id).first()
    if produto:
        db.delete(produto)
        db.commit()
    return RedirectResponse(url="/admin",status_code=303)

#carrinho simples
carrinhos={}

#adicionar item ao carrinho
@router.post("/carrinho/adicionar/{produto_id}")
def adicionar_carrinho(request:Request,produto_id:int,
    quantidade:int=Form(1),db:Session=Depends(get_db)):
    token=request.cookies.get("token")
    payload=verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login",status_code=303)
    email=payload.get("sub")
    usuario=db.query(Usuario).filter_by(email=email).first()
    produto=db.query(Produto).filter_by(id=produto_id).first()
    if not produto:
        return{"mensagem":"produto não encontrado"}
    carrinho=carrinhos.get(usuario.id,[])
    carrinho.append({
        "id":produto.id,
        "nome":produto.nome,
        "preco":produto.preco,
        "quantidade":quantidade})
    carrinhos[usuario.id]=carrinho
    return RedirectResponse(url="/carrinho",status_code=303)

#rota admin crud nos produtos
@router.get("/admin",response_class=HTMLResponse)
def pagina_admin(request:Request,db:Session=Depends(get_db)):
    #token do admin
    token=request.cookies.get("token")
    payload=verificar_token(token)
    if not payload or not payload.get("is_admin"):
        return RedirectResponse(url="/",status_code=303)
    produtos=db.query(Produto).all()
    return templates.TemplateResponse("admin.html",{
        "request":request,"produtos":produtos
    })
#rota criar produto
@router.post("/admin/produto")
def criar_produto(request:Request,nome:str=Form(...),
    preco:float=Form(...),quantidade:int=Form(...),
    imagem:UploadFile=File(...),db:Session=Depends(get_db)
):
    caminho_arquivo=f"{UPLOAD_DIR}/{imagem.filename}"
    with open(caminho_arquivo,"wb") as arquivo:
        shutil.copyfileobj(imagem.file,arquivo)
    novo_produto=Produto(
        nome=nome,preco=preco,quantidade=quantidade,
        imagem=imagem.filename
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return RedirectResponse(url="/admin",status_code=303)

#editar produto rota get edição
@router.get("/admin/produto/editar/{id}",
        response_class=HTMLResponse)
def editar_produto(id:int,request:Request,
                   db:Session=Depends(get_db)):
    token = request.cookies.get("token")
    payload = verificar_token(token)
    if not payload or not payload.get("is_admin"):
        return RedirectResponse(url="/", status_code=303)
    produto=db.query(Produto).filter(Produto.id==id).first()
    if not produto:
        return RedirectResponse(url="/admin",status_code=303)
    return templates.TemplateResponse("editar.html",{
        "request":request,"produto":produto
    })
#rota atualizar produto post
@router.post("/admin/produto/atualizar/{id}")
def atualizar_produto(id:int,nome:str=Form(...),
    preco:float=Form(...),quantidade:int=Form(...),
    imagem:UploadFile=File(None),db:Session=Depends(get_db)
):
    produto=db.query(Produto).filter(Produto.id==id).first()
    if not produto:
        return RedirectResponse(url="/admin",status_code=303)
    #atualizar campos
    produto.nome=nome
    produto.preco=preco
    produto.quantidade=quantidade
    #atualizar imagem se uma nova for enviada
    if imagem and imagem.filename !="":
        caminho_arquivo=f"{UPLOAD_DIR}/{imagem.filename}"
        with open(caminho_arquivo,"wb") as arquivo:
            shutil.copyfileobj(imagem.file,arquivo)
        produto.imagem=imagem.filename
    db.commit()
    db.refresh(produto)
    return RedirectResponse(url="/admin",status_code=303)

#deletar produto
@router.post("/admin/produto/deletar/{id}")
def deletar_produto(id:int,db:Session=Depends(get_db)):
    produto=db.query(Produto).filter(Produto.id==id).first()
    if produto:
        db.delete(produto)
        db.commit()
    return RedirectResponse(url="/admin",status_code=303)

#visualizar carrinho
@router.get("/carrinho",response_class=HTMLResponse)
def ver_carrinho(request:Request,
        db:Session=Depends(get_db)):
    token=request.cookies.get("token")
    payload=verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login",status_code=303)
    email=payload.get("sub")
    usuario=db.query(Usuario).filter_by(email=email).first()
    carrinho=carrinhos.get(usuario.id,[])
    total=sum(item["preco"]*item["quantidade"] for item in carrinho)
    return templates.TemplateResponse("carrinho.html",
        {"request":request,"carrinho":carrinho,"total":total})


#finalizar compra checkout
@router.post("/checkout")
def checkout(request:Request,db:Session=Depends(get_db)):
    token=request.cookies.get("token")
    payload=verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login",status_code=303)
    email=payload.get("sub")
    usuario=db.query(Usuario).filter_by(email=email).first()
    carrinho=carrinhos.get(usuario.id,[])
    if not carrinho:
        return {"mensagem":"Carrinho vazio"}
    total=sum(item["preco"]*item["quantidade"] for item in carrinho)
    pedido=Pedido(usuario_id=usuario.id,total=total)
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    #novo item
    for item in carrinho:
        novo_item=ItemPedido(
            pedido_id=pedido.id,
            produto_id=item["id"],
            quantidade=item["quantidade"],
            preco_unitario=item["preco"]
        )
        db.add(novo_item)
    db.commit()
    #limpar o carrinho
    carrinhos[usuario.id]=[]#limpeza do carrinho
    return RedirectResponse("/meus-pedidos",status_code=303)




#listar pedidos do usuário
@router.get("/meus-pedidos",response_class=HTMLResponse)
def meus_pedidos(request:Request,db:Session=Depends(get_db)):
    token=request.cookies.get("token")
    payload=verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login",status_code=303)
    email=payload.get("sub")
    usuario=db.query(Usuario).filter_by(email=email).first()
    pedidos=db.query(Pedido).filter_by(usuario_id=usuario.id).all()
    return templates.TemplateResponse("meus_pedidos.html",
            {"request":request,"pedidos":pedidos})

#Aula29 aula painel usuário fastapi aula base 28.
########################################################
#painel do usuário
@router.get("/me/painel",response_class=HTMLResponse)
def painel_usuario(request:Request,
    db:Session=Depends(get_db)):
    token=request.cookies.get("token")
    payload=verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login",status_code=303)
    usuario=db.query(Usuario).filter(Usuario.email==payload["sub"]).first()
    pedidos=db.query(Pedido).filter(Pedido.usuario_id==usuario.id).first()
    return templates.TemplateResponse("painel_usuario.html",{
        "request":request,"usuario":usuario,"pedidos":pedidos
    })
#rota dados do usuário
@router.get("/me/dados",response_class=HTMLResponse)
def meus_dados(request:Request,db:Session=(Depends(get_db))):
    token=request.cookies.get("token")
    payload=verificar_token(token)
    if not payload:
        return RedirectResponse(url="/login",status_code=303)
    usuario=db.query(Usuario).filter(Usuario.email==payload["sub"]).first()
    return templates.TemplateResponse("meus_dados.html",{
        "request":request,"usuario":usuario
    })
#remove o cookie do token do usuário
@router.get("/logout")
def logout(request:Request):
    response=RedirectResponse(url="/",status_code=303)
    response.delete_cookie(key="token")
    return response

#rota de frete.
#importar requests,math, HTTPException,Querry
#controller.py
#from fastapi import APIRouter,Request,Form,UploadFile,File,Depends,HTTPException,Query
#import request,math
#frete simulado
#CEP fixo da loja (exemplo SENAI Francisco Matarazzo)
CEP_LOJA="03552140"#CEP SENAI
@router.get("/api/frete")
def calcular_frete(request:Request,
    cep_destino:str=Query(...)):
    token=request.cookies.get("token")
    payload=verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401,
            detail="Usuário não autenticado")
   #validação simples de cep
    if not cep_destino.isdigit() or len(cep_destino) !=8:
        raise HTTPException(status_code=400,
                detail="CEP inválido")
    #consulta no ViaCep
    via_cep_url=f"https://viacep.com.br/ws/{cep_destino}/json/"
    resposta= requests.get(via_cep_url)
    if resposta.status_code !=200:
        raise HTTPException(status_code=400,
                detail="Erro ao consultar o CEP")
    dados=resposta.json()
    if "erro" in dados:
        raise HTTPException(status_code=400,
            detail="CEP não encontrado")
    #simulação do frete com dados fixo
    valor_frete =15.00
    prazo_estimado=6
    #retorno dados estruturado endereço via cep
    return {
        "endereco":f"{dados.get('logradouto')},{dados.get('bairro')},{dados.get('localidade')},{dados.get('uf')}",
        "cep":cep_destino,
        "valor_frete":valor_frete,
        "prazo_estimado_dias":prazo_estimado,
        "status":"simulação concluída"}