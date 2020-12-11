import numpy as np

from chimerax.atomic import selected_atoms, selected_bonds, AtomicStructure
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.ui.widgets import ColorButton
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands import run, BoolArg, ColorArg, FloatArg, IntArg, TupleOf

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QFormLayout, QCheckBox, QTabWidget, QPushButton, \
                            QSpinBox, QDoubleSpinBox, QWidget

from SEQCROW.utils import iter2str
from SEQCROW.residue_collection import ResidueCollection

from AaronTools.finders import AnyTransitionMetal


class _BondEditorSettings(Settings):
    AUTO_SAVE = {
        "hbond_color":         Value((0., 0.75, 1., 1.), TupleOf(FloatArg, 4), iter2str), 
        "hbond_dashes":        Value(6, IntArg), 
        "hbond_radius":        Value(0.075, FloatArg),         
        "tm_bond_color":       Value((147./255, 112./255, 219./255, 1.), TupleOf(FloatArg, 4), iter2str), 
        "tm_bond_dashes":      Value(6, IntArg), 
        "tm_bond_radius":      Value(0.075, FloatArg), 
        "tsbond_color":        Value((0.67, 1., 1., 1.), TupleOf(FloatArg, 4), iter2str), 
        "tsbond_transparency": Value(75., FloatArg),
        "tsbond_radius":       Value(0.16, FloatArg),
        "bond_color":          Value((0., 0., 0., 1.), TupleOf(FloatArg, 4), iter2str),
        "bond_halfbond":       Value(True, BoolArg), 
        "bond_radius":         Value(0.16, FloatArg), 
    }

class BondEditor(ToolInstance):

    help = "https://github.com/QChASM/SEQCROW/wiki/Bond-Editor-Tool"
    SESSION_ENDURING = True
    SESSION_SAVE = True
    
    def __init__(self, session, name):
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)
        
        self.settings = _BondEditorSettings(session, name)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QGridLayout()
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        ts_bond_tab = QWidget()
        ts_options = QFormLayout(ts_bond_tab)
        
        self.tsbond_color = ColorButton(has_alpha_channel=False, max_size=(16, 16))
        self.tsbond_color.set_color(self.settings.tsbond_color)
        ts_options.addRow("color:", self.tsbond_color)
        
        self.tsbond_transparency = QSpinBox()
        self.tsbond_transparency.setRange(1, 99)
        self.tsbond_transparency.setValue(self.settings.tsbond_transparency)
        self.tsbond_transparency.setSuffix("%")
        ts_options.addRow("transparency:", self.tsbond_transparency)
        
        self.tsbond_radius = QDoubleSpinBox()
        self.tsbond_radius.setRange(0.01, 1)
        self.tsbond_radius.setDecimals(3)
        self.tsbond_radius.setSingleStep(0.005)
        self.tsbond_radius.setSuffix(" \u212B")
        self.tsbond_radius.setValue(self.settings.tsbond_radius)
        ts_options.addRow("radius:", self.tsbond_radius)
        
        draw_tsbonds = QPushButton("draw TS bonds on selected atoms/bonds")
        draw_tsbonds.clicked.connect(self.run_tsbond)
        ts_options.addRow(draw_tsbonds)
        
        erase_tsbonds = QPushButton("erase selected TS bonds")
        erase_tsbonds.clicked.connect(self.run_erase_tsbond)
        ts_options.addRow(erase_tsbonds)
        
        
        bond_tab = QWidget()
        bond_options = QFormLayout(bond_tab)
        
        self.bond_halfbond = QCheckBox()
        self.bond_halfbond.setChecked(self.settings.bond_halfbond)
        self.bond_halfbond.setToolTip("each half of the bond will be colored according to the atom's color")
        bond_options.addRow("half-bond:", self.bond_halfbond)
        
        self.bond_color = ColorButton(has_alpha_channel=True, max_size=(16, 16))
        self.bond_color.set_color(self.settings.bond_color)
        self.bond_color.setEnabled(self.bond_halfbond.checkState() != Qt.Checked)
        self.bond_halfbond.stateChanged.connect(lambda state, widget=self.bond_color: self.bond_color.setEnabled(state != Qt.Checked))
        bond_options.addRow("color:", self.bond_color)
        
        self.bond_radius = QDoubleSpinBox()
        self.bond_radius.setRange(0.01, 1)
        self.bond_radius.setDecimals(3)
        self.bond_radius.setSingleStep(0.005)
        self.bond_radius.setSuffix(" \u212B")
        self.bond_radius.setValue(self.settings.bond_radius)
        bond_options.addRow("radius:", self.bond_radius)
        
        draw_tsbonds = QPushButton("draw bond between selected atoms")
        draw_tsbonds.clicked.connect(self.run_bond)
        bond_options.addRow(draw_tsbonds)
        
        erase_bonds = QPushButton("erase selected bonds")
        erase_bonds.clicked.connect(lambda *, ses=self.session: run(ses, "delete bonds sel"))
        bond_options.addRow(erase_bonds)

        
        hbond_tab = QWidget()
        hbond_options = QFormLayout(hbond_tab)
        
        self.hbond_color = ColorButton(has_alpha_channel=True, max_size=(16, 16))
        self.hbond_color.set_color(self.settings.hbond_color)
        hbond_options.addRow("color:", self.hbond_color)
        
        self.hbond_radius = QDoubleSpinBox()
        self.hbond_radius.setDecimals(3)
        self.hbond_radius.setSuffix(" \u212B")
        self.hbond_radius.setValue(self.settings.hbond_radius)
        hbond_options.addRow("radius:", self.hbond_radius)
        
        self.hbond_dashes = QSpinBox()
        self.hbond_dashes.setRange(0, 28)
        self.hbond_dashes.setSingleStep(2)
        self.hbond_radius.setSingleStep(0.005)
        self.hbond_dashes.setValue(self.settings.hbond_dashes)
        hbond_options.addRow("dashes:", self.hbond_dashes)
        
        draw_hbonds = QPushButton("draw H-bonds")
        draw_hbonds.clicked.connect(self.run_hbond)
        hbond_options.addRow(draw_hbonds)
        
        erase_hbonds = QPushButton("erase all H-bonds")
        erase_hbonds.clicked.connect(lambda *, ses=self.session: run(ses, "~hbonds"))
        hbond_options.addRow(erase_hbonds)


        tm_bond_tab = QWidget()
        tm_bond_options = QFormLayout(tm_bond_tab)
        
        self.tm_bond_color = ColorButton(has_alpha_channel=True, max_size=(16, 16))
        self.tm_bond_color.set_color(self.settings.tm_bond_color)
        tm_bond_options.addRow("color:", self.tm_bond_color)
        
        self.tm_bond_radius = QDoubleSpinBox()
        self.tm_bond_radius.setDecimals(3)
        self.tm_bond_radius.setSuffix(" \u212B")
        self.tm_bond_radius.setValue(self.settings.tm_bond_radius)
        tm_bond_options.addRow("radius:", self.tm_bond_radius)
        
        self.tm_bond_dashes = QSpinBox()
        self.tm_bond_dashes.setRange(0, 28)
        self.tm_bond_dashes.setSingleStep(2)
        self.tm_bond_radius.setSingleStep(0.005)
        self.tm_bond_dashes.setValue(self.settings.tm_bond_dashes)
        tm_bond_options.addRow("dashes:", self.tm_bond_dashes)
        
        draw_tm_bonds = QPushButton("draw metal coordination bonds")
        draw_tm_bonds.clicked.connect(self.run_tm_bond)
        tm_bond_options.addRow(draw_tm_bonds)
        
        erase_tm_bonds = QPushButton("erase all metal coordination bonds")
        erase_tm_bonds.clicked.connect(self.del_tm_bond)
        tm_bond_options.addRow(erase_tm_bonds)
        
        
        tabs.addTab(bond_tab, "covalent bonds")
        tabs.addTab(ts_bond_tab, "TS bonds")
        tabs.addTab(hbond_tab, "H-bonds")
        tabs.addTab(tm_bond_tab, "coordination bonds")
        
        self.tool_window.ui_area.setLayout(layout)
        
        self.tool_window.manage(None)
    
    def run_tsbond(self, *args):
        args = ["tsbond", "sel"]
        
        color = self.tsbond_color.get_color()
        args.extend(["color", "rgb(%i, %i, %i)" % tuple(color[:-1])])
        self.settings.tsbond_color = tuple([c/255. for c in color])
        
        radius = self.tsbond_radius.value()
        args.extend(["radius", "%.3f" % radius])
        self.settings.tsbond_radius = radius
        
        transparency = self.tsbond_transparency.value()
        args.extend(["transparency", "%i" % transparency])
        self.settings.tsbond_transparency = transparency
        
        run(self.session, " ".join(args))
    
    def run_erase_tsbond(self, *args):
        run(self.session, "~tsbond sel")
    
    def run_bond(self, *args):
        # TODO: switch to `bond sel` in 1.2
        sel = selected_atoms(self.session)
        halfbond = self.bond_halfbond.checkState() == Qt.Checked
        self.settings.bond_halfbond = halfbond
        
        if not halfbond:
            color = self.bond_color.get_color()
            color = tuple(x/255. for x in color)
            self.settings.bond_color = color
        
        radius = self.bond_radius.value()
        self.settings.bond_radius = radius
        
        for b in selected_bonds(self.session):
            b.halfbond = halfbond
            if not halfbond:
                b.color = np.array([int(x * 255) for x in color])
            
            b.radius = radius
        
        for i, a1 in enumerate(sel):
            for a2 in sel[:i]:
                if a1.structure is a2.structure and a2 not in a1.neighbors:
                    new_bond = a1.structure.new_bond(a1, a2)
                    new_bond.halfbond = halfbond
                    
                    if not halfbond:
                        new_bond.color = np.array([int(x * 255) for x in color])
                    
                    new_bond.radius = radius

    def run_hbond(self, *args):
        args = ["hbonds", "reveal", "true"]
        
        color = self.hbond_color.get_color()
        args.extend(["color", "rgb(%i, %i, %i)" % tuple(color[:-1])])
        self.settings.hbond_color = tuple([c/255. for c in color])
        
        radius = self.hbond_radius.value()
        args.extend(["radius", "%.3f" % radius])
        self.settings.hbond_radius = radius
        
        dashes = self.hbond_dashes.value()
        args.extend(["dashes", "%i" % dashes])
        self.settings.hbond_dashes = dashes
        
        run(self.session, " ".join(args))
    
    def run_tm_bond(self, *args):
        color = self.tm_bond_color.get_color()
        self.settings.tm_bond_color = tuple([c/255. for c in color])
        
        radius = self.tm_bond_radius.value()
        self.settings.tm_bond_radius = radius

        dashes = self.tm_bond_dashes.value()
        self.settings.tm_bond_dashes = dashes

        
        models = self.session.models.list(type=AtomicStructure)
        for model in models:
            rescol = ResidueCollection(model, bonds_matter=False)
            try:
                tm_list = rescol.find([AnyTransitionMetal(), "Na", "K", "Rb", "Cs", "Fr", "Mg", "Ca", "Sr", "Ba", "Ra"])
                for tm in tm_list:
                    for atom in rescol.atoms:
                        if atom is tm:
                            continue
                        
                        if atom.is_connected(tm):
                            pbg = model.pseudobond_group(model.PBG_METAL_COORDINATION, create_type="normal")
                            pbg.new_pseudobond(tm.chix_atom, atom.chix_atom)
                            pbg.dashes = dashes
                            pbg.color = color
                            pbg.radius = radius
                            
            except LookupError:
                pass

    def del_tm_bond(self, *args):
        models = self.session.models.list(type=AtomicStructure)
        for model in models:
            pbg = model.pseudobond_group(model.PBG_METAL_COORDINATION, create_type=None)
            if pbg is not None:
                pbg.delete()
