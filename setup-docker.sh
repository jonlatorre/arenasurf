#!/bin/bash

echo "🌊 Configurando Arena Surf Center para Docker..."

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Instálalo desde https://docker.com"
    exit 1
fi

# Verificar que Docker Compose esté instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado."
    exit 1
fi

echo "✅ Docker y Docker Compose están instalados"

# Crear directorios necesarios
mkdir -p media logs static/dist

echo "✅ Directorios creados"

# Dar permisos al script de entrada
chmod +x entrypoint.sh

echo "✅ Permisos configurados"

# Construir la imagen
echo "🔨 Construyendo imagen Docker..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Imagen construida exitosamente"
else
    echo "❌ Error al construir la imagen"
    exit 1
fi

# Levantar los servicios
echo "🚀 Levantando servicios..."
docker-compose up -d

# Esperar un poco para que se inicialicen
echo "⏳ Esperando que los servicios se inicialicen..."
sleep 15

# Verificar que los servicios estén corriendo
if docker-compose ps | grep -q "Up"; then
    echo "✅ Servicios levantados correctamente"
    echo ""
    echo "🎉 ¡Arena Surf Center está listo!"
    echo ""
    echo "📋 Información de acceso:"
    echo "   🌐 Aplicación: http://localhost"
    echo "   👤 Admin: http://localhost/admin/"
    echo "   🔑 Usuario: admin"
    echo "   🔑 Contraseña: admin123"
    echo ""
    echo "�️ Base de datos MySQL:"
    echo "   📊 Host: localhost:3306"
    echo "   🗃️ Base de datos: arenasurf"
    echo "   👤 Usuario: arenasurf"
    echo "   🔑 Contraseña: arenasurf123"
    echo ""
    echo "�📚 Comandos útiles:"
    echo "   make logs     - Ver logs"
    echo "   make shell    - Acceder al contenedor"
    echo "   make down     - Parar servicios"
    echo "   make help     - Ver todos los comandos"
    echo ""
else
    echo "❌ Error al levantar los servicios"
    echo "Ver logs con: docker-compose logs"
    exit 1
fi
