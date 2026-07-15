# Variables
PYTHON = python
CONDA_ENV = scraper_env

# Declaramos los comandos que no son archivos físicos
.PHONY: install db scrape run clean

# 1. Instala el entorno virtual con Conda
install:
	conda env create -f environment.yml

# 2. Crea la base de datos (Ejecuta models.py dentro de src)
db:
	$(PYTHON) src/models.py

# 3. Ejecuta únicamente el scraper (Ejecuta scrapping.py dentro de src)
scrape:
	$(PYTHON) src/scrapping.py

# 4. Flujo completo: Crea la base de datos y luego ejecuta el scraper
run: db scrape

# 5. Limpieza: Borra la base de datos y cachés
clean:
	rm -f prueba.db
	rm -rf src/__pycache__
	rm -rf __pycache__