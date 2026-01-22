.PHONY: setup lint format type test test-integration run docker-build compose-up compose-down

VENV ?= .venv
VENV_BIN = $(VENV)/bin
PYTHON = $(VENV_BIN)/python
UV ?= uv

setup:
	$(UV) venv $(VENV)
	$(UV) pip install --python $(PYTHON) -e ".[dev]"

lint:
	$(VENV_BIN)/ruff check src tests
	$(VENV_BIN)/ruff format --check src tests

format:
	$(VENV_BIN)/ruff format src tests

type:
	$(VENV_BIN)/mypy src

test:
	$(VENV_BIN)/pytest tests/unit tests/contract

test-integration:
	$(VENV_BIN)/pytest tests/integration

run:
	$(VENV_BIN)/uvicorn vectorless_rag_service.main:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -f deploy/docker/Dockerfile -t vectorless-rag-service:local .

compose-up:
	docker compose -f deploy/compose/docker-compose.yml up --build

compose-down:
	docker compose -f deploy/compose/docker-compose.yml down -v
