## not_found()


Abort the current view and render a friendly 404 page.


Usage

``` python
not_found(four04template_file="errors/404.pt")
```


Call this inside a view decorated with `@template`, e.g. when a database lookup comes up empty. The decorator catches the raised exception and renders the given 404 template with an empty model, `text/html` content type, and status code 404.


## Parameters


`four04template_file: str = ``"errors/404.pt"`  
The template to render for the 404 response (defaults to `errors/404.pt`).


## Raises


`FlaskChameleonNotFoundException`  
Always; the `@template` decorator turns it into the rendered 404 response.
