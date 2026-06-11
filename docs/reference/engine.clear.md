## engine.clear()


Reset the template engine to its uninitialized state.


Usage

``` python
engine.clear()
```


Forgets the cached template loader and template folder so a later [global_init()](global_init.md#chameleon_flask.global_init) call can re-initialize the engine with different settings. Mostly useful in tests.
