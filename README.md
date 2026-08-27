# AI CMD
Yes this tool was created with AI assistance for those who care. Please
read this readme, it tell you important stuff.

# BackStory

### In the beginning
I like many of you relied on the google overlord to look up syntax, regex, or
the 2am brainfog induced memory loss command help. It sucks to flip around
like that. So when i got may new laptop with an 
NPU (Nearly Pathetically Useless) AI chip that is able to,
despite my hate, run tiny (Basically useless) LLMs i couldn't have cared less.
"Then in an out of weeks and almost over a year" (Where the Wild Things Are).
I had an idea, "What if I am lame?" I know I am lame, "What if this crazy NPU could
run a tiny (useless) llm that could save me a few browser open and load and googles
a day?" Proceed to boring IT work of getting an amd npu working on linux. Then lets see,
certainly someone has an AI cmd line tool. Yep.

### Frustration
I proceed to start looking at AI CMD tools. And this is where I being me lost my
mind for almost a day into the night looking at these different options then entire
time saying "I could do what I want with a freaking declared function". 
So I did.

### Evolution
Well the declared function worked how i needed. But i have alot of computer systems
and I found that i wanted to use this on alot of them. I setup a local small server
and then started pointing non AI capable things at that. At that point I needed a
way to update installs as i added tweaks and features etc. So came an installer/Update
tool and a removal script. But i needed prompts that fit each environment so came 
the external prompt files. Now we have something and here we are now throwing it
into the wild of git-hub. Not because this is in any way a special tool. Quite the
opposite, its boring mundane scripts that just concats strings together, but we
tech people are lazy and if it save someone else having to invest a few minutes of
time to get what they want then here it is.

### What is it
I wanted a simple AI command line tool, one that i could change easily to suit.
I went looking and though what i found was TOO complex. I dont need a platform to
concat strings. Why not just have some nice little scripts and some text files to 
hold some context. Here we are AI CMD.

### What's Cool
You can read and understand this thing in 20 minutes. NOTHING is hidden. You are
meant to change anything and everything. Its you shell after all.

### Prompts
It comes with some extremely generic prompts. These will need to be tuned to get
the best performance from this tool. This is a feature.

### Nuances that you can change
You can change everything, download it look at it say this guys an idiot and change it all!

I have set the `crtl-g` command to NOT pass any context from the shell. If you want
context you would use the `aicmd`. you can edit context "length" by editing the 
`/.bashrc`.

If you think "I want more command versions, prompts, whatever". Great, Add them.
That's the point. This tool is the bare bones and is a pile of simple scripts, 
change them.

Hell Dump the files into your favorite ai thing and ask it to change it. Do what
makes you happy. That is the point of bash. To be powerful in its simplicity.

# What you actually Came here for

This package installs a runtime-independent Bash integration for local or
remote language-model servers.

- `Ctrl-G`: replace the text currently typed at the Bash prompt with one
  generated command, without sending shell context.
- `aicmd`: generate one command with the current Bash session context.
- `ai`: general local-model requests, with optional presets and shell context.
- `aicode`, `aidebug`, and `aireview`: focused helpers for longer technical work.
- Linux- and macOS-specific command prompts. The macOS prompt accounts for BSD
  userland and does not invent Linux-only commands.

The client talks to an OpenAI-compatible `chat/completions` endpoint. You can use
guided presets that are 

## Platform support

The Bash integration supports Linux and macOS. Ollama and llama.cpp are the
normal local macOS choices. Lemonade, FastFlowLM, or any other compatible
server can be used locally where supported or reached over the network.

macOS ships with zsh as the default interactive shell. `Ctrl-G` integration in
this package uses Bash Readline, so start Bash before using it:

```bash
bash
```

If you want Bash as your login shell, install a current Bash with Homebrew and
follow Homebrew's shell-registration instructions. Changing the login shell is
optional; the package works whenever an interactive Bash session is running.

## Requirements

- Bash 3.2 or newer
- `curl`
- Python 3
- An OpenAI-compatible local or remote chat-completions endpoint

Ubuntu/Debian prerequisites:

```bash
sudo apt update
sudo apt install -y curl python3
```

macOS prerequisites with Homebrew:

```bash
brew install bash python
```

## Install

Gather up your details:
  -Hostname/Ip/port
  -The Model Name
  -Maximum output tokens and model temp
  -this thing does not have a safe way to store and API KEY so that on you

Check the prompts make tweaks, change command names, do what you want
then extract the archive, enter the extracted directory, and run the Python
installer through its small shell launcher:

```bash
./install.sh
```

Reload Bash:

```bash
source ~/.bashrc
```

On a new installation it asks for:

- The model server location. You may enter a hostname, IP address,
  `host:port`, or a complete HTTP(S) URL.
- The model name.
- Maximum output tokens and temperature.
- An optional API key, entered without terminal echo.

The installer normalizes a bare host such as `192.168.1.26` to:

```text
http://192.168.1.26:11434/v1/chat/completions
```

The inferred port follows the chosen runtime; the installer shows the complete
endpoint before saving it.

The installer then:

1. Copies the integration to `~/.local/share/bash-ai/`.
2. Installs each prompt as a separate file under
   `~/.local/share/bash-ai/prompts/`.
3. Creates `~/.config/bash-ai/config` with the selected server settings.
4. Adds one guarded source block to `~/.bashrc`.
5. On macOS, ensures login Bash sessions load `.bashrc` through one guarded
   block in `~/.bash_profile`.
6. Backs up shell startup files before changing them.
7. Validates the resulting Bash syntax and stops without replacing it if validation
   fails.

When it detects an existing managed installation—or the earlier inline
`aicmd`/`_ai_replace_line` functions in `.bashrc`—it offers to:

1. Update the program and prompt files while keeping server settings.
2. Update files and modify the server/model settings.
3. Repair the managed installation and modify settings.
4. Remove the installation.
5. Cancel.

Existing configuration is preserved by the update-only choice. Reconfiguration
creates a timestamped backup before writing new settings.

During migration from the earlier inline `.bashrc` version, the installer adds
the managed source block at the end of `.bashrc`, so the packaged functions and
prompts take precedence. It leaves the old block in the timestamped backup and
does not attempt an unsafe guess at its boundaries; after verifying the new
installation, you may remove the old inline definitions from `.bashrc`.

## Configure the endpoint

Edit:

```text
~/.config/bash-ai/config
```

Default values:

```bash
BASH_AI_RUNTIME="ollama"
BASH_AI_ENDPOINT="http://127.0.0.1:11434/v1/chat/completions"
BASH_AI_MODEL="gemma3:4b"
BASH_AI_API_KEY=""
BASH_AI_MAX_TOKENS="4096"
BASH_AI_TEMPERATURE="0.1"
```

For a remote endpoint, use HTTPS and set the key in the config. Protect it:

```bash
chmod 600 ~/.config/bash-ai/config
```

You can also rerun the installer and choose the reconfiguration option, or ask
for it directly:

```bash
./install.sh --reconfigure
```

For unattended updates that preserve the installed server settings:

```bash
./install.sh --non-interactive
```

### Command-line configuration

Server and generation settings can be changed without entering the interactive
menu. Unspecified settings are preserved:

```bash
./install.sh --server modelbox:11434
./install.sh --temperature 0.2
./install.sh --model gemma3:4b --max-tokens 8192
```

Switch the runtime preset, server, and model together:

```bash
./install.sh \
  --runtime llama.cpp \
  --server modelbox:8080 \
  --model local-model \
  --temperature 0.1
```

Accepted options:

| Option | Purpose |
| --- | --- |
| `--server HOST_OR_URL` | Change the server hostname, host:port, or full endpoint URL. |
| `--temperature VALUE` | Set temperature from `0` through `2`. |
| `--runtime NAME` | Select `ollama`, `llama.cpp`, `lemonade`, `fastflowlm`, or `custom`. |
| `--model NAME` | Change the model identifier sent with requests. |
| `--max-tokens COUNT` | Change the maximum generated-token count. |

Changing only `--runtime` applies that runtime's default endpoint and model.
Changing `--server` preserves the selected runtime and uses its default port
when the supplied hostname has no port. Every configuration rewrite creates a
timestamped backup.

## Prompt files

Prompts are source-controlled as individual files in the package's `prompts/`
directory and installed individually at:

```text
~/.local/share/bash-ai/prompts/
```

The command prompt is selected at runtime:

| Platform | Prompt file |
| --- | --- |
| Linux | `linux-command.txt` |
| macOS | `macos-command.txt` |
| Other Unix | `unix-command.txt` |

The general, code, debug, and review presets use `general.txt`, `code.txt`,
`debug.txt`, and `review.txt`. You may edit the installed files directly for
local prompt experiments. A later installer update intentionally replaces the
installed prompts with the versions from the new package; edit the package
copies first if you want custom prompt changes to survive updates.

To keep prompts in a different directory, change `BASH_AI_PROMPT_DIR` in the
config file. The installer-managed default is:

```bash
BASH_AI_PROMPT_DIR="$HOME/.local/share/bash-ai/prompts"
```

## Supported model servers

The installer uses these endpoint presets:

| Runtime | Default chat-completions endpoint | Typical platforms |
| --- | --- | --- |
| Ollama | `http://127.0.0.1:11434/v1/chat/completions` | Linux, macOS |
| llama.cpp | `http://127.0.0.1:8080/v1/chat/completions` | Linux, macOS |
| Lemonade | `http://127.0.0.1:13305/v1/chat/completions` | Supported Lemonade hosts |
| FastFlowLM | `http://127.0.0.1:52625/v1/chat/completions` | Supported FastFlowLM hosts |
| Custom | User supplied | Any compatible server |

These are only connection presets. The package never installs, starts, stops,
updates, or removes a model runtime.

Ollama documents its OpenAI-compatible API at port `11434`, llama.cpp exposes
the same chat-completions route from `llama-server` and normally uses port
`8080`, and Lemonade documents it at port `13305`:

- [Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility)
- [llama.cpp server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
- [Lemonade OpenAI-compatible API](https://lemonade-server.ai/docs/api/openai/)

For Ollama, prepare a model separately before running the installer:

```bash
ollama pull gemma3:4b
```

For llama.cpp, a typical server invocation is:

```bash
llama-server --model /path/to/model.gguf --port 8080 --ctx-size 65536
```

Use the exact model identifier exposed by your runtime when the installer asks
for `Model name`. Some single-model llama.cpp servers accept an arbitrary model
label, while routers and multi-model servers require an exact identifier.

For a remote server, enter its complete HTTPS endpoint and API key during
installation, or update the config later:

```bash
BASH_AI_RUNTIME="custom"
BASH_AI_ENDPOINT="https://your-server.example/v1/chat/completions"
BASH_AI_MODEL="your-model-name"
BASH_AI_API_KEY="replace-me"
```

## macOS behavior

Use Ollama, llama.cpp, or another compatible server on macOS. FastFlowLM is not
presented as a macOS runtime path.

The macOS command preset understands that the native tools are BSD variants. In
particular, it avoids assuming GNU-only flags for `sed`, `stat`, `date`,
`find`, `xargs`, `du`, and `sort`; prefers `launchctl` and `log` over systemd;
uses `diskutil` rather than `lsblk`; and does not assume `/proc` exists.

## Usage

Type a terse request, do not press Enter, then press `Ctrl-G`:

```text
show the ten processes using the most memory
```

The typed text is replaced by a command. Review it and press Enter yourself.
The binding never executes generated commands automatically.

Generate a context-aware command:

```bash
aicmd "show information relevant to the current project"
```

Generate without shell context:

```bash
aicmd --no-shell-context "what owns TCP port 11434"
```

Other helpers:

```bash
ai "explain why this command failed"
aicode "write a robust backup script"
aidebug "diagnose the previous failure"
aireview "review the shell script named deploy.sh"
```

### Help

Open the complete interactive help menu:

```bash
ai --help
```

Display quick help:

```bash
ai -help
ai -h
ai '?'
```

The question mark is quoted so Bash cannot expand it as a filename wildcard.
Complete help can also open a section directly:

```bash
ai --help commands
ai --help configuration
ai --help prompts
ai --help troubleshooting
```

When standard input or output is not a terminal, `ai --help` prints all help
sections without opening the interactive menu. The help implementation is the
installed `~/.local/share/bash-ai/ai_help.py` file and can be customized like
the other package utilities.

### Change settings with `ai-conf`

Display the active configuration without exposing the API key:

```bash
ai-conf
```

Change the server, model, or temperature in the current shell:

```bash
ai-conf --server modelbox:11434
ai-conf --model gemma3:4b
ai-conf --temperature 0.2
```

Options can be combined:

```bash
ai-conf \
  --runtime llama.cpp \
  --server modelbox:8080 \
  --model local-model \
  --temperature 0.1 \
  --max-tokens 8192
```

`ai-conf` updates `~/.config/bash-ai/config`, creates a timestamped backup, and
reloads the new values into the current Bash session immediately. Changing only
the runtime applies that runtime's default server and model. Changing only the
server, temperature, model, or token limit preserves all other settings.

### Edit presets with `ai-prompt`

Open the interactive preset menu:

```bash
ai-prompt
```

The menu lists every installed prompt and marks the command-generation prompt
active for the current operating system. After selection, it opens the file
using `$VISUAL`, `$EDITOR`, `nano`, `vim`, or `vi`, in that order.

Open a preset directly:

```bash
ai-prompt command
ai-prompt general
ai-prompt code
ai-prompt debug
ai-prompt review
```

List available prompt names or choose an editor for one invocation:

```bash
ai-prompt --list
ai-prompt code --editor nano
```

`command` resolves to `linux-command.txt`, `macos-command.txt`, or
`unix-command.txt` for the current platform. Before opening an editor,
`ai-prompt` creates a timestamped backup beside the prompt file. An empty prompt
is rejected and restored automatically. Because prompts are read from disk for
every request, saved changes apply immediately without reloading Bash.

## Customize commands and core behavior

The integration is ordinary Bash and Python rather than a sealed application.
Its command names, helper behavior, key binding, context collection, request
format, and configuration interface can all be changed.

There are two useful customization layers:

| Goal | File to edit |
| --- | --- |
| Experiment with the running installation | `~/.local/share/bash-ai/bash-ai.bash` |
| Make changes survive installation and package updates | `bash-ai.bash` inside the extracted package |
| Change `ai-conf` behavior | Installed `ai_conf.py` or the package copy |
| Change the `ai-prompt` menu | Installed `ai_prompt.py` or the package copy |
| Change interactive and quick help | Installed `ai_help.py` or the package copy |
| Change prompt wording only | Use `ai-prompt`, or edit the installed `prompts/` files |

The public commands are Bash functions near the end of `bash-ai.bash`:

```text
ai
aicmd
aicode
aidebug
aireview
aichat
ai-model
ai-health
ai-conf
ai-prompt
```

Rename a function definition and any internal call sites to change a command
name. For example, a customized package could rename `aicmd()` to `askcmd()`.
The Ctrl-G behavior is defined by `_ai_replace_line()` and this binding:

```bash
bind -x '"\C-g":_ai_replace_line'
```

Change `\C-g` to another Readline key sequence to use a different shortcut.
After changing installed Bash functions or bindings, reload them:

```bash
source ~/.bashrc
```

Prompt text changes do not require a reload, and Python utility changes are
used on their next invocation.

Installer updates intentionally replace managed program and prompt files. To
distribute or retain renamed commands and other core modifications, edit the
files in the extracted installation package and run its installer. Direct edits
to the running installation are best treated as experiments unless copied back
into that package payload.

`aicmd` and the other helpers accept `--no-shell-context`. `ai` also accepts:

```text
--preset NAME
--context TEXT
--message TEXT
--no-shell-context
```

## Context and privacy

Context-aware requests include the working directory, previous status, a
filtered environment, recent history, aliases, shell options, jobs, a short
directory listing, and Git status when applicable. Values of variables whose
names look like passwords, tokens, API keys, cookies, credentials, or private
keys are redacted.

`Ctrl-G` deliberately sends no shell snapshot. It sends only the platform-aware
command prompt and the text currently on the command line.

All generated commands must be reviewed before execution. The model is asked to
prefer read-only inspection for ambiguous requests, but model output is not a
security boundary.

## Troubleshooting

Show the selected runtime, model, and endpoint:

```bash
ai-model
```

Confirm the endpoint is reachable and list its available models:

```bash
ai-health
```

Show the active client configuration without exposing the API key:

```bash
ai-model
```

Check the installed functions and key binding:

```bash
declare -f aicmd
declare -f ai-conf
declare -f ai-prompt
bind -S | grep '"\\C-g"'
```

If `Ctrl-G` prints a terminal bell, confirm that the current shell is Bash:

```bash
printf '%s\n' "$BASH_VERSION"
```

## Uninstall

Rerun the main installer and select `Remove installation`, or run:

```bash
./install.sh --remove
```

The interactive remover asks whether to preserve or delete the saved server
configuration. For a non-interactive removal that preserves configuration:

```bash
./install.sh --remove --non-interactive
```

To remove the integration and saved client configuration:

```bash
./install.sh --remove --purge-config
```

Removal deletes the managed integration and prompt directory and removes the
guarded startup blocks from `.bashrc` and, on macOS, `.bash_profile`. Startup
files are backed up first. The selected model runtime and downloaded models are
never modified.
