"""The Road Dog Ed25519 pin is one public key, and the 2-of-2 rule stays."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = ROOT / "install" / "keys" / "offline-ceremony.pub"
OLD_RAW = "ae57e283700b141ac40fe56b359f2196b567449c439c8f0f0a4c46076e8de14e"
NEW_RAW = "6e2440db06f9331c8830638f03baa9a7bd9ae2ba6daa33b4c31fc14cfc9c764d"
FINGERPRINT = "32002810c24cc633de7e868d3b5282c0ceab327e76d502bf067970738e695f03"


def _pem(text: str, marker: str) -> str:
    match = re.search(
        rf"-----BEGIN PUBLIC KEY-----\n.*?\n-----END PUBLIC KEY-----",
        text,
        re.DOTALL,
    )
    assert match is not None, marker
    return match.group(0) + "\n"


def test_public_key_copies_and_fingerprint_match() -> None:
    published = PUB.read_text(encoding="utf-8")
    shell = (ROOT / "install" / "install-verify.sh").read_text(encoding="utf-8")
    powershell = (ROOT / "install" / "install-verify.ps1").read_text(encoding="utf-8")
    assert _pem(shell, "sh") == published
    assert _pem(powershell, "ps1") == published
    assert FINGERPRINT in shell and FINGERPRINT in powershell
    der = Path(PUB).read_bytes()
    # Fingerprint is SHA-256 of the SPKI DER, not of the PEM armor.
    from base64 import b64decode

    body = "".join(
        line for line in published.splitlines() if not line.startswith("-----")
    )
    assert hashlib.sha256(b64decode(body)).hexdigest() == FINGERPRINT


def test_root_version_two_keeps_threshold_and_revokes_the_predecessor() -> None:
    first = json.loads((ROOT / "install" / "tuf" / "1.root.json").read_text())
    second = json.loads((ROOT / "install" / "tuf" / "2.root.json").read_text())
    assert first["signed"]["version"] == 1
    assert first["signed"]["keys"]["offline_ceremony"]["keyval"]["public"] == OLD_RAW
    assert second["signed"]["version"] == 2
    assert second["signatures"] == []
    offline = second["signed"]["keys"]["offline_ceremony"]
    assert offline["keytype"] == "ed25519"
    assert offline["keyval"]["public"] == NEW_RAW
    assert NEW_RAW != OLD_RAW
    for role in second["signed"]["roles"].values():
        assert role["threshold"] == 2
        assert role["keyids"] == ["fulcio_oidc", "offline_ceremony"]
    revoked = second["signed"]["unrecognized_fields"]["wave2_revocation"]["revoked_public"]
    assert revoked == OLD_RAW


def test_private_key_is_not_in_the_tree() -> None:
    for path in (ROOT / "install").rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in {".key", ".pem"} and "offline-ceremony" in path.name:
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert "BEGIN PRIVATE KEY" not in text
            assert "BEGIN OPENSSH PRIVATE KEY" not in text
