It turns out nothing mystical is wrong with NodeGraphQt or your flow-dock code – it’s simply never getting installed when folks do

    pip install aicodeprep-gui

even though you listed it in your pyproject.toml under `[project.dependencies]`.  Here’s why:

  1.  PEP 621 (the `[project]` table in pyproject.toml) only became “real” for setuptools in version 61.0, and pip only started paying attention to it in about pip 21.3.  
  2.  If your users’ machines have older pip/setuptools, they build your wheel but pip ignores your `[project.dependencies]`, so it never pulls in NodeGraphQt.  
  3.  At runtime, your code does  
         try:
             from NodeGraphQt import NodeGraph, PropertiesBinWidget
         except ImportError:
             …  
      and so it falls back to “NG_AVAILABLE = False” and tells them “NodeGraphQt not installed.”

How to fix it:

— Short term, on those machines:

   • `pip install NodeGraphQt`  
   • or simply upgrade pip & setuptools before installing your package:
       ```
       pip install --upgrade pip setuptools wheel
       pip install aicodeprep-gui
       ```

— Longer term, make your project install_requires work even on older installers.  You have two easy options:

  1.  Add a minimal `setup.cfg` (or `setup.py`) alongside your pyproject.toml with an `[options] install_requires = …` section that duplicates:
         install_requires =
             PySide6>=6.9,<6.10
             NodeGraphQt
             pathspec
             requests
             …
     setuptools will always read `install_requires` even on ancient pip.

  2.  Bump your build-backend requirement in pyproject.toml so that anyone installing your package is forced to use a new setuptools/pip:
     ```toml
     [build-system]
     requires = [
       "setuptools>=61.0.0",
       "wheel",
       "pip>=21.3"        # <— add this
     ]
     build-backend = "setuptools.build_meta"
     ```
     Then ensure your CI / docs tell users to run `pip install --upgrade pip setuptools wheel` before pulling you down.

Once pip actually installs NodeGraphQt, your Flow Studio dock will find it, `NG_AVAILABLE` will be true, and you won’t see that “not installed” warning anymore.

In summary: Your dependency declaration is perfectly correct for modern build tools, but older pip/setuptools clients simply ignore it.  Either upgrade your installers or add a legacy `install_requires` so that NodeGraphQt always comes along for the ride.