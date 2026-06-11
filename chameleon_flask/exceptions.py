from typing import Optional


class FlaskChameleonException(Exception):
    """Base exception for all chameleon-flask errors."""


class FlaskChameleonNotFoundException(FlaskChameleonException):
    """
    Raised by `not_found()` to signal that a view should render a 404 page.

    The `@template` decorator catches this exception and renders its `template_file`
    with an empty model and status code 404.

    Args:
        message: Optional description of the missing resource.
        four04template_file: The template to render for the 404 response.
    """

    def __init__(self, message: Optional[str] = None, four04template_file: str = 'errors/404.pt'):
        super().__init__(message)

        self.template_file: str = four04template_file
        self.message: Optional[str] = message
