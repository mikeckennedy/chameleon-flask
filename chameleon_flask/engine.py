"""The chameleon-flask template engine.

Holds the process-global Chameleon `PageTemplateLoader` along with the functions and the
`@template` decorator that render templates from Flask and Quart views. Initialize the
engine once at app startup with `global_init()`; everything else builds on that loader.
"""

import inspect
import os
from collections.abc import Callable
from functools import wraps
from typing import Any, NoReturn, cast

import flask
import werkzeug.sansio.response
from chameleon import PageTemplate, PageTemplateLoader

from chameleon_flask.exceptions import FlaskChameleonException, FlaskChameleonNotFoundException

__templates: PageTemplateLoader | None = None
template_path: str | None = None

# Fallback name matching for Response implementations that predate the shared werkzeug base class.
response_classes = {
    "<class 'flask.wrappers.Response'>",
    "<class 'quart.wrappers.response.Response'>",
    "<class 'flask.Response'>",
    "<class 'quart.response.Response'>",
    "<class 'quart.Response'>",
}


def global_init(
    template_folder: str, auto_reload: bool = False, cache_init: bool = True, restricted_namespace: bool = True
) -> None:
    """
    Initialize the Chameleon template engine.

    Call this once at app startup, before any decorated view is defined or runs. With
    `cache_init=True` (the default), later calls are silently ignored once the engine is
    initialized; pass `cache_init=False` (or call `chameleon_flask.engine.clear()`) to
    re-initialize with different settings.

    Args:
        template_folder: Path to the template directory.
        auto_reload: Whether to auto-reload templates on change (handy in dev mode).
        cache_init: If True, do nothing when the engine is already initialized.
        restricted_namespace: If True, only TAL/METAL/i18n namespaces are allowed.
            If False, allows attribute-based JS frameworks like Alpine.js
            to use shorthand syntax (@click, :class, etc.)

    Raises:
        FlaskChameleonException: If `template_folder` is empty or is not a directory.

    Examples:
        ```python
        from pathlib import Path
        import chameleon_flask

        dev_mode = True
        folder = Path(__file__).resolve().parent / 'templates'
        chameleon_flask.global_init(str(folder), auto_reload=dev_mode)
        ```
    """
    global __templates, template_path

    if __templates and cache_init:
        return

    if not template_folder:
        msg = 'The template_folder must be specified.'
        raise FlaskChameleonException(msg)

    if not os.path.isdir(template_folder):
        msg = f"The specified template folder must be a folder, it's not: {template_folder}"
        raise FlaskChameleonException(msg)

    template_path = template_folder
    __templates = PageTemplateLoader(
        template_folder,
        auto_reload=auto_reload,
        restricted_namespace=restricted_namespace,
    )


def clear() -> None:
    """
    Reset the template engine to its uninitialized state.

    Forgets the cached template loader and template folder so a later `global_init()`
    call can re-initialize the engine with different settings. Mostly useful in tests.
    """
    global __templates, template_path
    __templates = None
    template_path = None


def render(template_file: str, **template_data: Any) -> str:
    """
    Render a Chameleon template to an HTML string.

    Args:
        template_file: The Chameleon template file (path relative to the template folder).
        **template_data: Values passed to the template as the model.

    Returns:
        The rendered HTML as a string.

    Raises:
        FlaskChameleonException: If `global_init()` has not been called yet.
    """
    if not __templates:
        raise FlaskChameleonException('You must call global_init() before rendering templates.')

    page: PageTemplate = __templates[template_file]
    return page.render(encoding='utf-8', **template_data)


def response(
    template_file: str, content_type: str = 'text/html', status_code: int = 200, **template_data: Any
) -> flask.Response:
    """
    Render a Chameleon template directly to a `flask.Response`.

    Useful when you want a rendered response without the `@template` decorator, for
    example inside error handlers or conditional branches.

    Args:
        template_file: The Chameleon template file (path relative to the template folder).
        content_type: The content type of the response (defaults to `text/html`).
        status_code: The HTTP status code of the response (defaults to 200).
        **template_data: Values passed to the template as the model.

    Returns:
        The rendered `flask.Response`.

    Raises:
        FlaskChameleonException: If `global_init()` has not been called yet.

    Examples:
        ```python
        @app.errorhandler(500)
        def server_error(e):
            return chameleon_flask.response('errors/500.pt', status_code=500)
        ```
    """
    html = render(template_file, **template_data)
    return flask.Response(response=html, content_type=content_type, status=status_code)


def template(
    template_file: Callable[..., Any] | str | None = None, content_type: str = 'text/html', status_code: int = 200
) -> Callable[..., Any]:
    """
    Decorate a Flask or Quart view method to render a Chameleon template.

    Works on both sync and async views, bare (`@template`) or with arguments
    (`@template('home/index.pt')`). When used bare, the template file is derived from
    the view as `{module}/{function_name}.html`, falling back to `.pt` when no `.html`
    file exists in the template folder.

    The decorated view must return either a `dict` (passed to the template as the
    model) or a Flask/Quart `Response` (passed through untouched, e.g. for redirects).

    Note that the template file name is resolved once, when the view is decorated, not
    per request. When relying on the bare form, call `global_init()` before defining
    your views; otherwise the `.html`-or-`.pt` check assumes a folder named `templates`
    relative to the working directory.

    Args:
        template_file: Optional, the Chameleon template file (path relative to the
            template folder, e.g. `home/index.pt`). Derived from the view when omitted.
        content_type: The content type of the response (defaults to `text/html`).
        status_code: Default status code for responses. For example 201 on a POST/create action.

    Returns:
        The decorator to be consumed by Flask or Quart.

    Raises:
        FlaskChameleonException: At request time, if the view returns anything other
            than a `dict` or a recognized `Response` object, or if `global_init()`
            was never called.

    Examples:
        ```python
        @app.get('/')
        @chameleon_flask.template('home/index.pt')
        def index():
            return {'message': 'Hello world'}


        @app.get('/listing')
        @chameleon_flask.template  # Bare: renders {module}/{function_name}.html or .pt
        async def listing():
            return {'items': await db.all_items()}
        ```
    """

    wrapped_function = None
    if callable(template_file):
        wrapped_function = template_file
        template_file = None

    def response_inner(f):
        global template_path

        if not template_path:
            template_path = 'templates'

        if isinstance(template_file, str) and template_file:
            view_template: str = template_file
        else:
            # Use the default naming scheme: template_folder/module_name/function_name.pt
            module = f.__module__
            if '.' in module:
                module = module.split('.')[-1]
            view = f.__name__
            view_template = f'{module}/{view}.html'

            if not os.path.exists(os.path.join(template_path, view_template)):
                view_template = f'{module}/{view}.pt'

        # Shared by both wrappers so the sync and async paths cannot drift apart.
        def build_response(response_val: Any) -> flask.Response:
            return __render_response(view_template, response_val, content_type, status_code)

        def not_found_response(nfe: FlaskChameleonNotFoundException) -> flask.Response:
            return __render_response(nfe.template_file, {}, 'text/html', 404)

        @wraps(f)
        def sync_view_method(*args, **kwargs) -> flask.Response:
            try:
                return build_response(f(*args, **kwargs))
            except FlaskChameleonNotFoundException as nfe:
                return not_found_response(nfe)

        @wraps(f)
        async def async_view_method(*args, **kwargs) -> flask.Response:
            try:
                return build_response(await f(*args, **kwargs))
            except FlaskChameleonNotFoundException as nfe:
                return not_found_response(nfe)

        if inspect.iscoroutinefunction(f):
            return async_view_method
        else:
            return sync_view_method

    return response_inner(wrapped_function) if wrapped_function else response_inner


def __render_response(
    template_file: str, response_val: Any, content_type: str, status_code: int = 200
) -> flask.Response:
    if isinstance(response_val, werkzeug.sansio.response.Response) or str(type(response_val)) in response_classes:
        # May be a Quart or bare werkzeug response; those types can't be named here
        # without importing Quart, which this library intentionally avoids.
        return cast(flask.Response, response_val)

    if template_file and not isinstance(response_val, dict):
        msg = f'Invalid return type {type(response_val)}, we expected a dict or flask.Response as the return value.'
        raise FlaskChameleonException(msg)

    model = response_val

    html = render(template_file, **model)
    return flask.Response(response=html, content_type=content_type, status=status_code)


def not_found(four04template_file: str = 'errors/404.pt') -> NoReturn:
    """
    Abort the current view and render a friendly 404 page.

    Call this inside a view decorated with `@template`, e.g. when a database lookup
    comes up empty. The decorator catches the raised exception and renders the given
    404 template with an empty model, `text/html` content type, and status code 404
    (the view's own `content_type` and `status_code` do not apply to the 404 path).

    Args:
        four04template_file: The template to render for the 404 response. Defaults to
            `errors/404.pt`; an empty or blank value falls back to that same default.

    Raises:
        FlaskChameleonNotFoundException: Always; the `@template` decorator turns it
            into the rendered 404 response.

    Examples:
        ```python
        @app.get('/catalog/item/<int:item_id>')
        @chameleon_flask.template('catalog/item.pt')
        def item(item_id: int):
            item = service.get_item_by_id(item_id)
            if not item:
                chameleon_flask.not_found()

            return {'item': item}
        ```
    """
    msg = 'The URL resulted in a 404 response.'

    if four04template_file and four04template_file.strip():
        raise FlaskChameleonNotFoundException(msg, four04template_file)
    else:
        raise FlaskChameleonNotFoundException(msg)
