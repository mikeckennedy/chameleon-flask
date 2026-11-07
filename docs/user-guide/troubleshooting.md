# Troubleshooting

This is a field guide. Each heading is an error message, or the symptom you see when there is no message, so you can search this page for the text in your terminal. Under each one: what happened, why, and what to do about it.

The first six come from chameleon-flask itself and arrive as [FlaskChameleonException](../reference/FlaskChameleonException.md#chameleon_flask.FlaskChameleonException). They all mean the library was set up or called wrongly, and they are quick to fix. Everything after that comes from Chameleon, Flask, or Python and passes through unchanged, because the library deliberately never wraps another library's errors.


# FlaskChameleonException: You must call global_init() before rendering templates.

A view rendered before anyone told the library where the templates are. This is the classic first-request error in a new project. Move [global_init()](../reference/global_init.md#chameleon_flask.global_init) to app startup, before the first request is served. In a test, add a fixture that initializes the test template folder, as shown in [Testing](testing.md).


# FlaskChameleonException: The template_folder must be specified.

[global_init()](../reference/global_init.md#chameleon_flask.global_init) was called with an empty string or `None`, usually from a setting that was never filled in. Pass the path to the templates folder, and build it from `__file__` so the working directory cannot change the answer:

``` python
template_folder = str(Path(__file__).resolve().parent / 'templates')
```


# FlaskChameleonException: The specified template folder must be a folder, it's not: …

The path exists in your head but not on disk, or it points at a file. Check the spelling and whether the path was meant to be absolute. The failed call did not initialize the engine, so once the path is right a plain retry works.


# FlaskChameleonException: Invalid return type \<class '…'\>, we expected a dict or flask.Response as the return value.

The view returned something other than a `dict` or a `Response`. The message names the type. The usual causes, in order:

- A string. Wrap the values in a dict instead: `return {'message': text}`.
- `None`, from a code path with no `return`, or from `return` on its own.
- A tuple like `({'a': 1}, 201)`. Flask accepts that shape, this decorator does not; put the status code on the decorator with `status_code=201`.
- A model object or a dataclass. Convert it: `return {'item': item}` or `return dataclasses.asdict(item)`.


# FlaskChameleonException: The template model cannot contain the key 'encoding'

The dict the view returned has a key named `encoding`. Chameleon reserves that name as an argument to its own render call, and the library passes `encoding='utf-8'` on every render, so the key can never reach the template. Rename it; `charset` or `text_encoding` both work. `translate` and `target_language` are Chameleon render options too, so avoid them as model keys as well.


# FlaskChameleonException: The view … returned an awaitable from a sync call path.

An `async def` view is hidden behind a sync decorator that does not use `functools.wraps`, so `@template` could not see that the view was async and installed the sync wrapper. Inside a Flask request the library serves the view anyway, so you see this on Quart, or when calling the view directly in a test. The library closed the stray coroutine and raised this instead of letting the framework fail less clearly. Add `@functools.wraps(f)` to your decorator's wrapper and keep `@template` directly under the route decorator, or make your decorator async. [Async views, Flask, and Quart](async-flask-and-quart.md) has the full table of which orders work where.


# TypeError: The view function did not return a valid response … but it was a coroutine.

This one is Flask's, and it only happens on Python 3.10 and 3.11. A sync decorator sits *outside* `@template` on an async view, so the function Flask registered is a plain function that returns a coroutine, and Flask does not await it. Move `@template` up so it is directly under the route decorator, with your own decorator beneath it, or make your decorator async. On Python 3.12 and newer the library hands Flask something it can run, and any order works.


# TypeError: The response value type (coroutine) is not valid

Quart's version of the previous entry. A sync decorator sits outside `@template` on an async view, so Quart ran it as a sync function and received an awaitable it does not know how to serve. Quart has no equivalent of Flask's callable-response path, so the fix is the rule: `@template` directly under the route decorator, your sync decorators beneath it with `functools.wraps`, or make your decorator async.


# RuntimeError: Install Flask with the 'async' extra in order to use async views.

Flask needs the `asgiref` package to run `async def` views and does not have it. This library depends on `flask[async]`, which includes it, so Flask was installed separately without the extra. Run `pip install 'flask[async]'`.


# ValueError: Template not found: home/index.pt.

Chameleon could not find the file under the templates folder. It is raised at the first render, not when the view is decorated. Work through these in order:

- The path is relative to the folder passed to [global_init()](../reference/global_init.md#chameleon_flask.global_init), not to the module holding the view and not to another template. From a view in `views/home.py`, the template is `home/index.pt`, not `index.pt` and not `templates/home/index.pt`.
- The bare decorator derived a name you did not expect. It uses the last segment of the module name and the function name, so `my_app.views.home.index` looks for `home/index.html`, then `home/index.pt`. Print `chameleon_flask.engine.template_path` to confirm which folder it is searching.
- The bare decorator ran before [global_init()](../reference/global_init.md#chameleon_flask.global_init), and so assumed a folder named `templates` relative to the working directory. Move [global_init()](../reference/global_init.md#chameleon_flask.global_init) above the view imports.
- The case does not match on Linux. `Index.pt` and `index.pt` are different files there, even though macOS and Windows would load either. This one tends to appear the first time the app runs in a container.
- The folder is not the one you think, because an earlier [global_init()](../reference/global_init.md#chameleon_flask.global_init) pointed somewhere else and the second call was ignored. See the next heading.


# A second global_init() is ignored, or templates come from the wrong folder

With the default `cache_init=True`, [global_init()](../reference/global_init.md#chameleon_flask.global_init) does nothing once a previous call has succeeded. In an app that is the behaviour you want. In a test suite, or a process that must switch folders, call [chameleon_flask.engine.clear()](../reference/engine.clear.md#chameleon_flask.engine.clear) first or pass `cache_init=False`. [Testing](testing.md) has the fixture.


# NameError: some_name

Chameleon went looking for a name in the template's model and found nothing. The message names the variable, and Chameleon's traceback shows the template file and the line. Either add the key to the dict the view returns, or give the template a fallback: `${some_name | 'default'}`. On a 404 page, remember the model is empty, so a METAL layout that needs `title` will raise exactly this.


# KeyError: 'Undefined namespace prefix: …'

A template uses an attribute Chameleon reads as namespaced, almost always Alpine.js or Vue shorthand like `@click`, `:class`, or `x-on:click`. Chameleon's restricted namespace mode rejects anything outside `tal:`, `metal:`, and `i18n:`. Pass `restricted_namespace=False` to [global_init()](../reference/global_init.md#chameleon_flask.global_init), as described in [Writing templates](writing-templates.md#alpine.js-vue-and-friends).


# TypeError: template() got an unexpected keyword argument 'mimetype'

The keyword is `content_type`. An early release called it `mimetype`, and the rename in 0.0.4 was a breaking change. Update the decorator call.


# The page shows JSON, or the raw dict

The route decorator and `@template` are in the wrong order. Flask registered the raw view, received a dict, and turned it into a JSON response, which is what Flask does with dicts. Put the route decorator outermost and `@template` directly above the function.


# Markup shows up as escaped text

The page displays `<div>` and friends literally. The value was inserted with plain `${...}` or `tal:content`, which escape everything. For a value that is already safe HTML, use the `structure:` prefix: `<div tal:content="structure: html"></div>` or `${structure: html}`. Only do this for HTML you generated or sanitized yourself.


# Edits to a template do not show up

You changed the file, refreshed, and nothing happened. Chameleon compiled the template once and is serving the compiled version. Initialize with `auto_reload=True` during development so it checks the file's timestamp on each render. In production, leave it `False` and restart after deploying template changes.


# The 404 page has the wrong content type or status

The 404 path always renders with `text/html` and status `404`; the `content_type` and `status_code` on the decorator apply to the successful render only. If a client needs a different 404 shape, return a `Response` from the view instead of calling [not_found()](../reference/not_found.md#chameleon_flask.not_found).


# not_found() produced a 500 instead of a 404

[not_found()](../reference/not_found.md#chameleon_flask.not_found) was called from a function that is not decorated with `@template`, so nothing caught the [FlaskChameleonNotFoundException](../reference/FlaskChameleonNotFoundException.md#chameleon_flask.FlaskChameleonNotFoundException) and Flask reported it as an unhandled error. Either decorate the view, or catch the exception yourself and render its `template_file` with [chameleon_flask.response()](../reference/response.md#chameleon_flask.response), as [Friendly 404s and error pages](friendly-404s.md) shows.
