# Configuración de Variables para GitLab CI/CD
# Estas variables deben configurarse en GitLab en Settings > CI/CD > Variables

## Variables Obligatorias

### Para el Registry de Docker
- `CI_REGISTRY`: registry.gitlab.com/tu-usuario/arenasurf
- `CI_REGISTRY_USER`: Tu usuario de GitLab
- `CI_REGISTRY_PASSWORD`: Token de acceso personal o password

### Para Deployment en Staging
- `STAGING_SERVER`: IP o dominio del servidor de staging
- `STAGING_USER`: Usuario SSH para staging
- `SSH_PRIVATE_KEY`: Clave privada SSH (formato PEM)

### Para Deployment en Producción
- `PRODUCTION_SERVER`: IP o dominio del servidor de producción
- `PRODUCTION_USER`: Usuario SSH para producción
- `PRODUCTION_DOMAIN`: Dominio público de tu aplicación
- `SSH_PRIVATE_KEY`: Clave privada SSH (formato PEM) - puede ser la misma

### Notificaciones (Opcional)
- `SLACK_WEBHOOK`: URL del webhook de Slack para notificaciones

## Variables de Base de Datos (para tests)
- `DATABASE_URL`: mysql://root:testpassword@mysql:3306/test_arenasurf
- `MYSQL_ROOT_PASSWORD`: testpassword (para tests)

## Configuración Adicional

### Runners de GitLab
Asegúrate de que tus runners tengan:
- Docker habilitado
- Acceso a internet
- Recursos suficientes (2GB RAM mínimo)

### Archivos necesarios en el servidor
Los servidores de staging y producción deben tener:
- Docker y Docker Compose instalados
- Directorio `/opt/arenasurf` (o el que configures)
- docker-compose.yml configurado para usar imágenes del registry
- Variables de entorno configuradas

## Configuración de SSH

1. Generar clave SSH:
```bash
ssh-keygen -t rsa -b 4096 -C "gitlab-ci@arenasurf"
```

2. Copiar clave pública al servidor:
```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub usuario@servidor
```

3. Agregar clave privada a GitLab:
- Ir a Settings > CI/CD > Variables
- Crear variable `SSH_PRIVATE_KEY`
- Copiar el contenido de ~/.ssh/id_rsa
- Marcar como "Protected" y "Masked"

## Estructura de Deployment

### Staging (/opt/arenasurf-staging/)
```
docker-compose.yml
.env
nginx.conf
```

### Producción (/opt/arenasurf/)
```
docker-compose.yml
.env
nginx.conf
backup/
logs/
```

## Ejemplo de docker-compose.yml para servidor

```yaml
version: '3.8'

services:
  web:
    image: registry.gitlab.com/tu-usuario/arenasurf:latest
    restart: always
    environment:
      - DATABASE_URL=mysql://arenasurf:${MYSQL_PASSWORD}@db:3306/arenasurf
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - db

  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_DATABASE: arenasurf
      MYSQL_USER: arenasurf
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./backup:/backup

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  static_volume:
  media_volume:
  mysql_data:
```

## Archivo .env para servidores

```env
SECRET_KEY=tu_secret_key_super_segura
MYSQL_PASSWORD=tu_password_mysql_segura
MYSQL_ROOT_PASSWORD=tu_root_password_mysql_segura
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```
