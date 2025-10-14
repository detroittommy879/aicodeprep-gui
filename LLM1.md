Yep—there’s at least one concrete bug hiding in there.  
Take a look at the fallback `NodePropWidgetEnum` definitions that you use when `NodeGraphQt` isn’t installed:

```python
# llm_nodes.py
try:
    from NodeGraphQt.constants import NodePropWidgetEnum
except ImportError:
    class NodePropWidgetEnum:
        QLINE_EDIT = 3
        QCOMBO_BOX = 5
```

Everywhere else you call those with “`.value`”, e.g.:

```python
self.create_property("model", "", widget_type=NodePropWidgetEnum.QTEXT_EDIT.value)
```

Because the fallback constants are just plain integers with no `.value`, the moment this stub gets exercised (i.e., a user doesn’t have NodeGraphQt installed) you’ll get `AttributeError: 'int' object has no attribute 'value'`. The same problem exists in the other fallback (`io_nodes.py` also adds `.value`) and you’re actually missing the `QTEXT_EDIT` member entirely in the stub.  

Quick fix: make your stub mimic the enum API:

```python
class _EnumValue:
    def __init__(self, v): self.value = v

class NodePropWidgetEnum:
    QLINE_EDIT  = _EnumValue(3)
    QTEXT_EDIT  = _EnumValue(4)
    QCOMBO_BOX  = _EnumValue(5)
    FILE_SAVE   = _EnumValue(14)   # if you need it in io_nodes.py
```

(or swap over to using raw ints and stop calling `.value` in the fallback paths).

Once you adjust that, the “no NodeGraphQt” path will run instead of crashing during import.

Let me know if you’d like a quick patch for all of the fallback stubs.