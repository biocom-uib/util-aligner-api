alembic:
	docker-compose run --rm api alembic $(cmd)

sql:
	docker-compose run --rm mysql mysql -h mysql -u puser --password protein_db

clean:
	docker-compose down -v --remove-orphans

ipython:
	docker-compose run --rm api ipython