import csv
import json
from pathlib import Path

META = Path("meta")
FILES = Path("files")
AGG = Path("aggregated")

CSV_FILE = Path("solid_history.csv")


def load_existing_csv():
    if not CSV_FILE.exists():
        return [], []

    with CSV_FILE.open() as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames


def main():
    rows, fieldnames = load_existing_csv()
    index = {(r["commit"], r["file"]): r for r in rows}

    for agg_file in AGG.glob("*.json"):
        data = json.loads(agg_file.read_text())
        commit = data["commit"]

        score_col = next(k for k in data if k.startswith("solid_"))
        score = data[score_col]

        meta = json.loads((META / f"{commit}.json").read_text())
        files = json.loads((FILES / f"{commit}.json").read_text())

        if score_col not in fieldnames:
            fieldnames.append(score_col)

        for file_path in files:
            key = (commit, file_path)

            if key not in index:
                index[key] = {
                    "commit": commit,
                    "date": meta["date"],
                    "file": file_path,
                }

            index[key][score_col] = score

    final_rows = list(index.values())

    with CSV_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["commit", "date", "file"] +
                       [c for c in fieldnames if c.startswith("solid_")]
        )
        writer.writeheader()
        writer.writerows(final_rows)


if __name__ == "__main__":
    main()
