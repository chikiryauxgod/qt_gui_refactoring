import csv
import json
from pathlib import Path

META = Path("meta")
AGG = Path("aggregated")
CSV_FILE = Path("solid_history.csv")


def load_existing_csv():
    if not CSV_FILE.exists():
        return [], ["commit", "date", "file"]

    with CSV_FILE.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return rows, reader.fieldnames or []


def main():
    rows, fieldnames = load_existing_csv()
    fieldnames = list(fieldnames)

    for base in ["commit", "date", "file"]:
        if base not in fieldnames:
            fieldnames.append(base)

    # индекс теперь ТОЛЬКО по commit
    index = {}
    for r in rows:
        if "commit" in r:
            index[r["commit"]] = r

    for agg_file in AGG.glob("*.json"):
        data = json.loads(agg_file.read_text(encoding="utf-8"))
        commit = data["commit"]

        score_col = next(k for k in data if k.startswith("solid_"))
        score = data[score_col]

        meta = json.loads((META / f"{commit}.json").read_text(encoding="utf-8"))

        if score_col not in fieldnames:
            fieldnames.append(score_col)

        if commit not in index:
            index[commit] = {
                "commit": commit,
                "date": meta.get("date"),
                "file": "-",  # сохраняем поле, но без FILES
            }

        index[commit][score_col] = score

    final_rows = list(index.values())
    solid_cols = [c for c in fieldnames if c.startswith("solid_")]

    with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["commit", "date", "file"] + solid_cols
        )
        writer.writeheader()
        writer.writerows(final_rows)


if __name__ == "__main__":
    main()
