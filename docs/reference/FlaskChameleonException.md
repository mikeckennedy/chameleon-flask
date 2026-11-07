## FlaskChameleonException


Base exception for all chameleon-flask errors.


Usage

``` python
FlaskChameleonException()
```


Catch this to handle anything the library raises on purpose, from a missing [global_init()](global_init.md#chameleon_flask.global_init) call to a view that returned something other than a `dict` or a `Response`. The message always says what went wrong and, where there is one, the fix.
