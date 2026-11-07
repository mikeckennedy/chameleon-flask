# API Reference


Everything the package exports, in the order you meet it: set the engine up once, decorate your views, render directly when the decorator cannot reach, and the two exceptions that tie it together.


## Configuration


Point the engine at your templates folder once at app startup, and reset it when a test suite needs a clean slate.


[global_init()](global_init.md#chameleon_flask.global_init)  
Initialize the Chameleon template engine.

[engine.clear()](engine.clear.md#chameleon_flask.engine.clear)  
Reset the template engine to its uninitialized state.


## Decorating views


The decorator that turns a view returning a dict into a rendered response, sync or async, and the one call that swaps the page for a friendly 404.


[template()](template.md#chameleon_flask.template)  
Decorate a Flask or Quart view method to render a Chameleon template.

[not_found()](not_found.md#chameleon_flask.not_found)  
Abort the current view and render a friendly 404 page.


## Direct rendering


For error handlers, conditional branches, and anywhere else the decorator cannot reach: a template straight to a Response, or straight to an HTML string.


[response()](response.md#chameleon_flask.response)  
Render a Chameleon template directly to a `flask.Response`.

[engine.render()](engine.render.md#chameleon_flask.engine.render)  
Render a Chameleon template to an HTML string.


## Exceptions


The base error for everything the engine raises on purpose, and the not-found signal that `not_found()` raises and `@template` catches. Importable from `chameleon_flask` directly or from `chameleon_flask.exceptions`.


[FlaskChameleonException](FlaskChameleonException.md#chameleon_flask.FlaskChameleonException)  
Base exception for all chameleon-flask errors.

[FlaskChameleonNotFoundException](FlaskChameleonNotFoundException.md#chameleon_flask.FlaskChameleonNotFoundException)  
Raised by `not_found()` to signal that a view should render a 404 page.
