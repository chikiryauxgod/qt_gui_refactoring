import subprocess
import json
from pathlib import Path

COMMITS_DIR = Path("commits")
META_DIR = Path("meta")

COMMITS_DIR.mkdir(exist_ok=True)
META_DIR.mkdir(exist_ok=True)

def git(cmd):
    return subprocess.check_output(
        cmd,
        encoding="utf-8",
        errors="replace" 
    )



def get_commits():
    return git(["git", "rev-list", "--reverse", "--no-merges", "HEAD"]).splitlines()


def get_commit_raw(commit: str) -> str:
    return git([
        "git", "show", commit,
        "--patch",
        "--no-color",
        "--format=fuller"
    ])


def get_commit_meta(commit: str) -> dict:
    raw = git([
        "git", "show", commit,
        "--no-patch",
        "--format=%H%n%an%n%ad%n%s"
    ]).splitlines()

    return {
        "commit": raw[0],
        "author": raw[1],
        "date": raw[2],
        "message": raw[3]
    }



def main():
    for commit in get_commits():
        raw = get_commit_raw(commit)
        (COMMITS_DIR / f"{commit}.raw").write_text(raw, encoding="utf-8")

        meta = get_commit_meta(commit)
        (META_DIR / f"{commit}.json").write_text(
            json.dumps(meta, indent=2)
        )


if __name__ == "__main__":
    main()
