import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands import run
from chimerax.core.commands.cli import FloatArg, BoolArg, StringArg, IntArg

from numpy import isclose

from PyQt5.Qt import QClipboard, QStyle, QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QLabel, QGridLayout, QComboBox, QSplitter, QLineEdit, QDoubleSpinBox, \
                            QMenuBar, QFileDialog, QAction, QApplication, QWidget, QGroupBox, QStatusBar, \
                            QTabWidget, QTreeWidget, QSizePolicy, QPushButton, QHeaderView, QHBoxLayout, \
                            QTreeWidgetItem

from os.path import basename

from SEQCROW.widgets import FilereaderComboBox

from AaronTools.comp_output import CompOutput
from AaronTools.geometry import Geometry
from AaronTools.const import PHYSICAL, UNIT

class _ComputeThermoSettings(Settings):

    AUTO_SAVE = {
        'w0': Value(100.0, FloatArg, str),
        'include_header': Value(True, BoolArg, str),
        'delimiter': Value('comma', StringArg), 
        'rel_temp': Value(298.15, FloatArg, str), 
        'ref_col_1': Value(150, IntArg), 
        'ref_col_2': Value(150, IntArg), 
        'ref_col_3': Value(50, IntArg),         
        'other_col_1': Value(150, IntArg), 
        'other_col_2': Value(150, IntArg), 
        'other_col_3': Value(50, IntArg), 
    }


class Thermochem(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    help = "https://github.com/QChASM/SEQCROW/wiki/Process-Thermochemistry-Tool"

    theory_helper = {"Grimme's Quasi-RRHO":"https://doi.org/10.1002/chem.201200497",
                     "Truhlar's Quasi-Harmonic":"https://doi.org/10.1021/jp205508z"}
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.display_name = "Thermochemistry"
        
        self.tool_window = MainToolWindow(self)        

        self.settings = _ComputeThermoSettings(self.session, name)

        self.nrg_fr = {}
        self.thermo_fr = {}
        self.thermo_co = {}

        self._build_ui()
        
        self.set_sp()
        self.set_thermo_mdl()
        
        self.calc_relative_thermo()

    def _build_ui(self):
        #each group has an empty widget at the bottom so they resize the way I want while also having the
        #labels where I want them
        layout = QGridLayout()

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        #layout for absolute thermo stuff
        absolute_widget = QWidget()
        absolute_layout = QGridLayout(absolute_widget)


        #box for sp
        sp_area_widget = QGroupBox("Single-point")
        sp_layout = QGridLayout(sp_area_widget)

        self.sp_selector = FilereaderComboBox(self.session, otherItems=['energy'])
        self.sp_selector.currentIndexChanged.connect(self.set_sp)
        sp_layout.addWidget(self.sp_selector, 0, 0, 1, 3, Qt.AlignTop)
        
        nrg_label = QLabel("E =")
        sp_layout.addWidget(nrg_label, 1, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        self.sp_nrg_line = QLineEdit()
        self.sp_nrg_line.setReadOnly(True)
        self.sp_nrg_line.setToolTip("electronic energy")
        sp_layout.addWidget(self.sp_nrg_line, 1, 1, 1, 1, Qt.AlignTop)
        
        sp_layout.addWidget(QLabel("E<sub>h</sub>"), 1, 2, 1, 1, Qt.AlignVCenter)
        
        sp_layout.addWidget(QWidget(), 2, 0)
        
        sp_layout.setColumnStretch(0, 0)
        sp_layout.setColumnStretch(1, 1)
        sp_layout.setRowStretch(0, 0)
        sp_layout.setRowStretch(1, 0)
        sp_layout.setRowStretch(2, 1)
        

        row = 0
        #box for thermo
        therm_area_widget = QGroupBox("Thermal corrections")
        thermo_layout = QGridLayout(therm_area_widget)

        self.thermo_selector = FilereaderComboBox(self.session, otherItems=['frequency'])
        self.thermo_selector.currentIndexChanged.connect(self.set_thermo_mdl)
        thermo_layout.addWidget(self.thermo_selector, row, 0, 1, 3, Qt.AlignTop)

        row += 1

        thermo_layout.addWidget(QLabel("T ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        self.temperature_line = QDoubleSpinBox()
        self.temperature_line.setMaximum(2**31 - 1)
        self.temperature_line.setValue(298.15)
        self.temperature_line.setSingleStep(10)
        self.temperature_line.setSuffix(" K")
        self.temperature_line.setMinimum(0)
        self.temperature_line.valueChanged.connect(self.set_thermo)
        thermo_layout.addWidget(self.temperature_line, row, 1, 1, 2, Qt.AlignTop)
        
        row += 1
        
        thermo_layout.addWidget(QLabel("𝜔<sub>0</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        self.v0_edit = QDoubleSpinBox()
        self.v0_edit.setMaximum(4000)
        self.v0_edit.setValue(self.settings.w0)
        self.v0_edit.setSingleStep(25)
        self.v0_edit.setSuffix(" cm\u207b\u00b9")
        self.v0_edit.valueChanged.connect(self.set_thermo)
        self.v0_edit.setMinimum(0)
        self.v0_edit.setToolTip("frequency parameter for quasi treatments of entropy")
        thermo_layout.addWidget(self.v0_edit, row, 1, 1, 2, Qt.AlignTop)
        
        row += 1
    
        thermo_layout.addWidget(QLabel("𝛿ZPE ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)

        self.zpe_line = QLineEdit()
        self.zpe_line.setReadOnly(True)
        self.zpe_line.setToolTip("zero-point energy correction")
        thermo_layout.addWidget(self.zpe_line, row, 1, 1, 1, Qt.AlignTop)
        
        thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignVCenter)  
        
        row += 1

        thermo_layout.addWidget(QLabel("𝛿H<sub>RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)

        self.enthalpy_line = QLineEdit()
        self.enthalpy_line.setReadOnly(True)
        self.enthalpy_line.setToolTip("RRHO enthalpy correction")
        thermo_layout.addWidget(self.enthalpy_line, row, 1, 1, 1, Qt.AlignTop)
        
        thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignVCenter)        

        row += 1

        thermo_layout.addWidget(QLabel("𝛿G<sub>RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)

        self.rrho_g_line = QLineEdit()
        self.rrho_g_line.setReadOnly(True)
        self.rrho_g_line.setToolTip("""RRHO free energy correction\nRotational motion is completely independent from vibrations\nNormal mode vibrations behave like harmonic oscillators""")
        thermo_layout.addWidget(self.rrho_g_line, row, 1, 1, 1, Qt.AlignTop)
        
        thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignVCenter)        
        
        row += 1
        
        dqrrho_g_label = QLabel()
        dqrrho_g_label.setText("<a href=\"Grimme's Quasi-RRHO\" style=\"text-decoration: none;\">𝛿G<sub>Quasi-RRHO</sub></a> =")
        dqrrho_g_label.setTextFormat(Qt.RichText)
        dqrrho_g_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        dqrrho_g_label.linkActivated.connect(self.open_link)
        dqrrho_g_label.setToolTip("click to open a relevant reference\n" + \
                                  "see the \"Computation of internal (gas‐phase) entropies\" section for a description of the method")
        
        thermo_layout.addWidget(dqrrho_g_label, row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        self.qrrho_g_line = QLineEdit()
        self.qrrho_g_line.setReadOnly(True)
        self.qrrho_g_line.setToolTip("Quasi-RRHO free energy correction\n" + \
        "Vibrational entropy of each mode is weighted and complemented with rotational entropy\n" + \
        "The weighting is much lower for modes with frequencies less than 𝜔\u2080")        
        thermo_layout.addWidget(self.qrrho_g_line, row, 1, 1, 1, Qt.AlignTop)
        
        thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignVCenter)        
        
        row += 1
        
        dqharm_g_label = QLabel("")
        dqharm_g_label.setText("<a href=\"Truhlar's Quasi-Harmonic\" style=\"text-decoration: none;\">𝛿G<sub>Quasi-Harmonic</sub></a> =")
        dqharm_g_label.setTextFormat(Qt.RichText)
        dqharm_g_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        dqharm_g_label.linkActivated.connect(self.open_link)
        dqharm_g_label.setToolTip("click to open a relevant reference\n" + \
                                  "see the \"Computations\" section for a description of the method")
        
        thermo_layout.addWidget(dqharm_g_label, row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        self.qharm_g_line = QLineEdit()
        self.qharm_g_line.setReadOnly(True)
        self.qharm_g_line.setToolTip("Quasi-hamonic free energy correction\n" + \
        "For entropy, real vibrational modes lower than 𝜔\u2080 are treated as 𝜔\u2080")
        thermo_layout.addWidget(self.qharm_g_line, row, 1, 1, 1, Qt.AlignTop)
        
        thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignVCenter)

        thermo_layout.addWidget(QWidget(), row + 1, 0)

        thermo_layout.setColumnStretch(0, 0)
        thermo_layout.setColumnStretch(1, 1)
        for i in range(0, row):
            thermo_layout.setRowStretch(i, 0)
        
        thermo_layout.setRowStretch(row + 1, 1)        
        
        
        row = 0
        # for for total
        sum_area_widget = QGroupBox("Thermochemistry")
        sum_layout = QGridLayout(sum_area_widget)

        sum_layout.addWidget(QLabel("ZPE ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        self.zpe_sum_line = QLineEdit()
        self.zpe_sum_line.setReadOnly(True)
        self.zpe_sum_line.setToolTip("sum of electronic energy and ZPE correction")
        sum_layout.addWidget(self.zpe_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignVCenter)      
        
        row += 1

        sum_layout.addWidget(QLabel("H<sub>RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        self.h_sum_line = QLineEdit()
        self.h_sum_line.setReadOnly(True)
        self.h_sum_line.setToolTip("sum of electronic energy and RRHO enthalpy correction")
        sum_layout.addWidget(self.h_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignVCenter)      
        
        row += 1
        
        sum_layout.addWidget(QLabel("G<sub>RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        self.rrho_g_sum_line = QLineEdit()
        self.rrho_g_sum_line.setReadOnly(True)
        self.rrho_g_sum_line.setToolTip("sum of electronic energy and RRHO free energy correction\nRotational motion is completely independent from vibrations\nNormal mode vibrations behave like harmonic oscillators")
        sum_layout.addWidget(self.rrho_g_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignVCenter)        
        
        row += 1
        
        sum_layout.addWidget(QLabel("G<sub>Quasi-RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        self.qrrho_g_sum_line = QLineEdit()
        self.qrrho_g_sum_line.setReadOnly(True)
        self.qrrho_g_sum_line.setToolTip("Sum of electronic energy and quasi-RRHO free energy correction\n" + \
        "Vibrational entropy of each mode is weighted and complemented with rotational entropy\n" + \
        "The weighting is much lower for modes with frequencies less than 𝜔\u2080")
        sum_layout.addWidget(self.qrrho_g_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignVCenter)  
        
        row += 1
        
        sum_layout.addWidget(QLabel("G<sub>Quasi-Harmonic</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        self.qharm_g_sum_line = QLineEdit()
        self.qharm_g_sum_line.setReadOnly(True)
        self.qharm_g_sum_line.setToolTip("Sum of electronic energy and quasi-harmonic free energy correction\n" + \
        "For entropy, real vibrational modes lower than 𝜔\u2080 are treated as 𝜔\u2080")
        sum_layout.addWidget(self.qharm_g_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignVCenter)

        sum_layout.addWidget(QWidget(), row + 1, 0)
        
        sum_layout.setColumnStretch(0, 0)
        for i in range(0, row):
            sum_layout.setRowStretch(i, 0)

        sum_layout.setRowStretch(row + 1, 1)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(sp_area_widget)
        splitter.addWidget(therm_area_widget)
        splitter.addWidget(sum_area_widget)
        
        absolute_layout.addWidget(splitter)

        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        self.status.setStyleSheet("color: red")
        absolute_layout.addWidget(self.status, 1, 0, 1, 1, Qt.AlignTop)

        self.tab_widget.addTab(absolute_widget, "absolute")


        relative_widget = QWidget()
        relative_layout = QGridLayout(relative_widget)

        size = [self.settings.ref_col_1, self.settings.ref_col_2, self.settings.ref_col_3]
        self.ref_group = ThermoGroup("reference group", self.session, self.nrg_fr, self.thermo_co, size)
        self.ref_group.changes.connect(self.calc_relative_thermo)
        relative_layout.addWidget(self.ref_group, 0, 0, 1, 3, Qt.AlignTop)
        
        size = [self.settings.other_col_1, self.settings.other_col_2, self.settings.other_col_3]
        self.other_group = ThermoGroup("other group", self.session, self.nrg_fr, self.thermo_co, size)
        self.other_group.changes.connect(self.calc_relative_thermo)
        relative_layout.addWidget(self.other_group, 0, 3, 1, 3, Qt.AlignTop)
        
        self.relative_temperature = QDoubleSpinBox()
        self.relative_temperature.setMaximum(2**31 - 1)
        self.relative_temperature.setValue(self.settings.rel_temp)
        self.relative_temperature.setSingleStep(10)
        self.relative_temperature.setSuffix(" K")
        self.relative_temperature.setMinimum(0)
        self.relative_temperature.valueChanged.connect(self.calc_relative_thermo)
        relative_layout.addWidget(QLabel("T ="), 1, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        relative_layout.addWidget(self.relative_temperature, 1, 1, 1, 5, Qt.AlignLeft | Qt.AlignVCenter)

        self.relative_v0 = QDoubleSpinBox()
        self.relative_v0.setMaximum(2**31 - 1)
        self.relative_v0.setValue(self.settings.w0)
        self.relative_v0.setSingleStep(25)
        self.relative_v0.setSuffix(" cm\u207b\u00b9")
        self.relative_v0.setMinimum(0)
        self.relative_v0.setToolTip("frequency parameter for quasi treatments of entropy")
        self.relative_v0.valueChanged.connect(self.calc_relative_thermo)
        relative_layout.addWidget(QLabel("𝜔<sub>0</sub> ="), 2, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        relative_layout.addWidget(self.relative_v0, 2, 1, 1, 5, Qt.AlignLeft | Qt.AlignVCenter)

        relative_layout.addWidget(QLabel("relative energies in kcal/mol:"), 3, 0, 1, 6, Qt.AlignVCenter | Qt.AlignLeft)
        
        relative_layout.addWidget(QLabel("ΔE"), 4, 0, Qt.AlignTop | Qt.AlignVCenter)
        self.relative_dE = QLineEdit()
        self.relative_dE.setReadOnly(True)
        relative_layout.addWidget(self.relative_dE, 5, 0, Qt.AlignTop | Qt.AlignVCenter)
        
        relative_layout.addWidget(QLabel("ΔZPE"), 4, 1, Qt.AlignTop | Qt.AlignVCenter)
        self.relative_dZPVE = QLineEdit() 
        self.relative_dZPVE.setReadOnly(True)        
        relative_layout.addWidget(self.relative_dZPVE, 5, 1, Qt.AlignTop | Qt.AlignVCenter)

        relative_layout.addWidget(QLabel("ΔH<sub>RRHO</sub>"), 4, 2, Qt.AlignTop | Qt.AlignVCenter)
        self.relative_dH = QLineEdit()
        self.relative_dH.setReadOnly(True)
        relative_layout.addWidget(self.relative_dH, 5, 2, Qt.AlignTop | Qt.AlignVCenter)

        relative_layout.addWidget(QLabel("ΔG<sub>RRHO</sub>"), 4, 3, Qt.AlignTop | Qt.AlignVCenter)
        self.relative_dG = QLineEdit()
        self.relative_dG.setReadOnly(True)
        relative_layout.addWidget(self.relative_dG, 5, 3, Qt.AlignTop | Qt.AlignVCenter)

        relative_layout.addWidget(QLabel("ΔG<sub>Quasi-RRHO</sub>"), 4, 4, Qt.AlignTop | Qt.AlignVCenter)
        self.relative_dQRRHOG = QLineEdit()
        self.relative_dQRRHOG.setReadOnly(True)
        relative_layout.addWidget(self.relative_dQRRHOG, 5, 4, Qt.AlignTop | Qt.AlignVCenter)

        relative_layout.addWidget(QLabel("ΔG<sub>Quasi-Harmonic</sub>"), 4, 5, Qt.AlignTop | Qt.AlignVCenter)
        self.relative_dQHARMG = QLineEdit()
        self.relative_dQHARMG.setReadOnly(True)
        relative_layout.addWidget(self.relative_dQHARMG, 5, 5, Qt.AlignTop | Qt.AlignVCenter)

        
        relative_layout.setRowStretch(0, 1)
        relative_layout.setRowStretch(1, 0)
        relative_layout.setRowStretch(2, 0)
        relative_layout.setRowStretch(3, 0)
        relative_layout.setRowStretch(4, 0)
        relative_layout.setRowStretch(5, 0)
        
        self.tab_widget.addTab(relative_widget, "relative")
        
        #menu stuff
        menu = QMenuBar()
        
        export = menu.addMenu("&Export")
        copy = QAction("&Copy CSV to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_csv)
        shortcut = QKeySequence(Qt.CTRL + Qt.Key_C)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        
        save = QAction("&Save CSV...", self.tool_window.ui_area)
        save.triggered.connect(self.save_csv)
        #this shortcut interferes with main window's save shortcut
        #I've tried different shortcut contexts to no avail
        #thanks Qt...
        #shortcut = QKeySequence(Qt.CTRL + Qt.Key_S)
        #save.setShortcut(shortcut)
        #save.setShortcutContext(Qt.WidgetShortcut)
        export.addAction(save)

        delimiter = export.addMenu("Delimiter")
        
        comma = QAction("comma", self.tool_window.ui_area, checkable=True)
        comma.setChecked(self.settings.delimiter == "comma")
        comma.triggered.connect(lambda *args, delim="comma": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(comma)
        
        tab = QAction("tab", self.tool_window.ui_area, checkable=True)
        tab.setChecked(self.settings.delimiter == "tab")
        tab.triggered.connect(lambda *args, delim="tab": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(tab)
        
        space = QAction("space", self.tool_window.ui_area, checkable=True)
        space.setChecked(self.settings.delimiter == "space")
        space.triggered.connect(lambda *args, delim="space": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(space)
        
        semicolon = QAction("semicolon", self.tool_window.ui_area, checkable=True)
        semicolon.setChecked(self.settings.delimiter == "semicolon")
        semicolon.triggered.connect(lambda *args, delim="semicolon": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(semicolon)
        
        add_header = QAction("&Include CSV header", self.tool_window.ui_area, checkable=True)
        add_header.setChecked(self.settings.include_header)
        add_header.triggered.connect(self.header_check)
        export.addAction(add_header)
        
        comma.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        comma.triggered.connect(lambda *args, action=space: action.setChecked(False))
        comma.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        tab.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        tab.triggered.connect(lambda *args, action=space: action.setChecked(False))
        tab.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        space.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        space.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        space.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        semicolon.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        semicolon.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        semicolon.triggered.connect(lambda *args, action=space: action.setChecked(False))

        menu.setNativeMenuBar(False)
        layout.setMenuBar(menu)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def calc_relative_thermo(self, *args):
        def calc_free_energies(nrg_list, co_list, T, w0):
            ZPVEs = []
            Hs = []
            Gs = []
            RRHOG = []
            QHARMG = []
            for i in range(0, len(nrg_list)):
                ZPVEs.append([])
                Hs.append([])
                Gs.append([])
                RRHOG.append([])
                QHARMG.append([])
                for nrg, co in zip(nrg_list[i], co_list[i]):
                    ZPVE = co.ZPVE
                    ZPVEs[-1].append(nrg + ZPVE)
                    
                    dH = co.therm_corr(T, w0, CompOutput.RRHO)[1]
                    Hs[-1].append(nrg + dH)
                    
                    dG = co.calc_G_corr(temperature=T, v0=w0, method=CompOutput.RRHO)
                    Gs[-1].append(nrg + dG)            
                    
                    dQRRHOG = co.calc_G_corr(temperature=T, v0=w0, method=CompOutput.QUASI_RRHO)
                    RRHOG[-1].append(nrg + dQRRHOG)
                    
                    dQHARMG = co.calc_G_corr(temperature=T, v0=w0, method=CompOutput.QUASI_HARMONIC)
                    QHARMG[-1].append(nrg + dQHARMG)
            
            return ZPVEs, Hs, Gs, RRHOG, QHARMG
        
        def boltzmann_weight(energies1, energies2, T):
            
            totals1 = []
            totals2 = []

            beta = UNIT.HART_TO_JOULE/(PHYSICAL.KB * T)
            
            for energy_group in energies1:
                if len(energy_group) == 0:
                    continue
                    
                rezero = min(energy_group)
                rel_nrgs = [(x - rezero) for x in energy_group]
                weights = [np.exp(-beta*nrg) for nrg in rel_nrgs]

                totals1.append(-PHYSICAL.BOLTZMANN * T * np.log(sum(weights)) + rezero * UNIT.HART_TO_KCAL)

            for energy_group in energies2:
                if len(energy_group) == 0:
                    continue
                    
                rezero = min(energy_group)
                rel_nrgs = [(x - rezero) for x in energy_group]
                weights = [np.exp(-beta*nrg) for nrg in rel_nrgs]

                totals2.append(-PHYSICAL.BOLTZMANN * T * np.log(sum(weights)) + rezero * UNIT.HART_TO_KCAL)

            return sum(totals2) - sum(totals1)

        ref_Es = self.ref_group.energies()
        ref_cos = self.ref_group.compOutputs()
        
        empty_groups = []
        for i, group in enumerate(ref_cos):
            if len(group) == 0:
                empty_groups.append(i)
        
        for ndx in empty_groups[::-1]:
            ref_Es.pop(ndx)
            ref_cos.pop(ndx)
        
        other_Es = self.other_group.energies()
        other_cos = self.other_group.compOutputs()
        
        empty_groups = []
        for i, group in enumerate(other_cos):
            if len(group) == 0:
                empty_groups.append(i)
        
        for ndx in empty_groups[::-1]:
            other_Es.pop(ndx)
            other_cos.pop(ndx)

        if any(len(x) == 0  or all(len(x) == 0 for y in x) for x in [ref_Es, other_Es, ref_cos, other_cos]):
            self.relative_dE.setText("")
            self.relative_dZPVE.setText("")
            self.relative_dH.setText("")
            self.relative_dG.setText("")
            self.relative_dQRRHOG.setText("")
            self.relative_dQHARMG.setText("")
            return
        
        T = self.relative_temperature.value()
        self.settings.rel_temp = T
        w0 = self.relative_v0.value()

        if w0 != self.settings.w0:
            self.settings.w0 = w0

        ref_ZPVEs, ref_Hs, ref_Gs, ref_QRRHOGs, ref_QHARMGs = calc_free_energies(ref_Es, ref_cos, T, w0)
        other_ZPVEs, other_Hs, other_Gs, other_QRRHOGs, other_QHARMGs = calc_free_energies(other_Es, other_cos, T, w0)
        
        rel_E = boltzmann_weight(ref_Es, other_Es, T)
        rel_ZPVE = boltzmann_weight(ref_ZPVEs, other_ZPVEs, T)
        rel_H = boltzmann_weight(ref_Hs, other_Hs, T)
        rel_G = boltzmann_weight(ref_Gs, other_Gs, T)
        rel_QRRHOG = boltzmann_weight(ref_QRRHOGs, other_QRRHOGs, T)
        rel_QHARMG = boltzmann_weight(ref_QHARMGs, other_QHARMGs, T)
        
        self.relative_dE.setText("%.1f" % rel_E)
        self.relative_dZPVE.setText("%.1f" % rel_ZPVE)
        self.relative_dH.setText("%.1f" % rel_H)
        self.relative_dG.setText("%.1f" % rel_G)
        self.relative_dQRRHOG.setText("%.1f" % rel_QRRHOG)
        self.relative_dQHARMG.setText("%.1f" % rel_QHARMG)

    def open_link(self, theory):
        link = self.theory_helper[theory]
        run(self.session, "open %s" % link)

    def save_csv(self):
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
        if filename:
            s = self.get_csv()
   
            with open(filename, 'w') as f:
                f.write(s.strip())
                
            self.session.logger.status("saved to %s" % filename)

    def copy_csv(self):
        app = QApplication.instance()
        clipboard = app.clipboard()
        csv = self.get_csv()
        clipboard.setText(csv)
        self.session.logger.status("copied to clipboard")

    def get_csv(self):
        if self.settings.delimiter == "comma":
            delim = ","
        elif self.settings.delimiter == "space":
            delim = " "
        elif self.settings.delimiter == "tab":
            delim = "\t"
        elif self.settings.delimiter == "semicolon":
            delim = ";"

        if self.tab_widget.currentIndex() == 0:
            if self.settings.include_header:
                s = delim.join(["E" , "ZPE", "H(RRHO)", "G(RRHO)", "G(Quasi-RRHO)", "G(Quasi-harmonic)", \
                                "dZPE", "dH(RRHO)", "dG(RRHO)", "dG(Quasi-RRHO)", "dG(Quasi-harmonic)", \
                                "SP File", "Thermo File"])
                
                s += "\n"
            else:
                s = ""
            
            float_fmt = "%.12f" + delim
            str_dmt = "%s" + delim + "%s"
            
            fmt = 11*float_fmt + str_dmt + "\n"
            
            E    = float(self.sp_nrg_line.text())
            
            dZPE = float(self.zpe_line.text())
            dH       = float(self.enthalpy_line.text())
            rrho_dG  = float(self.rrho_g_line.text())
            qrrho_dG = float(self.qrrho_g_line.text())
            qharm_dG = float(self.qharm_g_line.text())            
            
            ZPE = float(self.zpe_sum_line.text())
            H       = float(self.h_sum_line.text())
            rrho_G  = float(self.rrho_g_sum_line.text())
            qrrho_G = float(self.qrrho_g_sum_line.text())
            qharm_G = float(self.qharm_g_sum_line.text())
            
            sp_mdl = self.sp_selector.currentData()
            sp_name = sp_mdl.name
                        
            therm_mdl = self.thermo_selector.currentData()
            therm_name = therm_mdl.name
            
            s += fmt % (E, ZPE, H, rrho_G, qrrho_G, qharm_G, dZPE, dH, rrho_dG, qrrho_dG, qharm_dG, sp_name, therm_name)
        
        elif self.tab_widget.currentIndex() == 1:
            if self.settings.include_header:
                s = delim.join(["ΔE", "ΔZPE", "ΔH(RRHO)", "ΔG(RRHO)", "ΔG(Quasi-RRHO)", "ΔG(Quasi-Harmonic)"])
                s+= "\n"
            else:
                s = ""
            
            float_fmt = "%.1f" + delim
            fmt = 6 * float_fmt
            try:
                dE = float(self.relative_dE.text())
                dZPVE = float(self.relative_dZPVE.text())
                dH = float(self.relative_dH.text())
                dG = float(self.relative_dG.text())
                dQRRHOG = float(self.relative_dQRRHOG.text())
                dQHARMG = float(self.relative_dQHARMG.text())
                s += fmt % (dE, dZPVE, dH, dG, dQRRHOG, dQHARMG)
            except ValueError:
                pass
        
        return s
    
    def header_check(self, state):
        if state:
            self.settings.include_header = True
        else:
            self.settings.include_header = False
    
    def set_sp(self):
        """set energy entry for when sp model changes"""
        if self.sp_selector.currentIndex() >= 0:
            fr = self.sp_selector.currentData()

            self.check_geometry_rmsd("SP")

            self.sp_nrg_line.setText("%.6f" % fr.other['energy'])
        else:
            self.sp_nrg_line.setText("")

        self.update_sum()

    def set_thermo_mdl(self):
        if self.thermo_selector.currentIndex() >= 0:
            fr = self.thermo_selector.currentData()
            
            self.check_geometry_rmsd("THERM")

            if 'temperature' in fr.other:
                self.temperature_line.setValue(fr.other['temperature'])

        self.set_thermo()

    def check_geometry_rmsd(self, *args):
        if self.thermo_selector.currentIndex() >= 0 and self.sp_selector.currentIndex() >= 0:
            fr = self.sp_selector.currentData()
            fr2 = self.thermo_selector.currentData()

            if len(fr.atoms) != len(fr2.atoms):
                self.status.showMessage("structures are not the same: different number of atoms")
                return

            geom = Geometry(fr)
            geom2 = Geometry(fr2)
            rmsd = geom.RMSD(geom2)
            if not isclose(rmsd, 0, atol=10**-5):
                rmsd = geom.RMSD(geom2, sort=True)
            
            if not isclose(rmsd, 0, atol=10**-5):
                self.status.showMessage("structures might not be the same - RMSD = %.4f" % rmsd)
            else:
                self.status.showMessage("")

    def set_thermo(self):
        """sets thermo entries for when thermo model changes"""
        #index of combobox is -1 when combobox has no entries
        if self.thermo_selector.currentIndex() >= 0:
            fr = self.thermo_selector.currentData()
            if fr not in self.thermo_co:
                self.thermo_co[fr] = CompOutput(fr)
            co = self.thermo_co[fr]

            v0 = self.v0_edit.value()

            if v0 != self.settings.w0:
                self.settings.w0 = v0

            T = self.temperature_line.value()
            if not T:
                return

            dZPE = co.ZPVE
            #compute enthalpy and entropy at this temperature
            #AaronTools uses Grimme's Quasi-RRHO, but this is the same as RRHO when w0=0
            dE, dH, s = co.therm_corr(temperature=T, v0=0, method="RRHO")
            rrho_dg = dH - T * s
            #compute G with quasi entropy treatments
            qrrho_dg = co.calc_G_corr(v0=v0, temperature=T, method="QRRHO")
            qharm_dg = co.calc_G_corr(v0=v0, temperature=T, method="QHARM")
            
            self.zpe_line.setText("%.6f" % dZPE)
            self.enthalpy_line.setText("%.6f" % dH)
            self.rrho_g_line.setText("%.6f" % rrho_dg)
            self.qrrho_g_line.setText("%.6f" % qrrho_dg)
            self.qharm_g_line.setText("%.6f" % qharm_dg)
        else:
            self.zpe_line.setText("")
            self.enthalpy_line.setText("")
            self.rrho_g_line.setText("")
            self.qrrho_g_line.setText("")
            self.qharm_g_line.setText("")
        
        self.update_sum()

    def update_sum(self):
        """updates the sum of energy and thermo corrections"""
        dZPE = self.zpe_line.text()
        dH = self.enthalpy_line.text()
        dG = self.rrho_g_line.text()
        dG_qrrho = self.qrrho_g_line.text()
        dG_qharm = self.qharm_g_line.text()
        
        nrg = self.sp_nrg_line.text()
        
        if len(dH) == 0 or len(nrg) == 0:
            self.zpe_sum_line.setText("")
            self.h_sum_line.setText("")
            self.rrho_g_sum_line.setText("")
            self.qrrho_g_sum_line.setText("")
            self.qharm_g_sum_line.setText("")
            return
        else:
            dZPE = float(dZPE)
            dH = float(dH)
            dG = float(dG)
            dG_qrrho = float(dG_qrrho)
            dG_qharm = float(dG_qharm)
            
            nrg = float(nrg)
            
            zpe = nrg + dZPE
            enthalpy = nrg + dH
            rrho_g = nrg + dG
            qrrho_g = nrg + dG_qrrho
            qharm_g = nrg + dG_qharm
            
            self.zpe_sum_line.setText("%.6f" % zpe)
            self.h_sum_line.setText("%.6f" % enthalpy)
            self.rrho_g_sum_line.setText("%.6f" % rrho_g)
            self.qrrho_g_sum_line.setText("%.6f" % qrrho_g)
            self.qharm_g_sum_line.setText("%.6f" % qharm_g)
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")

    def delete(self):
        #overload because closing a tool window doesn't destroy any widgets on it
        self.settings.ref_col_1 = self.ref_group.tree.columnWidth(0)
        self.settings.ref_col_2 = self.ref_group.tree.columnWidth(1)
        self.settings.ref_col_3 = self.ref_group.tree.columnWidth(2)        
        
        self.settings.other_col_1 = self.other_group.tree.columnWidth(0)
        self.settings.other_col_2 = self.other_group.tree.columnWidth(1)
        self.settings.other_col_3 = self.other_group.tree.columnWidth(2)
        
        self.sp_selector.deleteLater()
        self.thermo_selector.deleteLater()
        self.ref_group.deleteLater()
        self.other_group.deleteLater()
        
        return super().delete()           


class ThermoGroup(QWidget):
    changes = pyqtSignal()
    
    def __init__(self, name, session, nrg_fr, thermo_co, size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.session = session
        self.nrg_fr = nrg_fr
        self.thermo_co = thermo_co
        
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setRowStretch(0, 1)
        
        frame = QGroupBox(name)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        frame_layout = QGridLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setRowStretch(0, 1)
        
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["energy", "frequencies", "remove"])
        self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tree.setColumnWidth(0, size[0])
        self.tree.setColumnWidth(1, size[1])
        self.tree.setColumnWidth(2, size[2])
        
        root_item = self.tree.invisibleRootItem()
        plus = QTreeWidgetItem(root_item)
        plus_button = QPushButton("add molecule group")
        plus_button.setFlat(True)
        plus_button.clicked.connect(self.add_mol_group)        
        plus_button2 = QPushButton("")
        plus_button2.setFlat(True)
        plus_button2.clicked.connect(self.add_mol_group)
        self.tree.setItemWidget(plus, 0, plus_button)
        self.tree.setItemWidget(plus, 1, plus_button2)
        self.tree.insertTopLevelItem(1, plus)
        
        self.add_mol_group()
        
        frame_layout.addWidget(self.tree)

        layout.addWidget(frame)
    
    def add_mol_group(self, *args):
        row = self.tree.topLevelItemCount()
        
        root_item = self.tree.invisibleRootItem()
        
        mol_group = QTreeWidgetItem(root_item)
        self.tree.insertTopLevelItem(row, mol_group)
        trash_button = QPushButton()
        trash_button.setFlat(True)
        
        trash_button.clicked.connect(lambda *args, parent=mol_group: self.remove_mol_group(parent))
        trash_button.setIcon(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)))
        
        add_conf_button = QPushButton("add conformer")
        add_conf_button.setFlat(True)
        add_conf_button.clicked.connect(lambda *args, conf_group_widget=mol_group: self.add_conf_group(conf_group_widget))
        
        add_conf_button2 = QPushButton("")
        add_conf_button2.setFlat(True)
        add_conf_button2.clicked.connect(lambda *args, conf_group_widget=mol_group: self.add_conf_group(conf_group_widget))
        
        add_conf_child = QTreeWidgetItem(mol_group)
        self.tree.setItemWidget(add_conf_child, 0, add_conf_button)
        self.tree.setItemWidget(add_conf_child, 1, add_conf_button2)
        self.tree.setItemWidget(mol_group, 2, trash_button)
        
        mol_group.setText(0, "group %i" % row)
        
        mol_group.addChild(add_conf_child)
        self.add_conf_group(mol_group)

        self.tree.expandItem(mol_group)

        self.changes.emit()

    def add_conf_group(self, conf_group_widget):
        row = conf_group_widget.childCount()
        
        conformer_item = QTreeWidgetItem(conf_group_widget)
        conf_group_widget.insertChild(row, conformer_item)
        
        nrg_combobox = FilereaderComboBox(self.session, otherItems=['energy'])
        nrg_combobox.currentIndexChanged.connect(lambda *args: self.changes.emit())
        freq_combobox = FilereaderComboBox(self.session, otherItems=['frequency'])
        freq_combobox.currentIndexChanged.connect(lambda *args: self.changes.emit())
        
        trash_button = QPushButton()
        trash_button.setFlat(True)
        trash_button.clicked.connect(lambda *args, combobox=nrg_combobox: combobox.deleteLater())
        trash_button.clicked.connect(lambda *args, combobox=freq_combobox: combobox.deleteLater())
        trash_button.clicked.connect(lambda *args, child=conformer_item: conf_group_widget.removeChild(child))
        trash_button.clicked.connect(lambda *args: self.changes.emit())
        trash_button.setIcon(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)))
        
        self.tree.setItemWidget(conformer_item, 0, nrg_combobox)
        self.tree.setItemWidget(conformer_item, 1, freq_combobox)
        self.tree.setItemWidget(conformer_item, 2, trash_button)
        
        self.changes.emit()

    def compOutputs(self):
        out = []
        for mol_index in range(1, self.tree.topLevelItemCount()):
            out.append([])
            mol = self.tree.topLevelItem(mol_index)
            for conf_ndx in range(1, mol.childCount()):
                conf = mol.child(conf_ndx)
                fr = self.tree.itemWidget(conf, 1).currentData()
                if fr is None:
                    continue
                
                if fr not in self.thermo_co:
                    self.thermo_co[fr] = CompOutput(fr)
                out[-1].append(self.thermo_co[fr])
        
        return out
    
    def energies(self):
        out = []
        for mol_index in range(1, self.tree.topLevelItemCount()):
            out.append([])
            mol = self.tree.topLevelItem(mol_index)
            for conf_ndx in range(1, mol.childCount()):
                conf = mol.child(conf_ndx)
                fr = self.tree.itemWidget(conf, 0).currentData()
                if fr is None:
                    continue

                out[-1].append(fr.other['energy'])
        
        return out
    
    def remove_mol_group(self, parent):
        for conf_ndx in range(1, parent.childCount()):
            conf = parent.child(conf_ndx)
            self.tree.itemWidget(conf, 0).destroy()
            self.tree.itemWidget(conf, 1).destroy()
        
        ndx = self.tree.indexOfTopLevelItem(parent)
        self.tree.takeTopLevelItem(ndx)
        
        self.changes.emit()

    def deleteLater(self):
        for mol_index in range(1, self.tree.topLevelItemCount()):
            mol = self.tree.topLevelItem(mol_index)
            for conf_ndx in range(1, mol.childCount()):
                conf = mol.child(conf_ndx)
                self.tree.itemWidget(conf, 0).deleteLater()
                self.tree.itemWidget(conf, 1).deleteLater()
        
        super().deleteLater()

