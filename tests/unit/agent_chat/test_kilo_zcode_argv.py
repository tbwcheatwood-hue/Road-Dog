"""Argument construction for Kilo Code and Z Code. No vendor process is started."""

from __future__ import annotations

from pathlib import Path

import pytest

from jarvis.agent_chat import runner_cli as rc
from jarvis.agent_chat.permissions import normalize_permission
from jarvis.workspace import zcode_cli


@pytest.fixture
def prefixes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rc, "kilo_argv_prefix", lambda: ["kilo"])
    monkeypatch.setattr(rc, "z_argv_prefix", lambda: ["/usr/bin/node", "/opt/ZCode/zcode.cjs"])
    monkeypatch.setattr(rc, "_account_env", lambda platform: {})
    monkeypatch.setattr(rc, "_registry_env", lambda agent, base: dict(base))


def test_kilo_ask_does_not_pass_auto(prefixes: None) -> None:
    plan = rc.plan_kilo(
        prompt="look at this",
        cwd=Path("/work"),
        model="openrouter/model",
        effort="high",
        permission_mode="ask",
        resume="ses_1",
    )
    assert plan.argv[:4] == ["kilo", "run", "--format", "json"]
    assert "--auto" not in plan.argv
    assert plan.argv[plan.argv.index("--model") + 1] == "openrouter/model"
    assert plan.argv[plan.argv.index("--variant") + 1] == "high"
    assert plan.argv[plan.argv.index("--dir") + 1] == "/work"
    assert plan.argv[plan.argv.index("--session") + 1] == "ses_1"
    assert plan.shape == "kilo"


def test_kilo_auto_is_explicit(prefixes: None) -> None:
    plan = rc.plan_kilo(
        prompt="do it",
        cwd=Path("/work"),
        model="",
        effort="",
        permission_mode="auto",
        resume=None,
    )
    assert "--auto" in plan.argv
    assert "--model" not in plan.argv
    assert "--variant" not in plan.argv


def test_kilo_plan_stays_restricted(prefixes: None) -> None:
    plan = rc.plan_kilo(
        prompt="plan it",
        cwd=Path("/work"),
        model="",
        effort="",
        permission_mode="plan",
        resume=None,
    )
    assert "--auto" not in plan.argv
    assert "PLAN MODE" in plan.argv[-1]


def test_kilo_rejects_an_unknown_variant(prefixes: None) -> None:
    with pytest.raises(rc.CliUnavailable):
        rc.plan_kilo(
            prompt="x",
            cwd=Path("/work"),
            model="",
            effort="medium",
            permission_mode="ask",
            resume=None,
        )


def test_zcode_always_passes_mode_and_never_defaults_to_yolo(prefixes: None) -> None:
    plan = rc.plan_z(
        prompt="build it",
        cwd=Path("/work"),
        model="ignored",
        effort="high",
        permission_mode="ask",
        resume=None,
    )
    assert plan.argv[0:2] == ["/usr/bin/node", "/opt/ZCode/zcode.cjs"]
    assert plan.argv[plan.argv.index("--mode") + 1] == "build"
    assert "yolo" not in plan.argv
    assert "--model" not in plan.argv
    assert plan.shape == "zcode"

    yolo = rc.plan_z(
        prompt="go",
        cwd=Path("/work"),
        model="",
        effort="",
        permission_mode="bypassPermissions",
        resume="sess_9",
    )
    assert yolo.argv[yolo.argv.index("--mode") + 1] == "yolo"
    assert yolo.argv[yolo.argv.index("--resume") + 1] == "sess_9"


def test_permission_fold_does_not_widen_kilo_or_zcode() -> None:
    assert normalize_permission("kilo-code-cli", "accept-edits") == "ask"
    assert normalize_permission("kilo-code-cli", "") == "ask"
    assert normalize_permission("z-code-cli", "accept-edits") == "edit"
    assert normalize_permission("z-code-cli", "") == "build"


def test_zcode_resolver_prefers_the_cli_over_the_electron_app(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    app = tmp_path / "ZCode"
    app.mkdir()
    (app / "chrome-sandbox").write_text("suid", encoding="utf-8")
    (app / "zcode").write_text("gui", encoding="utf-8")
    script = app / "resources" / "glm" / "zcode.cjs"
    script.parent.mkdir(parents=True)
    script.write_text("// cli", encoding="utf-8")
    node = tmp_path / "node"
    node.write_text("node", encoding="utf-8")
    monkeypatch.setattr(zcode_cli, "_BUNDLE_CJS", (script,))
    monkeypatch.setattr(zcode_cli, "_node", lambda: str(node))
    monkeypatch.setattr(zcode_cli.shutil, "which", lambda name: str(app / "zcode"))
    assert zcode_cli.resolve_zcode_argv() == [str(node), str(script)]


def test_zcode_resolver_refuses_an_electron_binary_alone(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    app = tmp_path / "ZCode"
    app.mkdir()
    (app / "LICENSE.electron.txt").write_text("electron", encoding="utf-8")
    binary = app / "zcode"
    binary.write_text("gui", encoding="utf-8")
    monkeypatch.setattr(zcode_cli, "_BUNDLE_CJS", (tmp_path / "missing.cjs",))
    monkeypatch.setattr(zcode_cli.Path, "home", classmethod(lambda cls: tmp_path / "empty-home"))
    monkeypatch.setattr(zcode_cli.shutil, "which", lambda name: str(binary))
    assert zcode_cli.resolve_zcode_argv() is None


def test_kilo_json_and_zcode_json_become_chat_events() -> None:
    kilo_state = rc._OpenCodeState(turn_id="t", vendor_session=None)
    events = rc.translate_kilo_line({"sessionID": "ses_2", "response": "done"}, kilo_state)
    assert events and events[0]["kind"] == "assistant_text"
    assert kilo_state.vendor_session == "ses_2"

    z_state = rc._TextState(turn_id="t", vendor_session=None)
    events = rc.translate_zcode_line({"sessionId": "sess_3", "response": "built"}, z_state)
    assert events and events[0]["kind"] == "assistant_text"
    assert z_state.vendor_session == "sess_3"
