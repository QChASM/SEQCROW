![SEQCROW](SEQCROW.png)
# SEQCROW
SEQCROW is an AaronTools-based plugin for <a href="https://www.cgl.ucsf.edu/chimerax/" target="_blank">UCSF ChimeraX</a>, a cross-platform 3D molecular graphics program.
SEQCROW extends ChimeraX by adding tools to build and modify complex molecular structures, map new catalysts and ligands onto previously-computed structures, and manage AaronTools libraries.
These tools enable users to rapidly modify several structures simultaneously, providing an intuitive interface to build libraries of the complex molecular structures frequently encountered in modern quantum chemistry applications.

More information about SEQCROW features can be found on the [GitHub wiki](https://github.com/QChASM/SEQCROW/wiki).

## Installation
1. Download <a href="https://github.com/QChASM/SEQCROW/raw/master/dist/SEQCROW-0.1-py3-none-any.whl" target="_blank">SEQCROW-0.1-py3-none-any.whl</a>
2. On the ChimeraX command line, enter `toolshed install /path/to/SEQCROW-0.1-py3-none-any.whl`
3. Restart ChimeraX
4. If you have a personal AaronTools library already, you can specify the path to it in the SEQCROW settings. Open ChimeraX and go Favorites &rarr; Settings... &rarr; SEQCROW. You will have to restart ChimeraX if you change this setting. 

## Updating
1. Download <a href="https://github.com/QChASM/SEQCROW/raw/master/dist/SEQCROW-0.1-py3-none-any.whl" target="_blank">SEQCROW-0.1-py3-none-any.whl</a>
2. On the ChimeraX command line, enter `toolshed uninstall SEQCROW`
3. Restart ChimeraX
4. On the ChimeraX command line, enter `toolshed install /path/to/SEQCROW-0.1-py3-none-any.whl`

## Other Versions
This is a plug-in for ChimeraX.

### Chimera
The Chimera version of SEQCROW (ChimAARON) can be found on the [Chimera branch](https://github.com/QChASM/ChimAARON/tree/Chimera).

### ChimeraX Daily
For the latest features and bugs, go to the [development branch](https://github.com/QChASM/ChimAARON/tree/dev)
