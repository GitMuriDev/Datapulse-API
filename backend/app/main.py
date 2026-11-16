from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.db.session import engine, Base
import app.models


# Cria as tabelas no PostgreSQL automaticamente caso ainda não existam
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DataPulse API",
    description="API de Telemetria e Observabilidade em Tempo Real",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Permite chamadas de Frontends externos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conecta todas as nossas controllers ao app sob /api/v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "DataPulse API está rodando com sucesso!"}