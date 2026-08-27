#!/usr/bin/env python3
"""Interactive Linux/macOS installer for the Bash AI integration."""

from __future__ import annotations

import argparse
import getpass
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urlunparse


PACKAGE_DIR = Path(__file__).resolve().parent
HOME = Path.home()
INSTALL_DIR = HOME / ".local" / "share" / "bash-ai"
PROMPT_DIR = INSTALL_DIR / "prompts"
CONFIG_DIR = HOME / ".config" / "bash-ai"
CONFIG_FILE = CONFIG_DIR / "config"
LIFECYCLE_FILE = CONFIG_DIR / "lifecycle.bash"
BASHRC = HOME / ".bashrc"
BEGIN_MARKER = "# >>> bash-ai >>>"
END_MARKER = "# <<< bash-ai <<<"
PROFILE_BEGIN_MARKER = "# >>> bash-ai bashrc loader >>>"
PROFILE_END_MARKER = "# <<< bash-ai bashrc loader <<<"
DEFAULTS = {
    "BASH_AI_RUNTIME": "ollama",
    "BASH_AI_ENDPOINT": "http://127.0.0.1:11434/v1/chat/completions",
    "BASH_AI_MODEL": "gemma3:4b",
    "BASH_AI_API_KEY": "",
    "BASH_AI_MAX_TOKENS": "4096",
    "BASH_AI_TEMPERATURE": "0.1",
    "BASH_AI_PROMPT_DIR": str(PROMPT_DIR),
}

RUNTIMES = {
    "ollama": {
        "label": "Ollama",
        "endpoint": "http://127.0.0.1:11434/v1/chat/completions",
        "model": "gemma3:4b",
        "port": 11434,
    },
    "llama.cpp": {
        "label": "llama.cpp",
        "endpoint": "http://127.0.0.1:8080/v1/chat/completions",
        "model": "local-model",
        "port": 8080,
    },
    "lemonade": {
        "label": "Lemonade",
        "endpoint": "http://127.0.0.1:13305/v1/chat/completions",
        "model": "Qwen3-0.6B-GGUF",
        "port": 13305,
    },
    "fastflowlm": {
        "label": "FastFlowLM (Linux/Windows runtime)",
        "endpoint": "http://127.0.0.1:52625/v1/chat/completions",
        "model": "gemma4-it:e4b",
        "port": 52625,
    },
    "custom": {
        "label": "Other OpenAI-compatible server",
        "endpoint": "http://127.0.0.1:8000/v1/chat/completions",
        "model": "local-model",
        "port": 8000,
    },
}


def installed() -> bool:
    if (INSTALL_DIR / "bash-ai.bash").exists() or CONFIG_FILE.exists():
        return True
    if not BASHRC.exists():
        return False
    bashrc_text = BASHRC.read_text(errors="replace")
    return BEGIN_MARKER in bashrc_text or bool(
        re.search(r"(?m)^(?:aicmd|_ai_replace_line)\s*\(\)\s*\{", bashrc_text)
    )


def read_config() -> dict[str, str]:
    values = dict(DEFAULTS)
    if not CONFIG_FILE.exists():
        return values
    explicit_runtime = False
    pattern = re.compile(r"^([A-Z][A-Z0-9_]*)=(.*)$")
    for raw_line in CONFIG_FILE.read_text(errors="replace").splitlines():
        match = pattern.match(raw_line.strip())
        if not match or match.group(1) not in values:
            continue
        if match.group(1) == "BASH_AI_RUNTIME":
            explicit_runtime = True
        try:
            parsed = shlex.split(match.group(2), posix=True)
            values[match.group(1)] = parsed[0] if parsed else ""
        except ValueError:
            pass
    if not explicit_runtime:
        endpoint = values["BASH_AI_ENDPOINT"]
        for runtime_name, runtime in RUNTIMES.items():
            if f":{runtime['port']}/" in endpoint:
                values["BASH_AI_RUNTIME"] = runtime_name
                break
        else:
            values["BASH_AI_RUNTIME"] = "custom"
    return values


def prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{label}{suffix}: ").strip()
    return answer or default


def yes_no(label: str, default: bool = False) -> bool:
    marker = "Y/n" if default else "y/N"
    answer = input(f"{label} [{marker}]: ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def normalize_endpoint(value: str, default_port: int) -> str:
    value = value.strip().rstrip("/")
    if not value:
        return DEFAULTS["BASH_AI_ENDPOINT"]
    if "://" not in value:
        if "/" not in value and ":" not in value:
            value += f":{default_port}"
        value = "http://" + value
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("use a hostname, IP address, or HTTP(S) URL")
    path = parsed.path.rstrip("/")
    if path.endswith("/v1/chat/completions"):
        pass
    elif path.endswith("/v1"):
        path += "/chat/completions"
    else:
        path += "/v1/chat/completions"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def configure(current: dict[str, str]) -> dict[str, str]:
    runtime_names = list(RUNTIMES)
    current_runtime = current.get("BASH_AI_RUNTIME", "custom")
    if current_runtime not in RUNTIMES:
        current_runtime = "custom"
    default_choice = runtime_names.index(current_runtime) + 1

    print("\nModel server configuration")
    print("Select the runtime that exposes the OpenAI-compatible endpoint:")
    for index, runtime_name in enumerate(runtime_names, 1):
        print(f"  {index}. {RUNTIMES[runtime_name]['label']}")
    while True:
        choice = prompt("Runtime", str(default_choice))
        try:
            runtime = runtime_names[int(choice) - 1]
            break
        except (ValueError, IndexError):
            print(f"Enter a number from 1 through {len(runtime_names)}.")

    runtime_defaults = RUNTIMES[runtime]
    same_runtime = runtime == current_runtime
    endpoint_default = current["BASH_AI_ENDPOINT"] if same_runtime else runtime_defaults["endpoint"]
    model_default = current["BASH_AI_MODEL"] if same_runtime else runtime_defaults["model"]

    print("Enter a host such as 192.168.1.26, host:port, or a complete URL.")
    while True:
        location = prompt("Model server location", endpoint_default)
        try:
            endpoint = normalize_endpoint(location, int(runtime_defaults["port"]))
            break
        except ValueError as exc:
            print(f"Invalid location: {exc}")

    model = prompt("Model name", model_default)
    max_tokens = prompt("Maximum generated tokens", current["BASH_AI_MAX_TOKENS"])
    temperature = prompt("Temperature", current["BASH_AI_TEMPERATURE"])
    try:
        if int(max_tokens) < 1:
            raise ValueError
    except ValueError:
        raise SystemExit("Maximum generated tokens must be a positive integer.")
    try:
        if not 0 <= float(temperature) <= 2:
            raise ValueError
    except ValueError:
        raise SystemExit("Temperature must be a number from 0 through 2.")

    key = current["BASH_AI_API_KEY"]
    if key:
        if yes_no("Replace the saved API key", False):
            key = getpass.getpass("API key (input hidden; blank clears it): ")
    elif yes_no("Does this server require an API key", False):
        key = getpass.getpass("API key (input hidden): ")

    return {
        "BASH_AI_RUNTIME": runtime,
        "BASH_AI_ENDPOINT": endpoint,
        "BASH_AI_MODEL": model,
        "BASH_AI_API_KEY": key,
        "BASH_AI_MAX_TOKENS": max_tokens,
        "BASH_AI_TEMPERATURE": temperature,
        "BASH_AI_PROMPT_DIR": str(PROMPT_DIR),
    }


def shell_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("$", "\\$").replace("`", "\\`")
    return f'"{escaped}"'


def write_config(values: dict[str, str]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        backup(CONFIG_FILE, "before-reconfigure")
    lines = ["# Bash AI client configuration."]
    lines.extend(f"{name}={shell_quote(values[name])}" for name in DEFAULTS)
    atomic_write(CONFIG_FILE, "\n".join(lines) + "\n", 0o600)


def lifecycle_content(runtime: str) -> str | None:
    system = platform.system()
    header = (
        "# Managed by the AI CMD installer.\n"
        "# Server lifecycle customization lives in this file.\n"
        "# Replace the function bodies for a different service manager or server.\n"
        f"# Installed default: {runtime} on {system}\n"
        f"BASH_AI_LIFECYCLE_RUNTIME={runtime!r}\n\n"
    )
    if runtime == "fastflowlm" and system == "Linux":
        return header + '''ai-start() {
    systemctl --user start fastflowlm.service
}

ai-stop() {
    systemctl --user stop fastflowlm.service
}
'''
    if runtime == "ollama" and system == "Linux":
        return header + '''ai-start() {
    sudo systemctl start ollama
}

ai-stop() {
    sudo systemctl stop ollama
}
'''
    if runtime == "ollama" and system == "Darwin":
        return header + '''ai-start() {
    open -a Ollama
}

ai-stop() {
    osascript -e 'quit app "Ollama"'
}
'''
    return None


def write_lifecycle(values: dict[str, str], enabled: bool | None) -> bool:
    content = lifecycle_content(values["BASH_AI_RUNTIME"])
    existing_is_managed = (
        LIFECYCLE_FILE.exists()
        and LIFECYCLE_FILE.read_text(errors="replace").startswith(
            "# Managed by the AI CMD installer."
        )
    )
    if content is None:
        if existing_is_managed:
            LIFECYCLE_FILE.unlink()
        return False
    if enabled is False:
        if existing_is_managed:
            LIFECYCLE_FILE.unlink()
        return LIFECYCLE_FILE.exists()
    if enabled is None and not LIFECYCLE_FILE.exists():
        return False
    if LIFECYCLE_FILE.exists() and not existing_is_managed:
        print(f"Preserving custom lifecycle file: {LIFECYCLE_FILE}")
        return True
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    atomic_write(LIFECYCLE_FILE, content, 0o600)
    return True


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def backup(path: Path, label: str) -> Path:
    target = path.with_name(f"{path.name}.{label}-{timestamp()}")
    shutil.copy2(path, target)
    return target


def atomic_write(path: Path, content: str, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(content)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def copy_program_files() -> None:
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PACKAGE_DIR / "bash-ai.bash", INSTALL_DIR / "bash-ai.bash")
    os.chmod(INSTALL_DIR / "bash-ai.bash", 0o644)
    shutil.copy2(PACKAGE_DIR / "ai_conf.py", INSTALL_DIR / "ai_conf.py")
    os.chmod(INSTALL_DIR / "ai_conf.py", 0o755)
    shutil.copy2(PACKAGE_DIR / "ai_prompt.py", INSTALL_DIR / "ai_prompt.py")
    os.chmod(INSTALL_DIR / "ai_prompt.py", 0o755)
    shutil.copy2(PACKAGE_DIR / "ai_help.py", INSTALL_DIR / "ai_help.py")
    os.chmod(INSTALL_DIR / "ai_help.py", 0o755)
    for source in sorted((PACKAGE_DIR / "prompts").glob("*.txt")):
        shutil.copy2(source, PROMPT_DIR / source.name)
        os.chmod(PROMPT_DIR / source.name, 0o644)


def update_bashrc() -> Path | None:
    prior = BASHRC.read_text(errors="replace") if BASHRC.exists() else ""
    bashrc_backup = backup(BASHRC, "before-bash-ai") if BASHRC.exists() else None
    pattern = re.compile(
        rf"(?ms)^\s*{re.escape(BEGIN_MARKER)}$.*?^\s*{re.escape(END_MARKER)}\s*$"
    )
    cleaned = pattern.sub("", prior).rstrip()
    block = (
        f"{BEGIN_MARKER}\n"
        'if [[ -r "$HOME/.local/share/bash-ai/bash-ai.bash" ]]; then\n'
        '    source "$HOME/.local/share/bash-ai/bash-ai.bash"\n'
        "fi\n"
        f"{END_MARKER}\n"
    )
    result = (cleaned + "\n\n" if cleaned else "") + block

    with tempfile.NamedTemporaryFile("w", delete=False) as stream:
        stream.write(result)
        validation_path = stream.name
    try:
        check = subprocess.run(["bash", "-n", validation_path], capture_output=True, text=True)
    finally:
        os.unlink(validation_path)
    if check.returncode:
        raise SystemExit(f"Generated .bashrc failed validation:\n{check.stderr}")
    mode = BASHRC.stat().st_mode & 0o777 if BASHRC.exists() else 0o644
    atomic_write(BASHRC, result, mode)
    return bashrc_backup


def update_macos_bash_profile() -> Path | None:
    if platform.system() != "Darwin":
        return None
    profile = HOME / ".bash_profile"
    prior = profile.read_text(errors="replace") if profile.exists() else ""
    profile_backup = backup(profile, "before-bash-ai") if profile.exists() else None
    pattern = re.compile(
        rf"(?ms)^\s*{re.escape(PROFILE_BEGIN_MARKER)}$.*?"
        rf"^\s*{re.escape(PROFILE_END_MARKER)}\s*$"
    )
    cleaned = pattern.sub("", prior).rstrip()
    block = (
        f"{PROFILE_BEGIN_MARKER}\n"
        'if [[ -r "$HOME/.bashrc" ]]; then\n'
        '    source "$HOME/.bashrc"\n'
        "fi\n"
        f"{PROFILE_END_MARKER}\n"
    )
    result = (cleaned + "\n\n" if cleaned else "") + block
    mode = profile.stat().st_mode & 0o777 if profile.exists() else 0o644
    atomic_write(profile, result, mode)
    return profile_backup


def remove_marked_block(path: Path, begin_marker: str, end_marker: str) -> Path | None:
    if not path.exists():
        return None
    prior = path.read_text(errors="replace")
    pattern = re.compile(
        rf"(?ms)^\s*{re.escape(begin_marker)}$.*?^\s*{re.escape(end_marker)}\s*$"
    )
    result, replacements = pattern.subn("", prior)
    if not replacements:
        return None
    file_backup = backup(path, "before-bash-ai-remove")
    result = result.rstrip() + ("\n" if result.strip() else "")
    with tempfile.NamedTemporaryFile("w", delete=False) as stream:
        stream.write(result)
        validation_path = stream.name
    try:
        check = subprocess.run(["bash", "-n", validation_path], capture_output=True, text=True)
    finally:
        os.unlink(validation_path)
    if check.returncode:
        raise SystemExit(f"Removal would leave invalid Bash syntax in {path}:\n{check.stderr}")
    atomic_write(path, result, path.stat().st_mode & 0o777)
    return file_backup


def choose_removal_scope() -> bool | None:
    print("\nRemove Bash AI")
    print("  1. Remove integration and prompts; keep server configuration")
    print("  2. Remove integration, prompts, and server configuration")
    print("  3. Cancel")
    while True:
        value = input("Choose an action [1]: ").strip() or "1"
        if value == "1":
            return False
        if value == "2":
            return True
        if value == "3":
            return None
        print("Enter 1, 2, or 3.")


def remove_installation(purge_config: bool, ask_scope: bool) -> int:
    if ask_scope:
        selected = choose_removal_scope()
        if selected is None:
            print("Removal cancelled.")
            return 0
        purge_config = selected

    backups = []
    bashrc_backup = remove_marked_block(BASHRC, BEGIN_MARKER, END_MARKER)
    if bashrc_backup:
        backups.append(bashrc_backup)
    profile_backup = remove_marked_block(
        HOME / ".bash_profile", PROFILE_BEGIN_MARKER, PROFILE_END_MARKER
    )
    if profile_backup:
        backups.append(profile_backup)

    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)

    if purge_config:
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        for old_config in CONFIG_DIR.glob("config.before-reconfigure-*") if CONFIG_DIR.exists() else []:
            old_config.unlink()
        if LIFECYCLE_FILE.exists():
            LIFECYCLE_FILE.unlink()
        try:
            CONFIG_DIR.rmdir()
        except OSError:
            pass

    legacy_warning = False
    if BASHRC.exists():
        text = BASHRC.read_text(errors="replace")
        legacy_warning = bool(
            re.search(r"(?m)^(?:aicmd|_ai_replace_line)\s*\(\)\s*\{", text)
        )

    print("\nBash AI integration and installed prompts were removed.")
    print("Client configuration was removed." if purge_config else "Client configuration was preserved.")
    print("The model runtime and downloaded models were not modified.")
    for saved in backups:
        print(f"Startup-file backup: {saved}")
    if legacy_warning:
        print("Warning: older inline aicmd functions remain in .bashrc and were not guessed or removed.")
    print("Start a new Bash session to clear functions already loaded in this shell.")
    return 0


def choose_existing_action() -> str:
    print("\nAn existing Bash AI installation was detected.")
    print("  1. Update program and prompt files; keep server settings")
    print("  2. Update files and modify server/model settings")
    print("  3. Repair/reinstall managed files and modify settings")
    print("  4. Remove installation")
    print("  5. Cancel")
    choices = {
        "1": "update",
        "2": "reconfigure",
        "3": "repair",
        "4": "remove",
        "5": "cancel",
    }
    while True:
        value = input("Choose an action [1]: ").strip() or "1"
        if value in choices:
            return choices[value]
        print("Enter 1, 2, 3, 4, or 5.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconfigure", action="store_true", help="update server/model settings")
    parser.add_argument(
        "--server",
        metavar="HOST_OR_URL",
        help="set the model server hostname, host:port, or complete endpoint URL",
    )
    parser.add_argument(
        "--temperature", type=float, metavar="VALUE", help="set generation temperature from 0 through 2"
    )
    parser.add_argument("--model", metavar="NAME", help="set the model identifier sent to the server")
    parser.add_argument(
        "--runtime", choices=tuple(RUNTIMES), help="set the endpoint/runtime preset"
    )
    parser.add_argument(
        "--max-tokens", type=int, metavar="COUNT", help="set the maximum generated-token count"
    )
    parser.add_argument("--remove", action="store_true", help="remove the installed integration")
    parser.add_argument(
        "--purge-config",
        action="store_true",
        help="with --remove, also remove saved client configuration",
    )
    parser.add_argument(
        "--non-interactive", action="store_true", help="keep existing/default settings without questions"
    )
    lifecycle_group = parser.add_mutually_exclusive_group()
    lifecycle_group.add_argument(
        "--lifecycle",
        action="store_true",
        default=None,
        help="install ai-start and ai-stop when the runtime/platform is supported",
    )
    lifecycle_group.add_argument(
        "--no-lifecycle",
        dest="lifecycle",
        action="store_false",
        help="do not install, or remove managed, ai-start and ai-stop functions",
    )
    args = parser.parse_args()

    if args.purge_config and not args.remove:
        parser.error("--purge-config requires --remove")
    if args.temperature is not None and not 0 <= args.temperature <= 2:
        parser.error("--temperature must be from 0 through 2")
    if args.max_tokens is not None and args.max_tokens < 1:
        parser.error("--max-tokens must be a positive integer")
    if args.remove:
        return remove_installation(args.purge_config, not args.non_interactive and not args.purge_config)

    current = read_config()
    is_existing = installed()
    has_config_overrides = any(
        value is not None
        for value in (args.server, args.temperature, args.model, args.runtime, args.max_tokens)
    )
    action = "new"
    legacy_without_config = is_existing and not CONFIG_FILE.exists()
    if legacy_without_config and not args.non_interactive:
        print("\nAn earlier inline Bash AI installation was detected.")
        print("It will be migrated to managed files and needs server configuration.")
        action = "reconfigure"
    elif is_existing and not args.non_interactive and not args.reconfigure and not has_config_overrides:
        action = choose_existing_action()
        if action == "cancel":
            return 0
        if action == "remove":
            return remove_installation(False, True)
    elif is_existing:
        action = "reconfigure" if args.reconfigure else "update"

    should_configure = (
        action in {"new", "reconfigure", "repair"} or args.reconfigure or has_config_overrides
    )
    values = current
    if should_configure and not args.non_interactive and not has_config_overrides:
        values = configure(current)
    elif has_config_overrides:
        values = dict(current)
        selected_runtime = args.runtime or values.get("BASH_AI_RUNTIME", "custom")
        if selected_runtime not in RUNTIMES:
            selected_runtime = "custom"
        if args.runtime and args.runtime != values.get("BASH_AI_RUNTIME"):
            values["BASH_AI_RUNTIME"] = selected_runtime
            if args.server is None:
                values["BASH_AI_ENDPOINT"] = str(RUNTIMES[selected_runtime]["endpoint"])
            if args.model is None:
                values["BASH_AI_MODEL"] = str(RUNTIMES[selected_runtime]["model"])
        if args.server is not None:
            values["BASH_AI_ENDPOINT"] = normalize_endpoint(
                args.server, int(RUNTIMES[selected_runtime]["port"])
            )
        if args.temperature is not None:
            values["BASH_AI_TEMPERATURE"] = str(args.temperature)
        if args.model is not None:
            values["BASH_AI_MODEL"] = args.model
        if args.max_tokens is not None:
            values["BASH_AI_MAX_TOKENS"] = str(args.max_tokens)
        values["BASH_AI_RUNTIME"] = selected_runtime
        values["BASH_AI_PROMPT_DIR"] = str(PROMPT_DIR)

    copy_program_files()
    if should_configure or not CONFIG_FILE.exists():
        write_config(values)
    lifecycle_choice = args.lifecycle
    lifecycle_available = lifecycle_content(values["BASH_AI_RUNTIME"]) is not None
    if (
        lifecycle_choice is None
        and lifecycle_available
        and should_configure
        and not args.non_interactive
    ):
        default_lifecycle = LIFECYCLE_FILE.exists()
        suffix = "Y/n" if default_lifecycle else "y/N"
        answer = input(f"Install optional ai-start and ai-stop functions? [{suffix}]: ").strip().lower()
        lifecycle_choice = default_lifecycle if not answer else answer in {"y", "yes"}
    lifecycle_installed = write_lifecycle(values, lifecycle_choice)
    bashrc_backup = update_bashrc()
    profile_backup = update_macos_bash_profile()

    print("\nBash AI installation complete.")
    print(f"Runtime: {values['BASH_AI_RUNTIME']}")
    print(f"Server:  {values['BASH_AI_ENDPOINT']}")
    print(f"Model:   {values['BASH_AI_MODEL']}")
    print(f"Prompts: {PROMPT_DIR}")
    if lifecycle_installed:
        print(f"Start/stop: {LIFECYCLE_FILE}")
    else:
        print("Start/stop: not installed for this runtime/platform")
    if bashrc_backup:
        print(f"Backup:  {bashrc_backup}")
    if profile_backup:
        print(f"Backup:  {profile_backup}")
    print("Reload with: source ~/.bashrc")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInstallation cancelled.", file=sys.stderr)
        raise SystemExit(130)
