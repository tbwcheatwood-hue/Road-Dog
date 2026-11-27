"""Freeze Road Dog's own identity. It does not share Personal Jarvis paths."""

from __future__ import annotations

import importlib
import os

import pytest

import jarvis.core.branding as branding

_CURRENT_IDENTITY = {
    "PRODUCT_NAME": "Road Dog",
    "PRODUCT_COMPACT_NAME": "RoadDog",
    "PRODUCT_SLUG": "road-dog",
    "CONFIG_FILE_NAME": "jarvis.toml",
    "KEYRING_SERVICE_NAME": "road-dog",
    "CONTROL_KEY_PREFIX": "jctl_",
    "SESSION_COOKIE_NAME": "road_dog_session",
    "MANAGED_INSTALL_MARKER": ".road-dog-managed-install",
    "DEFAULT_INSTALL_DIR_NAME": ".road-dog",
    "WINDOWS_USER_DATA_DIR_NAME": "Road Dog",
    "FALLBACK_USER_DATA_DIR_NAME": ".road-dog",
    "DESKTOP_OUTPUT_MIRROR_DIR_NAME": "RoadDog-Output",
    "WINDOWS_MUTEX_NAME": r"Global\RoadDog_v1",
    "WINDOWS_APP_USER_MODEL_ID": "RoadDog.RoadDog",
    "WINDOWS_UNINSTALL_REGISTRY_SUBKEY": (
        r"Software\Microsoft\Windows\CurrentVersion\Uninstall\RoadDog"
    ),
    "WINDOWS_AUTOSTART_TASK_NAME": "Road Dog Autostart",
    "WINDOWS_SHORTCUT_FILE_NAME": "Road Dog.lnk",
    "WINDOWS_AUTOSTART_DESCRIPTION": "Road Dog (Autostart)",
    "WINDOWS_BRANDED_LAUNCHER_FILE_NAME": "RoadDog.exe",
    "WINDOWS_BRANDED_LAUNCHER_DIR_NAME": "RoadDog",
    "WINDOWS_BRANDED_LAUNCH_ENV_VAR": "JARVIS_BRANDED_LAUNCH",
    "MACOS_APP_NAME": "Road Dog",
    "MACOS_APP_DIR_NAME": "Road Dog.app",
    "MACOS_EXECUTABLE_NAME": "RoadDog",
    "MACOS_BUNDLE_ID": "com.road-dog.desktop",
    "MACOS_DMG_BUNDLE_ID": "ai.roaddog.desktop",
    "MACOS_AUTOSTART_LABEL": "com.road-dog.autostart",
    "LINUX_APP_NAME": "Road Dog",
    "LINUX_DESKTOP_ENTRY_FILE_NAME": "road-dog.desktop",
    "LINUX_WM_CLASS": "road-dog",
    "DEFAULT_OFFICIAL_REPO_SLUG": "tbwcheatwood-hue/Road-Dog",
    "OFFICIAL_REPO_SLUG_ENV_VAR": "JARVIS_OFFICIAL_REPO_SLUG",
    "OFFICIAL_REPO_SLUG": "tbwcheatwood-hue/Road-Dog",
    "OFFICIAL_REPO_URL": "https://github.com/tbwcheatwood-hue/Road-Dog",
    "OFFICIAL_REPO_GIT_URL": "https://github.com/tbwcheatwood-hue/Road-Dog.git",
    "OFFICIAL_RELEASES_LATEST_API_URL": (
        "https://api.github.com/repos/tbwcheatwood-hue/Road-Dog/releases/latest"
    ),
    "UPDATER_USER_AGENT": "RoadDog-Updater",
}


def test_default_exported_identity_values_are_frozen() -> None:
    previous = os.environ.pop(branding.OFFICIAL_REPO_SLUG_ENV_VAR, None)
    try:
        module = importlib.reload(branding)
        actual = {name: getattr(module, name) for name in _CURRENT_IDENTITY}
        assert actual == _CURRENT_IDENTITY
    finally:
        if previous is not None:
            os.environ[branding.OFFICIAL_REPO_SLUG_ENV_VAR] = previous
        importlib.reload(branding)


def test_official_repo_slug_override_is_exact() -> None:
    assert (
        branding.resolve_official_repo_slug(
            {"JARVIS_OFFICIAL_REPO_SLUG": "RenamedOrg/RenamedRepo"}
        )
        == "RenamedOrg/RenamedRepo"
    )


@pytest.mark.parametrize(
    "value",
    [
        "owner",
        "owner/repo/extra",
        "/repo",
        "owner/",
        "owner/repo evil",
        " owner/repo",
        "owner/repo ",
    ],
)
def test_official_repo_slug_override_rejects_non_exact_values(value: str) -> None:
    with pytest.raises(ValueError, match="exact owner/repository slug"):
        branding.resolve_official_repo_slug({"JARVIS_OFFICIAL_REPO_SLUG": value})
