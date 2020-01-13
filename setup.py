
"""
python3 setup.py sdist bdist_wheel
cp dist/ChimAARON-0.1-py3-none-any.whl $desktop/
"""

from setuptools import setup, find_packages
import os

description = """
ChimAARON but for ChimeraX
"""

# ChimeraX classifiers are put in the code as comments
# go find those comments so I don't have to remember to update setup.py
chimerax_classifiers = []
xml_mods = {}
d = os.path.dirname(os.path.realpath(__file__))
src_dir = "src"
src_path = os.path.join(d, src_dir)
for root, dirs, files in os.walk(src_path, topdown=False):
    for f in files:
        file_path = os.path.join(root, f)
        with open(file_path, 'r') as x:
            lines = [line.strip().lstrip('#').strip() for line in x.readlines()]
            
        for line in lines:
            if line.startswith('XML_TAG'):
                #this is a full XML tag
                chimerax_classifiers.append(line.replace('XML_TAG', '').strip())

            elif line.startswith('XML:'):
                #this is a modification to an XML tag
                modification = line.replace('XML:', '').strip()
                classifier, change = [s.strip() for s in modification.split('->')]
                replace_phrase, value = [s.strip() for s in change.split('=')]
                if classifier not in xml_mods:
                    xml_mods[classifier] = {}
                
                if replace_phrase in xml_mods[classifier]:
                    xml_mods[classifier][replace_phrase].append(value)
                else:
                    xml_mods[classifier][replace_phrase] = [value]

#make modifications to XML tags
for classifier in xml_mods:
    mod = xml_mods[classifier]
    print(classifier, mod)
    for i, c in enumerate(chimerax_classifiers):
        if c.startswith(classifier):
            for change in mod:
                chimerax_classifiers[i] = c.replace(change, ','.join(mod[change]))

for c in chimerax_classifiers:
    print(c)

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
        "ChimAARON": src_dir,
    },
    packages=[
        "ChimAARON",
        "ChimAARON.tools",
        "ChimAARON.managers", 
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
        "ChimeraX :: Bundle :: General,Input/Output,Structure Editing :: 1,1 :: ChimAARON :: ChimAARON :: true ",
        *chimerax_classifiers
    ] + environments,
)
