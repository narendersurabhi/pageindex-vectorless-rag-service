.PHONY: setup lint format type test test-integration run docker-build compose-up compose-down

setup:
	uv pip install -e ".[dev]"

lint:
	ruff check src tests
	ruff format --check src tests

format:
	ruff format src tests

type:
	mypy src

test:
	pytest tests/unit tests/contract

test-integration:
	pytest tests/integration

run:
	uvicorn vectorless_rag_service.main:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -f deploy/docker/Dockerfile -t vectorless-rag-service:local .

compose-up:
	docker compose -f deploy/compose/docker-compose.yml up --build

compose-down:
	docker compose -f deploy/compose/docker-compose.yml down -v
