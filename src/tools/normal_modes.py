import numpy as np
import matplotlib.pyplot as plt

from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.ui.widgets import ColorButton
from chimerax.bild.bild import read_bild
from chimerax.std_commands.coordset_gui import CoordinateSetSlider
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import FloatArg, TupleOf, IntArg
from chimerax.core.commands import run

from AaronTools.atoms import Atom
from AaronTools.const import PHYSICAL
from AaronTools.geometry import Geometry
from AaronTools.pathway import Pathway

from io import BytesIO

from os.path import basename

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure
from matplotlib import rc as matplotlib_rc

from PyQt5.QtCore import Qt, QRect, QItemSelectionModel 
from PyQt5.QtGui import QValidator, QFont, QIcon
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QGridLayout, QPushButton, QTabWidget, QComboBox, \
                            QTableWidget, QTableView, QWidget, QVBoxLayout, QTableWidgetItem, \
                            QFormLayout, QCheckBox, QHeaderView, QMenuBar, QAction, QFileDialog, QStyle

from SEQCROW.tools.per_frame_plot import NavigationToolbar
from SEQCROW.utils import iter2str
from SEQCROW.widgets import FilereaderComboBox

#TODO:
#make double clicking something in the table visualize it


matplotlib_rc('font',  **{'sans-serif' : 'Arial', 'family' : 'sans-serif'})

class _NormalModeSettings(Settings):
    AUTO_SAVE = {
        'arrow_color': Value((0.0, 1.0, 0.0, 1.0), TupleOf(FloatArg, 4), iter2str),
        'arrow_scale': Value(1.5, FloatArg),
        'anim_scale': Value(0.2, FloatArg),
        'anim_duration': Value(60, IntArg),
        'anim_fps': Value(60, IntArg), 
        'fwhm': Value(5, FloatArg), 
        'peak_type': 'Gaussian', 
        'plot_type': 'Absorbance', 
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
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(['Frequency (cm\u207b\u00b9)', 'IR intensity'])
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QTableView.SelectRows)
        table.setSelectionMode(QTableView.SingleSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        for i in range(0, 2):
            table.resizeColumnToContents(i)
        
        table.horizontalHeader().setStretchLastSection(False)            
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)        
        
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
        self.vec_scale.setToolTip("vectors will be scaled so that this is the length of the longest vector\nvectors shorter than 0.1 \u212B will not be displayed")
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

        close_vec_button = QPushButton("remove selected mode vectors")
        close_vec_button.clicked.connect(self.close_vec)
        vector_opts.addRow(close_vec_button)

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
        self.anim_fps.setToolTip("animation and recorded movie frames per second\n" +
                                 "60 must be evenly divisible by this number\n" +
                                 "animation speed in ChimeraX might be slower, depending on your hardware or graphics settings")
        anim_opts.addRow("animation FPS:", self.anim_fps)

        show_anim_button = QPushButton("animate selected mode")
        show_anim_button.clicked.connect(self.show_anim)
        anim_opts.addRow(show_anim_button)

        stop_anim_button = QPushButton("stop animation")
        stop_anim_button.clicked.connect(self.stop_anim)
        anim_opts.addRow(stop_anim_button)

        
        ir_tab = QWidget()
        ir_layout = QFormLayout(ir_tab)
        
        self.plot_type = QComboBox()
        self.plot_type.addItems(['Absorbance', 'Transmittance'])
        ndx = self.plot_type.findText(self.settings.plot_type, Qt.MatchExactly)
        self.plot_type.setCurrentIndex(ndx)
        ir_layout.addRow("plot type:", self.plot_type)
        
        self.peak_type = QComboBox()
        self.peak_type.addItems(['Gaussian', 'Lorentzian', 'Delta'])
        ndx = self.peak_type.findText(self.settings.peak_type, Qt.MatchExactly)
        self.peak_type.setCurrentIndex(ndx)
        ir_layout.addRow("peak type:", self.peak_type)
        
        self.fwhm = QDoubleSpinBox()
        self.fwhm.setSingleStep(5)
        self.fwhm.setRange(0.01, 200.0)
        self.fwhm.setValue(self.settings.fwhm)
        self.fwhm.setToolTip("width of peaks at half of their maximum value")
        ir_layout.addRow("FWHM:", self.fwhm)
        
        self.peak_type.currentTextChanged.connect(lambda text, widget=self.fwhm: widget.setEnabled(text != "Delta"))
        
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
            
        model = self.session.filereader_manager.get_model(fr)
        
        freq_data = fr.other['frequency'].data
        
        for i, mode in enumerate(freq_data):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            freq = FreqTableWidgetItem()
            freq.setData(Qt.DisplayRole, "%.2f%s" % (abs(mode.frequency), "i" if mode.frequency < 0 else ""))
            freq.setData(Qt.UserRole, i)
            self.table.setItem(row, 0, freq)
            
            intensity = QTableWidgetItem()
            if mode.intensity is not None:
                intensity.setData(Qt.DisplayRole, round(mode.intensity, 2))
            self.table.setItem(row, 1, intensity)
        
        self.table.setSelection(QRect(0, 0, 2, 1), QItemSelectionModel.Select)
    
    def change_mw_option(self, state):
        """toggle bool associated with mass-weighting option"""
        if state == Qt.Checked:
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
        
        #atoms can't be deep copied for some reason
        Xf = geom.coords() + dX
        X = geom.coords()
        Xr = geom.coords() - dX
        
        S = Pathway(geom, np.array([Xf, X, Xr, X, Xf]))
        
        coordsets = np.zeros((frames, len(geom.atoms), 3))
        for i, t in enumerate(np.linspace(0, 1, num=frames, endpoint=False)):
            coordsets[i] = S.coords_func(t)
            
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

        slider =  CoordinateSetSlider(self.session, model, movie_framerate=anim_fps, pause_frames=pause_frames)
        slider.play_cb()

    def stop_anim(self):
        fr = self.model_selector.currentData()
        model = self.session.filereader_manager.get_model(fr)
        for tool in self.session.tools.list():
            if isinstance(tool, CoordinateSetSlider):
                if tool.structure is model:
                    tool.delete()
                    
        geom = Geometry(fr)
        for atom, coord in zip(model.atoms, geom.coords()):
            atom.coord = coord
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
    
    def show_ir_plot(self):
        if self.ir_plot is None:
            self.ir_plot = self.tool_window.create_child_window("IR Plot", window_class=IRPlot)
        else:
            self.ir_plot.refresh_plot()
    
    def highlight_ir_plot(self, *args):
        if self.ir_plot is not None:
            self.ir_plot.highlight(self.table.selectedItems())

    def delete(self):
        self.model_selector.deleteLater()

        return super().delete()
    

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
        
        self._build_ui()
        self.refresh_plot()

    def _build_ui(self):
        
        layout = QGridLayout()
        
        self.figure = Figure(figsize=(2,2))
        self.canvas = Canvas(self.figure)
        
        ax = self.figure.add_axes((0.15, 0.20, 0.80, 0.70))
        
        self.canvas.mpl_connect('button_release_event', self.unclick)
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.mpl_connect('motion_notify_event', self.drag)
        self.canvas.mpl_connect('scroll_event', self.zoom)
        
        self.canvas.setMinimumWidth(500)
        self.canvas.setMinimumHeight(300)

        layout.addWidget(self.canvas, 0, 0, 1, 2)

        toolbar_widget = QWidget()
        self.toolbar = NavigationToolbar(self.canvas, toolbar_widget)
        self.toolbar.setMaximumHeight(24)
        layout.addWidget(self.toolbar, 1, 1, 1, 1)
        
        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon(refresh_button.style().standardIcon(QStyle.SP_BrowserReload)))
        refresh_button.clicked.connect(self.refresh_plot)
        layout.addWidget(refresh_button, 1, 0, 1, 1, Qt.AlignTop)
        
        #menu bar for saving stuff
        menu = QMenuBar()
        file = menu.addMenu("&Export")
        file.addAction("&Save CSV...")
        
        file.triggered.connect(self.save)
        
        menu.setNativeMenuBar(False)
        
        layout.setMenuBar(menu)        
        self.ui_area.setLayout(layout)
        self.manage(None)
    
    def save(self):
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
        if filename:
            s = "frequency (cm^-1),IR intensity\n"
            ax = self.figure.gca()
            if len(ax.lines) > 0:
                line = ax.lines[0]
                for x, y in zip(line.get_xdata(), line.get_ydata()):
                    s += "%f,%f\n" % (x, y)
            
            else:
                fr = self.tool_instance.model_selector.currentData()
                if fr is None:
                    self.tool_instance.session.logger.error("no model selected")
                    return 
                
                frequencies = [freq.frequency for freq in fr.other['frequency'].data]
                intensities = [freq.intensity for freq in fr.other['frequency'].data]
                for x, y in zip(frequencies, intensities):
                    s += "%f,%f\n" % (x, y if y is not None else 0)

            with open(filename, 'w') as f:
                f.write(s.strip())
                
            self.tool_instance.session.logger.info("saved to %s" % filename)

    def zoom(self, event):
        if event.xdata is None:
            return
        a = self.figure.gca()
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
        a = self.figure.gca()
        w = self.figure.get_figwidth() * self.figure.get_dpi()
        x0, x1 = a.get_xlim()
        xs = dx/w * (x1-x0)
        nx0, nx1 = x0-xs, x1-xs
        #y0, y1 = a.get_ylim()
        #ys = dy/h * (y1-y0)
        #ny0, ny1 = y0-ys, y1-ys
        a.set_xlim(nx0, nx1)
        #a.set_ylim(ny0, ny1)
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

        fwhm = self.tool_instance.fwhm.value()
        self.tool_instance.settings.fwhm = fwhm
        self.tool_instance.settings.peak_type = self.tool_instance.peak_type.currentText()
        self.tool_instance.settings.plot_type = self.tool_instance.plot_type.currentText()
        frequencies = [freq.frequency for freq in fr.other['frequency'].data if freq.frequency > 0]
        intensities = [freq.intensity for freq in fr.other['frequency'].data if freq.frequency > 0]
        
        if self.tool_instance.peak_type.currentText() != "Delta":
            functions = []
            x_values = np.linspace(0, max(frequencies) - 10 * fwhm, num=200).tolist()
            for freq, intensity in zip(frequencies, intensities):
                if intensity is not None:
                    #make sure to get x values near the peak
                    #this makes the peaks look hi res, but we can cheap out
                    #on areas where there's no peak
                    x_values.extend(np.linspace(max(freq - (5 * fwhm), 0), 
                                                freq + (5 * fwhm), 
                                                num=100).tolist()
                                    )
                    x_values.append(freq)
                    if self.tool_instance.peak_type.currentText() == "Gaussian":
                        functions.append(lambda x, x0=freq, inten=intensity, w=fwhm: \
                                        inten * np.exp(-4*np.log(2) * (x - x0)**2 / w**2))
    
                    elif self.tool_instance.peak_type.currentText() == "Lorentzian":
                        functions.append(lambda x, x0=freq, inten=intensity, w=fwhm, : \
                                        inten * 0.5 * (0.5 * w / ((x - x0)**2 + (0.5 * w)**2)))
        
            x_values = list(set(x_values))
            #print(len(x_values), len(functions))
            x_values.sort()
            y_values = np.array([sum(f(x) for f in functions) for x in x_values])
        
        else:
            x_values = []
            y_values = []

            for freq, intensity in zip(frequencies, intensities):
                if intensity is not None:
                    y_values.append(intensity)
                    x_values.append(freq)

            y_values = np.array(y_values)

        if len(y_values) == 0:
            self.tool_instance.session.logger.error("nothing to plot")
            return

        y_values /= np.amax(y_values)

        ax = self.figure.gca()
        ax.clear()
        self.highlighted_mode = None

        if self.tool_instance.plot_type.currentText() == "Transmittance":
            y_values = np.array([10 ** (2 - 0.9*y) for y in y_values])
            ax.set_ylabel('transmittance (%)')
        else:
            ax.set_ylabel('absorbance (a.u.)')
       
        ax.set_xlabel(r'wavenumber (cm$^{-1}$)')
        if self.tool_instance.peak_type.currentText() != "Delta":
            ax.plot(x_values, y_values, color='k', linewidth=0.5)
        else:
            if self.tool_instance.plot_type.currentText() == "Transmittance":
                ax.vlines(x_values, y_values, [100 for y in y_values], linewidth=0.5)
                ax.hlines(100, 0, max(4000, *frequencies), linewidth=0.5)
            
            else:
                ax.vlines(x_values, [0 for y in y_values], y_values, linewidth=0.5)
                ax.hlines(0, 0, max(4000, *frequencies), linewidth=0.5)

        x_lim = ax.get_xlim()
        ax.set_xlim(max(x_lim), min(x_lim))
        
        self.canvas.draw()

    def highlight(self, items):
        ax = self.figure.gca()
        if self.highlighted_mode is not None and self.highlighted_mode in ax.collections:
            ax.collections.remove(self.highlighted_mode)
        
        if len(items) == 0:
            self.highlighted_mode = None
            self.canvas.draw()
            return
        
        fr = self.tool_instance.model_selector.currentData()
        if fr is None:
            return 

        for item in items:
            if item.column() == 0:
                row = item.data(Qt.UserRole)
        
        frequency = [freq.frequency for freq in fr.other['frequency'].data][row]
        if frequency < 0:
            return
        
        if ax.get_ylim()[1] > 50:
            y_vals = (10**(2-0.9), 100)
        else:
            y_vals = (0, 1)
            
        self.highlighted_mode = ax.vlines(frequency, *y_vals, color='r', zorder=-1)
        
        self.canvas.draw()

    def cleanup(self):
        self.tool_instance.ir_plot = None
        
        super().cleanup()

