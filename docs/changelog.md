# Changelog

This changelog is generated automatically from [GitHub Releases](https://github.com/mikeckennedy/chameleon-flask/releases).


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
