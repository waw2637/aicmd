# Changelog

## 1.6.0

- Added opt-in `ai-start` and `ai-stop` functions for supported local
  runtime/platform combinations, with `--lifecycle` and `--no-lifecycle`
  installer controls.
- Kept lifecycle commands in the editable
  `~/.config/bash-ai/lifecycle.bash` file.
- Avoided installing guessed lifecycle commands for custom or unsupported
  servers.

## 1.5.0

- Added Linux, macOS, and generic Unix command prompts.
- Added runtime-neutral configuration for Ollama, llama.cpp, Lemonade,
  FastFlowLM, and custom OpenAI-compatible endpoints.
- Added `ai-conf` for changing server, model, temperature, and token limits.
- Added `ai-prompt` for selecting and editing prompt files.
- Added complete interactive help and quick-help forms.
- Added installer update, reconfigure, repair, migration, and removal flows.
- Kept Ctrl-G context-free while retaining context-aware `aicmd` behavior.
