## response()


Render a Chameleon template directly to a `flask.Response`.


Usage

``` python
response(
    template_file, content_type="text/html", status_code=200, **template_data
)
```


Useful when you want a rendered response without the `@template` decorator, for example inside error handlers or conditional branches.


## Parameters


`template_file: str`  
The Chameleon template file (path relative to the template folder).

`content_type: str = ``"text/html"`  
The content type of the response (defaults to `text/html`).

`status_code: int = ``200`  
The HTTP status code of the response (defaults to 200).

`**template_data: Any`  
Values passed to the template as the model.


## Returns


`flask.Response`  
The rendered `flask.Response`.


## Raises


`FlaskChameleonException`  
If [global_init()](global_init.md#chameleon_flask.global_init) has not been called yet.


## Examples

``` python
@app.errorhandler(500)
def server_error(e):
    return chameleon_flask.response('errors/500.pt', status_code=500)
```
