# Decorating views

`@template` is the decorator the library is built around, and it has a small number of rules. Most of them exist because someone, usually the author, got them wrong once. Here they are in the order you are likely to meet them.


# Rule one: return a dict, or a Response, and nothing else

A decorated view returns one of two things. A `dict` becomes the template's model, each key a name the template can use:

``` python
@app.get('/')
@chameleon_flask.template('home/index.pt')
def index():
    return {'title': 'Home', 'videos': video_service.latest(10)}
```

Or a Flask or Quart `Response`, which is passed straight through. The template never runs, and the response's status code and headers survive untouched. Redirects are the everyday case:

``` python
@app.get('/account')
@chameleon_flask.template('account/index.pt')
def account():
    user = current_user()
    if not user:
        return flask.redirect('/login')  # A Response: passed through, template never runs.

    return {'user': user}
```

Anything else, a string, a tuple, a list, `None` from a forgotten `return`, raises a [FlaskChameleonException](../reference/FlaskChameleonException.md#chameleon_flask.FlaskChameleonException) that names the type you returned. The library is deliberately strict here. Flask would happily turn a string into a response, but a string from a `@template` view is almost always a mistake, and a clear error beats a page that says `{'title': 'Home'}`.

Pass-through detection works on the `werkzeug` base class that `flask.Response`, `quart.Response`, and any subclass of either share, so your own `Response` subclasses pass through too.


# Rule two: paths are relative to the templates folder

The string you give the decorator is resolved against the folder passed to [global_init()](../reference/global_init.md#chameleon_flask.global_init), never against the module that holds the view:

``` python
@chameleon_flask.template('catalog/item.pt')   # -> templates/catalog/item.pt
```

Chameleon's own `load:` expressions, used for METAL layouts, are relative to the template file instead. Both conventions live in the same project, so it is worth saying out loud: the decorator thinks like the folder, `load:` thinks like a file.

A path that does not exist is not caught when the view is decorated. It surfaces at the first request, as Chameleon's `ValueError: Template not found`. [Testing](testing.md) shows the three-line test that catches it before a user does.


# Rule three: the bare form derives the name from the view

If you name templates after the views that render them, you can stop naming them at all. Use the decorator bare, with or without parentheses, and the template file is derived from the view:

``` python
# views/account.py
@bp.get('/')
@chameleon_flask.template
def index():
    return {'user': current_user()}     # renders templates/account/index.html, or .pt
```

The rule is `{last segment of the module name}/{function name}`, so a view named `index` in a module `my_app.views.account` maps to `account/index`. The library looks for `account/index.html` on disk first and falls back to `account/index.pt` if the `.html` file does not exist.

The name is resolved once, at decoration time, when Python imports the module. That has one consequence: [global_init()](../reference/global_init.md#chameleon_flask.global_init) must have run before the module that holds the view is imported. If it has not, the decorator assumes a folder named `templates` relative to the working directory, which is the wrong folder for almost everyone. Call [global_init()](../reference/global_init.md#chameleon_flask.global_init) in your app module before you import your views, and the bare form never surprises you.


# Rule four: content type and status code live on the decorator

Templates are not only for HTML pages. The decorator takes the content type and the default status code, and the same machinery serves XML, text, or a `201 Created` after a POST:

``` python
@app.get('/feed.xml')
@chameleon_flask.template('feed/items.xml', content_type='application/xml')
def feed():
    return {'items': video_service.latest(50)}


@app.post('/videos')
@chameleon_flask.template('videos/created.pt', status_code=201)
def create_video():
    video = video_service.create(flask.request.form)
    return {'video': video}
```

The keyword is `content_type`. An early release called it `mimetype`, and that spelling was removed in 0.0.4, so if an old snippet raises `TypeError: unexpected keyword argument 'mimetype'`, that is why.

These two settings apply to the template path only. A `Response` you return yourself keeps its own values, and the 404 path described in [Friendly 404s and error pages](friendly-404s.md) always uses `text/html` and `404`.


# Rule five: the route decorator goes outermost

``` python
@app.get('/')                          # 1. outermost: registers the function with Flask
@chameleon_flask.template('home/index.pt')   # 2. turns a dict into a Response
def index():                           # 3. returns the dict
    ...
```

Flask registers whatever the route decorator receives, and it has to receive the wrapper that produces a `Response`. Swap the two and Flask registers the raw view, gets a `dict` back, and renders it as JSON, because Flask treats a returned dict as a JSON response. That is a confusing afternoon.

Your own decorators go between `@template` and the function, and for sync views any decorator works there. Async views have more history: on Flask with Python 3.12 or newer any arrangement works, while Quart and older Pythons need your sync decorators beneath `@template` and using `functools.wraps`. [Async views, Flask, and Quart](async-flask-and-quart.md) has the full table.


# Blueprints

Nothing changes. The engine is process-wide, so a blueprint's views decorate exactly like the app's own, and the bare form uses the blueprint module's name just as you would hope:

``` python
# views/catalog.py
bp = flask.Blueprint('catalog', __name__, url_prefix='/catalog')


@bp.get('/item/<int:item_id>')
@chameleon_flask.template            # -> templates/catalog/item.pt
def item(item_id: int):
    item = service.get_item_by_id(item_id)
    if not item:
        chameleon_flask.not_found()

    return {'item': item}
```

Register the blueprint after [global_init()](../reference/global_init.md#chameleon_flask.global_init) has run, which in a normal app means [global_init()](../reference/global_init.md#chameleon_flask.global_init) sits above the blueprint imports in `app.py`.


# Rendering without the decorator

The decorator cannot reach everywhere. Flask's error handlers are registered directly, and sometimes you want the HTML as a string for an email body or a JSON payload. Two functions cover those cases.

[chameleon_flask.response()](../reference/response.md#chameleon_flask.response) renders a template straight to a `flask.Response`, with the same `content_type` and `status_code` arguments as the decorator:

``` python
@app.errorhandler(500)
def server_error(e):
    return chameleon_flask.response('errors/500.pt', status_code=500)
```

[chameleon_flask.engine.render()](../reference/engine.render.md#chameleon_flask.engine.render) is the bottom rung of the ladder: a model goes in, a string comes out:

``` python
html = chameleon_flask.engine.render('email/welcome.pt', user=user)
mailer.send(user.email, subject='Welcome', html=html)
```

It lives on the `engine` module rather than the package root because most apps never need it, but it is a public, documented function.


# A layout for the templates folder

The library has no opinion about folder structure, but the one the bare decorator rewards has held up well: one folder per view module, errors in their own folder, and the METAL layouts somewhere shared:

``` text
templates/
├── account/
│   ├── index.pt
│   └── settings.pt
├── catalog/
│   └── item.pt
├── errors/
│   ├── 404.pt
│   └── 500.pt
├── home/
│   └── index.pt
└── shared/
    └── layout.pt
```
