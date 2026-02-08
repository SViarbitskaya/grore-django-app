# build_thumbnails.py
import os
from PIL import Image

SRC_DIR = os.path.abspath("media/images")          # where your images are
DEST_DIR = os.path.abspath("media/thumbs")  # where thumbnails will go
THUMB_SIZE = (600, 600)

os.makedirs(DEST_DIR, exist_ok=True)

def is_image(filename):
    return filename.lower().endswith((".tiff", ".tif", ".jpg", ".jpeg", ".png"))

count = 0

for root, _, files in os.walk(SRC_DIR):
    for file in files:
        if not is_image(file):
            continue

        src_path = os.path.join(root, file)

        # avoid generating thumbs from thumbs themselves
        if DEST_DIR in src_path:
            continue

        base = os.path.splitext(file)[0]
        thumb_name = base + ".jpg"
        thumb_path = os.path.join(DEST_DIR, thumb_name)

        # if os.path.exists(thumb_path):
        #     print(f"Skip (already exists): {thumb_name}")
        #     continue

        try:
            img = Image.open(src_path)
            img = img.convert("RGB")
            img.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
            img.save(thumb_path, "JPEG", quality=85, optimize=True)

            print(f"Created: {thumb_name}")
            count += 1
        except Exception as e:
            print(f"Failed on {file}: {e}")

print(f"\nDone. {count} thumbnails generated.")
