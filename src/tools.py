from chimerax.core.tools import ToolInstance
from PyQt5 import QtCore, QtGui, QtWidgets

class AaronTools_Library(ToolInstance):
    #XML_TAG ChimeraX :: Tool :: Browse AaronTools Libraries :: AaronTools :: Browse the AaronTools ligand, substituent, and ring libraries
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    display_name = "Browse AaronTools Libraries"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        
        self._build_ui()
        
    def _build_ui(self):
        from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout
        layout = QGridLayout()

        self.library_tabs = QtWidgets.QTabWidget()

        self.ligand_tab = QtWidgets.QWidget()
        self.ligand_layout = QtWidgets.QVBoxLayout(self.ligand_tab)
        
        self.substituent_tab = QtWidgets.QWidget()
        self.ring_tab = QtWidgets.QWidget()
        
        self.library_tabs.resize(300, 200)
        
        self.library_tabs.addTab(self.ligand_tab, "ligands")
        self.library_tabs.addTab(self.substituent_tab, "substituents")
        self.library_tabs.addTab(self.ring_tab, "rings")

        layout.addWidget(self.library_tabs)
        
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)