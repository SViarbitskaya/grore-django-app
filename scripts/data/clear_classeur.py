import pandas as pd

df = pd.read_csv("classeur.csv")

df["identifier"] = df["identifier"].astype(str).str.strip().str.replace("\u00a0", "")

for col in ["note_fr", "note_en"]:
    df[col] = df[col].astype(str)
    df[col] = df[col].str.replace("\u00a0", " ")  # non-breaking spaces
    df[col] = df[col].str.replace("’", "'")      # curly apostrophes
    df[col] = df[col].str.replace("“", '"').str.replace("”", '"')  # curly quotes
    df[col] = df[col].str.strip()  # remove leading/trailing spaces

df.to_csv("classeur_clean.csv", index=False, encoding="utf-8")

print("Cleaned CSV saved as 'classeur_clean.csv'")