#main.py

#uvicorn main:app --reload

from fastapi import FastAPI
from controller import router
from fastapi.staticfiles import StaticFiles
#montar pasta de imagem
app=FastAPI(title="MVC Produtos")

app.mount("/static",StaticFiles(directory="static"),
          name="static")
app.include_router(router)