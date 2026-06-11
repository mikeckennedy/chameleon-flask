# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`chameleon_flask` (currently v0.6.0) integrates the Chameleon template language with Flask **and Quart**. It is a small library: three modules in `chameleon_flask/`, a test suite in `tests/`, and a runnable demo in `example/example_app.py`. The project began as a fork of the sibling `fastapi-chameleon` project, which explains the FastAPI-style code that still lingers in the README's `not_found` example — a stale copy-paste artifact, not real FastAPI support.

- Python >= 3.10; runtime deps are just `flask[async]` and `Chameleon` (unpinned)
- Build backend: hatchling; version is **hardcoded** in `pyproject.toml` (`[project].version`) — bump it manually (hatch-vcs is listed in build requires but not wired up)
- Publishing is manual via twine; `dist/`, `tests/`, `example/`, `ruff.toml` etc. are excluded from sdist/wheel builds

## Commands

Dev dependencies (pytest, pytest-clarity, twine, hatchling, setuptools, plus `-r requirements.txt`) live in `requirements-dev.txt`, **not** in `pyproject.toml` — there are no `[dependency-groups]`, so a plain `uv run pytest` fails. Two ways to run tests:

```bash
# Zero-setup (ephemeral pytest overlay, doesn't touch the venv):
uv run --with pytest pytest tests/ -q

# Or install dev deps into the venv first, then plain pytest works:
pip install -r requirements-dev.txt
pytest tests/ -q
```

Single file / single test:

```bash
uv run --with pytest pytest tests/test_render.py -q
uv run --with pytest pytest tests/test_render.py::test_default_template_name_pt -q
```

`tests/conftest.py` locates templates via `pytestconfig.rootdir / 'tests' / 'templates'`. Pytest anchors rootdir to the repo root (via `pyproject.toml`/`tox.ini`) regardless of the invocation directory, so running from a subdirectory is fine — but do **not** pass a custom `--rootdir`, which breaks template resolution for most of the suite.

Lint and format (ruff is the enforced style — see `ruff.toml`: line-length 120, **single quotes**, rules E/F/I):

```bash
ruff check .          # add --fix for auto-fixes (import sorting is enforced via I)
ruff format .
```

Do **not** use tox: `tox.ini` is stale — its `commands = pytest flask-chameleon` references a path from the project's old name, and its envlist starts at py39 while the package requires >= 3.10.

Local quirk: the repo's virtualenv is `venv/` (not `.venv/`) and does not include pytest by default.

## Architecture

All real logic lives in `chameleon_flask/engine.py`. `__init__.py` re-exports the public API (`__all__ = ['template', 'global_init', 'not_found', 'response']`) and derives `__version__` from package metadata. `exceptions.py` defines `FlaskChameleonException` and its subclass `FlaskChameleonNotFoundException`.

### Module-level global state (the core design)

The engine is process-global, not app-scoped:

- `global_init(template_folder, auto_reload=False, cache_init=True, restricted_namespace=True)` creates a `chameleon.PageTemplateLoader` stored in a module global, and records `template_path`.
- **`global_init()` is one-shot by default**: with `cache_init=True` it silently returns if already initialized — a second call with a different folder or different `restricted_namespace` is ignored. Use `engine.clear()` (not exported in `__all__`) or `cache_init=False` to re-initialize. Tests depend on this discipline.
- The `@template` decorator itself mutates global state: if `global_init` hasn't run at decoration time, it defaults `template_path` to `'templates'` and resolves the template filename **once, at decoration time** — calling `global_init` later does not re-resolve already-decorated views.

### The `@template` decorator flow

- Usable bare (`@template`) or with args (`@template('home/index.pt', content_type=..., status_code=...)`). Bare usage derives the template path as `{last segment of module}/{function_name}.html`, falling back to `.pt` if the `.html` file doesn't exist on disk. (This is why templates for `tests/test_render.py` live in `tests/templates/test_render/` — renaming that test file breaks those tests.)
- Sync vs async is dispatched via `inspect.iscoroutinefunction`. Both wrappers delegate to shared `build_response`/`not_found_response` closures so the two paths cannot drift — the only difference between them is the `await`. (Historically parity bugs were a theme: commit 669af91 fixed `status_code` being dropped only on the async path.)
- A decorated view must return either a `dict` (splatted into the template as the model) or a Flask/Quart `Response` (passed through untouched, e.g. for redirects). Anything else raises `FlaskChameleonException`.
- Response pass-through detection is an `isinstance` check against `werkzeug.sansio.response.Response` — the shared base class of `flask.Response`, `quart.Response`, bare werkzeug responses, and any subclasses — so the library never has to import Quart. A legacy `str(type(x))` string-set fallback (`response_classes`) remains for Response implementations that predate the shared werkzeug base.
- `not_found()` raises `FlaskChameleonNotFoundException`; both wrappers catch it and render the 404 template (`errors/404.pt` by default) with an **empty model**, hardcoded `text/html`, status 404 — the view's own `content_type`/`status_code` are ignored for 404s.

### Namespace restriction (the v0.6.0 feature)

`restricted_namespace=True` (the default) makes Chameleon reject non-TAL/METAL/i18n namespaced attributes. Pass `restricted_namespace=False` to `global_init()` to allow Alpine.js/Vue-style shorthand attributes (`@click`, `:class`, `x-data`) in templates. The flag is forwarded directly to `PageTemplateLoader`. The v0.6.0 release notes were committed and then deleted; recover them with `git show 895621d:RELEASE_v0.6.0.md`.

## Testing notes

- There is **no Flask app or test client** anywhere in the suite. Decorated views are called as plain Python functions (async ones via `asyncio.run()`); the engine constructs `flask.Response` objects directly, so no app/request context is needed.
- `tests/conftest.py` has two fixtures: `test_templates_path` and `setup_global_template` (calls `global_init`, yields, then `engine.clear()` on teardown). Because engine state is module-global, any test that initializes the engine must clean up, or later tests silently reuse the old template path — `test_init.py` calls `clear()` defensively and uses `cache_init=False` for exactly this reason.

## Known wrinkles

- The README's `not_found()` example still uses FastAPI route syntax (`'/catalog/item/{item_id}'`, `item.dict()`) — a leftover from the fork. The README also doesn't document `restricted_namespace`, `content_type`/`status_code` on `@template`, or the `response()`/`render()` functions.
- Commit dc0cdf0 renamed the `mimetype` kwarg to `content_type` (breaking change) — use `content_type` in all new code and docs.
- `render()` and `clear()` are importable from `chameleon_flask.engine` but intentionally absent from the package `__all__`.
