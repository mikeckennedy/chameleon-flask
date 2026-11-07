"""The chameleon-flask template engine.

This module is where the library lives. `global_init()` creates one process-wide Chameleon
`PageTemplateLoader`, and everything else is a thin layer on top of it: `render()` turns a
template and a model into HTML, `response()` wraps that HTML in a `flask.Response`, and the
`@template` decorator lets a Flask or Quart view return a plain `dict` and get a finished
response back. `not_found()` is the escape hatch that swaps the page for a friendly 404.

Initialize the engine once at app startup with `global_init()`; the rest builds on that loader.
"""

import asyncio
import inspect
import os
import sys
import types
from collections.abc import Awaitable, Callable
from functools import update_wrapper, wraps
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


def _running_loop() -> asyncio.AbstractEventLoop | None:
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return None


async def _await(awaitable: Awaitable[flask.Response]) -> flask.Response:
    return await awaitable


def _run_to_completion(awaitable: Awaitable[flask.Response]) -> flask.Response:
    # The same mechanism Flask uses to run its own async views from a WSGI worker.
    from asgiref.sync import async_to_sync  # Installed by flask[async], the library's declared dependency.

    return async_to_sync(_await)(awaitable)


class _PendingResponse:
    """
    The awaitable an async view hands back, which Flask can also run on its own.

    Normally whoever receives this awaits it: Flask through asgiref, Quart directly, or a test
    through `asyncio.run()`. It implements the full coroutine protocol so all of those accept it
    exactly like the coroutine it wraps.

    When a sync decorator is stacked *outside* `@template`, Flask calls that decorator as a
    plain function and receives this object as the view's return value without awaiting it.
    Flask treats a callable return value as a WSGI application, so `__call__` runs the view
    to completion and serves the resulting response. That is what makes decorator order
    irrelevant on Flask.
    """

    __slots__ = ('_coro',)

    def __init__(self, coro: Awaitable[flask.Response]):
        self._coro = coro

    def __await__(self):
        return self._coro.__await__()

    def send(self, value):
        return self._coro.send(value)  # type: ignore[attr-defined]

    def throw(self, *args):
        return self._coro.throw(*args)  # type: ignore[attr-defined]

    def close(self) -> None:
        self._coro.close()  # type: ignore[attr-defined]

    def __call__(self, environ, start_response):
        response = _run_to_completion(self._coro)
        return response(environ, start_response)


class _AsyncView:
    """
    The callable `@template` installs on an async view (Python 3.12 and newer).

    It is marked as a coroutine function, so Flask and Quart detect the async view exactly as
    they would an `async def` and await what it returns. Calling it returns a
    `_PendingResponse`, which awaits like a coroutine but can also be served by Flask directly
    when a sync decorator outside `@template` returns it without awaiting.

    The coroutine mark lives on the class, not the instance, so `functools.wraps` in an outer
    decorator does not copy it onto that decorator's plain wrapper (which may return a redirect
    without awaiting anything, and must stay a sync function in Flask's eyes).
    """

    def __init__(self, view: Callable[..., Any], run: Callable[..., Awaitable[flask.Response]]):
        self._run = run
        update_wrapper(self, view)

    def __call__(self, *args: Any, **kwargs: Any) -> _PendingResponse:
        return _PendingResponse(self._run(*args, **kwargs))

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        # Bind like a function does, so @template works on async methods of class-based views.
        return self if obj is None else types.MethodType(self, obj)

    def __repr__(self) -> str:
        return f'<chameleon_flask async view {getattr(self, "__qualname__", "?")}>'


if sys.version_info >= (3, 12):
    inspect.markcoroutinefunction(_AsyncView)


def global_init(
    template_folder: str, auto_reload: bool = False, cache_init: bool = True, restricted_namespace: bool = True
) -> None:
    """
    Initialize the Chameleon template engine.

    Point the library at your templates folder once, at app startup, and every decorated
    view in the process knows where to look from then on. Under the hood this creates a
    single Chameleon `PageTemplateLoader`, which compiles each template to Python bytecode
    the first time it renders and caches the result.

    The call is one-shot by design. With `cache_init=True` (the default), later calls are
    silently ignored once the engine is initialized, so a stray second `global_init()` deep
    in some module cannot swap your template folder out from under you. To re-initialize
    with different settings, pass `cache_init=False` or call `chameleon_flask.engine.clear()`
    first.

    Call this before any decorated view is defined: the bare `@template` form resolves its
    template file name at decoration time and relies on the folder recorded here.

    Args:
        template_folder: Path to the template directory.
        auto_reload: Re-read a template whenever its file changes. Exactly what you want
            while editing templates and an unneeded file check per render in production,
            so tie it to your dev-mode flag.
        cache_init: If True, do nothing when the engine is already initialized.
        restricted_namespace: If True, only TAL/METAL/i18n namespaced attributes are allowed
            in templates. Set it to False to let attribute-based JavaScript frameworks such
            as Alpine.js and Vue use their shorthand (`@click`, `:class`, `x-data`).

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

    Forgets the cached template loader and the template folder, so the next `global_init()`
    call starts from scratch with whatever settings it is given. An app will rarely need
    this; it exists for test suites that initialize the engine against different template
    folders and must not leak state from one test into the next.
    """
    global __templates, template_path
    __templates = None
    template_path = None


def render(template_file: str, **template_data: Any) -> str:
    """
    Render a Chameleon template to an HTML string.

    This is the bottom rung of the ladder: a model goes in, HTML comes out, and nothing is
    wrapped in a response. Reach for it when you want the markup itself, for example to
    build an email body or to tuck rendered HTML into a JSON payload. Decorated views and
    `response()` both end up here.

    Args:
        template_file: The Chameleon template file (path relative to the template folder).
        **template_data: Values passed to the template as the model.

    Returns:
        The rendered HTML as a string.

    Raises:
        FlaskChameleonException: If `global_init()` has not been called yet, or if
            `template_data` contains the key `encoding`, which Chameleon reserves as a
            render argument and cannot expose to the template.
    """
    if not __templates:
        raise FlaskChameleonException('You must call global_init() before rendering templates.')

    if 'encoding' in template_data:
        msg = (
            "The template model cannot contain the key 'encoding': Chameleon reserves it as a "
            'render argument. Rename it in the view (for example to text_encoding).'
        )
        raise FlaskChameleonException(msg)

    page: PageTemplate = __templates[template_file]
    return page.render(encoding='utf-8', **template_data)


def response(
    template_file: str, content_type: str = 'text/html', status_code: int = 200, **template_data: Any
) -> flask.Response:
    """
    Render a Chameleon template directly to a `flask.Response`.

    The `@template` decorator is the comfortable path, but it cannot reach everywhere.
    Error handlers are registered with Flask directly, a view may need to render a
    different template down one branch, and a helper may build a response for a view to
    return. All of them have the same need: a template, a model, and a finished response.
    This function meets that need in one call.

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

    This is the decorator the library is built around. The view underneath it returns a
    plain `dict`, and the decorator renders that dict through the template into a finished
    `flask.Response`. Return a Flask/Quart `Response` instead (a redirect, say) and it is
    passed through untouched; the template never runs. Anything else raises
    `FlaskChameleonException` naming the offending type.

    It works on sync and async views alike, bare (`@template`) or with arguments
    (`@template('home/index.pt')`). When used bare, the template file is derived from the
    view as `{module}/{function_name}.html`, falling back to `.pt` when no `.html` file
    exists in the template folder.

    Two things are decided once, when the view is decorated, not per request. The first is
    the template file name: when relying on the bare form, call `global_init()` before
    defining your views, otherwise the `.html`-or-`.pt` check assumes a folder named
    `templates` relative to the working directory. The second is whether the view is async.
    On Flask with Python 3.12 or newer, your own decorators may sit above or below
    `@template` in any order. On Quart, and on older Pythons, keep `@template` directly
    under the route decorator and put sync decorators beneath it using `functools.wraps`
    (which `@template` looks through), or make them async; otherwise the framework cannot
    see the coroutine function and a clear error is raised.

    Put the route decorator outermost and `@template` directly below it. The route must
    register the wrapper that produces a `Response`, not the raw view.

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

        async def finish(awaitable: Awaitable[Any]) -> flask.Response:
            try:
                return build_response(await awaitable)
            except FlaskChameleonNotFoundException as nfe:
                return not_found_response(nfe)

        @wraps(f)
        def sync_view_method(*args, **kwargs) -> Any:
            try:
                result = f(*args, **kwargs)
            except FlaskChameleonNotFoundException as nfe:
                return not_found_response(nfe)

            if inspect.isawaitable(result):
                # An async view hid behind a sync decorator without functools.wraps, so it could
                # not be detected at decoration time. Inside a Flask request there is no event
                # loop and Flask will not await anything, but it will serve a callable, so hand
                # back a pending response it can run. Anywhere else, explain the fix.
                if _running_loop() is None and flask.has_request_context():
                    return _PendingResponse(finish(result))
                if inspect.iscoroutine(result):
                    result.close()  # Avoid the "coroutine was never awaited" warning.
                msg = (
                    f'The view {f.__qualname__} returned an awaitable from a sync call path. Give the decorator '
                    'between @template and the async def functools.wraps so the async view can be detected, '
                    'or make that decorator async.'
                )
                raise FlaskChameleonException(msg)

            try:
                return build_response(result)
            except FlaskChameleonNotFoundException as nfe:
                return not_found_response(nfe)

        async def run_async_view(*args, **kwargs) -> flask.Response:
            try:
                result = f(*args, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
                return build_response(result)
            except FlaskChameleonNotFoundException as nfe:
                return not_found_response(nfe)

        # Also look through functools.wraps chains so a sync decorator stacked between @template
        # and an async def still gets the awaiting wrapper (and Flask/Quart see a coroutine function).
        if inspect.iscoroutinefunction(f) or inspect.iscoroutinefunction(inspect.unwrap(f)):
            if sys.version_info >= (3, 12):
                return _AsyncView(f, run_async_view)
            return wraps(f)(run_async_view)  # Older Pythons cannot mark a plain callable as async.
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

    Somewhere in most views there is a lookup that can come up empty: an item id that was
    deleted last week, a slug that never existed. Call this at that point, inside a view
    decorated with `@template`, and stop worrying about the rest of the function. It raises
    `FlaskChameleonNotFoundException`, the decorator catches it, and the visitor gets your
    404 template in the site's own look instead of the framework's bare error text.

    The 404 page is rendered with an empty model, `text/html` content type, and status
    code 404; the view's own `content_type` and `status_code` do not apply to this path.

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
