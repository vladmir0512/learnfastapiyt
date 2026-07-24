up:
	docker compose up

down:
	docker compose down

migrate:
	docker exec -it users_app bash -c "alembic upgrade $(MIGRATION)"

upgrade:
	docker exec -it users_app bash -c "alembic upgrade head"


build:
	docker compose up --build

test:
	docker compose -f docker-compose.test.yml up --build -d --remove-orphans
	docker compose -f docker-compose.test.yml exec -T test_users_app bash -c "pytest --tb=short -q --asyncio-mode=auto"
	docker compose -f docker-compose.test.yml exec -T test_tasks_app bash -c "pytest --tb=short -q --asyncio-mode=auto"
	docker compose -f docker-compose.test.yml down
