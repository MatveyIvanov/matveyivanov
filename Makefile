PROJECT_NAME=matveyivanov

localup:
	docker compose -f docker/docker-compose.local.yml -p matveyivanov up --remove-orphans
localbuild:
	docker compose -f docker/docker-compose.local.yml -p matveyivanov build --no-cache
developup:
	docker compose -f docker/docker-compose.yml -p matveyivanov up --remove-orphans
developbuild:
	docker compose -f docker/docker-compose.yml -p matveyivanov build --no-cache
mainup:
	docker compose -f docker/docker-compose.main.yml -p matveyivanov up --remove-orphans
mainbuild:
	docker compose -f docker/docker-compose.main.yml -p matveyivanov build --no-cache
test:
	docker exec -it $(PROJECT_NAME)-asgi pytest .
lint:
	docker exec -it $(PROJECT_NAME)-asgi flake8 .
typecheck:
	docker exec -it $(PROJECT_NAME)-asgi mypy .
black:
	docker exec -it $(PROJECT_NAME)-asgi black .
isort:
	docker exec -it $(PROJECT_NAME)-asgi isort . --profile black --filter-files
makemigrations:
	docker exec -it $(PROJECT_NAME)-asgi alembic revision --autogenerate -m "$(MESSAGE)"
migrate:
	docker exec -it $(PROJECT_NAME)-asgi alembic upgrade head
