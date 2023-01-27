import os
from os.path import join, basename, exists
import glob



data_dir = 'data'

# If the data directory doesn't exist, create it
if not exists(data_dir):
    os.makedirs(data_dir)

