# User Guide

A Flask view, at its best, is a short function that fetches some data and hands it to a template. Flask ships with Jinja for that job, and for most people Jinja is where the story ends. This library is for the people who have seen Chameleon and want it in their Flask or Quart app.

Chameleon is the template language from the Pyramid and Zope world. Its templates are HTML documents first: the logic lives in `tal:` attributes on ordinary elements, values drop in through `${...}`, and the expression inside the braces is plain Python. There is no second syntax of `{% %}` blocks layered over the markup, so a `.pt` file opens in a browser and still looks like the page it will become. Chameleon compiles each template to Python bytecode the first time it renders, so none of that costs you speed.

chameleon-flask is the glue. It adds one decorator that turns this:

``` python
@app.get('/catalog/item/<int:item_id>')
@chameleon_flask.template('catalog/item.pt')
def item(item_id: int):
    item = service.get_item_by_id(item_id)
    if not item:
        chameleon_flask.not_found()

    return {'item': item}
```

into a finished `flask.Response`. The view returns a plain `dict`, the decorator pours it into the template, and when the lookup comes up empty one call swaps the page for your 404 template. Views return data; the decorator turns data into HTML. That split is the whole library, and this guide is the long version of it.


# Where to go next

- [Getting started](getting-started.md) takes an app from `pip install` to a rendered page in four moves: install, point the engine at a folder, write a template, decorate a view.
- [Writing templates](writing-templates.md) is a Chameleon primer for people arriving from Jinja: interpolation, loops, conditions, attributes, METAL layouts, and the switch that lets Alpine.js and Vue attributes through.
- [Decorating views](decorating-views.md) is the rulebook for `@template`: what a view may return, how bare `@template` finds its file, content types and status codes, and the one rule about decorator order.
- [Friendly 404s and error pages](friendly-404s.md) covers [not_found()](../reference/not_found.md#chameleon_flask.not_found), custom 404 templates, and rendering error pages from Flask's own error handlers.
- [Async views, Flask, and Quart](async-flask-and-quart.md) explains how async views are detected, why decorator order no longer matters on Flask, the one rule that still applies on Quart, and when to turn `auto_reload` off.
- [Testing](testing.md) shows that decorated views are plain functions, which makes them pleasant to test once you know about the one-shot engine.
- [Troubleshooting](troubleshooting.md) is a field guide to every error the library, Chameleon, or Flask raises in normal use. Each heading is the message you will see.
- [How it works](how-it-works.md) walks through the one module that does everything, for when you want to know rather than trust.
- [FAQ](faq.md) has the short answers: Jinja side by side, partials, HTMX, FastAPI, and friends.
- The [API reference](../reference/index.md) holds every public name with its full docstring.

The [example app](https://github.com/mikeckennedy/chameleon-flask/tree/main/example) in the repository is small enough to read in one sitting and exercises everything in this guide: a sync view, an async view, an XML response with a `201` status, and a catalog where item `99` does not exist and shows the friendly 404. Run it with `python example/example_app.py` and visit http://127.0.0.1:5555.
