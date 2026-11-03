import re

from md3.gitinfo import commit_date, detect_version


def test_version_is_the_tag_without_v_in_ci_tag_builds():
    assert detect_version({"GITHUB_REF_TYPE": "tag", "GITHUB_REF_NAME": "v3.0-rc1"}) == "3.0-rc1"


def test_version_ignores_branch_builds_and_asks_git():
    version = detect_version({"GITHUB_REF_TYPE": "branch", "GITHUB_REF_NAME": "main"})
    assert version != "main"
    assert version and not version.startswith("v")


def test_commit_date_is_iso():
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", commit_date())
