# Imagem base oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Define variáveis de ambiente para otimizar o Python no container
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala dependências do sistema necessárias para compilação (se houver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta em que o FastAPI rodará
EXPOSE 8000

# Comando para iniciar o servidor ASGI (Uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]