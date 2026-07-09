import json
import os
import sys

def load_names(path):
    with open(path, "r") as f:
        files = json.load(f)

    # remove extension and normalize case
    return {os.path.splitext(name.strip().lower())[0] for name in files}


def analyze(json1, json2):
    set1 = load_names(json1)
    set2 = load_names(json2)

    matched = set1 & set2
    only_in_1 = set1 - set2
    only_in_2 = set2 - set1

    print("=== Comparison analysis (extensions ignored) ===\n")
    print(f"Total in {json1}: {len(set1)}")
    print(f"Total in {json2}: {len(set2)}\n")

    print(f"Matched filenames: {len(matched)}")
    print(f"Only in {json1}: {len(only_in_1)}")
    print(f"Only in {json2}: {len(only_in_2)}\n")

    # Optional: print details
    print("Files only in first collection:")
    for f in sorted(only_in_1):
        print(" ", f)

    # print("\nFiles only in second collection:")
    # for f in sorted(only_in_2):
    #     print(" ", f)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare.py file1.json file2.json")
        sys.exit(1)

    analyze(sys.argv[1], sys.argv[2])
