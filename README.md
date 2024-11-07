# chameleon-flask

Adds integration of the Chameleon template language to Flask and Quart. 

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
import os
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

## Friendly 404s and errors

A common technique for user-friendly sites is to use a [custom HTML page for 404 responses](http://www.instantshift.com/2019/10/16/user-friendly-404-pages/).
This library has support for friendly 404 pages using the `chameleon_flask.not_found()` function.

Here's an example:

```python
@app.get('/catalog/item/{item_id}')
@chameleon_flask.template('catalog/item.pt')
async def item(item_id: int):
    item = service.get_item_by_id(item_id)
    if not item:
        chameleon_flask.not_found()
    
    return item.dict()
```

This will render a 404 response with using the template file `templates/errors/404.pt`.
You can specify another template to use for the response, but it's not required.

## An example

See the `example/example_app.py` file for a working example to play with.

