import re
from pathlib import Path

from md3.paths import TEMPLATES

PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
# Skin files (.wps, .sbs) use CRLF like the original theme; .cfg uses LF.
SKIN_FILES = {"wps": True, "sbs": True, "cfg": False}  # extension -> CRLF


def render(template: str, values: dict[str, str]) -> str:
    def substitute(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(f"unknown placeholder {{{{{key}}}}}")
        return values[key]

    return PLACEHOLDER.sub(substitute, template)


def render_skin_file(ext: str, values: dict[str, str]) -> str:
    """templates/MD3.<ext>.tpl filled in, with LF line endings."""
    text = (TEMPLATES / f"MD3.{ext}.tpl").read_text(encoding="utf-8").replace("\r\n", "\n")
    return render(text, values)


def write_skin_file(path: Path, ext: str, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\r\n" if SKIN_FILES[ext] else "\n")
