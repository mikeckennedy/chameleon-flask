# API Reference


The complete public API: engine setup, the <span class="citation" cites="template">@template</span> decorator, direct rendering, and exceptions.


## Configuration


Set up the Chameleon template engine once at app startup.


[global_init()](global_init.md#chameleon_flask.global_init)  
Initialize the Chameleon template engine.

[engine.clear()](engine.clear.md#chameleon_flask.engine.clear)  
Reset the template engine to its uninitialized state.


## Decorating views


Render templates from Flask/Quart view functions (sync or async) and return friendly 404s.


[template()](template.md#chameleon_flask.template)  
Decorate a Flask or Quart view method to render a Chameleon template.

[not_found()](not_found.md#chameleon_flask.not_found)  
Abort the current view and render a friendly 404 page.


## Direct rendering


Render a template to a Response or raw HTML without the decorator.


[response()](response.md#chameleon_flask.response)  
Render a Chameleon template directly to a `flask.Response`.

[engine.render()](engine.render.md#chameleon_flask.engine.render)  
Render a Chameleon template to an HTML string.


## Exceptions


Errors raised by the engine. Importable from `chameleon_flask` directly or from `chameleon_flask.exceptions`.


[FlaskChameleonException](FlaskChameleonException.md#chameleon_flask.FlaskChameleonException)  
Base exception for all chameleon-flask errors.

[FlaskChameleonNotFoundException](FlaskChameleonNotFoundException.md#chameleon_flask.FlaskChameleonNotFoundException)  
Raised by `not_found()` to signal that a view should render a 404 page.
