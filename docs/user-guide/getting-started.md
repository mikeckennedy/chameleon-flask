# Getting started

This page takes a Flask app from nothing to a rendered Chameleon page in four moves. Everything here works the same on Quart; the differences, which are few, get their own page in [Async views, Flask, and Quart](async-flask-and-quart.md).


# Move one: install

``` bash
uv add chameleon-flask
# or
pip install chameleon_flask
```

Hyphen or underscore, PyPI accepts both spellings of the name. The import is always `chameleon_flask` with an underscore. Python 3.10 or newer is required, and the only runtime dependencies are `flask[async]` and `Chameleon`. The `[async]` extra pulls in the small `asgiref` package that lets Flask run `async def` views; you get it whether or not you ever write one.


# Move two: point the engine at a folder

Create a folder for your templates. Any layout works, but grouping templates by the view module that renders them pays off later, when you let the decorator derive template names on its own:

``` text
my_app/
├── app.py
├── views/
│   └── home.py
└── templates/
    ├── home/
    │   └── index.pt
    ├── errors/
    │   └── 404.pt
    └── shared/
        └── layout.pt
```

At startup, tell the library where that folder is:

``` python
# app.py
from pathlib import Path

import flask

import chameleon_flask

dev_mode = True

app = flask.Flask(__name__)
template_folder = str(Path(__file__).resolve().parent / 'templates')
chameleon_flask.global_init(template_folder, auto_reload=dev_mode)
```

Build the path from `__file__` rather than a relative string, so the app works no matter which directory it was launched from. [global_init()](../reference/global_init.md#chameleon_flask.global_init) creates one Chameleon template loader for the whole process; every decorated view in the app uses it from then on.

Two properties of this call matter from day one. It is one-shot: once it has succeeded, calling it again does nothing, so a stray second [global_init()](../reference/global_init.md#chameleon_flask.global_init) cannot swap your template folder out from under you. And it should run before you define your views. The bare form of the decorator, the one without a template path, works out its template file at the moment the view is decorated, and it needs to know the folder to do that. In practice: call [global_init()](../reference/global_init.md#chameleon_flask.global_init) in `app.py` before you import the modules that hold your views.

`auto_reload` deserves its own sentence. With it on, Chameleon re-reads a template whenever its file changes, which is exactly what you want while editing templates and exactly what you don't want in production, where compiled templates should stay cached. Tie it to your dev-mode flag and forget about it.


# Move three: write a template

A Chameleon template is an HTML file. Here is the home page, with a loop and an expression:

``` html
<!-- templates/home/index.pt -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>${title}</title>
</head>
<body>
<h1>${title}</h1>
<p>You have ${len(videos)} video(s).</p>
<ul>
    <li tal:repeat="video videos">${video.title} by ${video.author}</li>
</ul>
</body>
</html>
```

Three things are going on, and they are most of Chameleon. `${title}` inserts a value from the model, HTML-escaped. `${len(videos)}` shows that the expression inside the braces is ordinary Python. And `tal:repeat="video videos"` repeats the `<li>` once per item, binding each to `video` for the element's contents. Strip the `tal:` attribute and the braces and you have exactly the HTML a designer would hand you, which is the point. [Writing templates](writing-templates.md) covers the rest of the language.

The `.pt` extension is the Chameleon convention and the one this guide uses. Plain `.html` works too, and the bare decorator form described below checks for `.html` first.


# Move four: decorate a view

Decorate the view with the template path, relative to the folder from move two, and return a `dict`:

``` python
# views/home.py
import flask

import chameleon_flask

bp = flask.Blueprint('home', __name__)


@bp.get('/')
@chameleon_flask.template('home/index.pt')
def index():
    videos = video_service.latest(10)
    return {'title': 'Latest videos', 'videos': videos}
```

Register the blueprint in `app.py`, after [global_init()](../reference/global_init.md#chameleon_flask.global_init), and run the app. The keys of the returned dict are the names the template sees: `title` and `videos`, nothing more and nothing less. The decorator renders the template with that model and returns a `flask.Response` with a `200` status and a `text/html` content type.

The decorator order matters in one respect: the route decorator goes outermost, `@chameleon_flask.template` directly under it. Flask registers whatever the route decorator receives, and that has to be the wrapper that produces a `Response`, not the raw view that returns a dict.


# What you have now

Four moves, and the app renders Chameleon. From here the paths fork. If the template language is new to you, read [Writing templates](writing-templates.md) next. If you know Chameleon from Pyramid and want the rules of the decorator, go to [Decorating views](decorating-views.md). And the [example app](https://github.com/mikeckennedy/chameleon-flask/tree/main/example) in the repository is these four moves plus a 404 page and an XML response, in two files you can run right now.
