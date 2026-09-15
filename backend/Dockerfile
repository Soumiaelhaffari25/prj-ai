FROM python:3.11-slim

# Évite les fichiers .pyc et force les logs non bufferisés
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système minimales (pour psycopg, bcrypt, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installe les dépendances Python.
# --extra-index-url CPU de PyTorch : force torch en version CPU
#   (évite ~1,5 Go de libs CUDA/NVIDIA inutiles).
# --timeout / --retries : tolère les coupures réseau sur les gros téléchargements.
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --timeout 120 --retries 5 \
    -r requirements.txt

# Copie le code de l'application
COPY . .

# Commande par défaut (surchargée pour le worker dans docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]