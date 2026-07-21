## End-to-end wiring

A complete, minimal app — engine init, a decorated view, and the template it renders. The `@template` path is always relative to the folder passed to `global_init()`.

```python
# app.py
from pathlib import Path
import flask
import chameleon_flask

app = flask.Flask(__name__)

# Init once at startup, BEFORE any decorated view is defined.
templates = Path(__file__).resolve().parent / 'templates'
chameleon_flask.global_init(str(templates), auto_reload=True)  # auto_reload for dev only


@app.get('/')
@chameleon_flask.template('home/index.pt')   # route decorator OUTERMOST, @template just above the function
def index():
    return {'title': 'Home', 'items': ['a', 'b', 'c']}   # dict == the template model
```

```html
<!-- templates/home/index.pt -->
<!DOCTYPE html>
<html lang="en">
<body>
  <h1>${title}</h1>
  <ul>
    <li tal:repeat="item items">${item}</li>
  </ul>
</body>
</html>
```

## Chameleon template syntax (this is TAL, not Jinja)

Chameleon templates are valid XML/HTML where directives live in `tal:`, `metal:`, and `i18n:` attributes. There is no `{% ... %}` or `{{ ... }}` — do not use Jinja/Django syntax. Interpolation uses `${ ... }` and may contain arbitrary Python expressions.

```html
<!-- Interpolation: any Python expression inside ${ } -->
<h1>Hello, ${user.name.title()}!</h1>
<p>You have ${len(items)} item(s).</p>

<!-- Loop -->
<li tal:repeat="item items">${item.name} — ${item.price}</li>

<!-- The repeat variable exposes index/number/even/odd/first/last -->
<li tal:repeat="item items" tal:attributes="class 'odd' if repeat.item.odd else 'even'">
  ${repeat.item.number}. ${item}
</li>

<!-- Condition (element is omitted entirely when falsy) -->
<div tal:condition="user">Welcome back, ${user.name}.</div>
<div tal:condition="not user">Please sign in.</div>

<!-- Set element content / replace whole element -->
<span tal:content="message">placeholder shown only in a browser preview</span>
<span tal:replace="formatted_date">2024-01-01</span>

<!-- Set attributes (semicolon-separated); escaping is automatic -->
<a tal:attributes="href item.url; class item.css_class">${item.name}</a>

<!-- Define a reusable local variable -->
<span tal:define="total sum(i.price for i in items)">Total: ${total}</span>
```

Escaping is on by default (`${expr}` is HTML-escaped). Use `structure:` to emit already-safe HTML without escaping: `<div tal:content="structure: raw_html"></div>`.

## Shared layouts with METAL macros

METAL is how Chameleon does template inheritance / partials — the equivalent of Jinja's `{% extends %}`/`{% block %}`.

```html
<!-- templates/shared/layout.pt -->
<html metal:define-macro="layout">
  <head><title>${title}</title></head>
  <body>
    <main metal:define-slot="content">default content</main>
  </body>
</html>
```

```html
<!-- templates/home/index.pt -->
<div metal:use-macro="load: ../shared/layout.pt">
  <div metal:fill-slot="content">
    <h1>${title}</h1>
  </div>
</div>
```

## Template resolution & project layout

With an explicit path (`@template('catalog/item.pt')`) the string is resolved relative to the `global_init()` folder. With the bare form (`@template` or `@template()`) the path is derived **once at decoration time** as `{last segment of module}/{function_name}.html`, falling back to `.pt` if the `.html` file does not exist on disk.

```
my_app/
├── app.py                 # global_init() here, before views are imported/defined
├── views/
│   └── home.py            # def index(...)  ->  bare @template looks for home/index.html|.pt
├── templates/
│   ├── home/index.pt
│   ├── errors/404.pt      # default target of not_found()
│   └── shared/layout.pt   # METAL macros
└── static/
```

## Flask and Quart

The same decorator API works for both frameworks and for both sync and async views — async is detected automatically, so no separate import or flag is needed. The library never imports Quart; it recognizes Quart responses through the shared werkzeug response base class.

```python
# Works identically whether app is flask.Flask(__name__) or quart.Quart(__name__)
@app.get('/')
@chameleon_flask.template('home/index.pt')
async def index():
    return {'items': await load_items()}
```

## Alpine.js / Vue shorthand in templates

`restricted_namespace=True` (the default) makes Chameleon reject non-TAL/METAL/i18n namespaced attributes, which includes Alpine.js/Vue shorthand like `@click`, `:class`, and `x-data`. Initialize with `restricted_namespace=False` to allow them, then use the shorthand normally in templates.

```python
chameleon_flask.global_init(str(templates), restricted_namespace=False)
```

```html
<div x-data="{ open: false }">
  <button @click="open = !open">Toggle</button>
  <div :class="{ hidden: !open }">Content</div>
</div>
```

## Fetching the docs as Markdown

Every page on the documentation site has a plain-Markdown twin: swap the `.html` extension for `.md` to get token-efficient source without the site chrome. For example https://mkennedy.codes/docs/chameleon-flask/reference/template.html is also available at https://mkennedy.codes/docs/chameleon-flask/reference/template.md. Prefer the `.md` form when reading these docs programmatically.
