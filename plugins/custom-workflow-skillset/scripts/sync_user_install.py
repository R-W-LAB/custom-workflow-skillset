#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import shutil
from pathlib import Path


HOME = Path.home()
PLUGIN_NAME = "custom-workflow-skillset"
SKILL_NAMES = (
    "deep-interview",
    "design-grill",
    "design-grill-with-docs",
    "parallel-lane-runner",
    "plan-goal-runner",
)
SKIP_PARTS = {"__pycache__", "__MACOSX"}
SKIP_NAMES = {".DS_Store"}


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


def comparable_files(root: Path) -> dict[str, Path]:
    files = {}
    if not root.is_dir():
        return files
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if path.is_file() and path.suffix != ".pyc" and not (set(rel.parts) & SKIP_PARTS) and path.name not in SKIP_NAMES:
            files[str(rel)] = path
    return files


def same_tree(left: Path, right: Path) -> bool:
    left_files = comparable_files(left)
    right_files = comparable_files(right)
    if set(left_files) != set(right_files):
        return False
    return all(left_files[name].read_bytes() == right_files[name].read_bytes() for name in left_files)


def reference_skill_dirs(root: Path, version: str, name: str) -> list[Path]:
    return [
        root / "skills" / name,
        HOME / ".codex" / "plugins" / "cache" / PLUGIN_NAME / PLUGIN_NAME / version / "skills" / name,
        HOME / ".codex" / "plugins" / "cache" / "local" / PLUGIN_NAME / version / "skills" / name,
    ]


def disable_legacy_global_skills(root: Path, version: str) -> int:
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = HOME / ".codex" / "skills-disabled" / f"{PLUGIN_NAME}-{timestamp}"
    moved = 0
    for base, bucket in ((HOME / ".codex" / "skills", "codex-skills"), (HOME / ".agents" / "skills", "agents-skills")):
        for name in SKILL_NAMES:
            target = base / name
            if not target.is_dir():
                continue
            refs = [ref for ref in reference_skill_dirs(root, version, name) if ref.is_dir()]
            if refs and any(same_tree(target, ref) for ref in refs):
                destination = backup / bucket / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), str(destination))
                moved += 1
                print(f"Disabled legacy global skill copy: {target} -> {destination}")
            else:
                print(f"Kept possible user-owned skill directory: {target}")
    return moved


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Custom Workflow Skillset into user-level Codex locations.")
    parser.add_argument(
        "--install-codex-skills",
        action="store_true",
        help="Also copy skills into ~/.codex/skills. Off by default to avoid duplicate skill catalog entries.",
    )
    parser.add_argument(
        "--install-agents-skills",
        action="store_true",
        help="Also copy skills into ~/.agents/skills. Off by default to avoid duplicate skill catalog entries.",
    )
    parser.add_argument(
        "--skip-marketplace",
        action="store_true",
        help="Skip updating ~/.agents/plugins/marketplace.json.",
    )
    parser.add_argument(
        "--disable-legacy-global-skills",
        action="store_true",
        help="Move exact-match legacy global skill copies out of ~/.codex/skills and ~/.agents/skills.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / ".codex-plugin" / "plugin.json").read_text())
    version = manifest["version"]

    if args.disable_legacy_global_skills:
        moved = disable_legacy_global_skills(root, version)
        print(f"Disabled {moved} legacy global skill copies.")

    copy_tree(root, HOME / "plugins" / PLUGIN_NAME)
    copy_dir_contents(root / "agents", HOME / ".codex" / "agents")
    if args.install_agents_skills:
        copy_dir_contents(root / "skills", HOME / ".agents" / "skills")
    if args.install_codex_skills:
        copy_dir_contents(root / "skills", HOME / ".codex" / "skills")
    copy_tree(root, HOME / ".codex" / "plugins" / "cache" / "local" / PLUGIN_NAME / version)
    if not args.skip_marketplace:
        update_marketplace()
    install_global_commands(version)
    print(f"Synced {PLUGIN_NAME} {version}; global skill copies are opt-in.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
