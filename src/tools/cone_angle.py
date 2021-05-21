from io import BytesIO

from chimerax.atomic import selected_atoms
from chimerax.bild.bild import read_bild
from chimerax.core.generic3d import Generic3DModel 
from chimerax.core.settings import Settings
from chimerax.core.tools import ToolInstance

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
)

from AaronTools.component import Component
from AaronTools.const import VDW_RADII, BONDI_RADII
from AaronTools.finders import BondedTo, NotAny

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec


class _ConeAngleSettings(Settings):
    AUTO_SAVE = {
        "cone_option": "Tolman (Unsymmetrical)",
        "radii": "UMN",
        "display_cone": True,
        "display_radii": True,
        "delimiter": "comma",
        "include_header": True,
    }


class ConeAngle(ToolInstance):
    
    help = "https://github.com/QChASM/SEQCROW/wiki/Cone-Angle-Tool"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        
        self.settings = _ConeAngleSettings(self.session, name)
        
        self.ligands = dict()
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QFormLayout()

        self.cone_option = QComboBox()
        self.cone_option.addItems(["Tolman (Unsymmetrical)", "Exact"])
        ndx = self.cone_option.findText(self.settings.cone_option, Qt.MatchExactly)
        self.cone_option.setCurrentIndex(ndx)
        layout.addRow("method:", self.cone_option)

        self.radii_option = QComboBox()
        self.radii_option.addItems(["Bondi", "UMN"])
        ndx = self.radii_option.findText(self.settings.radii, Qt.MatchExactly)
        self.radii_option.setCurrentIndex(ndx)
        layout.addRow("radii:", self.radii_option)

        self.display_cone = QCheckBox()
        self.display_cone.setChecked(self.settings.display_cone)
        layout.addRow("show cone:", self.display_cone)
        
        self.display_radii = QCheckBox()
        self.display_radii.setChecked(self.settings.display_radii)
        layout.addRow("show radii:", self.display_radii)

        set_ligand_button = QPushButton("set ligand to current selection")
        set_ligand_button.clicked.connect(self.set_ligand)
        layout.addRow(set_ligand_button)
        self.set_ligand_button = set_ligand_button

        calc_cone_button = QPushButton("calculate cone angle for ligand on selected center")
        calc_cone_button.clicked.connect(self.calc_cone)
        layout.addRow(calc_cone_button)
        self.calc_cone_button = calc_cone_button
        
        remove_cone_button = QPushButton("remove cone visualizations")
        remove_cone_button.clicked.connect(self.del_cone)
        layout.addRow(remove_cone_button)
        self.remove_cone_button = remove_cone_button
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            [
                'model',
                'center',
                'cone angle (°)',
            ]
        )
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
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
                ["model", "center_atom", "cone_angle"]
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
    
    def del_cone(self):
        for model in self.session.models.list(type=Generic3DModel):
            if model.name.startswith("Cone angle"):
                model.delete()

    def set_ligand(self, *args):
        self.ligands = {}
        for atom in selected_atoms(self.session):
            if atom.structure not in self.ligands:
                self.ligands[atom.structure] = []
            self.ligands[atom.structure].append(atom)
        self.session.logger.status("set ligand to current selection")

    def calc_cone(self, *args):
        self.settings.cone_option = self.cone_option.currentText()
        self.settings.radii = self.radii_option.currentText()
        self.settings.display_radii = self.display_radii.checkState() == Qt.Checked
        self.settings.display_cone = self.display_cone.checkState() == Qt.Checked
        
        if self.cone_option.currentText() == "Tolman (Unsymmetrical)":
            method = "tolman"
        else:
            method = self.cone_option.currentText()
        
        radii = self.radii_option.currentText()
        return_cones = self.display_cone.checkState() == Qt.Checked
        display_radii = self.display_radii.checkState() == Qt.Checked
        
        self.table.setRowCount(0)

        for center_atom in selected_atoms(self.session):
            rescol = ResidueCollection(center_atom.structure)
            at_center = rescol.find_exact(AtomSpec(center_atom.atomspec))[0]
            if center_atom.structure in self.ligands:
                comp = Component(
                    rescol.find(
                        [AtomSpec(atom.atomspec) for atom in self.ligands[center_atom.structure]]
                    ),
                    to_center=rescol.find_exact(AtomSpec(center_atom.atomspec)),
                    key_atoms=rescol.find(BondedTo(at_center)),
                )
            else:
                comp = Component(
                    rescol.find(NotAny(at_center)),
                    to_center=rescol.find_exact(AtomSpec(center_atom.atomspec)),
                    key_atoms=rescol.find(BondedTo(at_center)),
                )
            
            cone_angle = comp.cone_angle(
                center=rescol.find(AtomSpec(center_atom.atomspec)),
                method=method,
                radii=radii,
                return_cones=return_cones,
            )
            
            if return_cones:
                cone_angle, cones = cone_angle
                s = ".transparency 0.5\n"
                for cone in cones:
                    apex, base, radius = cone
                    s += ".cone   %6.3f %6.3f %6.3f   %6.3f %6.3f %6.3f   %.3f open\n" % (
                        *apex, *base, radius
                    )
                
                stream = BytesIO(bytes(s, "utf-8"))
                bild_obj, status = read_bild(
                    self.session,
                    stream,
                    "Cone angle %s" % center_atom
                )
                
                self.session.models.add(bild_obj, parent=center_atom.structure)
                    
                    
            if display_radii:
                s = ".note radii\n"
                s += ".transparency 75\n"
                color = None
                for atom in comp.atoms:
                    chix_atom = atom.chix_atom
                    if radii.lower() == "umn":
                        r = VDW_RADII[chix_atom.element.name]
                    elif radii.lower() == "bondi":
                        r = BONDI_RADII[chix_atom.element.name]
                    
                    if color is None or chix_atom.color != color:
                        color = chix_atom.color
                        rgb = [x/255. for x in chix_atom.color]
                        rgb.pop(-1)
                        
                        s += ".color %f %f %f\n" % tuple(rgb)
                    
                    s += ".sphere %f %f %f %f\n" % (*chix_atom.coord, r)
            
                stream = BytesIO(bytes(s, "utf-8"))
                bild_obj, status = read_bild(self.session, stream, "Cone angle radii")
                
                self.session.models.add(bild_obj, parent=center_atom.structure)
            
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            name = QTableWidgetItem()
            name.setData(Qt.DisplayRole, center_atom.structure.name)
            self.table.setItem(row, 0, name)

            center = QTableWidgetItem()
            center.setData(Qt.DisplayRole, center_atom.atomspec)
            self.table.setItem(row, 1, center)
            
            ca = QTableWidgetItem()
            ca.setData(Qt.DisplayRole, "%.2f" % cone_angle)
            self.table.setItem(row, 2, ca)
    
            self.table.resizeColumnToContents(0)
            self.table.resizeColumnToContents(1)
            self.table.resizeColumnToContents(2)
    