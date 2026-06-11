## template()


Decorate a Flask or Quart view method to render a Chameleon template.


Usage

``` python
template(
    template_file=None,
    content_type="text/html",
    status_code=200,
)
```


Works on both sync and async views, bare (`@template`) or with arguments (`@template('home/index.pt')`). When used bare, the template file is derived from the view as `{module}/{function_name}.html`, falling back to `.pt` when no `.html` file exists in the template folder.

The decorated view must return either a `dict` (passed to the template as the model) or a Flask/Quart `Response` (passed through untouched, e.g. for redirects).


## Parameters


`template_file: Optional[Union[Callable, str]] = None`  
Optional, the Chameleon template file (path relative to the template folder, e.g. `home/index.pt`). Derived from the view when omitted.

`content_type: str = ``"text/html"`  
The content type of the response (defaults to `text/html`).

`status_code: int = ``200`  
Default status code for responses. For example 201 on a POST/create action.


## Returns


The decorator to be consumed by Flask or Quart.


## Raises


`FlaskChameleonException`  
At request time, if the view returns anything other than a `dict` or a recognized `Response` object.
