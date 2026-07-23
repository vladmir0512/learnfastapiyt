up:
	docker compose up

down:
	docker compose down

migrate:
	docker exec -it fastapi_app bash -c "alembic upgrade $(MIGRATION)"

upgrade:
	docker exec -it fastapi_app bash -c "alembic upgrade head"


build:
	docker compose up --build

test:
	docker compose -f docker-compose.test.yml up --build -d --remove-orphans
	docker compose -f docker-compose.test.yml exec -it test_app bash -c "pytest -s -vvv --asyncio-mode=auto"
	docker compose -f docker-compose.test.yml down
