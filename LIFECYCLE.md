# Starting and stopping the model server

AI CMD can install two small convenience functions:

```bash
ai-start
ai-stop
```

They are installed only when the installer knows a reasonable default for the
selected runtime and operating system:

| Runtime | Platform | Default |
| --- | --- | --- |
| Ollama | Linux | `sudo systemctl start/stop ollama` |
| Ollama | macOS | Open or quit the Ollama application |
| FastFlowLM | Linux | `systemctl --user start/stop fastflowlm.service` |

llama.cpp, Lemonade, custom endpoints, and remote servers do not receive these
functions. Their launch commands depend on model paths, arguments, containers,
service names, or a different host. Guessing would be less useful than being
honest.

## Customize the commands

The installer writes supported defaults to:

```text
~/.config/bash-ai/lifecycle.bash
```

The location is also commented inside the generated file. It contains ordinary
Bash function definitions. For a server outside the defaults, create it
yourself:

```bash
ai-start() {
    your-server-start-command
}

ai-stop() {
    your-server-stop-command
}
```

Then reload Bash:

```bash
source ~/.bashrc
```

You can override the location before loading AI CMD by setting
`BASH_AI_LIFECYCLE_FILE`. A lifecycle file without the installer's managed
header is treated as user-owned and is preserved during updates.

Changing the configured endpoint does not imply that the client has permission
to control that server. Remote endpoints intentionally receive no lifecycle
functions.
