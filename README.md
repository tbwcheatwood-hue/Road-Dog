<h1 align="center">Road Dog</h1>

<p align="center">
  <strong>Your AI. Your crew. Your road.</strong><br />
  Every road is better with a Road Dog — a standalone, local-first AI agent app
  for your desktop, with Sam(wise) riding shotgun.
</p>

<p align="center">
  <a href="#license"><img alt="Apache 2.0 fork" src="https://img.shields.io/badge/License-Apache_2.0-F7F7F4?labelColor=0A0A0A" /></a>
</p>

<p align="center">
  <img src="assets/road-dog-architecture.svg" alt="Road Dog architecture" width="100%"/>
</p>

---

Road Dog is a standalone desktop AI agent app. It runs every coding agent side by side, talks with you through a wake word or push-to-talk, keeps a team of agents (the Crew) working while you are away, controls your desktop and browser under your rules, and remembers your world locally. It works with the models you already pay for — hosted, local, or through a subscription — and runs local-only without any paid credentials.

**Sam(wise)** — Sam for short — is the built-in companion: loyal, resourceful, dry-witted, honest about limits. His personality ships as editable data (`jarvis/brain/JARVIS_PERSONA.md` + the SOUL.md seed) and he grows through persistent memory you can inspect, edit, export and delete. Optional check-ins (off by default, quiet hours respected) let him notice when you have been grinding.

Road Dog is a fork of the open-source **Personal Jarvis (Hue)** project — Apache 2.0 — with required attribution in [`NOTICE`](NOTICE) and [`docs/road-dog/UPSTREAM-ATTRIBUTION.md`](docs/road-dog/UPSTREAM-ATTRIBUTION.md). It installs independently (`~/.road-dog`, own desktop entries and app ids) and can import an upstream install's config and memory only when you explicitly ask.

## Quick Start

```bash
git clone <your-road-dog-repo> road-dog && cd road-dog
python install/install.sh        # macOS / Linux bootstrap + guided install
# Windows:  powershell -ExecutionPolicy Bypass -File install\install.ps1
```

or by hand:

```bash
pip install -e . --no-deps
pip install -r requirements.txt
```

**Launch** — `roaddog serve` (headless, http://127.0.0.1:47821) or `roaddog` (desktop). If 47821 is already taken, start with `--port`. `jarvis`/`jarvis serve` remain aliases. The Python environment stays on the machine: `.venv/` is gitignored, and this tree does not pin a virtualenv from another install.

**Connect a model** — exactly one of: an API key, a subscription, or a local server (Ollama, LM Studio, llama.cpp, any OpenAI-compatible endpoint). Add/test/select endpoints in the UI (`/api/local-endpoints`); the onboarding wizard tests them with zero-spend metadata probes.

## What is new in v1.3.0

This tree is Road Dog 1.3.0. The release notes are in [`ROAD_DOG_CHANGELOG.md`](ROAD_DOG_CHANGELOG.md). On top of that release, this branch also does the following:

- **Local chat stays inside the model.** An Ollama chat raises the running context allocation when it is smaller than the model's own window, so a selected local model is not refused for a 4096-token cap.
- **Front-page chat leaves the crew alone.** Society tools and the team card stay off that chat while `ENABLED` in `jarvis/society/chat_gate.py` is `False`. Society chats and spoken turns still have them. Set `ENABLED` to `True` to put them back on the next chat turn.
- **Antigravity 1.5 sign-in is recognized** from its current config directory.
- **The in-app tool server keeps Antigravity connected.** A listener `GET` is answered with 405, which is the signal that there is no event stream to retry. Tool calls continue over the normal connection (`jarvis-hands`).
- **Speech recognition is pinned to English** in `scripts/config-soll.json`. The config drift guard writes that pin back into the live config.

## Earlier, in v1.1.0

See [`docs/road-dog/UPGRADE-REPORT.md`](docs/road-dog/UPGRADE-REPORT.md). Highlights:

- **Independent identity:** Road Dog-owned data root (`~/.road-dog/data`, overridable via `ROAD_DOG_DATA_DIR`), own endpoint registry and config copies — coexists with a Personal Jarvis/Hue install. Explicit, authorized upstream import (`jarvis/migration/upstream_import.py`, `/api/migration/*`): plan-first, never touches credentials, never auto-runs.
- **First-class local endpoints:** add/edit/remove/test/select inference servers in the UI; capability-aware routing (`pick`) over declared/probed capabilities; test = GET metadata only (never launches a server, never downloads a model, never spends).
- **Small-model kit** (`jarvis/brain/small_model.py`): compact role instructions, reasoning/tool separation (never executes from `<think>`), schema-validated structured output with bounded repair, strict single-line tool protocol with allow-listing.
- **Crew handoffs** (`jarvis/missions/handoff.py`): structured sender/receiver/completed/remaining/artifacts/failures/verification/usage payloads; cycle detection; depth bounds; permission elevation blocked (receivers only hold their role's permissions).
- **Enforced budgets** (`jarvis/costs/budgets.py`): per-agent/per-mission token, request and cost caps with escrow semantics — `check_and_reserve` raises BEFORE dispatch; concurrent dispatch cannot race past a cap; measured usage settles estimates.
- **Acceptance mission** (`jarvis/acceptance/mission.py` + `tests/acceptance/`): a full crew build (architect→developer→tester→reviewer→docs→delivery) of a real, verified offline checksum CLI — real pytest execution and CLI launch; model turns are a deterministic simulation, labelled honestly.
- **Sam's memory surface** (`/api/sam/memories`): inspect, search, edit, delete and export your memories; path-traversal-proof; untrusted content stays data.
- **Push-to-talk restored** as first-class: `[trigger] push_to_talk_key` arms the pipeline's hold-to-talk slot, independent of the wake word (audio-hardware verification documented as pending).
- **Onboarding endpoint test**: verify Ollama/LM Studio during the wizard with zero spend.
- Kilo Code / Zed Code remain honestly classified: **experimental/unavailable** (placeholder binaries, spawn-gated; upstream added no verified integration).

## You stay in control

Risk-tiered actions (safe/monitor/ask/block), keys in the OS credential store, zero-spend diagnostics, localhost-default listeners, opt-in cloud/remote. Untrusted content (screens, documents, tool output, plugin responses) is data — prompt injection cannot grant permissions or move budgets. Personality, agent instructions and memories never override security boundaries.

## Docs

[installation](docs/road-dog/INSTALLATION.md) · [local models](docs/road-dog/LOCAL-MODELS.md) · [the Crew](docs/road-dog/CREW-GUIDE.md) · [Sam's personality & memory](docs/road-dog/SAM-PERSONALITY.md) · [upstream migration](docs/road-dog/MIGRATION.md) · [upgrade report](docs/road-dog/UPGRADE-REPORT.md) · [security review](docs/road-dog/SECURITY-REVIEW.md) · [test report](docs/road-dog/TEST-REPORT.md) · [known limitations](docs/road-dog/KNOWN-LIMITATIONS.md)

## License

Apache 2.0, inherited from upstream Personal Jarvis (Hue) (releases ≤1.6.0 MIT). See [`LICENSE`](LICENSE), [`NOTICE`](NOTICE), [`TRADEMARK.md`](TRADEMARK.md).
