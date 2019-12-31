from setuptools import setup, Extension
import os, os.path, sys

description = """
ChimAARON but for ChimeraX
"""

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
    name="ChimAARON",
    version="0.1",  
    description="Use useful things from QChASM in ChimeraX!",  
    long_description=description,
    author="QChASM",
    author_email="catalysttrends@uga.edu",
    url="https://github.com/QChASM",
    python_requires=">= 3.5",
    package_dir={
        "ChimAARON": "src",
    },
    packages=[
        "ChimAARON",
    ],
    ext_modules=ext_mods,
    install_requires=[
        #TODO: add AaronTools
        "ChimeraX-Core >= 0.1",
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
        "ChimeraX :: Bundle :: General :: 1,1 :: ChimAARON :: ChimAARON :: ",
        "ChimeraX :: DataFormat :: XYZ :: XYZ :: Molecular structure :: .xyz :: :: :: :: :: XYZ Format :: utf-8",
        "ChimeraX :: DataFormat :: XYZ trajectory :: XYZ trajectory :: Molecular trajectory :: .xyz :: :: :: :: :: XYZ trajectory :: utf-8",
        "ChimeraX :: DataFormat :: COM :: Gaussian input file :: Molecular structure :: .com,.gjf :: :: :: :: :: Gaussian input file :: utf-8",
#        "ChimeraX :: DataFormat :: LOG :: Gaussian output file :: Molecular structure :: .log :: :: :: :: :: Gaussian output file :: utf-8",
        "ChimeraX :: DataFormat :: LOG trajectory :: Gaussian output trajectory :: Molecular trajectory :: .log :: :: :: :: :: Gaussian output file :: utf-8",
        "ChimeraX :: Open :: XYZ :: AaronTools ::",
#        "ChimeraX :: Open :: XYZ trajectory :: AaronTools :: :: coordsets:Bool",
        "ChimeraX :: Save :: XYZ :: AaronTools ::",
#        "ChimeraX :: Open :: LOG :: Gaussian output file ::",
        "ChimeraX :: Open :: LOG trajectory :: Gaussian output trajectory :: :: coordsets:Bool",
        "ChimeraX :: Open :: COM :: Gaussian input file ::",
    ] + environments,
)
