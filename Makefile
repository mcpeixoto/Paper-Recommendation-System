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
	@echo "    download_checkpoint  📥 Download the checkpoint for the data & index."
	@echo "    create_index      	🏋️‍♀️ Creates the FAISS index by embedding all the papers."
	@echo "    update 		   		🔄 Update the app with the latest papers."
	@echo "    run              	🏃 Run the aplication."
	@echo ""

# Variables
CURRENT_DIR = $(shell pwd)
SHELL = /bin/bash
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

install:
	@echo "Creating conda enviroment..."
	@# Create conda enviroment
	conda env create -f environment.yml -p .env
	@# Activate conda enviroment
	$(CONDA_ACTIVATE) $(CURRENT_DIR)/.env

download:
	@echo "Downloading data..."
	@# Activate conda enviroment
	$(CONDA_ACTIVATE) $(CURRENT_DIR)/.env
	@# Download data
	python data_handling/download.py

download_checkpoint:
	@echo "Downloading checkpoint..."
	@# Activate conda enviroment
	$(CONDA_ACTIVATE) $(CURRENT_DIR)/.env
	@# Download checkpoint
	python data_handling/download_checkpoint.py

create_index:
	@echo "Creating FAISS index..."
	@# Activate conda enviroment
	$(CONDA_ACTIVATE) $(CURRENT_DIR)/.env
	@# Create FAISS index
	python data_handling/create_index.py


update:
	@echo "Updating app..."
	@# Activate conda enviroment
	$(CONDA_ACTIVATE) $(CURRENT_DIR)/.env
	@# Delete old files (arxiv.json and arxiv_processed.csv) if they exist
	@echo "Deleting old files..."
	rm -f data/arxiv.json
	rm -f data/arxiv_processed.csv
	
	make download
	make create_index
	@echo "Done!"

run:
	@echo "Running app..."
	@# Activate conda enviroment
	$(CONDA_ACTIVATE) $(CURRENT_DIR)/.env
	@# Run app
	streamlit run website/app.py 