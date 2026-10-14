import os
import json

# Path to the folder on your external drive
# folder_path = "/run/media/mumu/Backup Plus/GRORE_IMAGES_catalogue_HTE_DEF"  # <-- change this
folder_path = os.path.abspath("media")

# List to store file names
image_files = []

# Walk through the folder (non-recursive, just folder contents)
for entry in os.listdir(folder_path):
    full_path = os.path.join(folder_path, entry)
    if os.path.isfile(full_path) and entry.lower().endswith((".tif", ".tiff", ".jpg", ".jpeg")):
        image_files.append(entry)

# Save to JSON
output_path = "low_res_filenames.json"
with open(output_path, "w") as f:
    json.dump(image_files, f, indent=4)

print(f"{len(image_files)} Image file names saved to {output_path}")
