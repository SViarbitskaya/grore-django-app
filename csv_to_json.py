"""csv-to_json.py
Creates a json fixure for images from the 'classeur.csv' file, save to classeur.json.
"""

import pandas as pd
from datetime import datetime
import json
from json import load, dumps
import re

df = pd.read_csv('classeur.csv')

result_json = df.to_json(orient='records', force_ascii=False)

# Replace non-breaking spaces with regular spaces
result_json = result_json.replace('\u00a0', '')
result_json = result_json.replace('’', "'")

# Decode Unicode escape sequences using json.loads
decoded_json = json.loads(result_json)

fixtures_list = []

for i, row in enumerate(decoded_json):
    entry = {
        "model": "images.image",
            "pk": i+1,
            "fields": {
                "identifier": row["identifier"],
                "slug": row["identifier"],       
                "note": "",
                "note_en": row["note_en"],
                "note_fr": row["note_fr"],
                "pub_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "modif_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "file": row["identifier"] +".jpg"
        }
}
fixtures_list.append(entry)

# Convert to JSON string with readable strings using json.dumps
file_path = 'classeur.json'
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(fixtures_list, file, ensure_ascii=False)

print("Created classeur.json. now you can load the fixtures!")