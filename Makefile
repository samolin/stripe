.PHONY: install
install:
	@poetry install

.PHONY: start
start:
	@docker-compose -f docker-compose.yaml up -d
