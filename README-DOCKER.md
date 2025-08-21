# 🌊 Arena Surf Center - Docker Setup

Este documento explica cómo ejecutar la aplicación Arena Surf Center usando Docker.

## 🚀 Inicio Rápido

### Prerequisitos
- Docker
- Docker Compose
- Make (opcional, para comandos simplificados)

### Instalación Rápida

```bash
# Clonar el repositorio
git clone <repository-url>
cd arenasurf

# Instalación completa automática
make install
```

### Acceso a la Aplicación
- **Aplicación**: http://localhost
- **Admin Django**: http://localhost/admin/
  - Usuario: `admin`
  - Contraseña: `admin123`

## 🛠️ Comandos Disponibles

### Comandos con Make
```bash
make help              # Ver todos los comandos disponibles
make build             # Construir imagen Docker
make dev               # Modo desarrollo (recarga automática)
make prod              # Modo producción
make up                # Levantar servicios
make down              # Parar servicios
make logs              # Ver logs
make shell             # Acceder al shell del contenedor
make migrate           # Ejecutar migraciones
make createsuperuser   # Crear superusuario
make test              # Ejecutar tests
make clean             # Limpiar contenedores no utilizados
```

### Comandos Docker Compose Directos

#### Desarrollo
```bash
# Levantar en modo desarrollo
docker-compose -f docker-compose.dev.yml up --build

# Ver logs
docker-compose -f docker-compose.dev.yml logs -f web

# Acceder al shell
docker-compose -f docker-compose.dev.yml exec web /bin/bash
```

#### Producción
```bash
# Levantar servicios completos (Django + PostgreSQL + Nginx)
docker-compose up -d --build

# Ver logs
docker-compose logs -f web

# Parar servicios
docker-compose down
```

## 📁 Estructura de Archivos Docker

```
arenasurf/
├── Dockerfile              # Imagen principal de Django
├── docker-compose.yml      # Configuración producción
├── docker-compose.dev.yml  # Configuración desarrollo
├── entrypoint.sh           # Script de inicialización
├── nginx.conf              # Configuración Nginx
├── .dockerignore           # Archivos a ignorar
└── Makefile               # Comandos simplificados
```

## 🔧 Configuraciones

### Variables de Entorno
Puedes personalizar la configuración usando variables de entorno:

```bash
# Ejemplo para desarrollo
export DEBUG=1
export SECRET_KEY="tu-clave-secreta"
export DATABASE_URL="sqlite:///app/dev.db"
```

### Volúmenes
- `media/`: Archivos subidos por usuarios
- `logs/`: Logs de la aplicación
- `static/`: Archivos estáticos (CSS, JS, imágenes)

### Puertos
- **8000**: Aplicación Django (desarrollo)
- **80**: Nginx (producción)
- **3306**: MySQL (desarrollo y producción)

## 🗄️ Base de Datos

### MySQL (Desarrollo y Producción)
```bash
# La configuración está en docker-compose.yml
# Base de datos: arenasurf (producción) / arenasurf_dev (desarrollo)
# Usuario: arenasurf
# Contraseña: arenasurf123
# Puerto: 3306
```

### Migraciones
```bash
# Crear migraciones
make makemigrations

# Aplicar migraciones
make migrate

# O directamente:
docker-compose exec web python manage.py migrate
```

## 🔐 Usuarios y Permisos

### Superusuario Automático
Se crea automáticamente al levantar el contenedor:
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Email**: `admin@arenasurf.com`

### Crear Usuarios Adicionales
```bash
make createsuperuser
# O:
docker-compose exec web python manage.py createsuperuser
```

## 📊 Logs y Monitoreo

### Ver Logs en Tiempo Real
```bash
# Todos los servicios
docker-compose logs -f

# Solo Django
docker-compose logs -f web

# Solo base de datos
docker-compose logs -f db
```

### Logs Persistentes
Los logs se almacenan en `./logs/` en el host.

## 🧪 Testing

### Ejecutar Tests
```bash
make test
# O:
docker-compose exec web python manage.py test
```

### Coverage
```bash
make coverage
# O:
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

## 🔄 Backup y Restore

### Backup de Base de Datos
```bash
make backup-db
# Crea backup_YYYYMMDD_HHMMSS.sql
```

### Restaurar Base de Datos
```bash
make restore-db BACKUP_FILE=backup_20250821_120000.sql
```

## 🚨 Resolución de Problemas

### Puerto ya en uso
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar 8000 por 8001
```

### Permisos de archivos
```bash
# Reconstruir con permisos correctos
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Limpiar todo y empezar de nuevo
```bash
make clean
docker-compose down -v  # Elimina volúmenes también
make install
```

### Base de datos corrupta
```bash
# Eliminar base de datos y recrear
docker-compose down
docker volume rm arenasurf_mysql_data
docker-compose up -d
make migrate
```

## 🌐 Despliegue en Producción

### Configuración Recomendada
1. Cambiar `SECRET_KEY` en producción
2. Configurar `ALLOWED_HOSTS` apropiadamente
3. Usar MySQL con configuración robusta
4. Configurar SSL/HTTPS
5. Configurar backups automáticos

### Variables de Entorno Producción
```bash
export DEBUG=0
export SECRET_KEY="clave-secreta-muy-larga-y-aleatoria"
export ALLOWED_HOSTS="tudominio.com,www.tudominio.com"
export USE_MYSQL=1
export MYSQL_HOST="mysql-server"
export MYSQL_DATABASE="arenasurf_prod"
export MYSQL_USER="arenasurf_user"
export MYSQL_PASSWORD="password-muy-segura"
```

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `make logs`
2. Verifica el estado: `make status`
3. Limpia y reinstala: `make clean && make install`

---

¡Disfruta gestionando Arena Surf Center! 🏄‍♂️🌊
