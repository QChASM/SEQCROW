# ChimAARON
QChASM plug-in for ChimeraX

## Installation
1. Download [https://github.com/QChASM/ChimAARON/blob/dev/dist/ChimAARON-0.1-py3-none-any.whl ChimAARON-0.1-py3-none-any.whl]
2. open ChimeraX
3. on the command line, enter `toolshed install /path/to/ChimAARON-0.1-py3-none-any.whl`
4. close ChimeraX
5. install [AaronTools](https://github.com/QChASM/AaronTools.py) in a directory where ChimeraX can find it
   * AaronTools can be in the directory where ChimeraX installed ChimAARON
   * In ChimeraX, open the python notebook (Tools &rarr; General &rarr; Shell)
   * Enter the following in the notebook:
   ```python
   import ChimAARON
   ChimAARON.__file__
   ```
   * This should print out the path to ChimAARON's \_\_init\_\_ file (something like "/stuff/things/UCSF/ChimeraX/version/site-packages/ChimAARON/\_\_init\_\_.py"). You should, then, be able to put AaronTools in "/stuff/things/UCSF/ChimeraX/version/site-packages".
6. If you have a personal AaronTools library already, you can specify the path to it in the ChimAARON settings. Open ChimeraX and go Favorites &rarr; Settings... &rarr; ChimAARON. You will have to restart ChimeraX if you change this setting. 

## Other Versions
### Chimera
The Chimera version can be found on the [master branch](https://github.com/QChASM/ChimAARON/tree/master).
