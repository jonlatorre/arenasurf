#!/bin/bash

# Script de deployment para Arena Surf
# Uso: ./deploy.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para verificar si el servicio está ejecutándose
check_service() {
    local service_url=$1
    local timeout=60
    local counter=0
    
    echo_info "Verificando servicio en $service_url..."
    
    while [ $counter -lt $timeout ]; do
        if curl -s -f "$service_url" > /dev/null 2>&1; then
            echo_success "Servicio respondiendo correctamente"
            return 0
        fi
        
        counter=$((counter + 5))
        echo_info "Esperando... ($counter/$timeout)"
        sleep 5
    done
    
    echo_error "El servicio no responde después de $timeout segundos"
    return 1
}

# Función de backup
backup_database() {
    local env=$1
    echo_info "Creando backup de la base de datos..."
    
    if [ "$env" = "production" ]; then
        docker-compose exec -T db mysqldump -u root -p$MYSQL_ROOT_PASSWORD arenasurf > "backup_$(date +%Y%m%d_%H%M%S).sql"
    elif [ "$env" = "staging" ]; then
        docker-compose exec -T db mysqldump -u root -p$MYSQL_ROOT_PASSWORD arenasurf_staging > "backup_staging_$(date +%Y%m%d_%H%M%S).sql"
    fi
    
    echo_success "Backup creado exitosamente"
}

# Función principal de deployment
deploy() {
    local env=$1
    
    echo_info "Iniciando deployment para $env..."
    
    # Verificar que existe docker-compose.yml
    if [ ! -f "docker-compose.yml" ]; then
        echo_error "No se encontró docker-compose.yml en el directorio actual"
        exit 1
    fi
    
    # Verificar que existe .env
    if [ ! -f ".env" ]; then
        echo_error "No se encontró .env en el directorio actual"
        exit 1
    fi
    
    # Backup de base de datos (solo para producción)
    if [ "$env" = "production" ]; then
        backup_database $env
    fi
    
    # Pull de las nuevas imágenes
    echo_info "Descargando nuevas imágenes..."
    docker-compose pull
    
    # Restart de los servicios
    echo_info "Reiniciando servicios..."
    docker-compose up -d
    
    # Ejecutar migraciones
    echo_info "Ejecutando migraciones..."
    docker-compose exec -T web python manage.py migrate
    
    # Recopilar archivos estáticos
    echo_info "Recopilando archivos estáticos..."
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    # Limpiar imágenes antiguas
    echo_info "Limpiando imágenes no utilizadas..."
    docker image prune -f
    
    # Verificar que el servicio está funcionando
    if [ "$env" = "production" ]; then
        check_service "https://$PRODUCTION_DOMAIN/admin/"
    elif [ "$env" = "staging" ]; then
        check_service "http://localhost:8000/admin/"
    fi
    
    echo_success "Deployment de $env completado exitosamente!"
}

# Función de rollback
rollback() {
    local env=$1
    
    echo_warning "Iniciando rollback para $env..."
    echo_warning "Esta acción restaurará la versión anterior"
    
    read -p "¿Estás seguro? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo_info "Ejecutando rollback..."
        
        # Detener servicios actuales
        docker-compose down
        
        # Restaurar imagen anterior (asumiendo que existe un tag :previous)
        docker tag registry.gitlab.com/tu-usuario/arenasurf:previous registry.gitlab.com/tu-usuario/arenasurf:latest
        
        # Reiniciar servicios
        docker-compose up -d
        
        echo_success "Rollback completado"
    else
        echo_info "Rollback cancelado"
    fi
}

# Función de limpieza
cleanup() {
    echo_info "Ejecutando limpieza del sistema..."
    
    # Limpiar contenedores parados
    echo_info "Limpiando contenedores parados..."
    docker container prune -f
    
    # Limpiar imágenes no utilizadas
    echo_info "Limpiando imágenes no utilizadas..."
    docker image prune -f
    
    # Limpiar volúmenes no utilizados
    echo_info "Limpiando volúmenes no utilizados..."
    docker volume prune -f
    
    # Limpiar networks no utilizados
    echo_info "Limpiando networks no utilizados..."
    docker network prune -f
    
    echo_success "Limpieza completada"
}

# Función de logs
show_logs() {
    local service=${1:-web}
    local lines=${2:-100}
    
    echo_info "Mostrando últimas $lines líneas de logs para $service..."
    docker-compose logs --tail=$lines -f $service
}

# Función de status
show_status() {
    echo_info "Estado de los servicios:"
    docker-compose ps
    
    echo_info "Uso de recursos:"
    docker stats --no-stream
}

# Script principal
case $1 in
    "staging"|"production")
        deploy $1
        ;;
    "rollback")
        rollback ${2:-production}
        ;;
    "cleanup")
        cleanup
        ;;
    "logs")
        show_logs $2 $3
        ;;
    "status")
        show_status
        ;;
    "backup")
        backup_database ${2:-production}
        ;;
    *)
        echo "Uso: $0 {staging|production|rollback|cleanup|logs|status|backup}"
        echo ""
        echo "Comandos disponibles:"
        echo "  staging         - Deploy en ambiente de staging"
        echo "  production      - Deploy en ambiente de producción"
        echo "  rollback [env]  - Rollback a versión anterior"
        echo "  cleanup         - Limpiar imágenes y contenedores no utilizados"
        echo "  logs [service] [lines] - Mostrar logs de un servicio"
        echo "  status          - Mostrar estado de servicios y recursos"
        echo "  backup [env]    - Crear backup de base de datos"
        echo ""
        echo "Ejemplos:"
        echo "  $0 production"
        echo "  $0 logs web 200"
        echo "  $0 rollback staging"
        exit 1
        ;;
esac
