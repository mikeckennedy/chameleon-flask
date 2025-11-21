# Release v0.6.0

## New Feature: Namespace Restriction Control

Added support for controlling Chameleon's namespace restriction, enabling better compatibility with attribute-based JavaScript frameworks like Vue.js and Alpine.js.

### What's New

The `global_init()` function now accepts a `restricted_namespace` parameter (defaults to `True` for backward compatibility). When set to `False`, Chameleon only treats its own namespaces (TAL, METAL, i18n) specially, allowing all other attributes to pass through unchanged.

### Usage

```python
import chameleon_flask

# Turn off namespace restriction for Alpine.js/Vue.js compatibility
chameleon_flask.global_init(
    template_folder='templates',
    auto_reload=True,
    restricted_namespace=False  # <-- Enable attribute-based JS frameworks
)
```

### Why This Matters

With `restricted_namespace=False`:
- Chameleon only processes its own namespaces (`tal:`, `metal:`, `i18n:`)
- All other attributes like `x-data`, `x-on:click`, `x-bind:class`, `@click`, `:class` are left untouched
- Perfect for templates using Alpine.js, Vue.js, or other attribute-based frameworks
- No need to escape or work around Chameleon's namespace restrictions

### Backward Compatibility

This change is fully backward compatible. The default value is `True`, maintaining the existing behavior unless explicitly changed.

