"""chameleon-flask - Adds integration of the Chameleon template language to Flask and Quart."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _get_version

from .engine import (
    global_init,  # noqa: I001
    not_found,
    response,
    template,
)

try:
    __version__ = _get_version('chameleon_flask')
except PackageNotFoundError:
    __version__ = '0.0.0'

__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__all__ = [
    'template',
    'global_init',
    'not_found',
    'response',
]
