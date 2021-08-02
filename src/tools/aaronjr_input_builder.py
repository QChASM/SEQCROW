from chimerax.atomic import AtomicStructure, selected_atoms, selected_bonds, selected_pseudobonds, get_triggers
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import StringArg, BoolArg, ListOf, IntArg
from chimerax.core.commands import run
from chimerax.core.models import ADD_MODELS, REMOVE_MODELS

from json import dumps, loads, dump, load

from Qt.QtCore import Qt, QRegularExpression, Signal
from Qt.QtGui import QKeySequence, QFontMetrics, QFontDatabase, QClipboard, QIcon
from Qt.QtWidgets import (
    QCheckBox,
    QLabel,
    QGridLayout,
    QComboBox,
    QSplitter,
    QFrame,
    QLineEdit, 
    QSpinBox,
    QMenuBar,
    QFileDialog,
    QAction,
    QApplication,
    QPushButton, 
    QTabWidget,
    QWidget,
    QGroupBox,
    QListWidget,
    QTableWidget,
    QTableWidgetItem, 
    QHBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QHeaderView,
    QTextBrowser, 
    QStatusBar,
    QTextEdit,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QSizePolicy, 
    QStyle
)

from SEQCROW.widgets import PeriodicTable
from SEQCROW.tools.input_generator import MethodOption, BasisWidget, _InputGeneratorSettings
from SEQCROW.tools.coordination_complexes import create_coord_items

class AARONInputBuilder(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False    
    
    def __init__(self, session, name):
        super().__init__(session, name)
        
        self.theory_settings = _InputGeneratorSettings(
            session, "Build QM Input", version="3"
        )
        
        self.tool_window = MainToolWindow(self)        
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QGridLayout()
        
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        structure_widget = QWidget()
        structure_layout = QGridLayout(structure_widget)
        tab_widget.addTab(structure_widget, "structure")
        
        self.structure_source = QComboBox()
        self.structure_source.addItems([
            "AARON template", "file", "coordination complexes", "SMILES"
        ])
        
        structure_layout.addWidget(
            QLabel("structure source:"),
            0, 0, 1, 1,
            Qt.AlignLeft | Qt.AlignVCenter
        )
        
        structure_layout.addWidget(
            self.structure_source,
            0, 1, 1, 1, 
        )
        
        open_button = QPushButton("open")
        open_button.clicked.connect(self.open_template)
        structure_layout.addWidget(
            open_button,
            0, 2, 1, 1,
        )

        # SMILES options
        self.smiles_options = QGroupBox("SMILES options")
        smiles_layout = QFormLayout(self.smiles_options)
        structure_layout.addWidget(
            self.smiles_options,
            1, 0, 1, 3,
            Qt.AlignTop | Qt.AlignHCenter
        )
        
        self.smiles_line = QLineEdit()
        smiles_layout.addRow("SMILES string:", self.smiles_line)
        
        self.smiles_options.setVisible(
            self.structure_source.currentText() == "SMILES"
        )
        self.structure_source.currentTextChanged.connect(
            lambda text: self.smiles_options.setVisible(
                text == "SMILES"
            )
        )

        # coordination complexes options
        self.coord_comp_options = QGroupBox("Coordination Complex Options")
        coord_layout = QFormLayout(self.coord_comp_options)
        structure_layout.addWidget(
            self.coord_comp_options,
            1, 0, 1, 3,
            Qt.AlignTop | Qt.AlignHCenter
        )
        
        create_coord_items(
            self, coord_layout, allow_minimization=False, default_ele="Pd"
        )
        
        self.coord_comp_options.setVisible(
            self.structure_source.currentText() == "coordination complexes"
        )
        self.structure_source.currentTextChanged.connect(
            lambda text: self.coord_comp_options.setVisible(
                text == "coordination complexes"
            )
        )

        # aaron template options
        self.aaron_options = QGroupBox("AARON template structures")
        aaron_layout = QFormLayout(self.aaron_options)
        structure_layout.addWidget(
            self.aaron_options,
            1, 0, 1, 3,
            Qt.AlignTop | Qt.AlignHCenter
        )
        
        self.aaron_options.setVisible(
            self.structure_source.currentText() == "AARON template"
        )
        self.structure_source.currentTextChanged.connect(
            lambda text: self.aaron_options.setVisible(
                text == "AARON template"
            )
        )

        # file options
        self.file_options = QGroupBox("single file options")
        file_layout = QFormLayout(self.file_options)
        structure_layout.addWidget(
            self.file_options,
            1, 0, 1, 3,
            Qt.AlignTop | Qt.AlignHCenter
        )
        
        file_widget = QWidget()
        file_browse_layout = QGridLayout(file_widget)
        
        self.template_file = QLineEdit()
        file_browse_layout.addWidget(
            self.template_file, 0, 0, 1, 1,
            Qt.AlignCenter
        )
        browse_button = QPushButton("browse...")
        # browse_button.clicked.connect(self.browse_file_template)
        file_browse_layout.addWidget(
            browse_button, 0, 1, 1, 1,
            Qt.AlignCenter
        )
        
        file_browse_layout.setColumnStretch(0, 1)
        file_browse_layout.setColumnStretch(1, 0)
        margins = file_browse_layout.contentsMargins()
        file_browse_layout.setContentsMargins(margins.left(), 0, margins.right(), 0)
        
        file_layout.addRow("file:", file_widget)
        
        self.file_options.setVisible(
            self.structure_source.currentText() == "file"
        )
        self.structure_source.currentTextChanged.connect(
            lambda text: self.file_options.setVisible(
                text == "file"
            )
        )
    
        self.optimize_template = QCheckBox()
        self.optimize_template.setCheckState(Qt.Checked)
        structure_layout.addWidget(
            QLabel("optimize template:"),
            2, 0, 1, 1,
            Qt.AlignLeft | Qt.AlignVCenter,
        )
        structure_layout.addWidget(
            self.optimize_template,
            2, 1, 1, 2,
            Qt.AlignLeft | Qt.AlignVCenter,
        )
        
        structure_layout.setColumnStretch(0, 0)
        structure_layout.setColumnStretch(1, 1)
        structure_layout.setColumnStretch(2, 0)


        # structure changes
        changes_widget = QWidget()
        changes_layout = QGridLayout(changes_widget)
        tab_widget.addTab(changes_widget, "changes")


        # HPC settings
        hpc_widget = QWidget()
        hpc_layout = QGridLayout(hpc_widget)
        tab_widget.addTab(hpc_widget, "HPC")
        

        # theory settings
        theory_widget = QWidget()
        theory_layout = QGridLayout(theory_widget)
        tab_widget.addTab(theory_widget, "theory")
        

        # results
        results_widget = QWidget()
        results_layout = QGridLayout(results_widget)
        tab_widget.addTab(results_widget, "results")
        

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def open_template(self):
        pass

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
        self._menu = menu
        layout.setMenuBar(menu)
        menu.setVisible(True)
        
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