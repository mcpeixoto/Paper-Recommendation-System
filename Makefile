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
	@echo "    create_index      	🏋️‍♀️ Create the FAISS index by embedding all the papers."
	@echo "    run              	🏃 Run the aplication."
	@echo ""

# Variables
CURRENT_DIR = $(shell pwd)
SHELL = /bin/bash

install:
	@echo "Creating conda enviroment..."
	# Create conda enviroment
	conda env create -f environment.yml -p .env
	# Activate conda enviroment
	conda activate $(CURRENT_DIR)/.env

download:
	@echo "Downloading data..."
	# Download data
	python data_handling/download.py	

