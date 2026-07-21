## FlaskChameleonNotFoundException


Raised by [not_found()](not_found.md#chameleon_flask.not_found) to signal that a view should render a 404 page.


Usage

``` python
FlaskChameleonNotFoundException(
    message=None, four04template_file="errors/404.pt"
)
```


The `@template` decorator catches this exception and renders its `template_file` with an empty model and status code 404.


## Parameters


`message: str | None = None`  
Optional description of the missing resource.

`four04template_file: str = ``"errors/404.pt"`  
The template to render for the 404 response.


## Attributes


`message: str | None`  
The message passed in, if any.

`template_file: str`  
The template the decorator will render for the 404 response.
