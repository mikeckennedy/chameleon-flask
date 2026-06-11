# chameleon-flask

[![PyPI version](https://img.shields.io/pypi/v/chameleon-flask.svg)](https://pypi.org/project/chameleon-flask/)
[![Python versions](https://img.shields.io/pypi/pyversions/chameleon-flask.svg)](https://pypi.org/project/chameleon-flask/)
[![License](https://img.shields.io/github/license/mikeckennedy/chameleon-flask.svg)](https://github.com/mikeckennedy/chameleon-flask/blob/main/LICENSE)

Adds integration of the Chameleon template language to Flask and Quart.

📖 **Documentation**: [mkennedy.codes/docs/chameleon-flask](https://mkennedy.codes/docs/chameleon-flask/)

## Installation

Simply `pip install chameleon_flask`.

## Usage

This is easy to use. Just create a folder within your web app to hold the templates such as:

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

In the app startup, tell the library about the folder you wish to use:

```python
from pathlib import Path
import chameleon_flask

dev_mode = True

BASE_DIR = Path(__file__).resolve().parent
template_folder = str(BASE_DIR / 'templates')
chameleon_flask.global_init(template_folder, auto_reload=dev_mode)
```

Then just decorate the Flask or Quart view methods (works on sync and async methods):

```python
@app.get('/async')
@chameleon_flask.template('async.pt')
async def async_world():
    await asyncio.sleep(.01)
    return {'message': "Let's go async Chameleon!"}
```

The view method should return a `dict` to be passed as variables/values to the template.

If a `flask.Response` is returned, the template is skipped and the response along with status_code and
other values is directly passed through. This is common for redirects and error responses not meant
for this page template. Otherwise the dictionary is used to render `async.pt` in this example.

Everything works the same on a Quart app — decorate your async Quart views and return a
dict or a `quart.Response`.

You can also control the response's content type and default status code right on the decorator:

```python
@app.get('/xml')
@chameleon_flask.template('sample.xml', content_type='application/xml', status_code=201)
def xml_response():
    return {'items': ['pyramid', 'flask', 'fastapi']}
```

## Default template names

Use the decorator bare and the template file is derived from the view: a function `index`
in `views.py` maps to `{template_folder}/views/index.html`, falling back to
`views/index.pt` if no `.html` file exists. The name is resolved when the view is
decorated, so call `global_init()` before defining views when you rely on this form.

```python
@app.get('/')
@chameleon_flask.template
def index():
    return {'message': 'Hello world'}  # renders templates/views/index.pt
```

## Friendly 404s and errors

A common technique for user-friendly sites is to use a [custom HTML page for 404 responses](http://www.instantshift.com/2019/10/16/user-friendly-404-pages/).
This library has support for friendly 404 pages using the `chameleon_flask.not_found()` function.

Here's an example:

```python
@app.get('/catalog/item/<int:item_id>')
@chameleon_flask.template('catalog/item.pt')
def item(item_id: int):
    item = service.get_item_by_id(item_id)
    if not item:
        chameleon_flask.not_found()

    return {'item': item}
```

This will render a 404 response using the template file `templates/errors/404.pt`.
You can specify another template to use for the response, but it's not required.

## Alpine.js, Vue, and friends

By default, Chameleon rejects attributes outside its own TAL/METAL/i18n namespaces, which
breaks the shorthand syntax used by attribute-based JavaScript frameworks (`@click`, `:class`,
`x-data`, and so on). Pass `restricted_namespace=False` to allow them through unchanged:

```python
chameleon_flask.global_init(
    template_folder,
    auto_reload=dev_mode,
    restricted_namespace=False,  # Enable Alpine.js / Vue-style attributes
)
```

## Rendering without the decorator

For error handlers and other spots where the decorator doesn't fit, render directly:

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

## An example

See [example/example_app.py](https://github.com/mikeckennedy/chameleon-flask/blob/main/example/example_app.py)
for a working example to play with.
