import os
from PIL import Image

TIFF_DIR = os.path.abspath("media/tiffs")
ZOOM_DIR = os.path.abspath("media/zoom")

os.makedirs(ZOOM_DIR, exist_ok=True)

for filename in os.listdir(TIFF_DIR):
    if not filename.lower().endswith((".tif", ".tiff")):
        continue

    src_path = os.path.join(TIFF_DIR, filename)
    base_name = os.path.splitext(filename)[0]
    dst_path = os.path.join(ZOOM_DIR, base_name + ".jpg")

    # Skip if already exists
    if os.path.exists(dst_path):
        print(f"Skipping (already exists): {dst_path}")
        continue

    try:
        img = Image.open(src_path)
        img = img.convert("RGB")

        # Resize for zoom view (large but browser-friendly)
        img.thumbnail((3000, 3000), Image.Resampling.LANCZOS)

        img.save(dst_path, "JPEG", quality=90, optimize=True)
        print(f"Created: {dst_path}")

    except Exception as e:
        print(f"Failed on {filename}: {e}")

print("Done.")
