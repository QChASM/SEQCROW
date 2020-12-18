from SEQCROW.widgets import FilereaderComboBox

from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence, QClipboard
from PySide2.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, \
                            QTabWidget, QHeaderView, QSizePolicy, QMenuBar, QAction, \
                            QFileDialog, QApplication

from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.settings import Settings

from AaronTools.theory import Theory
from AaronTools.const import UNIT, PHYSICAL


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
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Data', 'Value'])
        self.table.horizontalHeader().setStretchLastSection(False)            
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        layout.insertWidget(1, self.table, 1)
        
        
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
        
        # comma = QAction("comma", self.tool_window.ui_area, checkable=True)
        # comma.setChecked(self.settings.delimiter == "comma")
        # comma.triggered.connect(lambda *args, delim="comma": self.settings.__setattr__("delimiter", delim))
        # delimiter.addAction(comma)
        
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
            
        if self.settings.include_header:
            s = delim.join(["Data", "Value"])
            s += "\n"
        else:
            s = ""
        
        for i in range(0, self.table.rowCount()):
            s += delim.join([item.data(Qt.DisplayRole) for item in [self.table.item(i, j) for j in range(0, 2)]])
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
        
        if ndx < 0:
            return
        
        fr = self.file_selector.currentData()
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
                    info_name += " (%s)" % self.settings.energy
                    if self.settings.energy == "kcal/mol":
                        val *= UNIT.HART_TO_KCAL
                    elif self.settings.energy == "kJ/mol":
                        val *= 4.184 * UNIT.HART_TO_KCAL

                    val = "%.9f" % val

                item.setData(Qt.DisplayRole, info_name)
                self.table.setItem(row, 0, item)
                
                value = QTableWidgetItem()
                val = str(val)
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
                    
            elif hasattr(fr.other[info], "__iter__") and all(isinstance(x, float) for x in fr.other[info]):
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                item = QTableWidgetItem()
                info_name = info.replace("_", " ")
                vals = fr.other[info]
                if info == "rotational_temperature":
                    info_name = "rotational constants (%s)" % self.settings.rot_const
                    if self.settings.rot_const == "GHz":
                        vals = [x * PHYSICAL.KB / (PHYSICAL.PLANCK * (10 ** 9)) for x in vals]
                
                item.setData(Qt.DisplayRole, info_name)
                self.table.setItem(row, 0, item)
                
                value = QTableWidgetItem()
                value.setData(Qt.DisplayRole, ", ".join(["%.4f" % x for x in vals]))
                self.table.setItem(row, 1, value)
        
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
    
    def delete(self):
        self.file_selector.deleteLater()

        return super().delete()    
    
    def close(self):
        self.file_selector.deleteLater()

        return super().close()