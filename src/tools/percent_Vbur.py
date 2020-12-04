import os

from chimerax.core.tools import ToolInstance
from chimerax.atomic import selected_atoms
from chimerax.core.configfile import Value
from chimerax.core.commands import BoolArg
from chimerax.core.settings import Settings
from chimerax.core.models import Surface

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QClipboard
from PyQt5.QtWidgets import QPushButton, QFormLayout, QComboBox, QLineEdit, QLabel, QCheckBox, \
                            QMenuBar, QAction, QFileDialog, QApplication, QTableWidget, \
                            QTableWidgetItem, QHeaderView, QDoubleSpinBox, QSpinBox, QWidget

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec
from SEQCROW.commands.percent_Vbur import percent_vbur as percent_vbur_cmd

class _VburSettings(Settings):

    AUTO_SAVE = {
        "radii": "UMN",
        "vdw_scale": 1.17,
        "center_radius": 3.5,
        "method": "Lebedev",
        "angular_points": "1454",
        "radial_points": "20",
        "minimum_iterations": 25,
        "use_centroid": Value(False, BoolArg), 
        "display_cutout": Value(False, BoolArg), 
        "include_header": Value(True, BoolArg),
        "delimiter": "comma",
    }

class PercentVolumeBuried(ToolInstance):

    help = "https://github.com/QChASM/SEQCROW/wiki/Buried-Volume-Tool"
    SESSION_ENDURING = True
    SESSION_SAVE = True
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        
        self.settings = _VburSettings(self.session, name)
        
        self.ligand_atoms = []
        
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout()

        self.radii_option = QComboBox()
        self.radii_option.addItems(["Bondi", "UMN"])
        ndx = self.radii_option.findText(self.settings.radii, Qt.MatchExactly)
        self.radii_option.setCurrentIndex(ndx)
        layout.addRow("radii:", self.radii_option)
       
        self.scale = QDoubleSpinBox()
        self.scale.setValue(self.settings.vdw_scale)
        self.scale.setSingleStep(0.01)
        self.scale.setRange(1., 1.5)
        layout.addRow("VDW scale:", self.scale)
        
        self.radius = QDoubleSpinBox()
        self.radius.setValue(self.settings.center_radius)
        self.radius.setSuffix(" \u212B")
        self.radius.setDecimals(1)
        self.radius.setSingleStep(0.1)
        self.radius.setRange(1., 5.)
        layout.addRow("radius around center:", self.radius)
        
        self.method = QComboBox()
        self.method.addItems(["Lebedev", "Monte-Carlo"])
        self.method.setToolTip("Lebedev: systematic method, gives reproducable results\n" +
                               "Monte-Carlo: non-deterministic method"
        )
        ndx = self.method.findText(self.settings.method, Qt.MatchExactly)
        self.method.setCurrentIndex(ndx)
        layout.addRow("integration method:", self.method)
        
        leb_widget = QWidget()
        leb_layout = QFormLayout(leb_widget)
        leb_layout.setContentsMargins(0, 0, 0, 0)
        
        self.radial_points = QComboBox()
        self.radial_points.addItems(["20", "32", "64", "75", "99", "127"])
        self.radial_points.setToolTip("more radial points will give more accurate results, but integration will take longer")
        ndx = self.radial_points.findText(self.settings.radial_points, Qt.MatchExactly)
        self.radial_points.setCurrentIndex(ndx)
        leb_layout.addRow("radial points:", self.radial_points)
        
        self.angular_points = QComboBox()
        self.angular_points.addItems(["110", "194", "302", "590", "974", "1454", "2030", "2702", "5810"])
        self.angular_points.setToolTip("more angular points will give more accurate results, but integration will take longer")
        ndx = self.angular_points.findText(self.settings.angular_points, Qt.MatchExactly)
        self.angular_points.setCurrentIndex(ndx)
        leb_layout.addRow("angular points:", self.angular_points)
        
        layout.addRow(leb_widget)
        
        mc_widget = QWidget()
        mc_layout = QFormLayout(mc_widget)
        mc_layout.setContentsMargins(0, 0, 0, 0)
        
        self.min_iter = QSpinBox()
        self.min_iter.setValue(self.settings.minimum_iterations)
        self.min_iter.setToolTip("each iteration is 3000 points\n" +
                                 "iterations continue until convergence criteria are met"
        )
        mc_layout.addRow("minimum interations:", self.min_iter)
        
        layout.addRow(mc_widget)
        
        if self.settings.method == "Lebedev":
            mc_widget.setVisible(False)
        elif self.settings.method == "Monte-Carlo":
            leb_widget.setVisible(False)
        
        self.method.currentTextChanged.connect(lambda text, widget=leb_widget: widget.setVisible(text == "Lebedev"))
        self.method.currentTextChanged.connect(lambda text, widget=mc_widget: widget.setVisible(text == "Monte-Carlo"))
        
        set_ligand_atoms = QPushButton("set ligands to current selection")
        set_ligand_atoms.clicked.connect(self.set_ligand_atoms)
        layout.addRow(set_ligand_atoms)
        
        self.use_centroid = QCheckBox()
        self.use_centroid.setChecked(self.settings.use_centroid)
        layout.addRow("use centroid of centers:", self.use_centroid)
        
        self.display_cutout = QCheckBox()
        self.display_cutout.setChecked(self.settings.display_cutout)
        layout.addRow("display cutout:", self.display_cutout)
        
        calc_vbur_button = QPushButton("calculate % buried volume for selected centers")
        calc_vbur_button.clicked.connect(self.calc_vbur)
        layout.addRow(calc_vbur_button)
        
        remove_vbur_button = QPushButton("remove % buried volume visualizations")
        remove_vbur_button.clicked.connect(self.del_vbur)
        layout.addRow(remove_vbur_button)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['model', 'center', '%Vbur'])
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
        layout.setMenuBar(menu)
        
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def set_ligand_atoms(self):
        self.ligand_atoms = selected_atoms(self.session)

    def calc_vbur(self):
        args = dict()
        
        cur_sel = selected_atoms(self.session)
        if len(cur_sel) == 0:
            return
        
        models = []
        for atom in cur_sel:
            if atom.structure not in models:
                models.append(atom.structure)
        
        center = []
        for atom in cur_sel:
            center.append(atom)
        
        args["center"] = center
        
        radii = self.radii_option.currentText()
        self.settings.radii = radii
        args["radii"] = radii
        
        scale = self.scale.value()
        self.settings.vdw_scale = scale
        args["scale"] = scale

        radius = self.radius.value()
        self.settings.center_radius = radius
        args["radius"] = radius
        
        use_centroid = self.use_centroid.checkState() == Qt.Checked
        self.settings.use_centroid = use_centroid
        args["useCentroid"] = use_centroid
        
        method = self.method.currentText()
        self.settings.method = method
        args["method"] = method
        
        if method == "Lebedev":
            rad_pts = self.radial_points.currentText()
            self.settings.radial_points = rad_pts
            args["radialPoints"] = rad_pts
            
            ang_pts = self.angular_points.currentText()
            self.settings.angular_points = ang_pts
            args["angularPoints"] = ang_pts
        
        elif method == "Monte-Carlo":
            min_iter = self.min_iter.value()
            self.settings.minimum_iterations = min_iter
            args["minimumIterations"] = min_iter
        
        display_cutout = self.display_cutout.checkState() == Qt.Checked
        self.settings.display_cutout = display_cutout
        args["displaySphere"] = display_cutout

        if len(self.ligand_atoms) > 0:
            args["onlyAtoms"] = [a for a in self.ligand_atoms if not a.deleted]
            if len(args["onlyAtoms"]) == 0:
                args["onlyAtoms"] = None

        info = percent_vbur_cmd(
            self.session,
            models,
            return_values=True, 
            **args
        )
        
        self.table.setRowCount(0)
        
        for mdl, cent, vbur in info:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            m = QTableWidgetItem()
            m.setData(Qt.DisplayRole, mdl)
            self.table.setItem(row, 0, m)
            
            c = QTableWidgetItem()
            c.setData(Qt.DisplayRole, cent)
            self.table.setItem(row, 1, c)
            
            v = QTableWidgetItem()
            v.setData(Qt.DisplayRole, "%.1f" % vbur)
            self.table.setItem(row, 2, v)
        
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
    
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
            s = delim.join(["model", "center", "%Vbur"])
            s += "\n"
        else:
            s = ""
        
        for i in range(0, self.table.rowCount()):
            s += delim.join([item.data(Qt.DisplayRole) for item in [self.table.item(i, j) for j in range(0, 3)]])
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
    
    def del_vbur(self):
        for model in self.session.models.list(type=Surface):
            if model.name.startswith("%Vbur"):
                model.delete()
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
