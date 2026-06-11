## engine.render()


Render a Chameleon template to an HTML string.


Usage

``` python
engine.render(
    template_file,
    **template_data,
)
```


## Parameters


`template_file: str`  
The Chameleon template file (path relative to the template folder).

`**template_data: dict`  
Values passed to the template as the model.


## Returns


`str`  
The rendered HTML as a string.


## Raises


`FlaskChameleonException`  
If [global_init()](global_init.md#chameleon_flask.global_init) has not been called yet.
