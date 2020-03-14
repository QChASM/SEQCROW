import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.ui.widgets import ColorButton
from chimerax.bild.bild import read_bild
from chimerax.core.models import MODEL_DISPLAY_CHANGED, ADD_MODELS
from chimerax.std_commands.coordset_gui import CoordinateSetSlider
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import FloatArg, TupleOf, IntArg

from AaronTools.atoms import Atom
from AaronTools.geometry import Geometry
from AaronTools.trajectory import Pathway

from io import BytesIO

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QGridLayout, QPushButton, QTabWidget, QComboBox, QTableWidget, QTableView, QWidget, QVBoxLayout, QTableWidgetItem, QFormLayout, QCheckBox

from ..managers import FILEREADER_CHANGE
from SEQCRO.settings import tuple2str

class _NormalModeSettings(Settings):
    AUTO_SAVE = {
        'arrow_color': Value((0.0, 1.0, 0.0, 1.0), TupleOf(FloatArg, 4), tuple2str),
        'arrow_scale': Value(1.5, FloatArg, str),
        'anim_scale': Value(0.2, FloatArg, str),
        'anim_duration': Value(101, IntArg, str),
    }

class NormalModes(ToolInstance):
    #XML_TAG ChimeraX :: Tool :: Visualize Normal Modes :: AaronTools :: Visualize normal modes from a Gaussian output file as displacement vectors or as an animation
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    help = "https://github.com/QChASM/ChimAARON/wiki/Visualize-Normal-Modes-Tool"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)        
        
        self.vec_mw_bool = False
        
        self.settings = _NormalModeSettings(self.session, name)
        
        self.models_with_freq = self.session.filereader_manager.frequency_models

        self._build_ui()

        self.refresh_models()

        self._add_handler = self.session.triggers.add_handler(ADD_MODELS, self.refresh_models)
        self._refresh_handler = self.session.filereader_manager.triggers.add_handler(FILEREADER_CHANGE, self.refresh_models)

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
        
        layout.addWidget(table)
        self.table = table
        
        #tab thing to select animation or vectors
        self.display_tabs = QTabWidget()

        self.vector_tab = QWidget()
        self.vector_layout = QVBoxLayout(self.vector_tab)
        vec_opts_form = QWidget()
        vector_opts = QFormLayout(vec_opts_form)
        
        self.vec_scale = QDoubleSpinBox()
        self.vec_scale.setDecimals(1)
        self.vec_scale.setRange(-100.0, 100.0)
        self.vec_scale.setValue(self.settings.arrow_scale)
        self.vec_scale.setSuffix(" \u212B")
        self.vec_scale.setSingleStep(1.0)
        self.vec_scale.setToolTip("vectors will be scaled so that this is the length of the longest vector")
        vector_opts.addRow("vector scale:", self.vec_scale)
        
        self.vec_use_mass_weighted = QCheckBox()
        self.vec_use_mass_weighted.stateChanged.connect(self.change_mw_option)
        self.vec_use_mass_weighted.setToolTip("if checked, vectors will show mass-weighted displacements")
        vector_opts.addRow("use mass-weighted:", self.vec_use_mass_weighted)
        
        self.vector_layout.addWidget(vec_opts_form)
        
        self.vector_color = ColorButton("vector color", has_alpha_channel=True)
        self.vector_color.setToolTip("color of vectors")
        self.vector_color.set_color(self.settings.arrow_color)
        self.vector_layout.addWidget(self.vector_color)
        
        show_vec_button = QPushButton("display selected modes")
        show_vec_button.clicked.connect(self.show_vec)
        self.vector_layout.addWidget(show_vec_button)
        
        self.animate_tab = QWidget()
        self.animate_layout = QVBoxLayout(self.animate_tab)
        anim_opts_form = QWidget()
        anim_opts = QFormLayout(anim_opts_form)
        
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
        self.anim_duration.setToolTip("number of frames in animation")
        self.anim_duration.setSingleStep(10)
        anim_opts.addRow("duration:", self.anim_duration)
        
        self.animate_layout.addWidget(anim_opts_form)
        
        show_anim_button = QPushButton("animate selected mode")
        show_anim_button.clicked.connect(self.show_anim)
        self.animate_layout.addWidget(show_anim_button)
        
        self.display_tabs.addTab(self.vector_tab, "vectors")
        self.display_tabs.addTab(self.animate_tab, "animate")
        
        layout.addWidget(self.display_tabs)
        
        #only the table can stretch
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 0)
        
        self.tool_window.ui_area.setLayout(layout)

        if len(self.models_with_freq) > 0:
            self.create_freq_table(0)

        self.tool_window.manage(None)
        
    def create_freq_table(self, state):
        """populate the table with frequencies from self.models_with_freq[state]"""
        
        self.table.setRowCount(0)

        if state == -1:
            # early return if no frequency models
            return
            
        model = self.models_with_freq[state]
        fr = self.session.filereader_manager.filereader_dict[model]
        
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
        self.models_with_freq = self.session.filereader_manager.frequency_models
            
        for i in range(0, self.model_selector.count()):
            if self.model_selector.itemData(i) not in self.models_with_freq:
                self.model_selector.removeItem(i)
                
        for model in self.models_with_freq:
            if self.model_selector.findData(model) == -1:
                self.model_selector.addItem("%s (%s)" % (model.name, model.atomspec), model)

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

    def show_vec(self):
        """display normal mode displacement vector"""
        model = self.models_with_freq[self.model_selector.currentIndex()]
        fr = self.session.filereader_manager.filereader_dict[model]
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
        coords = np.array([geom.coords()])
        model.add_coordsets(coords, replace=True)
        
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
        
        if hasattr(model, "seqcro_freq_slider") and model.seqcro_freq_slider.structure is not None:
            #close animation slider
            model.seqcro_freq_slider.delete()
    
    def show_anim(self):
        """play selected modes as an animation"""
        model = self.models_with_freq[self.model_selector.currentIndex()]
        fr = self.session.filereader_manager.filereader_dict[model]
        modes = self.table.selectedItems()
        if len([mode for mode in modes if mode.column() == 0]) != 1:
            raise RuntimeError("one mode must be selected")
        else:
            mode = modes[::2][0]
            mode = self.rows.index(mode)

        scale = self.anim_scale.value()
        frames = self.anim_duration.value()
        
        self.settings.anim_scale = scale
        self.settings.anim_duration = frames
        
        geom = Geometry(fr)
        #if the filereader has been processed somewhere else, the atoms might
        #have a chimerax atom associated with them that prevents them from being pickled 
        for atom in geom.atoms:
            if hasattr(atom, "chix_atom"):
                atom.chix_atom = None
                
        coords = np.array([geom.coords()])
        
        vector = fr.other['frequency'].data[mode].vector

        dX = self._get_coord_change(geom, vector, scale)
        
        #atoms can't be deep copied for some reason
        geom_forward = geom.copy()
        geom_forward.update_geometry(geom.coords() + dX)
        geom_reverse = geom.copy()
        geom_reverse.update_geometry(geom.coords() - dX)
        
        S = Pathway([geom_forward, geom, geom_reverse, geom, geom_forward])
        
        coordsets = np.zeros((frames, len(geom.atoms), 3))
        for i, t in enumerate(np.linspace(0, 1, num=frames, endpoint=False)):
            coordsets[i] = S.Geom_func(t).coords()
            
        model.add_coordsets(coordsets, replace=True)
        for i, coordset in enumerate(coordsets):
            model.active_coordset_id = i + 1

            for atom, coord in zip(model.atoms, coordset):
                atom.coord = coord
        
        for atom, chix_atom in zip(geom.atoms, model.atoms):
            atom.chix_atom = chix_atom
        
        if hasattr(model, "seqcro_freq_slider") and model.seqcro_freq_slider.structure is not None:
            model.seqcro_freq_slider.delete()
            
        model.seqcro_freq_slider = CoordinateSetSlider(self.session, model)
        model.seqcro_freq_slider.play_cb()

    def delete(self):
        """overload delete"""
        self.session.triggers.remove_handler(self._add_handler)
        self.session.filereader_manager.triggers.remove_handler(self._refresh_handler)
        super().delete()
