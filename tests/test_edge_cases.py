"""Edge cases around reserved model keys and async views behind other decorators."""

import asyncio
import functools
import inspect
import sys
import warnings

import flask
import flask.views
import pytest

import chameleon_flask as fc

PY312 = sys.version_info >= (3, 12)


def test_model_key_encoding_raises_clear_error(setup_global_template):
    @fc.template('home/index.pt')
    def view():
        return {'encoding': 'latin-1'}

    with pytest.raises(fc.FlaskChameleonException, match="'encoding'"):
        view()


def test_render_rejects_encoding_key(setup_global_template):
    with pytest.raises(fc.FlaskChameleonException, match="'encoding'"):
        fc.engine.render('home/index.pt', encoding='utf-8', a=1, b=2, c=3)


def passthrough(f):
    """A sync decorator that uses functools.wraps, like most real-world decorators."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def opaque(f):
    """A sync decorator without functools.wraps, which hides the async def completely."""

    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def redirect_unless(flag_name):
    """A sync decorator with an early return, like login_required."""

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if flask.request.args.get(flag_name) is None:
                return flask.redirect('/login')
            return f(*args, **kwargs)

        return wrapper

    return decorator


def test_async_view_under_wrapping_sync_decorator(setup_global_template):
    @fc.template('home/index.pt')
    @passthrough
    async def view(a, b, c):
        return {'a': a, 'b': b, 'c': c}

    assert inspect.iscoroutinefunction(view)
    resp = asyncio.run(view(1, 2, 3))
    assert isinstance(resp, flask.Response)
    assert resp.status_code == 200


def test_not_found_under_wrapping_sync_decorator(setup_global_template):
    @fc.template('home/index.pt')
    @passthrough
    async def view():
        fc.not_found()

    resp = asyncio.run(view())
    assert resp.status_code == 404


def test_async_view_under_opaque_sync_decorator_raises_clear_error(setup_global_template):
    # Without functools.wraps the async def cannot be detected, so the sync wrapper is installed.
    # Outside a Flask request nothing would await the view, so the error explains the fix.
    @fc.template('home/index.pt')
    @opaque
    async def view(a, b, c):
        return {'a': a, 'b': b, 'c': c}

    with warnings.catch_warnings():
        warnings.simplefilter('error', RuntimeWarning)  # the stray coroutine must be closed, not leaked
        with pytest.raises(fc.FlaskChameleonException, match='awaitable'):
            view(1, 2, 3)


def test_async_view_returns_awaitable_that_asyncio_accepts(setup_global_template):
    @fc.template('home/index.pt')
    async def view():
        return {}

    pending = view()
    assert inspect.isawaitable(pending)
    assert asyncio.iscoroutine(pending)  # asyncio.run(), create_task() and gather() all accept it
    assert asyncio.run(pending).status_code == 200


def _client(*routes):
    app = flask.Flask(__name__)
    app.config['PROPAGATE_EXCEPTIONS'] = True
    for rule, view in routes:
        app.add_url_rule(rule, view_func=view)
    return app.test_client()


def test_flask_serves_plain_async_view(setup_global_template):
    @fc.template('home/index.pt')
    async def view():
        return {}

    assert _client(('/', view)).get('/').status_code == 200


def test_flask_serves_async_view_under_opaque_sync_decorator(setup_global_template):
    @fc.template('home/index.pt')
    @opaque
    async def view():
        return {}

    assert _client(('/', view)).get('/').status_code == 200


@pytest.mark.skipif(not PY312, reason='decorator order is only irrelevant on Python 3.12+')
def test_flask_serves_async_view_with_sync_decorator_outside_template(setup_global_template):
    # The decorator Flask registers is a plain function, so Flask calls it synchronously and gets
    # whatever @template's wrapper returns. That must be a Response, not a coroutine.
    @redirect_unless('user')
    @fc.template('home/index.pt')
    async def view():
        return {}

    client = _client(('/', view))
    assert client.get('/?user=ada').status_code == 200
    redirected = client.get('/')
    assert redirected.status_code == 302
    assert redirected.headers['Location'] == '/login'


@pytest.mark.skipif(not PY312, reason='decorator order is only irrelevant on Python 3.12+')
def test_flask_serves_async_view_with_opaque_decorator_outside_template(setup_global_template):
    @opaque
    @fc.template('home/index.pt')
    async def view():
        return {}

    assert _client(('/', view)).get('/').status_code == 200


def test_outer_wraps_decorator_does_not_inherit_coroutine_mark(setup_global_template):
    # If the mark leaked onto the outer sync wrapper, Flask would await its plain redirect Response.
    @redirect_unless('user')
    @fc.template('home/index.pt')
    async def view():
        return {}

    assert not inspect.iscoroutinefunction(view)
    assert inspect.iscoroutinefunction(inspect.unwrap(view))


def test_async_method_view(setup_global_template):
    class Page(flask.views.MethodView):
        @fc.template('home/index.pt')
        async def get(self):
            return {}

    assert _client(('/', Page.as_view('page'))).get('/').status_code == 200


def test_sync_views_unchanged(setup_global_template):
    @fc.template('home/index.pt')
    def view():
        return {}

    assert inspect.isfunction(view)
    assert not inspect.iscoroutinefunction(view)
    assert view().status_code == 200
    assert _client(('/', view)).get('/').status_code == 200
