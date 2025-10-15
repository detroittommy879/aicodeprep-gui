`pip` is actually bringing `NodeGraphQt` into the environment – the package is there.  
The reason Flow Studio keeps telling you that *NodeGraphQt isn’t installed* is that the import of `NodeGraphQt` fails on a clean machine. Flow Studio suppresses the real exception and just prints the generic “not installed” message.

On a fresh install you only have **PySide6** (your GUI depends on it).  
When `NodeGraphQt` is imported it uses the `Qt.py` compatibility layer and looks for a Qt binding in this order: `PySide2`, `PyQt5`, … If none of those are present it raises `ImportError: No module named 'PySide2'`. Because Flow Studio catches every exception and assumes it means the wheel is missing, you end up with the wrong message.

On your development box you still had `PySide2` around, so the import succeeded and Flow Studio worked.

### Fix

Force `Qt.py` to use PySide6 before the first import of `NodeGraphQt`.

```python
import os

# … before “from NodeGraphQt import …”
os.environ.setdefault("QT_API", "PySide6")
os.environ.setdefault("QT_PREFERRED_BINDING", "PySide6")
```

Put those two lines at the very top of the module where Flow Studio imports `NodeGraphQt`  
(e.g. `aicodeprep_gui/pro/flow/flow_dock.py`).

Because `Qt.py` ≥ 1.3.10 understands PySide6, this makes the import succeed on a clean install where only PySide6 is present. After you republish, Flow Studio should start up without complaining.

(If you want to be sure what’s happening now, temporarily print the stored `_NG_IMPORT_ERROR` so you see the real traceback instead of the “not installed” placeholder.)