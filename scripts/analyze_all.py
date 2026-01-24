from pathlib import Path
import json
from ollama_client import analyze_chunk

COMMITS = Path("commits")
OUT = Path("results")
OUT.mkdir(exist_ok=True)


def main():
    for commit_dir in COMMITS.iterdir():
        if not commit_dir.is_dir():
            continue

        out_file = OUT / f"{commit_dir.name}.json"
        commit_results = []

        chunks = sorted(commit_dir.glob("chunk_*.txt"), key=lambda p: p.name)

        print(f"\n== COMMIT {commit_dir.name} | chunks: {len(chunks)} ==")

        for i, chunk in enumerate(chunks, start=1):
            text = chunk.read_text(encoding="utf-8", errors="ignore")

            print(f"[{commit_dir.name}] {i}/{len(chunks)} -> {chunk.name} ({len(text)} chars)")

            try:
                result = analyze_chunk(text)
                commit_results.append({
                    "chunk": chunk.name,
                    "result": result
                })
            except Exception as e:
                commit_results.append({
                    "chunk": chunk.name,
                    "error": str(e)
                })
            out_file.write_text(
                json.dumps(commit_results, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

        print(f"Saved: {out_file}")


if __name__ == "__main__":
    main()
