# Road Dog — Installation guide

## One-step (recommended)

| Platform | Command |
|---|---|
| macOS / Linux | `python install/install.sh` |
| Windows (PowerShell) | `powershell -ExecutionPolicy Bypass -File install\install.ps1` |

The bootstrap checks Python 3.11+ and git (offering to install them where the
OS allows), clones/updates into `~/.road-dog`, creates a venv, and hands over
to `install/installer.py` for the guided install: dependency install, desktop
shortcut, launcher, and first-run configuration. `install/install-verify.sh`
(`.ps1`) verifies a release artifact's signatures before you run it.

## Manual install

```bash
pip install -e . --no-deps
pip install -r requirements.txt        # hash-pinned, platform-universal lockfile
cp jarvis.toml.example jarvis.toml     # optional; every default is built in
```

Launch with `roaddog` (desktop app) or `roaddog serve` (headless, http://127.0.0.1:47821). If that port is taken, pass `--port`.
The `jarvis` commands remain aliases.

## What the installer does
- Virtual-environment management inside `~/.road-dog/.venv`.
- Optional dependency groups offered with clear prompts (voice, telephony,
  desktop extras) — a base install boots headless with none of them.
- Desktop shortcut / application launcher (`road-dog.desktop` on Linux,
  `Road Dog.lnk` on Windows, `Road Dog.app` on macOS).
- **Config preservation:** upgrading re-uses the existing `jarvis.toml`,
  keyring credentials and the `Jarvis`/`~/.jarvis` user-data folders.
- **Repair:** re-running the installer detects the existing venv and only
  refreshes what is missing.
- **Clean uninstall:** `install/uninstall.sh` (`.ps1`) removes the install
  dir, shortcuts, autostart entries and — with confirmation — keyring
  credentials under the `personal-jarvis` service name.

## Headless server deployment
1. Any Linux box or `python:3.11`-slim container (no GPU/audio required).
2. `python install/install.sh --headless` or the manual steps above.
3. `roaddog serve` → `http://127.0.0.1:47821` (or `--port` when that port is taken). Remote access is opt-in — see
   the security review for the listener binding rules.
4. `Dockerfile` / `docker-compose.yml` are provided for container hosting.

## First-run onboarding
The desktop app walks through: assistant name + wake word ("Hey Sam" is the
suggested phrase), model connection (key, subscription, or local endpoint —
**local-only operation works without any paid credentials**), voice and
permissions (each requested at first use via the OS dialog). The readiness
dashboard (`GET /api/diagnostics/readiness`, Settings → Diagnostics) shows
what is ready on this machine — without spending tokens.
