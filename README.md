# chameleon-flask

[![PyPI version](https://img.shields.io/pypi/v/chameleon-flask.svg)](https://pypi.org/project/chameleon-flask/)
[![Python versions](https://img.shields.io/pypi/pyversions/chameleon-flask.svg)](https://pypi.org/project/chameleon-flask/)
[![License](https://img.shields.io/github/license/mikeckennedy/chameleon-flask.svg)](https://github.com/mikeckennedy/chameleon-flask/blob/main/LICENSE)

Adds integration of the Chameleon template language to Flask and Quart.

📖 **Documentation**: [mkennedy.codes/docs/chameleon-flask](https://mkennedy.codes/docs/chameleon-flask/)

This README is the short version. The user guide tells the whole story:

- [Getting started](https://mkennedy.codes/docs/chameleon-flask/user-guide/getting-started.html): install, point the engine at a folder, write a template, decorate a view.
- [Writing templates](https://mkennedy.codes/docs/chameleon-flask/user-guide/writing-templates.html): a Chameleon primer for people arriving from Jinja, METAL layouts included.
- [Decorating views](https://mkennedy.codes/docs/chameleon-flask/user-guide/decorating-views.html): the rulebook for `@template`, from return types to decorator order.
- [Friendly 404s and error pages](https://mkennedy.codes/docs/chameleon-flask/user-guide/friendly-404s.html) and [Async views, Flask, and Quart](https://mkennedy.codes/docs/chameleon-flask/user-guide/async-flask-and-quart.html), with the table of which decorator orders work on async views.
- [Testing](https://mkennedy.codes/docs/chameleon-flask/user-guide/testing.html), [Troubleshooting](https://mkennedy.codes/docs/chameleon-flask/user-guide/troubleshooting.html), [How it works](https://mkennedy.codes/docs/chameleon-flask/user-guide/how-it-works.html), and the [FAQ](https://mkennedy.codes/docs/chameleon-flask/user-guide/faq.html).
- [API reference](https://mkennedy.codes/docs/chameleon-flask/reference/).

## The whole library in one view

Here is a complete chameleon-flask view, the kind you will write dozens of:

```python
@app.get('/catalog/item/<int:item_id>')
@chameleon_flask.template('catalog/item.pt')
def item(item_id: int):
    item = service.get_item_by_id(item_id)
    if not item:
        chameleon_flask.not_found()

    return {'item': item}
```

Read it top to bottom. The function asks the database for an item and hands back a plain
`dict`. It never calls a render function, never constructs a `Response`, never mentions a
status code. The decorator takes that dict, pours it into `catalog/item.pt`, and returns a
finished `flask.Response`. When the lookup comes up empty, one call swaps the page for your
404 template. Views return data; the decorator turns data into HTML. That split is the whole
library, and everything below is detail.

The template on the other side of that decorator is an HTML document first:

```html
<h1>${item.name}</h1>
<p tal:condition="item.on_sale">On sale: ${item.price}</p>
<ul>
    <li tal:repeat="tag item.tags">${tag}</li>
</ul>
```

Chameleon is the template language from the Pyramid and Zope world. Its directives live in
`tal:` attributes, values drop in through `${...}`, and the expression inside the braces is
ordinary Python. There is no second syntax of `{% %}` blocks layered over the markup, so the
file stays valid HTML that a browser, an editor, or a designer can open as-is. Chameleon
compiles each template to Python bytecode the first time it renders, so none of this costs
you speed. This library started life as a fork of its sibling,
[fastapi-chameleon](https://github.com/mikeckennedy/fastapi-chameleon), and brings the same
shape to Flask and Quart.

## Installation

```bash
pip install chameleon_flask
```

Or `uv add chameleon-flask`. Python 3.10 or newer. The only runtime dependencies are
`flask[async]` and `Chameleon`, and the `[async]` extra is what lets Flask run the async views
shown below.

## Setting up

Create a folder in your web app to hold the templates. Any layout works; this one groups
templates by the view module that renders them, which pays off later with default template
names:

```
├── app.py
├── views.py
│
├── templates
│   ├── home
│   │   └── index.pt
│   └── shared
│       └── layout.pt

```

At app startup, tell the library where that folder is:

```python
from pathlib import Path
import chameleon_flask

dev_mode = True

BASE_DIR = Path(__file__).resolve().parent
template_folder = str(BASE_DIR / 'templates')
chameleon_flask.global_init(template_folder, auto_reload=dev_mode)
```

`global_init()` builds one Chameleon template loader for the whole process. Do this once,
before you define your views. The call is deliberately one-shot: a second `global_init()`
buried in some module is ignored rather than swapping your template folder out from under
you (pass `cache_init=False` if you really do mean it).

`auto_reload` deserves its own sentence. With it on, Chameleon re-reads a template whenever
its file changes, which is exactly what you want while you are editing templates and exactly
what you don't want in production, where the compiled templates should stay cached. Tie it to
your dev-mode flag and forget about it.

## Decorating views

Decorate the Flask or Quart view and return a `dict`. The keys become the variables your
template sees:

```python
@app.get('/')
@chameleon_flask.template('home/index.pt')
def index():
    return {'message': 'Hello world'}
```

Async views need no special treatment. The decorator notices the `async def` and awaits it:

```python
@app.get('/async')
@chameleon_flask.template('async.pt')
async def async_world():
    await asyncio.sleep(.01)
    return {'message': "Let's go async Chameleon!"}
```

Sometimes a view decides, partway through, that this request is not getting the page at all.
Return a `flask.Response` and the template is skipped; the response, its status code and its
headers pass straight through. Redirects are the everyday case:

```python
@app.get('/account')
@chameleon_flask.template('account/index.pt')
def account():
    user = current_user()
    if not user:
        return flask.redirect('/login')  # A Response: passed through, template never runs.

    return {'user': user}
```

Return anything other than a `dict` or a `Response` and you get a `FlaskChameleonException`
naming the type, rather than a mysterious 500.

Everything works the same on a Quart app. Decorate your async Quart views and return a dict
or a `quart.Response`. The library never imports Quart; it recognizes Quart responses through
the werkzeug base class the two frameworks share.

## Content type and status code

Templates are not only for HTML pages. Set the content type and the default status code right
on the decorator, and the same machinery serves XML, text, or a `201 Created` after a POST:

```python
@app.get('/xml')
@chameleon_flask.template('sample.xml', content_type='application/xml', status_code=201)
def xml_response():
    return {'items': ['pyramid', 'flask', 'fastapi']}
```

## Default template names

If you name templates after the views that render them, you can stop naming them at all. Use
the decorator bare and the template file is derived from the view: a function `index` in
`views.py` maps to `{template_folder}/views/index.html`, falling back to `views/index.pt` if
no `.html` file exists.

```python
@app.get('/')
@chameleon_flask.template
def index():
    return {'message': 'Hello world'}  # renders templates/views/index.pt
```

The name is resolved once, when the view is decorated, so call `global_init()` before
defining views when you rely on this form.

## Friendly 404s

Every catalog has a missing item. A thoughtful site answers a request for it with a
[real 404 page](http://www.instantshift.com/2019/10/16/user-friendly-404-pages/) in the site's
own look, with navigation and a way back, rather than the framework's bare error text. Call
`chameleon_flask.not_found()` at the point where the lookup fails and stop worrying about the
rest of the function:

```python
@app.get('/catalog/item/<int:item_id>')
@chameleon_flask.template('catalog/item.pt')
def item(item_id: int):
    item = service.get_item_by_id(item_id)
    if not item:
        chameleon_flask.not_found()

    return {'item': item}
```

The decorator catches the exception that `not_found()` raises and renders
`templates/errors/404.pt` with status code 404. Pass a different template path to
`not_found()` if one page should have its own flavor of missing, but you don't have to.

## Alpine.js, Vue, and friends

Chameleon is strict about attributes by default: anything outside its own TAL/METAL/i18n
namespaces is rejected. That strictness collides head-on with attribute-based JavaScript
frameworks, whose whole idiom is shorthand attributes like `@click`, `:class`, and `x-data`.
Pass `restricted_namespace=False` and Chameleon lets them through unchanged:

```python
chameleon_flask.global_init(
    template_folder,
    auto_reload=dev_mode,
    restricted_namespace=False,  # Enable Alpine.js / Vue-style attributes
)
```

## Rendering without the decorator

The decorator can't reach everywhere. Error handlers, for instance, are registered with Flask
directly, and sometimes you want the rendered HTML as a string for an email or a JSON payload.
Both are a single call:

```python
import chameleon_flask

@app.errorhandler(500)
def server_error(e):
    return chameleon_flask.response('errors/500.pt', status_code=500)

# Or get the raw HTML as a string:
html = chameleon_flask.engine.render('home/index.pt', message='Hi')
```

See the full [API reference](https://mkennedy.codes/docs/chameleon-flask/reference/) for
every function, parameter, and exception.

## The small print

A few things are worth knowing before they find you:

- **Decorator order matters.** Put the route decorator outermost and `@template` directly
  above the function. The route has to register the wrapper that produces a `Response`, not
  the raw view that returns a dict.
- **Names are resolved at decoration time.** The bare `@template` form looks up its template
  file when your module is imported. If `global_init()` hasn't run yet, it assumes a folder
  named `templates` relative to the working directory.
- **An async view behind another decorator.** On Flask with Python 3.12 or newer, stack your
  decorators in any order; the library hands Flask something it can run either way. On Quart,
  and on older Pythons, keep `@template` directly under the route and put your sync decorators
  beneath it with `functools.wraps`, or make them async.
- **`encoding` is a reserved key.** Chameleon takes it as a render argument, so a model
  containing `encoding` is rejected with a clear `FlaskChameleonException` instead of a
  confusing traceback. Rename the key.
- **It's `content_type`, not `mimetype`.** The decorator keyword was renamed in an earlier
  release.

## An example

[example/example_app.py](https://github.com/mikeckennedy/chameleon-flask/blob/main/example/example_app.py)
is a small, runnable Flask app that exercises everything on this page: a sync view, an async
view, an XML response with a `201` status, and a catalog where item `99` does not exist and
shows the friendly 404. Run it with `python example/example_app.py` and visit
http://127.0.0.1:5555.

Coding agents can load the [agent skill](https://mkennedy.codes/docs/chameleon-flask/skill.md)
or read [llms-full.txt](https://mkennedy.codes/docs/chameleon-flask/llms-full.txt), which
also cover Chameleon's TAL syntax and METAL layouts.
