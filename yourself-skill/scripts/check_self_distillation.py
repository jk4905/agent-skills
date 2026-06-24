#!/usr/bin/env python3
"""Check the local self-distillation workspace and final skill structure."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "outputs" / "yourself-skill"
WORK = ROOT / "work" / "self-distillation"


def status(label: str, ok: bool, detail: str = "") -> None:
    marker = "OK" if ok else "MISSING"
    suffix = f" - {detail}" if detail else ""
    print(f"[{marker}] {label}{suffix}")


def main() -> int:
    required_dirs = [
        WORK / "raw",
        WORK / "dot-skill-runs",
        SKILL / "references",
        SKILL / "scripts",
    ]
    required_files = [
        SKILL / "SKILL.md",
        SKILL / "references" / "self-memory.md",
        SKILL / "references" / "work-principles.md",
        SKILL / "references" / "communication-style.md",
        SKILL / "references" / "workflows.md",
        SKILL / "references" / "corrections.md",
        SKILL / "references" / "source-map.md",
        SKILL / "references" / "dot-skill-workflow.md",
    ]

    print("Self-distillation workspace check")
    print(f"Root: {ROOT}")

    for directory in required_dirs:
        status(str(directory.relative_to(ROOT)), directory.is_dir())

    for file_path in required_files:
        status(str(file_path.relative_to(ROOT)), file_path.is_file())

    dot_skill = shutil.which("dot-skill")
    status("dot-skill CLI", dot_skill is not None, dot_skill or "not found in PATH")

    raw_files = list((WORK / "raw").glob("**/*")) if (WORK / "raw").is_dir() else []
    final_raw_leaks = [
        path for path in SKILL.glob("**/*")
        if path.is_file() and "raw" in path.name.lower()
    ]
    status("raw material kept out of final skill", not final_raw_leaks)
    print(f"Raw material files found in work area: {sum(p.is_file() for p in raw_files)}")

    return 0 if all(path.exists() for path in required_dirs + required_files) else 1


if __name__ == "__main__":
    raise SystemExit(main())
