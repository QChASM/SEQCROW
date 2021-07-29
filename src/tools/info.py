import re

from SEQCROW.widgets import FilereaderComboBox

from Qt.QtCore import Qt, QRegularExpression
from Qt.QtGui import QKeySequence
from Qt.QtWidgets import (
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QHeaderView,
    QSizePolicy,
    QMenuBar,
    QAction,
    QFileDialog,
    QApplication,
    QLineEdit,
    QLabel,
    QWidget,
)

from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow
from chimerax.core.settings import Settings

from AaronTools.theory import Theory
from AaronTools.const import UNIT, PHYSICAL

from SEQCROW.tools.normal_modes import FreqTableWidgetItem


nrg_infos = [
    "energy", 
    "ZPVE", 
    "enthalpy", 
    "free_energy", 
    "E_ZPVE",
    "Electrostatics",
    "Elst10,r",
    "Exchange",
    "Exch10",
    "Exch10(S^2)",
    "Induction",
    "Ind20,r",
    "Exch-Ind20,r",
    "delta HF,r (2)",
    "Dispersion",
    "Disp20",
    "Exch-Disp20",
    "Disp20 (SS)",
    "Disp20 (OS)",
    "Exch-Disp20 (SS)",
    "Exch-Disp20 (OS)",
    "Total HF",
    "Total SAPT0",
    "Electrostatics sSAPT0",
    "Exchange sSAPT0",
    "Induction sSAPT0",
    "Dispersion sSAPT0",
    "Total sSAPT0",
    "Alpha Orbital Energies",
    "Beta Orbital Energies",
]
    
pg_infos = [
    "full_point_group",
    "abelian_subgroup",
    "concise_abelian_subgroup",
    "full_point_group",
    "molecular_point_group",
]


class _InfoSettings(Settings):
    AUTO_SAVE = {
        "include_header": True,
        "delimiter": "tab",
        "energy": "Hartree",
        "mass": "kg",
        "rot_const": "K",
        "archive": False,
    }
   
   
class Info(ToolInstance):
    
    help = "https://github.com/QChASM/SEQCROW/wiki/File-Info-Tool"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)
        
        self.settings = _InfoSettings(self.session, name)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout()
        
        self.file_selector = FilereaderComboBox(self.session)
        self.file_selector.currentIndexChanged.connect(self.fill_table)
        layout.insertWidget(0, self.file_selector, 0)
        
        tabs = QTabWidget()
        self.tabs = tabs
        layout.insertWidget(1, self.tabs, 1)
        
        general_info = QWidget()
        general_layout = QVBoxLayout(general_info)
        tabs.addTab(general_info, "general")
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Data', 'Value'])
        self.table.horizontalHeader().setStretchLastSection(False)            
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        general_layout.insertWidget(1, self.table, 1)
        
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("filter data")
        self.filter.textChanged.connect(self.apply_filter)
        self.filter.setClearButtonEnabled(True)
        general_layout.insertWidget(2, self.filter, 0)
        
        freq_info = QWidget()
        freq_layout = QVBoxLayout(freq_info)
        tabs.addTab(freq_info, "harmonic frequencies")
        
        self.freq_table = QTableWidget()
        self.freq_table.setColumnCount(4)
        self.freq_table.setHorizontalHeaderLabels(
            [
                "Frequency (cm\u207b\u00b9)",
                "symmetry",
                "IR intensity",
                "force constant (mDyne/\u212B)",
            ]
        )
        self.freq_table.setSortingEnabled(True)
        self.freq_table.setEditTriggers(QTableWidget.NoEditTriggers)
        for i in range(0, 4):
            self.freq_table.resizeColumnToContents(i)
        
        self.freq_table.horizontalHeader().setStretchLastSection(False)            
        self.freq_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.freq_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)        
        self.freq_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)        
        self.freq_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)        
        
        self.freq_table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        freq_layout.insertWidget(1, self.freq_table, 1)        

        anharm_info = QWidget()
        anharm_layout = QVBoxLayout(anharm_info)
        tabs.addTab(anharm_info, "anharmonic frequencies")
        
        anharm_layout.insertWidget(0, QLabel("fundamentals:"), 0)
        
        self.fundamental_table = QTableWidget()
        self.fundamental_table.setColumnCount(3)
        self.fundamental_table.setHorizontalHeaderLabels(
            [
                "Fundamental (cm\u207b\u00b9)",
                "Δ\u2090\u2099\u2095 (cm\u207b\u00b9)",
                "IR intensity",
            ]
        )
        self.fundamental_table.setSortingEnabled(True)
        self.fundamental_table.setEditTriggers(QTableWidget.NoEditTriggers)
        for i in range(0, 3):
            self.fundamental_table.resizeColumnToContents(i)
        
        self.fundamental_table.horizontalHeader().setStretchLastSection(False)            
        self.fundamental_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.fundamental_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)        
        self.fundamental_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)        
        
        self.fundamental_table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        anharm_layout.insertWidget(1, self.fundamental_table, 1)

        # self.overtone_table = QTableWidget()
        # self.overtone_table.setColumnCount(3)
        # self.overtone_table.setHorizontalHeaderLabels(
        #     [
        #         "Fundamental (cm\u207b\u00b9)",
        #         "Overtone (cm\u207b\u00b9)",
        #         "IR intensity",
        #     ]
        # )
        # self.overtone_table.setSortingEnabled(True)
        # self.overtone_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # for i in range(0, 3):
        #     self.overtone_table.resizeColumnToContents(i)
        # 
        # self.overtone_table.horizontalHeader().setStretchLastSection(False)            
        # self.overtone_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        # self.overtone_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)        
        # self.overtone_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)        
        # 
        # self.overtone_table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # anharm_layout.insertWidget(2, self.overtone_table, 1)
        
        anharm_layout.insertWidget(2, QLabel("combinations and overtones:"), 0)

        self.combo_table = QTableWidget()
        self.combo_table.setColumnCount(4)
        self.combo_table.setHorizontalHeaderLabels(
            [
                "Fundamental (cm\u207b\u00b9)",
                "Fundamental (cm\u207b\u00b9)",
                "Combination (cm\u207b\u00b9)",
                "IR intensity",
            ]
        )
        self.combo_table.setSortingEnabled(True)
        self.combo_table.setEditTriggers(QTableWidget.NoEditTriggers)
        for i in range(0, 3):
            self.combo_table.resizeColumnToContents(i)
        
        self.combo_table.horizontalHeader().setStretchLastSection(False)            
        self.combo_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.combo_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)        
        self.combo_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)        
        self.combo_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)        
        
        self.combo_table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        anharm_layout.insertWidget(3, self.combo_table, 1)
        
        menu = QMenuBar()
        
        export = menu.addMenu("&Export")
        copy = QAction("&Copy CSV to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_csv)
        shortcut = QKeySequence(Qt.CTRL + Qt.Key_C)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        self.copy = copy
        
        save = QAction("&Save CSV...", self.tool_window.ui_area)
        save.triggered.connect(self.save_csv)
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
        
        # space = QAction("space", self.tool_window.ui_area, checkable=True)
        # space.setChecked(self.settings.delimiter == "space")
        # space.triggered.connect(lambda *args, delim="space": self.settings.__setattr__("delimiter", delim))
        # delimiter.addAction(space)
        
        semicolon = QAction("semicolon", self.tool_window.ui_area, checkable=True)
        semicolon.setChecked(self.settings.delimiter == "semicolon")
        semicolon.triggered.connect(lambda *args, delim="semicolon": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(semicolon)
        
        add_header = QAction("&Include CSV header", self.tool_window.ui_area, checkable=True)
        add_header.setChecked(self.settings.include_header)
        add_header.triggered.connect(self.header_check)
        export.addAction(add_header)

        tab.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        semicolon.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        
        archive = QAction("Include archive if present", self.tool_window.ui_area, checkable=True)
        archive.triggered.connect(lambda checked: setattr(self.settings, "archive", checked))
        archive.triggered.connect(lambda *args: self.fill_table(self.file_selector.count() - 1))
        archive.setChecked(self.settings.archive)
        export.addAction(archive)
        
        unit = menu.addMenu("&Units")
        
        energy = unit.addMenu("energy")
        hartree = QAction("Hartree", self.tool_window.ui_area, checkable=True)
        hartree.setChecked(self.settings.energy == "Hartree")
        kcal = QAction("kcal/mol", self.tool_window.ui_area, checkable=True)
        kcal.setChecked(self.settings.energy == "kcal/mol")
        kjoule = QAction("kJ/mol", self.tool_window.ui_area, checkable=True)
        kjoule.setChecked(self.settings.energy == "kJ/mol")
        energy.addAction(hartree)
        energy.addAction(kcal)
        energy.addAction(kjoule)

        hartree.triggered.connect(lambda *args, val="Hartree": setattr(self.settings, "energy", val))
        hartree.triggered.connect(lambda *args: self.fill_table(self.file_selector.count() - 1))
        hartree.triggered.connect(lambda *args, action=kcal: action.setChecked(False))
        hartree.triggered.connect(lambda *args, action=kjoule: action.setChecked(False))
        
        kcal.triggered.connect(lambda *args, val="kcal/mol": setattr(self.settings, "energy", val))
        kcal.triggered.connect(lambda *args: self.fill_table(self.file_selector.count() - 1))
        kcal.triggered.connect(lambda *args, action=hartree: action.setChecked(False))
        kcal.triggered.connect(lambda *args, action=kjoule: action.setChecked(False))
        
        kjoule.triggered.connect(lambda *args, val="kJ/mol": setattr(self.settings, "energy", val))
        kjoule.triggered.connect(lambda *args: self.fill_table(self.file_selector.count() - 1))
        kjoule.triggered.connect(lambda *args, action=hartree: action.setChecked(False))
        kjoule.triggered.connect(lambda *args, action=kcal: action.setChecked(False))

        mass = unit.addMenu("mass")
        kg = QAction("kg", self.tool_window.ui_area, checkable=True)
        kg.setChecked(self.settings.mass == "kg")
        amu = QAction("Da", self.tool_window.ui_area, checkable=True)
        amu.setChecked(self.settings.mass == "Da")
        mass.addAction(kg)
        mass.addAction(amu)

        kg.triggered.connect(lambda *args, val="kg": setattr(self.settings, "mass", val))
        kg.triggered.connect(lambda *args: self.fill_table(self.file_selector.count() - 1))
        kg.triggered.connect(lambda *args, action=amu: action.setChecked(False))

        amu.triggered.connect(lambda *args, val="Da": setattr(self.settings, "mass", val))
        amu.triggered.connect(lambda *args: self.fill_table(self.file_selector.count() - 1))
        amu.triggered.connect(lambda *args, action=kg: action.setChecked(False))

        rot_const = unit.addMenu("rotational constants")
        temperature = QAction("K", self.tool_window.ui_area, checkable=True)
        temperature.setChecked(self.settings.rot_const == "K")
        hertz = QAction("GHz", self.tool_window.ui_area, checkable=True)
        hertz.setChecked(self.settings.rot_const == "GHz")
        rot_const.addAction(temperature)
        rot_const.addAction(hertz)

        temperature.triggered.connect(lambda *args, val="K": setattr(self.settings, "rot_const", val))
        temperature.triggered.connect(lambda *args: self.fill_table(self.file_selector.count() - 1))
        temperature.triggered.connect(lambda *args, action=hertz: action.setChecked(False))

        hertz.triggered.connect(lambda *args, val="GHz": setattr(self.settings, "rot_const", val))
        hertz.triggered.connect(lambda *args: self.fill_table(self.file_selector.count() - 1))
        hertz.triggered.connect(lambda *args, action=temperature: action.setChecked(False))

        menu.setNativeMenuBar(False)
        self._menu = menu
        layout.setMenuBar(menu)


        if len(self.session.filereader_manager.list()) > 0:
            self.fill_table(0)
        
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
    
    def header_check(self, state):
        """user has [un]checked the 'include header' option on the menu"""
        if state:
            self.settings.include_header = True
        else:
            self.settings.include_header = False

    def get_csv(self):
        if self.settings.delimiter == "comma":
            delim = ","
        elif self.settings.delimiter == "space":
            delim = " "
        elif self.settings.delimiter == "tab":
            delim = "\t"
        elif self.settings.delimiter == "semicolon":
            delim = ";"

        if self.tabs.currentIndex() == 0:
            if self.settings.include_header:
                s = delim.join(["Data", "Value"])
                s += "\n"
            else:
                s = ""
            
            for i in range(0, self.table.rowCount()):
                if self.table.isRowHidden(i):
                    continue
                s += delim.join(
                    [
                        item.text().replace("<sub>", "").replace("</sub>", "") for item in [
                            self.table.item(i, j) if self.table.item(i, j) is not None 
                            else self.table.cellWidget(i, j) for j in range(0, 2)
                        ]
                    ]
                )
                s += "\n"
        
        elif self.tabs.currentIndex() == 1:
            if self.settings.include_header:
                s = delim.join(
                    ["Frequency (cm\u207b\u00b9)", "symmetry", "IR intensity", "force constant"]
                )
                s += "\n"
            else:
                s = ""
            
            for i in range(0, self.freq_table.rowCount()):
                if self.freq_table.isRowHidden(i):
                    continue
                s += delim.join(
                    [
                        item.text().replace("<sub>", "").replace("</sub>", "") for item in [
                            self.freq_table.item(i, j) if self.freq_table.item(i, j) is not None 
                            else self.freq_table.cellWidget(i, j) for j in range(0, 4)
                        ]
                    ]
                )
                s += "\n"
        
        else:
            if self.settings.include_header:
                s = delim.join(
                    ["Fundamental (cm\u207b\u00b9)", "Δanh", "IR intensity"]
                )
                s += "\n"
            else:
                s = ""
            
            for i in range(0, self.fundamental_table.rowCount()):
                if self.fundamental_table.isRowHidden(i):
                    continue
                s += delim.join(
                    [
                        item.text().replace("<sub>", "").replace("</sub>", "") for item in [
                            self.fundamental_table.item(i, j) if self.fundamental_table.item(i, j) is not None 
                            else self.fundamental_table.cellWidget(i, j) for j in range(0, 3)
                        ]
                    ]
                )
                s += "\n"
            
            if self.settings.include_header:
                s += delim.join(
                    [
                        "Fundamental (cm\u207b\u00b9)",
                        "Fundamental (cm\u207b\u00b9)",
                        "Combination (cm\u207b\u00b9)",
                        "IR intensity"
                    ]
                )
                s += "\n"
            else:
                s += "\n"
            
            for i in range(0, self.combo_table.rowCount()):
                if self.combo_table.isRowHidden(i):
                    continue
                s += delim.join(
                    [
                        item.text().replace("<sub>", "").replace("</sub>", "") for item in [
                            self.combo_table.item(i, j) if self.combo_table.item(i, j) is not None 
                            else self.combo_table.cellWidget(i, j) for j in range(0, 4)
                        ]
                    ]
                )
                s += "\n"

        return s
    
    def copy_csv(self):
        app = QApplication.instance()
        clipboard = app.clipboard()
        csv = self.get_csv()
        clipboard.setText(csv)
        self.session.logger.status("copied to clipboard")

    def save_csv(self):
        """save data on current tab to CSV file"""
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
        if filename:
            s = self.get_csv()
   
            with open(filename, 'w') as f:
                f.write(s.strip())
                
            self.session.logger.status("saved to %s" % filename)
    
    def fill_table(self, ndx):
        self.table.setRowCount(0)
        self.freq_table.setRowCount(0)
        self.fundamental_table.setRowCount(0)
        # self.overtone_table.setRowCount(0)
        self.combo_table.setRowCount(0)
        
        if ndx < 0:
            self.fundamental_table.setVisible(False)
            self.combo_table.setVisible(False)
            return
        
        fr = self.file_selector.currentData()
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, "name")
        val = QTableWidgetItem()
        val.setData(Qt.DisplayRole, fr.name)
        self.table.insertRow(0)
        self.table.setItem(0, 0, item)
        self.table.setItem(0, 1, val)
        for info in fr.other.keys():
            if info == "archive" and not self.settings.archive:
                continue

            if any(isinstance(fr.other[info], obj) for obj in [str, float, int]):
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                item = QTableWidgetItem()
                info_name = info.replace("_", " ")
                val = fr.other[info]
                if info == "mass":
                    info_name += " (%s)" % self.settings.mass
                    if self.settings.mass == "Da":
                        val /= UNIT.AMU_TO_KG
                
                elif info == "temperature":
                    info_name += " (K)"
                
                elif (
                        any(info == s for s in nrg_infos) or
                        info.lower().endswith("energy") or
                        info.startswith("E(")
                ):
                    if self.settings.energy == "Hartree":
                        info_name += " (E<sub>h</sub>)"
                    else:
                        info_name += " (%s)" % self.settings.energy
                    info_name = info_name.replace("orrelation", "orr.")
                    info_name = info_name.replace("Same-spin", "SS")
                    info_name = info_name.replace("Opposite-spin", "OS")
                    if self.settings.energy == "kcal/mol":
                        val *= UNIT.HART_TO_KCAL
                    elif self.settings.energy == "kJ/mol":
                        val *= 4.184 * UNIT.HART_TO_KCAL

                    val = "%.6f" % val

                elif info.startswith("optical rotation"):
                    info_name += " (°)"

                elif any(info == x for x in pg_infos):
                    info_name = info.replace("_", " ")
                    if re.search("\d", val):
                        val = re.sub(r"(\d+)", r"<sub>\1</sub>", val)
                    # gaussian uses * for infinity
                    val = val.replace("*", "<sub>∞</sub>")
                    # psi4 uses _inf_
                    val = val.replace("_inf_", "<sub>∞</sub>")
                    if any(val.endswith(char) for char in "vhdsiVHDSI"):
                        val = val[:-1] + "<sub>" + val[-1].lower() + "</sub>"

                if "<sub>" in info_name:
                    self.table.setCellWidget(row, 0, QLabel(info_name))
                else:
                    item = QTableWidgetItem()
                    item.setData(Qt.DisplayRole, info_name)
                    self.table.setItem(row, 0, item)
                
                value = QTableWidgetItem()
                val = str(val)
                if "<sub>" in val:
                    self.table.setCellWidget(row, 1, QLabel(val))
                else:
                    value.setData(Qt.DisplayRole, val)
                    self.table.setItem(row, 1, value)

            elif isinstance(fr.other[info], Theory):
                theory = fr.other[info]
                if theory.method is not None:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    
                    item = QTableWidgetItem()
                    item.setData(Qt.DisplayRole, "method")
                    self.table.setItem(row, 0, item)
                    
                    value = QTableWidgetItem()
                    value.setData(Qt.DisplayRole, theory.method.name)
                    self.table.setItem(row, 1, value)
                
                if theory.basis is not None:
                    if theory.basis.basis:
                        for basis in theory.basis.basis:
                            row = self.table.rowCount()
                            self.table.insertRow(row)
                            
                            item = QTableWidgetItem()
                            if not basis.elements:
                                item.setData(Qt.DisplayRole, "basis set")
                            else:
                                item.setData(Qt.DisplayRole, "basis for %s" % ", ".join(basis.elements))
                            self.table.setItem(row, 0, item)
                            
                            value = QTableWidgetItem()
                            value.setData(Qt.DisplayRole, basis.name)
                            self.table.setItem(row, 1, value)

                    if theory.basis.ecp:
                        for ecp in theory.basis.ecp:
                            row = self.table.rowCount()
                            self.table.insertRow(row)
                            
                            item = QTableWidgetItem()
                            if ecp.elements is None:
                                item.setData(Qt.DisplayRole, "ECP")
                            else:
                                item.setData(Qt.DisplayRole, "ECP %s" % " ".join(ecp.elements))
                            self.table.setItem(row, 0, item)
                            
                            value = QTableWidgetItem()
                            value.setData(Qt.DisplayRole, ecp.name)
                            self.table.setItem(row, 1, value)

            elif (
                hasattr(fr.other[info], "__iter__") and
                all(isinstance(x, float) for x in fr.other[info]) and
                len(fr.other[info]) > 1
            ):
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                item = QTableWidgetItem()
                info_name = info.replace("_", " ")
                vals = fr.other[info]
                if "rotational_temperature" in info:
                    info_name = info_name.replace("temperature", "constants (%s)" % self.settings.rot_const)
                    if self.settings.rot_const == "GHz":
                        vals = [x * PHYSICAL.KB / (PHYSICAL.PLANCK * (10 ** 9)) for x in vals]
                
                item.setData(Qt.DisplayRole, info_name)
                self.table.setItem(row, 0, item)
                
                value = QTableWidgetItem()
                value.setData(Qt.DisplayRole, ", ".join(["%.4f" % x for x in vals]))
                self.table.setItem(row, 1, value)


        if "frequency" in fr.other:
            self.tabs.setTabEnabled(1, True)
            freq_data = fr.other['frequency'].data
            
            for i, mode in enumerate(freq_data):
                row = self.freq_table.rowCount()
                self.freq_table.insertRow(row)
                
                freq = FreqTableWidgetItem()
                freq.setData(
                    Qt.DisplayRole,
                    "%.2f%s" % (abs(mode.frequency), "i" if mode.frequency < 0 else "")
                )
                freq.setData(Qt.UserRole, i)
                self.freq_table.setItem(row, 0, freq)
                
                if mode.symmetry:
                    text = mode.symmetry
                    if re.search("\d", text):
                        text = re.sub(r"(\d+)", r"<sub>\1</sub>", text)
                    if text.startswith("SG"):
                        text = "Σ" + text[2:]
                    elif text.startswith("PI"):
                        text = "Π" + text[2:]
                    elif text.startswith("DLT"):
                        text = "Δ" + text[3:]
                    if any(text.endswith(char) for char in "vhdugVHDUG"):
                        text = text[:-1] + "<sub>" + text[-1].lower() + "</sub>"
    
                    label = QLabel(text)
                    label.setAlignment(Qt.AlignCenter)
                    self.freq_table.setCellWidget(row, 1, label)
    
                intensity = QTableWidgetItem()
                if mode.intensity is not None:
                    intensity.setData(Qt.DisplayRole, round(mode.intensity, 2))
                self.freq_table.setItem(row, 2, intensity)
    
                forcek = QTableWidgetItem()
                if mode.forcek is not None:
                    forcek.setData(Qt.DisplayRole, round(mode.forcek, 2))
                self.freq_table.setItem(row, 3, forcek)

            if fr.other["frequency"].anharm_data:
                self.fundamental_table.setVisible(True)
                self.combo_table.setVisible(True)
                
                freq = fr.other["frequency"]
                self.tabs.setTabEnabled(2, True)
                anharm_data = sorted(
                    freq.anharm_data,
                    key=lambda x: x.harmonic_frequency,
                )
                
                for i, mode in enumerate(anharm_data):
                    row = self.fundamental_table.rowCount()
                    self.fundamental_table.insertRow(row)
                    
                    fund = FreqTableWidgetItem()
                    fund.setData(
                        Qt.DisplayRole,
                        "%.2f%s" % (abs(mode.frequency), "i" if mode.frequency < 0 else "")
                    )
                    fund.setData(Qt.UserRole, i)
                    self.fundamental_table.setItem(row, 0, fund)
                
                    delta_anh = QTableWidgetItem()
                    delta_anh.setData(Qt.DisplayRole, round(mode.delta_anh, 2))
                    self.fundamental_table.setItem(row, 1, delta_anh)
                
                    intensity = QTableWidgetItem()
                    if mode.intensity is not None:
                        intensity.setData(Qt.DisplayRole, round(mode.intensity, 2))
                    self.fundamental_table.setItem(row, 2, intensity)
                    
                    for overtone in mode.overtones:
                        row = self.combo_table.rowCount()
                        self.combo_table.insertRow(row)
                        
                        fund = FreqTableWidgetItem()
                        fund.setData(
                            Qt.DisplayRole,
                            "%.2f%s" % (abs(mode.frequency), "i" if mode.frequency < 0 else "")
                        )
                        fund.setData(Qt.UserRole, i)
                        self.combo_table.setItem(row, 0, fund)

                        fund = FreqTableWidgetItem()
                        fund.setData(Qt.UserRole, i)
                        self.combo_table.setItem(row, 1, fund)

                        ot = FreqTableWidgetItem()
                        ot.setData(
                            Qt.DisplayRole,
                            "%.2f%s" % (abs(overtone.frequency), "i" if overtone.frequency < 0 else "")
                        )
                        ot.setData(Qt.UserRole, i)
                        self.combo_table.setItem(row, 2, ot)
 
                        intensity = QTableWidgetItem()
                        if overtone.intensity is not None:
                            intensity.setData(Qt.DisplayRole, round(overtone.intensity, 2))
                        self.combo_table.setItem(row, 3, intensity)

                    for key in mode.combinations:
                        for combination in mode.combinations[key]:
                            row = self.combo_table.rowCount()
                            self.combo_table.insertRow(row)
                            
                            fund = FreqTableWidgetItem()
                            fund.setData(
                                Qt.DisplayRole,
                                "%.2f%s" % (abs(mode.frequency), "i" if mode.frequency < 0 else "")
                            )
                            fund.setData(Qt.UserRole, i)
                            self.combo_table.setItem(row, 0, fund)

                            other_freq = freq.anharm_data[key].frequency
                            fund = FreqTableWidgetItem()
                            fund.setData(
                                Qt.DisplayRole,
                                "%.2f%s" % (abs(other_freq), "i" if other_freq < 0 else "")
                            )
                            fund.setData(Qt.UserRole, i + len(freq.anharm_data) * key)
                            self.combo_table.setItem(row, 1, fund)
                            
                
                            combo = FreqTableWidgetItem()
                            combo.setData(
                                Qt.DisplayRole,
                                "%.2f%s" % (abs(combination.frequency), "i" if combination.frequency < 0 else "")
                            )
                            combo.setData(Qt.UserRole, i)
                            self.combo_table.setItem(row, 2, combo)
                        
                            intensity = QTableWidgetItem()
                            if combination.intensity is not None:
                                intensity.setData(Qt.DisplayRole, round(combination.intensity, 2))
                            self.combo_table.setItem(row, 3, intensity)

            else:
                self.fundamental_table.setVisible(False)
                self.combo_table.setVisible(False)                
                self.tabs.setTabEnabled(2, False)

        else:
            self.fundamental_table.setVisible(False)
            self.combo_table.setVisible(False)
            
            self.tabs.setTabEnabled(1, False)
            self.tabs.setTabEnabled(2, False)

        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)

        self.freq_table.resizeColumnToContents(0)
        self.freq_table.resizeColumnToContents(1)
        self.freq_table.resizeColumnToContents(2)
        
        self.apply_filter()
    
    def apply_filter(self, text=None):
        if text is None:
            text = self.filter.text()

        if text:
            text = text.replace("(", "\(")
            text = text.replace(")", "\)")
            m = QRegularExpression(text)
            m.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
            if m.isValid():
                m.optimize()
                filter = lambda row_num: m.match(
                    self.table.item(row_num, 0).text() if self.table.item(row_num, 0) is not None
                    else self.table.cellWidget(row_num, 0).text().replace("<sub>", "").replace("</sub>", "")
                ).hasMatch()
            else:
                return

        else:
            filter = lambda row: True
            
        for i in range(0, self.table.rowCount()):
            self.table.setRowHidden(i, not filter(i))
    
    def delete(self):
        self.file_selector.deleteLater()

        return super().delete()    
    
    def close(self):
        self.file_selector.deleteLater()

        return super().close()