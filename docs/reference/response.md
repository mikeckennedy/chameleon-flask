## response()


Render a Chameleon template directly to a `flask.Response`.


Usage

``` python
response(
    template_file, content_type="text/html", status_code=200, **template_data
)
```


The `@template` decorator is the comfortable path, but it cannot reach everywhere. Error handlers are registered with Flask directly, a view may need to render a different template down one branch, and a helper may build a response for a view to return. All of them have the same need: a template, a model, and a finished response. This function meets that need in one call.


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
