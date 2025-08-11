SHELL := /bin/bash

.PHONY: help run stop clean test

help:
	@echo "Commands:"
	@echo "  run    : Run the application using Docker Compose"
	@echo "  stop   : Stop the application"
	@echo "  clean  : Remove temporary files"
	@echo "  test   : Run tests"

run:
	docker compose up --build -d

stop:
	docker compose down

clean:
	@echo "Cleaning up..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

test:
	@echo "Running tests..."
	# Add test commands here
