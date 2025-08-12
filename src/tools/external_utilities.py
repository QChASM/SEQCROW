from AaronTools.utils.utils import angle_between_vectors, perp_vector, rotation_matrix
from AaronTools.substituent import Substituent

from chimerax.atomic import selected_atoms, AtomicStructure
from chimerax.ui.gui import MainToolWindow
from chimerax.core.tools import ToolInstance
from chimerax.core.commands import run
from chimerax.core.selection import SELECTION_CHANGED
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import StringArg

from Qt.QtCore import Qt
from Qt.QtWidgets import (
    QComboBox,
    QFormLayout,
)

from json import dumps, loads


class _ExternalUtilitiesSettings(Settings):
    AUTO_SAVE = {
        "data": Value(dumps(dict()), StringArg),
    }


class ExternalUtilitiesInterface(ToolInstance):
    def __init__(self, session, name):
        super().__init__(session, name)
        self.settings = _ExternalUtilitiesSettings(session, name)

        self.tool_window = MainToolWindow(self)

        self._build_ui()

    def _build_ui(self):
        self.layout = QFormLayout()
        
        self.utilities = QComboBox()
        self.utilities.addItems(self.session.external_quantum_utilities.utilities.keys())
        self.layout.addRow("utility:", self.utilities)
        
        
        self.utilities.currentTextChanged.connect(self.change_utility)
        self.current_utility = None
        self.previous_utility_name = None

        self.change_utility(self.utilities.currentText())        

        self.tool_window.ui_area.setLayout(self.layout)

        self.tool_window.manage(None)
    
    def change_utility(self, name):
        if self.current_utility is not None:
            data = loads(self.settings.data)
            self.update_settings(self.previous_utility_name)
            self.layout.removeRow(self.current_utility)
        
        self.current_utility = self.session.external_quantum_utilities.get_utility_widget(name)
        data = loads(self.settings.data)
        if name in data:
            self.current_utility.set_values(**data[name])
        try:
            self.current_utility.update.connect(self.update_settings)
        except Exception as e:
            print(e)
        self.layout.addRow(self.current_utility)
        self.previous_utility_name = name
    
    def update_settings(self, name=None):
        if name is None:
            name = self.utilities.currentText()
        if self.current_utility is None:
            return
        data = loads(self.settings.data)
        try:
            data[name] = self.current_utility.get_values()
            self.settings.data = dumps(data)
        except Exception as e:
            print(e)
    
    def delete(self):
        if self.current_utility is not None:
            self.update_settings()
            self.current_utility.deleteLater()
        
        super().delete()

