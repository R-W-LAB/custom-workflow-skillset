#!/usr/bin/env python3
import json
import os
import shutil
from pathlib import Path


HOME = Path.home()
PLUGIN_NAME = "custom-workflow-skillset"


def copy_tree(src: Path, dst: Path) -> None:
    if src.resolve() == dst.resolve():
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "__MACOSX"))


def copy_dir_contents(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copy_tree(item, target)
        else:
            shutil.copy2(item, target)


def update_marketplace() -> None:
    path = HOME / ".agents" / "plugins" / "marketplace.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        data = json.loads(path.read_text())
    else:
        data = {"name": "local", "interface": {"displayName": "Local Plugins"}, "plugins": []}
    data.setdefault("name", "local")
    data.setdefault("interface", {}).setdefault("displayName", "Local Plugins")
    plugins = data.setdefault("plugins", [])
    entry = {
        "name": PLUGIN_NAME,
        "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Coding",
    }
    for index, plugin in enumerate(plugins):
        if plugin.get("name") == PLUGIN_NAME:
            plugins[index] = entry
            break
    else:
        plugins.append(entry)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def install_global_commands(version: str) -> None:
    bin_dir = HOME / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = HOME / ".codex" / "plugins" / "cache" / "local" / PLUGIN_NAME / version / "scripts" / "watch_status.py"
    wrapper = bin_dir / "cws-watch"
    wrapper.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f'exec python3 "{script}" "$@"\n',
        encoding="utf-8",
    )
    os.chmod(wrapper, 0o755)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / ".codex-plugin" / "plugin.json").read_text())
    version = manifest["version"]

    copy_tree(root, HOME / "plugins" / PLUGIN_NAME)
    copy_dir_contents(root / "agents", HOME / ".codex" / "agents")
    copy_dir_contents(root / "skills", HOME / ".agents" / "skills")
    copy_dir_contents(root / "skills", HOME / ".codex" / "skills")
    copy_tree(root, HOME / ".codex" / "plugins" / "cache" / "local" / PLUGIN_NAME / version)
    update_marketplace()
    install_global_commands(version)
    print(f"Synced {PLUGIN_NAME} {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
