# Security

## Generated commands

Model output is untrusted input. Ctrl-G inserts a generated command onto the
Bash input line but never executes it. Review every command before pressing
Enter. Prompt instructions are not a security boundary.

## Context and secrets

Context-aware requests may contain information about the current shell,
directory, environment, history, and Git repository. Environment variable names
that look sensitive are redacted, but redaction cannot guarantee that no secret
appears elsewhere. Use `--no-shell-context` when the server should receive
only the request.

API keys are stored in `~/.config/bash-ai/config`. Keep that file mode
`0600`. Prefer HTTPS for servers outside the local machine or trusted network.

## Reporting

Please use GitHub private vulnerability reporting when available. Never include
real credentials or private shell context in a public issue.
