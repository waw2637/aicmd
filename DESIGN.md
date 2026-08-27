# Design

AI CMD is deliberately a thin shell-to-model adapter.

The request path is short:

```text
Bash function
  -> read a text prompt
  -> optionally collect shell context
  -> concatenate the request
  -> encode one JSON document with Python
  -> POST it with curl
  -> extract response text with Python
  -> print it or place it on the Readline input line
```

There is no resident AI CMD process. The selected model server is the only daemon.

## Why Bash and Python

Bash owns the shell state and Readline integration. Python handles the places
where shell quoting is needlessly risky: JSON encoding, response parsing,
configuration changes, and installer menus. `curl` keeps the network boundary
visible.

## Intentional boundaries

AI CMD does not:

- install, update, start, or stop model runtimes;
- download or remove models;
- execute generated commands automatically;
- maintain conversations in a database;
- hide prompts inside compiled code;
- require a specific inference engine.

It is effectively a useful string concatenator with shell ergonomics.

## Make it yours

Change command names, context collection, HTTP behavior, and Ctrl-G handling in
`bash-ai.bash`. Change model behavior in `prompts/`. Change configuration,
prompt editing, help, and installation in the correspondingly named Python
files.

The running copies live under `~/.local/share/bash-ai/`. Edit those to
experiment. Edit this repository and rerun `./install.sh` when a change should
survive reinstalling or belong in your fork.
