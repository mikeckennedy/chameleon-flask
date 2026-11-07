## engine.render()


Render a Chameleon template to an HTML string.


Usage

``` python
engine.render(
    template_file,
    **template_data,
)
```


This is the bottom rung of the ladder: a model goes in, HTML comes out, and nothing is wrapped in a response. Reach for it when you want the markup itself, for example to build an email body or to tuck rendered HTML into a JSON payload. Decorated views and [response()](response.md#chameleon_flask.response) both end up here.


## Parameters


`template_file: str`  
The Chameleon template file (path relative to the template folder).

`**template_data: Any`  
Values passed to the template as the model.


## Returns


`str`  
The rendered HTML as a string.


## Raises


`FlaskChameleonException`  
If [global_init()](global_init.md#chameleon_flask.global_init) has not been called yet, or if `template_data` contains the key `encoding`, which Chameleon reserves as a render argument and cannot expose to the template.
