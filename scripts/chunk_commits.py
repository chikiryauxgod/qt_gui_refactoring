from pathlib import Path

MAX_CHARS = 6000  

def chunk_commit(text: str) -> list[str]:
    chunks = []
    current = []

    for line in text.splitlines():
        if sum(len(l) for l in current) > MAX_CHARS:
            chunks.append("\n".join(current))
            current = []

        current.append(line)

    if current:
        chunks.append("\n".join(current))

    return chunks


def main():
    for norm_file in Path("commits").glob("*.norm"):
        chunks = chunk_commit(norm_file.read_text())

        out_dir = norm_file.with_suffix("")
        out_dir.mkdir(exist_ok=True)

        for i, chunk in enumerate(chunks):
            (out_dir / f"chunk_{i}.txt").write_text(chunk)


if __name__ == "__main__":
    main()
