import os

from chimerax.core.tools import ToolInstance
from chimerax.atomic import selected_atoms
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import BoolArg
from chimerax.core.settings import Settings
from chimerax.core.generic3d import Generic3DModel 

from Qt.QtCore import Qt
from Qt.QtGui import QKeySequence, QClipboard
from Qt.QtWidgets import QPushButton, QFormLayout, QComboBox, QLineEdit, QLabel, QCheckBox, QMenuBar, QAction, \
                            QFileDialog, QApplication, QTableWidget, QTableWidgetItem, QHeaderView

from AaronTools.const import VDW_RADII, BONDI_RADII
from AaronTools.substituent import Substituent

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec
from SEQCROW.commands.sterimol import sterimol as sterimol_cmd

class _SterimolSettings(Settings):

    AUTO_SAVE = {
        "radii": "UMN",
        "display_radii": Value(True, BoolArg),
        "display_vectors": Value(True, BoolArg),
        "include_header": Value(True, BoolArg),
        "delimiter": "comma",
    }

class Sterimol(ToolInstance):

    help = "https://github.com/QChASM/SEQCROW/wiki/Sterimol-Tool"
    SESSION_ENDURING = True
    SESSION_SAVE = True
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        
        self.settings = _SterimolSettings(self.session, name)
        
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout()

        self.radii_option = QComboBox()
        self.radii_option.addItems(["Bondi", "UMN"])
        ndx = self.radii_option.findText(self.settings.radii, Qt.MatchExactly)
        self.radii_option.setCurrentIndex(ndx)
        layout.addRow("radii:", self.radii_option)
        
        self.display_vectors = QCheckBox()
        self.display_vectors.setChecked(self.settings.display_vectors)
        layout.addRow("show vectors:", self.display_vectors)
        
        self.display_radii = QCheckBox()
        self.display_radii.setChecked(self.settings.display_radii)
        layout.addRow("show radii:", self.display_radii)
        
        calc_sterimol_button = QPushButton("calculate parameters for selected substituents")
        calc_sterimol_button.clicked.connect(self.calc_sterimol)
        layout.addRow(calc_sterimol_button)
        self.calc_sterimol_button = calc_sterimol_button
        
        remove_sterimol_button = QPushButton("remove Sterimol visualizations")
        remove_sterimol_button.clicked.connect(self.del_sterimol)
        layout.addRow(remove_sterimol_button)
        self.remove_sterimol_button = remove_sterimol_button
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['substituent atom', 'bonded atom', 'L', 'B\u2081', 'B\u2085'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.resizeColumnToContents(3)
        self.table.resizeColumnToContents(4)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addRow(self.table)

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
        self._menu = menu
        layout.setMenuBar(menu)
        
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def calc_sterimol(self, *args):
        self.settings.radii = self.radii_option.currentText()
        self.settings.display_radii = self.display_radii.checkState() == Qt.Checked
        self.settings.display_vectors = self.display_vectors.checkState() == Qt.Checked

        targets, neighbors, ls, b1s, b5s = sterimol_cmd(self.session, 
                                                        selected_atoms(self.session), 
                                                        radii=self.radii_option.currentText(),
                                                        showVectors=self.display_vectors.checkState() == Qt.Checked,
                                                        showRadii=self.display_radii.checkState() == Qt.Checked,
                                                        return_values=True,
        )
        
        if len(targets) == 0:
            return
        
        self.table.setRowCount(0)
        
        for t, b, l, b1, b5 in zip(targets, neighbors, ls, b1s, b5s):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            targ = QTableWidgetItem()
            targ.setData(Qt.DisplayRole, t)
            self.table.setItem(row, 0, targ)

            neigh = QTableWidgetItem()
            neigh.setData(Qt.DisplayRole, b)
            self.table.setItem(row, 1, neigh)

            li = QTableWidgetItem()
            li.setData(Qt.DisplayRole, "%.2f" % l)
            self.table.setItem(row, 2, li)

            b1i = QTableWidgetItem()
            b1i.setData(Qt.DisplayRole, "%.2f" % b1)
            self.table.setItem(row, 3, b1i)

            b5i = QTableWidgetItem()
            b5i.setData(Qt.DisplayRole, "%.2f" % b5)
            self.table.setItem(row, 4, b5i)
    
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
            s = delim.join(["substituent_atom", "bonded_atom", "L", "B1", "B5"])
            s += "\n"
        else:
            s = ""
        
        for i in range(0, self.table.rowCount()):
            s += delim.join([item.data(Qt.DisplayRole) for item in [self.table.item(i, j) for j in range(0, 5)]])
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
    
    def del_sterimol(self):
        for model in self.session.models.list(type=Generic3DModel):
            if model.name == "Sterimol":
                model.delete()
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
