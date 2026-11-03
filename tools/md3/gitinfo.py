import datetime
import os
import subprocess
from collections.abc import Mapping

from md3.paths import ROOT


def git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    except OSError:
        return None
    return (out.returncode == 0 and out.stdout.strip()) or None


def detect_version(env: Mapping[str, str] = os.environ) -> str:
    """Tag name in CI (GitHub Actions tag build), `git describe` locally. Leading `v` is dropped."""
    if env.get("GITHUB_REF_TYPE") == "tag":
        tag = env["GITHUB_REF_NAME"]
    else:
        tag = git("describe", "--tags", "--always", "--dirty") or "dev"
    return tag.removeprefix("v")


def commit_date() -> str:
    """Date of HEAD, so rebuilding the same commit gives the same files. Today outside a git checkout."""
    return git("log", "-1", "--format=%cs") or datetime.date.today().isoformat()
