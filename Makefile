PROJECT_NAME=matveyivanov

localup:
	docker compose -f docker/docker-compose.local.yml -p matveyivanov up --remove-orphans $(OPTS)
localbuild:
	docker compose -f docker/docker-compose.local.yml -p matveyivanov build --no-cache

ycbuild:
	docker compose -f docker/docker-compose.yc.yml -p matveyivanov build --no-cache
ycpush:
	docker compose -f docker/docker-compose.yc.yml -p matveyivanov push
publish:
	$(MAKE) ycbuild
	$(MAKE) ycpush

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
