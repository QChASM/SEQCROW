import numpy as np

from AaronTools.substituent import Substituent

from chimerax.atomic import selected_atoms
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow

from io import BytesIO

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QTabWidget, QComboBox, QTableWidget, QTableView, QWidget, QVBoxLayout, QTableWidgetItem, QFormLayout, QCheckBox

from ..residue_collection import ResidueCollection
from ..libraries import SubstituentTable

class EditStructure(ToolInstance):
    #XML_TAG ChimeraX :: Tool :: Structure Modification :: AaronTools :: Modify substituents, swap ligands, abd close rings, all for the one-time fee of an arm and a leg!
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    display_name = "The Alchemist"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)        

        self.close_previous_bool = True

        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()
        
        self.alchemy_tabs = QTabWidget()
        
        #substitute
        self.substitute_tab = QWidget()
        self.substitute_layout = QGridLayout(self.substitute_tab) 
                
        sublabel = QLabel("substituent name:")
        self.substitute_layout.addWidget(sublabel, 0, 0)
        
        self.subname = QLineEdit()
        self.subname.setToolTip("name of substituent in AaronTools library")
        self.substitute_layout.addWidget(self.subname, 0, 1)
        
        open_sub_lib = QPushButton("from library...")
        open_sub_lib.clicked.connect(self.open_sub_selector)
        self.substitute_layout.addWidget(open_sub_lib, 0, 2)        
        
        close_previous = QCheckBox("modify selected structure")
        close_previous.setToolTip("checked: selected structure will be modified\nunchecked: new model will be created for the modified structure")
        close_previous.toggle()
        close_previous.stateChanged.connect(self.close_previous_change)
        self.substitute_layout.addWidget(close_previous, 1, 0, 1, 3)
        
        substitute_button = QPushButton("substitute current selection")
        substitute_button.clicked.connect(self.do_substitute)
        self.substitute_layout.addWidget(substitute_button, 2, 0, 1, 3)
        
        #map ligand
        self.maplig_tab = QWidget()
        self.maplig_layout = QGridLayout(self.maplig_tab)
        
        #close ring
        self.closering_tab = QWidget()
        self.closering_layout = QGridLayout(self.closering_tab)
        
        self.alchemy_tabs.addTab(self.substitute_tab, "substitute")
        self.alchemy_tabs.addTab(self.maplig_tab, "swap ligand")
        self.alchemy_tabs.addTab(self.closering_tab, "close ring")

        layout.addWidget(self.alchemy_tabs)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage('side')
    
    def close_previous_change(self, state):
        if state == Qt.Checked:
            self.close_previous_bool = True
        else:
            self.close_previous_bool = False
    
    def do_substitute(self):
        subnames = self.subname.text()
        selection = selected_atoms(self.session)
        
        if len(selection) < 1:
            raise RuntimeWarning("nothing selected")
        
        models = {}
        for atom in selection:
            if atom.structure not in models:
                models[atom.structure] = [str(atom.atomspec)]
            else:
                models[atom.structure].append(str(atom.atomspec))
                
        first_pass = True
        new_structures = []
        for subname in subnames.split(','):
            subname = subname.strip()
            sub = Substituent(subname)
            for model in models:
                if self.close_previous_bool and first_pass:
                    rescol = ResidueCollection(model)
                    for target in models[model]:
                        rescol.substitute(sub.copy(), target)
                    
                    rescol.update_chix(model)
                    
                elif self.close_previous_bool and not first_pass:
                    raise RuntimeError("only the first model can be replaced")
                else:
                    model_copy = model.copy()
                    rescol = ResidueCollection(model_copy)
                    for target in models[model]:
                        rescol.substitute(sub.copy(), target)
                                
                    struc = rescol.get_chimera(self.session)
                    new_structures.append(struc)
            
            first_pass = False
        
        if not self.close_previous_bool:
            self.session.models.add(new_structures)
        
    def open_sub_selector(self):
        self.tool_window.create_child_window("select substituents", window_class=SubstituentSelection, textBox=self.subname)
        
class SubstituentSelection(ChildToolWindow):
    def __init__(self, tool_instance, title, textBox=None, **kwargs):
        super().__init__(tool_instance, title, **kwargs)
        
        self.textBox = textBox
        
        self._build_ui()
        
    def _build_ui(self):
        layout = QGridLayout()
        
        self.sub_table = SubstituentTable()
        self.sub_table.itemSelectionChanged.connect(self.refresh_selection)
        layout.addWidget(self.sub_table)
        
        self.ui_area.setLayout(layout)
        
        self.manage(None)
        
    def refresh_selection(self):
        sub_names = []
        for row in self.sub_table.selectionModel().selectedRows():
            sub_names.append(row.data())
            
        self.textBox.setText(",".join(sub_names))
        