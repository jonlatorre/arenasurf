FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=arenasurf.settings

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libc6-dev \
        libsqlite3-dev \
        curl \
        build-essential \
        default-mysql-client \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r django && useradd -r -g django django

# Copiar archivos de dependencias
COPY requirements.txt /app/
COPY requirements-zero.txt /app/
COPY requirements-account.txt /app/
COPY requirements-mysql.txt /app/

# Instalar dependencias de Python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install -r requirements-zero.txt \
    && pip install -r requirements-account.txt \
    && pip install -r requirements-mysql.txt \
    && pip install gunicorn

# Copiar el script de entrada y darle permisos
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Copiar el código de la aplicación
COPY . /app/

# Crear directorios necesarios
RUN mkdir -p /app/static/dist \
    && mkdir -p /app/media \
    && mkdir -p /app/logs

# Establecer permisos
RUN chown -R django:django /app

# Cambiar al usuario no-root
USER django

# Exponer puerto
EXPOSE 8000

# Script de entrada
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "arenasurf.wsgi:application"]
