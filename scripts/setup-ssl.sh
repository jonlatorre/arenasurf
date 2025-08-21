#!/bin/bash

# Script para configurar SSL con Let's Encrypt para Arena Surf
# Uso: ./setup-ssl.sh tu-dominio.com

set -e

DOMAIN=${1:-""}
EMAIL=${2:-"admin@$DOMAIN"}

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

if [ -z "$DOMAIN" ]; then
    echo_error "Debes proporcionar un dominio"
    echo "Uso: $0 tu-dominio.com [email@ejemplo.com]"
    exit 1
fi

echo_info "Configurando SSL para $DOMAIN"

# Verificar que Certbot está instalado
if ! command -v certbot &> /dev/null; then
    echo_warning "Certbot no está instalado. Instalando..."
    
    # Instalar certbot según el OS
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y certbot
    elif command -v yum &> /dev/null; then
        sudo yum install -y certbot
    elif command -v brew &> /dev/null; then
        brew install certbot
    else
        echo_error "No se pudo instalar certbot automáticamente"
        echo "Instala certbot manualmente y vuelve a ejecutar este script"
        exit 1
    fi
fi

# Crear directorio para verificación
mkdir -p ./nginx/certbot

# Configurar nginx temporal para verificación
echo_info "Configurando nginx temporal para verificación..."

cat > nginx/nginx.temp.conf << EOF
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name $DOMAIN www.$DOMAIN;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 200 'OK';
            add_header Content-Type text/plain;
        }
    }
}
EOF

# Iniciar nginx temporal
echo_info "Iniciando nginx temporal..."
docker run -d \
    --name nginx-temp \
    -p 80:80 \
    -v $(pwd)/nginx/nginx.temp.conf:/etc/nginx/nginx.conf:ro \
    -v $(pwd)/nginx/certbot:/var/www/certbot \
    nginx:alpine

sleep 5

# Obtener certificado SSL
echo_info "Obteniendo certificado SSL de Let's Encrypt..."
docker run -it --rm \
    -v $(pwd)/nginx/ssl:/etc/letsencrypt \
    -v $(pwd)/nginx/certbot:/var/www/certbot \
    certbot/certbot \
    certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Detener nginx temporal
echo_info "Deteniendo nginx temporal..."
docker stop nginx-temp
docker rm nginx-temp

# Copiar certificados a la ubicación correcta
echo_info "Configurando certificados..."
mkdir -p nginx/ssl

if [ -f "nginx/ssl/live/$DOMAIN/fullchain.pem" ]; then
    cp nginx/ssl/live/$DOMAIN/fullchain.pem nginx/ssl/
    cp nginx/ssl/live/$DOMAIN/privkey.pem nginx/ssl/
    
    echo_success "Certificados SSL configurados correctamente"
else
    echo_error "No se pudieron encontrar los certificados"
    exit 1
fi

# Actualizar configuración de nginx
echo_info "Actualizando configuración de nginx..."
sed -i.bak "s/tu-dominio.com/$DOMAIN/g" nginx/nginx.prod.conf

# Configurar renovación automática
echo_info "Configurando renovación automática..."

cat > scripts/renew-ssl.sh << 'EOF'
#!/bin/bash

# Script para renovar certificados SSL
DOMAIN=$1

echo "Renovando certificados SSL para $DOMAIN..."

# Renovar certificados
docker run --rm \
    -v $(pwd)/nginx/ssl:/etc/letsencrypt \
    -v $(pwd)/nginx/certbot:/var/www/certbot \
    certbot/certbot \
    renew \
    --webroot \
    --webroot-path=/var/www/certbot \
    --quiet

# Copiar certificados actualizados
if [ -f "nginx/ssl/live/$DOMAIN/fullchain.pem" ]; then
    cp nginx/ssl/live/$DOMAIN/fullchain.pem nginx/ssl/
    cp nginx/ssl/live/$DOMAIN/privkey.pem nginx/ssl/
    
    # Recargar nginx
    docker-compose exec nginx nginx -s reload
    
    echo "Certificados renovados exitosamente"
else
    echo "Error: No se encontraron certificados renovados"
    exit 1
fi
EOF

chmod +x scripts/renew-ssl.sh

# Configurar cron job para renovación automática
echo_info "¿Deseas configurar la renovación automática? (y/N)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    # Agregar al crontab para renovar cada 2 meses
    CRON_JOB="0 3 1 */2 * cd $(pwd) && ./scripts/renew-ssl.sh $DOMAIN >> /var/log/ssl-renewal.log 2>&1"
    
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    
    echo_success "Renovación automática configurada (cada 2 meses a las 3:00 AM)"
fi

# Limpiar archivos temporales
rm -f nginx/nginx.temp.conf

echo_success "¡SSL configurado exitosamente para $DOMAIN!"
echo_info "Ahora puedes:"
echo_info "1. Actualizar tu archivo .env con el dominio correcto"
echo_info "2. Ejecutar: docker-compose -f docker-compose.prod.yml up -d"
echo_info "3. Verificar que el sitio carga con HTTPS"

echo_warning "Recuerda:"
echo_warning "- Asegúrate de que tu dominio apunte a este servidor"
echo_warning "- Los certificados se renovarán automáticamente cada 2 meses"
echo_warning "- Los logs de renovación estarán en /var/log/ssl-renewal.log"
