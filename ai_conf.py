#!/usr/bin/env python3
"""Show or change the installed Bash AI client configuration."""

from __future__ import annotations

import argparse
import os
import re
import shlex
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urlunparse


HOME = Path.home()
CONFIG_FILE = Path(os.environ.get("BASH_AI_CONFIG", HOME / ".config/bash-ai/config"))
PROMPT_DIR = HOME / ".local/share/bash-ai/prompts"
RUNTIMES = {
    "ollama": (11434, "http://127.0.0.1:11434/v1/chat/completions", "gemma3:4b"),
    "llama.cpp": (8080, "http://127.0.0.1:8080/v1/chat/completions", "local-model"),
    "lemonade": (13305, "http://127.0.0.1:13305/v1/chat/completions", "Qwen3-0.6B-GGUF"),
    "fastflowlm": (52625, "http://127.0.0.1:52625/v1/chat/completions", "gemma4-it:e4b"),
    "custom": (8000, "http://127.0.0.1:8000/v1/chat/completions", "local-model"),
}
DEFAULTS = {
    "BASH_AI_RUNTIME": "ollama",
    "BASH_AI_ENDPOINT": RUNTIMES["ollama"][1],
    "BASH_AI_MODEL": RUNTIMES["ollama"][2],
    "BASH_AI_API_KEY": "",
    "BASH_AI_MAX_TOKENS": "4096",
    "BASH_AI_TEMPERATURE": "0.1",
    "BASH_AI_PROMPT_DIR": str(PROMPT_DIR),
}


def read_config() -> dict[str, str]:
    if not CONFIG_FILE.exists():
        raise SystemExit(f"Bash AI config does not exist: {CONFIG_FILE}")
    values = dict(DEFAULTS)
    pattern = re.compile(r"^([A-Z][A-Z0-9_]*)=(.*)$")
    explicit_runtime = False
    for raw_line in CONFIG_FILE.read_text(errors="replace").splitlines():
        match = pattern.match(raw_line.strip())
        if not match or match.group(1) not in values:
            continue
        explicit_runtime = explicit_runtime or match.group(1) == "BASH_AI_RUNTIME"
        try:
            parsed = shlex.split(match.group(2), posix=True)
            values[match.group(1)] = parsed[0] if parsed else ""
        except ValueError:
            pass
    if not explicit_runtime:
        endpoint = values["BASH_AI_ENDPOINT"]
        values["BASH_AI_RUNTIME"] = next(
            (name for name, details in RUNTIMES.items() if f":{details[0]}/" in endpoint),
            "custom",
        )
    return values


def normalize_endpoint(value: str, default_port: int) -> str:
    value = value.strip().rstrip("/")
    if "://" not in value:
        if "/" not in value and ":" not in value:
            value += f":{default_port}"
        value = "http://" + value
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("server must be a hostname, host:port, or HTTP(S) URL")
    path = parsed.path.rstrip("/")
    if path.endswith("/v1/chat/completions"):
        pass
    elif path.endswith("/v1"):
        path += "/chat/completions"
    else:
        path += "/v1/chat/completions"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def shell_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("$", "\\$").replace("`", "\\`")
    return f'"{escaped}"'


def write_config(values: dict[str, str]) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = CONFIG_FILE.with_name(f"config.before-ai-conf-{stamp}")
    backup.write_bytes(CONFIG_FILE.read_bytes())
    os.chmod(backup, 0o600)
    lines = ["# Bash AI client configuration."]
    lines.extend(f"{name}={shell_quote(values[name])}" for name in DEFAULTS)
    content = "\n".join(lines) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=".config.", dir=str(CONFIG_FILE.parent))
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(content)
        os.chmod(temporary, 0o600)
        os.replace(temporary, CONFIG_FILE)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return backup


def show(values: dict[str, str]) -> None:
    print(f"Runtime:     {values['BASH_AI_RUNTIME']}")
    print(f"Server:      {values['BASH_AI_ENDPOINT']}")
    print(f"Model:       {values['BASH_AI_MODEL']}")
    print(f"Temperature: {values['BASH_AI_TEMPERATURE']}")
    print(f"Max tokens:  {values['BASH_AI_MAX_TOKENS']}")
    print(f"API key:     {'configured' if values['BASH_AI_API_KEY'] else 'not configured'}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", metavar="HOST_OR_URL", help="change the model server")
    parser.add_argument("--temperature", type=float, metavar="VALUE", help="set temperature from 0 through 2")
    parser.add_argument("--model", metavar="NAME", help="change the model identifier")
    parser.add_argument("--runtime", choices=tuple(RUNTIMES), help="change the runtime preset")
    parser.add_argument("--max-tokens", type=int, metavar="COUNT", help="change maximum generated tokens")
    args = parser.parse_args()

    if args.temperature is not None and not 0 <= args.temperature <= 2:
        parser.error("--temperature must be from 0 through 2")
    if args.max_tokens is not None and args.max_tokens < 1:
        parser.error("--max-tokens must be a positive integer")
    if args.model is not None and not args.model.strip():
        parser.error("--model cannot be empty")

    values = read_config()
    changed = any(
        item is not None
        for item in (args.server, args.temperature, args.model, args.runtime, args.max_tokens)
    )
    if not changed:
        show(values)
        return 0

    runtime = args.runtime or values.get("BASH_AI_RUNTIME", "custom")
    if runtime not in RUNTIMES:
        runtime = "custom"
    if args.runtime and args.runtime != values.get("BASH_AI_RUNTIME"):
        values["BASH_AI_RUNTIME"] = runtime
        if args.server is None:
            values["BASH_AI_ENDPOINT"] = RUNTIMES[runtime][1]
        if args.model is None:
            values["BASH_AI_MODEL"] = RUNTIMES[runtime][2]
    if args.server is not None:
        try:
            values["BASH_AI_ENDPOINT"] = normalize_endpoint(args.server, RUNTIMES[runtime][0])
        except ValueError as exc:
            parser.error(str(exc))
    if args.temperature is not None:
        values["BASH_AI_TEMPERATURE"] = str(args.temperature)
    if args.model is not None:
        values["BASH_AI_MODEL"] = args.model
    if args.max_tokens is not None:
        values["BASH_AI_MAX_TOKENS"] = str(args.max_tokens)
    values["BASH_AI_RUNTIME"] = runtime
    values["BASH_AI_PROMPT_DIR"] = str(PROMPT_DIR)

    backup = write_config(values)
    show(values)
    print(f"Backup:      {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
