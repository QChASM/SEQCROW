from chimerax.core.tools import ToolInstance
from chimerax.ui.widgets import ColorButton
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QCheckBox, QTabWidget, QWidget, QVBoxLayout
from AaronTools.component import Component
from AaronTools.ringfragment import RingFragment
from AaronTools.substituent import Substituent

from .libraries import LigandTable, SubstituentTable, RingTable

class AaronTools_Library(ToolInstance):
    #XML_TAG ChimeraX :: Tool :: Browse AaronTools Libraries :: AaronTools :: Browse the AaronTools ligand, substituent, and ring libraries
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    display_name = "Browse AaronTools Libraries"
    
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

        self.library_tabs = QTabWidget()

        #add a tab for ligands
        self.ligand_tab = QWidget()
        self.ligand_layout = QVBoxLayout(self.ligand_tab)
        self.lig_table = LigandTable()
        self.ligand_layout.addWidget(self.lig_table)

        showKeyAtomsCheck = QCheckBox('show key atoms')
        showKeyAtomsCheck.setToolTip("ligand's coordinating atoms will be highlighted")
        showKeyAtomsCheck.toggle()
        showKeyAtomsCheck.stateChanged.connect(self.showKeyAtoms)
        self.ligand_layout.addWidget(showKeyAtomsCheck)
        
        self.lig_color = ColorButton('key atom color', has_alpha_channel=True)
        self.lig_color.setToolTip("highlight color for ligand's key atoms")
        self.lig_color.set_color([0.2, 0.5, 0.8, 0.5])
        self.ligand_layout.addWidget(self.lig_color)

        openLigButton = QPushButton("open selected ligands")
        openLigButton.setToolTip("ligands selected in the table will be loaded into ChimeraX")
        openLigButton.clicked.connect(self.open_ligands)
        self.ligand_layout.addWidget(openLigButton)

        #add a tab for substituents
        self.substituent_tab = QWidget()
        self.substituent_layout = QVBoxLayout(self.substituent_tab)
        self.sub_table = SubstituentTable()
        self.substituent_layout.addWidget(self.sub_table)
        
        showGhostConnectionCheck = QCheckBox('show ghost connection')
        showGhostConnectionCheck.setToolTip("ligand's coordinating atoms will be highlighted")
        showGhostConnectionCheck.toggle()
        showGhostConnectionCheck.stateChanged.connect(self.showGhostConnection)
        self.substituent_layout.addWidget(showGhostConnectionCheck)
        
        self.sub_color = ColorButton('ghost connection color', has_alpha_channel=True)
        self.sub_color.setToolTip("color of ghost connection")
        self.sub_color.set_color([0.60784, 0.145098, 0.70196, 0.5])
        self.substituent_layout.addWidget(self.sub_color)

        openSubButton = QPushButton("open selected substituents")
        openSubButton.setToolTip("substituents selected in the table will be loaded into ChimeraX")
        openSubButton.clicked.connect(self.open_substituents)
        self.substituent_layout.addWidget(openSubButton)
        
        #add a tab for rings
        self.ring_tab = QWidget()
        self.ring_layout = QVBoxLayout(self.ring_tab)
        self.ring_table = RingTable()
        self.ring_layout.addWidget(self.ring_table)
        
        showRingWalkCheck = QCheckBox('show ring walk')
        showRingWalkCheck.setToolTip("arrows will show the way AaronTools traverses the ring")
        showRingWalkCheck.toggle()
        showRingWalkCheck.stateChanged.connect(self.showRingWalk)
        self.ring_layout.addWidget(showRingWalkCheck)
        
        self.ring_color = ColorButton('walk arrow color', has_alpha_channel=True)
        self.ring_color.setToolTip("color of walk arrows")
        self.ring_color.set_color([0.9, 0.4, 0.3, 0.9])
        self.ring_layout.addWidget(self.ring_color)

        openRingButton = QPushButton("open selected rings")
        openRingButton.setToolTip("rings selected in the table will be loaded into ChimeraX")
        openRingButton.clicked.connect(self.open_rings)
        self.ring_layout.addWidget(openRingButton)
        
        self.library_tabs.resize(300, 200)
        
        self.library_tabs.addTab(self.ligand_tab, "ligands")
        self.library_tabs.addTab(self.substituent_tab, "substituents")
        self.library_tabs.addTab(self.ring_tab, "rings")

        layout.addWidget(self.library_tabs)
        
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage('side')

    def showKeyAtoms(self, state):
        if state == QtCore.Qt.Checked:
            self.showLigKeyBool = True
        else:
            self.showLigKeyBool = False

    def open_ligands(self):
        for row in self.lig_table.selectionModel().selectedRows():
            print(type(row.data()))
            
        self.session
        
        print('self has session property')
        
    def showGhostConnection(self, state):
        if state == QtCore.Qt.Checked:
            self.showSubGhostBool = True
        else:
            self.showSubGhostBool = False

    def open_substituents(self):
        print('poosh but on')
        
    def showRingWalk(self, state):
        if state == QtCore.Qt.Checked:
            self.showRingWalkBool = True
        else:
            self.showRingWalkBool = False

    def open_rings(self):
        print('poosh but on')