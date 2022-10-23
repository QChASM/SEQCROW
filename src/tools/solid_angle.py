from chimerax.atomic import selected_atoms, Atoms
from chimerax.core.models import Surface
from chimerax.core.settings import Settings
from chimerax.core.tools import ToolInstance

import numpy as np

from Qt.QtCore import Qt
from Qt.QtGui import QKeySequence
from Qt.QtWidgets import (
    QPushButton,
    QFormLayout,
    QComboBox,
    QCheckBox,
    QAction,
    QFileDialog,
    QApplication,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QLabel,
    QTabWidget,
    QWidget,
    QDoubleSpinBox,
)

from SEQCROW.commands.solid_angle import solid_angle
from SEQCROW.widgets import FakeMenu


class _SolidAngleSettings(Settings):
    AUTO_SAVE = {
        "radii": "UMN",
        "display": True,
        "delimiter": "comma",
        "include_header": True,
    }


class SolidAngle(ToolInstance):

    help = "https://github.com/QChASM/SEQCROW/wiki/Ligand-Solid-Angle-Tool"

    def __init__(self, session, name):       
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        
        self.settings = _SolidAngleSettings(self.session, name)
        
        self.ligands = dict()
        
        self._build_ui()
    
    def _build_ui(self):
        tabs = QTabWidget()
        
        layout = QFormLayout()
        layout.addRow(tabs)
        
        solid_widget = QWidget()
        solid_layout = QFormLayout(solid_widget)

        solid_layout.addRow("1.", QLabel("select ligand"))

        set_ligand_button = QPushButton("set ligand to current selection")
        set_ligand_button.clicked.connect(self.set_ligand)
        solid_layout.addRow("2.", set_ligand_button)
        self.set_ligand_button = set_ligand_button

        solid_layout.addRow("3.", QLabel("change selection to metal center"))

        calc_solid_button = QPushButton("calculate solid angle")
        calc_solid_button.clicked.connect(self.calc_solid)
        solid_layout.addRow("4.", calc_solid_button)
        self.calc_solid_button = calc_solid_button

        tabs.addTab(solid_widget, "solid angle")

        settings = QWidget()
        settings_layout = QFormLayout(settings)

        self.radii_option = QComboBox()
        self.radii_option.addItems(["Bondi", "UMN"])
        ndx = self.radii_option.findText(self.settings.radii, Qt.MatchExactly)
        self.radii_option.setCurrentIndex(ndx)
        settings_layout.addRow("radii:", self.radii_option)

        self.radius_option = QDoubleSpinBox()
        self.radius_option.setMinimum(0)
        self.radius_option.setMaximum(30)
        self.radius_option.setSingleStep(0.5)
        self.radius_option.setToolTip(
            "sphere radius to project VDW radii onto\n"
            "use 0 to encompass the entire ligand"
        )
        settings_layout.addRow("projection radius:", self.radius_option)

        self.display_solid = QCheckBox()
        self.display_solid.setChecked(self.settings.display)
        settings_layout.addRow("show shadow:", self.display_solid)

        remove_shadow_button = QPushButton("remove solid angle visualizations")
        remove_shadow_button.clicked.connect(self.del_solid)
        settings_layout.addRow(remove_shadow_button)
        self.remove_shadow_button = remove_shadow_button
        
        tabs.addTab(settings, "options")

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            [
                'model',
                'center',
                'solid angle (sr)',
            ]
        )
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        solid_layout.addRow(self.table)


        menu = FakeMenu()
        
        export = menu.addMenu("Export")

        clear = QAction("Clear data table", self.tool_window.ui_area)
        clear.triggered.connect(self.clear_table)
        export.addAction(clear)

        copy = QAction("Copy CSV to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_csv)
        shortcut = QKeySequence(QKeySequence.Copy)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        
        save = QAction("Save CSV...", self.tool_window.ui_area)
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
        
        add_header = QAction("Include CSV header", self.tool_window.ui_area, checkable=True)
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

        self._menu = menu
        layout.setMenuBar(menu)
        
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
                ["model", "center_atom", "solid_angle"]
            )
            s += "\n"
        else:
            s = ""
        
        for i in range(0, self.table.rowCount()):
            s += delim.join(
                [
                    item.data(Qt.DisplayRole) for item in [
                        self.table.item(i, j) for j in range(0, 3)
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
    
    def del_solid(self):
        for model in self.session.models.list(type=Surface):
            if model.name.startswith("Solid angle"):
                model.delete()

    def set_ligand(self, *args):
        self.ligand_atoms = Atoms(selected_atoms(self.session))
        self.session.logger.status("set ligand to current selection")

    def calc_solid(self, *args):
        self.settings.radii = self.radii_option.currentText()
        self.settings.display = self.display_solid.checkState() == Qt.Checked

        if not selected_atoms(self.session):
            self.session.logger.error("no atoms selected")
            return

        info = solid_angle(
            self.session,
            self.ligand_atoms,
            center=selected_atoms(self.session),
            radii=self.settings.radii,
            display=self.settings.display,
            radius=self.radius_option.value(),
        )
            
            
        for item in info:
            model, cent, angle = item
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            name = QTableWidgetItem()
            name.setData(Qt.DisplayRole, model.name)
            self.table.setItem(row, 0, name)

            center = QTableWidgetItem()
            if isinstance(cent, np.ndarray):
                center.setData(Qt.DisplayRole, str(cent))
            elif not hasattr(cent, "__iter__"):
                center.setData(Qt.DisplayRole, cent.atomspec)
            else:
                center.setData(
                    Qt.DisplayRole,
                    self.settings.delimiter.join([c.atomspec for c in cent])
                )
            self.table.setItem(row, 1, center)
            
            ca = QTableWidgetItem()
            ca.setData(Qt.DisplayRole, "%.3f" % angle)
            self.table.setItem(row, 2, ca)
    
            self.table.resizeColumnToContents(2)
            self.table.resizeColumnToContents(1)
            self.table.resizeColumnToContents(0)
    