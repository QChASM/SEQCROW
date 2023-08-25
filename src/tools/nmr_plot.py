from json import loads, dumps
import re

import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.ui.widgets import ColorButton
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import FloatArg, TupleOf, IntArg
from chimerax.core.commands import run

from AaronTools.comp_output import CompOutput
from AaronTools.const import NMR_SCALE_LIBS, ELEMENTS, COMMONLY_ODD_ISOTOPES
from AaronTools.geometry import Geometry
from AaronTools.spectra import NMR, Shift

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from matplotlib import rcParams
import matplotlib.patheffects as pe

from Qt.QtCore import Qt, QSize
from Qt.QtGui import QIcon
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
    QGroupBox,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QTreeWidget,
    QSizePolicy,
    QTreeWidgetItem,
)

from SEQCROW.tools.per_frame_plot import NavigationToolbar
from SEQCROW.tools.uvvis_plot import (
    solid_line,
    dashed_line, 
    dotted_line,
    dashdot_line,
    color_cycle,
)
    
from SEQCROW.utils import iter2str
from SEQCROW.widgets import FilereaderComboBox, FakeMenu, ScientificSpinBox, ElementButton


rcParams["savefig.dpi"] = 300



class _NMRSpectrumSettings(Settings):
    AUTO_SAVE = {
        'fwhm': Value(2.5, FloatArg), 
        'peak_type': 'Lorentzian', 
        'voigt_mix': 0.5,
        'exp_color': Value((0.0, 0.0, 1.0), TupleOf(FloatArg, 3), iter2str),
        'reverse_x': True,
        'figure_width': 5,
        'figure_height': 3.5,
        "fixed_size": False,
        "scales": "{}",
        "version": 0,
        'w0': 100,
        'temperature': 298.15,
        "weight_method": "QRRHO",
        'col_1': Value(150, IntArg), 
        'col_2': Value(150, IntArg), 
        'col_3': Value(150, IntArg), 
        "pulse_frequency": 90.0,
}


class NMRSpectrum(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False
    
    def __init__(self, session, name):
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)        

        self.settings = _NMRSpectrumSettings(session, name)
        if self.settings.version == 0:
            self.update_scales()
            self.settings.version = 1

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

    def _build_ui(self):
        layout = QGridLayout()
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["NMR file", "frequency file", "energy file", "remove"])
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
        self.tree.setColumnWidth(2, self.settings.col_3)
        
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

        # show_conformers = QLabel("show contribution from conformers with a Boltzmann population above:")
        # component_layout.addWidget(show_conformers, 2, 0, 1, 4, Qt.AlignRight | Qt.AlignVCenter)
        # 
        # self.boltzmann_pop_limit = QDoubleSpinBox()
        # self.boltzmann_pop_limit.setRange(1.0, 99.0)
        # self.boltzmann_pop_limit.setSingleStep(1.0)
        # self.boltzmann_pop_limit.setDecimals(1)
        # self.boltzmann_pop_limit.setValue(10.0)
        # self.boltzmann_pop_limit.setSuffix("%")
        # component_layout.addWidget(self.boltzmann_pop_limit, 2, 4, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)
        # 
        # self.show_boltzmann_pop = QCheckBox()
        # component_layout.addWidget(self.show_boltzmann_pop, 2, 5, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)


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

        plot_layout.addWidget(self.canvas, 0, 0, 1, 7)

        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon(refresh_button.style().standardIcon(QStyle.SP_BrowserReload)))
        refresh_button.clicked.connect(self.refresh_plot)
        plot_layout.addWidget(refresh_button, 1, 0, 1, 1, Qt.AlignVCenter)

        toolbar_widget = QWidget()
        self.toolbar = NavigationToolbar(self.canvas, toolbar_widget)
        self.toolbar.setMaximumHeight(32)
        plot_layout.addWidget(self.toolbar, 1, 1, 1, 1)

        plot_layout.addWidget(QLabel("fixed size:"), 1, 2, 1, 1, Qt.AlignVCenter | Qt.AlignRight)

        self.fixed_size = QCheckBox()
        self.fixed_size.setCheckState(Qt.Checked if self.settings.fixed_size else Qt.Unchecked)
        self.fixed_size.stateChanged.connect(self.change_figure_size)
        plot_layout.addWidget(self.fixed_size, 1, 3, 1, 1, Qt.AlignVCenter | Qt.AlignLeft)

        self.figure_width = QDoubleSpinBox()
        self.figure_width.setRange(1, 24)
        self.figure_width.setDecimals(2)
        self.figure_width.setSingleStep(0.25)
        self.figure_width.setSuffix(" in.")
        self.figure_width.setValue(self.settings.figure_width)
        self.figure_width.valueChanged.connect(self.change_figure_size)
        plot_layout.addWidget(self.figure_width, 1, 4, 1, 1)
     
        plot_layout.addWidget(QLabel("x"), 1, 5, 1, 1, Qt.AlignVCenter | Qt.AlignHCenter)
     
        self.figure_height = QDoubleSpinBox()
        self.figure_height.setRange(1, 24)
        self.figure_height.setDecimals(2)
        self.figure_height.setSingleStep(0.25)
        self.figure_height.setSuffix(" in.")
        self.figure_height.setValue(self.settings.figure_height)
        self.figure_height.valueChanged.connect(self.change_figure_size)
        plot_layout.addWidget(self.figure_height, 1, 6, 1, 1)

        self.change_figure_size()

        plot_layout.setRowStretch(0, 1)
        plot_layout.setRowStretch(1, 0)
        
        tabs.addTab(plot_widget, "plot")

        # peak style
        plot_settings_widget = QWidget()
        plot_settings_layout = QFormLayout(plot_settings_widget)

        self.peak_type = QComboBox()
        self.peak_type.addItems(['Gaussian', 'Lorentzian', 'pseudo-Voigt'])
        ndx = self.peak_type.findText(self.settings.peak_type, Qt.MatchExactly)
        self.peak_type.setCurrentIndex(ndx)
        plot_settings_layout.addRow("peak type:", self.peak_type)
        
        self.fwhm = QDoubleSpinBox()
        self.fwhm.setSingleStep(0.25)
        self.fwhm.setRange(0.01, 200.0)
        self.fwhm.setSuffix(" Hz")
        self.fwhm.setValue(self.settings.fwhm)
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
        
        self.pulse_frequency = QDoubleSpinBox()
        self.pulse_frequency.setMinimum(1.0)
        self.pulse_frequency.setMaximum(10000.0)
        self.pulse_frequency.setSuffix(" MHz")
        self.pulse_frequency.setValue(self.settings.pulse_frequency)
        self.pulse_frequency.setSingleStep(10)
        plot_settings_layout.addRow("pulse frequency:", self.pulse_frequency)
        
        self.reverse_x = QCheckBox()
        self.reverse_x.setCheckState(Qt.Checked)
        plot_settings_layout.addRow("reverse x-axis:", self.reverse_x)
        
        self.elements = QHBoxLayout()
        plot_settings_layout.addRow("elements:", self.elements)
        
        self.couple_with = QHBoxLayout()
        plot_settings_layout.addRow("couple with:", self.couple_with)
        
        
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
        
        
        # frequency scaling
        scaling_group = QWidget()
        scaling_layout = QFormLayout(scaling_group)
        
        desc = QLabel("")
        desc.setText("<a href=\"test\" style=\"text-decoration: none;\">&#x1D6FF;' = &#x1D6FF;<sub>ref</sub> + &#x1D6FC; &times; &#x1D6FF;<sub>0</sub></a>")
        desc.setTextFormat(Qt.RichText)
        desc.setTextInteractionFlags(Qt.TextBrowserInteraction)
        desc.linkActivated.connect(self.open_link)
        desc.setToolTip("")
        scaling_layout.addRow(desc)

        self.scalar = QDoubleSpinBox()
        self.scalar.setMinimum(-100)
        self.scalar.setMaximum(100)
        self.scalar.setDecimals(4)
        self.scalar.setSingleStep(0.025)
        self.scalar.setValue(32)
        scaling_layout.addRow("&#x1D6FF;<sub>ref</sub> =", self.scalar)
        
        self.linear = QDoubleSpinBox()
        self.linear.setMaximum(2)
        self.linear.setMinimum(-2)
        self.linear.setDecimals(4)
        self.linear.setSingleStep(0.025)
        self.linear.setValue(-1.0)
        scaling_layout.addRow("α =", self.linear)

        save_scales = QPushButton("save current scale factors...")
        save_scales.clicked.connect(self.open_save_scales)
        scaling_layout.addRow(save_scales)
        
        set_zero = QPushButton("set scales to α = -1, reference δ = 0")
        set_zero.clicked.connect(lambda *args: self.linear.setValue(-1.0))
        set_zero.clicked.connect(lambda *args: self.scalar.setValue(0.))
        scaling_layout.addRow(set_zero)
        
        
        lookup_scale = QGroupBox("scale factor lookup")
        scaling_layout.addRow(lookup_scale)
        lookup_layout = QFormLayout(lookup_scale)
        
        self.library = QComboBox()
        lookup_layout.addRow("database:", self.library)
        
        self.method = QComboBox()
        lookup_layout.addRow("NMR method:", self.method)
        
        self.basis = QComboBox()
        lookup_layout.addRow("structure opt. method:", self.basis)
        
        self.fill_lib_options()
        
        desc = QLabel("")
        desc.setText("view database online <a href=\"test\" style=\"text-decoration: none;\">here</a>")
        desc.setTextFormat(Qt.RichText)
        desc.setTextInteractionFlags(Qt.TextBrowserInteraction)
        desc.linkActivated.connect(self.open_scale_library_link)
        desc.setToolTip("view library online")
        lookup_layout.addRow(desc)

        self.library.currentTextChanged.connect(self.change_scale_lib)
        self.method.currentTextChanged.connect(self.change_method)
        self.basis.currentTextChanged.connect(self.change_basis)

        # fit_scale = QGroupBox("linear least squares fitting")
        # scaling_layout.addRow(fit_scale)
        # fit_layout = QFormLayout(fit_scale)
        # 
        # self.fit_c1 = QCheckBox()
        # fit_layout.addRow("fit c<sub>1</sub>:", self.fit_c1)
        # 
        # self.fit_c2 = QCheckBox()
        # fit_layout.addRow("fit c<sub>2</sub>:", self.fit_c2)
        
        tabs.addTab(scaling_group, "shift scaling")
        
        
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
        tabs.currentChanged.connect(lambda ndx: self.set_available_elements() if ndx == 2 else None)
        tabs.currentChanged.connect(lambda ndx: self.set_coupling() if ndx == 2 else None)

        #menu bar for saving stuff
        menu = FakeMenu()
        file = menu.addMenu("Export")
        file.addAction("Save CSV...")
        
        file.triggered.connect(self.save)
        
        self._menu = menu
        layout.setMenuBar(menu)        
        self.tool_window.ui_area.setLayout(layout)
        self.tool_window.manage(None)

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
        
        add_conf_child = QTreeWidgetItem(mol_group)
        self.tree.setItemWidget(add_conf_child, 0, add_conf_button)
        self.tree.setItemWidget(add_conf_child, 1, add_conf_button2)
        self.tree.setItemWidget(mol_group, 2, trash_button)
        
        mol_group.setText(0, "group %i" % row)
        
        mol_fraction = QDoubleSpinBox()
        mol_fraction.setDecimals(2)
        mol_fraction.setRange(0, 100)
        mol_fraction.setSingleStep(0.01)
        mol_fraction.setValue(1)
        
        mol_fraction_widget = QWidget()
        mol_fraction_layout = QFormLayout(mol_fraction_widget)
        mol_fraction_layout.addRow("ratio:", mol_fraction)
        mol_fraction_layout.setContentsMargins(4, 1, 4, 1)
        self.tree.setItemWidget(mol_group, 1, mol_fraction_widget)
        
        mol_group.addChild(add_conf_child)
        self.add_conf_group(mol_group)

        self.tree.expandItem(mol_group)
    
    def remove_mol_group(self, parent):
        for conf_ndx in range(2, parent.childCount(), 2):
            conf = parent.child(conf_ndx)
            self.tree.itemWidget(conf, 0).destroy()
            self.tree.itemWidget(conf, 1).destroy()
        
        ndx = self.tree.indexOfTopLevelItem(parent)
        self.tree.takeTopLevelItem(ndx)

    def add_conf_group(self, conf_group_widget):
        row = conf_group_widget.childCount()
        
        conformer_item = QTreeWidgetItem(conf_group_widget)
        conf_group_widget.insertChild(row, conformer_item)
        
        nrg_combobox = FilereaderComboBox(self.session, otherItems=['energy'])
        freq_combobox = FilereaderComboBox(self.session, otherItems=['frequency'])
        nmr_combobox = FilereaderComboBox(self.session, otherItems=['nmr'])
        
        trash_button = QPushButton()
        trash_button.setFlat(True)
        trash_button.clicked.connect(lambda *args, combobox=nrg_combobox: combobox.deleteLater())
        trash_button.clicked.connect(lambda *args, combobox=freq_combobox: combobox.deleteLater())
        trash_button.clicked.connect(lambda *args, child=conformer_item: conf_group_widget.removeChild(child))
        trash_button.setIcon(QIcon(self.tree.style().standardIcon(QStyle.SP_DialogCancelButton)))
        
        self.tree.setItemWidget(conformer_item, 0, nmr_combobox)
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

    def fill_lib_options(self):
        cur_lib = self.library.currentIndex()
        cur_method = self.method.currentText()
        cur_basis = self.basis.currentText()
        self.library.blockSignals(True)
        self.method.blockSignals(True)
        self.basis.blockSignals(True)
        self.library.clear()
        self.method.clear()
        self.basis.clear()
        lib_names = list(NMR_SCALE_LIBS.keys())
        user_def = loads(self.settings.scales)
        if user_def:
            lib_names.append("user-defined")
        
        self.library.addItems(lib_names)
        if cur_lib >= 0:
            self.library.setCurrentIndex(cur_lib)

        if self.library.currentText() != "user-defined":
            self.method.addItems(
                NMR_SCALE_LIBS[self.library.currentText()][1].keys()
            )

            self.basis.addItems(
                NMR_SCALE_LIBS[lib_names[0]][1][self.method.currentText()].keys()
            )

        else:
            user_def = loads(self.settings.scales)
            self.method.addItems(user_def.keys())
            ndx = self.method.findText(cur_method, Qt.MatchExactly)
        
        ndx = self.method.findText(cur_method, Qt.MatchExactly)
        if ndx >= 0:
            self.method.setCurrentIndex(ndx)

        ndx = self.basis.findText(cur_basis, Qt.MatchExactly)
        if ndx >= 0:
            self.basis.setCurrentIndex(ndx)
        
        self.library.blockSignals(False)
        self.method.blockSignals(False)
        self.basis.blockSignals(False)

    def update_scales(self):
        from SEQCROW.tools.normal_modes import _NormalModeSettings
        normal_mode_settings = _NormalModeSettings(self.session, "Visualize Normal Modes")
        self.settings.scales = normal_mode_settings.scales

    def open_save_scales(self):
        m = self.linear.value()
        b = self.scalar.value()
        self.tool_window.create_child_window(
            "saving shift scales",
            window_class=SaveScales,
            m=m,
            b=b,
        )

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
    
    def add_section(self, xmin=0, xmax=11):
        rows = self.section_table.rowCount()
        if rows != 0:
            rows -= 1
            section_min = QDoubleSpinBox()
            section_min.setRange(0, 500)
            section_min.setValue(xmin)
            section_min.setSuffix(" ppm")
            section_min.setSingleStep(25)
            self.section_table.setCellWidget(rows, 0, section_min)
            
            section_max = QDoubleSpinBox()
            section_max.setRange(1, 500)
            section_max.setValue(xmax)
            section_max.setSuffix(" ppm")
            section_max.setSingleStep(25)
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
            s = "shift (ppm),intensity"

            mixed_nmr = self.get_mixed_spectrum()
            if not mixed_nmr:
                return
            
            mixed_nmr, shown_confs = mixed_nmr
        
            for conf in shown_confs:
                s += ",%s" % conf[-1]
            s += "\n"
        
            fwhm = self.fwhm.value()
            peak_type = self.peak_type.currentText()
            plot_type = self.plot_type.currentText()
            voigt_mixing = self.voigt_mix.value()
            linear = self.linear.value()
            scalar = self.scalar.value()

            funcs, x_positions, intensities = mixed_nmr.get_spectrum_functions(
                fwhm=fwhm,
                peak_type=peak_type,
                voigt_mixing=voigt_mixing,
                linear_scale=linear,
                scalar_scale=scalar,
            )
            
            show_functions = None
            if shown_confs:
                show_functions = [info[0] for info in shown_confs]
            
            x_values, y_values, other_y_list = mixed_nmr.get_plot_data(
                funcs,
                x_positions,
                transmittance="transmittance" in plot_type.lower(),
                peak_type=peak_type,
                fwhm=fwhm,
                show_functions=show_functions,
                normalize=False,
            )
                
            for i, (x, y) in enumerate(zip(x_values, y_values)):
                s += "%f,%f" % (x, y)
                for y_vals in other_y_list:
                    s += ",%f" % y_vals[i]
                s += "\n"

            with open(filename, 'w') as f:
                f.write(s.strip())
                
            self.session.logger.info("saved to %s" % filename)

    def open_link(self, *args):
        """open CHESHIRE CCAT site on scaling NMR shifts"""
        run(self.session, "open http://cheshirenmr.info/index.htm")

    def open_scale_library_link(self, *args):
        if self.library.currentText() != "user-defined":
            run(self.session, "open %s" % NMR_SCALE_LIBS[self.library.currentText()][0])
        else:
            self.session.logger.info("that's your database")

    def change_scale_lib(self, lib):
        cur_method = self.method.currentText()
        cur_basis = self.basis.currentText()
        self.prev_basis = self.basis.currentText()
        self.method.blockSignals(True)
        self.method.clear()
        self.method.blockSignals(False)
        if lib in NMR_SCALE_LIBS:
            self.basis.setEnabled(True)
            self.method.addItems(NMR_SCALE_LIBS[lib][1].keys())
            ndx = self.method.findText(cur_method, Qt.MatchExactly)
            if ndx >= 0:
                self.method.setCurrentIndex(ndx)
            
            ndx = self.basis.findText(cur_basis, Qt.MatchExactly)
            if ndx >= 0:
                self.basis.setCurrentIndex(ndx)
        else:
            self.basis.setEnabled(False)
            user_def = loads(self.settings.scales)
            self.method.addItems(user_def.keys())
    
    def change_method(self, method):
        cur_basis = self.basis.currentText()
        self.basis.blockSignals(True)
        self.basis.clear()
        self.basis.blockSignals(False)
        if self.library.currentText() in NMR_SCALE_LIBS:
            if isinstance(NMR_SCALE_LIBS[self.library.currentText()][1][method], dict):
                self.basis.addItems(
                    NMR_SCALE_LIBS[self.library.currentText()][1][method].keys()
                )
                ndx = self.basis.findText(cur_basis, Qt.MatchExactly)
                if ndx >= 0:
                    self.basis.setCurrentIndex(ndx)
            else:
                slope, intercept = NMR_SCALE_LIBS[self.library.currentText()][1][method]
                self.linear.setValue(slope)
                self.quadratic.setValue(intercept)
        elif method:
            user_def = loads(self.settings.scales)
            m, b = user_def[method]
            self.linear.setValue(m)
            self.scalar.setValue(b)

    def change_basis(self, basis):
        slope, intercept = NMR_SCALE_LIBS[self.library.currentText()][1][self.method.currentText()][basis]
        self.linear.setValue(slope)
        self.scalar.setValue(intercept)

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
        raise NotImplementedError
        if self.toolbar.mode != "":
            return

        self.press = event.x, event.y, event.xdata, event.ydata
        
        if event.dblclick and event.xdata:
            anharmonic = self.anharmonic.checkState() == Qt.Checked
            data_attr = "data"
            if anharmonic:
                data_attr = "anharm_data"
            closest = None
            for mol_ndx in range(1, self.tree.topLevelItemCount()):
                mol = self.tree.topLevelItem(mol_ndx)
                for conf_ndx in range(2, mol.childCount(), 2):
                    conf = mol.child(conf_ndx)
                    data = self.tree.itemWidget(conf, 0).currentData()
                    if data is None:
                        continue
                    fr, _ = data
                    freq = fr["frequency"]
                    if anharmonic and not freq.anharm_data:
                        self.session.logger.error(
                            "anharmonic frequencies requested on the 'plot settings' "
                            "tab, but anharmonic data was not parsed from %s" % fr["name"]
                        )
                        return
                    
                    data_list = getattr(freq, data_attr)
                    data_list = [data for data in data_list if data.frequency > 0]
                    frequencies = np.array([data.frequency for data in data_list])
                    c1 = self.linear.value()
                    c2 = self.quadratic.value()
                    frequencies -= c1 * frequencies + c2 * frequencies ** 2
                    diff = np.abs(
                        event.xdata - frequencies
                    )
                    min_arg = np.argmin(diff)
                    if not closest or diff[min_arg] < closest[0]:
                        closest = (diff[min_arg], data_list[min_arg], fr)
            
            if closest:
                self.highlight(closest[1], closest[2])

    def unclick(self, event):
        if self.toolbar.mode != "":
            return

        self.press = None
        self.drag_prev = None
        self.dragging = False

    # def show_conformers(self):
    #     fracs = self.get_mixed_spectrum(weights_only=True)
    #     if not fracs:
    #         return
    #     fracs, weights = fracs
    #     min_pop = self.boltzmann_pop_limit.value() / 100.0
    #     
    #     i = 0
    #     for mol_ndx in range(1, self.tree.topLevelItemCount()):
    #         mol = self.tree.topLevelItem(mol_ndx)
    #         w = weights[i]
    #         j = 0
    #         for conf_ndx in range(2, mol.childCount(), 2):
    #             conf = mol.child(conf_ndx)
    #             data = self.tree.itemWidget(conf, 0).currentData()
    #             if data is None:
    #                 continue
    #             fr, _ = data
    #             conf_style = mol.child(conf_ndx + 1)
    #             show_button = self.tree.itemWidget(conf_style, 0).layout().itemAt(1).widget()
    #             if w[j] > min_pop:
    #                 show_button.setCheckState(Qt.Checked)
    #                 self.session.logger.info(
    #                     "Boltzmann population of %s: %.1f%%" % (
    #                         fr["name"],
    #                         100 * w[j],
    #                     )
    #                 )
    #             else:
    #                 show_button.setCheckState(Qt.Unchecked)
    #             j += 1
    #         if j > 0:
    #             i += 1

    def get_mixed_spectrum(self, weights_only=False):
        weight_method = self.weight_method.currentData(Qt.UserRole)
        nmrs = []
        freqs = []
        single_points = []
        mol_fracs = []
        show_components = []
        data_attr = "data"
        for mol_ndx in range(1, self.tree.topLevelItemCount()):
            nmrs.append([])
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
                nmrs[-1].append(fr["nmr"])

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
                    start_ndx = stop_ndx - len(nmrs[-1][-1].data)
                    color = self.tree.itemWidget(conf_style, 0).layout().itemAt(2).widget().get_color()
                    line_style = self.tree.itemWidget(conf_style, 1).layout().itemAt(1).widget().currentData(Qt.UserRole)
                    show_components.append([
                        (start_ndx, stop_ndx),
                        [c / 255. for c in color],
                        line_style,
                        fr["name"],
                    ])

            if not nmrs[-1]:
                nmrs.pop(-1)
                geoms.pop(-1)
                freqs.pop(-1)
                single_points.pop(-1)
            else:
                mol_style = mol.child(0)
                show_mol = self.tree.itemWidget(mol_style, 0).layout().itemAt(1).widget()
                if show_mol.checkState() == Qt.Checked:
                    stop_ndx = sum(sum(len(uv_vis.data) for uv_vis in conf) for conf in uv_vis_files)
                    start_ndx = stop_ndx - sum(len(f.data) for f in nmrs[-1])
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
        mixed_nmrs = []
        for i, (conf_freq, conf_nrg) in enumerate(zip(freqs, single_points)):
            # for j, freq1 in enumerate(conf_freq):
            #     for k, freq2 in enumerate(conf_freq[:j]):
            #         rmsd = freq1.geometry.RMSD(freq2.geometry, sort=True)
            #         if rmsd < 1e-2:
            #             s = "%s and %s appear to be duplicate structures " % (
            #                     freq1.geometry.name, freq2.geometry.name
            #                 )
            #             self.session.logger.warning(s)
            weights = CompOutput.boltzmann_weights(
                conf_freq,
                nrg_cos=conf_nrg,
                temperature=self.temperature.value(),
                v0=self.w0.value(),
                weighting=weight_method,
            )
            weights_list.append(weights)

            conf_mixed = NMR.get_mixed_signals(
                nmrs[i],
                weights=weights,
                data_attr=data_attr,
            )
            mixed_nmrs.append(conf_mixed)

        data = []
        coupling = {}
        for i, (mol_frac, nmr) in enumerate(zip(mol_fracs, mixed_nmrs)):
            offset = len(data)
            data.extend([
                Shift(
                    shift.shift,
                    intensity=(mol_frac * shift.intensity),
                    element=shift.element,
                    ndx=i + shift.ndx,
                ) for shift in nmr.data
            ])
            for i in nmr.coupling:
                coupling[i] = {}
                for j in nmr.coupling[i]:
                    coupling[i + offset][j + offset] = nmr.coupling[i][j]
        print("final mixed", data)
        print("final coupling", coupling)
        final_mixed = NMR(data)
        final_mixed.coupling = coupling
        
        if weights_only:
            return mol_fracs, weights_list
        return final_mixed, show_components

    def set_available_elements(self):
        elements = set()
        data_attr = "data"
        for mol_ndx in range(1, self.tree.topLevelItemCount()):
            mol = self.tree.topLevelItem(mol_ndx)

            for conf_ndx in range(2, mol.childCount(), 2):
                conf = mol.child(conf_ndx)
                data = self.tree.itemWidget(conf, 0).currentData()
                if data is None:
                    continue
                fr, mdl = data
                nmr = fr["nmr"]
                elements.update([shift.element for shift in getattr(nmr, data_attr)])


        previous_eles = {}
        while (item := self.elements.takeAt(0)) is not None:
            button = item.widget()
            if button is None:
                del item
                continue
            previous_eles[button.text()] = button.state == ElementButton.Checked
            button.deleteLater()
            del item
        
        elements = sorted([e for e in elements if e in ELEMENTS], key=ELEMENTS.index)
        for i, ele in enumerate(elements):
            ele_button = ElementButton(ele)
            try:
                checked = previous_eles[ele]
                if checked:
                    ele_button.setState(ElementButton.Checked)
                else:
                    ele_button.setState(ElementButton.Unchecked)
            except KeyError:
                if ele in COMMONLY_ODD_ISOTOPES:
                    ele_button.setState(ElementButton.Checked)
                else:
                    ele_button.setState(ElementButton.Unchecked)
            self.elements.addWidget(ele_button, stretch=0)
        self.elements.addStretch(1)

    def set_coupling(self):
        elements = set()
        data_attr = "data"
        for mol_ndx in range(1, self.tree.topLevelItemCount()):
            mol = self.tree.topLevelItem(mol_ndx)

            for conf_ndx in range(2, mol.childCount(), 2):
                conf = mol.child(conf_ndx)
                data = self.tree.itemWidget(conf, 0).currentData()
                if data is None:
                    continue
                fr, mdl = data
                nmr = fr["nmr"]
                for shift in getattr(nmr, data_attr):
                    try:
                        for j in nmr.coupling[shift.ndx]:
                            j_shift = [shift for shift in getattr(nmr, data_attr) if shift.ndx == j][0]
                            elements.add(j_shift.element)
                    except KeyError:
                        pass

        previous_eles = {}
        while (item := self.couple_with.takeAt(0)) is not None:
            button = item.widget()
            if button is None:
                del item
                continue
            previous_eles[button.text()] = button.state == ElementButton.Checked
            button.deleteLater()
            del item
        
        elements = sorted([e for e in elements if e in ELEMENTS], key=ELEMENTS.index)
        for i, ele in enumerate(elements):
            ele_button = ElementButton(ele)
            try:
                checked = previous_eles[ele]
                if checked:
                    ele_button.setState(ElementButton.Checked)
                else:
                    ele_button.setState(ElementButton.Unchecked)
            except KeyError:
                if ele in COMMONLY_ODD_ISOTOPES:
                    ele_button.setState(ElementButton.Checked)
                else:
                    ele_button.setState(ElementButton.Unchecked)
            self.couple_with.addWidget(ele_button, stretch=0)
        self.couple_with.addStretch(1)

    def refresh_plot(self):
        # if self.show_boltzmann_pop.checkState() == Qt.Checked:
        #     self.show_conformers()
    
        mixed_spectra = self.get_mixed_spectrum()
        if not mixed_spectra:
            return

        mixed_spectra, show_components = mixed_spectra

        self.figure.clear()
        
        temperature = self.temperature.value()
        self.settings.temperature = temperature
        w0 = self.w0.value()
        self.settings.w0 = w0
        weight_method = self.weight_method.currentData(Qt.UserRole)
        self.settings.weight_method = weight_method
        
        fwhm = self.fwhm.value()
        self.settings.fwhm = fwhm
        peak_type = self.peak_type.currentText()
        self.settings.peak_type = peak_type
        reverse_x = self.reverse_x.checkState() == Qt.Checked
        voigt_mixing = self.voigt_mix.value()
        self.settings.voigt_mix = voigt_mixing
        linear = self.linear.value()
        scalar = self.scalar.value()

        elements = set()
        for i in range(0, self.elements.count()):
            item = self.elements.itemAt(i)
            button = item.widget()
            if button is None:
                del item
                continue
            if button.state == ElementButton.Checked:
                elements.add(button.text())
        
        couple_with = set()
        for i in range(0, self.couple_with.count()):
            item = self.couple_with.itemAt(i)
            button = item.widget()
            if button is None:
                del item
                continue
            if button.state == ElementButton.Checked:
                couple_with.add(button.text())
        
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
        
        mixed_spectra.plot_nmr(
            self.figure,
            centers=centers,
            widths=widths,
            exp_data=self.exp_data,
            peak_type=peak_type,
            reverse_x=reverse_x,
            fwhm=fwhm,
            voigt_mixing=voigt_mixing,
            linear_scale=linear,
            scalar_scale=scalar,
            show_functions=show_components,
            element=elements,
            couple_with=couple_with,
        )

        self.canvas.draw()
        # if self.highlighted_mode:
        #     mode = self.highlighted_mode
        #     self.highlighted_mode = None
        #     self.highlight(mode, self.highlight_frs)

    # def highlight(self, item, fr):
    #     highlights = []
    #     labels = []
    # 
    #     freqs = self.get_mixed_spectrum()
    #     if not freqs:
    #         return
    # 
    #     freqs, _ = freqs
    # 
    #     anharmonic = self.anharmonic.checkState() == Qt.Checked
    #     data_attr = "data"
    #     if anharmonic:
    #         data_attr = "anharm_data"
    # 
    #     plot_type = self.plot_type.currentText()
    #     
    #     for ax in self.figure.get_axes():
    #         for mode in self.highlighted_lines:
    #             if mode in ax.collections:
    #                 ax.collections.remove(mode)
    # 
    #         for text in ax.texts:
    #             text.remove()
    # 
    #         if item is self.highlighted_mode:
    #             continue
    #             
    #         for freq in getattr(freqs, data_attr):
    #             if freq.frequency == item.frequency:
    #                 break
    #         else:
    #             continue
    # 
    #         c1 = self.linear.value()
    #         c2 = self.quadratic.value()
    #         frequency = freq.frequency
    #         frequency -= c1 * frequency + c2 * frequency ** 2
    #         
    #         if plot_type == "Transmittance":
    #             y_vals = (10 ** (2 - 0.9), 100)
    #         elif plot_type == "VCD":
    #             y_vals = (0, np.sign(item.rotation))
    #         else:
    #             y_vals = (0, 1)
    #         
    #         if plot_type == "Raman":
    #             y_rel = freq.raman_activity / item.raman_activity
    #         elif plot_type == "VCD":
    #             y_rel = freq.rotation / item.rotation
    #         else:
    #             y_rel = freq.intensity / item.intensity
    #         
    #         label = "%s" % fr["name"]
    #         label += "\n%.2f cm$^{-1}$" % frequency
    #         if c1 or c2:
    #             label += "\n$\Delta_{corr}$ = %.2f cm$^{-1}$" % (frequency - item.frequency)
    #         if item.symmetry and item.symmetry != "A":
    #             text = item.symmetry
    #             if re.search("\d", text):
    #                 text = re.sub(r"(\d+)", r"$_{\1", text)
    #             if text.startswith("SG"):
    #                 text = "$\Sigma$" + text[2:]
    #             elif text.startswith("PI"):
    #                 text = "$\Pi$" + text[2:]
    #             elif text.startswith("DLT"):
    #                 text = "$\Delta$" + text[3:]
    #                 if text[1:] == "A":
    #                     text = text[0]
    #             if any(text.endswith(char) for char in "vhdugVHDUG"):
    #                 if "_" not in text:
    #                     text = text[:-1] + "$_{" + text[-1]
    #                 text = text + text[-1].lower()
    #             if "_" in text:
    #                 text = text + "}$"
    #             label += "\n%s" % text
    #         label += "\nintensity scaled by %.2e" % y_rel
    #         
    #         if frequency < min(ax.get_xlim()) or frequency > max(ax.get_xlim()):
    #             continue
    #         
    #         x_mid = frequency > sum(ax.get_xlim()) / 2
    #         label_x = frequency
    #         if x_mid:
    #             label_x -= 0.01 * sum(ax.get_xlim())
    #         else:
    #             label_x += 0.01 * sum(ax.get_xlim())
    #         
    #         labels.append(
    #             ax.text(
    #                 label_x,
    #                 y_vals[1] / len(label.splitlines()),
    #                 label,
    #                 va="bottom" if y_vals[1] > 0 else "top",
    #                 ha="left" if x_mid else "right",
    #                 path_effects=[pe.withStroke(linewidth=2, foreground="white")],
    #             )
    #         )
    #         
    #         highlights.append(
    #             ax.vlines(
    #                 frequency, *y_vals, color='r', zorder=-1, label="highlight"
    #             )
    #         )
    #     
    #     if item is not self.highlighted_mode:
    #         self.highlighted_mode = item
    #         self.highlight_frs = fr
    #     else:
    #         self.highlighted_mode = None
    #         self.highlight_frs = None
    # 
    #     self.highlighted_lines = highlights
    #     self.highlighted_labels = labels
    #     self.canvas.draw()
    
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


class SaveScales(ChildToolWindow):
    def __init__(self, tool_instance, title, *args, m=-1.0, b=38.0, **kwargs):
        super().__init__(tool_instance, title, *args, **kwargs)
        
        self.m = m
        self.b = b
        self._build_ui()
    
    def _build_ui(self):
        layout = QFormLayout()
        
        self.scale_name = QLineEdit()
        layout.addRow("name:", self.scale_name)
        
        do_it = QPushButton("save scales")
        do_it.clicked.connect(self.save_scales)
        layout.addRow(do_it)
        
        self.ui_area.setLayout(layout)
        self.manage(None)
    
    def save_scales(self):
        name = self.scale_name.text()
        if not name:
            self.session.logger.warning("no name entered")
            return
        
        current = loads(self.tool_instance.settings.scales)
        current[name] = (self.m, self.b)
        self.tool_instance.settings.scales = dumps(current)
        self.tool_instance.fill_lib_options()
        
        self.session.logger.info(
            "saved NMR scale factors to user-defined database"
        )
        self.session.logger.status(
            "saved NMR scale factors to user-defined database"
        )

        self.destroy()

