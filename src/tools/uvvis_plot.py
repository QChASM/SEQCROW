import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow
from chimerax.ui.widgets import ColorButton
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import FloatArg, TupleOf, IntArg

from AaronTools.comp_output import CompOutput
from AaronTools.geometry import Geometry
from AaronTools.spectra import ValenceExcitations

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from matplotlib import rcParams
import matplotlib.patheffects as pe

from Qt.QtCore import Qt, QSize
from Qt.QtGui import QIcon, QPixmap, QAction
from Qt.QtWidgets import (
    QSpinBox,
    QDoubleSpinBox,
    QGridLayout,
    QPushButton,
    QTabWidget,
    QComboBox,
    QTableWidget,
    QWidget,
    QFormLayout,
    QCheckBox,
    QFileDialog,
    QStyle,
    QLabel,
    QHBoxLayout,
    QTreeWidget,
    QSizePolicy,
    QTreeWidgetItem,
)

from SEQCROW.tools.per_frame_plot import NavigationToolbar
from SEQCROW.utils import iter2str
from SEQCROW.widgets import (
    FilereaderComboBox,
    FakeMenu,
    ScientificSpinBox,
    Choices,
)



rcParams["savefig.dpi"] = 300


solid_line_pixmap = QPixmap([
    "50  4  2  1",
    "a c #FFFFFF",
    "b c #000000",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "abbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbba",
    "abbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbba",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
])
solid_line = QIcon(solid_line_pixmap)

dashed_line_pixmap = QPixmap([
    "50  4  2  1",
    "a c #FFFFFF",
    "b c #000000",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "abbbbbbbbaabbbbbbbbaabbbbbbbbaabbbbbbbbaabbbbbbbba",
    "abbbbbbbbaabbbbbbbbaabbbbbbbbaabbbbbbbbaabbbbbbbba",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
])
dashed_line = QIcon(dashed_line_pixmap)

dotted_line_pixmap = QPixmap([
    "48  4  2  1",
    "a c #FFFFFF",
    "b c #000000",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "abbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabba",
    "abbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabbaabba",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
])
dotted_line = QIcon(dotted_line_pixmap)

dashdot_line_pixmap = QPixmap([
    "56  4  2  1",
    "a c #FFFFFF",
    "b c #000000",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "abbbbbbbbaabbaabbbbbbbbaabbaabbbbbbbbaabbaabbbbbbbbaabba",
    "abbbbbbbbaabbaabbbbbbbbaabbaabbbbbbbbaabbaabbbbbbbbaabba",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
])
dashdot_line = QIcon(dashdot_line_pixmap)

dashdotdot_line_pixmap = QPixmap([
    "50  4  2  1",
    "a c #FFFFFF",
    "b c #000000",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "abbbbbbbbaabbaabbaabbbbbbbbaabbaabbaabbbbbbbbaabba",
    "abbbbbbbbaabbaabbaabbbbbbbbaabbaabbaabbbbbbbbaabba",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
])
dashdotdot_line = QIcon(dashdotdot_line_pixmap)


color_cycle = [
    (1.0, 0.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.0, 0.7, 0.1),
    (0.9, 0.6, 0.2),
    (0.8, 0.1, 0.8),
]


class _UVVisSpectrumSettings(Settings):
    AUTO_SAVE = {
        'fwhm': Value(0.5, FloatArg), 
        'peak_type': 'Gaussian', 
        'plot_type': 'uv-vis',
        'voigt_mix': 0.5,
        'exp_color': Value((0.0, 0.0, 1.0), TupleOf(FloatArg, 3), iter2str),
        'figure_width': 5,
        'figure_height': 3.5,
        "fixed_size": False,
        'w0': 100,
        'temperature': 298.15,
        'transient': False,
        "weight_method": "QRRHO",
        'col_1': Value(150, IntArg), 
        'col_2': Value(150, IntArg), 
        'col_3': Value(150, IntArg), 
        'x_units': "nm",
        "point_spacing": 0.1,
        "spacing_type": "nonlinear spacing",
}


class UVVisSpectrum(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False
    help = "https://github.com/QChASM/SEQCROW/wiki/UV-Vis-Spectrum-Tool"
    
    def __init__(self, session, name):
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)      

        self.settings = _UVVisSpectrumSettings(session, "UV-Vis Spectrum")

        self.highlighted_mode = []
        self.highlight_frs = []
        self.highlighted_labels = []
        self.highlighted_lines = []
        self._last_mouse_xy = None
        self._dragged = False
        self._min_drag = 10	
        self._drag_mode = None
        self.press = None
        self.drag_prev = None
        self.dragging = False
        self.exp_data = None
        
        self._build_ui()
        
        self.tool_window.fill_context_menu = self.fill_context_menu

    def _build_ui(self):
        layout = QGridLayout()
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["UV/vis file", "frequency file", "energy file", "remove"])
        self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tree.resizeColumnToContents(3)
        
        component_widget = QWidget()
        component_layout = QGridLayout(component_widget)
        
        root_item = self.tree.invisibleRootItem()
        plus = QTreeWidgetItem(root_item)
        plus_button = QPushButton("add molecule")
        plus_button.setFlat(True)
        plus_button.clicked.connect(self.add_mol_group)        
        plus_button2 = QPushButton("")
        plus_button2.setFlat(True)
        plus_button2.clicked.connect(self.add_mol_group)
        self.tree.setItemWidget(plus, 0, plus_button)
        self.tree.setItemWidget(plus, 1, plus_button2)
        self.tree.insertTopLevelItem(1, plus)
        # TODO: have a setting save the size the thermo tool
        self.tree.setColumnWidth(0, self.settings.col_1)
        self.tree.setColumnWidth(1, self.settings.col_2)
        
        self.add_mol_group()
        
        component_layout.addWidget(self.tree, 0, 0, 1, 6)
        
        self.temperature = QDoubleSpinBox()
        self.temperature.setDecimals(2)
        self.temperature.setRange(0.01, 5000)
        self.temperature.setSingleStep(1)
        self.temperature.setValue(self.settings.temperature)
        self.temperature.setSuffix(" K")
        component_layout.addWidget(QLabel("T ="), 1, 2, 1, 1, Qt.AlignRight | Qt.AlignHCenter)
        component_layout.addWidget(self.temperature, 1, 3, 1, 1, Qt.AlignLeft | Qt.AlignHCenter)
        
        self.w0 = QDoubleSpinBox()
        self.w0.setDecimals(2)
        self.w0.setRange(1, 250)
        self.w0.setSingleStep(5)
        self.w0.setValue(self.settings.w0)
        self.w0.setSuffix(" cm\u207b\u00b9")
        component_layout.addWidget(QLabel("ω<sub>0</sub> ="), 1, 4, 1, 1, Qt.AlignRight | Qt.AlignHCenter)
        component_layout.addWidget(self.w0, 1, 5, 1, 1, Qt.AlignLeft | Qt.AlignHCenter)

        self.weight_method = QComboBox()
        self.weight_method.addItems([
            "electronic",
            "zero-point",
            "enthalpy",
            "free (RRHO)",
            "free (Quasi-RRHO)",
            "free (Quasi-harmonic)",
        ])
        self.weight_method.setItemData(0, CompOutput.ELECTRONIC_ENERGY)
        self.weight_method.setItemData(1, CompOutput.ZEROPOINT_ENERGY)
        self.weight_method.setItemData(2, CompOutput.RRHO_ENTHALPY)
        self.weight_method.setItemData(3, CompOutput.RRHO)
        self.weight_method.setItemData(4, CompOutput.QUASI_RRHO)
        self.weight_method.setItemData(5, CompOutput.QUASI_HARMONIC)
        ndx = self.weight_method.findData(self.settings.weight_method, flags=Qt.MatchExactly)
        self.weight_method.setCurrentIndex(ndx)
        component_layout.addWidget(QLabel("energy for weighting:"), 1, 0, 1, 1, Qt.AlignRight | Qt.AlignHCenter)
        component_layout.addWidget(self.weight_method, 1, 1, 1, 1, Qt.AlignLeft | Qt.AlignHCenter)


        show_conformers = QLabel("show contribution from conformers with a Boltzmann population above:")
        component_layout.addWidget(show_conformers, 2, 0, 1, 4, Qt.AlignRight | Qt.AlignVCenter)
        
        self.boltzmann_pop_limit = QDoubleSpinBox()
        self.boltzmann_pop_limit.setRange(1.0, 99.0)
        self.boltzmann_pop_limit.setSingleStep(1.0)
        self.boltzmann_pop_limit.setDecimals(1)
        self.boltzmann_pop_limit.setValue(10.0)
        self.boltzmann_pop_limit.setSuffix("%")
        component_layout.addWidget(self.boltzmann_pop_limit, 2, 4, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)
        
        self.show_boltzmann_pop = QCheckBox()
        component_layout.addWidget(self.show_boltzmann_pop, 2, 5, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)


        tabs.addTab(component_widget, "components")
        
        
        plot_widget = QWidget()
        
        plot_widget = QWidget()
        plot_layout = QGridLayout(plot_widget)
        
        self.figure = Figure(figsize=(1.5, 1.5), dpi=100)
        self.figure.subplots_adjust(bottom=0.15)
        self.canvas = Canvas(self.figure)

        self.canvas.mpl_connect('button_release_event', self.unclick)
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.mpl_connect('motion_notify_event', self.drag)
        self.canvas.mpl_connect('scroll_event', self.zoom)
        
        self.canvas.setMinimumWidth(400)
        # self.canvas.setMinimumHeight(300)

        plot_layout.addWidget(self.canvas, 1, 0, 1, 7)

        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon(refresh_button.style().standardIcon(QStyle.SP_BrowserReload)))
        refresh_button.clicked.connect(self.refresh_plot)
        plot_layout.addWidget(refresh_button, 2, 0, 1, 1, Qt.AlignVCenter)

        toolbar_widget = QWidget()
        self.toolbar = NavigationToolbar(self.canvas, toolbar_widget)
        self.toolbar.setMaximumHeight(32)
        plot_layout.addWidget(self.toolbar, 2, 1, 1, 1)

        plot_layout.addWidget(QLabel("fixed size:"), 2, 2, 1, 1, Qt.AlignVCenter | Qt.AlignRight)

        self.fixed_size = QCheckBox()
        self.fixed_size.setCheckState(Qt.Checked if self.settings.fixed_size else Qt.Unchecked)
        self.fixed_size.stateChanged.connect(self.change_figure_size)
        plot_layout.addWidget(self.fixed_size, 2, 3, 1, 1, Qt.AlignVCenter | Qt.AlignLeft)

        self.figure_width = QDoubleSpinBox()
        self.figure_width.setRange(1, 24)
        self.figure_width.setDecimals(2)
        self.figure_width.setSingleStep(0.25)
        self.figure_width.setSuffix(" in.")
        self.figure_width.setValue(self.settings.figure_width)
        self.figure_width.valueChanged.connect(self.change_figure_size)
        plot_layout.addWidget(self.figure_width, 2, 4, 1, 1)
     
        plot_layout.addWidget(QLabel("x"), 2, 5, 1, 1, Qt.AlignVCenter | Qt.AlignHCenter)
     
        self.figure_height = QDoubleSpinBox()
        self.figure_height.setRange(1, 24)
        self.figure_height.setDecimals(2)
        self.figure_height.setSingleStep(0.25)
        self.figure_height.setSuffix(" in.")
        self.figure_height.setValue(self.settings.figure_height)
        self.figure_height.valueChanged.connect(self.change_figure_size)
        plot_layout.addWidget(self.figure_height, 2, 6, 1, 1)

        self.change_figure_size()

        self.plot_type = QComboBox()
        self.plot_type.addItems([
            "UV/vis",
            "UV/vis transmittance",
            "UV/vis (dipole velocity)",
            "UV/vis transmittance (dipole velocity)",
            "ECD",
            "ECD (dipole velocity)",
        ])
        self.plot_type.setItemData(0, "uv-vis")
        self.plot_type.setItemData(1, "transmittance")
        self.plot_type.setItemData(2, "uv-vis-velocity")
        self.plot_type.setItemData(3, "transmittance-velocity")
        self.plot_type.setItemData(4, "ecd")
        self.plot_type.setItemData(5, "ecd-velocity")
        ndx = self.plot_type.findData(self.settings.plot_type, flags=Qt.MatchExactly)
        if ndx:
            self.plot_type.setCurrentIndex(ndx)
        self.plot_type.currentIndexChanged.connect(self.refresh_plot)
        plot_layout.addWidget(QLabel("plot type:"), 0, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        plot_layout.addWidget(self.plot_type, 0, 1, 1, 6, Qt.AlignLeft | Qt.AlignVCenter)
        
        plot_layout.setRowStretch(0, 0)
        plot_layout.setRowStretch(1, 1)
        plot_layout.setRowStretch(2, 0)
        
        tabs.addTab(plot_widget, "plot")

        # peak style
        plot_settings_widget = QWidget()
        plot_settings_layout = QFormLayout(plot_settings_widget)

        self.peak_type = QComboBox()
        self.peak_type.addItems(['Gaussian', 'Lorentzian', 'pseudo-Voigt', 'Delta'])
        ndx = self.peak_type.findText(self.settings.peak_type, Qt.MatchExactly)
        self.peak_type.setCurrentIndex(ndx)
        plot_settings_layout.addRow("peak type:", self.peak_type)
        
        self.fwhm = QDoubleSpinBox()
        self.fwhm.setRange(0.01, 10.0)
        self.fwhm.setSingleStep(0.01)
        self.fwhm.setValue(self.settings.fwhm)
        self.fwhm.setSuffix(" eV")
        self.fwhm.setToolTip("width of peaks at half of their maximum value")
        plot_settings_layout.addRow("FWHM:", self.fwhm)
        
        self.fwhm.setEnabled(self.peak_type.currentText() != "Delta")
        self.peak_type.currentTextChanged.connect(lambda text, widget=self.fwhm: widget.setEnabled(text != "Delta"))
        
        self.voigt_mix = QDoubleSpinBox()
        self.voigt_mix.setSingleStep(0.005)
        self.voigt_mix.setDecimals(3)
        self.voigt_mix.setRange(0, 1)
        self.voigt_mix.setValue(self.settings.voigt_mix)
        self.voigt_mix.setToolTip("fraction of pseudo-Voigt function that is Gaussian")
        plot_settings_layout.addRow("Voigt mixing:", self.voigt_mix)
        
        self.voigt_mix.setEnabled(self.peak_type.currentText() == "pseudo-Voigt")
        self.peak_type.currentTextChanged.connect(lambda text, widget=self.voigt_mix: widget.setEnabled(text == "pseudo-Voigt"))
        
        self.shift = QDoubleSpinBox()
        self.shift.setRange(-5, 5)
        self.shift.setSingleStep(0.1)
        self.shift.setDecimals(2)
        self.shift.setSuffix(" eV")
        plot_settings_layout.addRow("shift excitation energies:", self.shift)

        self.x_units = QComboBox()
        self.x_units.addItems(["nm", "eV"])
        ndx = self.x_units.findText(self.settings.x_units, Qt.MatchExactly)
        self.x_units.setCurrentIndex(ndx)
        plot_settings_layout.addRow("x-axis units:", self.x_units)
        
        spacing = ScientificSpinBox(
            minimum=1e-6,
            maximum=10,
            default=self.settings.point_spacing,
            suffix=" eV",
        )
        self.point_spacing = Choices(
            options={
                None: "nonlinear spacing",
                spacing: "fixed spacing",
            },
            default=self.settings.spacing_type,
        )
        plot_settings_layout.addRow("point spacing:", self.point_spacing)

        self.spectra_type = QComboBox()
        self.spectra_type.addItems(["regular", "transient", "SOC"])
        plot_settings_layout.addRow("data:", self.spectra_type)
        
        tabs.addTab(plot_settings_widget, "plot settings")
        
        # plot experimental data alongside computed
        experimental_widget = QWidget()
        experimental_layout = QFormLayout(experimental_widget)
        
        self.skip_lines = QSpinBox()
        self.skip_lines.setRange(0, 15)
        experimental_layout.addRow("skip first lines:", self.skip_lines)
        
        browse_button = QPushButton("browse...")
        browse_button.clicked.connect(self.load_data)
        experimental_layout.addRow("load CSV data:", browse_button)
        
        self.line_color = ColorButton(has_alpha_channel=False, max_size=(16, 16))
        self.line_color.set_color(self.settings.exp_color)
        experimental_layout.addRow("line color:", self.line_color)
        
        clear_button = QPushButton("clear experimental data")
        clear_button.clicked.connect(self.clear_data)
        experimental_layout.addRow(clear_button)
        
        tabs.addTab(experimental_widget, "plot experimental data")
        
        # break x axis
        interrupt_widget = QWidget()
        interrupt_layout = QFormLayout(interrupt_widget)

        self.section_table = QTableWidget()
        self.section_table.setColumnCount(3)
        self.section_table.setHorizontalHeaderLabels(["minimum", "maximum", "remove"])
        self.section_table.cellClicked.connect(self.section_table_clicked)
        self.section_table.setEditTriggers(QTableWidget.NoEditTriggers)
        interrupt_layout.addRow(self.section_table)
        self.add_section()

        # auto_section = QPushButton("automatically section")
        # auto_section.clicked.connect(self.auto_breaks)
        # interrupt_layout.addRow(auto_section)

        tabs.addTab(interrupt_widget, "x-axis breaks")
        

        tabs.currentChanged.connect(lambda ndx: self.refresh_plot() if ndx == 1 else None)
        tabs.currentChanged.connect(lambda ndx: self.check_units() if ndx == 4 else None)

        #menu bar for saving stuff
        menu = FakeMenu()
        file = menu.addMenu("Export")
        file.addAction("Save CSV...")
        
        file.triggered.connect(self.save)
        
        self._menu = menu
        layout.setMenuBar(menu)        
        self.tool_window.ui_area.setLayout(layout)
        self.tool_window.manage(None)

    def check_units(self):
        units = self.x_units.currentText()
        if self.section_table.rowCount() > 1:
            for i in range(0, self.section_table.rowCount() - 1):
                curr_units = self.section_table.cellWidget(i, 0).suffix().strip()
                if curr_units == "nm" and units == "eV":
                    val1 = self.section_table.cellWidget(i, 0).value()
                    val1 = ValenceExcitations.nm_to_ev(val1)
                    val2 = self.section_table.cellWidget(i, 1).value()
                    val2 = ValenceExcitations.nm_to_ev(val2)
                    self.section_table.cellWidget(i, 0).setValue(val2)
                    self.section_table.cellWidget(i, 1).setValue(val1)
                    self.section_table.cellWidget(i, 0).setSingleStep(0.5)
                    self.section_table.cellWidget(i, 1).setSingleStep(0.5)
                if curr_units == "eV" and units == "nm":
                    val1 = self.section_table.cellWidget(i, 0).value()
                    val1 = ValenceExcitations.ev_to_nm(val1)
                    val2 = self.section_table.cellWidget(i, 1).value()
                    val2 = ValenceExcitations.ev_to_nm(val2)
                    self.section_table.cellWidget(i, 0).setValue(val2)
                    self.section_table.cellWidget(i, 1).setValue(val1)
                    self.section_table.cellWidget(i, 0).setSingleStep(25)
                    self.section_table.cellWidget(i, 1).setSingleStep(25)
                self.section_table.cellWidget(i, 0).setSuffix(" %s" % units)
                self.section_table.cellWidget(i, 1).setSuffix(" %s" % units)

    def add_mol_group(self, *args):
        row = self.tree.topLevelItemCount()
        
        root_item = self.tree.invisibleRootItem()
        
        mol_group = QTreeWidgetItem(root_item)
        self.tree.insertTopLevelItem(row, mol_group)

        line_widget = QWidget()
        line_widget_layout = QHBoxLayout(line_widget)
        line_widget_layout.setContentsMargins(4, 0, 4, 0)
        line_widget_layout.insertWidget(0, QLabel("show:"), 0, Qt.AlignLeft | Qt.AlignVCenter)
        show_line = QCheckBox()
        line_widget_layout.insertWidget(1, show_line, 0, Qt.AlignLeft | Qt.AlignVCenter)
        line_color = ColorButton(has_alpha_channel=False, max_size=(16, 16))
        color_ndx = (row - 1) % len(color_cycle) 
        line_color.set_color(color_cycle[color_ndx - 1])
        line_color.setEnabled(False)
        show_line.stateChanged.connect(
            lambda state, widget=line_color: widget.setEnabled(Qt.CheckState(state) == Qt.Checked)
        )
        line_widget_layout.insertWidget(2, line_color, 1, Qt.AlignLeft | Qt.AlignVCenter)
        
        line_widget2 = QWidget()
        line_widget_layout2 = QHBoxLayout(line_widget2)
        line_widget_layout2.setContentsMargins(4, 0, 4, 0)
        line_widget_layout2.insertWidget(0, QLabel("style:"), 0, Qt.AlignLeft | Qt.AlignVCenter)
        line_style = QComboBox()
        line_style.addItem(solid_line, "", "-")
        line_style.addItem(dashed_line, "", "--")
        line_style.addItem(dotted_line, "", ":")
        line_style.addItem(dashdot_line, "", "-.")
        line_style.setIconSize(QSize(50, 4))
        line_widget_layout2.insertWidget(1, line_style, 1, Qt.AlignLeft | Qt.AlignVCenter)
        line_widget2.setEnabled(False)
        show_line.stateChanged.connect(
            lambda state, widget=line_widget2: widget.setEnabled(Qt.CheckState(state) == Qt.Checked)
        )
        
        style_group = QTreeWidgetItem(mol_group)
        self.tree.setItemWidget(style_group, 0, line_widget)
        self.tree.setItemWidget(style_group, 1, line_widget2)
        
        
        trash_button = QPushButton()
        trash_button.setFlat(True)
        trash_button.clicked.connect(lambda *args, parent=mol_group: self.remove_mol_group(parent))
        trash_button.setIcon(QIcon(self.tree.style().standardIcon(QStyle.SP_DialogDiscardButton)))
        
        add_conf_button = QPushButton("add conformer")
        add_conf_button.setFlat(True)
        add_conf_button.clicked.connect(lambda *args, conf_group_widget=mol_group: self.add_conf_group(conf_group_widget))
        
        add_conf_button2 = QPushButton("")
        add_conf_button2.setFlat(True)
        add_conf_button2.clicked.connect(lambda *args, conf_group_widget=mol_group: self.add_conf_group(conf_group_widget))
        
        add_conf_button3 = QPushButton("")
        add_conf_button3.setFlat(True)
        add_conf_button3.clicked.connect(lambda *args, conf_group_widget=mol_group: self.add_conf_group(conf_group_widget))
        
        add_conf_child = QTreeWidgetItem(mol_group)
        self.tree.setItemWidget(add_conf_child, 0, add_conf_button)
        self.tree.setItemWidget(add_conf_child, 1, add_conf_button2)
        self.tree.setItemWidget(add_conf_child, 2, add_conf_button3)
        self.tree.setItemWidget(mol_group, 3, trash_button)
        
        mol_group.setText(0, "group %i" % row)
        
        mol_fraction = QDoubleSpinBox()
        mol_fraction.setDecimals(2)
        mol_fraction.setRange(0, 100)
        mol_fraction.setSingleStep(0.01)
        mol_fraction.setValue(1)
        
        mol_fraction_widget = QWidget()
        mol_fraction_layout = QFormLayout(mol_fraction_widget)
        mol_fraction_layout.setContentsMargins(4, 1, 4, 1)
        mol_fraction_layout.addRow("ratio:", mol_fraction)
        self.tree.setItemWidget(mol_group, 1, mol_fraction_widget)
        
        mol_group.addChild(add_conf_child)
        self.add_conf_group(mol_group)

        self.tree.expandItem(mol_group)
    
    def remove_mol_group(self, parent):
        for conf_ndx in range(2, parent.childCount(), 2):
            conf = parent.child(conf_ndx)
            self.tree.itemWidget(conf, 0).destroy()
            self.tree.itemWidget(conf, 1).destroy()
            self.tree.itemWidget(conf, 2).destroy()
        
        ndx = self.tree.indexOfTopLevelItem(parent)
        self.tree.takeTopLevelItem(ndx)

    def add_conf_group(self, conf_group_widget):
        row = conf_group_widget.childCount()
        
        conformer_item = QTreeWidgetItem(conf_group_widget)
        conf_group_widget.insertChild(row, conformer_item)
        
        uv_vis_combobox = FilereaderComboBox(self.session, otherItems=['uv_vis'])
        nrg_combobox = FilereaderComboBox(self.session, otherItems=['energy'])
        freq_combobox = FilereaderComboBox(self.session, otherItems=['frequency'])
        
        trash_button = QPushButton()
        trash_button.setFlat(True)
        trash_button.clicked.connect(lambda *args, combobox=uv_vis_combobox: combobox.deleteLater())
        trash_button.clicked.connect(lambda *args, combobox=nrg_combobox: combobox.deleteLater())
        trash_button.clicked.connect(lambda *args, combobox=freq_combobox: combobox.deleteLater())
        trash_button.clicked.connect(
            lambda *args, child=conformer_item: conf_group_widget.removeChild(child)
        )
        trash_button.setIcon(QIcon(self.tree.style().standardIcon(QStyle.SP_DialogCancelButton)))
        
        self.tree.setItemWidget(conformer_item, 0, uv_vis_combobox)
        self.tree.setItemWidget(conformer_item, 1, freq_combobox)
        self.tree.setItemWidget(conformer_item, 2, nrg_combobox)
        self.tree.setItemWidget(conformer_item, 3, trash_button)

        style_group = QTreeWidgetItem(conf_group_widget)
        conf_group_widget.insertChild(row + 1, style_group)

        line_widget = QWidget()
        line_widget_layout = QHBoxLayout(line_widget)
        line_widget_layout.setContentsMargins(4, 0, 4, 2)
        line_widget_layout.insertWidget(0, QLabel("show:"), 1, Qt.AlignRight | Qt.AlignVCenter)
        show_line = QCheckBox()
        line_widget_layout.insertWidget(1, show_line, 0, Qt.AlignRight | Qt.AlignVCenter)
        line_color = ColorButton(has_alpha_channel=False, max_size=(16, 16))
        color_ndx = ((row - 1)// 2) % len(color_cycle) 
        line_color.set_color(color_cycle[color_ndx])
        line_color.setEnabled(False)
        show_line.stateChanged.connect(
            lambda state, widget=line_color: widget.setEnabled(Qt.CheckState(state) == Qt.Checked)
        )
        line_widget_layout.insertWidget(2, line_color, 0, Qt.AlignRight | Qt.AlignVCenter)
        
        line_widget2 = QWidget()
        line_widget_layout2 = QHBoxLayout(line_widget2)
        line_widget_layout2.setContentsMargins(4, 0, 4, 2)
        line_widget_layout2.insertWidget(0, QLabel("style:"), 0, Qt.AlignLeft | Qt.AlignVCenter)
        line_style = QComboBox()
        line_style.addItem(dashed_line, "", "--")
        line_style.addItem(dotted_line, "", ":")
        line_style.addItem(dashdot_line, "", "-.")
        line_style.addItem(solid_line, "", "-")
        # this doesn't work for some reason
        # line_style.addItem(dashdotdot_line, "", (0, (3, 5, 1, 5, 1, 5)))
        line_style.setIconSize(QSize(50, 4))
        line_widget_layout2.insertWidget(1, line_style, 1, Qt.AlignLeft | Qt.AlignVCenter)
        line_widget2.setEnabled(False)
        show_line.stateChanged.connect(
            lambda state, widget=line_widget2: widget.setEnabled(Qt.CheckState(state) == Qt.Checked)
        )
        trash_button.clicked.connect(
            lambda *args, child=conformer_item: conf_group_widget.removeChild(style_group)
        )

        self.tree.setItemWidget(style_group, 0, line_widget)
        self.tree.setItemWidget(style_group, 1, line_widget2)

    def change_figure_size(self, *args):
        if self.fixed_size.checkState() == Qt.Checked:
            self.figure_height.setEnabled(True)
            self.figure_width.setEnabled(True)
            h = self.figure_height.value()
            w = self.figure_width.value()
            
            self.figure.set_size_inches(w, h)
            
            self.canvas.setMinimumHeight(int(96 * h))
            self.canvas.setMaximumHeight(int(96 * h))
            self.canvas.setMinimumWidth(int(96 * w))
            self.canvas.setMaximumWidth(int(96 * w))
        else:
            self.canvas.setMinimumHeight(1)
            self.canvas.setMaximumHeight(100000)
            self.canvas.setMinimumWidth(1)
            self.canvas.setMaximumWidth(100000)
            self.figure_height.setEnabled(False)
            self.figure_width.setEnabled(False)
    
    def section_table_clicked(self, row, column):
        if row == self.section_table.rowCount() - 1 or self.section_table.rowCount() == 1:
            self.add_section()
        elif column == 2:
            self.section_table.removeRow(row)
    
    def add_section(self, xmin=150.0, xmax=450.0):
        rows = self.section_table.rowCount()
        units = self.x_units.currentText()
        single_step = 25
        if units == "eV":
            x1 = ValenceExcitations.nm_to_ev(xmin)
            x2 = ValenceExcitations.nm_to_ev(xmax)
            xmax = x1
            xmin = x2
            single_step = 0.5
        if rows != 0:
            rows -= 1
            section_min = QDoubleSpinBox()
            section_min.setRange(0, 5000)
            section_min.setValue(xmin)
            section_min.setSuffix(" %s" % units)
            section_min.setSingleStep(single_step)
            self.section_table.setCellWidget(rows, 0, section_min)
            
            section_max = QDoubleSpinBox()
            section_max.setRange(1, 5000)
            section_max.setValue(xmax)
            section_max.setSuffix(" %s" % units)
            section_max.setSingleStep(single_step)
            self.section_table.setCellWidget(rows, 1, section_max)
            
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            section_remove = QLabel()
            dim = int(1.5 * section_remove.fontMetrics().boundingRect("Q").height())
            section_remove.setPixmap(QIcon(section_remove.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(dim, dim))
            widget_layout.addWidget(section_remove, 0, Qt.AlignHCenter)
            widget_layout.setContentsMargins(0, 0, 0, 0)
            self.section_table.setCellWidget(rows, 2, widget_that_lets_me_horizontally_align_an_icon)
            rows += 1

        self.section_table.insertRow(rows)

        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        section_add = QLabel("add section")
        widget_layout.addWidget(section_add, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        self.section_table.setCellWidget(rows, 1, widget_that_lets_me_horizontally_align_an_icon)
    
    def save(self):
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
        if filename:
            units = self.x_units.currentText()
            if units == "nm":
                s = "wavelenth (nm),intensity"
            else:
                s = "hv (eV),intensity"

            data = self.get_mixed_spectrum()
            if not data:
                self.session.logger.error("no data to save")
                return
            
            mixed_uv_vis, shown_confs = data
        
            for conf in shown_confs:
                s += ",%s" % conf[-1]
            s += "\n"
        
            fwhm = self.fwhm.value()
            peak_type = self.peak_type.currentText()
            plot_type = self.plot_type.currentData(Qt.UserRole)
            voigt_mixing = self.voigt_mix.value()
            shift = self.shift.value()
            intensity_attr = "oscillator_str"
            if plot_type.lower() == "uv-vis-velocity":
                intensity_attr = "oscillator_str_vel"
            elif plot_type.lower() == "transmittance-velocity":
                intensity_attr = "oscillator_str_vel"
            elif plot_type.lower() == "transmittance":
                intensity_attr = "oscillator_str"
            elif plot_type.lower() == "uv-vis":
                intensity_attr = "oscillator_str"
            elif plot_type.lower() == "ecd":
                intensity_attr = "delta_abs_len"
            elif plot_type.lower() == "ecd-velocity":
                intensity_attr = "delta_abs_vel"
            change_x_unit_func = None
            if units == "nm":
                change_x_unit_func = ValenceExcitations.ev_to_nm

            funcs, x_positions, intensities = mixed_uv_vis.get_spectrum_functions(
                fwhm=fwhm,
                peak_type=peak_type,
                voigt_mixing=voigt_mixing,
                scalar_scale=shift,
                intensity_attr=intensity_attr,
            )
            
            show_functions = None
            if shown_confs:
                show_functions = [info[0] for info in shown_confs]
            
            x_values, y_values, other_y_list = mixed_uv_vis.get_plot_data(
                funcs,
                x_positions,
                transmittance="transmittance" in plot_type,
                peak_type=peak_type,
                fwhm=fwhm,
                normalize=True,
                show_functions=show_functions,
                change_x_unit_func=change_x_unit_func,
                point_spacing=self.point_spacing.value(),
            )

            for i, (x, y) in enumerate(zip(x_values, y_values)):
                s += "%f,%f" % (x, y)
                for y_vals in other_y_list:
                    s += ",%f" % y_vals[i]
                s += "\n"

            with open(filename, 'w') as f:
                f.write(s.strip())
                
            self.session.logger.info("saved to %s" % filename)

    def zoom(self, event):
        if event.xdata is None:
            return
        for a in self.figure.get_axes():
            x0, x1 = a.get_xlim()
            x_range = x1 - x0
            xdiff = -0.05 * event.step * x_range
            xshift = 0.2 * (event.xdata - (x0 + x1)/2)
            nx0 = x0 - xdiff + xshift
            nx1 = x1 + xdiff + xshift
    
            a.set_xlim(nx0, nx1)
        self.canvas.draw()

    def drag(self, event):
        if self.toolbar.mode != "":
            return

        if event.button is not None and self.press is not None:
            x, y, xpress, ypress = self.press
            dx = event.x - x
            dy = event.y - y
            drag_dist = np.linalg.norm([dx, dy])
            if self.dragging or drag_dist >= self._min_drag or event.button == 2:
                self.dragging = True
                if self.drag_prev is not None:
                    x, y, xpress, ypress = self.drag_prev
                    dx = event.x - x
                    dy = event.y - y
                
                self.drag_prev = event.x, event.y, event.xdata, event.ydata
                self.move(dx, dy)

    def move(self, dx, dy):
        for ax in self.figure.get_axes():
            w = self.figure.get_figwidth() * self.figure.get_dpi()
            x0, x1 = self.figure.gca().get_xlim()
            xs = dx/w * (x1 - x0)
            x0, x1 = ax.get_xlim()
            nx0, nx1 = x0 - xs, x1 - xs
            #y0, y1 = ax.get_ylim()
            #ys = dy/h * (y1-y0)
            #ny0, ny1 = y0-ys, y1-ys
            ax.set_xlim(nx0, nx1)
            #ax.set_ylim(ny0, ny1)
        self.canvas.draw()

    def onclick(self, event):
        if self.toolbar.mode != "":
            return

        self.press = event.x, event.y, event.xdata, event.ydata
        
        if event.dblclick and event.xdata:
            closest = None
            for mol_ndx in range(1, self.tree.topLevelItemCount()):
                mol = self.tree.topLevelItem(mol_ndx)
                for conf_ndx in range(2, mol.childCount(), 2):
                    conf = mol.child(conf_ndx)
                    data = self.tree.itemWidget(conf, 0).currentData()
                    if data is None:
                        continue
                    fr, _ = data
                    uv_vis = fr["uv_vis"]
                    
                    data_attr = "data"
                    if self.spectra_type.currentText() == "transient":
                        data_attr = "transient_data"
                    elif self.spectra_type.currentText() == "SOC":
                        data_attr = "spin_orbit_data"
                    
                    excitations = np.array(
                        [data.excitation_energy for data in getattr(uv_vis, data_attr)]
                    )
                    c0 = self.shift.value()
                    excitations += c0
                    if self.x_units.currentText() == "nm":
                        excitations = ValenceExcitations.ev_to_nm(excitations)[0]
                    diff = np.abs(
                        event.xdata - excitations
                    )
                    min_arg = np.argmin(diff)
                    if not closest or diff[min_arg] < closest[0]:
                        closest = (diff[min_arg], getattr(uv_vis, data_attr)[min_arg], fr)
            
            if closest:
                self.highlight(closest[1], closest[2])

    def unclick(self, event):
        if self.toolbar.mode != "":
            return

        self.press = None
        self.drag_prev = None
        self.dragging = False

    def show_conformers(self):
        fracs = self.get_mixed_spectrum(weights_only=True)
        if not fracs:
            return
        fracs, weights = fracs
        min_pop = self.boltzmann_pop_limit.value() / 100.0
        
        i = 0
        for mol_ndx in range(1, self.tree.topLevelItemCount()):
            mol = self.tree.topLevelItem(mol_ndx)
            w = weights[i]
            j = 0
            for conf_ndx in range(2, mol.childCount(), 2):
                conf = mol.child(conf_ndx)
                uv_vis_file, _ = self.tree.itemWidget(conf, 0).currentData()
                if uv_vis_file is None:
                    continue
                conf_style = mol.child(conf_ndx + 1)
                show_button = self.tree.itemWidget(conf_style, 0).layout().itemAt(1).widget()
                if w[j] > min_pop:
                    show_button.setCheckState(Qt.Checked)
                    self.session.logger.info(
                        "Boltzmann population of %s: %.1f%%" % (
                            uv_vis_file["name"],
                            100 * w[j],
                        )
                    )
                else:
                    show_button.setCheckState(Qt.Unchecked)
                j += 1
            if j > 0:
                i += 1

    def get_mixed_spectrum(self, weights_only=False):
        weight_method = self.weight_method.currentData(Qt.UserRole)
        data_attr = "data"
        if self.spectra_type.currentText() == "transient":
            data_attr = "transient_data"
        elif self.spectra_type.currentText() == "SOC":
            data_attr = "spin_orbit_data"

        uv_vis_files = []
        freqs = []
        single_points = []
        mol_fracs = []
        show_components = []
        for mol_ndx in range(1, self.tree.topLevelItemCount()):
            uv_vis_files.append([])
            freqs.append([])
            single_points.append([])
            mol = self.tree.topLevelItem(mol_ndx)
            mol_fracs_widget = self.tree.itemWidget(mol, 1).layout().itemAt(1).widget()
            mol_fracs.append(mol_fracs_widget.value())

            for conf_ndx in range(2, mol.childCount(), 2):
                conf = mol.child(conf_ndx)
                data = self.tree.itemWidget(conf, 0).currentData()
                if data is None:
                    continue
                fr, mdl = data
                uv_vis = fr["uv_vis"]
                if getattr(uv_vis, data_attr) is None:
                    self.session.logger.warning("%s does not have %s data - skipping" % (
                        fr["name"], self.spectra_type.currentText(),
                    ))
                    continue
                uv_vis_files[-1].append(uv_vis)

                sp_file, _ = self.tree.itemWidget(conf, 2).currentData()
                single_points[-1].append(CompOutput(sp_file))

                if weight_method != CompOutput.ELECTRONIC_ENERGY:
                    freq_file = self.tree.itemWidget(conf, 1).currentData()
                    if freq_file is None:
                        self.session.logger.error(
                            "frequency jobs must be given if you are not weighting"
                            " based on electronic energy"
                        )
                        return
                    freq_file, _ = freq_file
                    freqs[-1].append(CompOutput(freq_file))
                
                    if single_points[-1][-1].geometry.num_atoms != freqs[-1][-1].geometry.num_atoms:
                        self.session.logger.error(
                            "different number of atoms between paired frequency file %s "
                            "and energy file %s. Structures for the energy and frequency "
                            "are expected to match, otherwise the Boltzmann weighting "
                            "of conformers will be incorrect" % (
                                single_points[-1][-1].geometry.name,
                                freqs[-1][-1].geometry.name
                            )
                        )
                        return
                
                    rmsd = freqs[-1][-1].geometry.RMSD(
                        single_points[-1][-1].geometry,
                        sort=True,
                    )
                    if rmsd > 1e-2:
                        s = "the structure of %s (frequencies) might not match" % freqs[-1][-1].geometry.name
                        s += " the structure of %s (energy)" % single_points[-1][-1].geometry.name
                        self.session.logger.warning(s)
                else:
                    freqs[-1].append(None)
                
                geom = Geometry(fr["atoms"])
                
                if single_points[-1][-1].geometry.num_atoms != geom.num_atoms:
                    self.session.logger.error(
                        "different number of atoms between paired energy file %s "
                        "and UV/vis file %s." % (
                            single_points[-1][-1].geometry.name,
                            geom.name
                        )
                    )
                    return
                
                rmsd = single_points[-1][-1].geometry.RMSD(
                    geom,
                    sort=True,
                )
                if rmsd > 1e-2:
                    s = "the structure of %s (UV/vis) might not match" % geom.name
                    s += "the structure of %s (energy)" % single_points[-1][-1].geometry.name
                    self.session.logger.warning(s)
                
                conf_style = mol.child(conf_ndx + 1)
                show_comp = self.tree.itemWidget(conf_style, 0).layout().itemAt(1).widget()
                if show_comp.checkState() == Qt.Checked:
                    stop_ndx = sum(sum(len(uv_vis.data) for uv_vis in conf) for conf in uv_vis_files)
                    start_ndx = stop_ndx - len(uv_vis_files[-1][-1].data)
                    color = self.tree.itemWidget(conf_style, 0).layout().itemAt(2).widget().get_color()
                    line_style = self.tree.itemWidget(conf_style, 1).layout().itemAt(1).widget().currentData(Qt.UserRole)
                    show_components.append([
                        (start_ndx, stop_ndx),
                        [c / 255. for c in color],
                        line_style,
                        fr["name"],
                    ])

            if not uv_vis_files[-1]:
                uv_vis_files.pop(-1)
                freqs.pop(-1)
                single_points.pop(-1)
            else:
                mol_style = mol.child(0)
                show_mol = self.tree.itemWidget(mol_style, 0).layout().itemAt(1).widget()
                if show_mol.checkState() == Qt.Checked:
                    stop_ndx = sum(sum(len(uv_vis.data) for uv_vis in conf) for conf in uv_vis_files)
                    start_ndx = stop_ndx - sum(len(f.data) for f in uv_vis_files[-1])
                    color = self.tree.itemWidget(mol_style, 0).layout().itemAt(2).widget().get_color()
                    line_style = self.tree.itemWidget(mol_style, 1).layout().itemAt(1).widget().currentData(Qt.UserRole)
                    show_components.append([
                        (start_ndx, stop_ndx),
                        [c / 255. for c in color],
                        line_style,
                        "molecule %i" % mol_ndx,
                    ])

        if not freqs or all(not conf_group for conf_group in freqs):
            return
        
        weights_list = []
        mixed_spectra = []
        for i, (uv_vis, conf_freq, conf_nrg) in enumerate(zip(uv_vis_files, freqs, single_points)):
            for j, nrg_co1 in enumerate(conf_nrg):
                for k, nrg_co2 in enumerate(conf_nrg[:j]):
                    rmsd = nrg_co1.geometry.RMSD(nrg_co2.geometry, sort=True)
                    if rmsd < 1e-2:
                        s = "%s and %s appear to be duplicate structures " % (
                                nrg_co1.geometry.name, nrg_co2.geometry.name
                            )
                        self.session.logger.warning(s)
            
            if weight_method == CompOutput.ELECTRONIC_ENERGY:
                conf_freq = conf_nrg
            
            weights = CompOutput.boltzmann_weights(
                conf_freq,
                nrg_cos=conf_nrg,
                temperature=self.temperature.value(),
                v0=self.w0.value(),
                weighting=weight_method,
            )
            weights_list.append(weights)
            
            conf_mixed = ValenceExcitations.get_mixed_signals(
                uv_vis,
                weights=weights,
                data_attr=data_attr,
            )
            mixed_spectra.append(conf_mixed)
        
        final_mixed = ValenceExcitations.get_mixed_signals(
            mixed_spectra,
            weights=np.array(mol_fracs),
        )
        
        if weights_only:
            return mol_fracs, weights_list
        return final_mixed, show_components

    def refresh_plot(self):
        if self.show_boltzmann_pop.checkState() == Qt.Checked:
            self.show_conformers()
    
        mixed_spectra = self.get_mixed_spectrum()
        if not mixed_spectra:
            return

        mixed_spectra, show_components = mixed_spectra

        self.figure.clear()
        self.check_units()
        
        temperature=self.temperature.value()
        self.settings.temperature = temperature
        w0=self.w0.value()
        self.settings.w0 = w0
        weight_method = self.weight_method.currentData(Qt.UserRole)
        self.settings.weight_method = weight_method
        plot_type = self.plot_type.currentData(Qt.UserRole)
        data_attr = "data"
        if self.spectra_type.currentText() == "transient":
            data_attr = "transient_data"
        elif self.spectra_type.currentText() == "SOC":
            data_attr = "spin_orbit_data"

        model = self.plot_type.model()
        uv_vis_vel_item = model.item(2)
        uv_vis_trans_vel_item = model.item(3)
        ecd_item = model.item(4)
        ecd_vel_item = model.item(5)
        if any(data.oscillator_str_vel is None for data in mixed_spectra.data):
            uv_vis_vel_item.setFlags(uv_vis_vel_item.flags() & ~Qt.ItemIsEnabled)
            uv_vis_trans_vel_item.setFlags(uv_vis_trans_vel_item.flags() & ~Qt.ItemIsEnabled)
        else:
            uv_vis_vel_item.setFlags(uv_vis_vel_item.flags() | Qt.ItemIsEnabled)
            uv_vis_trans_vel_item.setFlags(uv_vis_trans_vel_item.flags() | Qt.ItemIsEnabled)
        
        if any(data.rotatory_str_len is None for data in mixed_spectra.data):
            ecd_item.setFlags(ecd_item.flags() & ~Qt.ItemIsEnabled)
        else:
            ecd_item.setFlags(ecd_item.flags() | Qt.ItemIsEnabled)
        
        if any(data.rotatory_str_vel is None for data in mixed_spectra.data):
            ecd_vel_item.setFlags(ecd_vel_item.flags() & ~Qt.ItemIsEnabled)
        else:
            ecd_vel_item.setFlags(ecd_vel_item.flags() | Qt.ItemIsEnabled)

        if plot_type == "ecd":
            if not all(data.rotatory_str_len is not None for data in mixed_spectra.data):
                self.plot_type.blockSignals(True)
                self.plot_type.setCurrentIndex(0)
                self.plot_type.blockSignals(False)
        if plot_type == "ecd-velocity":
            if not all(data.rotatory_str_vel is not None for data in mixed_spectra.data):
                self.plot_type.blockSignals(True)
                self.plot_type.setCurrentIndex(0)
                self.plot_type.blockSignals(False)
        if plot_type == "uv-vis-velocity" or plot_type == "transmittance-velocity":
            if not all(data.oscillator_str_vel is not None for data in mixed_spectra.data):
                self.plot_type.blockSignals(True)
                self.plot_type.setCurrentIndex(0)
                self.plot_type.blockSignals(False)

        fwhm = self.fwhm.value()
        self.settings.fwhm = fwhm
        peak_type = self.peak_type.currentText()
        self.settings.peak_type = peak_type
        plot_type = self.plot_type.currentData(Qt.UserRole)
        self.settings.plot_type = plot_type
        voigt_mixing = self.voigt_mix.value()
        self.settings.voigt_mix = voigt_mixing
        shift = self.shift.value()
        x_units = self.x_units.currentText()
        self.settings.x_units = x_units
        point_spacing = self.point_spacing.value()
        if point_spacing is None:
            self.settings.spacing_type = "nonlinear spacing"
        else:
            self.settings.point_spacing = point_spacing
            self.settings.spacing_type = "fixed spacing"

        centers = None
        widths = None
        if self.section_table.rowCount() > 1:
            centers = []
            widths = []
            for i in range(0, self.section_table.rowCount() - 1):
                xmin = self.section_table.cellWidget(i, 0).value()
                xmax = self.section_table.cellWidget(i, 1).value()
                centers.append((xmin + xmax) / 2)
                widths.append(abs(xmin - xmax))

        mixed_spectra.plot_uv_vis(
            self.figure,
            centers=centers,
            widths=widths,
            exp_data=self.exp_data,
            plot_type=plot_type,
            peak_type=peak_type,
            fwhm=fwhm,
            voigt_mixing=voigt_mixing,
            scalar_scale=shift,
            units=x_units,
            show_functions=show_components,
            normalize=True,
            point_spacing=point_spacing,
        )

        self.canvas.draw()
        if self.highlighted_mode:
            mode = self.highlighted_mode
            self.highlighted_mode = None
            self.highlight(mode, self.highlight_frs)

    def highlight(self, item, fr):
        highlights = []
        labels = []

        excits = self.get_mixed_spectrum()
        if not excits:
            return
        
        excits, _ = excits

        plot_type = self.plot_type.currentText()
        shift = self.shift.value()
        
        for ax in self.figure.get_axes():
            for i, mode in enumerate(ax.collections):
                if mode in self.highlighted_lines:
                    self.highlighted_lines.remove(mode)
                    ax.collections[i].remove()
                    break
            
            for text in ax.texts:
                text.remove()

            if item is self.highlighted_mode:
                continue
                
            for excit in excits.data:
                if excit.excitation_energy == item.excitation_energy:
                    break
            else:
                continue

            nrg = excit.excitation_energy + shift
            use_nm = self.x_units.currentText() == "nm"
            if use_nm:
                nrg = ValenceExcitations.ev_to_nm(nrg)
            
            if "transmittance" in plot_type:
                y_vals = (10 ** (2 - 0.9), 100)
            elif plot_type == "ECD":
                y_vals = (0, np.sign(item.rotatory_str_len))
            elif plot_type == "ECD (dipole velocity)":
                y_vals = (0, np.sign(item.rotatory_str_vel))
            else:
                y_vals = (0, 1)
            
            if plot_type == "UV/vis":
                y_rel = excit.oscillator_str / item.oscillator_str
            elif plot_type == "UV/vis (dipole velocity)":
                y_rel = excit.oscillator_str_vel / item.oscillator_str_vel
            elif plot_type == "UV/vis transmittance":
                y_rel = excit.oscillator_str / item.oscillator_str
            elif plot_type == "UV/vis transmittance (dipole velocity)":
                y_rel = excit.oscillator_str_vel / item.oscillator_str_vel
            elif plot_type == "ECD":
                y_rel = excit.rotatory_str_len / item.rotatory_str_len
            elif plot_type == "ECD (dipole velocity)":
                y_rel = excit.rotatory_str_vel / item.rotatory_str_vel
       
            label = "%s" % fr["name"]
            label += "\n%.2f %s" % (nrg, "nm" if use_nm else "eV")
            if shift:
                if use_nm:
                    delta = nrg - ValenceExcitations.ev_to_nm(item.excitation_energy)
                else:
                    delta = nrg - item.excitation_energy
                label += "\n$\Delta_{corr}$ = %.2f %s" % (delta, "nm" if use_nm else "eV")
            label += "\nintensity scaled by %.2e" % y_rel
            
            if nrg < min(ax.get_xlim()) or nrg > max(ax.get_xlim()):
                continue
            
            x_mid = nrg < sum(ax.get_xlim()) / 2
            label_x = nrg
            if x_mid:
                label_x += 0.01 * sum(ax.get_xlim())
            else:
                label_x -= 0.01 * sum(ax.get_xlim())
            
            labels.append(
                ax.text(
                    label_x,
                    y_vals[1] / len(label.splitlines()),
                    label,
                    va="bottom" if y_vals[1] > 0 else "top",
                    ha="left" if x_mid else "right",
                    path_effects=[pe.withStroke(linewidth=2, foreground="white")],
                )
            )
            
            highlights.append(
                ax.vlines(
                    nrg, *y_vals, color='r', zorder=-1, label="highlight"
                )
            )
        
        if item is not self.highlighted_mode:
            self.highlighted_mode = item
            self.highlight_frs = fr
        else:
            self.highlighted_mode = None
            self.highlight_frs = None

        self.highlighted_lines = highlights
        self.highlighted_labels = labels
        self.canvas.draw()

    def load_data(self, *args):
        filename, _ = QFileDialog.getOpenFileName(filter="comma-separated values file (*.csv)")

        if not filename:
            return

        data = np.loadtxt(filename, delimiter=",", skiprows=self.skip_lines.value())

        color = self.line_color.get_color()
        self.settings.exp_color = tuple([c / 255. for c in color[:-1]])
        
        # figure out hex code for specified color 
        # color is RGBA tuple with values from 0 to 255
        # python's hex turns that to base 16 (0 to ff)
        # if value is < 16, there will only be one digit, so pad with 0
        hex_code = "#"
        for x in color[:-1]:
            channel = str(hex(x))[2:]
            if len(channel) == 1:
                channel = "0" + channel
            hex_code += channel

        if self.exp_data is None:
            self.exp_data = []

        for i in range(1, data.shape[1]):
            self.exp_data.append((data[:,0], data[:,i], hex_code))

    def clear_data(self, *args):
        self.exp_data = None

    def cleanup(self):
        self.settings.figure_height = self.figure_height.value()
        self.settings.figure_width = self.figure_width.value()
        self.settings.fixed_size = self.fixed_size.checkState() == Qt.Checked
        self.settings.col_1 = self.tree.columnWidth(0)
        self.settings.col_2 = self.tree.columnWidth(1)
        self.settings.col_3 = self.tree.columnWidth(2)

        for mol_index in range(1, self.tree.topLevelItemCount()):
            mol = self.tree.topLevelItem(mol_index)
            for conf_ndx in range(2, mol.childCount(), 2):
                conf = mol.child(conf_ndx)
                self.tree.itemWidget(conf, 0).deleteLater()
                self.tree.itemWidget(conf, 1).deleteLater()
                self.tree.itemWidget(conf, 2).deleteLater()

        super().cleanup()

    def close(self):
        self.settings.figure_height = self.figure_height.value()
        self.settings.figure_width = self.figure_width.value()
        self.settings.fixed_size = self.fixed_size.checkState() == Qt.Checked
        self.settings.col_1 = self.tree.columnWidth(0)
        self.settings.col_2 = self.tree.columnWidth(1)
        self.settings.col_3 = self.tree.columnWidth(2)

        for mol_index in range(1, self.tree.topLevelItemCount()):
            mol = self.tree.topLevelItem(mol_index)
            for conf_ndx in range(2, mol.childCount(), 2):
                conf = mol.child(conf_ndx)
                self.tree.itemWidget(conf, 0).deleteLater()
                self.tree.itemWidget(conf, 1).deleteLater()
                self.tree.itemWidget(conf, 2).deleteLater()

        super().close()

    def delete(self):
        self.settings.figure_height = self.figure_height.value()
        self.settings.figure_width = self.figure_width.value()
        self.settings.fixed_size = self.fixed_size.checkState() == Qt.Checked
        self.settings.col_1 = self.tree.columnWidth(0)
        self.settings.col_2 = self.tree.columnWidth(1)
        self.settings.col_3 = self.tree.columnWidth(2)

        for mol_index in range(1, self.tree.topLevelItemCount()):
            mol = self.tree.topLevelItem(mol_index)
            for conf_ndx in range(2, mol.childCount(), 2):
                conf = mol.child(conf_ndx)
                self.tree.itemWidget(conf, 0).deleteLater()
                self.tree.itemWidget(conf, 1).deleteLater()
                self.tree.itemWidget(conf, 2).deleteLater()

        super().delete()

    def fill_context_menu(self, menu, x, y):
        fixed_size = QAction("fixed size", menu, checkable=True)
        fixed_size.setChecked(self.fixed_size.isChecked())
        fixed_size.triggered.connect(lambda checked: self.fixed_size.setChecked(checked))
        fixed_size.triggered.connect(lambda checked: self.tool_window.shrink_to_fit())
        menu.addAction(fixed_size)