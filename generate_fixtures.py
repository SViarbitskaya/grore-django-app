import os
import json

# Paths
THUMBS_DIR = os.path.abspath("media/thumbs")   # low-res JPG thumbnails
IMAGES_DIR = os.path.abspath("media/images")  # high-res TIFFs
ZOOM_DIR = os.path.abspath("media/zoom")      # high-res JPGs for zoom

# Scan folders

# All thumbnail JPGs
thumb_files = [f for f in os.listdir(THUMBS_DIR) if f.lower().endswith(".jpg")]
# Base names of thumbnail files
thumb_bases = {os.path.splitext(f)[0] for f in thumb_files}

# All high-res TIFFs
high_res_files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith((".tif", ".tiff"))]
# Base names of high-res images
high_res_bases = {os.path.splitext(f)[0] for f in high_res_files}

# Prepare fixture
fixture = []
pk_counter = 1

# First, add all thumbnail images
for thumb_file in sorted(thumb_files):
    base = os.path.splitext(thumb_file)[0]
    has_high_res = base in high_res_bases

    file_field = f"images/{base}.tiff" if has_high_res else f"thumbs/{thumb_file}"
    thumbnail_field = f"thumbs/{thumb_file}"
    zoom_field = f"zoom/{base}.jpg" if has_high_res else ""

    fixture.append({
        "model": "images.image",
        "pk": pk_counter,
        "fields": {
            "identifier": base,
            "slug": base,
            "note": "",
            "note_en": "test_en",
            "note_fr": "test_fr",
            "pub_date": "2026-01-11 00:00:00",
            "modif_date": "2026-01-11 00:00:00",
            "file": file_field,
            "thumbnail": thumbnail_field,
            "zoom": zoom_field,
            "high_res": has_high_res
        }
    })
    pk_counter += 1

# Then, add high-res images that do NOT have a thumbnail yet
for hr_file in high_res_files:
    base = os.path.splitext(hr_file)[0]
    if base in thumb_bases:
        continue  # already added
    # Only high-res image, no thumbnail
    fixture.append({
        "model": "images.image",
        "pk": pk_counter,
        "fields": {
            "identifier": base,
            "slug": base,
            "note": "",
            "note_en": "test_en",
            "note_fr": "test_fr",
            "pub_date": "2026-01-11 00:00:00",
            "modif_date": "2026-01-11 00:00:00",
            "file": f"images/{hr_file}",
            "thumbnail": "",
            "zoom": f"zoom/{base}.jpg",
            "high_res": True
        }
    })
    pk_counter += 1

# Save fixture to JSON
output_file = "media_fixture.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(fixture, f, ensure_ascii=False, indent=4)

print(f"Fixture created with {len(fixture)} images -> {output_file}")