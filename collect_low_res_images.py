import os
import shutil
import pandas as pd

src_root = os.path.abspath("scripts/data/low_res_dir")
dest_root = os.path.abspath("media")

os.makedirs(src_root, exist_ok=True)
os.makedirs(dest_root, exist_ok=True)

# Step 1: Move/copy images
def collect_images(src_root, dest_root):
    all_files = []
    for root, _, files in os.walk(src_root):
        for file in files:
            if file.lower().endswith('jpg'):
                src = os.path.join(root, file)
                dest = os.path.join(dest_root, file)
                shutil.copy2(src, dest)
                all_files.append(file)
    return all_files

low_images = collect_images(src_root, dest_root)
print(len(low_images))

