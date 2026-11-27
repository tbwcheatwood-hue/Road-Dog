# Road Dog — Migrating from Personal Jarvis / Hue (optional, explicit)

Road Dog and Personal Jarvis/Hue can coexist on one machine. Road Dog never
touches another install automatically.

## What is independent by default
- Install dir: `~/.road-dog` (vs upstream's `~/.personal-jarvis`).
- Road Dog data root: `~/.road-dog/data` (override with `ROAD_DOG_DATA_DIR`).
- Desktop entries, app ids, autostart labels, uninstall registry keys: Road
  Dog's own (`road-dog.desktop`, `Road Dog.app`, `RoadDog.exe`, …).
- Endpoint registry: `~/.road-dog/data/endpoints.json`.
- Update channel: none by default (an update check cannot pull upstream
  builds); set `JARVIS_OFFICIAL_REPO_SLUG` to your fork's repo to enable.

Shared for continuity (deliberate): the `jarvis` package/config name, the
`personal-jarvis` keyring service (so migrated keys work), and the
`Jarvis`/`~/.jarvis` user-data folders the legacy stack reads.

## The import (explicit, plan-first)
Either REST:

```bash
# 1. plan (dry run — nothing written)
curl -X POST 127.0.0.1:47821/api/migration/plan \
  -H 'Content-Type: application/json' \
  -d '{"source": "/home/you/.jarvis"}'
# 2. execute only when the plan looks right
curl -X POST 127.0.0.1:47821/api/migration/import \
  -H 'Content-Type: application/json' \
  -d '{"source": "/home/you/.jarvis", "execute": true}'
```

or in Python:

```python
from jarvis.migration.upstream_import import import_upstream_install
plan, result = import_upstream_install("/home/you/.jarvis", execute=True)
```

Rules enforced by the tool (see `jarvis/migration/upstream_import.py`):
- the source directory must be named by you; nothing is auto-discovered,
- credentials are NEVER migrated (keys stay in your OS keychain under
  `personal-jarvis`, which Road Dog reads for continuity),
- existing Road Dog files are never clobbered unless `overwrite=True`,
- the source is opened read-only; the upstream install is not modified.
