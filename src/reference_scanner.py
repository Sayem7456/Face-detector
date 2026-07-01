from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path

SUPPORTED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}

_UNSAFE_NAME_RE = re.compile(
    r"^\.|\.\.|[\\/:*?\"<>|~#]|^\s|\s$"
)


def is_safe_identity_name(name: str) -> bool:
    if not name or not name.strip():
        return False
    if _UNSAFE_NAME_RE.search(name):
        return False
    return True


def scan_identities(
    base_dir: str | Path = "data/reference_images",
) -> OrderedDict[str, list[Path]]:
    base = Path(base_dir)
    if not base.is_dir():
        raise NotADirectoryError(
            f"Reference image directory not found: {base.resolve()}"
        )

    identities: OrderedDict[str, list[Path]] = OrderedDict()

    entries = sorted(
        e for e in base.iterdir() if e.is_dir() and not e.name.startswith(".")
    )

    for entry in entries:
        name = entry.name
        if not is_safe_identity_name(name):
            continue

        seen: set[Path] = set()
        unique: list[Path] = []
        for p in sorted(entry.iterdir()):
            if not p.is_file() or p.name.startswith("."):
                continue
            if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            resolved = p.resolve()
            if resolved not in seen:
                seen.add(resolved)
                unique.append(resolved)

        identities[name] = unique

    return identities
