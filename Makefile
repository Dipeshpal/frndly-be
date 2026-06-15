.PHONY: up down dev migrate reset

up:
	docker compose up -d

down:
	docker compose down

dev:
	docker compose up -d && uv run uvicorn app.main:app --reload --port 8004

migrate:
	uv run alembic upgrade head

reset:
	docker compose down -v && docker compose up -d
	sleep 3
	uv run alembic upgrade head
