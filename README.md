![SEQCROW](SEQCROW.png)
# SEQCROW
SEQCROW is an AaronTools-based plugin for <a href="https://www.cgl.ucsf.edu/chimerax/" target="_blank">UCSF ChimeraX</a>, a cross-platform 3D molecular graphics program.
SEQCROW extends ChimeraX by adding tools to build and modify complex molecular structures, map new catalysts and ligands onto previously-computed structures, and manage AaronTools libraries.
These tools enable users to rapidly modify several structures simultaneously, providing an intuitive interface to build libraries of the complex molecular structures frequently encountered in modern quantum chemistry applications.

More information about SEQCROW features can be found on the [GitHub wiki](https://github.com/QChASM/SEQCROW/wiki).

## Installation
1. Download <a href="https://github.com/QChASM/SEQCROW/raw/master/dist/SEQCROW-0.1-py3-none-any.whl" target="_blank">SEQCROW-0.1-py3-none-any.whl</a>
2. Open ChimeraX
3. On the ChimeraX command line, enter `toolshed install /path/to/SEQCROW-0.1-py3-none-any.whl`
4. Download [AaronTools.py](https://github.com/QChASM/AaronTools.py/archive/master.zip) and save it under 'AaronTools' in the directory where ChimeraX installed SEQCROW
   * To find where ChimeraX installed SEQCROW, open the python notebook in ChimeraX (Tools &rarr; General &rarr; Shell)
   * Enter the following in the notebook:
   ```python
   import SEQCROW
   SEQCROW.__file__
   ```
   * This should print out the path to SEQCROW's \_\_init\_\_ file (something like "/stuff/things/UCSF/ChimeraX/version/site-packages/SEQCROW/\_\_init\_\_.py").
   * Save AaronTools in "/stuff/things/UCSF/ChimeraX/version/site-packages".
5. Restart ChimeraX
6. If you have a personal AaronTools library already, you can specify the path to it in the SEQCROW settings. Open ChimeraX and go Favorites &rarr; Settings... &rarr; SEQCROW. You will have to restart ChimeraX if you change this setting. 

## Other Versions
This is a plug-in for ChimeraX.

### Chimera
The Chimera version of SEQCROW (ChimAARON) can be found on the [Chimera branch](https://github.com/QChASM/ChimAARON/tree/Chimera).

### ChimeraX Daily
For the latest features and bugs, go to the [development branch](https://github.com/QChASM/ChimAARON/tree/dev)
