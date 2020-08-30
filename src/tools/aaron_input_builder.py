from chimerax.atomic import AtomicStructure, selected_atoms, selected_bonds, selected_pseudobonds, get_triggers
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import StringArg, BoolArg, ListOf, IntArg
from chimerax.core.commands import run
from chimerax.core.models import ADD_MODELS, REMOVE_MODELS

from json import dumps, loads, dump, load

from PyQt5.Qt import QClipboard, QStyle, QIcon
from PyQt5.QtCore import Qt, QRegularExpression, pyqtSignal
from PyQt5.QtGui import QKeySequence, QFontMetrics, QFontDatabase
from PyQt5.QtWidgets import QCheckBox, QLabel, QGridLayout, QComboBox, QSplitter, QFrame, QLineEdit, \
                            QSpinBox, QMenuBar, QFileDialog, QAction, QApplication, QPushButton, \
                            QTabWidget, QWidget, QGroupBox, QListWidget, QTableWidget, QTableWidgetItem, \
                            QHBoxLayout, QFormLayout, QDoubleSpinBox, QHeaderView, QTextBrowser, \
                            QStatusBar, QTextEdit, QMessageBox, QTreeWidget, QTreeWidgetItem, QSizePolicy

from SEQCROW.widgets import PeriodicTable
from SEQCROW.tools.input_generator import MethodOption, BasisWidget, _InputGeneratorSettings


class AARONInputBuilder(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False    
    
    def __init__(self, session, name):
        super().__init__(session, name)
        
        self.settings = _InputGeneratorSettings(session, "Build QM Input", version="2")
        
        self.tool_window = MainToolWindow(self)        
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QGridLayout()
        
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        #job details
        job_widget = QWidget()
        job_layout = QFormLayout(job_widget)
        
        self.reaction_type = QComboBox()
        job_layout.addRow("reaction type:", self.reaction_type)
        
        self.template = QComboBox()
        job_layout.addRow("template:", self.template)
        
        self.input_format = QComboBox()
        self.input_format.addItems(['Perl', 'Python'])
        job_layout.addRow("AARON input format:", self.input_format)
        
        self.charge = QSpinBox()
        self.charge.setRange(-5, 5)
        job_layout.addRow("charge:", self.charge)
        
        self.multiplicity = QSpinBox()
        self.multiplicity.setRange(1, 3)
        job_layout.addRow("multiplicity:", self.multiplicity)
        
        tab_widget.addTab(job_widget, "job details")
        
        #settings
        settings_widget = QWidget()
        settings_layout = QGridLayout(settings_widget)
        
        settings_tabs = QTabWidget()
        settings_layout.addWidget(settings_tabs)
        
        self.low_widget = AARONSettingsWidget(self.settings)
        settings_tabs.addTab(self.low_widget, "low")        
        
        self.default_widget = AARONSettingsWidget(self.settings)
        settings_tabs.addTab(self.default_widget, "default")
        
        self.high_widget = AARONSettingsWidget(self.settings)
        settings_tabs.addTab(self.high_widget, "single point energy")

        tab_widget.addTab(settings_widget, "settings")


        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

class AARONSettingsWidget(QWidget):
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QGridLayout(self)
        #layout.setContentsMargins(0, 0, 0, 0)
        
        settings_tabs = QTabWidget()
        layout.addWidget(settings_tabs)
        
        form = 'Gaussian'
        self.method = MethodOption(settings, form)
        settings_tabs.addTab(self.method, "Method")
        
        self.basis = BasisWidget(settings, form)
        settings_tabs.addTab(self.basis, "Basis Sets")
        #menu stuff
        menu = QMenuBar()

        self.presets_menu = menu.addMenu("Presets")
        
        menu.setNativeMenuBar(False)
        layout.setMenuBar(menu)
        
        self.settings = settings
        self.presets = {}
        self.presets['Gaussian'] = loads(self.settings.gaussian_presets)
        self.presets['ORCA'] = loads(self.settings.orca_presets)
        self.presets['Psi4'] = loads(self.settings.psi4_presets)
        
        self.refresh_presets()
        
    def refresh_presets(self):
        """cleans and repopulates the "presets" dropdown on the tool's ribbon"""
        self.presets_menu.clear()
        
        for program in self.presets:
            program_submenu = self.presets_menu.addMenu(program)
            for preset in self.presets[program]:
                preset_action = QAction(preset, self)
                preset_action.triggered.connect(lambda *args, program=program, name=preset: self.apply_preset(program, name))
                program_submenu.addAction(preset_action)
                
        self.settings.gaussian_presets = dumps(self.presets['Gaussian'])
        self.settings.orca_presets = dumps(self.presets['ORCA'])
        self.settings.psi4_presets = dumps(self.presets['Psi4'])        
    
    def apply_preset(self, program, preset_name):
        """apply preset named 'preset_name' for 'program'"""
        preset = self.presets[program][preset_name]
        
        print("come back later")
        
        return