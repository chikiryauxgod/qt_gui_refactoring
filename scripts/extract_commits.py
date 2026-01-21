import subprocess
from pathlib import Path

OUT_DIR = Path("commits")
OUT_DIR.mkdir(exist_ok=True)

def get_commits():
    return subprocess.check_output(
        ["git", "rev-list", "--reverse", "HEAD"],
        text=True
    ).splitlines()

def get_commit_diff(commit):
    return subprocess.check_output(
        [
            "git", "show", commit,
            "--patch",
            "--no-color",
            "--format=fuller"
        ],
        text=True
    )

def main():
    for commit in get_commits():
        diff = get_commit_diff(commit)
        (OUT_DIR / f"{commit}.raw").write_text(diff)

if __name__ == "__main__":
    main()


