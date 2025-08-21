#!/bin/bash

# Script de backup automático para Arena Surf
# Uso: ./backup.sh [daily|weekly|monthly]

set -e

BACKUP_TYPE=${1:-daily}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backup"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Crear directorio de backup si no existe
mkdir -p $BACKUP_DIR

echo_info "Iniciando backup $BACKUP_TYPE - $TIMESTAMP"

# Backup de base de datos
echo_info "Creando backup de base de datos..."
docker-compose exec -T db mysqldump \
    -u root \
    -p$MYSQL_ROOT_PASSWORD \
    --single-transaction \
    --routines \
    --triggers \
    --all-databases > "$BACKUP_DIR/db_${BACKUP_TYPE}_${TIMESTAMP}.sql"

if [ $? -eq 0 ]; then
    echo_success "Backup de base de datos creado: db_${BACKUP_TYPE}_${TIMESTAMP}.sql"
else
    echo_error "Error al crear backup de base de datos"
    exit 1
fi

# Backup de archivos media
echo_info "Creando backup de archivos media..."
if [ -d "./media" ] && [ "$(ls -A ./media)" ]; then
    tar -czf "$BACKUP_DIR/media_${BACKUP_TYPE}_${TIMESTAMP}.tar.gz" ./media/
    echo_success "Backup de media creado: media_${BACKUP_TYPE}_${TIMESTAMP}.tar.gz"
else
    echo_warning "No hay archivos media para respaldar"
fi

# Backup de configuración
echo_info "Creando backup de configuración..."
tar -czf "$BACKUP_DIR/config_${BACKUP_TYPE}_${TIMESTAMP}.tar.gz" \
    --exclude='./backup' \
    --exclude='./logs' \
    --exclude='./.git' \
    --exclude='./venv' \
    --exclude='./env' \
    --exclude='./__pycache__' \
    --exclude='./media' \
    --exclude='./static' \
    ./

echo_success "Backup de configuración creado: config_${BACKUP_TYPE}_${TIMESTAMP}.tar.gz"

# Comprimir backup de base de datos
echo_info "Comprimiendo backup de base de datos..."
gzip "$BACKUP_DIR/db_${BACKUP_TYPE}_${TIMESTAMP}.sql"
echo_success "Base de datos comprimida: db_${BACKUP_TYPE}_${TIMESTAMP}.sql.gz"

# Crear checksum para verificación
echo_info "Creando checksums..."
cd $BACKUP_DIR
find . -name "*_${TIMESTAMP}.*" -type f -exec sha256sum {} \; > "checksums_${BACKUP_TYPE}_${TIMESTAMP}.txt"
cd ..

echo_success "Checksums creados: checksums_${BACKUP_TYPE}_${TIMESTAMP}.txt"

# Limpiar backups antiguos
echo_info "Limpiando backups antiguos (más de $RETENTION_DAYS días)..."
find $BACKUP_DIR -name "*_${BACKUP_TYPE}_*" -type f -mtime +$RETENTION_DAYS -delete

CLEANED_COUNT=$(find $BACKUP_DIR -name "*_${BACKUP_TYPE}_*" -type f -mtime +$RETENTION_DAYS | wc -l)
if [ $CLEANED_COUNT -gt 0 ]; then
    echo_success "Se eliminaron $CLEANED_COUNT archivos de backup antiguos"
else
    echo_info "No hay backups antiguos para eliminar"
fi

# Mostrar resumen
echo_info "=== RESUMEN DEL BACKUP ==="
echo_info "Tipo: $BACKUP_TYPE"
echo_info "Timestamp: $TIMESTAMP"
echo_info "Archivos creados:"
ls -lh $BACKUP_DIR/*_${TIMESTAMP}.*

# Calcular tamaño total
TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
echo_info "Tamaño total del directorio backup: $TOTAL_SIZE"

echo_success "¡Backup completado exitosamente!"

# Opcional: Enviar backup a almacenamiento externo
if [ ! -z "$AWS_S3_BUCKET" ]; then
    echo_info "Enviando backup a S3..."
    aws s3 cp $BACKUP_DIR/ s3://$AWS_S3_BUCKET/arenasurf/backups/ --recursive --include "*_${TIMESTAMP}.*"
    echo_success "Backup enviado a S3"
fi

# Opcional: Notificación
if [ ! -z "$SLACK_WEBHOOK" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"✅ Backup $BACKUP_TYPE de Arena Surf completado - $TIMESTAMP\"}" \
        $SLACK_WEBHOOK
fi
