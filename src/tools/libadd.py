from chimerax.core.tools import ToolInstance

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QPushButton, QTabWidget, QWidget, QVBoxLayout, QLineEdit, QLabel, QSpinBox, QFormLayout

from AaronTools.component import Component
from AaronTools.ring import Ring
from AaronTools.substituent import Substituent

from ChimAARON.residue_collection import ResidueCollection

# TODO: change decorations to use ChimeraX atom/bond defaults

class LibAdd(ToolInstance):
    #XML_TAG ChimeraX :: Tool :: Add to Personal Library :: AaronTools :: Add to your personal ligand, substituent, and ring libraries
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    display_name = "Add to Personal AaronTools Library"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        
        self.showLigKeyBool = True
        self.showSubGhostBool = True
        self.showRingWalkBool = True
        
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()

        library_tabs = QTabWidget()
        
        
        #ligand tab
        ligand_tab = QWidget()
        ligand_layout = QGridLayout(ligand_tab)
        
        ligand_name_label = QLabel("ligand name:")
        ligand_layout.addWidget(ligand_name_label, 0, 0)
        ligand_name = QLineEdit()
        ligand_name.setText("")
        ligand_name.setToolTip("name of ligand you are adding to your ligand library\nleave blank to open a new model with just the ligand")
        ligand_layout.addWidget(ligand_name, 0, 1)
        
        ligand_key_atoms = QPushButton("set key atoms to current selection")
        ligand_key_atoms.setToolTip("the current selection will be the key atoms for the ligand\nleave blank to automatically determine key atoms")
        ligand_layout.addWidget(ligand_key_atoms, 1, 0, 1, 2)
        
        libadd_ligand = QPushButton("add current selection to library")
        ligand_layout.addWidget(libadd_ligand, 2, 0, 1, 2)  

        
        #substituent tab
        sub_tab = QWidget()
        sub_layout = QGridLayout(sub_tab)

        sub_info_form = QWidget()
        sub_info = QFormLayout(sub_info_form)
        
        sub_name = QLineEdit()
        sub_name.setText("")
        sub_name.setToolTip("name of substituent you are adding to your substituent library\nleave blank to open a new model with just the substituent")
        sub_info.addRow("substituent name:", sub_name)
        
        sub_confs = QSpinBox()
        sub_confs.setMinimum(1)
        sub_info.addRow("number of conformers:", sub_confs)
        
        sub_angle = QSpinBox()
        sub_angle.setRange(0, 180)
        sub_angle.setSingleStep(30)
        sub_info.addRow("angle between conformers:", sub_angle)
        
        sub_layout.addWidget(sub_info_form)
        
        libadd_sub = QPushButton("add current selection to library")
        sub_layout.addWidget(libadd_sub)

        #ring tab
        ring_tab = QWidget()
        ring_layout = QGridLayout(ring_tab)
        
        ring_name_label = QLabel("ring name:")
        ring_layout.addWidget(ring_name_label, 0, 0)
        ring_name = QLineEdit()
        ring_name.setText("")
        ring_name.setToolTip("name of ring you are adding to your ring library\nleave blank to open a new model with just the ring")
        ring_layout.addWidget(ring_name, 0, 1)
        
        libadd_ring = QPushButton("add ring with selected walk to library")
        ring_layout.addWidget(libadd_ring, 1, 0, 1, 2)
        
        
        library_tabs.addTab(sub_tab, "substituent")
        library_tabs.addTab(ring_tab, "ring")
        library_tabs.addTab(ligand_tab, "ligand")
        

        layout.addWidget(library_tabs)
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage('side')
