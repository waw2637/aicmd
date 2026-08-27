#!/usr/bin/env python3
"""Select and edit an installed Bash AI prompt preset."""

from __future__ import annotations

import argparse
import os
import platform
import shlex
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


HOME = Path.home()
PROMPT_DIR = Path(os.environ.get("BASH_AI_PROMPT_DIR", HOME / ".local/share/bash-ai/prompts"))
FRIENDLY_NAMES = {
    "linux-command": "Command generation — Linux",
    "macos-command": "Command generation — macOS",
    "unix-command": "Command generation — portable Unix",
    "general": "General assistant",
    "code": "Code generation",
    "debug": "Debugging",
    "review": "Code review",
}
PREFERRED_ORDER = (
    "linux-command",
    "macos-command",
    "unix-command",
    "general",
    "code",
    "debug",
    "review",
)


def active_command_preset() -> str:
    system = platform.system()
    if system == "Linux":
        return "linux-command"
    if system == "Darwin":
        return "macos-command"
    return "unix-command"


def prompt_files() -> list[Path]:
    if not PROMPT_DIR.is_dir():
        raise SystemExit(f"Bash AI prompt directory does not exist: {PROMPT_DIR}")
    available = {path.stem: path for path in PROMPT_DIR.glob("*.txt") if path.is_file()}
    ordered = [available.pop(name) for name in PREFERRED_ORDER if name in available]
    ordered.extend(available[name] for name in sorted(available))
    if not ordered:
        raise SystemExit(f"No prompt files were found in {PROMPT_DIR}")
    return ordered


def display_name(path: Path) -> str:
    label = FRIENDLY_NAMES.get(path.stem, path.stem.replace("-", " ").title())
    if path.stem == active_command_preset():
        label += " [active command preset]"
    return label


def select_prompt(files: list[Path]) -> Path | None:
    print("\nBash AI prompt presets")
    for index, path in enumerate(files, 1):
        print(f"  {index}. {display_name(path)}")
    print(f"  {len(files) + 1}. Cancel")
    while True:
        answer = input("Select a prompt to edit: ").strip()
        try:
            choice = int(answer)
        except ValueError:
            print("Enter a menu number.")
            continue
        if choice == len(files) + 1:
            return None
        if 1 <= choice <= len(files):
            return files[choice - 1]
        print(f"Enter a number from 1 through {len(files) + 1}.")


def resolve_named_prompt(name: str, files: list[Path]) -> Path:
    aliases = {
        "command": active_command_preset(),
        "linux": "linux-command",
        "mac": "macos-command",
        "macos": "macos-command",
        "unix": "unix-command",
    }
    requested = aliases.get(name.lower(), name.lower())
    if requested.endswith(".txt"):
        requested = requested[:-4]
    for path in files:
        if path.stem == requested:
            return path
    choices = ", ".join(path.stem for path in files)
    raise SystemExit(f"Unknown prompt preset '{name}'. Available presets: {choices}")


def editor_command(explicit: str | None) -> list[str]:
    candidates = []
    if explicit:
        candidates.append(explicit)
    else:
        candidates.extend(value for value in (os.environ.get("VISUAL"), os.environ.get("EDITOR")) if value)
        candidates.extend(("nano", "vim", "vi"))
    for candidate in candidates:
        try:
            command = shlex.split(candidate)
        except ValueError:
            continue
        if command and shutil.which(command[0]):
            return command
    raise SystemExit("No editor was found. Install nano or set the VISUAL or EDITOR environment variable.")


def edit_prompt(path: Path, editor: list[str]) -> int:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.name}.before-edit-{stamp}")
    shutil.copy2(path, backup)
    result = subprocess.run([*editor, str(path)])
    if result.returncode:
        print(f"Editor exited with status {result.returncode}. Backup: {backup}")
        return result.returncode
    if not path.read_text(errors="replace").strip():
        shutil.copy2(backup, path)
        print(f"The prompt was empty after editing; restored {backup}.")
        return 1
    print(f"Saved:  {path}")
    print(f"Backup: {backup}")
    print("The updated prompt will be used by the next AI request.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("preset", nargs="?", help="prompt name; omit for the interactive menu")
    parser.add_argument("--list", action="store_true", help="list installed prompt presets")
    parser.add_argument("--editor", metavar="COMMAND", help="editor command to use for this invocation")
    args = parser.parse_args()

    files = prompt_files()
    if args.list:
        for path in files:
            print(f"{path.stem:16} {display_name(path)}")
        return 0

    selected = resolve_named_prompt(args.preset, files) if args.preset else select_prompt(files)
    if selected is None:
        print("Prompt editing cancelled.")
        return 0
    return edit_prompt(selected, editor_command(args.editor))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nPrompt editing cancelled.")
        raise SystemExit(130)
