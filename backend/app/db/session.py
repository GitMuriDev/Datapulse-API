import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgrespassword@db:5432/datapulse_db"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe Base para os modelos
class Base(DeclarativeBase):
    pass


# Dependency Injection para obter a sessão do banco em cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()