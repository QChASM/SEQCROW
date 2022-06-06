from io import BytesIO
import re
from json import loads, dumps

import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.ui.widgets import ColorButton
from chimerax.bild.bild import read_bild
from chimerax.std_commands.coordset_gui import CoordinateSetSlider
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import FloatArg, TupleOf, IntArg
from chimerax.core.commands import run

from AaronTools.const import FREQUENCY_SCALE_LIBS
from AaronTools.geometry import Geometry
from AaronTools.spectra import HarmonicVibration
from AaronTools.pathway import Pathway

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from matplotlib import rcParams

from Qt.QtCore import Qt, QRect, QItemSelectionModel
from Qt.QtGui import QValidator, QFont, QIcon
from Qt.QtWidgets import (
    QSpinBox,
    QDoubleSpinBox,
    QGridLayout,
    QPushButton,
    QTabWidget,
    QComboBox,
    QTableWidget,
    QTableView,
    QWidget,
    QTableWidgetItem,
    QFormLayout,
    QCheckBox,
    QHeaderView,
    QMenuBar,
    QFileDialog,
    QStyle,
    QGroupBox,
    QLabel,
    QHBoxLayout,
    QLineEdit,
)

from SEQCROW.tools.per_frame_plot import NavigationToolbar
from SEQCROW.utils import iter2str
from SEQCROW.widgets import FilereaderComboBox

#TODO:
#make double clicking something in the table visualize it

rcParams["savefig.dpi"] = 300


class _NormalModeSettings(Settings):
    AUTO_SAVE = {
        'arrow_color': Value((0.0, 1.0, 0.0, 1.0), TupleOf(FloatArg, 4), iter2str),
        'arrow_scale': Value(1.5, FloatArg),
        'anim_scale': Value(0.2, FloatArg),
        'anim_duration': Value(60, IntArg),
        'anim_fps': Value(60, IntArg), 
        'fwhm': Value(5, FloatArg), 
        'peak_type': 'pseudo-Voigt', 
        'plot_type': 'Absorbance',
        'voigt_mix': 0.5,
        'exp_color': Value((0.0, 0.0, 1.0), TupleOf(FloatArg, 3), iter2str),
        'reverse_x': True,
        'figure_width': 5,
        'figure_height': 3.5,
        "fixed_size": False,
        "scales": "{}",
    }


class FPSSpinBox(QSpinBox):
    """spinbox that makes sure the value goes evenly into 60"""
    def validate(self, text, pos):
        if pos < len(text) or pos == 0:
            return (QValidator.Intermediate, text, pos)
        
        try:
            value = int(text)
        except:
            return (QValidator.Invalid, text, pos)
        
        if 60 % value != 0:
            if pos == 1:
                return (QValidator.Intermediate, text, pos)
            else:
                return (QValidator.Invalid, text, pos)
        elif value > self.maximum():
            return (QValidator.Invalid, text, pos)
        elif value < self.minimum():
            return (QValidator.Invalid, text, pos)
        else:
            return (QValidator.Acceptable, text, pos)
    
    def fixUp(self, text):
        try:
            value = int(text)
            new_value = 1
            for i in range(1, value+1):
                if 60 % i == 0:
                    new_value = i
            
            self.setValue(new_value)
        
        except:
            pass
    
    def stepBy(self, step):
        val = self.value()
        while step > 0:
            val += 1
            while 60 % val != 0:
                val += 1
            step -= 1
        
        while step < 0:
            val -= 1
            while 60 % val != 0:
                val -= 1
            step += 1
        
        self.setValue(val)


class FreqTableWidgetItem(QTableWidgetItem):
    def setData(self, role, value):
        super().setData(role, value)
        
        if role == Qt.DisplayRole:
            font = QFont()
            if "i" in value:
                font.setItalic(True)
            else:
                font.setItalic(False)
            
            self.setFont(font)

    def __lt__(self, other):
        return self.data(Qt.UserRole) < other.data(Qt.UserRole)


class NormalModes(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    help = "https://github.com/QChASM/SEQCROW/wiki/Visualize-Normal-Modes-Tool"
    
    def __init__(self, session, name):
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)        
        
        self.vec_mw_bool = False
        self.ir_plot = None
        self.match_peaks = None
        
        self.settings = _NormalModeSettings(session, name)
        
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()
        
        #select which molecule's frequencies to visualize
        model_selector = FilereaderComboBox(self.session, otherItems=['frequency'])

        model_selector.currentIndexChanged.connect(self.create_freq_table)
        self.model_selector = model_selector
        layout.addWidget(model_selector)
        
        #table that lists frequencies
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(
            ["Frequency (cm\u207b\u00b9)", "Symmetry", "IR Intensity"]
        )
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QTableView.SelectRows)
        table.setSelectionMode(QTableView.SingleSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        for i in range(0, 3):
            table.resizeColumnToContents(i)
        
        table.horizontalHeader().setStretchLastSection(False)            
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)        
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)        
        
        layout.addWidget(table)
        self.table = table
        self.table.itemDoubleClicked.connect(self.highlight_ir_plot)
        self.table.itemSelectionChanged.connect(self.highlight_ir_plot)
        
        #tab thing to select animation or vectors
        self.display_tabs = QTabWidget()

        vector_tab = QWidget()
        vector_opts = QFormLayout(vector_tab)
        
        self.vec_scale = QDoubleSpinBox()
        self.vec_scale.setDecimals(1)
        self.vec_scale.setRange(-100.0, 100.0)
        self.vec_scale.setValue(self.settings.arrow_scale)
        self.vec_scale.setSuffix(" \u212B")
        self.vec_scale.setSingleStep(0.1)
        self.vec_scale.setToolTip(
            "vectors will be scaled so that this is the length of the longest vector\n"
            "vectors shorter than 0.1 \u212B will not be displayed\n"
            "vector direction can be changed by switching the sign"
        )
        vector_opts.addRow("vector scale:", self.vec_scale)
        
        self.vec_use_mass_weighted = QCheckBox()
        self.vec_use_mass_weighted.stateChanged.connect(self.change_mw_option)
        self.vec_use_mass_weighted.setToolTip("if checked, vectors will show mass-weighted displacements")
        vector_opts.addRow("use mass-weighted:", self.vec_use_mass_weighted)

        self.vector_color = ColorButton(has_alpha_channel=True, max_size=(16, 16))
        self.vector_color.set_color(self.settings.arrow_color)
        vector_opts.addRow("vector color:", self.vector_color)

        show_vec_button = QPushButton("display selected mode")
        show_vec_button.clicked.connect(self.show_vec)
        vector_opts.addRow(show_vec_button)
        self.show_vec_button = show_vec_button

        close_vec_button = QPushButton("remove selected mode vectors")
        close_vec_button.clicked.connect(self.close_vec)
        vector_opts.addRow(close_vec_button)
        self.close_vec_button = close_vec_button

        stop_anim_button = QPushButton("reset coordinates")
        stop_anim_button.clicked.connect(self.stop_anim)
        vector_opts.addRow(stop_anim_button)
        
        
        animate_tab = QWidget()
        anim_opts = QFormLayout(animate_tab)
        
        self.anim_scale = QDoubleSpinBox()
        self.anim_scale.setSingleStep(0.05)
        self.anim_scale.setRange(0.01, 100.0)
        self.anim_scale.setValue(self.settings.anim_scale)
        self.anim_scale.setSuffix(" \u212B")
        self.anim_scale.setToolTip("maximum distance an atom is displaced from equilibrium")
        anim_opts.addRow("max. displacement:", self.anim_scale)
        
        self.anim_duration = QSpinBox()
        self.anim_duration.setRange(1, 1001)
        self.anim_duration.setValue(self.settings.anim_duration)
        self.anim_duration.setToolTip("number of frames in animation\nmore frames results in a smoother animation")
        self.anim_duration.setSingleStep(10)
        anim_opts.addRow("frames:", self.anim_duration)
        
        self.anim_fps = FPSSpinBox()
        self.anim_fps.setRange(1, 60)
        self.anim_fps.setValue(self.settings.anim_fps)
        self.anim_fps.setToolTip(
            "animation and recorded movie frames per second\n" +
            "60 must be evenly divisible by this number\n" +
            "animation speed in ChimeraX might be slower, depending on your hardware or graphics settings"
        )
        anim_opts.addRow("animation FPS:", self.anim_fps)

        show_anim_button = QPushButton("animate selected mode")
        show_anim_button.clicked.connect(self.show_anim)
        anim_opts.addRow(show_anim_button)
        self.show_anim_button = show_anim_button

        stop_anim_button = QPushButton("stop animation")
        stop_anim_button.clicked.connect(self.stop_anim)
        anim_opts.addRow(stop_anim_button)
        self.stop_anim_button = stop_anim_button

        # IR plot options
        ir_tab = QWidget()
        ir_layout = QFormLayout(ir_tab)
        
        self.plot_type = QComboBox()
        self.plot_type.addItems(['Absorbance', 'Transmittance', "VCD", "Raman"])
        ndx = self.plot_type.findText(self.settings.plot_type, Qt.MatchExactly)
        self.plot_type.setCurrentIndex(ndx)
        self.plot_type.currentIndexChanged.connect(lambda *args: self.show_ir_plot(create=False))
        ir_layout.addRow("plot type:", self.plot_type)
        
        self.reverse_x = QCheckBox()
        self.reverse_x.setCheckState(Qt.Checked if self.settings.reverse_x else Qt.Unchecked)
        self.reverse_x.stateChanged.connect(lambda *args: self.show_ir_plot(create=False))
        ir_layout.addRow("reverse x-axis:", self.reverse_x)
        
        show_plot = QPushButton("show plot")
        show_plot.clicked.connect(self.show_ir_plot)
        ir_layout.addRow(show_plot)
        
        
        self.display_tabs.addTab(vector_tab, "vectors")
        self.display_tabs.addTab(animate_tab, "animate")
        self.display_tabs.addTab(ir_tab, "IR spectrum")

        layout.addWidget(self.display_tabs)

        #only the table can stretch
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 0)
        
        self.tool_window.ui_area.setLayout(layout)

        if len(self.session.filereader_manager.frequency_models) > 0:
            self.create_freq_table(0)

        self.tool_window.manage(None)

    def create_freq_table(self, state):
        """populate the table with frequencies"""
        
        self.table.setRowCount(0)

        if state == -1:
            # early return if no frequency models
            return
            
        fr = self.model_selector.currentData()
        if fr is None:
            return 

        freq = fr.other['frequency']
        
        model = self.plot_type.model()
        vcd_item = model.item(2)
        raman_item = model.item(3)
        if freq.data[0].rotation is None:
            vcd_item.setFlags(vcd_item.flags() & ~Qt.ItemIsEnabled)
        else:
            vcd_item.setFlags(vcd_item.flags() | Qt.ItemIsEnabled)
        if freq.data[0].raman_activity is None:
            raman_item.setFlags(raman_item.flags() & ~Qt.ItemIsEnabled)
        else:
            raman_item.setFlags(raman_item.flags() | Qt.ItemIsEnabled)

        if freq.anharm_data:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels([
                "Fundamental (cm\u207b\u00b9)",
                "Δ\u2090\u2099\u2095",
                "symmetry",
                "IR intensity",
            ])
            freq_data = sorted(freq.anharm_data, key=lambda x: x.harmonic_frequency)
        else:
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels([
                "Frequency (cm\u207b\u00b9)",
                "symmetry",
                "IR intensity",
            ])
            freq_data = freq.data
        
        for i, mode in enumerate(freq_data):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            freq_cm = FreqTableWidgetItem()
            freq_cm.setData(Qt.DisplayRole, "%.2f%s" % (abs(mode.frequency), "i" if mode.frequency < 0 else ""))
            freq_cm.setData(Qt.UserRole, i)
            self.table.setItem(row, 0, freq_cm)

            if isinstance(mode, HarmonicVibration):
                symm = mode.symmetry
                offset = 0
            else:
                symm = mode.harmonic.symmetry
                delta_anh = QTableWidgetItem()
                delta_anh.setData(Qt.DisplayRole, round(mode.delta_anh, 2))
                offset = 1
                self.table.setItem(row, 1, delta_anh)

            if symm:
                text = symm
                if re.search("\d", text):
                    text = re.sub(r"(\d+)", r"<sub>\1</sub>", text)
                if text.startswith("SG"):
                    text = "Σ" + text[2:]
                elif text.startswith("PI"):
                    text = "Π" + text[2:]
                elif text.startswith("DLT"):
                    text = "Δ" + text[3:]
                    if text[1:] == "A":
                        text = text[0]
                if any(text.endswith(char) for char in "vhdugVHDUG"):
                    text = text[:-1] + "<sub>" + text[-1].lower() + "</sub>"

                label = QLabel(text)
                label.setAlignment(Qt.AlignCenter)
                self.table.setCellWidget(row, 1 + offset, label)

            intensity = QTableWidgetItem()
            if mode.intensity is not None:
                intensity.setData(Qt.DisplayRole, round(mode.intensity, 2))
            self.table.setItem(row, 2 + offset, intensity)
        
        if freq.anharm_data:
            for i in range(0, 4):
                self.table.resizeColumnToContents(i)
        else:
            for i in range(0, 3):
                self.table.resizeColumnToContents(i)
        
        self.table.setSelection(QRect(0, 0, 2, 1), QItemSelectionModel.Select)

        if self.plot_type.currentIndex() == 2 and freq.data[0].rotation is None:
            self.plot_type.setCurrentIndex(0)
        if self.plot_type.currentIndex() == 3 and freq.data[0].raman_activity is None:
            self.plot_type.setCurrentIndex(0)
        # elif freq.data[0].rotation is not None:
        #     self.plot_type.setCurrentIndex(2)

    def change_mw_option(self, state):
        """toggle bool associated with mass-weighting option"""
        if Qt.CheckState(state) == Qt.Checked:
            self.vec_mw_bool = True
        else:
            self.vec_mw_bool = False

    def _get_coord_change(self, geom, vector, scaling):
        """determine displacement given scaling and vector"""
        max_norm = None
        for i, displacement in enumerate(vector):
            n = np.linalg.norm(displacement)
            if self.vec_mw_bool and self.display_tabs.currentIndex() == 0:
                n *= geom.atoms[i].mass()

            if max_norm is None or n > max_norm:
                max_norm = n

        dX = vector * scaling/max_norm

        if self.vec_mw_bool and self.display_tabs.currentIndex() == 0:
            for i, x in enumerate(dX):
                dX[i] *= geom.atoms[i].mass()

        return dX

    def close_vec(self):
        modes = self.table.selectedItems()
        if len([mode for mode in modes if mode.column() == 0]) != 1:
            return 
            
        fr = self.model_selector.currentData()
        model = self.session.filereader_manager.get_model(fr)
        for m in modes:
            if m.column() == 0:
                mode = m.data(Qt.UserRole)
        
        name = "%.2f cm^-1" % fr.other['frequency'].data[mode].frequency
        
        for child in model.child_models():
            if child.name == name:
                run(self.session, "close %s" % child.atomspec)

    def show_vec(self):
        """display normal mode displacement vector"""
        fr = self.model_selector.currentData()
        model = self.session.filereader_manager.get_model(fr)
        modes = self.table.selectedItems()
        if len([mode for mode in modes if mode.column() == 0]) != 1:
            raise RuntimeError("one mode must be selected")
        else:
            for m in modes:
                if m.column() == 0:
                    mode = m.data(Qt.UserRole)

        scale = self.vec_scale.value()

        self.settings.arrow_scale = scale

        color = self.vector_color.get_color()

        color = [c/255. for c in color]

        self.settings.arrow_color = tuple(color)

        #reset coordinates if movie isn't playing
        geom = Geometry(fr)

        vector = fr.other['frequency'].data[mode].vector

        dX = self._get_coord_change(geom, vector, scale)
        
        #make a bild file for the model
        s = ".color %f %f %f\n" % tuple(color[:-1])
        s += ".transparency %f\n" % (1. - color[-1])
        for i in range(0, len(geom.atoms)):
            n = np.linalg.norm(dX[i])

            info = tuple(t for s in [[x for x in geom.atoms[i].coords], \
                                     [x for x in geom.atoms[i].coords + dX[i]], \
                                     [n/(n + 0.75)]] for t in s)
                                    
            if n > 0.1:
                s += ".arrow %10.6f %10.6f %10.6f   %10.6f %10.6f %10.6f   0.02 0.05 %5.3f\n" % info

        stream = BytesIO(bytes(s, 'utf-8'))
        bild_obj, status = read_bild(self.session, stream, "%.2f cm^-1" % fr.other['frequency'].data[mode].frequency)

        self.session.models.add(bild_obj, parent=model)
    
    def show_anim(self):
        """play selected modes as an animation"""
        fr = self.model_selector.currentData()
        model = self.session.filereader_manager.get_model(fr)
        modes = self.table.selectedItems()
        if len([mode for mode in modes if mode.column() == 0]) != 1:
            raise RuntimeError("one mode must be selected")
        else:
            for m in modes:
                if m.column() == 0:
                    mode = m.data(Qt.UserRole)

        scale = self.anim_scale.value()
        frames = self.anim_duration.value()
        anim_fps = self.anim_fps.value()

        self.settings.anim_scale = scale
        self.settings.anim_duration = frames
        self.settings.anim_fps = anim_fps

        geom = Geometry(fr)
        #if the filereader has been processed somewhere else, the atoms might
        #have a chimerax atom associated with them that prevents them from being pickled 
        for atom in geom.atoms:
            if hasattr(atom, "chix_atom"):
                atom.chix_atom = None

        vector = fr.other['frequency'].data[mode].vector

        dX = self._get_coord_change(geom, vector, scale)
        
        Xf = geom.coords + dX
        X = geom.coords
        Xr = geom.coords - dX
        
        S = Pathway(np.array([Xf, X, Xr, X, Xf]))
        
        coordsets = np.zeros((frames, len(geom.atoms), 3))
        for i, t in enumerate(np.linspace(0, 1, num=frames, endpoint=False)):
            coordsets[i] = S.interpolate_coords(t)
            
        model.add_coordsets(coordsets, replace=True)
        for i, coordset in enumerate(coordsets):
            model.active_coordset_id = i + 1

            for atom, coord in zip(model.atoms, coordset):
                atom.coord = coord
        
        for atom, chix_atom in zip(geom.atoms, model.atoms):
            atom.chix_atom = chix_atom
        
        for tool in self.session.tools.list():
            if isinstance(tool, CoordinateSetSlider):
                if tool.structure is model:
                    tool.delete()

        pause_frames = (60 // anim_fps)

        slider =  CoordinateSetSlider(
            self.session,
            model,
            movie_framerate=anim_fps,
            pause_frames=pause_frames,
        )
        slider.play_cb()

    def stop_anim(self):
        fr = self.model_selector.currentData()
        model = self.session.filereader_manager.get_model(fr)
        for tool in self.session.tools.list():
            if isinstance(tool, CoordinateSetSlider):
                if tool.structure is model:
                    tool.delete()
                    
        geom = Geometry(fr)
        for atom, coord in zip(model.atoms, geom.coords):
            atom.coord = coord
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
    
    def show_ir_plot(self, *args, create=True, **kwargs):
        if self.ir_plot is None and create:
            self.ir_plot = self.tool_window.create_child_window("IR Plot", window_class=IRPlot)
        elif self.ir_plot is not None:
            self.ir_plot.refresh_plot()
    
    def highlight_ir_plot(self, *args):
        if self.ir_plot is not None:
            self.ir_plot.highlight(self.table.selectedItems())

    def delete(self):
        self.model_selector.deleteLater()

        return super().delete()
    
    def close(self):
        self.model_selector.deleteLater()
    
    def cleanup(self):
        self.model_selector.deleteLater()

        return super().cleanup()
    

class IRPlot(ChildToolWindow):
    def __init__(self, tool_instance, title, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)
        
        self.highlighted_mode = None
        self._last_mouse_xy = None
        self._dragged = False
        self._min_drag = 10	
        self._drag_mode = None
        self.press = None
        self.drag_prev = None
        self.dragging = False
        self.exp_data = None
        
        self._build_ui()
        self.refresh_plot()

    def _build_ui(self):
        
        layout = QGridLayout()
        
        toolbox = QTabWidget()
        layout.addWidget(toolbox)
        
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
        self.fixed_size.setCheckState(Qt.Checked if self.tool_instance.settings.fixed_size else Qt.Unchecked)
        self.fixed_size.stateChanged.connect(self.change_figure_size)
        plot_layout.addWidget(self.fixed_size, 1, 3, 1, 1, Qt.AlignVCenter | Qt.AlignLeft)

        self.figure_width = QDoubleSpinBox()
        self.figure_width.setRange(1, 24)
        self.figure_width.setDecimals(2)
        self.figure_width.setSingleStep(0.25)
        self.figure_width.setSuffix(" in.")
        self.figure_width.setValue(self.tool_instance.settings.figure_width)
        self.figure_width.valueChanged.connect(self.change_figure_size)
        plot_layout.addWidget(self.figure_width, 1, 4, 1, 1)
     
        plot_layout.addWidget(QLabel("x"), 1, 5, 1, 1, Qt.AlignVCenter | Qt.AlignHCenter)
     
        self.figure_height = QDoubleSpinBox()
        self.figure_height.setRange(1, 24)
        self.figure_height.setDecimals(2)
        self.figure_height.setSingleStep(0.25)
        self.figure_height.setSuffix(" in.")
        self.figure_height.setValue(self.tool_instance.settings.figure_height)
        self.figure_height.valueChanged.connect(self.change_figure_size)
        plot_layout.addWidget(self.figure_height, 1, 6, 1, 1)

        self.change_figure_size()
        
        toolbox.addTab(plot_widget, "plot")

        # peak style
        peak_widget = QWidget()
        peak_layout = QFormLayout(peak_widget)

        self.peak_type = QComboBox()
        self.peak_type.addItems(['Gaussian', 'Lorentzian', 'pseudo-Voigt', 'Delta'])
        ndx = self.peak_type.findText(self.tool_instance.settings.peak_type, Qt.MatchExactly)
        self.peak_type.setCurrentIndex(ndx)
        peak_layout.addRow("peak type:", self.peak_type)
        
        self.fwhm = QDoubleSpinBox()
        self.fwhm.setSingleStep(5)
        self.fwhm.setRange(0.01, 200.0)
        self.fwhm.setValue(self.tool_instance.settings.fwhm)
        self.fwhm.setToolTip("width of peaks at half of their maximum value")
        peak_layout.addRow("FWHM:", self.fwhm)
        
        self.fwhm.setEnabled(self.peak_type.currentText() != "Delta")
        self.peak_type.currentTextChanged.connect(lambda text, widget=self.fwhm: widget.setEnabled(text != "Delta"))
        
        self.voigt_mix = QDoubleSpinBox()
        self.voigt_mix.setSingleStep(0.005)
        self.voigt_mix.setDecimals(3)
        self.voigt_mix.setRange(0, 1)
        self.voigt_mix.setValue(self.tool_instance.settings.voigt_mix)
        self.voigt_mix.setToolTip("fraction of pseudo-Voigt function that is Gaussian")
        peak_layout.addRow("Voigt mixing:", self.voigt_mix)
        
        self.voigt_mix.setEnabled(self.peak_type.currentText() == "pseudo-Voigt")
        self.peak_type.currentTextChanged.connect(lambda text, widget=self.voigt_mix: widget.setEnabled(text == "pseudo-Voigt"))
        
        self.anharm = QCheckBox()
        self.anharm.setCheckState(Qt.Checked)
        peak_layout.addRow("anharmonic:", self.anharm)

        # self.vcd = QCheckBox()
        # self.vcd.setCheckState(Qt.Checked)
        # peak_layout.addRow("VCD:", self.vcd)
        
        toolbox.addTab(peak_widget, "peak settings")
        
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
        self.line_color.set_color(self.tool_instance.settings.exp_color)
        experimental_layout.addRow("line color:", self.line_color)
        
        clear_button = QPushButton("clear experimental data")
        clear_button.clicked.connect(self.clear_data)
        experimental_layout.addRow(clear_button)
        
        toolbox.addTab(experimental_widget, "plot experimental data")
        
        
        # frequency scaling
        scaling_group = QWidget()
        scaling_layout = QFormLayout(scaling_group)
        
        desc = QLabel("")
        desc.setText("<a href=\"test\" style=\"text-decoration: none;\">Δ<sub>anh</sub> ≈ c<sub>1</sub>𝜈<sub>e</sub> + c<sub>2</sub>𝜈<sub>e</sub><sup>2</sup></a>")
        desc.setTextFormat(Qt.RichText)
        desc.setTextInteractionFlags(Qt.TextBrowserInteraction)
        desc.linkActivated.connect(self.open_link)
        desc.setToolTip("Crittenden and Sibaev's quadratic scaling for harmonic frequencies\nDOI 10.1021/acs.jpca.5b11386")
        scaling_layout.addRow(desc)

        self.linear = QDoubleSpinBox()
        self.linear.setDecimals(6)
        self.linear.setRange(-.2, .2)
        self.linear.setSingleStep(0.001)
        self.linear.setValue(0.)
        scaling_layout.addRow("c<sub>1</sub> =", self.linear)

        self.quadratic = QDoubleSpinBox()
        self.quadratic.setDecimals(9)
        self.quadratic.setRange(-.2, .2)
        self.quadratic.setSingleStep(0.000001)
        self.quadratic.setValue(0.)
        scaling_layout.addRow("c<sub>2</sub> =", self.quadratic)
        
        save_scales = QPushButton("save current scale factors...")
        save_scales.clicked.connect(self.open_save_scales)
        scaling_layout.addRow(save_scales)
        
        set_zero = QPushButton("set scales to 0")
        set_zero.clicked.connect(lambda *args: self.linear.setValue(0.))
        set_zero.clicked.connect(lambda *args: self.quadratic.setValue(0.))
        scaling_layout.addRow(set_zero)
        
        
        lookup_scale = QGroupBox("scale factor lookup")
        scaling_layout.addRow(lookup_scale)
        lookup_layout = QFormLayout(lookup_scale)
        
        self.library = QComboBox()
        lookup_layout.addRow("database:", self.library)
        
        self.method = QComboBox()
        lookup_layout.addRow("method:", self.method)
        
        self.basis = QComboBox()
        lookup_layout.addRow("basis set:", self.basis)
        
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

        fit_scale = QGroupBox("linear least squares fitting")
        scaling_layout.addRow(fit_scale)
        fit_layout = QFormLayout(fit_scale)
        
        self.fit_c1 = QCheckBox()
        fit_layout.addRow("fit c<sub>1</sub>:", self.fit_c1)
        
        self.fit_c2 = QCheckBox()
        fit_layout.addRow("fit c<sub>2</sub>:", self.fit_c2)
        
        match_peaks = QPushButton("match peaks...")
        match_peaks.clicked.connect(self.show_match_peaks)
        fit_layout.addRow(match_peaks)

        toolbox.addTab(scaling_group, "frequency scaling")
        
        
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

        auto_section = QPushButton("automatically section")
        auto_section.clicked.connect(self.auto_breaks)
        interrupt_layout.addRow(auto_section)

        toolbox.addTab(interrupt_widget, "x-axis breaks")
        

        toolbox.currentChanged.connect(lambda ndx: self.refresh_plot() if not ndx else None)
        # toolbox.setMinimumWidth(int(1.1 * plot_widget.size().width()))
        # toolbox.setMinimumHeight(int(1.2 * plot_widget.size().height()))

        self.tool_instance.model_selector.currentTextChanged.connect(self.check_anharm)
        self.check_anharm()
        # self.tool_instance.model_selector.currentTextChanged.connect(self.check_vcd)
        # self.check_vcd()

        #menu bar for saving stuff
        menu = QMenuBar()
        file = menu.addMenu("&Export")
        file.addAction("&Save CSV...")
        menu.setVisible(True)
        
        file.triggered.connect(self.save)
        
        menu.setNativeMenuBar(False)
        self._menu = menu
        layout.setMenuBar(menu)        
        menu.setVisible(True)
        self.ui_area.setLayout(layout)
        self.manage(None)

    def auto_breaks(self):
        fr = self.tool_instance.model_selector.currentData()
        if fr is None:
            return
        linear_scale = self.linear.value()
        quadratic_scale = self.quadratic.value()
        freq = fr.other["frequency"]
        frequencies = np.array(
            [mode.frequency for mode in freq.data if mode.frequency > 0]
        )
        fwhm = self.fwhm.value()
        frequencies -= linear_scale * frequencies + quadratic_scale * frequencies ** 2

        tolerance = max(2 * fwhm, 25)

        groups = []
        for freq in frequencies:
            added = False
            for group in groups:
                for other_freq in group:
                    if abs(freq - other_freq) < (8 * tolerance):
                        group.append(freq)
                        added = True
                        break
                if added:
                    break
            else:
                groups.append([freq])
        
        for group in groups:
            xmax = max(group) + 2 * tolerance
            xmin = min(group) - 2 * tolerance
            self.add_section(xmin=xmin, xmax=xmax)

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
        lib_names = list(FREQUENCY_SCALE_LIBS.keys())
        user_def = loads(self.tool_instance.settings.scales)
        if user_def:
            lib_names.append("user-defined")
        
        self.library.addItems(lib_names)
        if cur_lib >= 0:
            self.library.setCurrentIndex(cur_lib)

        if self.library.currentText() != "user-defined":
            self.method.addItems(
                FREQUENCY_SCALE_LIBS[self.library.currentText()][1].keys()
            )

            self.basis.addItems(
                FREQUENCY_SCALE_LIBS[lib_names[0]][1][self.method.currentText()].keys()
            )

        else:
            user_def = loads(self.tool_instance.settings.scales)
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

    def open_save_scales(self):
        c1 = self.linear.value()
        c2 = self.quadratic.value()
        self.tool_instance.tool_window.create_child_window(
            "saving frequency scales",
            window_class=SaveScales,
            c1=c1,
            c2=c2,
        )

    def check_anharm(self):
        data = self.tool_instance.model_selector.currentData()
        if not data:
            return
        freq = data.other["frequency"]
        self.anharm.setEnabled(bool(freq.anharm_data))
    
    # def check_vcd(self):
    #     data = self.tool_instance.model_selector.currentData()
    #     if not data:
    #         return
    #     freq = data.other["frequency"]
    #     if len(freq.data):
    #         self.vcd.setEnabled(bool(freq.data[0].rotation))

    def change_figure_size(self, *args):
        if self.fixed_size.checkState() == Qt.Checked:
            self.figure_height.setEnabled(True)
            self.figure_width.setEnabled(True)
            h = self.figure_height.value()
            w = self.figure_width.value()
            
            self.figure.set_size_inches(w, h)
            
            self.canvas.setMinimumHeight(96 * h)
            self.canvas.setMaximumHeight(96 * h)
            self.canvas.setMinimumWidth(96 * w)
            self.canvas.setMaximumWidth(96 * w)
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
    
    def add_section(self, xmin=450, xmax=1900):
        rows = self.section_table.rowCount()
        if rows != 0:
            rows -= 1
            section_min = QDoubleSpinBox()
            section_min.setRange(0, 5000)
            section_min.setValue(xmin)
            section_min.setSuffix(" cm\u207b\u00b9")
            section_min.setSingleStep(25)
            self.section_table.setCellWidget(rows, 0, section_min)
            
            section_max = QDoubleSpinBox()
            section_max.setRange(1, 5000)
            section_max.setValue(xmax)
            section_max.setSuffix(" cm\u207b\u00b9")
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
            s = "frequency (cm^-1),IR intensity\n"

        
            fr = self.tool_instance.model_selector.currentData()
            if fr is None:
                return
    
            freq = fr.other["frequency"]
        
            fwhm = self.fwhm.value()
            peak_type = self.peak_type.currentText()
            plot_type = self.tool_instance.plot_type.currentText()
            voigt_mixing = self.voigt_mix.value()
            linear = self.linear.value()
            quadratic = self.quadratic.value()
            anharmonic = freq.anharm_data and self.anharm.checkState() == Qt.Checked
            intensity_attr = "intensity"
            if plot_type.lower() == "vcd":
                intensity_attr = "rotation"
            if plot_type.lower() == "raman":
                intensity_attr = "raman_activity"
            data_attr = "data"
            if anharmonic:
                data_attr = "anharm_data"

            funcs, x_positions, intensities = freq.get_spectrum_functions(
                fwhm=fwhm,
                peak_type=peak_type,
                voigt_mixing=voigt_mixing,
                linear_scale=linear,
                quadratic_scale=quadratic,
                intensity_attr=intensity_attr,
                data_attr=data_attr,
            )
            
            x_values, y_values, _ = freq.get_plot_data(
                funcs,
                x_positions,
                transmittance="transmittance" in plot_type.lower(),
                peak_type=peak_type,
                fwhm=fwhm,
                normalize=False,
            )

            for x, y in zip(x_values, y_values):
                s += "%f,%f\n" % (x, y)

            with open(filename, 'w') as f:
                f.write(s.strip())
                
            self.tool_instance.session.logger.info("saved to %s" % filename)

    def open_link(self, *args):
        """open Crittenden's paper on scaling harmonic frequencies"""
        run(self.session, "open https://doi.org/10.1021/acs.jpca.5b11386")

    def open_scale_library_link(self, *args):
        if self.library.currentText() != "user-defined":
            run(self.session, "open %s" % FREQUENCY_SCALE_LIBS[self.library.currentText()][0])
        else:
            self.session.logger.info("that's your database")

    def change_scale_lib(self, lib):
        cur_method = self.method.currentText()
        cur_basis = self.basis.currentText()
        self.prev_basis = self.basis.currentText()
        self.method.blockSignals(True)
        self.method.clear()
        self.method.blockSignals(False)
        if lib in FREQUENCY_SCALE_LIBS:
            self.basis.setEnabled(True)
            self.method.addItems(FREQUENCY_SCALE_LIBS[lib][1].keys())
            ndx = self.method.findText(cur_method, Qt.MatchExactly)
            if ndx >= 0:
                self.method.setCurrentIndex(ndx)
            
            ndx = self.basis.findText(cur_basis, Qt.MatchExactly)
            if ndx >= 0:
                self.basis.setCurrentIndex(ndx)
        else:
            self.basis.setEnabled(False)
            user_def = loads(self.tool_instance.settings.scales)
            self.method.addItems(user_def.keys())
    
    def change_method(self, method):
        cur_basis = self.basis.currentText()
        self.basis.blockSignals(True)
        self.basis.clear()
        self.basis.blockSignals(False)
        if self.library.currentText() in FREQUENCY_SCALE_LIBS:
            if isinstance(FREQUENCY_SCALE_LIBS[self.library.currentText()][1][method], dict):
                self.basis.addItems(
                    FREQUENCY_SCALE_LIBS[self.library.currentText()][1][method].keys()
                )
                ndx = self.basis.findText(cur_basis, Qt.MatchExactly)
                if ndx >= 0:
                    self.basis.setCurrentIndex(ndx)
            else:
                scale = FREQUENCY_SCALE_LIBS[self.library.currentText()][1][method]
                self.linear.setValue(1 - scale)
                self.quadratic.setValue(0.)
        elif method:
            user_def = loads(self.tool_instance.settings.scales)
            c1, c2 = user_def[method]
            self.linear.setValue(c1)
            self.quadratic.setValue(c2)

    def change_basis(self, basis):
        scale = FREQUENCY_SCALE_LIBS[self.library.currentText()][1][self.method.currentText()][basis]
        self.linear.setValue(1 - scale)
        self.quadratic.setValue(0.)

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

    def unclick(self, event):
        if self.toolbar.mode != "":
            return

        self.press = None
        self.drag_prev = None
        self.dragging = False

    def refresh_plot(self):
        
        fr = self.tool_instance.model_selector.currentData()
        if fr is None:
            return
        self.figure.clear()

        freq = fr.other["frequency"]
        
        fwhm = self.fwhm.value()
        self.tool_instance.settings.fwhm = fwhm
        peak_type = self.peak_type.currentText()
        self.tool_instance.settings.peak_type = peak_type
        plot_type = self.tool_instance.plot_type.currentText()
        self.tool_instance.settings.plot_type = plot_type
        reverse_x = self.tool_instance.reverse_x.checkState() == Qt.Checked
        voigt_mixing = self.voigt_mix.value()
        self.tool_instance.voigt_mix = voigt_mixing
        linear = self.linear.value()
        quadratic = self.quadratic.value()
        anharmonic = freq.anharm_data and self.anharm.checkState() == Qt.Checked
        # vcd = self.vcd.isEnabled() and self.vcd.checkState() == Qt.Checked
        
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

        freq.plot_ir(
            self.figure,
            centers=centers,
            widths=widths,
            exp_data=self.exp_data,
            plot_type=plot_type,
            peak_type=peak_type,
            reverse_x=reverse_x,
            fwhm=fwhm,
            voigt_mixing=voigt_mixing,
            linear_scale=linear,
            quadratic_scale=quadratic,
            anharmonic=anharmonic,
        )

        self.canvas.draw()

    def highlight(self, items):
        highlights = []
        for ax in self.figure.get_axes():
            if self.highlighted_mode is not None:
                for mode in self.highlighted_mode:
                    if mode in ax.collections:
                        ax.collections.remove(mode)
            
            if len(items) == 0:
                continue
            
            fr = self.tool_instance.model_selector.currentData()
            if fr is None:
                return 
    
            for item in items:
                if item.column() == 0:
                    row = item.data(Qt.UserRole)
            
            freq = fr.other['frequency']
            if freq.anharm_data and self.anharm.checkState() == Qt.Checked:
                frequencies = sorted(freq.anharm_data, key=lambda x: x.harmonic_frequency)
            elif freq.anharm_data:
                frequencies = sorted(freq.anharm_data, key=lambda x: x.harmonic_frequency)
                frequencies = [x.harmonic for x in frequencies]
            else:
                frequencies = sorted(freq.data, key=lambda x: x.frequency)
            frequency = frequencies[row].frequency
            if frequency < 0:
                self.canvas.draw()
                continue
            
            c1 = self.linear.value()
            c2 = self.quadratic.value()
            frequency -= c1 * frequency + c2 * frequency ** 2
            
            if self.tool_instance.plot_type.currentText() == "Transmittance":
                y_vals = (10 ** (2 - 0.9), 100)
            else:
                y_vals = (0, 1)
                
            highlights.append(ax.vlines(frequency, *y_vals, color='r', zorder=-1, label="highlight"))
        
        self.highlighted_mode = highlights
        self.canvas.draw()

    def load_data(self, *args):
        filename, _ = QFileDialog.getOpenFileName(filter="comma-separated values file (*.csv)")

        if not filename:
            return

        data = np.loadtxt(filename, delimiter=",", skiprows=self.skip_lines.value())

        color = self.line_color.get_color()
        self.tool_instance.settings.exp_color = tuple([c / 255. for c in color[:-1]])
        
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

    def show_match_peaks(self, *args):
        if self.tool_instance.match_peaks is None:
            self.tool_instance.match_peaks = self.tool_instance.tool_window.create_child_window(
                "match peaks", window_class=MatchPeaks
            )

    def cleanup(self):
        self.tool_instance.ir_plot = None
        self.tool_instance.model_selector.currentTextChanged.disconnect(self.check_anharm)
        
        self.tool_instance.settings.figure_height = self.figure_height.value()
        self.tool_instance.settings.figure_width = self.figure_width.value()
        self.tool_instance.settings.fixed_size = self.fixed_size.checkState() == Qt.Checked
        
        super().cleanup()


class MatchPeaks(ChildToolWindow):
    def __init__(self, tool_instance, title, *args, **kwargs):
        super().__init__(tool_instance, title, *args, **kwargs)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QFormLayout()
        
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["comp. freq. (cm\u207b\u00b9)", "obs. freq. (cm\u207b\u00b9)"])
        for i in range(0, 2):
            table.resizeColumnToContents(i)
        
        table.horizontalHeader().setStretchLastSection(False)            
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)        
        
        fr = self.tool_instance.model_selector.currentData()
        if fr:
            freq_data = fr.other['frequency'].data
            
            for i, mode in enumerate(freq_data):
                if mode.frequency < 0:
                    continue
                row = table.rowCount()
                table.insertRow(row)
                
                freq = FreqTableWidgetItem()
                freq.setData(Qt.DisplayRole, "%.2f" % mode.frequency)
                freq.setData(Qt.UserRole, mode.frequency)
                table.setItem(row, 0, freq)
                
                exp_freq = QDoubleSpinBox()
                exp_freq.setRange(0, 4500)
                exp_freq.setDecimals(2)
                exp_freq.setToolTip("observed frequency\nleave at 0 to not use this in fitting")
                table.setCellWidget(row, 1, exp_freq)
        
        layout.addRow(table)
        self.table = table
        
        do_fit_button = QPushButton("do least squares")
        do_fit_button.clicked.connect(self.do_fit)
        layout.addRow(do_fit_button)
        
        self.ui_area.setLayout(layout)
        self.manage(None)
    
    def do_fit(self, *args):
        if not self.tool_instance.ir_plot:
            raise RuntimeError("plot window must be open during fitting")
        comp_freqs = []
        exp_freqs = []
        
        for i in range(0, self.table.rowCount()):
            spinbox = self.table.cellWidget(i, 1)
            if spinbox.value() != 0:
                exp_freqs.append(spinbox.value())
                comp_freqs.append(self.table.item(i, 0).data(Qt.UserRole))
        
        comp_freqs = np.array(comp_freqs)
        exp_freqs = np.array(exp_freqs)
        
        fit_c1 = self.tool_instance.ir_plot.fit_c1.checkState() == Qt.Checked
        fit_c2 = self.tool_instance.ir_plot.fit_c2.checkState() == Qt.Checked
        
        params = int(fit_c1) + int(fit_c2)
        
        if len(comp_freqs) < params:
            raise RuntimeError("must specify enough data for %i parameter(s)" % params)
        
        if fit_c1 and fit_c2:
            mat = np.array([comp_freqs, comp_freqs**2]).T

            c_vals, res, _, _ = np.linalg.lstsq(mat, comp_freqs - exp_freqs, rcond=None)
            self.tool_instance.session.logger.info("sum of squared residuals: %.2f" % sum(res))
            self.tool_instance.ir_plot.linear.setValue(c_vals[0])
            self.tool_instance.ir_plot.quadratic.setValue(c_vals[1])
            # res_v = comp_freqs - c_vals[0] * comp_freqs - c_vals[1] * comp_freqs ** 2
            # res_v -= exp_freqs
            # res = np.dot(res_v, res_v)
            # self.tool_instance.session.logger.info("sum of squared residuals: %.2f" % res)
            if abs(c_vals[0]) > 0.2:
                self.tool_instance.session.logger.warning("c1 value %f is outside the bounds of the spinbox widget, check your input" % c_vals[0])
            if abs(c_vals[1]) > 0.2:
                self.tool_instance.session.logger.warning("c2 value %f is outside the bounds of the spinbox widget, check your input" % c_vals[1])
        elif fit_c1:
            l = np.dot(exp_freqs, comp_freqs) / np.dot(comp_freqs, comp_freqs)
            self.tool_instance.ir_plot.linear.setValue(1 - l)
            self.tool_instance.ir_plot.quadratic.setValue(0.)
            res_v = (exp_freqs - (l * comp_freqs))
            res = np.dot(res_v, res_v)
            self.tool_instance.session.logger.info("sum of squared residuals: %.2f" % res)
            if abs(1 - l) > 0.2:
                self.tool_instance.session.logger.warning("c1 value %f is outside the bounds of the spinbox widget, check your input" % (1 - l))
        elif fit_c2:
            l = np.dot(comp_freqs - exp_freqs, comp_freqs ** 2) / np.dot(comp_freqs ** 2, comp_freqs ** 2)
            self.tool_instance.ir_plot.linear.setValue(0.)
            self.tool_instance.ir_plot.quadratic.setValue(l)
            res_v = comp_freqs - l * comp_freqs ** 2
            res_v -= exp_freqs
            res = np.dot(res_v, res_v)
            self.tool_instance.session.logger.info("sum of squared residuals: %.2f" % res)
            if abs(l) > 0.2:
                self.tool_instance.session.logger.warning("c2 value %f is outside the bounds of the spinbox widget, check your input" % l)
        else:
            self.tool_instance.session.logger.error("no fit parameters selected on plot tool window")

    def cleanup(self):
        self.tool_instance.match_peaks = None
        
        super().cleanup()


class SaveScales(ChildToolWindow):
    def __init__(self, tool_instance, title, *args, c1=0.0, c2=0.0, **kwargs):
        super().__init__(tool_instance, title, *args, **kwargs)
        
        self.c1 = c1
        self.c2 = c2
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
        current[name] = (self.c1, self.c2)
        self.tool_instance.settings.scales = dumps(current)
        if self.tool_instance.ir_plot:
            self.tool_instance.ir_plot.fill_lib_options()
        
        self.session.logger.info(
            "saved frequency scale factors to user-defined database"
        )
        self.session.logger.status(
            "saved frequency scale factors to user-defined database"
        )

        self.destroy()
    