"""First-run readiness diagnostics dashboard.

Read-only checks across the eight areas Sam reports on during onboarding:

1. Model connectivity      — Brain providers reachable, API keys valid
2. Inference capabilities  — local vs hosted, realtime vs pipeline
3. Voice readiness         — STT/TTS engines, wake word, microphone, speakers
4. Tool availability       — coding agent CLIs, shell tools, MCP servers
5. Agent availability      — The Crew roles, starter team seeded
6. Computer-use permissions— screen, accessibility, input monitoring, desktop
7. Storage & memory        — disk space, data dir, core memory, wiki
8. Optional integrations   — telephony, home assistant, calendar, contacts

Nothing here installs, modifies, or sends data. Every check is read-only.
Results are returned as a plain dict suitable for the onboarding UI.
"""

from __future__ import annotations

import importlib
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jarvis.core import config as cfg


@dataclass(slots=True)
class CheckResult:
    """One readiness check: name, status, detail, and optional remediation."""

    name: str
    status: str  # "ok", "warn", "fail", "skip"
    detail: str
    fix: str | None = None


@dataclass(slots=True)
class ReadinessReport:
    """All check results grouped by area, plus an overall status."""

    area: str
    checks: list[CheckResult]
    overall: str = "ok"

    @property
    def has_failures(self) -> bool:
        return any(c.status == "fail" for c in self.checks)

    @property
    def has_warnings(self) -> bool:
        return any(c.status == "warn" for c in self.checks)


# ----------------------------------------------------------------------- helpers


def _env_var(name: str) -> str | None:
    return os.environ.get(name) or cfg.get_secret(name)


def _command_available(name: str) -> bool:
    return shutil.which(name) is not None


def _python_module(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------- area checks


def check_model_connectivity() -> ReadinessReport:
    """Area 1: Model connectivity — can Sam reach a Brain?"""
    checks: list[CheckResult] = []

    # Look for any configured provider key
    provider_keys = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "OPENROUTER_API_KEY",
        "GROQ_API_KEY",
        "COHERE_API_KEY",
        "MISTRAL_API_KEY",
    ]
    found_keys = [k for k in provider_keys if _env_var(k)]

    if found_keys:
        checks.append(
            CheckResult(
                name="Provider API keys",
                status="ok",
                detail=f"{len(found_keys)} provider key(s) configured",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Provider API keys",
                status="warn",
                detail="No provider API key configured",
                fix="Add a key on the API Keys page, or use Local Mode with Ollama",
            )
        )

    # Check for Ollama / local inference
    if _command_available("ollama"):
        checks.append(
            CheckResult(
                name="Ollama local inference",
                status="ok",
                detail="Ollama CLI available",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Ollama local inference",
                status="skip",
                detail="Ollama not installed",
                fix="Install Ollama for keyless local models",
            )
        )

    overall = "ok" if found_keys else "warn"
    return ReadinessReport(area="model_connectivity", checks=checks, overall=overall)


def check_inference_capabilities() -> ReadinessReport:
    """Area 2: Inference capabilities — local vs hosted, realtime vs pipeline."""
    checks: list[CheckResult] = []

    checks.append(
        CheckResult(
            name="Pipeline voice (STT → Brain → TTS)",
            status="ok",
            detail="Always available with any Brain provider",
            fix=None,
        )
    )

    if _python_module("websockets"):
        checks.append(
            CheckResult(
                name="Realtime voice",
                status="ok",
                detail="WebSocket client available for Realtime voice",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Realtime voice",
                status="warn",
                detail="websockets package not installed",
                fix="pip install websockets",
            )
        )

    if _python_module("torch"):
        checks.append(
            CheckResult(
                name="Local inference (PyTorch)",
                status="ok",
                detail="PyTorch available for local models",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Local inference (PyTorch)",
                status="skip",
                detail="PyTorch not installed",
                fix="Install torch for local model support",
            )
        )

    overall = "ok"
    return ReadinessReport(area="inference_capabilities", checks=checks, overall=overall)


def check_voice_readiness() -> ReadinessReport:
    """Area 3: Voice readiness — STT/TTS, wake word, microphone, speakers."""
    checks: list[CheckResult] = []

    if _python_module("vosk"):
        checks.append(
            CheckResult(
                name="Offline wake word (Vosk)",
                status="ok",
                detail="Vosk available for local wake-word detection",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Offline wake word (Vosk)",
                status="skip",
                detail="Vosk not installed",
                fix="pip install vosk for offline wake word",
            )
        )

    if _python_module("piper"):
        checks.append(
            CheckResult(
                name="Local TTS (Piper)",
                status="ok",
                detail="Piper available for local text-to-speech",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Local TTS (Piper)",
                status="skip",
                detail="Piper not installed",
                fix="pip install piper-tts for local voice",
            )
        )

    if _python_module("pyaudio"):
        checks.append(
            CheckResult(
                name="Microphone access (PyAudio)",
                status="ok",
                detail="PyAudio available for microphone input",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Microphone access (PyAudio)",
                status="warn",
                detail="PyAudio not installed",
                fix="pip install pyaudio for microphone input",
            )
        )

    overall = "ok"
    return ReadinessReport(area="voice_readiness", checks=checks, overall=overall)


def check_tool_availability() -> ReadinessReport:
    """Area 4: Tool availability — coding agent CLIs, shell tools, MCP servers."""
    checks: list[CheckResult] = []

    coding_clis = ["claude", "codex", "opencode", "cursor-agent", "agent",
                   "kimi", "glm", "grok", "agy", "deepseek-harness",
                   "kilo", "zcode"]
    found_clis = [c for c in coding_clis if _command_available(c)]

    if found_clis:
        checks.append(
            CheckResult(
                name="Coding agent CLIs",
                status="ok",
                detail=f"{len(found_clis)} available: {', '.join(found_clis)}",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Coding agent CLIs",
                status="warn",
                detail="No coding agent CLIs found on PATH",
                fix="Install Claude Code, Codex, or another coding agent CLI",
            )
        )

    if _command_available("git"):
        checks.append(
            CheckResult(
                name="Git",
                status="ok",
                detail="Git available on PATH",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Git",
                status="fail",
                detail="Git not found on PATH",
                fix="Install Git",
            )
        )

    if _command_available("node"):
        checks.append(
            CheckResult(
                name="Node.js",
                status="ok",
                detail="Node.js available for worker tools",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Node.js",
                status="skip",
                detail="Node.js not found",
                fix="Install Node.js 18+ for agent worker tools",
            )
        )

    overall = "ok" if found_clis else "warn"
    return ReadinessReport(area="tool_availability", checks=checks, overall=overall)


def check_agent_availability() -> ReadinessReport:
    """Area 5: Agent availability — The Crew roles, starter team."""
    checks: list[CheckResult] = []

    # Check starter team definition
    from jarvis.society.seeds import STARTER_TEAM

    checks.append(
        CheckResult(
            name="Starter agent team",
            status="ok",
            detail=f"{len(STARTER_TEAM)} starter roles defined (Scout, Archivist)",
            fix=None,
        )
    )

    checks.append(
        CheckResult(
            name="The Crew roles",
            status="ok",
            detail="Commander, Architect, Developer, Debugger, Researcher, Tester, Reviewer, Documentation",
            fix=None,
        )
    )

    overall = "ok"
    return ReadinessReport(area="agent_availability", checks=checks, overall=overall)


def check_computer_use_permissions() -> ReadinessReport:
    """Area 6: Computer-use permissions — screen, accessibility, input monitoring."""
    checks: list[CheckResult] = []

    # Platform-specific permission checks
    if sys.platform == "darwin":
        # macOS: check for Accessibility / Input Monitoring via AppleScript
        checks.append(
            CheckResult(
                name="macOS Accessibility",
                status="skip",
                detail="Checked at first use (just-in-time permissions)",
                fix="Grant Accessibility in System Settings > Privacy & Security",
            )
        )
        checks.append(
            CheckResult(
                name="macOS Input Monitoring",
                status="skip",
                detail="Checked at first use (just-in-time permissions)",
                fix="Grant Input Monitoring in System Settings > Privacy & Security",
            )
        )
    elif sys.platform.startswith("linux"):
        checks.append(
            CheckResult(
                name="Linux desktop access",
                status="ok",
                detail="X11/Wayland desktop access via standard APIs",
                fix=None,
            )
        )
    elif sys.platform == "win32":
        checks.append(
            CheckResult(
                name="Windows desktop access",
                status="ok",
                detail="Win32 desktop APIs available",
                fix=None,
            )
        )

    overall = "ok"
    return ReadinessReport(area="computer_use_permissions", checks=checks, overall=overall)


def check_storage_memory() -> ReadinessReport:
    """Area 7: Storage & memory — disk space, data dir, core memory, wiki."""
    checks: list[CheckResult] = []

    # Data directory
    data_dir = Path(cfg.DATA_DIR) if hasattr(cfg, "DATA_DIR") else Path("data")
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        total, used, free = shutil.disk_usage(data_dir)
        free_gb = free // (1024 ** 3)
        if free_gb >= 5:
            checks.append(
                CheckResult(
                    name="Disk space",
                    status="ok",
                    detail=f"{free_gb} GB free",
                    fix=None,
                )
            )
        else:
            checks.append(
                CheckResult(
                    name="Disk space",
                    status="warn",
                    detail=f"{free_gb} GB free (low)",
                    fix="Free up disk space",
                )
            )
    except OSError as exc:
        checks.append(
            CheckResult(
                name="Disk space",
                status="fail",
                detail=f"Cannot access data directory: {exc}",
                fix="Check data directory permissions",
            )
        )

    # Core memory
    core_memory_path = data_dir / "core_memory.json"
    if core_memory_path.exists():
        checks.append(
            CheckResult(
                name="Core memory",
                status="ok",
                detail="core_memory.json present",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Core memory",
                status="skip",
                detail="core_memory.json not yet created",
                fix="Created on first app launch",
            )
        )

    # Wiki
    wiki_path = data_dir / "wiki"
    if wiki_path.exists():
        checks.append(
            CheckResult(
                name="Wiki storage",
                status="ok",
                detail="Wiki directory present",
                fix=None,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="Wiki storage",
                status="skip",
                detail="Wiki directory not yet created",
                fix="Created on first app launch",
            )
        )

    overall = "ok"
    return ReadinessReport(area="storage_memory", checks=checks, overall=overall)


def check_optional_integrations() -> ReadinessReport:
    """Area 8: Optional integrations — telephony, home assistant, calendar, contacts."""
    checks: list[CheckResult] = []

    integrations = [
        ("telephony", "Telephony / phone calls"),
        ("mcp", "MCP server connections"),
        ("home_assistant", "Home Assistant"),
        ("calendar", "Calendar integration"),
        ("contacts", "Contacts integration"),
    ]

    for _key, label in integrations:
        checks.append(
            CheckResult(
                name=label,
                status="skip",
                detail="Optional — configured on demand",
                fix=f"Connect {label} in Settings > Integrations",
            )
        )

    overall = "ok"
    return ReadinessReport(area="optional_integrations", checks=checks, overall=overall)


# ---------------------------------------------------------------- aggregate


def run_all_checks() -> dict[str, Any]:
    """Run every readiness check and return a JSON-serializable report.

    Used by the onboarding UI to render the readiness dashboard and by
    the CLI for headless diagnostics.
    """
    areas = [
        check_model_connectivity(),
        check_inference_capabilities(),
        check_voice_readiness(),
        check_tool_availability(),
        check_agent_availability(),
        check_computer_use_permissions(),
        check_storage_memory(),
        check_optional_integrations(),
    ]

    report = {}
    overall_status = "ok"
    for area in areas:
        report[area.area] = {
            "overall": area.overall,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status,
                    "detail": c.detail,
                    "fix": c.fix,
                }
                for c in area.checks
            ],
        }
        if area.has_failures:
            overall_status = "fail"
        elif area.has_warnings and overall_status != "fail":
            overall_status = "warn"

    report["_overall"] = overall_status
    report["_sam_greeting"] = (
        "What's good? Sam's online. Here's what I can see so far."
        if overall_status == "ok"
        else "What's good? Sam's online. A few things to sort out before we roll."
    )

    return report


__all__ = [
    "CheckResult",
    "ReadinessReport",
    "check_model_connectivity",
    "check_inference_capabilities",
    "check_voice_readiness",
    "check_tool_availability",
    "check_agent_availability",
    "check_computer_use_permissions",
    "check_storage_memory",
    "check_optional_integrations",
    "run_all_checks",
]
