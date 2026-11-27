"""Live installation test for the agent CLIs (Claude / Codex / Antigravity).

Backs the "Test" button on the three agent connection cards: an on-demand,
cache-busting probe that answers *is this CLI REALLY installed, where, which
version, and is it logged in?* — with the searched PATH directories included,
so a miss is diagnosable instead of a bare "not installed" (the recurring
macOS symptom: the CLI is installed for the user's shell, but the GUI-launched
process searches a minimal PATH and cannot see it).

Design:

* Re-runs :func:`jarvis.core.path_augment.ensure_cli_paths` first, so a CLI
  installed *after* app start (winget/npm just finished) becomes visible
  without a restart.
* Clears the per-process ``--version`` caches (Claude/Codex) so the result is
  a genuine spawn of the binary — proving it is executable, not just present.
* Never raises to the caller: every failure degrades to an honest
  ``ok=False`` result with a message.

All functions are synchronous/blocking (subprocess probes with tight
timeouts); routes must call them via ``asyncio.to_thread``.
"""
from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any, Literal

from jarvis.core.path_augment import ensure_cli_paths
from jarvis.core.process_utils import NO_WINDOW_CREATIONFLAGS

_VERSION_TIMEOUT_S = 8.0

AgentCliName = Literal["claude", "codex", "antigravity", "grok-build", "kilo-code", "z-code"]


@dataclass(frozen=True)
class AgentCliTestResult:
    """Outcome of one live CLI test — display-safe, no secret ever included."""

    cli: str
    ok: bool  # binary found AND a live version spawn answered
    installed: bool
    binary_path: str | None
    version: str | None
    connected: bool
    auth_mode: str
    account: str | None
    message: str
    searched_path: list[str] = field(default_factory=list)
    duration_ms: int = 0
    cli_kind: str | None = None  # antigravity only: "agy" | "gemini"

    def to_dict(self) -> dict[str, Any]:
        return {
            "cli": self.cli,
            "ok": self.ok,
            "installed": self.installed,
            "binary_path": self.binary_path,
            "version": self.version,
            "connected": self.connected,
            "auth_mode": self.auth_mode,
            "account": self.account,
            "message": self.message,
            "searched_path": self.searched_path,
            "duration_ms": self.duration_ms,
            "cli_kind": self.cli_kind,
        }


def _searched_path_dirs() -> list[str]:
    return [p for p in os.environ.get("PATH", "").split(os.pathsep) if p]


def _live_version(argv: list[str]) -> str | None:
    """Spawn ``<cli> --version`` and return the trimmed output, ``None`` on failure."""
    try:
        proc = subprocess.run(
            [*argv, "--version"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            text=True,
            timeout=_VERSION_TIMEOUT_S,
            creationflags=NO_WINDOW_CREATIONFLAGS,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    out = (proc.stdout or proc.stderr or "").strip()
    return out or None


def _not_installed(cli: str, hint: str, t0: float) -> AgentCliTestResult:
    return AgentCliTestResult(
        cli=cli,
        ok=False,
        installed=False,
        binary_path=None,
        version=None,
        connected=False,
        auth_mode="unknown",
        account=None,
        message=f"Binary not found on the app's PATH. {hint}",
        searched_path=_searched_path_dirs(),
        duration_ms=int((time.monotonic() - t0) * 1000),
    )


def test_claude() -> AgentCliTestResult:
    from jarvis import claude_auth

    t0 = time.monotonic()
    ensure_cli_paths()
    claude_auth.clear_version_cache()
    status = claude_auth.ClaudeAuthService().status()
    if not status.installed:
        return _not_installed(
            "claude", claude_auth.claude_install_hint(), t0
        )
    # status() already paid a fresh (cache-cleared) --version spawn; a None
    # version therefore means the binary exists but did not answer.
    ok = status.version is not None
    message = status.message if ok else (
        f"Found at {status.binary_path}, but 'claude --version' did not answer "
        "— the install looks broken."
    )
    return AgentCliTestResult(
        cli="claude",
        ok=ok,
        installed=True,
        binary_path=status.binary_path,
        version=status.version,
        connected=status.connected,
        auth_mode=status.mode,
        account=status.user_email or status.account_label,
        message=message,
        searched_path=_searched_path_dirs(),
        duration_ms=int((time.monotonic() - t0) * 1000),
    )


def test_codex(binary_path: str | None = None) -> AgentCliTestResult:
    from jarvis import codex_auth

    t0 = time.monotonic()
    ensure_cli_paths()
    codex_auth.clear_version_cache()
    status = codex_auth.CodexAuthService(binary_path).status()
    if not status.installed:
        return _not_installed("codex", "Install with: npm i -g @openai/codex", t0)
    ok = status.version is not None
    message = status.message if ok else (
        f"Found at {status.binary_path}, but 'codex --version' did not answer "
        "— the install looks broken."
    )
    return AgentCliTestResult(
        cli="codex",
        ok=ok,
        installed=True,
        binary_path=status.binary_path,
        version=status.version,
        connected=status.connected,
        auth_mode=status.mode,
        account=status.user_email,
        message=message,
        searched_path=_searched_path_dirs(),
        duration_ms=int((time.monotonic() - t0) * 1000),
    )


def test_antigravity() -> AgentCliTestResult:
    from jarvis.google_cli.auth_service import (
        GoogleCliAuthService,
        antigravity_install_hint,
    )
    from jarvis.google_cli.resolver import resolve_google_cli

    t0 = time.monotonic()
    ensure_cli_paths()
    cli = resolve_google_cli()
    if cli is None:
        return _not_installed(
            "antigravity",
            antigravity_install_hint(),
            t0,
        )
    # The resolver never runs the binary — do it here so "installed" is proven
    # executable, and so the card can show which CLI actually answered.
    version = _live_version(list(cli.argv_prefix))
    status = GoogleCliAuthService().status()
    kind_label = "Antigravity (agy)" if cli.kind == "agy" else "the Gemini CLI"
    if version is None:
        message = (
            f"Found {kind_label} at {cli.argv_prefix[0]}, but '--version' did "
            "not answer — the install looks broken."
        )
    else:
        message = f"{kind_label.capitalize()} answered. {status.message}"
    return AgentCliTestResult(
        cli="antigravity",
        ok=version is not None,
        installed=True,
        binary_path=cli.argv_prefix[0] if cli.argv_prefix else None,
        version=version,
        connected=status.connected,
        auth_mode=status.mode,
        account=status.user_email,
        message=message,
        searched_path=_searched_path_dirs(),
        duration_ms=int((time.monotonic() - t0) * 1000),
        cli_kind=cli.kind,
    )


def test_grok_build() -> AgentCliTestResult:
    from jarvis.grok_build_auth import GrokBuildAuthService, grok_build_install_hint

    t0 = time.monotonic()
    ensure_cli_paths()
    from jarvis import grok_build_auth

    grok_build_auth.clear_version_cache()
    status = GrokBuildAuthService().status()
    if not status.installed:
        return _not_installed("grok-build", grok_build_install_hint(), t0)
    ok = status.version is not None
    message = status.message if ok else (
        f"Found at {status.binary_path}, but 'grok --version' did not answer "
        "— the install looks broken."
    )
    return AgentCliTestResult(
        cli="grok-build",
        ok=ok,
        installed=True,
        binary_path=status.binary_path,
        version=status.version,
        connected=status.connected,
        auth_mode=status.mode,
        account=status.user_email,
        message=message,
        searched_path=_searched_path_dirs(),
        duration_ms=int((time.monotonic() - t0) * 1000),
    )


def _credential_state(factory: Any) -> tuple[bool, str, str]:
    """``(configured, auth_mode, sentence)`` from a spawn-env factory.

    A stored key or a vendor file means configured. It does not mean the
    provider accepted the credential.
    """
    try:
        env = factory()
    except Exception as exc:  # noqa: BLE001 — the probe reports the failure
        return False, "unavailable", f"Credential check failed ({type(exc).__name__})."
    if env is None:
        return False, "unconfigured", "No API key and no vendor credential file."
    if env:
        return True, "configured", "A credential is stored for this CLI. It was not sent to the vendor."
    return True, "vendor-config", "The CLI's own config is present. It was not opened and no request was sent."


def test_kilo_code() -> AgentCliTestResult:
    """Probe the Kilo Code CLI and whether it is configured.

    The binary is ``kilo``. Configuration is a Road Dog key or Kilo's own
    config directory. Neither is treated as a successful authentication.
    """
    from jarvis.agent_chat.runner_cli import kilo_argv_prefix
    from jarvis.workspace.agents import kilo_code_spawn_env

    t0 = time.monotonic()
    ensure_cli_paths()
    try:
        argv = kilo_argv_prefix()
    except Exception:  # noqa: BLE001 — missing CLI is the not-installed result
        argv = []
    if not argv:
        return _not_installed(
            "kilo-code",
            "Install Kilo Code with https://kilo.ai/cli/install or "
            "`npm install -g @kilocode/cli`, then make sure `kilo` is on PATH.",
            t0,
        )
    binary = argv[0]
    version = _live_version([*argv, "--version"])
    configured, auth_mode, auth_detail = _credential_state(kilo_code_spawn_env)
    if version is None:
        return AgentCliTestResult(
            cli="kilo-code",
            ok=False,
            installed=True,
            binary_path=binary,
            version=None,
            connected=False,
            auth_mode=auth_mode,
            account=None,
            message=f"Found Kilo Code at {binary}, but '--version' did not answer. {auth_detail}",
            searched_path=_searched_path_dirs(),
            duration_ms=int((time.monotonic() - t0) * 1000),
        )
    return AgentCliTestResult(
        cli="kilo-code",
        ok=True,
        installed=True,
        binary_path=binary,
        version=version,
        connected=configured,
        auth_mode=auth_mode,
        account=None,
        message=f"Kilo Code {version} at {binary}. {auth_detail}",
        searched_path=_searched_path_dirs(),
        duration_ms=int((time.monotonic() - t0) * 1000),
    )


def test_z_code() -> AgentCliTestResult:
    """Probe the Z Code headless CLI, not the desktop app of the same name.

    ``connected`` means a vendor config file or a stored key exists. The probe
    does not log in and does not send a prompt.
    """
    from jarvis.workspace.agents import z_code_spawn_env
    from jarvis.workspace.zcode_cli import resolve_zcode_argv

    t0 = time.monotonic()
    ensure_cli_paths()
    argv = resolve_zcode_argv()
    if not argv:
        return _not_installed(
            "z-code",
            "The Z Code desktop app is not the headless CLI. Install the CLI "
            "from the Z Code app or https://github.com/zai-org/ZCode.",
            t0,
        )
    binary = argv[-1]
    version = _live_version([*argv, "--version"])
    configured, auth_mode, auth_detail = _credential_state(z_code_spawn_env)
    if version is None:
        return AgentCliTestResult(
            cli="z-code",
            ok=False,
            installed=True,
            binary_path=binary,
            version=None,
            connected=False,
            auth_mode=auth_mode,
            account=None,
            message=f"Found the Z Code CLI at {binary}, but '--version' did not answer. {auth_detail}",
            searched_path=_searched_path_dirs(),
            duration_ms=int((time.monotonic() - t0) * 1000),
        )
    return AgentCliTestResult(
        cli="z-code",
        ok=True,
        installed=True,
        binary_path=binary,
        version=version,
        connected=configured,
        auth_mode=auth_mode,
        account=None,
        message=f"Z Code CLI {version} at {binary}. {auth_detail}",
        searched_path=_searched_path_dirs(),
        duration_ms=int((time.monotonic() - t0) * 1000),
    )


__all__ = [
    "AgentCliName",
    "AgentCliTestResult",
    "test_antigravity",
    "test_claude",
    "test_codex",
    "test_grok_build",
    "test_kilo_code",
    "test_z_code",
]
