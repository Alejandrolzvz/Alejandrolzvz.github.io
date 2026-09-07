# Usar imagen ligera de Python
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos y cachear instalación
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar el resto del código
COPY . /app/

# Inicializar DB si no existe (el script db.py debe manejarlo adecuadamente)
# RUN python init_db_all.py

# Exponer el puerto
EXPOSE 5000

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
