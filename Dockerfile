FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos
COPY requirements.txt .

# Instalar librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear el directorio de soportes si no existe
RUN mkdir -p soportes_compromisos

# Comando para ejecutar la aplicación usando el puerto dinámico de Railway
CMD streamlit run calendario.py --server.port=$PORT --server.address=0.0.0.0
