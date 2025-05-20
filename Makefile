PROJECT_NAME=matveyivanov

localup:
	docker compose -f docker/docker-compose.local.yml -p matveyivanov up --remove-orphans
localbuild:
	docker compose -f docker/docker-compose.local.yml -p matveyivanov build --no-cache

mainup:
	docker compose -f docker/docker-compose.main.yml -p matveyivanov up --remove-orphans
mainbuild:
	docker compose -f docker/docker-compose.main.yml -p matveyivanov build --no-cache
mainpush:
	docker compose -f docker/docker-compose.main.yml -p matveyivanov push
publish:
	$(MAKE) mainbuild
	$(MAKE) mainpush

test:
	cd src && poetry run pytest $(OPTS) .
lint:
	cd src && poetry run flake8 $(OPTS) .
analyze:
	cd src && poetry run mypy $(OPTS) .
format:
	cd src && poetry run black $(OPTS) .
formatcheck:
	$(MAKE) format OPTS="--check"
sort:
	cd src && poetry run isort --profile black --filter-files $(OPTS) .
sortcheck:
	$(MAKE) sort OPTS="--check"

install-git-hooks:
	cd src && poetry run pre-commit install --hook-type pre-commit
uninstall-git-hooks:
	cd src && poetry run pre-commit uninstall -t pre-commit
