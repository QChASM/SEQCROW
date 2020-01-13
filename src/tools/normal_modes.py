from chimerax.core.tools import ToolInstance
from chimerax.ui.widgets import ColorButton
from chimerax.bild.bild import read_bild
from chimerax.core.models import MODEL_DISPLAY_CHANGED

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QTabWidget, QComboBox, QTableWidget, QTableView, QWidget, QVBoxLayout, QTableWidgetItem, QFormLayout, QCheckBox

class NormalModes(ToolInstance):
    #XML_TAG ChimeraX :: Tool :: Visualize normal modes :: AaronTools :: Visualize normal modes from a Gaussian output file as displacement vectors or as an animation
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    display_name = "Visualize normal modes"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        
        self.refresh_models()
        
        self._build_ui()

    def _build_ui(self):
        #TODO: make only the table resize up and down
        layout = QGridLayout()
        
        #select which molecule's frequencies to visualize
        model_selector = QComboBox()
        for model in self.models_with_freq:
            print(model)
            model_selector.addItem(model.name, model)
        
        model_selector.currentIndexChanged.connect(self.create_freq_table)
        self.model_selector = model_selector
        layout.addWidget(model_selector)
        
        #table that lists frequencies
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(['Frequency (cm^-1)', 'IR intensity'])
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QTableView.SelectRows)
        table.setSelectionMode(QTableView.SingleSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(table)
        self.table = table
        
        #tab thing to select animation or vectors
        self.display_tabs = QTabWidget()

        self.vector_tab = QWidget()
        self.vector_layout = QVBoxLayout(self.vector_tab)
        vec_opts_form = QWidget()
        vector_opts = QFormLayout(vec_opts_form)
        
        self.vec_scale = QLineEdit()
        self.vec_scale.setText('1.5')
        self.vec_scale.setToolTip("vectors will be scaled so that the longest is this many Angstroms long")
        vector_opts.addRow("vector scale:", self.vec_scale)
        
        self.vec_use_mass_weighted = QCheckBox()
        self.vec_use_mass_weighted.setToolTip("if checked, vectors will show mass-weighted displacements")
        vector_opts.addRow("use mass-weighted:", self.vec_use_mass_weighted)
        
        self.vector_layout.addWidget(vec_opts_form)
        
        self.vector_color = ColorButton("vector color", has_alpha_channel=True)
        self.vector_color.setToolTip("color of vectors")
        self.vector_color.set_color([0.0, 1.0, 0.0, 1.0])
        self.vector_layout.addWidget(self.vector_color)
        
        show_vec_button = QPushButton("display selected modes")
        self.vector_layout.addWidget(show_vec_button)
        
        self.animate_tab = QWidget()
        self.animate_layout = QVBoxLayout(self.animate_tab)
        anim_opts_form = QWidget()
        anim_opts = QFormLayout(anim_opts_form)
        
        self.anim_scale = QLineEdit()
        self.anim_scale.setText('1.5')
        self.anim_scale.setToolTip("max. Angstroms an atom is displaced from equilibrium")
        anim_opts.addRow("max. displacement:", self.anim_scale)
        
        self.anim_duration = QLineEdit()
        self.anim_duration.setToolTip("number of frames in animation")
        anim_opts.addRow("duration:", self.anim_duration)
        
        self.animate_layout.addWidget(anim_opts_form)
        
        show_anim_button = QPushButton("display selected modes")
        self.animate_layout.addWidget(show_anim_button)
        
        self.display_tabs.addTab(self.animate_tab, "animate")
        self.display_tabs.addTab(self.vector_tab, "vectors")
        
        layout.addWidget(self.display_tabs)
        
        self.tool_window.ui_area.setLayout(layout)

        if len(self.models_with_freq) > 0:
            self.create_freq_table(0)

        self.tool_window.manage('side')
        
    def create_freq_table(self, state):
        """populate the table with frequencies from self.models_with_freq[state]"""
        model = self.models_with_freq[state]
        
        self.table.setRowCount(0)
        
        freq_data = model.aarontools_filereader.other['frequency'].data
        
        for mode in freq_data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            freq = QTableWidgetItem()
            freq.setData(Qt.DisplayRole, round(mode.frequency, 2))
            self.table.setItem(row, 0, freq)
            
            intensity = QTableWidgetItem()
            if mode.intensity is not None:
                intensity.setData(Qt.DisplayRole, round(mode.intensity, 2))
            self.table.setItem(row, 1, intensity)
    
    def refresh_models(self):
        self.models_with_freq = self.session.chimaaron_frequency_file_manager.frequency_models

        