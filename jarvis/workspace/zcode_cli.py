"""Locate the Z Code headless CLI without launching the desktop app.

The desktop package and the headless CLI share the command name ``zcode``.
On Linux the desktop installer puts an Electron binary on ``PATH``
(``/usr/bin/zcode`` → ``/opt/ZCode/zcode``). That binary does not accept the
headless flags; starting it opens the GUI. The CLI that ``--help`` documents
is ``resources/glm/zcode.cjs`` beside that install (verified on Z Code 0.18.0),
or a ``zcode`` script the CLI installer placed on ``PATH``.

This module only resolves an argv. It does not start a prompt, write config,
or read credential files.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

#: Bundled CLI entry next to a desktop install. The Electron executable in the
#: same tree is not this file.
_BUNDLE_CJS: tuple[Path, ...] = (
    Path("/opt/ZCode/resources/glm/zcode.cjs"),
    Path("/Applications/ZCode.app/Contents/Resources/glm/zcode.cjs"),
)


def _electron_app(path: Path) -> bool:
    """True when ``path`` is the desktop shell, not the headless CLI."""
    try:
        parent = path.resolve().parent
    except OSError:
        parent = path.parent
    return (parent / "chrome-sandbox").is_file() or (parent / "LICENSE.electron.txt").is_file()


def _node() -> str | None:
    return shutil.which("node")


def _cjs_argv(script: Path) -> list[str] | None:
    node = _node()
    if node is None or not script.is_file():
        return None
    return [node, str(script)]


def resolve_zcode_argv() -> list[str] | None:
    """Argv that runs the headless CLI, or None when only the GUI is present.

    Search order: the CLI bundle shipped beside a desktop install, the
    documented home-directory deploy locations, then a ``PATH`` entry that is
    not the Electron app. A GUI binary is never returned.
    """
    home = Path.home()
    scripts = (
        *_BUNDLE_CJS,
        home / ".zcode" / "server" / "agents" / "glm" / "zcode.cjs",
    )
    for script in scripts:
        argv = _cjs_argv(script)
        if argv is not None:
            return argv

    wrappers = (
        home / ".local" / "bin" / "zcode",
        home / ".zcode" / "bin" / "zcode",
        home / ".zcode" / "server" / "agents" / "glm" / "zcode-agent",
    )
    for wrapper in wrappers:
        if wrapper.is_file() and os.access(wrapper, os.X_OK) and not _electron_app(wrapper):
            return [str(wrapper)]

    names = ("zcode", "zcode.exe", "zcode.cmd", "z-code", "z-code.exe")
    if sys.platform == "win32":
        names = ("zcode.exe", "zcode.cmd", "zcode", "z-code.exe", "z-code")
    for name in names:
        found = shutil.which(name)
        if not found:
            continue
        path = Path(found)
        if _electron_app(path):
            continue
        if path.suffix == ".cjs":
            argv = _cjs_argv(path)
            if argv is not None:
                return argv
            continue
        return [str(path)]
    return None
