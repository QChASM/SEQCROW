from chimerax.core.tools import ToolInstance
from chimerax.atomic import selected_atoms
from chimerax.core.configfile import Value
from chimerax.core.commands import BoolArg
from chimerax.core.settings import Settings
from chimerax.core.models import Surface
from chimerax.ui.gui import MainToolWindow, ChildToolWindow

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
    QSpinBox,
    QWidget,
    QGridLayout,
    QTabWidget,
    QDoubleSpinBox,
    QMessageBox,
    QLabel,
)

from SEQCROW.commands.percent_Vbur import percent_vbur as percent_vbur_cmd
from SEQCROW.tools.per_frame_plot import NavigationToolbar
from SEQCROW.widgets import FakeMenu

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

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
        "point_spacing": 0.1,
        "intersection_scale": 6.0, 
        "include_header": Value(True, BoolArg),
        "delimiter": "comma",
        "steric_map": False,
        "use_scene": False,
        "report_component": "total",
        "num_pts": 100,
        "include_vbur": True,
        "map_shape": "circle", 
        "auto_minmax": True,
        "map_max": 3.5,
        "map_min": -3.5,
        "cutout_labels": "octants",
        "color_map": "jet",
        "contour_lines": True,
        "levels": 20,
    }


class PercentVolumeBuried(ToolInstance):

    help = "https://github.com/QChASM/SEQCROW/wiki/Buried-Volume-Tool"
    SESSION_ENDURING = False
    SESSION_SAVE = False
    
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
        settings_widget = QWidget()
        settings_layout = QFormLayout(settings_widget)
        steric_map_widget = QWidget()
        steric_layout = QFormLayout(steric_map_widget)
        cutout_widget = QWidget()
        vol_cutout_layout = QFormLayout(cutout_widget)
        layout.addWidget(tabs)
        
        tabs.addTab(calc_widget, "calculation")
        tabs.addTab(settings_widget, "settings")
        tabs.addTab(steric_map_widget, "steric map")
        tabs.addTab(cutout_widget, "volume cutout")

        self.radii_option = QComboBox()
        self.radii_option.addItems(["Bondi", "UMN"])
        ndx = self.radii_option.findText(self.settings.radii, Qt.MatchExactly)
        self.radii_option.setCurrentIndex(ndx)
        settings_layout.addRow("radii:", self.radii_option)
       
        self.scale = QDoubleSpinBox()
        self.scale.setValue(self.settings.vdw_scale)
        self.scale.setSingleStep(0.01)
        self.scale.setRange(1., 1.5)
        settings_layout.addRow("VDW scale:", self.scale)
        
        calc_layout.addRow("1.", QLabel("select ligand"))
        set_ligand_atoms = QPushButton("set ligands to current selection")
        set_ligand_atoms.clicked.connect(self.set_ligand_atoms)
        set_ligand_atoms.setToolTip(
            "specify atoms to use in calculation\n" +
            "by default, all atoms will be used unless a single center is specified\n" +
            "in the case of a single center, all atoms except the center is used"
        )
        calc_layout.addRow("2.", set_ligand_atoms)
        self.set_ligand_atoms = set_ligand_atoms
        
        self.radius = QDoubleSpinBox()
        self.radius.setValue(self.settings.center_radius)
        self.radius.setSuffix(" \u212B")
        self.radius.setDecimals(1)
        self.radius.setSingleStep(0.1)
        self.radius.setRange(1., 15.)
        settings_layout.addRow("radius around center:", self.radius)
        
        self.method = QComboBox()
        self.method.addItems(["Lebedev", "Monte-Carlo"])
        self.method.setToolTip(
            "Lebedev: deterministic method\n" +
            "Monte-Carlo: non-deterministic method"
        )
        ndx = self.method.findText(self.settings.method, Qt.MatchExactly)
        self.method.setCurrentIndex(ndx)
        settings_layout.addRow("integration method:", self.method)
        
        leb_widget = QWidget()
        leb_layout = QFormLayout(leb_widget)
        leb_layout.setContentsMargins(0, 0, 0, 0)
        
        self.radial_points = QComboBox()
        self.radial_points.addItems(["20", "32", "64", "75", "99", "127"])
        self.radial_points.setToolTip(
            "more radial points will give more accurate results, but integration will take longer"
        )
        ndx = self.radial_points.findText(self.settings.radial_points, Qt.MatchExactly)
        self.radial_points.setCurrentIndex(ndx)
        leb_layout.addRow("radial points:", self.radial_points)
        
        self.angular_points = QComboBox()
        self.angular_points.addItems(
            ["110", "194", "302", "590", "974", "1454", "2030", "2702", "5810"]
        )
        self.angular_points.setToolTip(
            "more angular points will give more accurate results, but integration will take longer"
        )
        ndx = self.angular_points.findText(self.settings.angular_points, Qt.MatchExactly)
        self.angular_points.setCurrentIndex(ndx)
        leb_layout.addRow("angular points:", self.angular_points)

        settings_layout.addRow(leb_widget)
        
        mc_widget = QWidget()
        mc_layout = QFormLayout(mc_widget)
        mc_layout.setContentsMargins(0, 0, 0, 0)
        
        self.min_iter = QSpinBox()
        self.min_iter.setValue(self.settings.minimum_iterations)
        self.min_iter.setRange(0, 10000)
        self.min_iter.setToolTip(
            "each iteration is 3000 points\n" +
            "iterations continue until convergence criteria are met"
        )
        mc_layout.addRow("minimum interations:", self.min_iter)
        
        settings_layout.addRow(mc_widget)
        
        if self.settings.method == "Lebedev":
            mc_widget.setVisible(False)
        elif self.settings.method == "Monte-Carlo":
            leb_widget.setVisible(False)
        
        self.report_component = QComboBox()
        self.report_component.addItems(
            ["total", "quadrants", "octants"]
        )
        ndx = self.report_component.findText(
            self.settings.report_component, Qt.MatchExactly
        )
        self.report_component.setCurrentIndex(ndx)
        settings_layout.addRow("report volume:", self.report_component)
        
        self.use_scene = QCheckBox()
        self.use_scene.setChecked(self.settings.use_scene)
        self.use_scene.setToolTip("quadrants/octants will use the orientation the molecule is displayed in")
        settings_layout.addRow("use display orientation:", self.use_scene)

        self.method.currentTextChanged.connect(
            lambda text, widget=leb_widget: widget.setVisible(text == "Lebedev")
        )
        self.method.currentTextChanged.connect(
            lambda text, widget=mc_widget: widget.setVisible(text == "Monte-Carlo")
        )

        calc_layout.addRow("3.", QLabel("change selection to reaction center"))
        self.use_centroid = QCheckBox("use centroid of centers")
        self.use_centroid.setChecked(self.settings.use_centroid)
        self.use_centroid.setToolTip(
            "place the center between selected atoms"
        )
        calc_layout.addRow(self.use_centroid)


        self.steric_map = QCheckBox()
        self.steric_map.setChecked(self.settings.steric_map)
        self.steric_map.setToolTip("produce a 2D projection of steric bulk\ncauses buried volume to be reported for individual quadrants")
        steric_layout.addRow("create steric map:", self.steric_map)

        self.pair_difference_map = QCheckBox()
        steric_layout.addRow("pairwise difference:", self.pair_difference_map)

        self.num_pts = QSpinBox()
        self.num_pts.setRange(25, 1000)
        self.num_pts.setValue(self.settings.num_pts)
        self.num_pts.setToolTip("number of points along x and y axes")
        steric_layout.addRow("number of points:", self.num_pts)
        
        self.levels = QSpinBox()
        self.levels.setRange(5, 1000)
        self.levels.setValue(self.settings.levels)
        self.levels.setToolTip("number of contour levels")
        steric_layout.addRow("contour levels:", self.levels)
        
        self.contour_lines = QCheckBox()
        self.contour_lines.setChecked(self.settings.contour_lines)
        self.contour_lines.setToolTip("add black contour lines to the plot")
        steric_layout.addRow("contour lines:", self.contour_lines)
        
        self.color_map = QComboBox()
        self.color_map.addItems(sorted([
            'viridis', 'plasma', 'inferno', 'magma', 'cividis',
            "Greys", "Purples", 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone',
            'pink', 'spring', 'summer', 'autumn', 'winter', 'cool',
            'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper',
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
            'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
            'twilight', 'twilight_shifted', 'hsv',
            'Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2',
            'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b',
            'tab20c', 'flag', 'prism', 'ocean', 'gist_earth', 'terrain',
            'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap',
            'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet',
            'turbo', 'nipy_spectral', 'gist_ncar',
        ]))
        ndx = self.color_map.findText(self.settings.color_map)
        self.color_map.setCurrentIndex(ndx)
        steric_layout.addRow("color map:", self.color_map)
        
        self.include_vbur = QCheckBox()
        self.include_vbur.setChecked(self.settings.include_vbur)
        steric_layout.addRow("label quadrants with %V<sub>bur</sub>", self.include_vbur)

        self.map_shape = QComboBox()
        self.map_shape.addItems(["circle", "square"])
        ndx = self.map_shape.findText(self.settings.map_shape, Qt.MatchExactly)
        self.map_shape.setCurrentIndex(ndx)
        steric_layout.addRow("map shape:", self.map_shape)
        
        self.auto_minmax = QCheckBox()
        self.auto_minmax.setChecked(self.settings.auto_minmax)
        steric_layout.addRow("automatic min. and max.:", self.auto_minmax)
        
        self.map_min = QDoubleSpinBox()
        self.map_min.setRange(-15., 0.)
        self.map_min.setSuffix(" \u212B")
        self.map_min.setSingleStep(0.1)
        self.map_min.setValue(self.settings.map_min)
        steric_layout.addRow("minimum value:", self.map_min)    
        
        self.map_max = QDoubleSpinBox()
        self.map_max.setRange(0., 15.)
        self.map_max.setSuffix(" \u212B")
        self.map_max.setSingleStep(0.1)
        self.map_max.setValue(self.settings.map_max)
        steric_layout.addRow("maximum value:", self.map_max)

        self.num_pts.setEnabled(self.settings.steric_map)
        self.steric_map.stateChanged.connect(
            lambda state, widget=self.num_pts: widget.setEnabled(Qt.CheckState(state) == Qt.Checked)
        )
        
        self.pair_difference_map.setEnabled(self.settings.steric_map)
        self.steric_map.stateChanged.connect(
            lambda state, widget=self.pair_difference_map: widget.setEnabled(Qt.CheckState(state) == Qt.Checked)
        )
        
        self.include_vbur.setEnabled(self.settings.steric_map)
        self.steric_map.stateChanged.connect(
            lambda state, widget=self.include_vbur: widget.setEnabled(Qt.CheckState(state) == Qt.Checked)
        )

        self.map_shape.setEnabled(self.settings.steric_map)
        self.steric_map.stateChanged.connect(
            lambda state, widget=self.map_shape: widget.setEnabled(Qt.CheckState(state) == Qt.Checked)
        )
        
        self.auto_minmax.setEnabled(self.settings.steric_map)
        self.steric_map.stateChanged.connect(
            lambda state, widget=self.auto_minmax: widget.setEnabled(Qt.CheckState(state) == Qt.Checked)
        )
        
        self.map_min.setEnabled(not self.settings.auto_minmax and self.settings.steric_map)
        self.steric_map.stateChanged.connect(
            lambda state, widget=self.map_min, widget2=self.auto_minmax: widget.setEnabled(Qt.CheckState(state) == Qt.Checked and not widget2.isChecked())
        )
        self.auto_minmax.stateChanged.connect(
            lambda state, widget=self.map_min, widget2=self.steric_map: widget.setEnabled(not Qt.CheckState(state) == Qt.Checked and widget2.isChecked())
        )

        self.map_max.setEnabled(not self.settings.auto_minmax and self.settings.steric_map)
        self.steric_map.stateChanged.connect(
            lambda state, widget=self.map_max, widget2=self.auto_minmax: widget.setEnabled(Qt.CheckState(state) == Qt.Checked and not widget2.isChecked())
        )
        self.auto_minmax.stateChanged.connect(
            lambda state, widget=self.map_max, widget2=self.steric_map: widget.setEnabled(not Qt.CheckState(state) == Qt.Checked and widget2.isChecked())
        )


        self.display_cutout = QComboBox()
        self.display_cutout.addItems(["no", "free", "buried"])
        ndx = self.display_cutout.findText(self.settings.display_cutout, Qt.MatchExactly)
        self.display_cutout.setCurrentIndex(ndx)
        self.display_cutout.setToolTip("show free or buried volume")
        vol_cutout_layout.addRow("display volume:", self.display_cutout)
        
        self.pair_difference_cutout = QCheckBox()
        vol_cutout_layout.addRow("pairwise difference:", self.pair_difference_cutout)
        
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
        vol_cutout_layout.addRow("point spacing:", self.point_spacing)
        
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
        vol_cutout_layout.addRow("intersection density:", self.intersection_scale)
        
        self.cutout_labels = QComboBox()
        self.cutout_labels.addItems(["none", "quadrants", "octants"])
        ndx = self.cutout_labels.findText(self.settings.cutout_labels, Qt.MatchExactly)
        self.cutout_labels.setCurrentIndex(ndx)
        vol_cutout_layout.addRow("label sections:", self.cutout_labels)

        self.point_spacing.setEnabled(self.settings.display_cutout != "no")
        self.pair_difference_cutout.setEnabled(self.settings.display_cutout != "no")
        self.intersection_scale.setEnabled(self.settings.display_cutout != "no")
        self.cutout_labels.setEnabled(self.settings.display_cutout != "no")
        
        self.display_cutout.currentTextChanged.connect(lambda text, widget=self.point_spacing: widget.setEnabled(text != "no"))
        self.display_cutout.currentTextChanged.connect(lambda text, widget=self.pair_difference_cutout: widget.setEnabled(text != "no"))
        self.display_cutout.currentTextChanged.connect(lambda text, widget=self.intersection_scale: widget.setEnabled(text != "no"))
        self.display_cutout.currentTextChanged.connect(lambda text, widget=self.cutout_labels: widget.setEnabled(text != "no"))

        calc_vbur_button = QPushButton("calculate % buried volume for selected centers")
        calc_vbur_button.clicked.connect(self.calc_vbur)
        calc_layout.addRow("4.", calc_vbur_button)
        self.calc_vbur_button = calc_vbur_button
        
        remove_vbur_button = QPushButton("remove % buried volume visualizations")
        remove_vbur_button.clicked.connect(self.del_vbur)
        vol_cutout_layout.addRow(remove_vbur_button)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['model', 'center', '%Vbur'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        calc_layout.addRow(self.table)

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
        self.copy = copy
        
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
        
        color_map = self.color_map.currentText()
        self.settings.color_map = color_map
        
        levels = self.levels.value()
        self.settings.levels = levels

        contour_lines = self.contour_lines.isChecked()
        self.settings.contour_lines = contour_lines
        
        use_scene = self.use_scene.checkState() == Qt.Checked
        self.settings.use_scene = use_scene
        args["useScene"] = use_scene
        
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

        report_component = self.report_component.currentText()
        self.settings.report_component = report_component
        args["reportComponent"] = report_component
        
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

        if display_cutout != "no":
            point_spacing = self.point_spacing.value()
            self.settings.point_spacing = point_spacing
            args["pointSpacing"] = point_spacing
            
            intersection_scale = self.intersection_scale.value()
            self.settings.intersection_scale = intersection_scale
            args["intersectionScale"] = intersection_scale

            cutout_labels = self.cutout_labels.currentText()
            self.settings.cutout_labels = cutout_labels
            args["labels"] = cutout_labels

            if self.pair_difference_cutout.isChecked():
                args["difference"] = True

        if len(self.ligand_atoms) > 0:
            args["onlyAtoms"] = [a for a in self.ligand_atoms if not a.deleted]
            if len(args["onlyAtoms"]) == 0:
                args["onlyAtoms"] = None

        auto_minmax = self.auto_minmax.checkState() == Qt.Checked
        self.settings.auto_minmax = auto_minmax
        if not auto_minmax:
            map_max = self.map_max.value()
            self.settings.map_max = map_max
            
            map_min = self.map_min.value()
            self.settings.map_min = map_min

        info = percent_vbur_cmd(
            self.session,
            models,
            return_values=True, 
            **args
        )
        
        # self.table.setRowCount(0)
        
        if steric_map:
            for mdl, cent, _, _, vbur, map_info in info:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                m = QTableWidgetItem()
                m.setData(Qt.DisplayRole, mdl.name)
                self.table.setItem(row, 0, m)
                
                c = QTableWidgetItem()
                if hasattr(cent, "__iter__"):
                    c.setData(Qt.DisplayRole, ", ".join([a.atomspec for a in cent]))
                else:
                    c.setData(Qt.DisplayRole, cent.atomspec)

                self.table.setItem(row, 1, c)
                
                v = QTableWidgetItem()
                if report_component == "octants":
                    v.setData(
                        Qt.DisplayRole,
                        ",".join(["%.1f" % x for x in vbur])
                    )
                elif report_component == "quadrants":
                    v.setData(
                        Qt.DisplayRole,
                        ",".join("%.1f" % x for x in
                            [
                                vbur[0] + vbur[7],
                                vbur[1] + vbur[6],
                                vbur[2] + vbur[5],
                                vbur[3] + vbur[4],
                            ]
                        )
                    )
                else:
                    if hasattr(vbur, "__iter__"):
                        v.setData(Qt.DisplayRole, "%.1f" % sum(vbur))
                    else:
                        v.setData(Qt.DisplayRole, "%.1f" % vbur)
                v.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table.setItem(row, 2, v)
                
                if self.pair_difference_map.isChecked():
                    continue
                
                x, y, z, min_alt, max_alt = map_info
                plot = self.tool_window.create_child_window(
                    "steric map of %s" % mdl.name, window_class=StericMap
                )
                if auto_minmax:
                    plot.set_data(
                        x, y, z,
                        min_alt, max_alt,
                        vbur, radius, include_vbur,
                        color_map, levels, contour_lines,
                    )
                else:
                    plot.set_data(
                        x, y, z,
                        map_min, map_max,
                        vbur, radius, include_vbur,
                        color_map, levels, contour_lines,
                    )

        
            if self.pair_difference_map.isChecked():
                for i, (mdl1, cent1, _, _, vbur1, map_info1) in enumerate(info):
                    x, y, z1, min_alt1, max_alt1 = map_info1
                    for mdl2, cent2, _, _, vbur2, map_info2 in info[i + 1:]:
                        x, y, z2, min_alt2, max_alt2 = map_info2
                        z = z1 - z2
                        a_not_in_b = np.zeros(z.shape)
                        b_not_in_a = np.zeros(z.shape)
                        for i in range(0, z.shape[0]):
                            for j in range(0, z.shape[1]):
                                if z1[i, j] < min_alt1:
                                    z[i, j] = -1000
                                    if z2[i, j] > min_alt2:
                                        b_not_in_a[i, j] = 1
                                elif z2[i, j] < min_alt2:
                                    z[i, j] = -1000
                                    if z1[i, j] > min_alt1:
                                        a_not_in_b[i, j] = 1
                        
                        min_alt = np.min(z[z > (min_alt1 - max_alt2)])
                        max_alt = np.max(z)
    
                        plot = self.tool_window.create_child_window(
                            "steric map difference of %s and %s" % (mdl1.name, mdl2.name),
                            window_class=StericMap
                        )
                        if auto_minmax:
                            plot.set_difference_data(
                                x, y, z,
                                a_not_in_b, b_not_in_a,
                                min_alt, max_alt, 
                                vbur1, vbur2,
                                radius,
                                include_vbur,
                                color_map,
                                levels, contour_lines,
                            )
                        else:
                            plot.set_difference_data(
                                x, y, z, 
                                a_not_in_b, b_not_in_a,
                                map_min, map_max, 
                                vbur1, vbur2,
                                radius,
                                include_vbur,
                                color_map,
                                levels, contour_lines,
                            )

        else:
            for mdl, cent, _, _, vbur in info:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                m = QTableWidgetItem()
                m.setData(Qt.DisplayRole, mdl.name)
                self.table.setItem(row, 0, m)
                
                c = QTableWidgetItem()
                c.setData(Qt.DisplayRole, cent)
                if hasattr(cent, "__iter__"):
                    c.setData(Qt.DisplayRole, ", ".join([a.atomspec for a in cent]))
                else:
                    c.setData(Qt.DisplayRole, cent.atomspec)
                self.table.setItem(row, 1, c)
                
                v = QTableWidgetItem()
                if report_component == "octants":
                    v.setData(
                        Qt.DisplayRole,
                        ",".join(["%.1f" % x for x in vbur])
                    )
                elif report_component == "quadrants":
                    v.setData(
                        Qt.DisplayRole,
                        ",".join("%.1f" % x for x in
                            [
                                vbur[0] + vbur[7],
                                vbur[1] + vbur[6],
                                vbur[2] + vbur[5],
                                vbur[3] + vbur[4],
                            ]
                        )
                    )
                else:
                    if hasattr(vbur, "__iter__"):
                        v.setData(Qt.DisplayRole, "%.1f" % sum(vbur))
                    else:
                        v.setData(Qt.DisplayRole, "%.1f" % vbur)
                v.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table.setItem(row, 2, v)
        
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)

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
    
    def set_data(
        self, x, y, z,
        min_alt, max_alt,
        vbur,
        radius,
        include_vbur,
        color_map, levels, contour_lines,
    ):
        fig, ax = plt.subplots()
        cmap = copy.copy(plt.cm.get_cmap(color_map))
        cmap.set_under('w')
        steric_map = ax.contourf(
            x, y, z,
            extend="min",
            cmap=cmap,
            levels=np.linspace(min_alt, max_alt, num=levels)
        )
        if contour_lines:
            ax.contour(
                x, y, z,
                extend="min",
                colors='k',
                levels=np.linspace(min_alt, max_alt, num=levels)
            )
        bar = fig.colorbar(steric_map, format="%.1f")
        bar.set_label("altitude (Å)")
        ax.set_aspect("equal")
        
        if include_vbur:
            ax.hlines(0, -radius, radius, color='k')
            ax.vlines(0, -radius, radius, color='k')

            vbur_1 = vbur[0] + vbur[7]
            vbur_2 = vbur[1] + vbur[6]
            vbur_3 = vbur[2] + vbur[5]
            vbur_4 = vbur[3] + vbur[4]
            ax.text(+0.7 * radius, +0.9 * radius, "%.1f%%" % vbur_1)
            ax.text(-0.9 * radius, +0.9 * radius, "%.1f%%" % vbur_2)
            ax.text(-0.9 * radius, -0.9 * radius, "%.1f%%" % vbur_3)
            ax.text(+0.7 * radius, -0.9 * radius, "%.1f%%" % vbur_4)
        
            circle = plt.Circle((0, 0), radius, color="k", fill=False, linewidth=4)
            ax.add_artist(circle)
        
        canvas = Canvas(fig)
        
        self.layout.addWidget(canvas)
        
        toolbar_widget = QWidget()
        toolbar = NavigationToolbar(canvas, toolbar_widget)
        toolbar.setMaximumHeight(32)
        self.layout.addWidget(toolbar) 

    def set_difference_data(
        self,
        x, y, z,
        a_not_in_b, b_not_in_a,
        min_alt, max_alt,
        vbur1, vbur2,
        radius,
        include_vbur,
        color_map, levels, contour_lines,
    ):
        vbur = [v1 - v2 for v1, v2 in zip(vbur1, vbur2)]
        fig, ax = plt.subplots()
        cmap = copy.copy(plt.cm.get_cmap(color_map))
        cmap_a_not_in_b = LinearSegmentedColormap.from_list("a_not_in_b", [(0.5, 0, 0), (0.5, 0, 0)])
        cmap_b_not_in_a = LinearSegmentedColormap.from_list("a_not_in_b", [(0, 0, 0.5), (0, 0, 0.5)])
        if abs(min_alt) < abs(max_alt):
            cmap_range = [-abs(max_alt), max_alt]
        else:
            cmap_range = [min_alt, abs(min_alt)]
        
        cmap_range.sort()
        
        cmap.set_under("w")
        steric_map = ax.contourf(
            x,
            y,
            z,
            extend="min",
            cmap=cmap,
            levels=np.linspace(*cmap_range, num=levels),
        )
        ax.contourf(
            x,
            y,
            a_not_in_b,
            extend="neither",
            cmap=cmap_a_not_in_b,
            levels=[0.99, 1],
        )
        ax.contourf(
            x,
            y,
            b_not_in_a,
            extend="neither",
            cmap=cmap_b_not_in_a,
            levels=[0.99, 1],
        )
        if contour_lines:
            steric_lines = ax.contour(
                x,
                y,
                z,
                extend="min",
                colors="k",
                levels=np.linspace(*cmap_range, num=levels),
            )
            steric_lines = ax.contour(
                x,
                y,
                a_not_in_b,
                extend="neither",
                colors="k",
                levels=[0.99, 1],
            )
            steric_lines = ax.contour(
                x,
                y,
                b_not_in_a,
                extend="neither",
                colors="k",
                levels=[0.99, 1],
            )
        bar = fig.colorbar(steric_map, format="%.1f")
        bar.set_label("\u0394altitude (Å)")
        ax.set_aspect("equal")

        if include_vbur:
            ax.hlines(0, -radius, radius, color="k")
            ax.vlines(0, -radius, radius, color="k")
    
            vbur_1 = vbur[0] + vbur[7]
            vbur_2 = vbur[1] + vbur[6]
            vbur_3 = vbur[2] + vbur[5]
            vbur_4 = vbur[3] + vbur[4]
            ax.text(+0.7 * radius, +0.9 * radius, "%.1f%%" % vbur_1)
            ax.text(-0.9 * radius, +0.9 * radius, "%.1f%%" % vbur_2)
            ax.text(-0.9 * radius, -0.9 * radius, "%.1f%%" % vbur_3)
            ax.text(+0.7 * radius, -0.9 * radius, "%.1f%%" % vbur_4)

            circle = plt.Circle((0, 0), radius, color="k", fill=False, linewidth=4)
            ax.add_artist(circle)
        
        canvas = Canvas(fig)
        
        self.layout.addWidget(canvas)
        
        toolbar_widget = QWidget()
        toolbar = NavigationToolbar(canvas, toolbar_widget)
        toolbar.setMaximumHeight(32)
        self.layout.addWidget(toolbar)