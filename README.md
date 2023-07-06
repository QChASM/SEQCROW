<img src="https://github.com/QChASM/SEQCROW/blob/master/SEQCROW.png?raw=true">

<a href="https://pubmed.ncbi.nlm.nih.gov/34109660/"><img src="https://img.shields.io/badge/PMID-34109660-blue?style=flat-square&logo=appveyor"></a>
<a href="https://doi.org/10.1002/jcc.26700"><img src="https://img.shields.io/badge/DOI-10.1002/jcc.26700-blue?style=flat-square&logo=appveyor"></a>

# SEQCROW
SEQCROW is an AaronTools-based plugin for <a href="https://www.cgl.ucsf.edu/chimerax/" target="_blank">UCSF ChimeraX</a>, a cross-platform 3D molecular graphics program.
SEQCROW extends ChimeraX by adding tools to build and modify complex molecular structures, map new catalysts and ligands onto previously-computed structures, and manage AaronTools libraries.
These tools enable users to rapidly modify several structures simultaneously, providing an intuitive interface to build libraries of the complex molecular structures frequently encountered in modern quantum chemistry applications.

More information about SEQCROW features can be found on the [GitHub wiki](https://github.com/QChASM/SEQCROW/wiki).
Several tutorials for SEQCROW's tools can be found under ChimeraX's Help menu

### File Types
* Open
   * XYZ files
   * Gaussian input and output
   * ORCA output
    * Psi4 output files
    * FCHK files (structure and orbitals)
    * sqm output files
    * NBO .31 and .47 files
    * Q-Chem output files
* Save 
   * XYZ files
   * The <b>Build QM Input</b> tool can be used to save Gaussian, ORCA, Psi4, sqm, Q-Chem, and xTB input files

### Tools
#### Quantum Chemistry
* <b>Build QM Input</b> - build Gaussian, ORCA, Psi4, SQM, Q-Chem, or xTB input files
* <b>IR Spectrum</b> - create a Boltzmann-averaged IR, VCD or Raman spectrum
* <b>Orbital Viewer</b> - view orbitals, electron density, or Fukui functions from FCHK, ORCA output, or NBO files
* <b>Thermochemistry</b> - compute thermal corrections for models with vibrational mode information
* <b>Visualize Normal Modes</b> - display normal modes for models with vibrational mode information as vectors, an animation, or an IR plot
* <b>UV/Vis Spectrum</b> - create a Boltzmann-averaged UV/vis or ECD spectrum from a ground state excitation computation (e.g. TD-DFT, EOM-CC, or ADC)

#### SEQCROW
* <b>AaronTools Fragment Library</b> - browse substituents, ligands, and rings in the AaronTools library
* <b>Add to Personal Library</b> - add substituents, ligands, or rings to your personal AaronTools library
* <b>File Info</b> - view most of the information AaronTools parsed from a structure's file
* <b>Job Queue</b> - manage QM jobs that are run with SEQCROW
* <b>Managed Models</b> - restore models opened through SEQCROW to their original state

#### Structure Analysis
* <b>Buried Volume</b> - calculate %V<sub>bur</sub> around a center, and generate some visuals
* <b>Substituent Sterimol</b> - determine the L, B<sub>1</sub>, B<sub>2</sub>, B<sub>3</sub>, B<sub>4</sub>, and B<sub>5</sub> Sterimol parameters for a selected substituent 
* <b>Cone Angles</b> - calculate Tolman cone angle for unsymmetrical ligands or 'exact' bone angle
* <b>Ligand Sterimol</b> - determine Sterimol or Sterimol2Vec parameters for ligands
* <b>Ligand Solid Angle</b> - solid angle cast by shadow of ligand's VDW radii

#### Structure Editing
* <b>2D Builder</b> - get a 3D molecule from a 2D drawing
* <b>Bond Editor</b> - draw covalent bonds or forming/breaking bonds, change bond lengths
* <b>Change Element</b> - change an atom's element or VSEPR shape
* <b>Change Substituents</b> - add or change substituents on an atomic structure
* <b>Fuse Ring</b> - attach a ring to an atomic structure
* <b>Rotate</b> - rotate selected atoms about a vector defined by a bond, plane, Cartesian axis, or user-defined vector
* <b>Swap Transition Metal Ligands</b> - change ligands on an organometallic catalyst
* <b>Coordination Complex Generator</b> - generate unique coordination complexes given a list of mono- or bidentate ligands

#### Structure Prediction
* <b>Conformer Search</b> - use the <a href="https://xtb-docs.readthedocs.io/en/latest/crest.html">CREST</a> tool to do automated conformer search
* <b>Transition State Structures</b> - locate potential transition state structures using reaction path interpolation methods


### Selectors
* <b>tm</b>  - select all d-block elements
* <b>connected</b> - expand selection to all atoms with a bonding path to the current selection
* <b>rings</b> - any atom in a ring
* several substituent selectors, including <b>Me</b>, <b>Et</b>, <b>iPr</b>, <b>tBu</b>, <b>Ph</b>, <b>COOCH3</b>, and <b>SuperMes</b>
  * more substituent selectors can be added by adding substituents with the <b>Add to Personal Library</b> tool
  * these selectors depend only on elements and bonding patterns, not atom name, serial number, residue, <i>etc.</i>


### Mouse Modes
These can be activated using the <code>mousemode</code> command or the "More Right Mouse" tab on ChimeraX's toolbar

* <b>select fragment</b> - select everything with a bonding path to clicked atoms or bonds
* <b>select same types</b> - select all fragments that are the same as the clicked fragment
* <b>bond</b> - click and drag from one atom to another to draw a bond
* <b>tsbond</b> - click and drag from one atom to another to draw a forming/breaking bond
* <b>change element</b> - click an atom to change its element or VSEPR shape
* <b>erase structure</b> - click atoms or bonds to delete them
* <b>substitute</b> - click an atom to replace it with a substituent

### Graphical Presets
* <b>ball-stick-endcap</b>       - all non-H atoms are represented as balls and sticks; H atoms are represented as sticks/endcaps
* <b>ball-stick-endcap 2</b> - apply ball-stick-endcap to visible atoms only
* <b>index labels</b>            - label each atom with its index (1-indexed)
* <b>sticks</b> - all heavy atoms are represented as sticks/endcaps, most hydrogen atoms bonded to carbon are hidden
* <b>sticks 2</b> - apply sticks to visible atoms only
* <b>VDW</b> - all atoms are represented as VDW spheres

In SEQCROW's settings (Favorites/Preferences &rarr; Settings... &rarr; SEQCROW), you can automatically apply one of SEQCROW's presets to a molecule opened with SEQCROW (<i>i.e.</i> from an XYZ, log, dat, <i>etc.</i> file).

### Commands
* <b>fuseRing</b> - attach a ring to a structure
* <b>highlight</b> (<b>~highlight</b>) - outline atoms and bonds so they stand out more
* <b>rmsdAlign</b> - calculate RMSD and align molecular structures, similar to ChimeraX's built-in `align` command
* <b>sterimol</b> - print Sterimol L, B<sub>1</sub>, B<sub>2</sub>, B<sub>3</sub>, B<sub>4</sub>, and B<sub>5</sub> of the selected substituents to the log
* <b>substitute</b> - add or change substituents
* <b>tsbond</b> (<b>~tsbond</b>) - display (erase) forming/breaking bond
* <b>percentVolumeBuried</b> - calculate volume buried by ligands around a metal center
* <b>pointGroup</b> - print the point group (Schönflies) to the log

### Running jobs through SEQCROW
QM computations can be run through SEQCROW if the appropriate QM software is installed. If you are running computations on the same computer running ChimeraX, specify the executable for the software in the "SEQCROW Jobs" section of the ChimeraX settings/preferences. If you are running ChimeraX on a computing cluster, jobs can be submitted to run on the cluster. The cluster's queuing software needs to be specified in the "SEQCROW Jobs" section of the ChimeraX settings/preferences. To run the computations, go to the "run" menu on either the QM Input Builder, Transition State Structure, or Conformer Search tool. When running jobs on a cluster, ensure the job submission template is appropriate for how the QM software is installed on the cluster.

## Installation
1. On the ChimeraX menu, go to Tools &rarr; More Tools...
2. find the SEQCROW page and click install
3. restart ChimeraX



## Citation
If you use SEQCROW, please cite the following:

1. A. J. Schaefer, V. M. Ingman, and S. E. Wheeler, "SEQCROW: A ChimeraX Bundle to Facilitate Quantum Chemical Applications to Complex Molecular Systems" <a href="http://dx.doi.org/10.1002/jcc.26700"><i>J. Comp. Chem.</i> <b>42</b>, 1750 (2021)</a>.

2. V. M. Ingman, A. J. Schaefer, L. R. Andreola, and S. E. Wheeler, "QChASM: Quantum Chemistry Automation and Structure Manipulation" <a href="http://dx.doi.org/10.1002/wcms.1510"><i>WIREs Comp. Mol. Sci.</i> <b>11</b>, 
e1510 (2021)</a>

## Other Versions
This is a plug-in for ChimeraX.

### Chimera
The Chimera version of SEQCROW (ChimAARON) can be found on the [Chimera branch](https://github.com/QChASM/ChimAARON/tree/Chimera).

### ChimeraX Stable
you are here

### ChimeraX Daily
For the version on the toolshed, check out the [dev branch](https://github.com/QChASM/ChimAARON/tree/dev)

## Contact
If you have any questions, feel free to contact us at qchasm@uga.edu
