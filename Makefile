run:
	uvicorn main:app --reload

migrate:
	alembic upgrade head

build:
	docker build -t clash-imposter .

docker-run:
	docker run -d --rm --name clash-cont -p 80:8000 clash-imposter