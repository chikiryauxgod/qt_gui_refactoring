import subprocess
import json
from pathlib import Path

COMMITS_DIR = Path("commits")
META_DIR = Path("meta")

COMMITS_DIR.mkdir(exist_ok=True)
META_DIR.mkdir(exist_ok=True)


def get_commits():
    return subprocess.check_output(
        ["git", "rev-list", "--reverse", "--no-merges", "HEAD"],
        text=True
    ).splitlines()


def get_commit_raw(commit: str) -> str:
    return subprocess.check_output(
        [
            "git", "show", commit,
            "--patch",
            "--no-color",
            "--format=fuller"
        ],
        text=True
    )


def get_commit_meta(commit: str) -> dict:
    raw = subprocess.check_output(
        [
            "git", "show", commit,
            "--no-patch",
            "--format=%H%n%an%n%ad%n%s"
        ],
        text=True
    ).splitlines()

    return {
        "commit": raw[0],
        "author": raw[1],
        "date": raw[2],
        "message": raw[3]
    }


def main():
    for commit in get_commits():
        raw = get_commit_raw(commit)
        (COMMITS_DIR / f"{commit}.raw").write_text(raw)

        meta = get_commit_meta(commit)
        (META_DIR / f"{commit}.json").write_text(
            json.dumps(meta, indent=2)
        )


if __name__ == "__main__":
    main()
