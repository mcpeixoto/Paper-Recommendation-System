# Makefile for the the Paper Recomendation System
# Author: Miguel Caçador Peixoto

# Help message
help:
	@echo "Makefile for the the Paper Recomendation System"
	@echo ""
	@echo "Usage:"
	@echo "    make <target>"
	@echo ""
	@echo "Targets:"
	@echo "    help                 💬 This help message"
	@echo "    install              📦 Create conda enviroment e install dependencies."
	@echo "    download             📥 Download data from the web."
	@echo "    create_index      	🏋️‍♀️ Creates the FAISS index by embedding all the papers. WARNING: This will overwrite any existing index."
	@echo "    run              	🏃 Run the aplication."
	@echo ""

# Variables
CURRENT_DIR = $(shell pwd)
SHELL = /bin/bash
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

install:
	@echo "Creating conda enviroment..."
	# Create conda enviroment
	conda env create -f environment.yml -p .env
	# Activate conda enviroment
	$(CONDA_ACTIVATE) $(CURRENT_DIR)/.env

download:
	@echo "Downloading data..."
	@# Activate conda enviroment
	$(CONDA_ACTIVATE) $(CURRENT_DIR)/.env
	@# Download data
	python data_handling/download.py

create_index:
	@echo "Creating FAISS index..."
	# Activate conda enviroment
	conda activate $(CURRENT_DIR)/.env
	# Create FAISS index
	python utils/create_index.py

