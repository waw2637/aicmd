# Contributing

Contributions are welcome, especially portability fixes, clearer prompts,
better errors, and small improvements that preserve the project's
inspectability.

Before adding a dependency or abstraction, ask whether a few obvious lines of
Bash or Python solve the problem more clearly. Feature count is not the goal.

## Guidelines

- Keep Bash compatible with Bash 3.2 unless a change explicitly raises the
  minimum version.
- Keep Linux and macOS command behavior distinct where GNU and BSD tools differ.
- Never automatically execute model-generated commands.
- Keep prompts as separate text files.
- Avoid runtime-specific client behavior when an OpenAI-compatible request works.
- Document user-visible flags and commands in both `README.md` and `ai_help.py`.
- Keep changes easy for another person to read, alter, or remove.

## Checks

```bash
bash -n bash-ai.bash install.sh uninstall.sh
python3 -m py_compile installer.py ai_conf.py ai_prompt.py ai_help.py
./install.sh --help
```
