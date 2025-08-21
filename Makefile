.PHONY: help build up down logs shell migrate collectstatic createsuperuser dev prod clean

# Variables
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_DEV = docker-compose -f docker-compose.dev.yml
SERVICE = web

help: ## Mostrar ayuda
	@echo "🌊 Arena Surf Center - Comandos Docker"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Construir la imagen Docker
	$(DOCKER_COMPOSE) build

up: ## Levantar los servicios en producción
	$(DOCKER_COMPOSE) up -d

down: ## Parar todos los servicios
	$(DOCKER_COMPOSE) down

logs: ## Ver logs de la aplicación
	$(DOCKER_COMPOSE) logs -f $(SERVICE)

shell: ## Acceder al shell del contenedor
	$(DOCKER_COMPOSE) exec $(SERVICE) /bin/bash

migrate: ## Ejecutar migraciones
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py migrate

collectstatic: ## Recopilar archivos estáticos
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py collectstatic --noinput

createsuperuser: ## Crear superusuario
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py createsuperuser

makemigrations: ## Crear nuevas migraciones
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py makemigrations

dev: ## Modo desarrollo (con recarga automática)
	$(DOCKER_COMPOSE_DEV) up --build

dev-down: ## Parar modo desarrollo
	$(DOCKER_COMPOSE_DEV) down

dev-logs: ## Ver logs en modo desarrollo
	$(DOCKER_COMPOSE_DEV) logs -f $(SERVICE)

dev-shell: ## Shell en modo desarrollo
	$(DOCKER_COMPOSE_DEV) exec $(SERVICE) /bin/bash

prod: ## Levantar en modo producción
	$(DOCKER_COMPOSE) up -d --build

restart: ## Reiniciar servicios
	$(DOCKER_COMPOSE) restart

clean: ## Limpiar contenedores e imágenes no utilizados
	docker system prune -f
	docker volume prune -f

backup-db: ## Hacer backup de la base de datos (MySQL)
	$(DOCKER_COMPOSE) exec db mysqldump -u arenasurf -parenasurf123 arenasurf > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restaurar base de datos MySQL (especificar BACKUP_FILE=archivo)
	$(DOCKER_COMPOSE) exec -T db mysql -u arenasurf -parenasurf123 arenasurf < $(BACKUP_FILE)

test: ## Ejecutar tests
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py test

coverage: ## Ejecutar tests con cobertura
	$(DOCKER_COMPOSE) exec $(SERVICE) coverage run --source='.' manage.py test
	$(DOCKER_COMPOSE) exec $(SERVICE) coverage report

install: ## Primera instalación (build + migrate + superuser)
	make build
	make up
	sleep 10
	make migrate
	@echo "🏄‍♂️ ¡Arena Surf Center instalado! Accede a http://localhost"
	@echo "Usuario admin: admin / admin123"

status: ## Ver estado de los servicios
	$(DOCKER_COMPOSE) ps

mysql-shell: ## Acceder al shell de MySQL
	$(DOCKER_COMPOSE) exec db mysql -u arenasurf -parenasurf123 arenasurf

mysql-root: ## Acceder a MySQL como root
	$(DOCKER_COMPOSE) exec db mysql -u root -proot123

mysql-logs: ## Ver logs de MySQL
	$(DOCKER_COMPOSE) logs -f db
