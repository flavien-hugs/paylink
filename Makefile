COMPOSE = docker compose
API = $(COMPOSE) exec backend poetry run

.PHONY: help run up down build restart logs ps migrate makemigration seed test fernet-key api-shell

help:
	@echo "PayLink — monorepo commands"
	@echo "  make run            Start all services (no rebuild)"
	@echo "  make up             Build & start all services (postgres, backend, payment-ui, admin-ui)"
	@echo "  make down           Stop all services"
	@echo "  make build          Rebuild images"
	@echo "  make restart        Restart all services"
	@echo "  make logs           Tail logs"
	@echo "  make migrate        Apply DB migrations (alembic upgrade head)"
	@echo "  make makemigration m='msg'  Autogenerate a migration"
	@echo "  make seed           Seed admin + demo entity"
	@echo "  make test           Run backend tests"
	@echo "  make fernet-key     Generate a Fernet key for FERNET_KEY"

run:
	$(COMPOSE) up -d

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

migrate:
	$(API) alembic upgrade head

makemigration:
	$(API) alembic revision --autogenerate -m "$(m)"

seed:
	$(API) app seed

test:
	$(COMPOSE) run --rm backend poetry run pytest

fernet-key:
	@python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

api-shell:
	$(COMPOSE) exec backend bash
