import asyncio

import flask

import chameleon_flask
import chameleon_flask as fc


# setup_global_template - needed as pytest mix-in.
# noinspection PyUnusedLocal
def test_friendly_404_sync_method(setup_global_template):
    @fc.template('home/index.pt')
    def view_method(a, b, c):
        chameleon_flask.not_found()
        return {'a': a, 'b': b, 'c': c}

    resp = view_method(1, 2, 3)
    html = response_to_html(resp)
    assert isinstance(resp, flask.Response)
    assert resp.status_code == 404
    assert '<h1>This is a pretty 404 page.</h1>' in html


# setup_global_template - needed as pytest mix-in.
# noinspection PyUnusedLocal
def test_friendly_404_custom_template_sync_method(setup_global_template):
    @fc.template('home/index.pt')
    def view_method(a, b, c):
        chameleon_flask.not_found(four04template_file='errors/other_error_page.pt')
        return {'a': a, 'b': b, 'c': c}

    resp = view_method(1, 2, 3)
    html = response_to_html(resp)
    assert isinstance(resp, flask.Response)
    assert resp.status_code == 404
    assert '<h1>Another pretty 404 page.</h1>' in html


# setup_global_template - needed as pytest mix-in.
# noinspection PyUnusedLocal
def test_friendly_404_async_method(setup_global_template):
    @fc.template('home/index.pt')
    async def view_method(a, b, c) -> flask.Response:
        chameleon_flask.not_found()
        return {'a': a, 'b': b, 'c': c}

    resp = asyncio.run(view_method(1, 2, 3))
    html = response_to_html(resp)
    assert isinstance(resp, flask.Response)
    assert resp.status_code == 404
    assert '<h1>This is a pretty 404 page.</h1>' in html


def response_to_html(response: flask.Response) -> str:
    # noinspection PyUnresolvedReferences
    return response.response[0].decode('utf-8')