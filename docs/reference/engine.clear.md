## engine.clear()


Reset the template engine to its uninitialized state.


Usage

``` python
engine.clear()
```


Forgets the cached template loader and the template folder, so the next [global_init()](global_init.md#chameleon_flask.global_init) call starts from scratch with whatever settings it is given. An app will rarely need this; it exists for test suites that initialize the engine against different template folders and must not leak state from one test into the next.
