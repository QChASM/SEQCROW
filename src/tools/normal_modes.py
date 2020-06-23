import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.ui.widgets import ColorButton
from chimerax.bild.bild import read_bild
from chimerax.core.models import ADD_MODELS, REMOVE_MODELS
from chimerax.std_commands.coordset_gui import CoordinateSetSlider
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import FloatArg, TupleOf, IntArg
from chimerax.core.commands import run

from AaronTools.atoms import Atom
from AaronTools.geometry import Geometry
from AaronTools.trajectory import Pathway

from io import BytesIO

from os.path import basename

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QGridLayout, QPushButton, QTabWidget, QComboBox, \
                            QTableWidget, QTableView, QWidget, QVBoxLayout, QTableWidgetItem, \
                            QFormLayout, QCheckBox, QHeaderView

from ..managers import FILEREADER_CHANGE
from SEQCROW.utils import iter2str

#TODO:
#make double clicking something in the table visualize it

class _NormalModeSettings(Settings):
    AUTO_SAVE = {
        'arrow_color': Value((0.0, 1.0, 0.0, 1.0), TupleOf(FloatArg, 4), iter2str),
        'arrow_scale': Value(1.5, FloatArg, str),
        'anim_scale': Value(0.2, FloatArg, str),
        'anim_duration': Value(120, IntArg, str),
        'anim_fps': Value(60, IntArg), 
    }

class FPSSpinBox(QSpinBox):
    """spinbox that makes sure the value goes evenly into 60"""
    def validate(self, text, pos):
        if pos < len(text) or len(text) < 2:
            return (QValidator.Intermediate, text, pos)
        
        try:
            value = int(text)
        except:
            return (QValidator.Invalid, text, pos)
        
        if 60 % value != 0:
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


class NormalModes(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    help = "https://github.com/QChASM/SEQCROW/wiki/Visualize-Normal-Modes-Tool"
    
    def __init__(self, session, name):
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)        
        
        self.vec_mw_bool = False
        
        self.settings = _NormalModeSettings(session, name)
        
        self._build_ui()

        self.refresh_models()

        self._add_handler = session.triggers.add_handler(ADD_MODELS, self.refresh_models)
        self._refresh_handler = session.triggers.add_handler(REMOVE_MODELS, self.refresh_models)
        self._fr_update_handler = session.filereader_manager.triggers.add_handler(FILEREADER_CHANGE, self.refresh_models)

    def _build_ui(self):
        layout = QGridLayout()
        
        #select which molecule's frequencies to visualize
        model_selector = QComboBox()
                
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
        self.vector_color.setToolTip("color of vectors")
        self.vector_color.set_color(self.settings.arrow_color)
        vector_opts.addRow("vector color:", self.vector_color)
        
        show_vec_button = QPushButton("display selected mode")
        show_vec_button.clicked.connect(self.show_vec)
        vector_opts.addRow(show_vec_button)
        
        close_vec_button = QPushButton("remove selected mode vectors")
        close_vec_button.clicked.connect(self.close_vec)
        vector_opts.addRow(close_vec_button)
        
        animate_tab = QWidget()
        anim_opts = QFormLayout(animate_tab)
        
        self.anim_scale = QDoubleSpinBox()
        self.anim_scale.setSingleStep(0.1)
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
                                 "animation speed in ChimeraX might be slower, depending on your hardware")
        anim_opts.addRow("animation FPS:", self.anim_fps)

        show_anim_button = QPushButton("animate selected mode")
        show_anim_button.clicked.connect(self.show_anim)
        anim_opts.addRow(show_anim_button)
        
        stop_anim_button = QPushButton("stop animation")
        stop_anim_button.clicked.connect(self.stop_anim)
        anim_opts.addRow(stop_anim_button)
        
        self.display_tabs.addTab(vector_tab, "vectors")
        self.display_tabs.addTab(animate_tab, "animate")
        
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
        self.rows = []
        
        for i, mode in enumerate(freq_data):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            freq = QTableWidgetItem()
            freq.setData(Qt.DisplayRole, round(mode.frequency, 2))
            self.table.setItem(row, 0, freq)
            self.rows.append(freq)
            
            intensity = QTableWidgetItem()
            if mode.intensity is not None:
                intensity.setData(Qt.DisplayRole, round(mode.intensity, 2))
            self.table.setItem(row, 1, intensity)
    
    def refresh_models(self, *args, **kwargs):
        """refresh the list of models with frequency data and add or remove items from the combobox"""        
        #remove in reverse order b/c sometimes they don't get removed in forwards order
        #TODO: we use FileReaders now, not models - look for those
        for i in range(self.model_selector.count(), -1, -1):
            if self.model_selector.itemData(i) not in self.session.filereader_manager.frequency_filereaders:
                self.model_selector.removeItem(i)
                
        for model in self.session.filereader_manager.frequency_models:
            if len(model.atomspec) > 1:
                for fr in self.session.filereader_manager.filereader_dict[model]:
                    if 'frequency' not in fr.other:
                        continue
                        
                    if self.model_selector.findData(fr) == -1:
                        self.model_selector.addItem("%s (%s)" % (basename(fr.name), model.atomspec), fr)

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
        mode = modes[::2][0]
        mode = self.rows.index(mode)
        
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
            mode = modes[::2][0]
            mode = self.rows.index(mode)

        scale = self.vec_scale.value()
                
        self.settings.arrow_scale = scale
                
        color = self.vector_color.get_color()
        
        color = [c/255. for c in color]
        
        self.settings.arrow_color = tuple(color)
        
        #reset coordinates b/c movie maight be playing
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
            mode = modes[::2][0]
            mode = self.rows.index(mode)

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
    
    def delete(self):
        """overload delete"""
        self.session.triggers.remove_handler(self._add_handler)
        self.session.triggers.remove_handler(self._refresh_handler)
        self.session.filereader_manager.triggers.remove_handler(self._fr_update_handler)
        super().delete()
