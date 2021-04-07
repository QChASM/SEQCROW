from io import BytesIO
from os.path import basename
import re

import numpy as np
import matplotlib.pyplot as plt

from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.ui.widgets import ColorButton
from chimerax.bild.bild import read_bild
from chimerax.std_commands.coordset_gui import CoordinateSetSlider
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import FloatArg, TupleOf, IntArg
from chimerax.core.commands import run

from AaronTools.atoms import Atom
from AaronTools.const import PHYSICAL
from AaronTools.geometry import Geometry
from AaronTools.pathway import Pathway

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure
from matplotlib import rcParams

from Qt.QtCore import Qt, QRect, QItemSelectionModel 
from Qt.QtGui import QValidator, QFont, QIcon
from Qt.QtWidgets import QSpinBox, QDoubleSpinBox, QGridLayout, QPushButton, QTabWidget, QComboBox, \
                            QTableWidget, QTableView, QWidget, QVBoxLayout, QTableWidgetItem, \
                            QFormLayout, QCheckBox, QHeaderView, QMenuBar, QAction, QFileDialog, QStyle, \
                            QGroupBox, QLabel, QToolBox, QHBoxLayout

from SEQCROW.tools.per_frame_plot import NavigationToolbar
from SEQCROW.utils import iter2str
from SEQCROW.widgets import FilereaderComboBox

#TODO:
#make double clicking something in the table visualize it

rcParams["savefig.dpi"] = 300


class _NormalModeSettings(Settings):
    AUTO_SAVE = {
        'arrow_color': Value((0.0, 1.0, 0.0, 1.0), TupleOf(FloatArg, 4), iter2str),
        'arrow_scale': Value(1.5, FloatArg),
        'anim_scale': Value(0.2, FloatArg),
        'anim_duration': Value(60, IntArg),
        'anim_fps': Value(60, IntArg), 
        'fwhm': Value(5, FloatArg), 
        'peak_type': 'pseudo-Voigt', 
        'plot_type': 'Absorbance',
        'voigt_mix': 0.5,
        'exp_color': Value((0.0, 0.0, 1.0), TupleOf(FloatArg, 3), iter2str),
        'reverse_x': True,
    }


SCALE_LIBS = {
    "NIST CCCBDB": (
        "https://cccbdb.nist.gov/vibscalejust.asp",
        {
            "HF": {
                "STO-3G": 0.817,
                "3-21G": 0.906,
                "3-21G(d)": 0.903,
                "6-31G": 0.903,
                "6-31G(d)": 0.899,
                "6-31G(d,p)": 0.903,
                "6-31+G(d,p)": 0.904,
                "6-311G(d)": 0.904,
                "6-311G(d,p)": 0.909,
                "6-31G(2df,p)": 0.906,
                "6-311+G(3df,2p)": 0.909,
                "6-311+G(3df,2pd)": 0.906,
                "TZVP": 0.909,
                "cc-pVDZ": 0.908,
                "cc-pVTZ": 0.910,
                "cc-pVQZ": 0.908,
                "aug-cc-pVDZ": 0.911,
                "aug-cc-pVTZ": 0.910,
                "aug-cc-pVQZ": 0.909,
                "cc-pV(T+d)Z": 0.910,
                "cc-pCVDZ": 0.916,
                "cc-pCVTZ": 0.913,
                "daug-cc-pVDZ": 0.912,
                "daug-cc-pVTZ": 0.905,
                "Sadlej_pVTZ": 0.913,
            },
            "ROHF": {
                "3-21G": 0.907,
                "3-21G(d)": 0.909,
                "6-31G": 0.895,
                "6-31G(d)": 0.890,
                "6-31G(d,p)": 0.855,
                "6-31+G(d,p)": 0.856,
                "6-311G(d)": 0.856,
                "6-311G(d,p)": 0.913,
                "6-311+G(3df,2p)": 0.909,
                "cc-pVDZ": 0.861,
                "cc-pVTZ": 0.901,
            },
            "LSDA": {
                "STO-3G": 0.896,
                "3-21G": 0.984,
                "3-21G(d)": 0.982,
                "6-31G": 0.980,
                "6-31G(d)": 0.981,
                "6-31G(d,p)": 0.981,
                "6-31+G(d,p)": 0.985,
                "6-311G(d)": 0.984,
                "6-311G(d,p)": 0.988,
                "6-31G(2df,p)": 0.984,
                "TZVP": 0.988,
                "cc-pVDZ": 0.989,
                "cc-pVTZ": 0.989,
                "aug-cc-pVDZ": 0.989,
                "aug-cc-pVTZ": 0.991,
                "cc-pV(T+d)Z": 0.990,
            },
            "BLYP": {
                "STO-3G": 0.925,
                "3-21G": 0.995,
                "3-21G(d)": 0.994,
                "6-31G": 0.992,
                "6-31G(d)": 0.992,
                "6-31G(d,p)": 0.992,
                "6-31+G(d,p)": 0.995,
                "6-311G(d)": 0.998,
                "6-311G(d,p)": 0.996,
                "6-31G(2df,p)": 0.995,
                "6-311+G(3df,2p)": 0.995,
                "TZVP": 0.998,
                "cc-pVDZ": 1.002,
                "cc-pVTZ": 0.997,
                "aug-cc-pVDZ": 0.998,
                "aug-cc-pVTZ": 0.997,
                "cc-pV(T+d)Z": 0.996,
            },
            "B1B95": {
                "STO-3G": 0.883,
                "3-21G": 0.957,
                "3-21G(d)": 0.955,
                "6-31G": 0.954,
                "6-31G(d)": 0.949,
                "6-31G(d,p)": 0.955,
                "6-31+G(d,p)": 0.957,
                "6-311G(d)": 0.959,
                "6-311G(d,p)": 0.960,
                "6-31G(2df,p)": 0.958,
                "TZVP": 0.957,
                "cc-pVDZ": 0.961,
                "cc-pVTZ": 0.957,
                "aug-cc-pVDZ": 0.958,
                "aug-cc-pVTZ": 0.959,
                "cc-pV(T+d)Z": 0.957,
            },
            "B3LYP": {
                "STO-3G": 0.892,
                "3-21G": 0.965,
                "3-21G(d)": 0.962,
                "6-31G": 0.962,
                "6-31G(d)": 0.960,
                "6-31G(d,p)": 0.961,
                "6-31+G(d,p)": 0.964,
                "6-311G(d)": 0.966,
                "6-311G(d,p)": 0.967,
                "6-31G(2df,p)": 0.965,
                "6-311+G(3df,2p)": 0.967,
                "6-311+G(3df,2pd)": 0.964,
                "TZVP": 0.965,
                "cc-pVDZ": 0.970,
                "cc-pVTZ": 0.967,
                "cc-pVQZ": 0.969,
                "aug-cc-pVDZ": 0.970,
                "aug-cc-pVTZ": 0.968,
                "aug-cc-pVQZ": 0.969,
                "cc-pV(T+d)Z": 0.965,
                "Sadlej_pVTZ": 0.972,
            },
            "B3LYP (ultrafine grid)": {
                "STO-3G": 0.892,
                "3-21G": 0.965,
                "3-21G(d)": 0.962,
                "6-31G": 0.962,
                "6-31G(d)": 0.958,
                "6-31G(d,p)": 0.961,
                "6-31+G(d,p)": 0.963,
                "6-311G(d)": 0.966,
                "6-311G(d,p)": 0.967,
                "6-31G(2df,p)": 0.965,
                "6-311+G(3df,2pd)": 0.970,
                "TZVP": 0.963,
                "cc-pVDZ": 0.970,
                "cc-pVTZ": 0.967,
                "aug-cc-pVDZ": 0.970,
                "aug-cc-pVTZ": 0.968,
            },
            "B3PW91": {
                "STO-3G": 0.885,
                "3-21G": 0.961,
                "3-21G(d)": 0.959,
                "6-31G": 0.958,
                "6-31G(d)": 0.957,
                "6-31G(d,p)": 0.958,
                "6-31+G(d,p)": 0.960,
                "6-311G(d)": 0.963,
                "6-311G(d,p)": 0.963,
                "6-31G(2df,p)": 0.961,
                "6-311+G(3df,2p)": 0.957,
                "TZVP": 0.964,
                "cc-pVDZ": 0.965,
                "cc-pVTZ": 0.962,
                "aug-cc-pVDZ": 0.965,
                "aug-cc-pVTZ": 0.965,
                "cc-pV(T+d)Z": 0.964,
            },
            "mPW1PW91": {
                "STO-3G": 0.879,
                "3-21G": 0.955,
                "3-21G(d)": 0.950,
                "6-31G": 0.947,
                "6-31G(d)": 0.948,
                "6-31G(d,p)": 0.952,
                "6-31+G(d,p)": 0.952,
                "6-311G(d)": 0.954,
                "6-311G(d,p)": 0.957,
                "6-31G(2df,p)": 0.955,
                "TZVP": 0.954,
                "cc-pVDZ": 0.958,
                "cc-pVTZ": 0.959,
                "aug-cc-pVDZ": 0.958,
                "aug-cc-pVTZ": 0.958,
                "cc-pV(T+d)Z": 0.958,
            },
            "M06-2X": {
                "3-21G": 0.959,
                "3-21G(d)": 0.947,
                "6-31G(d)": 0.947,
                "6-31G(d,p)": 0.950,
                "6-31+G(d,p)": 0.952,
                "6-31G(2df,p)": 0.952,
                "TZVP": 0.946,
                "cc-pVTZ": 0.955,
                "aug-cc-pVTZ": 0.956,
            },
            "PBEPBE": {
                "STO-3G": 0.914,
                "3-21G": 0.991,
                "3-21G(d)": 0.954,
                "6-31G": 0.986,
                "6-31G(d)": 0.986,
                "6-31G(d,p)": 0.986,
                "6-31+G(d,p)": 0.989,
                "6-311G(d)": 0.990,
                "6-311G(d,p)": 0.991,
                "6-31G(2df,p)": 0.990,
                "6-311+G(3df,2p)": 0.992,
                "6-311+G(3df,2pd)": 0.990,
                "TZVP": 0.989,
                "cc-pVDZ": 0.994,
                "cc-pVTZ": 0.993,
                "aug-cc-pVDZ": 0.994,
                "aug-cc-pVTZ": 0.994,
                "cc-pV(T+d)Z": 0.993,
                "Sadlej_pVTZ": 0.995,
            },
            "PBEPBE (ultrafine grid)": {
                "STO-3G": 0.914,
                "3-21G": 0.991,
                "3-21G(d)": 0.954,
                "6-31G": 0.986,
                "6-31G(d)": 0.984,
                "6-31G(d,p)": 0.986,
                "6-31+G(d,p)": 0.989,
                "6-311G(d)": 0.990,
                "6-311G(d,p)": 0.991,
                "6-31G(2df,p)": 0.990,
                "6-311+G(3df,2pd)": 0.990,
                "TZVP": 0.989,
                "cc-pVDZ": 0.994,
                "cc-pVTZ": 0.993,
                "aug-cc-pVDZ": 0.994,
                "aug-cc-pVTZ": 0.989,
            },
            "PBE0": {
                "STO-3G": 0.882,
                "3-21G": 0.960,
                "3-21G(d)": 0.960,
                "6-31G": 0.956,
                "6-31G(d)": 0.950,
                "6-31G(d,p)": 0.953,
                "6-31+G(d,p)": 0.955,
                "6-311G(d)": 0.959,
                "6-311G(d,p)": 0.959,
                "6-31G(2df,p)": 0.957,
                "TZVP": 0.960,
                "cc-pVDZ": 0.962,
                "cc-pVTZ": 0.961,
                "aug-cc-pVDZ": 0.962,
                "aug-cc-pVTZ": 0.962,
            },
            "HSEh1PBE": {
                "STO-3G": 0.883,
                "3-21G": 0.963,
                "3-21G(d)": 0.960,
                "6-31G": 0.957,
                "6-31G(d)": 0.951,
                "6-31G(d,p)": 0.954,
                "6-31+G(d,p)": 0.955,
                "6-311G(d)": 0.960,
                "6-311G(d,p)": 0.960,
                "6-31G(2df,p)": 0.958,
                "TZVP": 0.960,
                "cc-pVDZ": 0.962,
                "cc-pVTZ": 0.961,
                "aug-cc-pVDZ": 0.962,
                "aug-cc-pVTZ": 0.962,
            },
            "TPSSh": {
                "3-21G": 0.969,
                "3-21G(d)": 0.966,
                "6-31G": 0.962,
                "6-31G(d)": 0.959,
                "6-31G(d,p)": 0.959,
                "6-31+G(d,p)": 0.963,
                "6-311G(d)": 0.963,
                "6-31G(2df,p)": 0.965,
                "TZVP": 0.964,
                "cc-pVDZ": 0.972,
                "cc-pVTZ": 0.968,
                "aug-cc-pVDZ": 0.967,
                "aug-cc-pVTZ": 0.965,
            },
            "ωB97X-D": {
                "3-21G(d)": 0.948,
                "6-31G(d)": 0.949,
                "6-31+G(d,p)": 0.952,
                "6-311G(d,p)": 0.957,
                "TZVP": 0.955,
                "cc-pVDZ": 0.953,
                "cc-pVTZ": 0.956,
                "aug-cc-pVDZ": 0.957,
                "aug-cc-pVTZ": 0.957,
            },
            "B97-D3": {
                "3-21G": 0.983,
                "6-31G(d)": 0.980,
                "6-31+G(d,p)": 0.983,
                "6-311G(d,p)": 0.986,
                "6-311+G(3df,2p)": 0.987,
                "6-311+G(3df,2pd)": 0.986,
                "TZVP": 0.986,
                "cc-pVDZ": 0.992,
                "cc-pVTZ": 0.986,
                "aug-cc-pVTZ": 0.985,
            },
            "MP2": {
                "STO-3G": 0.872,
                "3-21G": 0.955,
                "3-21G(d)": 0.951,
                "6-31G": 0.957,
                "6-31G(d)": 0.943,
                "6-31G(d,p)": 0.937,
                "6-31+G(d,p)": 0.941,
                "6-311G(d)": 0.950,
                "6-311G(d,p)": 0.950,
                "6-31G(2df,p)": 0.945,
                "6-311+G(3df,2p)": 0.943,
                "6-311+G(3df,2pd)": 0.950,
                "TZVP": 0.948,
                "cc-pVDZ": 0.953,
                "cc-pVTZ": 0.950,
                "cc-pVQZ": 0.948,
                "aug-cc-pVDZ": 0.959,
                "aug-cc-pVTZ": 0.953,
                "aug-cc-pVQZ": 0.950,
                "cc-pV(T+d)Z": 0.953,
                "cc-pCVDZ": 0.956,
                "cc-pCVTZ": 0.953,
                "Sadlej_pVTZ": 0.962,
            },
            "MP2=Full": {
                "STO-3G": 0.889,
                "3-21G": 0.955,
                "3-21G(d)": 0.948,
                "6-31G": 0.950,
                "6-31G(d)": 0.942,
                "6-31G(d,p)": 0.934,
                "6-31+G(d,p)": 0.939,
                "6-311G(d)": 0.947,
                "6-311G(d,p)": 0.949,
                "6-31G(2df,p)": 0.940,
                "6-311+G(3df,2p)": 0.943,
                "TZVP": 0.953,
                "cc-pVDZ": 0.950,
                "cc-pVTZ": 0.949,
                "cc-pVQZ": 0.957,
                "aug-cc-pVDZ": 0.969,
                "aug-cc-pVTZ": 0.951,
                "aug-cc-pVQZ": 0.956,
                "cc-pV(T+d)Z": 0.948,
                "cc-pCVDZ": 0.955,
                "cc-pCVTZ": 0.951,
            },
            "MP3": {
                "STO-3G": 0.894,
                "3-21G": 0.968,
                "3-21G(d)": 0.965,
                "6-31G": 0.966,
                "6-31G(d)": 0.939,
                "6-31G(d,p)": 0.935,
                "6-31+G(d,p)": 0.931,
                "TZVP": 0.935,
                "cc-pVDZ": 0.948,
                "cc-pVTZ": 0.945,
            },
            "MP3=Full": {
                "6-31G(d)": 0.938,
                "6-31+G(d,p)": 0.932,
                "6-311G(d)": 0.904,
                "TZVP": 0.934,
                "cc-pVDZ": 0.940,
                "cc-pVTZ": 0.933,
            },
            "MP4": {
                "3-21G": 0.970,
                "3-21G(d)": 0.944,
                "6-31G": 0.944,
                "6-31G(d)": 0.955,
                "6-31G(d,p)": 0.944,
                "6-31+G(d,p)": 0.944,
                "6-311G(d)": 0.959,
                "6-311G(d,p)": 0.970,
                "6-311+G(3df,2p)": 0.944,
                "TZVP": 0.963,
                "cc-pVDZ": 0.967,
                "cc-pVTZ": 0.969,
                "aug-cc-pVDZ": 0.977,
                "aug-cc-pVTZ": 0.973,
            },
            "MP4=Full": {
                "3-21G": 0.979,
                "6-31G(d)": 0.962,
                "6-311G(d,p)": 0.962,
                "TZVP": 0.966,
                "cc-pVDZ": 0.965,
                "cc-pVTZ": 0.963,
                "aug-cc-pVDZ": 0.975,
                "aug-cc-pVTZ": 0.969,
            },
            "B2PLYP": {
                "6-31G(d)": 0.949,
                "6-31+G(d,p)": 0.952,
                "6-31G(2df,p)": 0.955,
                "TZVP": 0.954,
                "cc-pVDZ": 0.958,
                "cc-pVTZ": 0.959,
                "cc-pVQZ": 0.957,
                "aug-cc-pVTZ": 0.961,
            },
            "B2PLYP=Full": {
                "3-21G": 0.952,
                "6-31G(d)": 0.948,
                "6-31+G(d,p)": 0.951,
                "6-311G(d)": 0.904,
                "TZVP": 0.954,
                "cc-pVDZ": 0.959,
                "cc-pVTZ": 0.956,
                "aug-cc-pVDZ": 0.962,
                "aug-cc-pVTZ": 0.959,
            },
            "B2PLYP=Full (ultrafine grid)": {
                "6-31G(d)": 0.949,
                "cc-pVDZ": 0.958,
                "cc-pVTZ": 0.955,
                "aug-cc-pVDZ": 0.962,
                "aug-cc-pVTZ": 0.959,
            },
            "CID": {
                "3-21G": 0.932,
                "3-21G(d)": 0.931,
                "6-31G": 0.935,
                "6-31G(d)": 0.924,
                "6-31G(d,p)": 0.924,
                "6-31+G(d,p)": 0.924,
                "6-311G(d)": 0.929,
                "6-311+G(3df,2p)": 0.924,
                "cc-pVDZ": 0.924,
                "cc-pVTZ": 0.927,
            },
            "CISD": {
                "3-21G": 0.941,
                "3-21G(d)": 0.934,
                "6-31G": 0.938,
                "6-31G(d)": 0.926,
                "6-31G(d,p)": 0.918,
                "6-31+G(d,p)": 0.922,
                "6-311G(d)": 0.925,
                "6-311+G(3df,2p)": 0.922,
                "cc-pVDZ": 0.922,
                "cc-pVTZ": 0.930,
            },
            "QCISD": {
                "3-21G": 0.969,
                "3-21G(d)": 0.961,
                "6-31G": 0.964,
                "6-31G(d)": 0.952,
                "6-31G(d,p)": 0.941,
                "6-31+G(d,p)": 0.945,
                "6-311G(d)": 0.957,
                "6-311G(d,p)": 0.954,
                "6-31G(2df,p)": 0.947,
                "6-311+G(3df,2p)": 0.954,
                "TZVP": 0.955,
                "cc-pVDZ": 0.959,
                "cc-pVTZ": 0.956,
                "aug-cc-pVDZ": 0.969,
                "aug-cc-pVTZ": 0.962,
                "cc-pV(T+d)Z": 0.955,
            },
            "QCISD(T)": {
                "3-21G": 0.954,
                "3-21G(d)": 0.954,
                "6-31G": 0.954,
                "6-31G(d)": 0.959,
                "6-31G(d,p)": 0.937,
                "6-31+G(d,p)": 0.939,
                "6-311G(d)": 0.963,
                "6-311+G(3df,2p)": 0.954,
                "TZVP": 0.963,
                "cc-pVDZ": 0.953,
                "cc-pVTZ": 0.949,
                "aug-cc-pVDZ": 0.978,
                "aug-cc-pVTZ": 0.967,
            },
            "QCISD(T)=Full": {
                "cc-pVDZ": 0.959,
                "cc-pVTZ": 0.957,
                "aug-cc-pVDZ": 0.970,
            },
            "CCD": {
                "3-21G": 0.972,
                "3-21G(d)": 0.957,
                "6-31G": 0.960,
                "6-31G(d)": 0.947,
                "6-31G(d,p)": 0.938,
                "6-31+G(d,p)": 0.942,
                "6-311G(d)": 0.955,
                "6-311G(d,p)": 0.955,
                "6-31G(2df,p)": 0.947,
                "6-311+G(3df,2p)": 0.943,
                "TZVP": 0.948,
                "cc-pVDZ": 0.957,
                "cc-pVTZ": 0.934,
                "aug-cc-pVDZ": 0.965,
                "aug-cc-pVTZ": 0.957,
                "cc-pV(T+d)Z": 0.952,
            },
            "CCSD": {
                "3-21G": 0.943,
                "3-21G(d)": 0.943,
                "6-31G": 0.943,
                "6-31G(d)": 0.944,
                "6-31G(d,p)": 0.933,
                "6-31+G(d,p)": 0.934,
                "6-311G(d)": 0.954,
                "6-31G(2df,p)": 0.946,
                "6-311+G(3df,2p)": 0.943,
                "TZVP": 0.954,
                "cc-pVDZ": 0.947,
                "cc-pVTZ": 0.941,
                "cc-pVQZ": 0.951,
                "aug-cc-pVDZ": 0.963,
                "aug-cc-pVTZ": 0.956,
                "aug-cc-pVQZ": 0.953,
            },
            "CCSD=Full": {
                "6-31G(d)": 0.950,
                "6-31G(2df,p)": 0.942,
                "TZVP": 0.948,
                "cc-pVTZ": 0.948,
                "aug-cc-pVTZ": 0.951,
            },
            "CCSD(T)": {
                "3-21G": 0.991,
                "3-21G(d)": 0.943,
                "6-31G": 0.943,
                "6-31G(d)": 0.962,
                "6-31G(d,p)": 0.949,
                "6-31+G(d,p)": 0.960,
                "6-311G(d)": 0.963,
                "6-311G(d,p)": 0.965,
                "6-311+G(3df,2p)": 0.987,
                "TZVP": 0.963,
                "cc-pVDZ": 0.979,
                "cc-pVTZ": 0.975,
                "cc-pVQZ": 0.970,
                "aug-cc-pVDZ": 0.963,
                "aug-cc-pVTZ": 0.970,
                "aug-cc-pVQZ": 0.961,
                "cc-pV(T+d)Z": 0.965,
                "cc-pCVDZ": 0.971,
                "cc-pCVTZ": 0.966,
            },
            "CCSD(T)=Full": {
                "6-31G(d)": 0.971,
                "TZVP": 0.956,
                "cc-pVDZ": 0.963,
                "cc-pVTZ": 0.958,
                "cc-pVQZ": 0.966,
                "aug-cc-pVDZ": 0.971,
                "aug-cc-pVTZ": 0.964,
                "aug-cc-pVQZ": 0.958,
                "cc-pV(T+d)Z": 0.959,
                "cc-pCVDZ": 0.969,
                "cc-pCVTZ": 0.966,
            },
            "AM1": 0.954,
            "PM3": 0.974,
            "PM6": 1.062,
            "AMBER": 1.000,
            "DREIDING": 0.936,
        }
    ),
    "UMN CTC (v4)": (
        "https://comp.chem.umn.edu/freqscale/index.html",
        {
            "B1B95": {
                "6-31+G(d,p)": 0.946,
                "MG3S": 0.948,
            },
            "B1LYP": {
                "MG3S": 0.955,
            },
            "B3LYP": {
                "6-31G(d)": 0.952,
                "6-31G(2df,2p)": 0.955,
                "MG3S": 0.960,
                "aug-cc-pVTZ": 0.959,
                "def2-TZVP": 0.960,
                "ma-TZVP": 0.960,
            },
            "B3P86": {
                "6-31G(d)": 0.946,
            },
            "B3PW91": {
                "6-31G(d)": 0.947,
            },
            "B97-3": {
                "def2-TZVP": 0.949,
                "ma-TZVP": 0.950,
                "MG3S": 0.947,
            },
            "B98": {
                "def2-TZVP": 0.958,
                "ma-TZVP": 0.959,
                "MG3S": 0.956,
            },
            "BB1K": {
                "MG3S": 0.932,
                "6-31+G(d,p)": 0.929,
            },
            "BB95": {
                "6-31+G(d,p)": 0.985,
                "MG3S": 0.986,
            },
            "BLYP": {
                "6-311G(df,p)": 0.987,
                "6-31G(d)": 0.983,
                "MG3S": 0.991,
            },
            "BMK": {
                "ma-TZVP": 0.947,
                "MG3S": 0.945,
            },
            "BP86": {
                "6-31G(d)": 0.981,
                "ma-TZVP": 0.988,
            },
            "BPW60": {
                "6-311+G(d,p)": 0.947,
            },
            "BPW63": {
                "MG3S": 0.936,
            },
            "CAM-B3LYP": {
                "ma-TZVP": 0.951,
            },
            "CCSD(T)": {
                "jul-cc-pVTZ": 0.958,
                "aug-cc-pVTZ": 0.961,
            },
            "CCSD(T)-F12": {
                "jul-cc-pVTZ": 0.955,
            },
            "CCSD(T)-F12a": {
                "cc-pVDZ-F12": 0.957,
                "cc-pVTZ-F12": 0.958,
            },
            "CCSD": {
                "jul-cc-pVTZ": 0.948,
            },
            "CCSD-F12": {
                "jul-cc-pVTZ": 0.946,
            },
            "G96LYP80": {
                "6-311+G(d,p)": 0.924,
            },
            "G96LYP82": {
                "MG3S": 0.920,
            },
            "GAM": {
                "def2-TZVP": 0.955,
                "ma-TZVP": 0.956,
            },
            "HF": {
                "3-21G": 0.895,
                "6-31+G(d)": 0.887,
                "6-31+G(d,p)": 0.891,
                "6-311G(d,p)": 0.896,
                "6-311G(df,p)": 0.896,
                "6-31G(d)": 0.885,
                "6-31G(d,p)": 0.889,
                "MG3S": 0.895,
            },
            "HFLYP": {
                "MG3S": 0.876,
            },
            "HSEh1PBE": {
                "ma-TZVP": 0.954,
            },
            "M05": {
                "aug-cc-pVTZ": 0.953,
                "def2-TZVP": 0.952,
                "ma-TZVP": 0.954,
                "maug-cc-pVTZ": 0.953,
                "MG3S": 0.951,
            },
            "M05-2X": {
                "6-31+G(d,p)": 0.936,
                "aug-cc-pVTZ": 0.939,
                "def2-TZVPP": 0.938,
                "ma-TZVP": 0.940,
                "maug-cc-pVTZ": 0.939,
                "MG3S": 0.937,
            },
            "M06": {
                "6-31+G(d,p)": 0.950,
                "aug-cc-pVTZ": 0.958,
                "def2-TZVP": 0.956,
                "def2-TZVPP": 0.963,
                "ma-TZVP": 0.956,
                "maug-cc-pVTZ": 0.956,
                "MG3S": 0.955,
            },
            "M06-2X": {
                "6-31+G(d,p)": 0.940,
                "6-311+G(d,p)": 0.944,
                "6-311++G(d,p)": 0.944,
                "aug-cc-pVDZ": 0.954,
                "aug-cc-pVTZ": 0.946,
                "def2-TZVP": 0.946,
                "def2-QZVP": 0.945,
                "def2-TZVPP": 0.945,
                "jul-cc-pVDZ": 0.952,
                "jul-cc-pVTZ": 0.946,
                "jun-cc-pVDZ": 0.951,
                "jun-cc-pVTZ": 0.946,
                "ma-TZVP": 0.947,
                "maug-cc-pV(T+d)Z": 0.945,
                "MG3S": 0.944,
            },
            "M06-HF": {
                "6-31+G(d,p)": 0.931,
                "aug-cc-pVTZ": 0.936,
                "def2-TZVPP": 0.932,
                "ma-TZVP": 0.932,
                "maug-cc-pVTZ": 0.934,
                "MG3S": 0.930,
            },
            "M06-L": {
                "6-31G(d,p)": 0.952,
                "6-31+G(d,p)": 0.953,
                "aug-cc-pVTZ": 0.955,
                "aug-cc-pV(T+d)Z": 0.955,
                "aug-cc-pVTZ-pp": 0.955,
                "def2-TZVP": 0.951,
                "def2-TZVPP": 0.956,
                "ma-TZVP": 0.956,
                "maug-cc-pVTZ": 0.952,
                "MG3S": 0.958,
            },
            "M06-L(DKH2)": {
                "aug-cc-pwcVTZ-DK": 0.959,
            },
            "M08-HX": {
                "6-31+G(d,p)": 0.944,
                "aug-cc-pVTZ": 0.950,
                "cc-pVTZ+": 0.946,
                "def2-TZVPP": 0.945,
                "jun-cc-pVTZ": 0.947,
                "ma-TZVP": 0.951,
                "maug-cc-pVTZ": 0.951,
                "MG3S": 0.946,
            },
            "M08-SO": {
                "6-31+G(d,p)": 0.951,
                "aug-cc-pVTZ": 0.959,
                "cc-pVTZ+": 0.956,
                "def2-TZVPP": 0.954,
                "ma-TZVP": 0.958,
                "maug-cc-pVTZ": 0.957,
                "MG3": 0.959,
                "MG3S": 0.956,
                "MG3SXP": 0.957,
            }, 
            "M11-L": {
                "maug-cc-pVTZ": 0.962,
            }, 
            "MN11-L": {
                "MG3S": 0.959,
            },
            "MN12-L": {
                "jul-cc-pVDZ": 0.950,
                "MG3S": 0.959,
            },
            "MN12-SX": {
                "6-311++G(d,p)": 0.947,
                "jul-cc-pVDZ": 0.954,
            },
            "MN15-L": {
                "MG3S": 0.952,
                "maug-cc-pVTZ": 0.954,
            },
            "MOHLYP": {
                "ma-TZVP": 1.000,
                "MG3S": 0.995,
            },
            "MP2 (frozen core)": {
                "6-31+G(d,p)": 0.943,
                "6-311G(d,p)": 0.945,
                "6-31G(d)": 0.939,
                "6-31G(d,p)": 0.933,
                "cc-pVDZ": 0.952,
                "cc-pVTZ": 0.953,
            },
            "MP2 (full)": {
                "6-31G(d)": 0.938,
            },
            "MP4 (SDQ)": {
                "jul-cc-pVTZ": 0.948,
            },
            "MPW1B95": {
                "6-31+G(d,p)": 0.945,
                "MG3": 0.945,
                "MG3S": 0.947,
            },
            "MPW1K": {
                "6-31+G(d,p)": 0.924,
                "aug-cc-pVDTZ": 0.934,
                "aug-cc-pVTZ": 0.930,
                "jul-cc-pVDZ": 0.932,
                "jul-cc-pVTZ": 0.929,
                "jun-cc-pVDZ": 0.930,
                "jun-cc-pVTZ": 0.929,
                "ma-TZVP": 0.931,
                "MG3": 0.928,
                "MG3S": 0.931,
                "MIDI!": 0.928,
                "MIDIY": 0.922,
            },
            "MPW3LYP": {
                "6-31+G(d,p)": 0.955,
                "6-311+G(2d,p)": 0.960,
                "6-31G(d)": 0.951,
                "ma-TZVP": 0.960,
                "MG3S": 0.956,
            },
            "MPW74": {
                "6-311+G(d,p)": 0.925,
            },
            "MPW76": {
                "MG3S": 0.956,
            },
            "MPWB1K": {
                "6-31+G(d,p)": 0.926,
                "MG3S": 0.929
            },
            "MPWLYP1M": {
                "ma-TZVP": 0.983,
            },
            "OreLYP": {
                "ma-TZVP": 0.984,
                "def2-TZVP": 0.982,
            },
            "PBE": {
                "def2-TZVP": 0.985,
                "MG3S": 0.985,
                "ma-TZVP": 0.987,
            },
            "PBE0": {
                "MG3S": 0.950,
            },
            "PBE1KCIS": {
                "MG3": 0.955,
                "MG3S": 0.955,
            },
            "PW6B95": {
                "def2-TZVP": 0.949,
            },
            "PWB6K": {
                "cc-pVDZ": 0.928,
            },
            "QCISD": {
                "cc-pVTZ": 0.950,
                "MG3S": 0.953,
            },
            "QCISD(FC)": {
                "6-31G(d)": 0.948,
            },
            "QCISD(T)": {
                "aug-cc-pVQZ": 0.963,
            },
            "revTPSS": {
                "def2-TZVP": 0.972,
                "ma-TZVP": 0.973,
            },
            "SOGGA": {
                "ma-TZVP": 0.991,
            },
            "τHCTHhyb": {
                "ma-TZVP": 0.963,
            },
            "TPSS1KCIS": {
                "def2-TZVP": 0.956,
                "ma-TZVP": 0.957,
            },
            "TPSSh": {
                "MG3S": 0.963,
            },
            "VSXC": {
                "MG3S": 0.962,
            },
            "ωB97": {
                "def2-TZVP": 0.944,
                "ma-TZVP": 0.945,
            },
            "ωB97X-D": {
                "def2-TZVP": 0.945,
                "ma-TZVP": 0.946,
                "maug-cc-pVTZ": 0.949,
            },
            "X1B95": {
                "6-31+G(d,p)": 0.943,
                "MG3S": 0.946,
            },
            "XB1K": {
                "6-31+G(d,p)": 0.927,
                "MG3S": 0.930,
            },
            "AM1": 0.923,
            "PM3": 0.916,
            "PM6": 1.050,
        }
    ),
}


class FPSSpinBox(QSpinBox):
    """spinbox that makes sure the value goes evenly into 60"""
    def validate(self, text, pos):
        if pos < len(text) or pos == 0:
            return (QValidator.Intermediate, text, pos)
        
        try:
            value = int(text)
        except:
            return (QValidator.Invalid, text, pos)
        
        if 60 % value != 0:
            if pos == 1:
                return (QValidator.Intermediate, text, pos)
            else:
                return (QValidator.Invalid, text, pos)
        elif value > self.maximum():
            return (QValidator.Invalid, text, pos)
        elif value < self.minimum():
            return (QValidator.Invalid, text, pos)
        else:
            return (QValidator.Acceptable, text, pos)
    
    def fixUp(self, text):
        try:
            value = int(text)
            new_value = 1
            for i in range(1, value+1):
                if 60 % i == 0:
                    new_value = i
            
            self.setValue(new_value)
        
        except:
            pass
    
    def stepBy(self, step):
        val = self.value()
        while step > 0:
            val += 1
            while 60 % val != 0:
                val += 1
            step -= 1
        
        while step < 0:
            val -= 1
            while 60 % val != 0:
                val -= 1
            step += 1
        
        self.setValue(val)


class FreqTableWidgetItem(QTableWidgetItem):
    def setData(self, role, value):
        super().setData(role, value)
        
        if role == Qt.DisplayRole:
            font = QFont()
            if "i" in value:
                font.setItalic(True)
            else:
                font.setItalic(False)
            
            self.setFont(font)

    def __lt__(self, other):
        return self.data(Qt.UserRole) < other.data(Qt.UserRole)


class NormalModes(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    help = "https://github.com/QChASM/SEQCROW/wiki/Visualize-Normal-Modes-Tool"
    
    def __init__(self, session, name):
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)        
        
        self.vec_mw_bool = False
        self.ir_plot = None
        self.match_peaks = None
        
        self.settings = _NormalModeSettings(session, name)
        
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()
        
        #select which molecule's frequencies to visualize
        model_selector = FilereaderComboBox(self.session, otherItems=['frequency'])

        model_selector.currentIndexChanged.connect(self.create_freq_table)
        self.model_selector = model_selector
        layout.addWidget(model_selector)
        
        #table that lists frequencies
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Frequency (cm\u207b\u00b9)", "symmetry", "IR intensity"])
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QTableView.SelectRows)
        table.setSelectionMode(QTableView.SingleSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        for i in range(0, 3):
            table.resizeColumnToContents(i)
        
        table.horizontalHeader().setStretchLastSection(False)            
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)        
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)        
        
        layout.addWidget(table)
        self.table = table
        self.table.itemDoubleClicked.connect(self.highlight_ir_plot)
        self.table.itemSelectionChanged.connect(self.highlight_ir_plot)
        
        #tab thing to select animation or vectors
        self.display_tabs = QTabWidget()

        vector_tab = QWidget()
        vector_opts = QFormLayout(vector_tab)
        
        self.vec_scale = QDoubleSpinBox()
        self.vec_scale.setDecimals(1)
        self.vec_scale.setRange(-100.0, 100.0)
        self.vec_scale.setValue(self.settings.arrow_scale)
        self.vec_scale.setSuffix(" \u212B")
        self.vec_scale.setSingleStep(0.1)
        self.vec_scale.setToolTip("vectors will be scaled so that this is the length of the longest vector\nvectors shorter than 0.1 \u212B will not be displayed")
        vector_opts.addRow("vector scale:", self.vec_scale)
        
        self.vec_use_mass_weighted = QCheckBox()
        self.vec_use_mass_weighted.stateChanged.connect(self.change_mw_option)
        self.vec_use_mass_weighted.setToolTip("if checked, vectors will show mass-weighted displacements")
        vector_opts.addRow("use mass-weighted:", self.vec_use_mass_weighted)

        self.vector_color = ColorButton(has_alpha_channel=True, max_size=(16, 16))
        self.vector_color.set_color(self.settings.arrow_color)
        vector_opts.addRow("vector color:", self.vector_color)

        show_vec_button = QPushButton("display selected mode")
        show_vec_button.clicked.connect(self.show_vec)
        vector_opts.addRow(show_vec_button)
        self.show_vec_button = show_vec_button

        close_vec_button = QPushButton("remove selected mode vectors")
        close_vec_button.clicked.connect(self.close_vec)
        vector_opts.addRow(close_vec_button)
        self.close_vec_button = close_vec_button

        stop_anim_button = QPushButton("reset coordinates")
        stop_anim_button.clicked.connect(self.stop_anim)
        vector_opts.addRow(stop_anim_button)
        
        
        animate_tab = QWidget()
        anim_opts = QFormLayout(animate_tab)
        
        self.anim_scale = QDoubleSpinBox()
        self.anim_scale.setSingleStep(0.05)
        self.anim_scale.setRange(0.01, 100.0)
        self.anim_scale.setValue(self.settings.anim_scale)
        self.anim_scale.setSuffix(" \u212B")
        self.anim_scale.setToolTip("maximum distance an atom is displaced from equilibrium")
        anim_opts.addRow("max. displacement:", self.anim_scale)
        
        self.anim_duration = QSpinBox()
        self.anim_duration.setRange(1, 1001)
        self.anim_duration.setValue(self.settings.anim_duration)
        self.anim_duration.setToolTip("number of frames in animation\nmore frames results in a smoother animation")
        self.anim_duration.setSingleStep(10)
        anim_opts.addRow("frames:", self.anim_duration)
        
        self.anim_fps = FPSSpinBox()
        self.anim_fps.setRange(1, 60)
        self.anim_fps.setValue(self.settings.anim_fps)
        self.anim_fps.setToolTip(
            "animation and recorded movie frames per second\n" +
            "60 must be evenly divisible by this number\n" +
            "animation speed in ChimeraX might be slower, depending on your hardware or graphics settings"
        )
        anim_opts.addRow("animation FPS:", self.anim_fps)

        show_anim_button = QPushButton("animate selected mode")
        show_anim_button.clicked.connect(self.show_anim)
        anim_opts.addRow(show_anim_button)
        self.show_anim_button = show_anim_button

        stop_anim_button = QPushButton("stop animation")
        stop_anim_button.clicked.connect(self.stop_anim)
        anim_opts.addRow(stop_anim_button)
        self.stop_anim_button = stop_anim_button

        # IR plot options
        ir_tab = QWidget()
        ir_layout = QFormLayout(ir_tab)
        
        self.plot_type = QComboBox()
        self.plot_type.addItems(['Absorbance', 'Transmittance'])
        ndx = self.plot_type.findText(self.settings.plot_type, Qt.MatchExactly)
        self.plot_type.setCurrentIndex(ndx)
        self.plot_type.currentIndexChanged.connect(lambda *args: self.show_ir_plot(create=False))
        ir_layout.addRow("plot type:", self.plot_type)
        
        self.reverse_x = QCheckBox()
        self.reverse_x.setCheckState(Qt.Checked if self.settings.reverse_x else Qt.Unchecked)
        self.reverse_x.stateChanged.connect(lambda *args: self.show_ir_plot(create=False))
        ir_layout.addRow("reverse x-axis:", self.reverse_x)
        
        show_plot = QPushButton("show plot")
        show_plot.clicked.connect(self.show_ir_plot)
        ir_layout.addRow(show_plot)
        
        
        self.display_tabs.addTab(vector_tab, "vectors")
        self.display_tabs.addTab(animate_tab, "animate")
        self.display_tabs.addTab(ir_tab, "IR spectrum")

        layout.addWidget(self.display_tabs)

        #only the table can stretch
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 0)
        
        self.tool_window.ui_area.setLayout(layout)

        if len(self.session.filereader_manager.frequency_models) > 0:
            self.create_freq_table(0)

        self.tool_window.manage(None)

    def create_freq_table(self, state):
        """populate the table with frequencies"""
        
        self.table.setRowCount(0)

        if state == -1:
            # early return if no frequency models
            return
            
        fr = self.model_selector.currentData()
        if fr is None:
            return 

        freq_data = fr.other['frequency'].data
        
        for i, mode in enumerate(freq_data):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            freq = FreqTableWidgetItem()
            freq.setData(Qt.DisplayRole, "%.2f%s" % (abs(mode.frequency), "i" if mode.frequency < 0 else ""))
            freq.setData(Qt.UserRole, i)
            self.table.setItem(row, 0, freq)
            
            if mode.symmetry:
                text = mode.symmetry
                if re.search("\d", text):
                    text = re.sub(r"(\d+)", r"<sub>\1</sub>", text)
                if text.startswith("SG"):
                    text = "Σ" + text[2:]
                elif text.startswith("PI"):
                    text = "Π" + text[2:]
                elif text.startswith("DLT"):
                    text = "Δ" + text[3:]
                if any(text.endswith(char) for char in "vhdugVHDUG"):
                    text = text[:-1] + "<sub>" + text[-1].lower() + "</sub>"

                label = QLabel(text)
                label.setAlignment(Qt.AlignCenter)
                self.table.setCellWidget(row, 1, label)

            intensity = QTableWidgetItem()
            if mode.intensity is not None:
                intensity.setData(Qt.DisplayRole, round(mode.intensity, 2))
            self.table.setItem(row, 2, intensity)
        
        self.table.setSelection(QRect(0, 0, 2, 1), QItemSelectionModel.Select)
    
    def change_mw_option(self, state):
        """toggle bool associated with mass-weighting option"""
        if state == Qt.Checked:
            self.vec_mw_bool = True
        else:
            self.vec_mw_bool = False

    def _get_coord_change(self, geom, vector, scaling):
        """determine displacement given scaling and vector"""
        max_norm = None
        for i, displacement in enumerate(vector):
            n = np.linalg.norm(displacement)
            if self.vec_mw_bool and self.display_tabs.currentIndex() == 0:
                n *= geom.atoms[i].mass()

            if max_norm is None or n > max_norm:
                max_norm = n

        dX = vector * scaling/max_norm

        if self.vec_mw_bool and self.display_tabs.currentIndex() == 0:
            for i, x in enumerate(dX):
                dX[i] *= geom.atoms[i].mass()

        return dX

    def close_vec(self):
        modes = self.table.selectedItems()
        if len([mode for mode in modes if mode.column() == 0]) != 1:
            return 
            
        fr = self.model_selector.currentData()
        model = self.session.filereader_manager.get_model(fr)
        for m in modes:
            if m.column() == 0:
                mode = m.data(Qt.UserRole)
        
        name = "%.2f cm^-1" % fr.other['frequency'].data[mode].frequency
        
        for child in model.child_models():
            if child.name == name:
                run(self.session, "close %s" % child.atomspec)

    def show_vec(self):
        """display normal mode displacement vector"""
        fr = self.model_selector.currentData()
        model = self.session.filereader_manager.get_model(fr)
        modes = self.table.selectedItems()
        if len([mode for mode in modes if mode.column() == 0]) != 1:
            raise RuntimeError("one mode must be selected")
        else:
            for m in modes:
                if m.column() == 0:
                    mode = m.data(Qt.UserRole)

        scale = self.vec_scale.value()

        self.settings.arrow_scale = scale

        color = self.vector_color.get_color()

        color = [c/255. for c in color]

        self.settings.arrow_color = tuple(color)

        #reset coordinates if movie isn't playing
        geom = Geometry(fr)

        vector = fr.other['frequency'].data[mode].vector

        dX = self._get_coord_change(geom, vector, scale)
        
        #make a bild file for the model
        s = ".color %f %f %f\n" % tuple(color[:-1])
        s += ".transparency %f\n" % (1. - color[-1])
        for i in range(0, len(geom.atoms)):
            n = np.linalg.norm(dX[i])

            info = tuple(t for s in [[x for x in geom.atoms[i].coords], \
                                     [x for x in geom.atoms[i].coords + dX[i]], \
                                     [n/(n + 0.75)]] for t in s)
                                    
            if n > 0.1:
                s += ".arrow %10.6f %10.6f %10.6f   %10.6f %10.6f %10.6f   0.02 0.05 %5.3f\n" % info

        stream = BytesIO(bytes(s, 'utf-8'))
        bild_obj, status = read_bild(self.session, stream, "%.2f cm^-1" % fr.other['frequency'].data[mode].frequency)

        self.session.models.add(bild_obj, parent=model)
    
    def show_anim(self):
        """play selected modes as an animation"""
        fr = self.model_selector.currentData()
        model = self.session.filereader_manager.get_model(fr)
        modes = self.table.selectedItems()
        if len([mode for mode in modes if mode.column() == 0]) != 1:
            raise RuntimeError("one mode must be selected")
        else:
            for m in modes:
                if m.column() == 0:
                    mode = m.data(Qt.UserRole)

        scale = self.anim_scale.value()
        frames = self.anim_duration.value()
        anim_fps = self.anim_fps.value()

        self.settings.anim_scale = scale
        self.settings.anim_duration = frames
        self.settings.anim_fps = anim_fps

        geom = Geometry(fr)
        #if the filereader has been processed somewhere else, the atoms might
        #have a chimerax atom associated with them that prevents them from being pickled 
        for atom in geom.atoms:
            if hasattr(atom, "chix_atom"):
                atom.chix_atom = None

        vector = fr.other['frequency'].data[mode].vector

        dX = self._get_coord_change(geom, vector, scale)
        
        Xf = geom.coords + dX
        X = geom.coords
        Xr = geom.coords - dX
        
        S = Pathway(geom, np.array([Xf, X, Xr, X, Xf]))
        
        coordsets = np.zeros((frames, len(geom.atoms), 3))
        for i, t in enumerate(np.linspace(0, 1, num=frames, endpoint=False)):
            coordsets[i] = S.coords_func(t)
            
        model.add_coordsets(coordsets, replace=True)
        for i, coordset in enumerate(coordsets):
            model.active_coordset_id = i + 1

            for atom, coord in zip(model.atoms, coordset):
                atom.coord = coord
        
        for atom, chix_atom in zip(geom.atoms, model.atoms):
            atom.chix_atom = chix_atom
        
        for tool in self.session.tools.list():
            if isinstance(tool, CoordinateSetSlider):
                if tool.structure is model:
                    tool.delete()
    
        pause_frames = (60 // anim_fps)

        slider =  CoordinateSetSlider(self.session, model, movie_framerate=anim_fps, pause_frames=pause_frames)
        slider.play_cb()

    def stop_anim(self):
        fr = self.model_selector.currentData()
        model = self.session.filereader_manager.get_model(fr)
        for tool in self.session.tools.list():
            if isinstance(tool, CoordinateSetSlider):
                if tool.structure is model:
                    tool.delete()
                    
        geom = Geometry(fr)
        for atom, coord in zip(model.atoms, geom.coords):
            atom.coord = coord
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
    
    def show_ir_plot(self, *args, create=True, **kwargs):
        if self.ir_plot is None and create:
            self.ir_plot = self.tool_window.create_child_window("IR Plot", window_class=IRPlot)
        else:
            self.ir_plot.refresh_plot()
    
    def highlight_ir_plot(self, *args):
        if self.ir_plot is not None:
            self.ir_plot.highlight(self.table.selectedItems())

    def delete(self):
        self.model_selector.deleteLater()

        return super().delete()
    
    def close(self):
        self.model_selector.deleteLater()

        return super().close()
    

class IRPlot(ChildToolWindow):
    def __init__(self, tool_instance, title, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)
        
        self.highlighted_mode = None
        self._last_mouse_xy = None
        self._dragged = False
        self._min_drag = 10	
        self._drag_mode = None
        self.press = None
        self.drag_prev = None
        self.dragging = False
        self.exp_data = None
        
        self._build_ui()
        self.refresh_plot()

    def _build_ui(self):
        
        layout = QGridLayout()
        
        toolbox = QTabWidget()
        layout.addWidget(toolbox)
        
        plot_widget = QWidget()
        plot_layout = QGridLayout(plot_widget)
        
        self.figure = Figure(figsize=(1.5, 1.5), dpi=100)
        self.canvas = Canvas(self.figure)

        self.canvas.mpl_connect('button_release_event', self.unclick)
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.mpl_connect('motion_notify_event', self.drag)
        self.canvas.mpl_connect('scroll_event', self.zoom)
        
        self.canvas.setMinimumWidth(400)
        self.canvas.setMinimumHeight(300)

        plot_layout.addWidget(self.canvas, 0, 0, 1, 2)

        toolbar_widget = QWidget()
        self.toolbar = NavigationToolbar(self.canvas, toolbar_widget)
        self.toolbar.setMaximumHeight(32)
        plot_layout.addWidget(self.toolbar, 1, 1, 1, 1)
        
        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon(refresh_button.style().standardIcon(QStyle.SP_BrowserReload)))
        refresh_button.clicked.connect(self.refresh_plot)
        plot_layout.addWidget(refresh_button, 1, 0, 1, 1, Qt.AlignVCenter)
        
        toolbox.addTab(plot_widget, "plot")

        # peak style
        peak_widget = QWidget()
        peak_layout = QFormLayout(peak_widget)

        self.peak_type = QComboBox()
        self.peak_type.addItems(['Gaussian', 'Lorentzian', 'pseudo-Voigt', 'Delta'])
        ndx = self.peak_type.findText(self.tool_instance.settings.peak_type, Qt.MatchExactly)
        self.peak_type.setCurrentIndex(ndx)
        peak_layout.addRow("peak type:", self.peak_type)
        
        self.fwhm = QDoubleSpinBox()
        self.fwhm.setSingleStep(5)
        self.fwhm.setRange(0.01, 200.0)
        self.fwhm.setValue(self.tool_instance.settings.fwhm)
        self.fwhm.setToolTip("width of peaks at half of their maximum value")
        peak_layout.addRow("FWHM:", self.fwhm)
        
        self.fwhm.setEnabled(self.peak_type.currentText() != "Delta")
        self.peak_type.currentTextChanged.connect(lambda text, widget=self.fwhm: widget.setEnabled(text != "Delta"))
        
        self.voigt_mix = QDoubleSpinBox()
        self.voigt_mix.setSingleStep(0.005)
        self.voigt_mix.setDecimals(3)
        self.voigt_mix.setRange(0, 1)
        self.voigt_mix.setValue(self.tool_instance.settings.voigt_mix)
        self.voigt_mix.setToolTip("fraction of pseudo-Voigt function that is Gaussian")
        peak_layout.addRow("Voigt mixing:", self.voigt_mix)
        
        self.voigt_mix.setEnabled(self.peak_type.currentText() == "pseudo-Voigt")
        self.peak_type.currentTextChanged.connect(lambda text, widget=self.voigt_mix: widget.setEnabled(text == "pseudo-Voigt"))
        
        toolbox.addTab(peak_widget, "peak settings")
        
        # plot experimental data alongside computed
        experimental_widget = QWidget()
        experimental_layout = QFormLayout(experimental_widget)
        
        self.skip_lines = QSpinBox()
        self.skip_lines.setRange(0, 15)
        experimental_layout.addRow("skip first lines:", self.skip_lines)
        
        browse_button = QPushButton("browse...")
        browse_button.clicked.connect(self.load_data)
        experimental_layout.addRow("load CSV data:", browse_button)
        
        self.line_color = ColorButton(has_alpha_channel=False, max_size=(16, 16))
        self.line_color.set_color(self.tool_instance.settings.exp_color)
        experimental_layout.addRow("line color:", self.line_color)
        
        clear_button = QPushButton("clear experimental data")
        clear_button.clicked.connect(self.clear_data)
        experimental_layout.addRow(clear_button)
        
        toolbox.addTab(experimental_widget, "plot experimental data")
        
        
        # frequency scaling
        scaling_group = QWidget()
        scaling_layout = QFormLayout(scaling_group)
        
        desc = QLabel("")
        desc.setText("<a href=\"test\" style=\"text-decoration: none;\">Δ<sub>anh</sub> ≈ c<sub>1</sub>𝜈<sub>e</sub> + c<sub>2</sub>𝜈<sub>e</sub><sup>2</sup></a>")
        desc.setTextFormat(Qt.RichText)
        desc.setTextInteractionFlags(Qt.TextBrowserInteraction)
        desc.linkActivated.connect(self.open_link)
        desc.setToolTip("Crittenden and Sibaev's quadratic scaling for harmonic frequencies\nDOI 10.1021/acs.jpca.5b11386")
        scaling_layout.addRow(desc)

        self.linear = QDoubleSpinBox()
        self.linear.setDecimals(6)
        self.linear.setRange(-.2, .2)
        self.linear.setSingleStep(0.001)
        self.linear.setValue(0.)
        scaling_layout.addRow("c<sub>1</sub> =", self.linear)

        self.quadratic = QDoubleSpinBox()
        self.quadratic.setDecimals(9)
        self.quadratic.setRange(-.2, .2)
        self.quadratic.setSingleStep(0.000001)
        self.quadratic.setValue(0.)
        scaling_layout.addRow("c<sub>2</sub> =", self.quadratic)
        
        set_zero = QPushButton("set scales to 0")
        set_zero.clicked.connect(lambda *args: self.linear.setValue(0.))
        set_zero.clicked.connect(lambda *args: self.quadratic.setValue(0.))
        scaling_layout.addRow(set_zero)
        
        
        lookup_scale = QGroupBox("scale factor lookup")
        scaling_layout.addRow(lookup_scale)
        lookup_layout = QFormLayout(lookup_scale)
        
        self.library = QComboBox()
        self.library.addItems(SCALE_LIBS.keys())
        lookup_layout.addRow("database:", self.library)
        
        self.method = QComboBox()
        self.method.addItems(SCALE_LIBS[self.library.currentText()][1].keys())
        lookup_layout.addRow("method:", self.method)
        
        self.basis = QComboBox()
        self.basis.addItems(SCALE_LIBS[self.library.currentText()][1][self.method.currentText()].keys())
        lookup_layout.addRow("basis set:", self.basis)
        
        desc = QLabel("")
        desc.setText("view database online <a href=\"test\" style=\"text-decoration: none;\">here</a>")
        desc.setTextFormat(Qt.RichText)
        desc.setTextInteractionFlags(Qt.TextBrowserInteraction)
        desc.linkActivated.connect(self.open_scale_library_link)
        desc.setToolTip("view library online")
        lookup_layout.addRow(desc)

        self.library.currentTextChanged.connect(self.change_scale_lib)
        self.method.currentTextChanged.connect(self.change_method)
        self.basis.currentTextChanged.connect(self.change_basis)

        fit_scale = QGroupBox("linear least squares fitting")
        scaling_layout.addRow(fit_scale)
        fit_layout = QFormLayout(fit_scale)
        
        self.fit_c1 = QCheckBox()
        fit_layout.addRow("fit c<sub>1</sub>:", self.fit_c1)
        
        self.fit_c2 = QCheckBox()
        fit_layout.addRow("fit c<sub>2</sub>:", self.fit_c2)
        
        match_peaks = QPushButton("match peaks...")
        match_peaks.clicked.connect(self.show_match_peaks)
        fit_layout.addRow(match_peaks)

        toolbox.addTab(scaling_group, "frequency scaling")
        
        
        # break x axis
        interrupt_widget = QWidget()
        interrupt_layout = QFormLayout(interrupt_widget)

        self.section_table = QTableWidget()
        self.section_table.setColumnCount(3)
        self.section_table.setHorizontalHeaderLabels(["section center", "width", "remove"])
        self.section_table.cellClicked.connect(self.section_table_clicked)
        interrupt_layout.addRow(self.section_table)
        self.add_section()

        toolbox.addTab(interrupt_widget, "x-axis breaks")
        

        toolbox.currentChanged.connect(lambda ndx: self.refresh_plot() if not ndx else None)
        # toolbox.setMinimumWidth(int(1.1 * plot_widget.size().width()))
        # toolbox.setMinimumHeight(int(1.2 * plot_widget.size().height()))

        #menu bar for saving stuff
        menu = QMenuBar()
        file = menu.addMenu("&Export")
        file.addAction("&Save CSV...")
        
        file.triggered.connect(self.save)
        
        menu.setNativeMenuBar(False)
        self._menu = menu
        layout.setMenuBar(menu)        
        self.ui_area.setLayout(layout)
        self.manage(None)
    
    def section_table_clicked(self, row, column):
        if row == self.section_table.rowCount() - 1:
            self.add_section()
        elif column == 2:
            self.section_table.removeRow(row)
    
    def add_section(self):
        rows = self.section_table.rowCount()
        if rows != 0:
            rows -= 1
        else:
            self.section_table.insertRow(rows)

        section_center = QDoubleSpinBox()
        section_center.setRange(0, 5000)
        section_center.setValue(950)
        section_center.setSuffix(" cm\u207b\u00b9")
        section_center.setSingleStep(25)
        self.section_table.setCellWidget(rows, 0, section_center)
        
        section_width = QDoubleSpinBox()
        section_width.setRange(1, 5000)
        section_width.setValue(1900)
        section_width.setSuffix(" cm\u207b\u00b9")
        section_width.setSingleStep(25)
        self.section_table.setCellWidget(rows, 1, section_width)
        
        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        section_remove = QLabel()
        dim = int(1.5 * section_remove.fontMetrics().boundingRect("Q").height())
        section_remove.setPixmap(QIcon(section_remove.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(dim, dim))
        widget_layout.addWidget(section_remove, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        self.section_table.setCellWidget(rows, 2, widget_that_lets_me_horizontally_align_an_icon)
        
        rows += 1
        self.section_table.insertRow(rows)

        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        section_add = QLabel("add section")
        widget_layout.addWidget(section_add, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        self.section_table.setCellWidget(rows, 1, widget_that_lets_me_horizontally_align_an_icon)
    
    def save(self):
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
        if filename:
            s = "frequency (cm^-1),IR intensity\n"
            data = self.get_data()
            x_values, y_values = data
            for x, y in zip(x_values, y_values):
                s += "%f,%f\n" % (x, y)

            with open(filename, 'w') as f:
                f.write(s.strip())
                
            self.tool_instance.session.logger.info("saved to %s" % filename)

    def open_link(self, *args):
        """open Crittenden's paper on scaling harmonic frequencies"""
        run(self.session, "open https://doi.org/10.1021/acs.jpca.5b11386")

    def open_scale_library_link(self, *args):
        run(self.session, "open %s" % SCALE_LIBS[self.library.currentText()][0])

    def change_scale_lib(self, lib):
        cur_method = self.method.currentText()
        cur_basis = self.basis.currentText()
        self.prev_basis = self.basis.currentText()
        self.method.blockSignals(True)
        self.method.clear()
        self.method.blockSignals(False)
        self.method.addItems(SCALE_LIBS[lib][1].keys())
        ndx = self.method.findText(cur_method, Qt.MatchExactly)
        if ndx >= 0:
            self.method.setCurrentIndex(ndx)
        
        ndx = self.basis.findText(cur_basis, Qt.MatchExactly)
        if ndx >= 0:
            self.basis.setCurrentIndex(ndx)
    
    def change_method(self, method):
        cur_basis = self.basis.currentText()
        self.basis.blockSignals(True)
        self.basis.clear()
        self.basis.blockSignals(False)
        if isinstance(SCALE_LIBS[self.library.currentText()][1][method], dict):
            self.basis.addItems(SCALE_LIBS[self.library.currentText()][1][method].keys())
            ndx = self.basis.findText(cur_basis, Qt.MatchExactly)
            if ndx >= 0:
                self.basis.setCurrentIndex(ndx)
        else:
            scale = SCALE_LIBS[self.library.currentText()][1][method]
            self.linear.setValue(1 - scale)
            self.quadratic.setValue(0.)

    def change_basis(self, basis):
        scale = SCALE_LIBS[self.library.currentText()][1][self.method.currentText()][basis]
        self.linear.setValue(1 - scale)
        self.quadratic.setValue(0.)

    def zoom(self, event):
        if event.xdata is None:
            return
        for a in self.figure.get_axes():
            x0, x1 = a.get_xlim()
            x_range = x1 - x0
            xdiff = -0.05 * event.step * x_range
            xshift = 0.2 * (event.xdata - (x0 + x1)/2)
            nx0 = x0 - xdiff + xshift
            nx1 = x1 + xdiff + xshift
    
            a.set_xlim(nx0, nx1)
        self.canvas.draw()

    def drag(self, event):
        if self.toolbar.mode != "":
            return

        if event.button is not None and self.press is not None:
            x, y, xpress, ypress = self.press
            dx = event.x - x
            dy = event.y - y
            drag_dist = np.linalg.norm([dx, dy])
            if self.dragging or drag_dist >= self._min_drag or event.button == 2:
                self.dragging = True
                if self.drag_prev is not None:
                    x, y, xpress, ypress = self.drag_prev
                    dx = event.x - x
                    dy = event.y - y
                
                self.drag_prev = event.x, event.y, event.xdata, event.ydata
                self.move(dx, dy)

    def move(self, dx, dy):
        for ax in self.figure.get_axes():
            w = self.figure.get_figwidth() * self.figure.get_dpi()
            x0, x1 = self.figure.gca().get_xlim()
            xs = dx/w * (x1 - x0)
            x0, x1 = ax.get_xlim()
            nx0, nx1 = x0 - xs, x1 - xs
            #y0, y1 = ax.get_ylim()
            #ys = dy/h * (y1-y0)
            #ny0, ny1 = y0-ys, y1-ys
            ax.set_xlim(nx0, nx1)
            #ax.set_ylim(ny0, ny1)
        self.canvas.draw()

    def onclick(self, event):
        if self.toolbar.mode != "":
            return

        self.press = event.x, event.y, event.xdata, event.ydata

    def unclick(self, event):
        if self.toolbar.mode != "":
            return

        self.press = None
        self.drag_prev = None
        self.dragging = False

    def get_data(self):
        fr = self.tool_instance.model_selector.currentData()
        if fr is None:
            return None
        fwhm = self.fwhm.value()
        self.tool_instance.settings.fwhm = fwhm
        self.tool_instance.settings.peak_type = self.peak_type.currentText()
        self.tool_instance.settings.plot_type = self.tool_instance.plot_type.currentText()
        self.tool_instance.settings.reverse_x = self.tool_instance.reverse_x.checkState() == Qt.Checked
        eta = self.voigt_mix.value()
        self.tool_instance.settings.voigt_mix = eta
        
        frequencies = np.array([freq.frequency for freq in fr.other['frequency'].data if freq.frequency > 0])
        c1 = self.linear.value()
        c2 = self.quadratic.value()
        frequencies -= c1 * frequencies + c2 * frequencies ** 2
        
        intensities = [freq.intensity for freq in fr.other['frequency'].data if freq.frequency > 0]
        e_factor = -4 * np.log(2) / fwhm ** 2
        
        if self.peak_type.currentText() != "Delta":
            functions = []
            x_values = np.linspace(0, max(frequencies) - 10 * fwhm, num=100).tolist()
            for freq, intensity in zip(frequencies, intensities):
                if intensity is not None:
                    #make sure to get x values near the peak
                    #this makes the peaks look hi res, but we can cheap out
                    #on areas where there's no peak
                    x_values.extend(
                        np.linspace(
                            max(freq - (3.5 * fwhm), 0), 
                            freq + (3.5 * fwhm), 
                            num=65,
                        ).tolist()
                    )
                    x_values.append(freq)
                    if self.peak_type.currentText() == "Gaussian":
                        functions.append(lambda x, x0=freq, inten=intensity: \
                                        inten * np.exp(e_factor * (x - x0) ** 2))
    
                    elif self.peak_type.currentText() == "Lorentzian":
                        functions.append(lambda x, x0=freq, inten=intensity, : \
                                        inten * 0.5 * (0.5 * fwhm / ((x - x0) ** 2 + (0.5 * fwhm)**2)))
                    
                    elif self.peak_type.currentText() == "pseudo-Voigt":
                        functions.append(
                            lambda x, x0=freq, inten=intensity:
                                inten * (
                                    (1 - eta) * 0.5 * (0.5 * fwhm / ((x - x0)**2 + (0.5 * fwhm)**2)) + 
                                    eta * np.exp(e_factor * (x - x0)**2)
                                )
                        )
    
        
            x_values = np.array(list(set(x_values)))
            x_values.sort()
            y_values = np.sum([f(x_values) for f in functions], axis=0)
        
        else:
            x_values = []
            y_values = []

            for freq, intensity in zip(frequencies, intensities):
                if intensity is not None:
                    y_values.append(intensity)
                    x_values.append(freq)

            y_values = np.array(y_values)

        if len(y_values) == 0:
            self.tool_instance.session.logger.error("nothing to plot")
            return None

        y_values /= np.amax(y_values)


        if self.tool_instance.plot_type.currentText() == "Transmittance":
            y_values = np.array([10 ** (-y) for y in y_values])

        return x_values, y_values

    def refresh_plot(self):
        data = self.get_data()
        if data is None:
            return
        x_values, y_values = data

        self.figure.clear()

        if self.section_table.rowCount() <= 2:
            axes = [self.figure.subplots(nrows=1, ncols=1)]
            widths = [max(x_values)]
            centers = [max(x_values) / 2]
        else:
            n_sections = self.section_table.rowCount() - 1
            self.figure.subplots_adjust(wspace=0.05)
            centers = []
            widths = []
            for i in range(0, self.section_table.rowCount() - 1):
                centers.append(self.section_table.cellWidget(i, 0).value())
                widths.append(self.section_table.cellWidget(i, 1).value())
                
            widths = [x for _, x in sorted(
                zip(centers, widths),
                key=lambda p: p[0],
                reverse=self.tool_instance.reverse_x.checkState() == Qt.Checked,
            )]
            centers = sorted(centers, reverse=self.tool_instance.reverse_x.checkState() == Qt.Checked)
            
            axes = self.figure.subplots(
                nrows=1,
                ncols=n_sections,
                sharey=True,
                gridspec_kw={'width_ratios': widths},
            )

        for i, ax in enumerate(axes):
            if i == 0:
                if self.tool_instance.plot_type.currentText() == "Transmittance":
                    ax.set_ylabel('transmittance (arb.)')
                else:
                    ax.set_ylabel('absorbance (arb.)')
            
                if len(axes) > 1:
                    ax.spines["right"].set_visible(False)
                    ax.tick_params(labelright=False, right=False)
                    ax.plot(
                        [1, 1],
                        [0, 1],
                        marker=((-1, -1), (1, 1)),
                        markersize=5,
                        linestyle='none',
                        color='k',
                        mec='k',
                        mew=1,
                        clip_on=False,
                        transform=ax.transAxes,
                    )

            elif i == len(axes) - 1 and len(axes) > 1:
                ax.spines["left"].set_visible(False)
                ax.tick_params(labelleft=False, left=False)
                ax.plot(
                    [0, 0],
                    [0, 1],
                    marker=((-1, -1), (1, 1)),
                    markersize=5,
                    linestyle='none',
                    color='k',
                    mec='k',
                    mew=1,
                    clip_on=False,
                    transform=ax.transAxes,
                )

            elif len(axes) > 1:
                ax.spines["right"].set_visible(False)
                ax.spines["left"].set_visible(False)
                ax.tick_params(labelleft=False, labelright=False, left=False, right=False)
                ax.plot(
                    [0, 0],
                    [0, 1],
                    marker=((-1, -1), (1, 1)),
                    markersize=5,
                    linestyle='none',
                    label="Silence Between Two Subplots",
                    color='k',
                    mec='k',
                    mew=1,
                    clip_on=False,
                    transform=ax.transAxes,
                )
                ax.plot(
                    [1, 1],
                    [0, 1],
                    marker=((-1, -1), (1, 1)),
                    markersize=5,
                    label="Silence Between Two Subplots",
                    linestyle='none',
                    color='k',
                    mec='k',
                    mew=1,
                    clip_on=False,
                    transform=ax.transAxes,
                )


            if self.peak_type.currentText() != "Delta":
                ax.plot(
                    x_values,
                    y_values,
                    color='k',
                    linewidth=0.5,
                    label="computed",
                )
            else:
                if self.tool_instance.plot_type.currentText() == "Transmittance":
                    ax.vlines(
                        x_values,
                        y_values,
                        [1 for y in y_values],
                        linewidth=0.5,
                        colors=['k' for x in x_values],
                        label="computed"
                    )
                    ax.hlines(
                        1,
                        0,
                        max(4000, *x_values),
                        linewidth=0.5,
                        colors=['k' for y in y_values],
                        label="computed",
                    )
                
                else:
                    ax.vlines(
                        x_values,
                        [0 for y in y_values],
                        y_values,
                        linewidth=0.5,
                        colors=['k' for x in x_values],
                        label="computed"
                    )
                    ax.hlines(
                        0,
                        0,
                        max(4000, *x_values),
                        linewidth=0.5,
                        colors=['k' for y in y_values],
                        label="computed"
                    )

            if self.exp_data:
                for x, y, color in self.exp_data:
                    ax.plot(x, y, color=color, zorder=-1, linewidth=0.5, label="observed")

            center = centers[i]
            width = widths[i]
            high = center + width / 2
            low = center - width / 2
            if self.tool_instance.reverse_x.checkState() == Qt.Checked:
                ax.set_xlim(high, low)
            else:
                ax.set_xlim(low, high)
        
        self.figure.text(0.5, 0.0, r"wavenumber (cm$^{-1}$)" , ha="center", va="bottom")

        self.canvas.draw()

    def highlight(self, items):
        highlights = []
        for ax in self.figure.get_axes():
            if self.highlighted_mode is not None:
                for mode in self.highlighted_mode:
                    if mode in ax.collections:
                        ax.collections.remove(mode)
            
            if len(items) == 0:
                self.highlighted_mode = None
                self.canvas.draw()
                continue
            
            fr = self.tool_instance.model_selector.currentData()
            if fr is None:
                return 
    
            for item in items:
                if item.column() == 0:
                    row = item.data(Qt.UserRole)
            
            frequency = [freq.frequency for freq in fr.other['frequency'].data][row]
            if frequency < 0:
                self.canvas.draw()
                continue
            
            c1 = self.linear.value()
            c2 = self.quadratic.value()
            frequency -= c1 * frequency + c2 * frequency ** 2
            
            if ax.get_ylim()[1] > 50:
                y_vals = (10 ** (2 - 0.9), 100)
            else:
                y_vals = (0, 1)
                
            highlights.append(ax.vlines(frequency, *y_vals, color='r', zorder=-1, label="highlight"))
        
        self.highlighted_mode = highlights
        self.canvas.draw()

    def load_data(self, *args):
        filename, _ = QFileDialog.getOpenFileName(filter="comma-separated values file (*.csv)")

        if not filename:
            return

        data = np.loadtxt(filename, delimiter=",", skiprows=self.skip_lines.value())

        color = self.line_color.get_color()
        self.tool_instance.settings.exp_color = tuple([c / 255. for c in color[:-1]])
        
        # figure out hex code for specified color 
        # color is RGBA tuple with values from 0 to 255
        # python's hex turns that to base 16 (0 to ff)
        # if value is < 16, there will only be one digit, so pad with 0
        hex_code = "#"
        for x in color[:-1]:
            channel = str(hex(x))[2:]
            if len(channel) == 1:
                channel = "0" + channel
            hex_code += channel

        if self.exp_data is None:
            self.exp_data = []

        for i in range(1, data.shape[1]):
            print(i)
            self.exp_data.append((data[:,0], data[:,i], hex_code))

    def clear_data(self, *args):
        self.exp_data = None

    def show_match_peaks(self, *args):
        if self.tool_instance.match_peaks is None:
            self.tool_instance.match_peaks = self.tool_instance.tool_window.create_child_window("match peaks", window_class=MatchPeaks)

    def cleanup(self):
        self.tool_instance.ir_plot = None
        
        super().cleanup()


class MatchPeaks(ChildToolWindow):
    def __init__(self, tool_instance, title, *args, **kwargs):
        super().__init__(tool_instance, title, *args, **kwargs)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QFormLayout()
        
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["comp. freq. (cm\u207b\u00b9)", "obs. freq. (cm\u207b\u00b9)"])
        for i in range(0, 2):
            table.resizeColumnToContents(i)
        
        table.horizontalHeader().setStretchLastSection(False)            
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)        
        
        fr = self.tool_instance.model_selector.currentData()
        if fr:
            freq_data = fr.other['frequency'].data
            
            for i, mode in enumerate(freq_data):
                if mode.frequency < 0:
                    continue
                row = table.rowCount()
                table.insertRow(row)
                
                freq = FreqTableWidgetItem()
                freq.setData(Qt.DisplayRole, "%.2f" % mode.frequency)
                freq.setData(Qt.UserRole, mode.frequency)
                table.setItem(row, 0, freq)
                
                exp_freq = QDoubleSpinBox()
                exp_freq.setRange(0, 4500)
                exp_freq.setDecimals(2)
                exp_freq.setToolTip("observed frequency\nleave at 0 to not use this in fitting")
                table.setCellWidget(row, 1, exp_freq)
        
        layout.addRow(table)
        self.table = table
        
        do_fit_button = QPushButton("do least squares")
        do_fit_button.clicked.connect(self.do_fit)
        layout.addRow(do_fit_button)
        
        self.ui_area.setLayout(layout)
        self.manage(None)
    
    def do_fit(self, *args):
        if not self.tool_instance.ir_plot:
            raise RuntimeError("plot window must be open during fitting")
        comp_freqs = []
        exp_freqs = []
        
        for i in range(0, self.table.rowCount()):
            spinbox = self.table.cellWidget(i, 1)
            if spinbox.value() != 0:
                exp_freqs.append(spinbox.value())
                comp_freqs.append(self.table.item(i, 0).data(Qt.UserRole))
        
        comp_freqs = np.array(comp_freqs)
        exp_freqs = np.array(exp_freqs)
        
        fit_c1 = self.tool_instance.ir_plot.fit_c1.checkState() == Qt.Checked
        fit_c2 = self.tool_instance.ir_plot.fit_c2.checkState() == Qt.Checked
        
        params = int(fit_c1) + int(fit_c2)
        
        if len(comp_freqs) < params:
            raise RuntimeError("must specify enough data for %i parameter(s)" % params)
        
        if fit_c1 and fit_c2:
            mat = np.array([comp_freqs, comp_freqs**2]).T

            c_vals, res, _, _ = np.linalg.lstsq(mat, comp_freqs - exp_freqs)
            self.tool_instance.ir_plot.linear.setValue(c_vals[0])
            self.tool_instance.ir_plot.quadratic.setValue(c_vals[1])
            if abs(c_vals[0]) > 0.2:
                self.tool_instance.session.logger.warning("c1 value %f is outside the bounds of the spinbox widget, check your input" % c_vals[0])
            if abs(c_vals[1]) > 0.2:
                self.tool_instance.session.logger.warning("c2 value %f is outside the bounds of the spinbox widget, check your input" % c_vals[1])
        elif fit_c1:
            l = np.dot(exp_freqs, comp_freqs) / np.dot(comp_freqs, comp_freqs)
            self.tool_instance.ir_plot.linear.setValue(1 - l)
            self.tool_instance.ir_plot.quadratic.setValue(0.)
            if abs(1 - l) > 0.2:
                self.tool_instance.session.logger.warning("c1 value %f is outside the bounds of the spinbox widget, check your input" % (1 - l))
        elif fit_c2:
            l = np.dot(comp_freqs - exp_freqs, comp_freqs ** 2) / np.dot(comp_freqs ** 2, comp_freqs ** 2)
            self.tool_instance.ir_plot.linear.setValue(0.)
            self.tool_instance.ir_plot.quadratic.setValue(l)
            if abs(l) > 0.2:
                self.tool_instance.session.logger.warning("c2 value %f is outside the bounds of the spinbox widget, check your input" % l)
        else:
            self.tool_instance.session.logger.error("no fit parameters selected on plot tool window")

    def cleanup(self):
        self.tool_instance.match_peaks = None
        
        super().cleanup()
