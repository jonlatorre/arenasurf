# Arena Surf - Guía de Deployment CI/CD

Este documento describe cómo configurar y usar el pipeline CI/CD para Arena Surf con GitLab.

## 🚀 Configuración Inicial

### 1. Configurar GitLab Registry

```bash
# Habilitar Container Registry en tu proyecto GitLab
# Ir a Settings > General > Visibility, project features, permissions > Container Registry
```

### 2. Variables de GitLab CI/CD

Ve a tu proyecto en GitLab → Settings → CI/CD → Variables y agrega:

#### Variables Obligatorias
```bash
CI_REGISTRY_PASSWORD    # Tu token de acceso personal
SSH_PRIVATE_KEY        # Clave privada SSH (formato PEM)
STAGING_SERVER         # IP del servidor de staging
STAGING_USER          # Usuario SSH para staging  
PRODUCTION_SERVER     # IP del servidor de producción
PRODUCTION_USER       # Usuario SSH para producción
PRODUCTION_DOMAIN     # Dominio de producción (ejemplo.com)
```

#### Variables Opcionales
```bash
SLACK_WEBHOOK         # Para notificaciones
MYSQL_ROOT_PASSWORD   # Para tests (por defecto: testpassword)
```

### 3. Preparar Servidores

#### En el servidor de staging:
```bash
# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Crear directorio del proyecto
sudo mkdir -p /opt/arenasurf-staging
sudo chown $USER:$USER /opt/arenasurf-staging
cd /opt/arenasurf-staging

# Copiar archivos de configuración
cp docker-compose.prod.yml docker-compose.yml
cp .env.production.example .env
# Editar .env con valores de staging
```

#### En el servidor de producción:
```bash
# Mismo proceso que staging, pero en /opt/arenasurf
sudo mkdir -p /opt/arenasurf
sudo chown $USER:$USER /opt/arenasurf
cd /opt/arenasurf

# Configurar SSL (opcional pero recomendado)
./scripts/setup-ssl.sh tu-dominio.com admin@tu-dominio.com
```

## 📋 Pipeline Stages

### 1. **Test Stage**
- **Lint**: Verifica estilo de código con flake8, black, isort
- **Security**: Escanea vulnerabilidades con safety y bandit  
- **Django Tests**: Ejecuta tests unitarios con cobertura

### 2. **Build Stage**
- **Docker Build**: Construye imagen y la sube al GitLab Registry

### 3. **Deploy Stage**
- **Staging**: Deploy automático en rama `develop`
- **Production**: Deploy manual en rama `main`
- **Rollback**: Capacidad de rollback manual

## 🔄 Flujo de Trabajo

### Desarrollo Normal
```bash
# 1. Crear feature branch
git checkout -b feature/nueva-funcionalidad

# 2. Desarrollar y hacer commits
git add .
git commit -m "feat: agregar nueva funcionalidad"

# 3. Push y crear Merge Request
git push origin feature/nueva-funcionalidad
# Crear MR en GitLab

# 4. El pipeline ejecutará tests automáticamente
# 5. Después del merge a develop, se despliega automáticamente a staging
```

### Deploy a Producción
```bash
# 1. Merge develop a main
git checkout main
git merge develop
git push origin main

# 2. En GitLab, ir a CI/CD > Pipelines
# 3. Encontrar el pipeline de main
# 4. Hacer clic en "Manual" en el job deploy:production
# 5. Confirmar el deployment
```

### Rollback de Emergencia
```bash
# En GitLab CI/CD > Pipelines
# Encontrar un pipeline anterior exitoso
# Ejecutar el job "rollback:production"
```

## 📁 Estructura de Archivos

```
arenasurf/
├── .gitlab-ci.yml              # Configuración del pipeline
├── docker-compose.prod.yml     # Docker Compose para producción
├── .env.production.example     # Variables de entorno de ejemplo
├── scripts/
│   ├── deploy.sh              # Script de deployment manual
│   ├── setup-ssl.sh           # Configuración SSL automática  
│   └── backup.sh              # Script de backup automático
├── nginx/
│   ├── nginx.prod.conf        # Configuración Nginx producción
│   └── proxy_params           # Parámetros proxy Nginx
└── GITLAB_CI_SETUP.md         # Documentación de configuración
```

## 🔧 Scripts Útiles

### Deploy Manual
```bash
# En el servidor
./scripts/deploy.sh production

# Ver logs
./scripts/deploy.sh logs web 100

# Ver estado
./scripts/deploy.sh status

# Backup manual
./scripts/deploy.sh backup production
```

### Configurar SSL
```bash
# En el servidor de producción
./scripts/setup-ssl.sh tu-dominio.com admin@tu-dominio.com
```

### Backup Automático
```bash
# Configurar en crontab del servidor
# Backup diario a las 2:00 AM
0 2 * * * cd /opt/arenasurf && ./scripts/backup.sh daily >> /var/log/backup.log 2>&1

# Backup semanal los domingos a las 3:00 AM  
0 3 * * 0 cd /opt/arenasurf && ./scripts/backup.sh weekly >> /var/log/backup.log 2>&1

# Backup mensual el día 1 a las 4:00 AM
0 4 1 * * cd /opt/arenasurf && ./scripts/backup.sh monthly >> /var/log/backup.log 2>&1
```

## 🔍 Monitoreo y Logs

### Ver logs de la aplicación
```bash
# En el servidor
docker-compose logs -f web
docker-compose logs -f db  
docker-compose logs -f nginx
```

### Health checks
```bash
# Verificar estado de servicios
docker-compose ps

# Verificar conectividad
curl -f https://tu-dominio.com/admin/login/
```

### Métricas de recursos
```bash
# Uso de recursos
docker stats

# Espacio en disco
df -h
du -h /opt/arenasurf
```

## 🚨 Solución de Problemas

### Error en deployment
```bash
# 1. Verificar logs del pipeline en GitLab
# 2. Conectarse al servidor y verificar
docker-compose ps
docker-compose logs web

# 3. Rollback si es necesario
./scripts/deploy.sh rollback production
```

### Error de base de datos
```bash
# Verificar estado de MySQL
docker-compose exec db mysql -u root -p -e "SHOW DATABASES;"

# Restaurar backup si es necesario
docker-compose exec -T db mysql -u root -p arenasurf < backup/db_daily_YYYYMMDD_HHMMSS.sql
```

### Error de SSL
```bash
# Verificar certificados
openssl x509 -in nginx/ssl/fullchain.pem -text -noout

# Renovar certificados
./scripts/setup-ssl.sh tu-dominio.com
```

## 📞 Soporte

Para problemas con el pipeline CI/CD:
1. Revisar logs en GitLab CI/CD > Pipelines
2. Verificar variables de entorno en Settings > CI/CD > Variables  
3. Comprobar conectividad SSH a los servidores
4. Revisar configuración de Docker Registry

Para problemas en producción:
1. Conectarse al servidor via SSH
2. Revisar logs con `docker-compose logs`
3. Verificar estado con `./scripts/deploy.sh status`
4. Considerar rollback si es crítico
