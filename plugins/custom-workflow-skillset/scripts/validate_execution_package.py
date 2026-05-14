#!/usr/bin/env python3
import runpy
from pathlib import Path


if __name__ == "__main__":
    script = Path(__file__).resolve().parents[1] / "skills" / "plan-goal-runner" / "scripts" / "validate_execution_package.py"
    runpy.run_path(str(script), run_name="__main__")
