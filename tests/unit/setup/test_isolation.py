"""Data migration is optional and does not delete the source."""

from __future__ import annotations

from pathlib import Path

from jarvis.setup.isolation import copy_data_dir


def test_copy_requires_authorization_and_keeps_the_source(tmp_path: Path) -> None:
    source = tmp_path / "personal-jarvis"
    source.mkdir()
    (source / "jarvis.toml").write_text("owned = true\n", encoding="utf-8")
    destination = tmp_path / "road-dog"

    assert copy_data_dir(source, destination, authorized=False) is None
    assert not destination.exists()
    assert copy_data_dir(source, destination, authorized=True) == destination
    assert (destination / "jarvis.toml").read_text(encoding="utf-8") == "owned = true\n"
    assert (source / "jarvis.toml").is_file()
    # A second call must not overwrite a directory Road Dog already has.
    (destination / "jarvis.toml").write_text("kept = true\n", encoding="utf-8")
    assert copy_data_dir(source, destination, authorized=True) is None
    assert (destination / "jarvis.toml").read_text(encoding="utf-8") == "kept = true\n"
