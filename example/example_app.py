import asyncio
from pathlib import Path

import flask

import chameleon_flask

app = flask.Flask(__name__)


@app.get('/')
@chameleon_flask.template('index.pt')
def hello_world():
    return {'message': "Let's go Chameleon!"}


@app.get('/async')
@chameleon_flask.template('async.pt')
async def async_world():
    await asyncio.sleep(.01)  # Just a little asyncio to prove it works.
    return {'message': "Let's go async Chameleon!"}


@app.get('/xml')
@chameleon_flask.template('sample.xml', content_type='application/xml', status_code=201)
def xml_response():
    return {
        'items': [
            'pyramid',
            'flask',
            'fastapi',
        ],
    }


def add_chameleon():
    dev_mode = True

    # noinspection PyPep8Naming
    BASE_DIR = Path(__file__).resolve().parent
    template_folder = (BASE_DIR / 'templates').as_posix()
    chameleon_flask.global_init(template_folder, auto_reload=dev_mode)


def main():
    add_chameleon()
    app.run(debug=True, host='127.0.0.1', port=5555)


if __name__ == '__main__':
    main()
