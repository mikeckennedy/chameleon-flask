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


Point the library at your templates folder once, at app startup, and every decorated view in the process knows where to look from then on. Under the hood this creates a single Chameleon `PageTemplateLoader`, which compiles each template to Python bytecode the first time it renders and caches the result.

The call is one-shot by design. With `cache_init=True` (the default), later calls are silently ignored once the engine is initialized, so a stray second [global_init()](global_init.md#chameleon_flask.global_init) deep in some module cannot swap your template folder out from under you. To re-initialize with different settings, pass `cache_init=False` or call [chameleon_flask.engine.clear()](engine.clear.md#chameleon_flask.engine.clear) first.

Call this before any decorated view is defined: the bare `@template` form resolves its template file name at decoration time and relies on the folder recorded here.


## Parameters


`template_folder: str`  
Path to the template directory.

`auto_reload: bool = ``False`  
Re-read a template whenever its file changes. Exactly what you want while editing templates and an unneeded file check per render in production, so tie it to your dev-mode flag.

`cache_init: bool = ``True`  
If True, do nothing when the engine is already initialized.

`restricted_namespace: bool = ``True`  
If True, only TAL/METAL/i18n namespaced attributes are allowed in templates. Set it to False to let attribute-based JavaScript frameworks such as Alpine.js and Vue use their shorthand (`@click`, `:class`, `x-data`).


## Raises


`FlaskChameleonException`  
If `template_folder` is empty or is not a directory.


## Examples

``` python
from pathlib import Path
import chameleon_flask

dev_mode = True
folder = Path(__file__).resolve().parent / 'templates'
chameleon_flask.global_init(str(folder), auto_reload=dev_mode)
```
