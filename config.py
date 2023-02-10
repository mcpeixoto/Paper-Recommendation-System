import os
from os.path import join, basename, exists
import glob


data_dir = "data"
thumbnail_dir = join(data_dir, "thumbnails")
testing = False

# If the directorys doesn't exist, create it
for dir in [data_dir, thumbnail_dir]:
    if not exists(dir):
        os.mkdir(dir)
