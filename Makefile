up:
	docker compose up

down:
	docker compose down

build:
	docker compose up --build

test:
	docker compose -f docker-compose.test.yml up --build -d --remove-orphans
	docker compose -f docker-compose.test.yml exec -it test_app bash -c "pytest --maxfail=5 -v"
	docker compose -f docker-compose.test.yml down