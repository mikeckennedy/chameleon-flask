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

## Resources

- [Full documentation](https://mkennedy.codes/docs/chameleon-flask/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
