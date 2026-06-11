## global_init()


Initialize the Chameleon template engine.


Usage

``` python
global_init(
    template_folder,
    auto_reload=False,
    cache_init=True,
    restricted_namespace=True
)
```


Call this once at app startup, before any decorated view runs. With `cache_init=True` (the default), later calls are silently ignored once the engine is initialized; pass `cache_init=False` (or call [chameleon_flask.engine.clear()](engine.clear.md#chameleon_flask.engine.clear)) to re-initialize with different settings.


## Parameters


`template_folder: str`  
Path to the template directory.

`auto_reload=``False`  
Whether to auto-reload templates on change (handy in dev mode).

`cache_init=``True`  
If True, do nothing when the engine is already initialized.

`restricted_namespace=``True`  
If True, only TAL/METAL/i18n namespaces are allowed. If False, allows attribute-based JS frameworks like Alpine.js to use shorthand syntax (<span class="citation" cites="click">@click</span>, :class, etc.)


## Raises


`FlaskChameleonException`  
If `template_folder` is empty or is not a directory.
