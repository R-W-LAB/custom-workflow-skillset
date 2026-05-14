#!/usr/bin/env python3
import json
import sys
import zipfile
from pathlib import Path


EXCLUDE_PARTS = {"__pycache__", "__MACOSX"}
EXCLUDE_NAMES = {".DS_Store"}


def should_include(path: Path) -> bool:
    return not (set(path.parts) & EXCLUDE_PARTS or path.name in EXCLUDE_NAMES or path.suffix == ".pyc")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / ".codex-plugin" / "plugin.json").read_text())
    version = manifest.get("version", "local")
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else root.parent / f"{root.name}-plugin-{version}.zip"
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file() and should_include(path.relative_to(root)):
                zf.write(path, root.name / path.relative_to(root))
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
