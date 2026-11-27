# Road Dog runtime repair — 2026-11-26

This note records what was repaired, what was executed, and what is still
unqualified. It is not a release announcement.

## 1. Kilo Code and Z Code

**Root cause.** The headless planners called `normalize_permission` and
discarded the result. Kilo was launched as `kilo-code` with the prompt and
no `--auto` decision. Z Code was launched as `z-code` with no `--mode`. On
Z Code 0.18.0, `zcode --prompt` defaults to `--mode yolo`. The spawn-env
factories returned `None` whenever no Road Dog key was stored, including
when the CLI's own config already existed, and the launcher treats `None`
as "do not start".

**Production path.** Chat turns go through `plan_kilo` / `plan_z` in
`jarvis/agent_chat/runner_cli.py`. IDE panes go through
`jarvis/agentic_ide/session.py` `agent_argv` and the registry's
`launch_picks`. `kilo_code_spawn_env` and `z_code_spawn_env` return `{}`
when a vendor config file is present (the CLI's own login), a one-key env
when only a Road Dog secret exists, and `None` when neither does.

**Permission rule.** Kilo passes `--auto` only for the `auto` stance. Ask
and plan pass no permission flag. Z Code always passes `--mode`, and the
default stance is `build`. Folding a middle stance lands on ask (Kilo) or
edit (Z Code), not on the unrestricted mode.

**Verified.** Z Code 0.18.0 `--help` was read from
`node /opt/ZCode/resources/glm/zcode.cjs --help` on this machine. The
desktop `/usr/bin/zcode` is the Electron app and is not used. Kilo's flags
come from the published `kilo run` reference (`--format json`, `--model`,
`--variant`, `--session`, `--dir`, `--auto`). Kilo is not installed here,
so its help text was not executed. No prompt was sent to either CLI.

**Tests.** `tests/unit/agent_chat/test_kilo_zcode_argv.py` and the spawn-env
cases in `tests/unit/workspace/test_agents.py`.

**Limit.** Z Code 0.18.0 has no headless `--model` flag. A model pick in
the chat is not forwarded. Remote panes still send the command name
`zcode`, which on some machines is the GUI.

## 2. LM Studio

**Root cause.** There was no `lmstudio` brain. The generic local OpenAI
card was the only path, and the resolver appended other providers,
including paid ones, after a local primary.

**Production path.** `LMStudioBrain` uses provider id `lmstudio`. The
default root is `http://127.0.0.1:1234`. A URL saved on that card replaces
it. `/v1` is appended once. The class does not start or stop LM Studio.
When `lmstudio` or `local-openai` is the selected primary, the resolver
does not append a paid provider or another local server. `lmstudio` is not
in the ambient tail, so selecting Gemini does not silently call LM Studio.

**Tests.** `tests/unit/plugins/brain/test_lmstudio_endpoint.py`. No live
completion was requested.

## 3. Readiness

**Root cause.** A stored API key was reported `ok`, and `ollama` on `PATH`
was reported as working inference.

**Production path.** `jarvis/setup/readiness.py` now sets `state` to
`installed`, `configured`, `reachable`, `operational`, `unavailable`, or
`unverified`. A stored key is `configured`. Ollama is `operational` only
when `GET http://127.0.0.1:11434/api/tags` returns a body. LM Studio is
`operational` only when its configured `/v1/models` does. Timeout is 2
seconds. `GET /api/setup-report/diagnostics` serves the same report. The
settings page and the connect step render it. `jarvis --readiness` still
prints the JSON, with `state` added.

**Tests.** `tests/unit/setup/test_readiness_states.py`. The probes in
those tests are stubbed. A paid catalog API is not called.

**Limit.** `authenticated` is defined and unused. This module does not
send a credential, so it will not report that state.

## 4. Signing and the native-crypto index

The Fulcio identity in `install/tuf/1.root.json` is the Road Dog tag
workflow. The offline Ed25519 public key in that file is the predecessor
key. `gh secret list` on `tbwcheatwood-hue/Road-Dog`, authenticated as the
repository owner, returned no secret names on 2026-11-26. No private key
was generated. Verification was not disabled. Threshold stays 2-of-2.
`install/TRUST_ROOT.md` records this.

The `native-crypto` index URL in `pyproject.toml` was probed the same day.
`https://tbwcheatwood-hue.github.io/Hue/native-crypto/50.0.2-1/simple/`,
the predecessor Pages index, and a Road-Dog Pages path each returned
HTTP 404. The pin was left in place so installation fails closed.

**No release archive was cut.** Qualification requires a signing secret
that matches the pinned public key and an index that serves the pinned
wheel. Neither is true.

## 5. Isolation

User-facing identity is Road Dog: slug `road-dog`, keyring service
`road-dog`, data directory `.road-dog` (Windows `Road Dog`), session
cookie `road_dog_session`, bundle `com.road-dog.desktop`, updater
`RoadDog-Updater`. The official repository slug is
`tbwcheatwood-hue/Road-Dog`. The config file name stays `jarvis.toml`
inside Road Dog's directory. The Python package stays `jarvis`.

The Windows installer AppId is `C4E8A17B-6D2F-4B9A-8C31-5F0E2A9D7B64`.
The predecessor AppId is not reused, so this installer does not upgrade
that product. `jarvis/setup/isolation.py` copies a data directory only
when the caller passes `authorized=True`. It does not delete the source
and does not copy credentials.

## 6. Advertised features

Sam's personality seed, persistent memory, the Crew, wake word,
push-to-talk, check-ins, and quiet hours are existing product code. This
repair did not reimplement them and did not run a live conversation.
README claims for those features describe that inherited behavior. Kilo
Code and Z Code are operational only to the extent of section 1. LM
Studio is operational only to the extent of section 2. A stored key is
not advertised as a proven login.

## 7. Security review

- Kilo `--auto` and Z Code `--mode yolo` are passed only for the
  unrestricted stance. A missing Z Code mode is a refused start, because
  omission is yolo.
- Spawn environment does not read `~/.zcode` config contents. It checks
  that a file is non-empty, then lets the CLI use its own login. A stored
  token is placed only in the child environment.
- Readiness GETs local discovery URLs and does not attach API keys.
- LM Studio and the generic local server do not gain a paid fallback when
  they are the selected brain. Neither class starts a server.
- Installer verification was not weakened. The offline private key was
  not created or printed. `gh secret list` showed no names.
- The Windows AppId changed so this installer does not upgrade the
  predecessor product. Data copy runs only when `authorized=True` and
  never deletes the source.
- No new secret is written to `jarvis.toml` or to the repository.

## 8. What was not verified

- A live Kilo process, a live Z Code prompt, and a live LM Studio
  completion. Those would spend a model or require a server this repair
  refused to start.
- The full Python suite, the frontend production build, and GitHub
  Actions on this commit. The focused run below passed. It is not the
  whole suite.

Focused run, 2026-11-26, from the repository root with `.venv/bin/python`:

```
pytest tests/unit/ui/web/test_permissions_snapshot.py \
  tests/unit/plugins/brain/test_local_openai.py \
  tests/unit/plugins/brain/test_lmstudio_endpoint.py \
  tests/unit/agent_chat/test_kilo_zcode_argv.py \
  tests/unit/setup/test_readiness_states.py \
  tests/unit/setup/test_isolation.py \
  tests/unit/core/test_branding.py \
  tests/unit/agent_chat/test_ide_cli_seats.py::test_every_chat_cli_seat_names_a_registered_ide_entry_in_the_ide_order \
  tests/unit/workspace/test_agents.py -k "not pty_available"
```

Result: 120 passed, 1 deselected, 2 warnings. The deselected test is
`test_pty_available_is_true_on_a_host_with_a_shell`. `pty_available()`
returned false on this host outside the sandbox. That assertion was not
changed.
- The settings readiness panel in a browser. The component is wired to
  `GET /api/setup-report/diagnostics`.
- PTY availability on this host. `pty_available()` returned false outside
  the sandbox. That check was already false before these edits and was
  not weakened.
