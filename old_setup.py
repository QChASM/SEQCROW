#this is no longer used
#all info should be in bundle_info.xml

"""
python3 setup.py sdist bdist_wheel
cp dist/SEQCROW-0.1-py3-none-any.whl $desktop/
"""

from setuptools import setup, find_packages
import os

synopsis = "Structure Editing and Quantum Chemical Representation and Organization"

description = """
An AaronTools-based plugin for ChimeraX. 

SEQCROW adds the following to ChimeraX:
I/O:
    read XYZ, Gaussian COM, Gaussian LOG files, and Orca output files
    save models to XYZ files

tools:
    AaronTools
        Add to Personal Library  - add substituents, ligands, or rings to your personal AaronTools library
        Browse AaronTools        - browse substituents, ligands, and rings in the AaronTools library
        Process Thermochemistry  - compute thermal corrections for models with vibrational mode information
        Structure Modification   - modify your structure using pieces from the AaronTools library
        Visualize Normal Modes   - display normal modes for models with vibrational mode information as vectors or an animation

    SEQCROW
        Managed Models           - restore models opened through SEQCROW to their original state

selectors:
    tm  - select all transition metals

presets:
    ball-stick-endcap       - all non-H atoms are represented as balls and sticks; H atoms are represented as sticks/endcaps
    index labels            - label each atom with its index (1-indexed)
    sticks                  - all atoms are represented as sticks/endcaps
"""

# ChimeraX classifiers are put in the code as comments
# go find those comments so I don't have to remember to update setup.py
chimerax_classifiers = []
xml_mods = {}
d = os.path.dirname(os.path.realpath(__file__))
src_dir = "src"

ext_mods = []
#pure python hopefully works everywhere
#windows users may have to set USERPROFILE environment variable 
environments = [
    "Environment :: MacOS X :: Aqua",
    "Environment :: Win32 (MS Windows)",
    "Environment :: X11 Applications",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "Operating System :: POSIX :: Linux",
]

setup(
    name="SEQCROW",
    version="0.1",  
    description=synopsis,  
    long_description=description,
    author="QChASM",
    author_email="catalysttrends@uga.edu",
    url="https://github.com/QChASM",
    python_requires=">= 3.5",
    package_dir={
        "SEQCROW": src_dir,
    },
    packages=[
        "SEQCROW", 
        "SEQCROW.tools", 
        "SEQCROW.managers", 
    ],
    ext_modules=ext_mods,
    install_requires=[
        #TODO: add AaronTools (AaronTools should require scipy)
        "ChimeraX-Core >= 0.93",
        "scipy",
        "numpy", 
    ],
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        # https://www.rbvi.ucsf.edu/chimerax/docs/devel/tutorials/bundle_info.html#chimerax-metadata-classifiers
        "Development Status :: 2 - Pre-Alpha",  # TODO: update as appropriate
        "Framework :: ChimeraX",
        "Intended Audience :: Science/Research",
        "License :: Free for non-commercial use",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Chemistry",
        "ChimeraX :: Bundle :: General,Input/Output,Structure Editing,External Program :: 1,1 :: SEQCROW :: ChimAARON,SEQCRO,SEQCROW :: true ",
        "ChimeraX :: Tool :: Build QM Input :: SEQCROW :: Create input file for Gaussian or Orca",
        "ChimeraX :: Tool :: Structure Modification :: AaronTools :: Modify substituents, swap ligands, and close rings, all for the one-time fee of an arm and a leg!",
        "ChimeraX :: Tool :: Browse AaronTools Libraries :: AaronTools :: Browse the AaronTools ligand, substituent, and ring libraries", 
        "ChimeraX :: Tool :: Process Thermochemistry :: AaronTools :: Compute the free energy of a molecule with frequency data", 
        "ChimeraX :: Tool :: Managed Models :: SEQCROW :: see models managed by SEQCROW", 
        "ChimeraX :: Tool :: Add to Personal Library :: AaronTools :: Add to your personal ligand, substituent, and ring libraries", 
        "ChimeraX :: Tool :: Visualize Normal Modes :: AaronTools :: Visualize normal modes from a Gaussian output file as displacement vectors or as an animation", 
        "ChimeraX :: DataFormat :: XYZ :: XYZ :: Molecular structure :: .xyz :: :: :: :: :: XYZ Format :: utf-8",
        "ChimeraX :: Open :: XYZ :: AaronTools :: false :: coordsets:Bool",
        "ChimeraX :: DataFormat :: COM :: Gaussian input file :: Molecular structure :: .com,.gjf :: :: :: :: :: Gaussian input file :: utf-8",
        "ChimeraX :: Open :: COM :: Gaussian input file ::",
        "ChimeraX :: DataFormat :: LOG :: Gaussian output file :: Molecular structure :: .log :: :: :: :: :: Gaussian output file :: utf-8",
        "ChimeraX :: Open :: LOG :: Gaussian output file :: false :: coordsets:Bool",
        "ChimeraX :: DataFormat :: OUT :: Orca output file :: Molecular structure :: .out :: :: :: :: :: Orca output file :: utf-8",
        "ChimeraX :: Open :: OUT :: Orca output file :: false :: coordsets:Bool",
        "ChimeraX :: Manager :: filereader_manager",
        "ChimeraX :: Manager :: seqcrow_ordered_selection_manager", 
    ] + environments,
)
