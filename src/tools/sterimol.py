import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.atomic import selected_atoms
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import BoolArg
from chimerax.core.settings import Settings
from chimerax.core.generic3d import Generic3DModel 

from Qt.QtCore import Qt
from Qt.QtGui import QKeySequence
from Qt.QtWidgets import (
    QPushButton,
    QFormLayout,
    QComboBox,
    QCheckBox,
    QMenuBar,
    QAction,
    QFileDialog,
    QApplication,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from SEQCROW.commands.sterimol import sterimol as sterimol_cmd

class _SterimolSettings(Settings):

    AUTO_SAVE = {
        "radii": "UMN",
        "display_radii": Value(True, BoolArg),
        "display_vectors": Value(True, BoolArg),
        "include_header": Value(True, BoolArg),
        "L_style": "FORTRAN",
        "delimiter": "comma",
    }

class Sterimol(ToolInstance):

    help = "https://github.com/QChASM/SEQCROW/wiki/Sterimol-Tool"
    SESSION_ENDURING = False
    SESSION_SAVE = False
    
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

        self.L_style = QComboBox()
        self.L_style.addItems(["FORTRAN", "AaronTools"])
        ndx = self.L_style.findText(self.settings.L_style, Qt.MatchExactly)
        self.L_style.setCurrentIndex(ndx)
        self.L_style.setToolTip(
            """FORTRAN: Add 0.4 + the ideal X-H bond length to the length
of the substituent
AaronTools: add VDW radius to the length of the substituent"""
        )
        layout.addRow("L correction:", self.L_style)

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
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                'model',
                'substituent atom',
                'B\u2081',
                'B\u2082',
                'B\u2083',
                'B\u2084',
                'B\u2085',
                'L',
            ]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.resizeColumnToContents(3)
        self.table.resizeColumnToContents(4)
        self.table.resizeColumnToContents(5)
        self.table.resizeColumnToContents(6)
        self.table.resizeColumnToContents(7)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)
        layout.addRow(self.table)

        menu = QMenuBar()
        
        export = menu.addMenu("&Export")

        clear = QAction("Clear data table", self.tool_window.ui_area)
        clear.triggered.connect(self.clear_table)
        export.addAction(clear)

        copy = QAction("&Copy CSV to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_csv)
        shortcut = QKeySequence(QKeySequence.Copy)
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
        menu.setVisible(True)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def clear_table(self):
        are_you_sure = QMessageBox.question(
            None,
            "Clear table?",
            "Are you sure you want to clear the data table?",
        )
        if are_you_sure != QMessageBox.Yes:
            return
        self.table.setRowCount(0)

    def calc_sterimol(self, *args):
        self.settings.radii = self.radii_option.currentText()
        self.settings.display_radii = self.display_radii.checkState() == Qt.Checked
        self.settings.display_vectors = self.display_vectors.checkState() == Qt.Checked
        self.settings.L_style = self.L_style.currentText()

        model_names, targets, datas = sterimol_cmd(
            self.session, 
            selected_atoms(self.session), 
            radii=self.radii_option.currentText(),
            showVectors=self.display_vectors.checkState() == Qt.Checked,
            showRadii=self.display_radii.checkState() == Qt.Checked,
            return_values=True,
            LCorrection=self.settings.L_style,
        )
        
        if len(model_names) == 0:
            return
        
        # self.table.setRowCount(0)
        
        for t, b, data in zip(model_names, targets, datas):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            targ = QTableWidgetItem()
            targ.setData(Qt.DisplayRole, t)
            self.table.setItem(row, 0, targ)

            neigh = QTableWidgetItem()
            neigh.setData(Qt.DisplayRole, b)
            self.table.setItem(row, 1, neigh)

            l = np.linalg.norm(data["L"][1] - data["L"][0])
            b1 = np.linalg.norm(data["B1"][1] - data["B1"][0])
            b2 = np.linalg.norm(data["B2"][1] - data["B2"][0])
            b3 = np.linalg.norm(data["B3"][1] - data["B3"][0])
            b4 = np.linalg.norm(data["B4"][1] - data["B4"][0])
            b5 = np.linalg.norm(data["B5"][1] - data["B5"][0])
            
            li = QTableWidgetItem()
            li.setData(Qt.DisplayRole, "%.2f" % l)
            self.table.setItem(row, 7, li)

            b1i = QTableWidgetItem()
            b1i.setData(Qt.DisplayRole, "%.2f" % b1)
            self.table.setItem(row, 2, b1i)

            b2i = QTableWidgetItem()
            b2i.setData(Qt.DisplayRole, "%.2f" % b2)
            self.table.setItem(row, 3, b2i)

            b3i = QTableWidgetItem()
            b3i.setData(Qt.DisplayRole, "%.2f" % b3)
            self.table.setItem(row, 4, b3i)

            b4i = QTableWidgetItem()
            b4i.setData(Qt.DisplayRole, "%.2f" % b4)
            self.table.setItem(row, 5, b4i)

            b5i = QTableWidgetItem()
            b5i.setData(Qt.DisplayRole, "%.2f" % b5)
            self.table.setItem(row, 6, b5i)
        
        for i in range(0, 7):
            if i == 1:
                continue
            self.table.resizeColumnToContents(i)
    
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
            s = delim.join(
                ["substituent_atom", "bonded_atom", "B1", "B2", "B3", "B4", "B5", "L"]
            )
            s += "\n"
        else:
            s = ""
        
        for i in range(0, self.table.rowCount()):
            s += delim.join(
                [
                    item.data(Qt.DisplayRole) for item in [
                        self.table.item(i, j) for j in range(0, 8)
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
    
    def del_sterimol(self):
        for model in self.session.models.list(type=Generic3DModel):
            if model.name.startswith("Sterimol"):
                model.delete()
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
