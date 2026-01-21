import json
from statistics import mean
from pathlib import Path

RUN_ID = "qwen_0_5b"

RESULTS = Path("results")
OUT = Path("aggregated")
OUT.mkdir(exist_ok=True)


def aggregate_commit(commit: str) -> dict:
    data = json.loads((RESULTS / f"{commit}.json").read_text())

    scores = [
        r["solid_score"]
        for r in data
        if isinstance(r, dict) and "solid_score" in r
    ]

    return {
        "commit": commit,
        f"solid_{RUN_ID}": round(mean(scores), 2) if scores else None
    }


def main():
    for f in RESULTS.glob("*.json"):
        commit = f.stem
        summary = aggregate_commit(commit)

        (OUT / f"{commit}.{RUN_ID}.json").write_text(
            json.dumps(summary, indent=2)
        )


if __name__ == "__main__":
    main()
