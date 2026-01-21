from pathlib import Path
import json
from ollama_client import analyze_chunk

OUT = Path("results")
OUT.mkdir(exist_ok=True)

def main():
    for commit_dir in Path("commits").iterdir():
        if not commit_dir.is_dir():
            continue

        commit_results = []

        for chunk in commit_dir.glob("chunk_*.txt"):
            try:
                result = analyze_chunk(chunk.read_text())
                commit_results.append(result)
            except Exception as e:
                commit_results.append({"error": str(e)})

        (OUT / f"{commit_dir.name}.json").write_text(
            json.dumps(commit_results, indent=2)
        )

if __name__ == "__main__":
    main()
