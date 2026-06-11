## not_found()


Abort the current view and render a friendly 404 page.


Usage

``` python
not_found(four04template_file="errors/404.pt")
```


Call this inside a view decorated with `@template`, e.g. when a database lookup comes up empty. The decorator catches the raised exception and renders the given 404 template with an empty model, `text/html` content type, and status code 404 (the view's own `content_type` and `status_code` do not apply to the 404 path).


## Parameters


`four04template_file: str = ``"errors/404.pt"`  
The template to render for the 404 response. Defaults to `errors/404.pt`; an empty or blank value falls back to that same default.


## Raises


`FlaskChameleonNotFoundException`  
Always; the `@template` decorator turns it into the rendered 404 response.


## Examples

``` python
@app.get('/catalog/item/<int:item_id>')
@chameleon_flask.template('catalog/item.pt')
def item(item_id: int):
    item = service.get_item_by_id(item_id)
    if not item:
        chameleon_flask.not_found()

    return {'item': item}
```
