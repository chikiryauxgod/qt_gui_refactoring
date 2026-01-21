import re
from pathlib import Path

EXCLUDED_DIRS = (
    "vendor/",
    "node_modules/",
    "dist/",
    "build/",
)

MAX_LINES = 300

def detect_language(path):
    return Path(path).suffix.lstrip(".")

def normalize_commit(raw: str) -> str:
    lines = raw.splitlines()
    header, diff = [], []
    in_diff = False

    for line in lines:
        if line.startswith("diff --git"):
            in_diff = True
        if in_diff:
            diff.append(line)
        else:
            header.append(line)

    result = ["\n".join(header), "\nFILES:"]

    blocks = "\n".join(diff).split("diff --git ")

    for block in blocks:
        if not block.strip():
            continue

        m = re.search(r"a/(.*?) b/(.*?)$", block.splitlines()[0])
        if not m:
            continue

        path = m.group(2)
        if path.startswith(EXCLUDED_DIRS):
            continue

        content = block.splitlines()[1:]
        if len(content) > MAX_LINES:
            continue

        result.append(
            f"""
FILE: {path}
LANG: {detect_language(path)}

{chr(10).join(content)}
"""
        )

    return "\n".join(result)

def main():
    for raw_file in Path("commits").glob("*.raw"):
        normalized = normalize_commit(raw_file.read_text())
        raw_file.with_suffix(".norm").write_text(normalized)

if __name__ == "__main__":
    main()
