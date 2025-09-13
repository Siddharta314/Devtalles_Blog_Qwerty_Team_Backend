PROJECT_NAME=devtalles-blog
DOCKER_COMPOSE=docker compose -p $(PROJECT_NAME) -f docker-compose.yml
PYTHON=docker compose exec backend


# =====================
# Comandos principales
# =====================

# Construir imágenes
build:
	$(DOCKER_COMPOSE) build

# Levantar servicios en segundo plano
up:
	$(DOCKER_COMPOSE) up -d

# Detener servicios
down:
	$(DOCKER_COMPOSE) down

# Ver logs del backend
logs:
	$(DOCKER_COMPOSE) logs -f backend

# Ejecutar shell en el contenedor backend
bash-backend:
	$(DOCKER_COMPOSE) exec backend bash

# Ejecutar shell en el contenedor db
bash-db:
	$(DOCKER_COMPOSE) exec db bash

# Aplicar cambios en dependencias
rebuild:
	$(DOCKER_COMPOSE) up -d --build

# Eliminar todo (containers, volúmenes, networks, imágenes huérfanas)
clean:
	$(DOCKER_COMPOSE) down -v --rmi all --remove-orphans

# ---- DATABASE ----
migrate:
	$(PYTHON) alembic upgrade head

mm:
	$(PYTHON) alembic revision --autogenerate -m "New migration"

makemigration:
	$(PYTHON) alembic revision --autogenerate -m "$(m)"

reset-hard:
	$(DOCKER_COMPOSE) down -v
	rm -f alembic/versions/*.py
	$(DOCKER_COMPOSE) up -d db
	$(PYTHON) alembic revision --autogenerate -m "Initial migration"
	$(PYTHON) alembic upgrade head

seed:
	@echo "Poblando base de datos con datos de ejemplo..."
	$(PYTHON) seed.py
	@echo "Seed completado!"