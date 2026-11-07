"""Edge cases around the model contents and decorator stacking."""

import asyncio
import functools
import warnings

import flask
import pytest

import chameleon_flask as fc


def test_model_key_encoding_raises_clear_error(setup_global_template):
    @fc.template('home/index.pt')
    def view_method():
        return {'encoding': 'utf-8', 'a': 1, 'b': 2, 'c': 3}

    with pytest.raises(fc.FlaskChameleonException, match="'encoding'"):
        view_method()


def test_render_rejects_encoding_key(setup_global_template):
    with pytest.raises(fc.FlaskChameleonException, match="'encoding'"):
        fc.engine.render('home/index.pt', encoding='utf-8', a=1, b=2, c=3)


def test_async_view_under_wrapping_sync_decorator(setup_global_template):
    def passthrough(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    @fc.template('home/index.pt')
    @passthrough
    async def view_method(a, b, c):
        return {'a': a, 'b': b, 'c': c}

    resp = asyncio.run(view_method(1, 2, 3))
    assert isinstance(resp, flask.Response)
    assert resp.status_code == 200


def test_not_found_under_wrapping_sync_decorator(setup_global_template):
    def passthrough(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    @fc.template('home/index.pt')
    @passthrough
    async def view_method():
        fc.not_found()

    resp = asyncio.run(view_method())
    assert isinstance(resp, flask.Response)
    assert resp.status_code == 404


def test_async_view_under_opaque_sync_decorator_raises_clear_error(setup_global_template):
    def opaque(f):
        def wrapper(*args, **kwargs):  # No functools.wraps: the async def is hidden.
            return f(*args, **kwargs)

        return wrapper

    @fc.template('home/index.pt')
    @opaque
    async def view_method(a, b, c):
        return {'a': a, 'b': b, 'c': c}

    with warnings.catch_warnings():
        warnings.simplefilter('error', RuntimeWarning)  # The coroutine must be closed, not leaked.
        with pytest.raises(fc.FlaskChameleonException, match='awaitable'):
            view_method(1, 2, 3)
