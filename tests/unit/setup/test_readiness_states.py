"""Readiness states come from probes, not from a binary or a stored key."""

from __future__ import annotations

from jarvis.setup.readiness import check_model_connectivity, run_all_checks


def test_a_stored_key_is_configured_not_authenticated(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-sent")
    monkeypatch.setattr(
        "jarvis.setup.readiness._http_get",
        lambda url, timeout=2.0: (None, "", "URLError"),
    )
    report = check_model_connectivity()
    keys = next(check for check in report.checks if check.name == "Provider API keys")
    assert keys.state == "configured"
    assert keys.state != "authenticated"
    assert keys.status != "ok"
    dumped = run_all_checks()
    assert dumped["model_connectivity"]["checks"][0]["state"] == "configured"


def test_installed_ollama_without_a_server_is_not_operational(monkeypatch) -> None:
    monkeypatch.setattr("jarvis.setup.readiness._command_available", lambda name: name == "ollama")
    monkeypatch.setattr(
        "jarvis.setup.readiness._http_get",
        lambda url, timeout=2.0: (None, "", "URLError"),
    )
    monkeypatch.setattr("jarvis.setup.readiness._env_var", lambda name: None)
    report = check_model_connectivity()
    ollama = next(check for check in report.checks if check.name == "Ollama local inference")
    assert ollama.state == "installed"
    assert ollama.status != "ok"


def test_a_discovery_document_is_operational(monkeypatch) -> None:
    monkeypatch.setattr("jarvis.setup.readiness._command_available", lambda name: False)
    monkeypatch.setattr("jarvis.setup.readiness._env_var", lambda name: None)

    def _get(url: str, timeout: float = 2.0):
        if url.endswith("/v1/models"):
            return 200, '{"data":[{"id":"local"}]}', ""
        return None, "", "URLError"

    monkeypatch.setattr("jarvis.setup.readiness._http_get", _get)
    report = check_model_connectivity()
    studio = next(check for check in report.checks if check.name == "LM Studio")
    assert studio.state == "operational"
    assert studio.status == "ok"
