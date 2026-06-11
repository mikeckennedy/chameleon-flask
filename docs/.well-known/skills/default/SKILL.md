---
name: chameleon-flask
description: >
  Adds integration of the Chameleon template language to Flask and Quart. Use when writing Python code that uses the chameleon_flask package.
license: MIT
compatibility: Requires Python >=3.10.
---

# chameleon-flask

Adds integration of the Chameleon template language to Flask and Quart.

## Installation

```bash
pip install chameleon-flask
```

## When to use what

| Need | Use |
|------|-----|
| Render a Chameleon template from a Flask/Quart view | `@chameleon_flask.template('home/index.pt') on the view function` |
| Return a friendly 404 page from a view | `chameleon_flask.not_found()` |
| Build a rendered Response outside a decorated view | `chameleon_flask.response(template_file, **model)` |
| Get rendered HTML as a plain string | `chameleon_flask.engine.render(template_file, **model)` |
| Use Alpine.js/Vue shorthand attributes in templates | `global_init(..., restricted_namespace=False)` |

## API overview

### Configuration

Set up the Chameleon template engine once at app startup.

- `global_init`: Initialize the Chameleon template engine
- `engine.clear`

### Decorating views

Render templates from Flask/Quart view functions (sync or async) and return friendly 404s.

- `template`: Decorate a Flask or Quart view method to render a Chameleon template
- `not_found`: Abort the current view and render a friendly 404 page

### Direct rendering

Render a template to a Response or raw HTML without the decorator.

- `response`: Render a Chameleon template directly to a `flask.Response`
- `engine.render`

### Exceptions

Errors raised by the engine. Importable from `chameleon_flask` directly or from `chameleon_flask.exceptions`.

- `FlaskChameleonException`: Base exception for all chameleon-flask errors
- `FlaskChameleonNotFoundException`: Raised by `not_found()` to signal that a view should render a 404 page

## Gotchas

1. global_init() is one-shot by default: with cache_init=True, later calls are silently ignored. Pass cache_init=False or call chameleon_flask.engine.clear() to re-initialize.
2. The bare @template form resolves the template file name once, at decoration time — call global_init() before defining views that rely on it.
3. Decorated views must return a dict (the template model) or a Flask/Quart Response; any other return type raises FlaskChameleonException at request time.
4. Chameleon's restricted namespace (the default) rejects Alpine.js/Vue shorthand attributes like @click, :class, and x-data. Pass restricted_namespace=False to global_init() to allow them.
5. The 404 path from not_found() always renders with text/html and status 404; the view's own content_type and status_code do not apply.
6. The decorator keyword is content_type, not mimetype (renamed in an earlier release).

## Best practices

- Call global_init(template_folder, auto_reload=dev_mode) exactly once at app startup, before any views are defined.
- Return plain dicts from views; return a Response only for redirects and other pass-through cases.
- Enable auto_reload only during development so templates stay cached in production.
- Use chameleon_flask.response() inside error handlers and other spots where the decorator doesn't fit.

## Resources

- [Full documentation](https://mkennedy.codes/docs/chameleon-flask/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
