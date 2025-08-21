#!/bin/bash

# Función para esperar a que la base de datos esté disponible
wait_for_db() {
    echo "Esperando a que MySQL esté disponible..."
    while ! python manage.py check --database default 2>/dev/null; do
        echo "MySQL no disponible, esperando..."
        sleep 1
    done
    echo "MySQL disponible!"
}

# Función para aplicar migraciones
apply_migrations() {
    echo "Aplicando migraciones..."
    python manage.py migrate --noinput
}

# Función para recopilar archivos estáticos
collect_static() {
    echo "Recopilando archivos estáticos..."
    python manage.py collectstatic --noinput --clear
    
    # Copiar archivos CSS específicos si existen
    if [ -f "static/dist/css/app.css" ]; then
        echo "Copiando archivo CSS personalizado..."
        mkdir -p /app/static/css
        cp static/dist/css/app.css /app/static/css/app.css
        echo "Archivo CSS copiado exitosamente"
    fi
}

# Función para crear superusuario si no existe
create_superuser() {
    echo "Verificando superusuario..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@arenasurf.com',
        password='admin123'
    )
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"
}

# Función para cargar datos iniciales
load_fixtures() {
    echo "Cargando datos iniciales..."
    if [ -f "fixtures/sites.json" ]; then
        python manage.py loaddata fixtures/sites.json
        echo "Datos iniciales cargados"
    fi
}

# Función principal
main() {
    echo "🌊 Iniciando Arena Surf Center..."
    
    # Esperar a la base de datos
    wait_for_db
    
    # Aplicar migraciones
    apply_migrations
    
    # Recopilar archivos estáticos
    collect_static
    
    # Crear superusuario
    create_superuser
    
    # Cargar datos iniciales
    load_fixtures
    
    echo "🏄‍♂️ Arena Surf Center listo!"
    
    # Ejecutar el comando pasado como argumentos
    exec "$@"
}

# Ejecutar función principal con todos los argumentos
main "$@"
