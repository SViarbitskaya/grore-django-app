import pandas as pd
import json
from datetime import datetime
import os

# Paths
CSV_FILE = "classeur_clean.csv"
HIGH_JSON = "high_res_filenames.json"
LOW_JSON = "low_res_filenames.json"
OUTPUT_FIXTURE = "image_fixture.json"

# Load CSV
df = pd.read_csv(CSV_FILE)
df["identifier"] = df["identifier"].astype(str).str.strip()

# Load JSON lists
with open(HIGH_JSON, "r", encoding="utf-8") as f:
    high_res_files = set(json.load(f))  # assume it's a list of filenames

with open(LOW_JSON, "r", encoding="utf-8") as f:
    low_res_files = set(json.load(f))

# Prepare fixture
fixture = []
pk_counter = 1
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for _, row in df.iterrows():
    base = row["identifier"]

    # Determine high-res file
    high_res_name = f"{base}.tiff"
    has_high_res = high_res_name in high_res_files
    file_field = f"images/{high_res_name}" if has_high_res else ""

    # Determine low-res thumbnail
    thumb_name = f"{base}.jpg"
    has_low_res = thumb_name in low_res_files
    thumbnail_field = f"thumbs/{thumb_name}" if has_low_res else ""

    # Zoom field, optional: set only if high-res exists
    zoom_field = f"zoom/{base}.jpg" if has_high_res else ""

    fixture.append({
        "model": "images.image",
        "pk": pk_counter,
        "fields": {
            "identifier": base,
            "slug": base,
            "note": row.get("note", ""),
            "note_en": row.get("note_en", "test_en"),
            "note_fr": row.get("note_fr", "test_fr"),
            "pub_date": NOW,
            "modif_date": NOW,
            "file": file_field,
            "thumbnail": thumbnail_field,
            "zoom": zoom_field,
            "high_res": has_high_res
        }
    })
    pk_counter += 1

# Save fixture
with open(OUTPUT_FIXTURE, "w", encoding="utf-8") as f:
    json.dump(fixture, f, ensure_ascii=False, indent=4)

print(f"Created fixture with {len(fixture)} entries -> {OUTPUT_FIXTURE}")
