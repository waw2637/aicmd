#!/usr/bin/env python3
"""Interactive and printable help for the Bash AI terminal integration."""

from __future__ import annotations

import argparse
import sys
from collections import OrderedDict


QUICK_HELP = """Bash AI quick help

Ctrl-G                 Replace typed text with a generated command; no shell context
aicmd REQUEST           Generate one command with full shell context
ai REQUEST              General context-aware request
aicode REQUEST          Code-generation preset
aidebug REQUEST         Debugging preset
aireview REQUEST        Review preset
ai-conf                 Show current server/model settings
ai-conf --server HOST   Change the model server
ai-conf --model NAME    Change the model
ai-conf --temperature N Change generation temperature
ai-prompt               Select and edit a prompt preset
ai-model                Show runtime, model, and endpoint
ai-health               Test the server and list models

Complete interactive help: ai --help
Quick help: ai -help, ai -h, or ai '?'
"""

SECTIONS = OrderedDict(
    [
        (
            "getting-started",
            (
                "Getting started",
                """The integration sends requests to an OpenAI-compatible model server.

Type a natural-language command request at an interactive Bash prompt and press
Ctrl-G. The line is replaced, never executed automatically. Review it, then press
Enter yourself.

Use `aicmd` when generation needs the current directory, history, environment,
Git state, or previous command status. Use `ai` and the named presets for longer
answers, scripts, diagnosis, and review.""",
            ),
        ),
        (
            "commands",
            (
                "Commands",
                """ai [OPTIONS] MESSAGE       General assistant with shell context
aicmd [OPTIONS] REQUEST     One validated Bash command with shell context
aicode [OPTIONS] REQUEST    Code-generation preset
aidebug [OPTIONS] REQUEST   Evidence-driven debugging preset
aireview [OPTIONS] REQUEST  Code-review preset
aichat [OPTIONS] MESSAGE    General conversational preset
ai-model                    Show platform, runtime, model, and endpoint
ai-health                   Query the server's /v1/models endpoint
ai-conf [OPTIONS]           Show or change client configuration
ai-prompt [PRESET]          Select and edit prompt files

Common AI options:
  --no-shell-context        Do not include the Bash snapshot
  --preset NAME             Select general, command, code, debug, or review
  --context TEXT            Add explicit context
  --message TEXT            Add message text explicitly""",
            ),
        ),
        (
            "context",
            (
                "Shell context and Ctrl-G",
                """`Ctrl-G` deliberately sends no shell snapshot. It uses the current
platform's command prompt plus only the text on the command line.

`aicmd` and ordinary `ai` calls include the working directory, previous exit
status, filtered environment, recent history, aliases, shell options, jobs, a
short directory listing, and Git status when applicable. Values whose variable
names look like secrets, passwords, tokens, cookies, credentials, or private
keys are redacted.

Any helper accepts `--no-shell-context` when speed or privacy matters more than
session awareness.""",
            ),
        ),
        (
            "presets",
            (
                "Presets",
                """general   Concise technical assistance
command   Platform-aware, one-line Bash command generation
code      Complete code and scripts
debug     Evidence-first diagnosis
review    Correctness and risk-oriented review

Command generation automatically selects linux-command.txt, macos-command.txt,
or unix-command.txt for the current operating system.""",
            ),
        ),
        (
            "configuration",
            (
                "Configuration",
                """Show configuration:
  ai-conf

Change settings individually or together:
  ai-conf --server modelbox:11434
  ai-conf --model gemma3:4b
  ai-conf --temperature 0.2
  ai-conf --runtime llama.cpp --server modelbox:8080 --model local-model
  ai-conf --max-tokens 8192

Supported runtime labels are ollama, llama.cpp, lemonade, fastflowlm, and
custom. The runtime is metadata plus endpoint defaults; the client works with
any compatible server. Changes are backed up and loaded into the current shell.""",
            ),
        ),
        (
            "prompts",
            (
                "Prompt editing",
                """Open the interactive menu:
  ai-prompt

Edit directly:
  ai-prompt command
  ai-prompt general
  ai-prompt code
  ai-prompt debug
  ai-prompt review

List names or choose an editor:
  ai-prompt --list
  ai-prompt code --editor nano

The editor preference order is VISUAL, EDITOR, nano, vim, then vi. Each edit is
backed up. Empty prompts are rejected and restored. Prompt changes apply to the
next request without reloading Bash.""",
            ),
        ),
        (
            "runtime",
            (
                "Model runtimes and health",
                """The client does not install or manage a model runtime. Ollama,
llama.cpp, Lemonade, FastFlowLM, and custom OpenAI-compatible endpoints are
supported through /v1/chat/completions.

Show the selected connection with `ai-model`. Test the server and display its
model list with `ai-health`. Use `ai-conf --server`, `--runtime`, and `--model`
to change backends without reinstalling the shell integration.""",
            ),
        ),
        (
            "customization",
            (
                "Core customization",
                """The installed core is ~/.local/share/bash-ai/bash-ai.bash.
Functions can be renamed, context collection changed, request behavior altered,
and the Ctrl-G binding replaced. Reload Bash changes with `source ~/.bashrc`.

Python utilities are ai_conf.py, ai_prompt.py, and ai_help.py in the same
directory. Prompt files are under ~/.local/share/bash-ai/prompts/.

Installer updates replace managed files. For durable or distributable changes,
edit the corresponding files in the extracted installation package rather than
only the running installation.""",
            ),
        ),
        (
            "lifecycle",
            (
                "Install, update, and remove",
                """Run ./install.sh from the extracted package. Existing installations
offer update, reconfigure, repair, remove, and cancel choices.

Useful non-interactive operations:
  ./install.sh --non-interactive
  ./install.sh --server modelbox:11434 --temperature 0.2
  ./install.sh --remove --non-interactive
  ./install.sh --remove --purge-config

Removal deletes only the client integration, managed prompts, and selected
client configuration. It never changes the runtime or downloaded models.""",
            ),
        ),
        (
            "troubleshooting",
            (
                "Troubleshooting and safety",
                """Run `ai-model` to inspect the active connection and `ai-health` to
test /v1/models. Run `declare -f aicmd` and `bind -S` to inspect loaded Bash
functions and bindings. Start a new Bash session after core changes.

Generated commands are not executed automatically. Always review them. The
command prompt prefers read-only inspection for ambiguity, but model output is
not a security boundary.

Configuration: ~/.config/bash-ai/config
Installed core: ~/.local/share/bash-ai/
Installed prompts: ~/.local/share/bash-ai/prompts/""",
            ),
        ),
    ]
)


def print_section(key: str) -> None:
    title, body = SECTIONS[key]
    print(f"\n{title}\n{'=' * len(title)}\n{body}\n")


def print_full() -> None:
    print(QUICK_HELP.rstrip())
    for key in SECTIONS:
        print_section(key)


def resolve_topic(value: str) -> str:
    normalized = value.lower().replace("_", "-")
    aliases = {
        "command": "commands",
        "config": "configuration",
        "conf": "configuration",
        "prompt": "prompts",
        "health": "runtime",
        "install": "lifecycle",
        "remove": "lifecycle",
        "customize": "customization",
        "trouble": "troubleshooting",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in SECTIONS:
        choices = ", ".join(SECTIONS)
        raise SystemExit(f"Unknown help topic '{value}'. Topics: {choices}")
    return normalized


def interactive_menu() -> int:
    keys = list(SECTIONS)
    while True:
        print("\nBash AI complete help")
        for index, key in enumerate(keys, 1):
            print(f"  {index}. {SECTIONS[key][0]}")
        print(f"  {len(keys) + 1}. Show all help")
        print(f"  {len(keys) + 2}. Exit")
        answer = input("Select a help topic: ").strip()
        try:
            choice = int(answer)
        except ValueError:
            print("Enter a menu number.")
            continue
        if choice == len(keys) + 2:
            return 0
        if choice == len(keys) + 1:
            print_full()
        elif 1 <= choice <= len(keys):
            print_section(keys[choice - 1])
        else:
            print(f"Enter a number from 1 through {len(keys) + 2}.")
            continue
        input("Press Enter to return to the help menu...")


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("topic", nargs="?")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()
    if args.quick:
        print(QUICK_HELP.rstrip())
        return 0
    if args.topic:
        print_section(resolve_topic(args.topic))
        return 0
    if args.interactive or (sys.stdin.isatty() and sys.stdout.isatty()):
        return interactive_menu()
    print_full()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nHelp closed.")
        raise SystemExit(130)
