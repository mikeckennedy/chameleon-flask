# Changelog

This changelog is generated automatically from [GitHub Releases](https://github.com/mikeckennedy/chameleon-flask/releases).


# v0.6.2

*2026-11-07* · [GitHub](https://github.com/mikeckennedy/chameleon-flask/releases/tag/v0.6.2)

Clearer errors and wraps-aware async detection

- `[@template](https://github.com/template)` now looks through `functools.wraps` chains when deciding whether a view is async, so an `async def` wrapped by your own sync decorator is awaited correctly instead of failing with "Invalid return type coroutine".
- When the outer decorator hides the `async def` (no `functools.wraps`), the stray coroutine is closed and a [FlaskChameleonException](reference/FlaskChameleonException.html#chameleon_flask.FlaskChameleonException) tells you to put `[@template](https://github.com/template)` directly on the `async def`.
- A view model containing the key `encoding` now raises a clear [FlaskChameleonException](reference/FlaskChameleonException.html#chameleon_flask.FlaskChameleonException) (Chameleon reserves it as a render argument) instead of a confusing Chameleon `TypeError`.
- Tests covering all three edge cases.
- Docs: README and API reference rewritten in a narrative voice, site rebuilt with Great Docs 0.17.0, and the navbar version badge is now taken from `pyproject.toml` at build time instead of the latest GitHub release.

No breaking changes: each of the fixed code paths previously failed.


# v0.6.1

*2026-06-11* · [GitHub](https://github.com/mikeckennedy/chameleon-flask/releases/tag/v0.6.1)

Tighten types and docs across the public API

- Complete annotations: NoReturn on not_found, fix **template_data: dict -\> Any, modern X \| None unions, full param/return types everywhere**
- Cast the response passthrough (pyrefly caught the flask.Response mismatch)
- Pin ty and pyrefly to the venv via pyproject \[tool.\*\] config
- Examples sections and module docstrings; document decoration-time template resolution
- Export exceptions at the package root with test coverage
- README: badges, default naming, Quart note, direct rendering section
- Example app: not_found demo with catalog and 404 templates


# v0.6.0

*2025-11-21* · [GitHub](https://github.com/mikeckennedy/chameleon-flask/releases/tag/v0.6.0)

Release v0.6.0


## New Feature: Namespace Restriction Control

Added support for controlling Chameleon's namespace restriction, enabling better compatibility with attribute-based JavaScript frameworks like Vue.js and Alpine.js.


### What's New

The [global_init()](reference/global_init.html#chameleon_flask.global_init) function now accepts a `restricted_namespace` parameter (defaults to `True` for backward compatibility). When set to `False`, Chameleon only treats its own namespaces (TAL, METAL, i18n) specially, allowing all other attributes to pass through unchanged.


### Usage

``` python
import chameleon_flask

# Turn off namespace restriction for Alpine.js/Vue.js compatibility
chameleon_flask.global_init(
    template_folder='templates',
    auto_reload=True,
    restricted_namespace=False  # <-- Enable attribute-based JS frameworks
)
```


### Why This Matters

With `restricted_namespace=False`: - Chameleon only processes its own namespaces (`tal:`, `metal:`, `i18n:`) - All other attributes like `x-data`, `x-on:click`, `x-bind:class`, `[@click](https://github.com/click)`, `:class` are left untouched - Perfect for templates using Alpine.js, Vue.js, or other attribute-based frameworks - No need to escape or work around Chameleon's namespace restrictions


### Backward Compatibility

This change is fully backward compatible. The default value is `True`, maintaining the existing behavior unless explicitly changed.


# v0.5.1

*2025-01-12* · [GitHub](https://github.com/mikeckennedy/chameleon-flask/releases/tag/v0.5.1)

Things are getting stable now.

This release fixes a bug where the status code is not passed as part of the response. For example, the sync version is status code 201 whereas the async one is status code 200 with this bug (now fixed):

``` python
[@blueprint](https://github.com/blueprint).post('/saves/new')
[@template](https://github.com/template)('saves/partials/card-processing.pt', status_code=201)
def save_new():
   # ...


[@blueprint](https://github.com/blueprint).post('/saves/new')
[@template](https://github.com/template)('saves/partials/card-processing.pt', status_code=201)
async def save_new():
   # ...
```


# v0.0.5

*2024-11-14* · [GitHub](https://github.com/mikeckennedy/chameleon-flask/releases/tag/v0.0.5)

Add support for non-200 status code in template decorator. For example 201 for a POST handling view.


# v0.0.4

*2024-11-13* · [GitHub](https://github.com/mikeckennedy/chameleon-flask/releases/tag/v0.0.4)

BREAKING CHANGE: Rename `mimetype` parameter named on [template()](reference/template.html#chameleon_flask.template) to `content_type` (as that is that it represents).


# v0.0.3

*2024-11-13* · [GitHub](https://github.com/mikeckennedy/chameleon-flask/releases/tag/v0.0.3)

There was a problem with 0.0.2 using quart responses. Now working.


# v0.0.2

*2024-11-13* · [GitHub](https://github.com/mikeckennedy/chameleon-flask/releases/tag/v0.0.2)

Allow quart and flask raw responses.


# v0.0.1

*2024-11-13* · [GitHub](https://github.com/mikeckennedy/chameleon-flask/releases/tag/v0.0.1)

First release, published to PyPI on 2024-11-07.

chameleon-flask began as a copy of the sibling [fastapi-chameleon](https://github.com/mikeckennedy/fastapi-chameleon) project, reworked for Flask and Quart. The package was first named the other way round; it became `chameleon-flask` because that name on PyPI was already taken.

- `global_init(template_folder, auto_reload=False, cache_init=True)` sets up one process-wide Chameleon template loader.
- `[@template](https://github.com/template)` decorates sync and async Flask/Quart views; the view returns a `dict` for the template model, or a `flask.Response` to pass straight through (redirects and the like). Usable bare, deriving the template name from the view, or with an explicit template path.
- [not_found()](reference/not_found.html#chameleon_flask.not_found) renders a friendly 404 page (`errors/404.pt` by default) from inside a view.
- [response()](reference/response.html#chameleon_flask.response) renders a template directly to a `flask.Response`.
- Example app and a test suite; packaging via `pyproject.toml`.
