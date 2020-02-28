from chimerax.atomic import selected_atoms, selected_residues
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow
from chimerax.core.models import MODEL_ID_CHANGED, MODEL_NAME_CHANGED
            
from io import BytesIO

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QGridLayout, QPushButton, QTreeWidget, QWidget, QVBoxLayout, QTreeWidgetItem, QCheckBox

from ChimAARON.residue_collection import ResidueCollection
from ChimAARON.managers.filereader_manager import FILEREADER_CHANGE 

class FileReaderPanel(ToolInstance):
    #XML_TAG ChimeraX :: Tool :: FileReader Panel :: ChimAARON :: Access information from a model's FileReader object
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    
    NAME_COL = 0
    ID_COL = 1
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        # a lot of this is basically copy pasta from the model panel
        self.display_name = "FileReader Panel"
        
        self.tool_window = MainToolWindow(self)        

        self._build_ui()
        self.fill_tree()

    def _build_ui(self):
        layout = QGridLayout()

        self.tree = QTreeWidget()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.tree)

        self.tree.setHeaderLabels(["Name", "ID"])
        self.tree.setUniformRowHeights(True)
        
        self._fr_change = self.session.filereader_manager.triggers.add_handler(FILEREADER_CHANGE,
            lambda *args: self.fill_tree(*args))
        self._molid_change = self.session.triggers.add_handler(MODEL_ID_CHANGED,
            lambda *args: self.fill_tree(*args))
        self._molname_change = self.session.triggers.add_handler(MODEL_NAME_CHANGED,
            lambda *args: self.fill_tree(*args))

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
        
    def fill_tree(self, *args):        
        item_stack = [self.tree.invisibleRootItem()]
        
        self.tree.clear()
        self._items = []

        for model in self.session.filereader_manager.models:
            id = model.id
            name = model.name
            parent = item_stack[0]
            item = QTreeWidgetItem(parent)
            item._model = model
            item_stack.append(item)
            self._items.append(item)
            
            item.setText(self.NAME_COL, name)
            item.setText(self.ID_COL, ".".join([str(x) for x in id]))
    
            self.tree.expandItem(item)
    
    def delete(self):
        """overload delete"""
        self.session.filereader_manager.triggers.remove_handler(self._fr_change)
        self.session.triggers.remove_handler(self._molid_change)
        self.session.triggers.remove_handler(self._molname_change)
        super().delete()