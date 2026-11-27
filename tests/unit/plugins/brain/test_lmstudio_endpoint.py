"""LM Studio uses its own endpoint and does not fall through to a paid provider.

The HTTP server is a local fixture. No completion is requested.
"""

from __future__ import annotations

from jarvis.brain import resolver
from jarvis.core.config import BrainConfig, BrainProviderConfig, JarvisConfig
from jarvis.plugins.brain.local_openai import LMSTUDIO_DEFAULT_ROOT, LMStudioBrain
from jarvis.society.browser.llm import llm_spec_for


def test_lmstudio_default_root_is_its_own_port() -> None:
    assert LMSTUDIO_DEFAULT_ROOT == "http://127.0.0.1:1234"
    assert LMStudioBrain.provider_id == "lmstudio"
    assert LMStudioBrain.name == "lmstudio"


def test_lmstudio_primary_does_not_append_a_paid_provider(monkeypatch) -> None:
    import jarvis.core.config as cfg_mod

    resolver._reset_for_tests()
    monkeypatch.setattr(
        cfg_mod,
        "get_provider_secret",
        lambda pid: "sk-test" if pid == "gemini" else None,
    )
    config = JarvisConfig(
        brain=BrainConfig(
            primary="lmstudio",
            local_fallback="claude-api",
            providers={"lmstudio": BrainProviderConfig(base_url="http://192.168.1.20:1234/v1")},
        )
    )
    providers = [provider for provider, _model in resolver._resolve_chain(config)]
    assert providers == ["lmstudio"]
    assert "gemini" not in providers
    assert "claude-api" not in providers
    resolver._reset_for_tests()


def test_lmstudio_is_not_an_ambient_fallback(monkeypatch) -> None:
    import jarvis.core.config as cfg_mod

    resolver._reset_for_tests()
    monkeypatch.setattr(cfg_mod, "get_provider_secret", lambda pid: "sk-test" if pid == "gemini" else None)
    config = JarvisConfig(brain=BrainConfig(primary="gemini"))
    providers = [provider for provider, _model in resolver._resolve_chain(config)]
    assert "lmstudio" not in providers
    assert providers[-2:] == ["ollama", "local-openai"]
    resolver._reset_for_tests()


def test_browser_llm_uses_the_lmstudio_card(monkeypatch) -> None:
    import jarvis.core.config as cfg_mod

    monkeypatch.setattr(
        cfg_mod,
        "resolve_provider_endpoint",
        lambda provider, vendor_default_base_url=None: type(
            "E", (), {"base_url": "http://10.0.0.8:1234/v1", "credential": ""}
        )(),
    )
    spec = llm_spec_for("lmstudio", "loaded-model")
    assert spec.base_url == "http://10.0.0.8:1234/v1"
    assert spec.model == "loaded-model"
    assert spec.api_key is None
