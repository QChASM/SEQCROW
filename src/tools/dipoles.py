from os import cpu_count

from chimerax.atomic import Atoms
from chimerax.core.commands import run
from chimerax.core.commands.cli import TupleOf, FloatArg
from chimerax.core.configfile import Value
from chimerax.core.tools import ToolInstance
from chimerax.core.settings import Settings
from chimerax.ui.gui import MainToolWindow
from chimerax.ui.widgets import ColorButton

import numpy as np

from Qt.QtCore import Qt
from Qt.QtWidgets import (
    QPushButton,
    QFormLayout,
    QComboBox,
    QSizePolicy,
)


from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.widgets import FilereaderComboBox, ScientificSpinBox
from SEQCROW.utils import iter2str

class _DipoleSettings(Settings):
    AUTO_SAVE = {
        'color': Value((0.0, 1.0, 1.0, 1.0), TupleOf(FloatArg, 4), iter2str),
    }



class Dipoles(ToolInstance):
    def __init__(self, session, name):
        super().__init__(session, name)

        self.tool_window = MainToolWindow(self)
        self.settings = _DipoleSettings(session, name)
        self._build_ui()
    
    def _build_ui(self):
        layout = QFormLayout()
        
        self.model_selector = FilereaderComboBox(
            self.session,
            otherItems=[
                "Hirshfeld Charges",
                "Löwdin Charges",
                "Mulliken Charges",
                "ESP Charges",
                "CM5 Charges",
                "NPA Charges",
                "uv_vis",
            ],
        )
        layout.addRow(self.model_selector)
        
        self.dipole_type = QComboBox()
        layout.addRow("dipole type:", self.dipole_type)
        self.model_selector.currentIndexChanged.connect(self.fill_dipole_types)
        
        self.origin = QComboBox()
        self.origin.addItems([
            "center of nuclear charge",
            "center of mass",
            "centroid",
            "zero",
        ])
        layout.addRow("origin:", self.origin)
        
        self.color = ColorButton(has_alpha_channel=False, max_size=(16, 16))
        self.color.set_color(self.settings.color)
        self.color.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addRow("color:", self.color)
        
        self.scale = ScientificSpinBox(
            minimum=1e-3,
            maximum=1e3,
            decimals=2,
            maxAbsoluteCharacteristic=3,
            suffix=" X"
        )
        layout.addRow("scale:", self.scale)
        
        self.fill_dipole_types(0)
        
        self.tool_window.ui_area.setLayout(layout)
        
        self.tool_window.manage(None)
    
    def fill_dipole_types(self, ndx):
        current_text = self.dipole_type.currentText()
        
        self.dipole_type.clear()
        
        info = self.model_selector.currentData()
        if info is None:
            return
        fr, mdl = info
        
        items = []
        def name_map(x, fr):
            if "Charges" in x:
                return [x.replace("Charges", "Charge Dipole")]
            if x == "uv_vis":
                uv_vis_dipoles = []
                exc = fr[x].data[0]
                if exc.dipole_len_vec is not None:
                    uv_vis_dipoles.append("Transition Dipole Moment")
                if exc.dipole_vel_vec is not None:
                    uv_vis_dipoles.append("Transition Velocity Moment")
                if exc.magnetic_mom is not None:
                    uv_vis_dipoles.append("Transition Magnetic Dipole")
                return uv_vis_dipoles
        
        for x in [
            "Hirshfeld Charges",
            "Löwdin Charges",
            "Mulliken Charges",
            "ESP Charges",
            "CM5 Charges",
            "NPA Charges",
            "uv_vis",
        ]:
            if x in fr:
                items.extend(name_map(x, fr))
        
        self.dipole_type.addItems(items)
        n = self.dipole_type.findText(current_text, Qt.MatchExactly)
        if n >= 0:
            self.dipole_type.setCurrentIndex(n)
        else:
            self.dipole_type.setCurrentIndex(0)