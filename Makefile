PROJECT_NAME=matveyivanov

localup:
	docker compose -f docker/docker-compose.local.yml -p matveyivanov up --remove-orphans $(OPTS)
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
	cd src && poetry run flake8 $(OPTS) ../f-locations
analyze:
	cd src && poetry run mypy $(OPTS) .
	cd src && poetry run mypy $(OPTS) ../f-locations
format:
	cd src && poetry run black $(OPTS) .
	cd src && poetry run black $(OPTS) ../f-locations
formatcheck:
	$(MAKE) format OPTS="--check"
sort:
	cd src && poetry run isort --profile black --filter-files $(OPTS) .
	cd src && poetry run isort --profile black --filter-files $(OPTS) ../f-locations
sortcheck:
	$(MAKE) sort OPTS="--check"

install-git-hooks:
	cd src && poetry run pre-commit install --hook-type pre-commit
uninstall-git-hooks:
	cd src && poetry run pre-commit uninstall -t pre-commit
