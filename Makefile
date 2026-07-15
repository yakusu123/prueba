.PHONY: install run lint db scrape clean

install:
	conda env create -f environment.yml

db:
	python src/models.py

scrape:
	python src/scrapping.py

run: db scrape

lint:
	ruff check --fix .
	ruff format .

clean:
	rm -f prueba.db
	rm -rf src/__pycache__
	rm -rf .ruff_cache