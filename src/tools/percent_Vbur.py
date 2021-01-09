import os

from chimerax.core.tools import ToolInstance
from chimerax.atomic import selected_atoms
from chimerax.core.configfile import Value
from chimerax.core.commands import BoolArg
from chimerax.core.settings import Settings
from chimerax.core.models import Surface
from chimerax.ui.gui import MainToolWindow, ChildToolWindow

from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence, QClipboard
from PySide2.QtWidgets import QPushButton, QFormLayout, QComboBox, QCheckBox, QMenuBar, QAction, \
                            QFileDialog, QApplication, QTableWidget, QTableWidgetItem, \
                            QHeaderView, QSpinBox, QWidget, QGridLayout, \
                            QTabWidget, QGroupBox, QDoubleSpinBox

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec
from SEQCROW.commands.percent_Vbur import percent_vbur as percent_vbur_cmd
from SEQCROW.tools.per_frame_plot import NavigationToolbar

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib.pyplot as plt

import copy

import numpy as np

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
        "display_cutout": "no", 
        "point_spacing": 0.075,
        "intersection_scale": 2.0, 
        "include_header": Value(True, BoolArg),
        "delimiter": "comma",
        "steric_map": False,
        "num_pts": 100,
        "include_vbur": True,
        "map_shape": "circle", 
        "auto_minmax": True,
        "map_max": 3.5,
        "map_min": -3.5,
    }

class PercentVolumeBuried(ToolInstance):

    help = "https://github.com/QChASM/SEQCROW/wiki/Buried-Volume-Tool"
    SESSION_ENDURING = True
    SESSION_SAVE = True
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)
        
        self.settings = _VburSettings(self.session, name)
        
        self.ligand_atoms = []
        
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()

        tabs = QTabWidget()
        calc_widget = QWidget()
        calc_layout = QFormLayout(calc_widget)
        vis_widget = QWidget()
        vis_layout = QFormLayout(vis_widget)
        layout.addWidget(tabs)
        
        tabs.addTab(calc_widget, "calculation")
        tabs.addTab(vis_widget, "visualization")

        self.radii_option = QComboBox()
        self.radii_option.addItems(["Bondi", "UMN"])
        ndx = self.radii_option.findText(self.settings.radii, Qt.MatchExactly)
        self.radii_option.setCurrentIndex(ndx)
        calc_layout.addRow("radii:", self.radii_option)
       
        self.scale = QDoubleSpinBox()
        self.scale.setValue(self.settings.vdw_scale)
        self.scale.setSingleStep(0.01)
        self.scale.setRange(1., 1.5)
        calc_layout.addRow("VDW scale:", self.scale)
        
        set_ligand_atoms = QPushButton("set ligands to current selection")
        set_ligand_atoms.clicked.connect(self.set_ligand_atoms)
        set_ligand_atoms.setToolTip(
            "specify atoms to use in calculation\n" +
            "by default, all atoms will be used unless a single center is specified\n" +
            "in the case of a single center, all atoms except the center is used"
        )
        calc_layout.addRow(set_ligand_atoms)
        self.set_ligand_atoms = set_ligand_atoms
        
        self.radius = QDoubleSpinBox()
        self.radius.setValue(self.settings.center_radius)
        self.radius.setSuffix(" \u212B")
        self.radius.setDecimals(1)
        self.radius.setSingleStep(0.1)
        self.radius.setRange(1., 15.)
        calc_layout.addRow("radius around center:", self.radius)
        
        self.method = QComboBox()
        self.method.addItems(["Lebedev", "Monte-Carlo"])
        self.method.setToolTip("Lebedev: deterministic method\n" +
                               "Monte-Carlo: non-deterministic method"
        )
        ndx = self.method.findText(self.settings.method, Qt.MatchExactly)
        self.method.setCurrentIndex(ndx)
        calc_layout.addRow("integration method:", self.method)
        
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

        calc_layout.addRow(leb_widget)
        
        mc_widget = QWidget()
        mc_layout = QFormLayout(mc_widget)
        mc_layout.setContentsMargins(0, 0, 0, 0)
        
        self.min_iter = QSpinBox()
        self.min_iter.setValue(self.settings.minimum_iterations)
        self.min_iter.setRange(0, 10000)
        self.min_iter.setToolTip("each iteration is 3000 points\n" +
                                 "iterations continue until convergence criteria are met"
        )
        mc_layout.addRow("minimum interations:", self.min_iter)
        
        calc_layout.addRow(mc_widget)
        
        if self.settings.method == "Lebedev":
            mc_widget.setVisible(False)
        elif self.settings.method == "Monte-Carlo":
            leb_widget.setVisible(False)
        
        self.method.currentTextChanged.connect(lambda text, widget=leb_widget: widget.setVisible(text == "Lebedev"))
        self.method.currentTextChanged.connect(lambda text, widget=mc_widget: widget.setVisible(text == "Monte-Carlo"))

        self.use_centroid = QCheckBox()
        self.use_centroid.setChecked(self.settings.use_centroid)
        self.use_centroid.setToolTip(
            "place the center between selected atoms\n" +
            "might be useful for polydentate ligands"
        )
        calc_layout.addRow("use centroid of centers:", self.use_centroid)

        steric_map_options = QGroupBox("steric map")
        steric_map_layout = QFormLayout(steric_map_options)
        
        self.steric_map = QCheckBox()
        self.steric_map.setChecked(self.settings.steric_map)
        self.steric_map.setToolTip("produce a 2D projection of steric bulk\ncauses buried volume to be reported for individual quadrants")
        steric_map_layout.addRow("create steric map:", self.steric_map)
        
        self.num_pts = QSpinBox()
        self.num_pts.setRange(25, 250)
        self.num_pts.setValue(self.settings.num_pts)
        self.num_pts.setToolTip("number of points along x and y axes")
        steric_map_layout.addRow("number of points:", self.num_pts)
        
        self.include_vbur = QCheckBox()
        self.include_vbur.setChecked(self.settings.include_vbur)
        steric_map_layout.addRow("label quadrants with %V<sub>bur</sub>", self.include_vbur)

        self.map_shape = QComboBox()
        self.map_shape.addItems(["circle", "square"])
        ndx = self.map_shape.findText(self.settings.map_shape, Qt.MatchExactly)
        self.map_shape.setCurrentIndex(ndx)
        steric_map_layout.addRow("map shape:", self.map_shape)
        
        self.auto_minmax = QCheckBox()
        self.auto_minmax.setChecked(self.settings.auto_minmax)
        steric_map_layout.addRow("automatic min. and max.:", self.auto_minmax)
        
        self.map_min = QDoubleSpinBox()
        self.map_min.setRange(-15., 3.5)
        self.map_min.setSingleStep(0.1)
        self.map_min.setValue(self.settings.map_min)
        steric_map_layout.addRow("minimum value:", self.map_min)    
        
        self.map_max = QDoubleSpinBox()
        self.map_max.setRange(-3.5, 15.)
        self.map_max.setSingleStep(0.1)
        self.map_max.setValue(self.settings.map_max)
        steric_map_layout.addRow("maximum value:", self.map_max)
        
        self.num_pts.setEnabled(self.settings.steric_map)
        self.steric_map.stateChanged.connect(lambda state, widget=self.num_pts: widget.setEnabled(state == Qt.Checked))
        
        self.include_vbur.setEnabled(self.settings.steric_map)
        self.steric_map.stateChanged.connect(lambda state, widget=self.include_vbur: widget.setEnabled(state == Qt.Checked))        

        self.map_shape.setEnabled(self.settings.steric_map)
        self.steric_map.stateChanged.connect(lambda state, widget=self.map_shape: widget.setEnabled(state == Qt.Checked))        
        
        self.auto_minmax.setEnabled(self.settings.steric_map)
        self.steric_map.stateChanged.connect(lambda state, widget=self.auto_minmax: widget.setEnabled(state == Qt.Checked))        
        
        self.map_min.setEnabled(not self.settings.auto_minmax and self.settings.steric_map)
        self.steric_map.stateChanged.connect(
            lambda state, widget=self.map_min, widget2=self.auto_minmax: widget.setEnabled(state == Qt.Checked and not widget2.isChecked())
        )
        self.auto_minmax.stateChanged.connect(
            lambda state, widget=self.map_min, widget2=self.steric_map: widget.setEnabled(not state == Qt.Checked and widget2.isChecked())
        )

        self.map_max.setEnabled(not self.settings.auto_minmax and self.settings.steric_map)
        self.steric_map.stateChanged.connect(
            lambda state, widget=self.map_max, widget2=self.auto_minmax: widget.setEnabled(state == Qt.Checked and not widget2.isChecked())
        )
        self.auto_minmax.stateChanged.connect(
            lambda state, widget=self.map_max, widget2=self.steric_map: widget.setEnabled(not state == Qt.Checked and widget2.isChecked())
        )
        
        vis_layout.addRow(steric_map_options)
        
        cutout_options = QGroupBox("volume cutout")
        cutout_layout = QFormLayout(cutout_options)
        
        self.display_cutout = QComboBox()
        self.display_cutout.addItems(["no", "free", "buried"])
        ndx = self.display_cutout.findText(self.settings.display_cutout, Qt.MatchExactly)
        self.display_cutout.setCurrentIndex(ndx)
        self.display_cutout.setToolTip("show free or buried volume")
        cutout_layout.addRow("display volume:", self.display_cutout)
        
        self.point_spacing = QDoubleSpinBox()
        self.point_spacing.setDecimals(3)
        self.point_spacing.setRange(0.01, 0.5)
        self.point_spacing.setSingleStep(0.005)
        self.point_spacing.setSuffix(" \u212B")
        self.point_spacing.setValue(self.settings.point_spacing)
        self.point_spacing.setToolTip(
            "distance between points on cutout\n" +
            "smaller spacing will narrow gaps, but increase time to create the cutout"
        )
        cutout_layout.addRow("point spacing:", self.point_spacing)
        
        self.intersection_scale = QDoubleSpinBox()
        self.intersection_scale.setDecimals(2)
        self.intersection_scale.setRange(1., 10.)
        self.intersection_scale.setSingleStep(0.5)
        self.intersection_scale.setSuffix("x")
        self.intersection_scale.setToolTip(
            "relative density of points where VDW radii intersect\n" +
            "higher density will narrow gaps, but increase time to create cutout"
        )
        self.intersection_scale.setValue(self.settings.intersection_scale)
        cutout_layout.addRow("intersection density:", self.intersection_scale)
        
        self.point_spacing.setEnabled(self.settings.display_cutout != "no")
        self.intersection_scale.setEnabled(self.settings.display_cutout != "no")
        
        self.display_cutout.currentTextChanged.connect(lambda text, widget=self.point_spacing: widget.setEnabled(text != "no"))
        self.display_cutout.currentTextChanged.connect(lambda text, widget=self.intersection_scale: widget.setEnabled(text != "no"))
        
        vis_layout.addRow(cutout_options)
        
        calc_vbur_button = QPushButton("calculate % buried volume for selected centers")
        calc_vbur_button.clicked.connect(self.calc_vbur)
        calc_layout.addRow(calc_vbur_button)
        self.calc_vbur_button = calc_vbur_button
        
        remove_vbur_button = QPushButton("remove % buried volume visualizations")
        remove_vbur_button.clicked.connect(self.del_vbur)
        cutout_layout.addRow(remove_vbur_button)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['model', 'center', '%Vbur'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        calc_layout.addRow(self.table)

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

    def set_ligand_atoms(self):
        self.ligand_atoms = selected_atoms(self.session)
        self.session.logger.status("set ligand to current selection")

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
        
        steric_map = self.steric_map.checkState() == Qt.Checked
        self.settings.steric_map = steric_map
        args["steric_map"] = steric_map
        
        num_pts = self.num_pts.value()
        self.settings.num_pts = num_pts
        args["num_pts"] = num_pts
        
        include_vbur = self.include_vbur.checkState() == Qt.Checked
        self.settings.include_vbur = include_vbur

        use_centroid = self.use_centroid.checkState() == Qt.Checked
        self.settings.use_centroid = use_centroid
        args["useCentroid"] = use_centroid
        
        shape = self.map_shape.currentText()
        self.settings.map_shape = shape
        args["shape"] = shape
        
        method = self.method.currentText()
        self.settings.method = method
        
        if method == "Lebedev":
            args["method"] = "lebedev"
            rad_pts = self.radial_points.currentText()
            self.settings.radial_points = rad_pts
            args["radialPoints"] = rad_pts
            
            ang_pts = self.angular_points.currentText()
            self.settings.angular_points = ang_pts
            args["angularPoints"] = ang_pts

        elif method == "Monte-Carlo":
            args["method"] = "mc"
            min_iter = self.min_iter.value()
            self.settings.minimum_iterations = min_iter
            args["minimumIterations"] = min_iter
        
        display_cutout = self.display_cutout.currentText()
        self.settings.display_cutout = display_cutout
        if display_cutout != "no":
            args["displaySphere"] = display_cutout

        if display_cutout is not None:
            point_spacing = self.point_spacing.value()
            self.settings.point_spacing = point_spacing
            args["pointSpacing"] = point_spacing
            
            intersection_scale = self.intersection_scale.value()
            self.settings.intersection_scale = intersection_scale
            args["intersectionScale"] = intersection_scale

        if len(self.ligand_atoms) > 0:
            args["onlyAtoms"] = [a for a in self.ligand_atoms if not a.deleted]
            if len(args["onlyAtoms"]) == 0:
                args["onlyAtoms"] = None

        auto_minmax = self.auto_minmax.checkState() == Qt.Checked
        self.settings.auto_minmax = auto_minmax
        if not auto_minmax:
            map_max = self.map_max.value()
            self.settings.map_max = map_max
            
            map_min = self.settings.map_min
            self.settings.map_min = map_min

        info = percent_vbur_cmd(
            self.session,
            models,
            return_values=True, 
            **args
        )
        
        self.table.setRowCount(0)
        
        if steric_map:
            for mdl, cent, vbur, map_info in info:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                m = QTableWidgetItem()
                m.setData(Qt.DisplayRole, mdl)
                self.table.setItem(row, 0, m)
                
                c = QTableWidgetItem()
                c.setData(Qt.DisplayRole, cent)
                self.table.setItem(row, 1, c)
                
                v = QTableWidgetItem()
                v.setData(Qt.DisplayRole, ",".join(["%.1f" % x for x in vbur]))
                v.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table.setItem(row, 2, v)
                
                x, y, z, min_alt, max_alt = map_info
                plot = self.tool_window.create_child_window("steric map of %s" % mdl, window_class=StericMap)
                if auto_minmax:
                    plot.set_data(x, y, z, min_alt, max_alt, vbur, radius, include_vbur)
                else:
                    plot.set_data(x, y, z, map_min, map_max, vbur, radius, include_vbur)

        else:
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
                v.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
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
            if model.name.startswith("%Vbur") or model.name.startswith("%Vfree"):
                model.delete()
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")

class StericMap(ChildToolWindow):
    def __init__(self, tool_instance, title, *args, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, *args, **kwargs)

        self._build_ui()
    
    def _build_ui(self):
        self.layout = QGridLayout()
        
        self.ui_area.setLayout(self.layout)
        self.manage(None)
    
    def set_data(self, x, y, z, min_alt, max_alt, vbur, radius, include_vbur):
        fig, ax = plt.subplots()
        steric_map = ax.contourf(x, y, z, extend="min", cmap=copy.copy(plt.cm.get_cmap("jet")), levels=np.linspace(min_alt, max_alt, num=21))
        steric_map.cmap.set_under('w')
        steric_lines = ax.contour(x, y, z, extend="min", colors='k', levels=np.linspace(min_alt, max_alt, num=21))
        bar = fig.colorbar(steric_map, format="%.1f")
        bar.set_label("altitude (Å)")
        ax.set_aspect("equal")
        
        if include_vbur:
            ax.hlines(0, -radius, radius, color='k')
            ax.vlines(0, -radius, radius, color='k')

            ax.text( 0.7 * radius,  0.9 * radius, "%.1f%%" % vbur[0])
            ax.text(-0.9 * radius,  0.9 * radius, "%.1f%%" % vbur[1])
            ax.text(-0.9 * radius, -0.9 * radius, "%.1f%%" % vbur[2])
            ax.text( 0.7 * radius, -0.9 * radius, "%.1f%%" % vbur[3])
        
        if include_vbur:
            circle = plt.Circle((0, 0), radius, color="k", fill=False, linewidth=4)
            ax.add_artist(circle)
        
        canvas = Canvas(fig)
        
        self.layout.addWidget(canvas)
        
        toolbar_widget = QWidget()
        toolbar = NavigationToolbar(canvas, toolbar_widget)
        toolbar.setMaximumHeight(32)
        self.layout.addWidget(toolbar)