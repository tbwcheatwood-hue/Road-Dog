"""Optional copy of a Personal Jarvis data directory into Road Dog's.

Nothing in this module runs at import or at startup. A copy happens only when
the caller passes ``authorized=True`` or the process has
``ROAD_DOG_MIGRATE_DATA=1``. The source directory is never deleted, and
credentials are never copied.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

_AUTH_ENV = "ROAD_DOG_MIGRATE_DATA"


def migration_authorized(environ: dict[str, str] | None = None) -> bool:
    source = os.environ if environ is None else environ
    return source.get(_AUTH_ENV, "").strip() == "1"


def copy_data_dir(source: Path, destination: Path, *, authorized: bool) -> Path | None:
    """Copy ``source`` onto ``destination`` when ``authorized`` is true.

    An existing destination is left untouched. Returns the destination when a
    copy was made, otherwise ``None``.
    """
    if not authorized:
        return None
    if not source.is_dir():
        return None
    if destination.exists():
        return None
    shutil.copytree(source, destination)
    return destination
