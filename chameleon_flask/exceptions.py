"""Exceptions raised by chameleon-flask.

There are only two. `FlaskChameleonException` is the base for everything the library raises
on purpose: a missing `global_init()`, a view returning the wrong type, a reserved key in the
model. `FlaskChameleonNotFoundException` is the odd one out. It is raised deliberately by
`not_found()` and caught deliberately by the `@template` decorator, which makes it control
flow in an exception's clothing rather than an error you are expected to see.

Both are importable from the package root (e.g. `chameleon_flask.FlaskChameleonException`)
as well as from this module.
"""


class FlaskChameleonException(Exception):
    """
    Base exception for all chameleon-flask errors.

    Catch this to handle anything the library raises on purpose, from a missing
    `global_init()` call to a view that returned something other than a `dict` or a
    `Response`. The message always says what went wrong and, where there is one, the fix.
    """


class FlaskChameleonNotFoundException(FlaskChameleonException):
    """
    Raised by `not_found()` to signal that a view should render a 404 page.

    You will rarely raise or catch this yourself. `not_found()` raises it from deep inside
    a view, the `@template` decorator catches it on the way out and renders its
    `template_file` with an empty model and status code 404. It only escapes if the view
    is not decorated, which is the one situation where you might want to catch it.

    Args:
        message: Optional description of the missing resource.
        four04template_file: The template to render for the 404 response.

    Attributes:
        message: The message passed in, if any.
        template_file: The template the decorator will render for the 404 response.
    """

    def __init__(self, message: str | None = None, four04template_file: str = 'errors/404.pt'):
        super().__init__(message)

        self.template_file: str = four04template_file
        self.message: str | None = message
