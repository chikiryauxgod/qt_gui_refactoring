import json
from statistics import mean
from pathlib import Path

def aggregate(results: list[dict]) -> dict:
    scores = {k: [] for k in ["SRP", "OCP", "LSP", "ISP", "DIP"]}

    for r in results:
        if "error" in r:
            continue
        for k in scores:
            scores[k].append(r[k]["score"])

    return {
        k: round(mean(v), 2) if v else None
        for k, v in scores.items()
    }

def main():
    for file in Path("results").glob("*.json"):
        data = json.loads(file.read_text())
        summary = aggregate(data)
        file.with_suffix(".summary.json").write_text(
            json.dumps(summary, indent=2)
        )

if __name__ == "__main__":
    main()
