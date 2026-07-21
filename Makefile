.PHONY: up build test

up:
	docker compose up

build:
	docker compose up --build

test:
	docker compose -f docker-compose.test.yml up --build -d --remove-orphans
	docker compose -f docker-compose.test.yml run --rm test_app pytest --maxfail=5 -v
	docker compose -f docker-compose.test.yml down