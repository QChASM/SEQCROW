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
    QAction,
    QFileDialog,
    QApplication,
    QLineEdit,
    QLabel,
    QWidget,
    QPushButton,
)

from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow
from chimerax.core.settings import Settings

from AaronTools.theory import Theory
from AaronTools.const import UNIT, PHYSICAL
from AaronTools.spectra import Signal

from SEQCROW.presets import indexLabel
from SEQCROW.tools.normal_modes import FreqTableWidgetItem
from SEQCROW.widgets import FakeMenu, copy_icon

import numpy as np


nrg_infos = (
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
    "Dimer Basis Electrostatics",
    "Dimer Basis Elst10,r",
    "Dimer Basis Exchange",
    "Dimer Basis Exch10",
    "Dimer Basis Exch10(S^2)",
    "Dimer Basis Induction",
    "Dimer Basis Ind20,r",
    "Dimer Basis Exch-Ind20,r",
    "Dimer Basis delta HF,r (2)",
    "Dimer Basis Dispersion",
    "Dimer Basis Disp20",
    "Dimer Basis Exch-Disp20",
    "Dimer Basis Disp20 (SS)",
    "Dimer Basis Disp20 (OS)",
    "Dimer Basis Exch-Disp20 (SS)",
    "Dimer Basis Exch-Disp20 (OS)",
    "Dimer Basis Total HF",
    "Dimer Basis Total SAPT0",
    "Dimer Basis Electrostatics sSAPT0",
    "Dimer Basis Exchange sSAPT0",
    "Dimer Basis Induction sSAPT0",
    "Dimer Basis Dispersion sSAPT0",
    "Monomer Basis Total sSAPT0",
    "Monomer Basis Electrostatics",
    "Monomer Basis Elst10,r",
    "Monomer Basis Exchange",
    "Monomer Basis Exch10",
    "Monomer Basis Exch10(S^2)",
    "Monomer Basis Induction",
    "Monomer Basis Ind20,r",
    "Monomer Basis Exch-Ind20,r",
    "Monomer Basis delta HF,r (2)",
    "Monomer Basis Dispersion",
    "Monomer Basis Disp20",
    "Monomer Basis Exch-Disp20",
    "Monomer Basis Disp20 (SS)",
    "Monomer Basis Disp20 (OS)",
    "Monomer Basis Exch-Disp20 (SS)",
    "Monomer Basis Exch-Disp20 (OS)",
    "Monomer Basis Total HF",
    "Monomer Basis Total SAPT0",
    "Monomer Basis Electrostatics sSAPT0",
    "Monomer Basis Exchange sSAPT0",
    "Monomer Basis Induction sSAPT0",
    "Monomer Basis Dispersion sSAPT0",
    "Monomer Basis Total sSAPT0",
    "Dimer Basis SAPT Ind20,r (A<-B)",
    "Dimer Basis SAPT Ind20,r (B<-A)",
    "Dimer Basis SAPT Exch-Ind20,r (A<-B)",
    "Dimer Basis SAPT Exch-Ind20,r (B<-A)",
    "Monomer Basis SAPT Ind20,r (A<-B)",
    "Monomer Basis SAPT Ind20,r (B<-A)",
    "Monomer Basis SAPT Exch-Ind20,r (A<-B)",
    "Monomer Basis SAPT Exch-Ind20,r (B<-A)",
    "Alpha Orbital Energies",
    "Beta Orbital Energies",
)
    
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
        self.signal_tables = []
        
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
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Data', 'Value', ""])
        self.table.horizontalHeader().setStretchLastSection(False)            
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        general_layout.insertWidget(0, self.table, 1)

        self.filter = QLineEdit()
        self.filter.setPlaceholderText("filter data")
        self.filter.textChanged.connect(self.apply_filter)
        self.filter.setClearButtonEnabled(True)
        general_layout.insertWidget(1, self.filter, 0)

        menu = FakeMenu()

        export = menu.addMenu("Export")
        copy = QAction("Copy CSV to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_csv)
        shortcut = QKeySequence(QKeySequence.Copy)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        self.copy = copy

        save = QAction("Save CSV...", self.tool_window.ui_area)
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

        add_header = QAction("Include CSV header", self.tool_window.ui_area, checkable=True)
        add_header.setChecked(self.settings.include_header)
        add_header.triggered.connect(self.header_check)
        export.addAction(add_header)

        comma.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        comma.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        tab.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        tab.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        semicolon.triggered.connect(lambda *args, action=comma: action.setChecked(False))
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

        self._menu = menu
        layout.setMenuBar(menu)

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
                        item.text().replace("<sub>", "").replace("</sub>", "").replace("&larr;", "<-") for item in [
                            self.table.item(i, j) if self.table.item(i, j) is not None 
                            else self.table.cellWidget(i, j) for j in range(0, 2)
                        ]
                    ]
                )
                s += "\n"
        
        else:
            table = self.signal_tables[self.tabs.currentIndex() - 1]
            if self.settings.include_header:
                if self.tabs.currentIndex() == 2:
                    s = delim
                else:
                    s = ""
                s += delim.join([
                    table.horizontalHeaderItem(i).text().replace(delim, "_") for i in range(0, table.columnCount())
                ])
                s += "\n"
            else:
                s = ""
            
            for i in range(0, table.rowCount()):
                if self.settings.include_header:
                    if table.verticalHeaderItem(i) is None and self.tabs.currentIndex() == 2:
                        s += delim
                    elif table.verticalHeaderItem(i) is not None:
                        s += table.verticalHeaderItem(i).text().replace(delim, "_")
                    if self.tabs.currentIndex() == 2:
                        s += delim
                s += delim.join(
                    [
                        item.replace("<sub>", "").replace("</sub>", "") for item in [
                            table.item(i, j).text() if table.item(i, j) is not None 
                            else table.cellWidget(i, j).text() if table.cellWidget(i, j) is not None
                            else ""
                            for j in range(0, table.columnCount()) 
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
        current_tab = self.tabs.currentIndex()
        self.table.setRowCount(0)
        self.signal_tables = []
        
        while self.tabs.count() > 1:
            self.tabs.removeTab(1)
        
        if ndx < 0:
            return
        
        fr = self.file_selector.currentData()
        if fr is None:
            return
        fr, model = fr
        item = QTableWidgetItem()
        item.setData(Qt.DisplayRole, "name")
        val = QTableWidgetItem()
        val.setData(Qt.DisplayRole, fr["name"])
        self.table.insertRow(0)
        self.table.setItem(0, 0, item)
        self.table.setItem(0, 1, val)
        self.add_copy_button(0)
        for info in fr.keys():
            if info == "archive" and not self.settings.archive:
                continue

            if info == "name":
                continue

            if any(isinstance(fr[info], obj) for obj in [str, float, int]):
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                item = QTableWidgetItem()
                info_name = info.replace("_", " ")
                val = fr[info]
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
                    if "<-" in info_name:
                        info_name = info_name.replace("<-", "&larr;")
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

                self.add_copy_button(row)

            elif isinstance(fr[info], Theory):
                theory = fr[info]
                if theory.method is not None:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    
                    item = QTableWidgetItem()
                    item.setData(Qt.DisplayRole, "method")
                    self.table.setItem(row, 0, item)
                    
                    value = QTableWidgetItem()
                    value.setData(Qt.DisplayRole, theory.method.name)
                    self.table.setItem(row, 1, value)
                    self.add_copy_button(row)
                    
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
                            self.add_copy_button(row)
                        
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
                            self.add_copy_button(row)

            elif (
                hasattr(fr[info], "__iter__") and
                all(isinstance(x, float) for x in fr[info]) and
                len(fr[info]) > 1
            ):
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                item = QTableWidgetItem()
                info_name = info.replace("_", " ")
                vals = fr[info]
                if "rotational_temperature" in info:
                    info_name = info_name.replace("temperature", "constants (%s)" % self.settings.rot_const)
                    if self.settings.rot_const == "GHz":
                        vals = [x * PHYSICAL.KB / (PHYSICAL.PLANCK * (10 ** 9)) for x in vals]
                
                item.setData(Qt.DisplayRole, info_name)
                self.table.setItem(row, 0, item)
                
                value = QTableWidgetItem()
                value.setData(Qt.DisplayRole, ", ".join(["%.4f" % x for x in vals]))
                self.table.setItem(row, 1, value)
                
                self.add_copy_button(row)

        # show spectra data
        for signal_data in ["frequency", "uv_vis", "nmr"]:
            if signal_data not in fr.keys():
                continue
            for data_type in fr[signal_data].__dict__.keys():
                data = getattr(fr[signal_data], data_type)
                if not data:
                    continue
                if not isinstance(data, list):
                    continue
                if not all(isinstance(x, Signal) for x in data):
                    continue
                nested_tables = []
                nested_data = [None]
                if data[0].nested:
                    nested_data.extend(data[0].nested)

                labels = [attr for attr in dir(data[-1]) if getattr(data[-1], attr) is not None]
                labels.remove(data[0].x_attr)
                for nest in nested_data:
                    try:
                        labels.remove(nest)
                    except ValueError:
                        pass
                normal_labels = [self.header_map(data[0].x_attr)]
                for name in sorted(labels):
                    if name == "x_attr":
                        labels.remove(name)
                        continue
                    if name == "required_attrs":
                        labels.remove(name)
                        continue
                    if name == "nested":
                        labels.remove(name)
                        continue
                    if name.startswith("__"):
                        labels.remove(name)
                        continue
                    value = getattr(data[0], name)
                    if isinstance(value, np.ndarray):
                        labels.remove(name)
                        continue
                    if isinstance(value, Signal):
                        labels.remove(name)
                        continue
                    normal_label = self.header_map(name)
                    if not normal_label:
                        labels.remove(name)
                        continue
                    normal_labels.append(normal_label)

                for i, nest in enumerate(nested_data):
                    table = QTableWidget()
                    table.setColumnCount(len(labels) + 1)
                    table.setEditTriggers(QTableWidget.NoEditTriggers)
                    table.setHorizontalHeaderLabels(normal_labels)
                    table.doubleClicked.connect(
                        lambda ndx, t=table, s=self: s.copy_table_item(t, ndx)
                    )
                    self.signal_tables.append(table)
                    for group in data:
                        signals = [group]
                        if nest:
                            signals = getattr(group, nest)
                            if isinstance(signals, dict):
                                all_signals = []
                                for signal in signals.values():
                                    all_signals.extend(signal)
                                signals = all_signals
                        for signal in signals:
                            row = table.rowCount()
                            table.insertRow(row)
                            decimals = 4
                            if signal_data == "frequency" or signal_data == "anharm_data":
                                decimals = 2
                            elif signal_data == "uv_vis":
                                decimals = 3
                            fmt = "%%.%if" % decimals
                            item = QTableWidgetItem()
                            item.setData(Qt.DisplayRole, fmt % getattr(signal, signal.x_attr))
                            table.setItem(row, 0, item)
                            columns = 0
                            for info in sorted(labels):
                                value = getattr(signal, info)
                                if isinstance(value, float):
                                    text = "%.4f" % value
                                elif isinstance(value, int):
                                    text = "%i" % value
                                elif isinstance(value, str):
                                    text = value
                                elif isinstance(value, Signal):
                                    text = fmt % getattr(value, value.x_attr)
                                else:
                                    text = repr(value)
                                item = QTableWidgetItem()
                                item.setData(Qt.DisplayRole, text)
                                table.setItem(row, columns + 1, item)
                                columns += 1
                                if info == "ndx":
                                    if "atomspec" not in normal_labels:
                                        normal_labels.insert(columns + 1, "atomspec")
                                        normal_labels.insert(columns + 1, "atom name")
                                        table.setColumnCount(len(normal_labels))
                                        table.setHorizontalHeaderLabels(normal_labels)
                                    item = QTableWidgetItem()
                                    item.setData(Qt.DisplayRole, model.atoms[value].name)
                                    table.setItem(row, columns + 1, item)
                                    columns += 1
                                    item = QTableWidgetItem()
                                    item.setData(Qt.DisplayRole, model.atoms[value].atomspec)
                                    table.setItem(row, columns + 1, item)
                                    columns += 1

                    for j in range(0, table.columnCount()):
                        table.resizeColumnToContents(j)
                    if not nest:
                        nest = data_type
                    label = self.signal_name_map(signal_data, nest)
                    self.tabs.addTab(table, label)

            if "nmr" in fr.keys():
                widget = QWidget()
                coupling_layout = QVBoxLayout(widget)
                button = QPushButton("label atoms with indices")
                button.clicked.connect(lambda *args, mdl=model: indexLabel(self.session, models=mdl))
                coupling_layout.addWidget(button, 0)
                nmr = fr["nmr"]
                table = QTableWidget()
                table.setColumnCount(len(nmr.data))
                table.setEditTriggers(QTableWidget.NoEditTriggers)
                table.setHorizontalHeaderLabels([str(shift.ndx + 1) for shift in nmr.data])
                table.doubleClicked.connect(
                    lambda ndx, t=table, s=self: s.copy_table_item(t, ndx)
                )
                self.signal_tables.append(table)
                for i, shift in enumerate(nmr.data):
                    table.insertRow(table.rowCount())
                    for j, shift2 in enumerate(nmr.data[:i]):
                        try:
                            coupling = nmr.coupling[shift.ndx][shift2.ndx]
                        except KeyError:
                            continue
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, "%.2f" % coupling)
                        table.setItem(i, j, item)
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, "%.2f" % coupling)
                        table.setItem(j, i, item)
                for j in range(0, table.columnCount()):
                    table.resizeColumnToContents(j)
                table.setVerticalHeaderLabels([str(shift.ndx + 1) for shift in nmr.data])
                coupling_layout.addWidget(table, 1)
                self.tabs.addTab(widget, "NMR coupling")

        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)

        if current_tab < self.tabs.count():
            self.tabs.setCurrentIndex(current_tab)

        self.apply_filter()
    
    def copy_table_item(self, table, item_coord):
        try:
            item = table.item(item_coord.row(), item_coord.column())
            text = item.text()
            app = QApplication.instance()
            clipboard = app.clipboard()
            clipboard.setText(text)
            self.session.logger.status("copied %s to clipboard" % text)
        except Exception as e:
            print(e)
    
    def signal_name_map(self, signal_type, data_type):
        """returns a normal name for the data type"""
        if signal_type == "frequency":
            if data_type == "data":
                return "harmonic frequencies"
            if data_type == "anharm_data":
                return "anharmonic fundamentals"
        if signal_type == "uv_vis":
            if data_type == "data":
                return "excitations"
            if data_type == "transient_data":
                return "transient excitations"
            if data_type == "spin_orbit_data":
                return "SOC excitations"
        if signal_type == "nmr":
            return "NMR shifts"
        return data_type
    
    def header_map(self, attribute_type):
        """returns a normal name for data_type"""
        translation = {
            "frequency": "frequency (cm\u207b\u00b9)",
            "raman_activity": "Raman activity",
            "rotation": "rotatory strength",
            "forcek": "force constant (mDyne/\u212B)",
            "red_mass": "reduced mass",
            "harmonic_frequency": "harmonic frequency cm\u207b\u00b9",
            "delta_anh": "Δ\u2090\u2099\u2095 cm\u207b\u00b9", # I know this looks stupid, but for some reason you can't put <sub> in a header
            "excitation_energy": "excitation energy (eV)",
            "rotatory_str_len": "rot. str. (from len.)",
            "rotatory_str_vel": "rot. str. (from vel.)",
            "oscillator_str": "oscillator str. (from len.)",
            "oscillator_str_vel": "oscillator str. (from vel.)",
            "multiplicity": "spin state",
        }
        banned = set([
            "dipole_str_len",
            "dipole_str_vel",
            "delta_abs_len",
            "delta_abs_vel",
        ])
        if attribute_type in banned:
            return False
        
        try:
            return translation[attribute_type]
        except KeyError:
            return attribute_type
    
    def copy_item(self, row_ndx):
        item = self.table.item(row_ndx, 1)
        if item is None:
            item = self.table.cellWidget(row_ndx, 1)
        text = item.text().replace("<sub>", "").replace("</sub>", "")
        app = QApplication.instance()
        clipboard = app.clipboard()
        clipboard.setText(text)
        self.session.logger.status("copied to clipboard")

    def add_copy_button(self, row):
        copy = QPushButton(self.table)
        copy.setIcon(copy_icon)
        copy.setMinimumWidth(int(1.6*copy.fontMetrics().boundingRect("Qy").width()))
        # copy.setMaximumWidth(int(1.6*copy.fontMetrics().boundingRect("Qy").width()))
        copy.setMinimumHeight(int(1.6*copy.fontMetrics().boundingRect("Qy").height()))
        # copy.setMaximumHeight(int(1.6*copy.fontMetrics().boundingRect("Qy").height()))
        copy.setFlat(True)
        copy.setToolTip("copy this value to your clipboard")
        copy.clicked.connect(
            lambda *args, row_ndx=row: self.copy_item(row_ndx)
        )
        self.table.setCellWidget(row, 2, copy)

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