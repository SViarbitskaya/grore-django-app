import pandas as pd
import json
from datetime import datetime

# -------------------------------
# CONFIG
# -------------------------------
CSV_FILE = "classeur.csv"
OUTPUT_JSON = "classeur.json"
IMAGE_FOLDER = "images/"
THUMB_FOLDER = "thumbs/"

# -------------------------------
# LOAD CSV
# -------------------------------
df = pd.read_csv(CSV_FILE)

# Strip whitespace and replace non-breaking spaces for all string columns
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].astype(str).str.replace("\u00a0", " ").str.strip()

# Ensure 'identifier' has no spaces
df["identifier"] = df["identifier"].str.replace(" ", "").str.strip()

# -------------------------------
# CREATE FIXTURES
# -------------------------------
fixtures_list = []

for i, row in df.iterrows():
    entry = {
        "model": "images.image",
        "pk": i + 1,
        "fields": {
            "identifier": row["identifier"],
            "slug": row["identifier"],
            "note": "",
            "note_en": row.get("note_en", ""),
            "note_fr": row.get("note_fr", ""),
            "pub_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modif_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file": IMAGE_FOLDER + row["identifier"] + ".tiff",
            "thumbnail": THUMB_FOLDER + row["identifier"] + ".jpg"
        }
    }
    fixtures_list.append(entry)

# -------------------------------
# SAVE TO JSON
# -------------------------------
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(fixtures_list, f, ensure_ascii=False, indent=2)

print(f"✅ Django fixture created: {OUTPUT_JSON} ({len(fixtures_list)} entries)")
