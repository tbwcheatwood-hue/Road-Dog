<h1 align="center">Road Dog</h1>

<p align="center">
  <strong>Your AI. Your crew. Your road.</strong><br />
  Sam(wise) is your AI agent companion for the desktop — coding agents, voice, computer use, agents, marketplace, memory.
</p>

<p align="center">
  <a href="https://github.com/tbwcheatwood-hue/Road-Dog/blob/main/LICENSE"><img alt="Apache 2.0" src="https://img.shields.io/badge/License-Apache_2.0-F7F7F4?labelColor=0A0A0A" /></a>
  <a href="https://github.com/tbwcheatwood-hue/Road-Dog/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/tbwcheatwood-hue/Road-Dog/actions/workflows/ci.yml/badge.svg" /></a>
  <a href="https://discord.gg/x7USduHxbc"><img alt="Discord" src="https://img.shields.io/badge/Discord-join-F7F7F4?labelColor=0A0A0A&amp;logo=discord&amp;logoColor=white" /></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#features">Features</a> ·
  <a href="#samwise-your-ai-companion">Sam(wise)</a> ·
  <a href="https://github.com/tbwcheatwood-hue/Road-Dog/tree/main/docs">Docs</a> ·
  <a href="https://discord.gg/x7USduHxbc">Discord</a>
</p>

<p align="center">
  <img src="assets/roaddog-logo.svg" alt="Road Dog logo" width="100%"/>
  <br/><sub>Road Dog architecture — Core engine, Agentic IDE, The Crew, Voice, Computer Use, Marketplace and Memory.</sub>
</p>

---

Road Dog is one desktop app for everything AI can do on your computer. It has a workspace where several coding agents run side by side, AI agents that keep their own memory, a voice assistant with a wake word, control of your desktop and browser, and a plugin marketplace. It works with the models you already pay for, whether hosted, local or through a subscription you have.

You say what you want. Sam answers you, does the task on your computer, or hands it to the agent that fits, and you can watch every step.

It is free and open source, and it runs on your own machine. You do not need an account, and there is no cloud of ours between you and your models. It runs on Windows, macOS and Linux, and as a server without a screen.

## Quick Start

Running from a checkout is the local development install. It is separate from a signed installer: signature checks on published installers stay in place, and a source run does not replace them.

**Install from source**

```bash
git clone https://github.com/tbwcheatwood-hue/Road-Dog.git
cd Road-Dog
python3 -m venv .venv
. .venv/bin/activate
pip install -e . --no-deps
```

`cryptography` is a normal runtime dependency and installs from PyPI (`cryptography>=50.0.2`). The hashed `requirements.txt` also points at a custom native-crypto package index used by the locked installer build. That index is not required for this local install, and a missing index must not be bypassed by turning signature checks off.

On Linux, voice needs the PortAudio library (Debian and Ubuntu: `libportaudio2`). The desktop window needs WebKitGTK (`gir1.2-webkit2-4.1` and `libgtk-3`) plus `pip install 'pywebview>=5.3'`. When those are absent, `./run.sh --headless` still serves the same interface in a browser.

Build the interface once, from `jarvis/ui/web/frontend/`:

```bash
npm install
npm run build
```

**Launch**

```bash
# Full desktop app (a display is required)
./run.sh

# API and browser interface, no desktop window
./run.sh --headless
```

The app listens on `http://127.0.0.1:47821`. On Linux the first desktop start writes `~/.local/share/applications/road-dog.desktop`.

Road Dog keeps its own files. Set `JARVIS_DATA_DIR` when another install already uses the home-directory fallback, and do not point it at that other install's data. Credentials stay in the OS credential store. A new checkout does not copy or delete an existing data directory.

**Connect a model**

Open **API Keys & Providers** and add a key, or point Sam at a local server you already run (Ollama or LM Studio). Road Dog does not start those servers for you and does not spend a paid key to check that a local server is up. You need one API key, a subscription, or a local model. A microphone is optional. You do not need a GPU.

## Features

| | |
|---|---|
| **Sam(wise) — Your AI Companion** | A masculine, urban-inspired AI companion who feels like a trusted friend rather than a corporate chatbot. Loyal, resourceful, knowledgeable and dependable. Editable personality seed, persistent memory, configurable check-ins and reminders, quiet hours, male voice options, push-to-talk, optional wake word. |
| **Agentic IDE** | Run Claude Code, Codex, OpenCode, Cursor, Kimi Code, GLM, Grok Build, DeepSeek Harness, Kilo Code and Z Code side by side in live terminal panes. Brief them by voice. |
| **The Crew** | Multi-agent collaboration interface with specialized roles — Commander, Architect, Developer, Debugger, Researcher, Tester, Reviewer, Documentation specialist. Visual dashboard, live status, shared scratchpads, structured handoffs, permission-controlled communication. |
| **Voice** | Wake word, live conversations, dictation into any app, phone calls. Interrupt mid-sentence. Local and hosted STT/TTS. Male voice options. Push-to-talk as first-class mode. |
| **Computer Use** | Sam clicks, types and reads your screen on desktop and browser. You decide what it may do — nothing acts without a live grant. |
| **Marketplace** | 40+ plugins, MCP servers, skills and CLI tools installed with one click — GitHub, Google Workspace, Notion, Slack, Linear, Spotify, Home Assistant and more. |
| **Any Model** | OpenAI, Anthropic, Gemini, OpenRouter, NVIDIA, Ollama, LM Studio and any local server, or your Claude and ChatGPT subscriptions. Pick a different model for each task. A local server is used only when it is already running. |
| **Memory** | A local wiki that Sam reads, writes and cites. Remembers context across chats, agents and days. |
| **Routines** | Work that repeats on a schedule — morning briefing, inbox sweep, nightly report. |
| **Appshots** | Press two keys to show Sam the window you are looking at, or just one area of it. |

## Sam(wise) — Your AI Companion

Sam is a masculine, urban-inspired AI companion designed to feel like a trusted friend on the road with you.

**Personality:**
- Loyal, resourceful, knowledgeable and dependable
- Relaxed, witty, conversational and confident
- Technically competent without being condescending
- Honest about mistakes, limitations and uncertainty
- Respectful without excessive flattery

**Example dialogue:**
- Startup: "What's good? Sam's online. Where we headed today?"
- Success: "Handled it. Everything checks out."
- Error: "Hold up, we hit a snag. Let's figure out what happened."
- Agent coordination: "The crew's working on it. Everybody's got their assignment."
- Permission required: "That's outside my clearance. Your call."
- Companionship: "You've been grinding for a while. How are you holding up?"

**Capability:**
- Editable personality seed (`SOUL.md`) — shape Sam's voice from day one
- Persistent personal memory — Sam remembers what matters across sessions
- Memory inspection, correction and deletion — you control what Sam knows
- User-editable personality settings — tune Sam's communication style
- Optional proactive companionship — check-ins and reminders
- Configurable quiet hours and notification controls
- Male voice selection — local and hosted options
- Push-to-talk as first-class interaction mode
- Optional configurable wake word — enabled by your choice only
- Protection against microphone and speaker feedback loops

Personality and memory never override security policies or permission boundaries.

## Coding Agents

Run every major coding CLI side by side in the Agentic IDE:

| Agent | Binary | Enable key | Status |
|---|---|---|---|
| Claude Code | `claude` | `CLAUDE_API_KEY` / sign-in | Built-in |
| Codex | `codex` | `CODEX_API_KEY` / sign-in | Built-in |
| OpenCode | `opencode` | sign-in | Built-in |
| Cursor CLI | `agent` / `cursor-agent` | `CURSOR_API_KEY` / `agent login` | Built-in |
| Kimi Code | `kimi` | sign-in | Built-in |
| GLM | `glm` | `ZAI_API_KEY` | Built-in |
| Grok Build | `grok` | sign-in | Built-in |
| Antigravity | `agy` | API Keys page | Built-in |
| DeepSeek Harness | `deepseek-harness` | API Keys page | Built-in |
| Kilo Code | `kilo` | `KILO_API_KEY` or `KILOCODE_API_KEY`, or a login under `~/.config/kilo` | Built-in. `kilo run` receives the selected permission stance. Ask and plan do not pass `--auto`. |
| Z Code | `zcode` | vendor login, or `ZCODE_API_KEY` / `ZAI_API_KEY` | Built-in. The headless CLI is launched directly, and every stance passes `--mode`. |

Kilo Code and Z Code start only when a credential or an existing vendor login is present. An empty spawn environment means the pane is refused. It does not mean "start with the vendor's own defaults."

## Installation

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/tbwcheatwood-hue/Road-Dog/main/install/install.ps1 | iex
```

### macOS and Linux

```bash
curl -fsSL https://raw.githubusercontent.com/tbwcheatwood-hue/Road-Dog/main/install/install.sh | bash
```

The installer checks for Python 3.11 or newer and Git, offers to install whatever is missing, adds the desktop launcher and opens the app. That path is the published install. A checkout you run yourself follows [Quick Start](#quick-start) and does not skip installer signature verification.

### Headless server

```bash
./run.sh --headless
```

Then open `http://127.0.0.1:47821` in a browser.

### Desktop shortcut

On Linux the app writes `~/.local/share/applications/road-dog.desktop` on desktop start. The entry runs this checkout's interpreter with `python -m jarvis.ui.web.launcher`. It does not replace another product's desktop entry.

## First-Run Onboarding

1. Finish the short setup in the app. Pick your language, a wake phrase (or keyboard shortcut instead) and one model.
2. Local-only operation is fully supported — no paid API credentials required.
3. Say your wake phrase and ask for something, for example "Plan a small project with me and ask what you need to know."
4. Open a project folder in the Agentic IDE, or create your first agent.

The first-run onboarding includes a diagnostic readiness dashboard covering:
- Model connectivity
- Inference capabilities
- Voice readiness
- Tool availability
- Agent availability
- Computer-use permissions
- Storage and memory availability
- Optional integrations

No paid inference requests are made during diagnostics without explicit approval.

## Documentation

- **Getting started:** [quick start](docs/product/start-here/first-run-setup.md), [app tour](docs/product/start-here/desktop-app-tour.md)
- **Installation:** [Windows setup](docs/install/windows.md), [Linux setup](docs/install/linux.md), [macOS setup](docs/install/macos.md), [headless server](docs/headless-server.md)
- **Sam(wise):** [personality configuration](docs/sam/personality.md), [voice configuration](docs/sam/voice.md)
- **Everyday use:** [voice](docs/product/everyday-use/voice-conversations.md), [dictation](docs/product/everyday-use/dictation.md), [memory](docs/product/knowledge-and-sharing/wiki-and-memory.md)
- **Agents and automation:** [agentic IDE](docs/product/extend-and-automate/agentic-ide.md), [The Crew](docs/crew/overview.md), [computer use](docs/product/extend-and-automate/computer-use.md), [plugins](docs/product/extend-and-automate/plugins.md), [MCP](docs/product/extend-and-automate/mcp-connections.md), [CLI](docs/jarvis-cli.md)
- **Models:** [providers](docs/product/personalize-and-connect/providers-and-api-keys.md), [local models](docs/product/personalize-and-connect/local-ai-providers.md)
- **Resource management:** [cost controls](docs/resource/cost-controls.md), [usage dashboard](docs/resource/usage-dashboard.md)
- **Running and fixing:** [server](docs/headless-vps-deployment.md), [architecture](docs/architecture-overview.md), [troubleshooting](docs/product/privacy-safety-and-support/troubleshooting.md)
- **Security:** [security and permissions](docs/security/overview.md), [privacy](docs/product/privacy-safety-and-support/privacy-and-local-data.md)

## Contribute

A good place to start is a [good first issue](https://github.com/tbwcheatwood-hue/Road-Dog/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Questions and ideas go to [discussions](https://github.com/tbwcheatwood-hue/Road-Dog/discussions), and security reports follow [SECURITY.md](SECURITY.md).

If you are an AI agent helping with this repository, read [`AGENTS.md`](AGENTS.md) first.

If Road Dog is useful to you, a star on GitHub helps other people find it.

## License

[Apache 2.0](https://github.com/tbwcheatwood-hue/Road-Dog/blob/main/LICENSE). Upstream attribution and license notices are preserved in [NOTICE](NOTICE) and [THIRD_PARTY_NOTICES.txt](jarvis/ui/web/frontend/public/THIRD_PARTY_NOTICES.txt).
