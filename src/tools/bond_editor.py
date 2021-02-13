import numpy as np

from chimerax.atomic import selected_atoms, selected_bonds, selected_pseudobonds, AtomicStructure
from chimerax.atomic.colors import element_color
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.ui.widgets import ColorButton
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands import run, BoolArg, ColorArg, FloatArg, IntArg, TupleOf

from Qt.QtCore import Qt
from Qt.QtWidgets import QGridLayout, QFormLayout, QCheckBox, QTabWidget, QPushButton, \
                         QSpinBox, QDoubleSpinBox, QWidget, QLabel, QStatusBar, QSizePolicy, \
                         QGroupBox, QComboBox

from SEQCROW.utils import iter2str
from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.selectors import get_fragment
from SEQCROW.widgets import PeriodicTable
from SEQCROW.tools.structure_editing import PTable

from AaronTools.finders import AnyTransitionMetal
from AaronTools.atoms import BondOrder
from AaronTools.const import ELEMENTS

ORDER_BOND_ORDER = BondOrder()


class BondOrderSpinBox(QDoubleSpinBox):
    def stepBy(self, step):
        val = self.value()
        if step > 0:
            if val < 1.5:
                self.setValue(1.5)
            elif val < 2.0:
                self.setValue(2.0)
            elif val <= 3.0:
                self.setValue(3.0)
        
        elif step < 0:
            if val <= 1.5:
                self.setValue(1.0)
            elif val <= 2.0:
                self.setValue(1.5)
            elif val <= 3.0:
                self.setValue(2.0)


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
        self.draw_tsbonds = draw_tsbonds
        
        erase_tsbonds = QPushButton("erase selected TS bonds")
        erase_tsbonds.clicked.connect(self.run_erase_tsbond)
        ts_options.addRow(erase_tsbonds)
        self.erase_tsbonds = erase_tsbonds
        
        
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
        self.draw_tsbonds = draw_tsbonds
        
        erase_bonds = QPushButton("erase selected bonds")
        erase_bonds.clicked.connect(lambda *, ses=self.session: run(ses, "delete bonds sel"))
        bond_options.addRow(erase_bonds)
        self.erase_bonds = erase_bonds

        
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
        self.draw_hbonds = draw_hbonds
        
        erase_hbonds = QPushButton("erase all H-bonds")
        erase_hbonds.clicked.connect(lambda *, ses=self.session: run(ses, "~hbonds"))
        hbond_options.addRow(erase_hbonds)
        self.erase_hbonds = erase_hbonds


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
        self.draw_tm_bonds = draw_tm_bonds
        
        erase_tm_bonds = QPushButton("erase all metal coordination bonds")
        erase_tm_bonds.clicked.connect(self.del_tm_bond)
        tm_bond_options.addRow(erase_tm_bonds)
        self.erase_tm_bonds = erase_tm_bonds
        
        
        bond_length_tab = QWidget()
        bond_length_layout = QFormLayout(bond_length_tab)
        
        self.bond_distance = QDoubleSpinBox()
        self.bond_distance.setRange(0.5, 10.0)
        self.bond_distance.setSingleStep(0.05)
        self.bond_distance.setValue(1.51)
        self.bond_distance.setSuffix(" \u212B")
        bond_length_layout.addRow("bond length:", self.bond_distance)
        
        self.move_fragment = QComboBox()
        self.move_fragment.addItems(["both", "smaller", "larger"])
        bond_length_layout.addRow("move side:", self.move_fragment)
        
        bond_lookup = QGroupBox("lookup bond length:")
        bond_lookup_layout = QGridLayout(bond_lookup)
        
        bond_lookup_layout.addWidget(
            QLabel("elements:"),
            0, 0,
        )
        
        self.ele1 = QPushButton("C")
        self.ele1.setMinimumWidth(int(1.3*self.ele1.fontMetrics().boundingRect("QQ").width()))
        self.ele1.setMaximumWidth(int(1.3*self.ele1.fontMetrics().boundingRect("QQ").width()))
        self.ele1.setMinimumHeight(int(1.5*self.ele1.fontMetrics().boundingRect("QQ").height()))
        self.ele1.setMaximumHeight(int(1.5*self.ele1.fontMetrics().boundingRect("QQ").height()))
        self.ele1.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        ele_color = tuple(list(element_color(ELEMENTS.index("C")))[:-1])
        self.ele1.setStyleSheet(
            "QPushButton { background: rgb(%i, %i, %i); color: %s; font-weight: bold; }" % (
                *ele_color,
                'white' if sum(
                    int(x < 130) - int(x > 225) for x in ele_color
                ) - int(ele_color[1] > 225) +
                int(ele_color[2] > 200) >= 2 else 'black'
            )
        )
        self.ele1.clicked.connect(lambda *args, button=self.ele1: self.open_ptable(button))
        bond_lookup_layout.addWidget(self.ele1, 0, 1, Qt.AlignRight | Qt.AlignTop)
        
        bond_lookup_layout.addWidget(QLabel("-"), 0, 2, Qt.AlignHCenter | Qt.AlignVCenter)
        
        self.ele2 = QPushButton("C")
        self.ele2.setMinimumWidth(int(1.3*self.ele2.fontMetrics().boundingRect("QQ").width()))
        self.ele2.setMaximumWidth(int(1.3*self.ele2.fontMetrics().boundingRect("QQ").width()))
        self.ele2.setMinimumHeight(int(1.5*self.ele2.fontMetrics().boundingRect("QQ").height()))
        self.ele2.setMaximumHeight(int(1.5*self.ele2.fontMetrics().boundingRect("QQ").height()))
        self.ele2.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        ele_color = tuple(list(element_color(ELEMENTS.index("C")))[:-1])
        self.ele2.setStyleSheet(
            "QPushButton { background: rgb(%i, %i, %i); color: %s; font-weight: bold; }" % (
                *ele_color,
                'white' if sum(
                    int(x < 130) - int(x > 225) for x in ele_color
                ) - int(ele_color[1] > 225) +
                int(ele_color[2] > 200) >= 2 else 'black'
            )
        )
        self.ele2.clicked.connect(lambda *args, button=self.ele2: self.open_ptable(button))
        bond_lookup_layout.addWidget(self.ele2, 0, 3, Qt.AlignLeft | Qt.AlignTop)
        
        bond_lookup_layout.addWidget(QLabel("bond order:"), 1, 0)
        
        self.bond_order = BondOrderSpinBox()
        self.bond_order.setRange(1., 3.)
        self.bond_order.setValue(1)
        self.bond_order.setSingleStep(0.5)
        self.bond_order.setDecimals(1)
        self.bond_order.valueChanged.connect(self.check_bond_lengths)
        bond_lookup_layout.addWidget(self.bond_order, 1, 1, 1, 3)
        
        bond_lookup_layout.setColumnStretch(0, 0)
        bond_lookup_layout.setColumnStretch(1, 0)
        bond_lookup_layout.setColumnStretch(2, 0)
        bond_lookup_layout.setColumnStretch(3, 1)
        
        bond_length_layout.addRow(bond_lookup)
        
        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        bond_lookup_layout.addWidget(self.status, 2, 0, 1, 4)
        
        self.do_bond_change = QPushButton("change selected bond lengths")
        self.do_bond_change.clicked.connect(self.change_bond_length)
        bond_length_layout.addRow(self.do_bond_change)
        
        
        tabs.addTab(bond_tab, "covalent bonds")
        tabs.addTab(ts_bond_tab, "TS bonds")
        tabs.addTab(hbond_tab, "H-bonds")
        tabs.addTab(tm_bond_tab, "coordination bonds")
        tabs.addTab(bond_length_tab, "bond length")
        
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

    def open_ptable(self, button):
        self.tool_window.create_child_window("select element", window_class=PTable2, button=button, callback=self.check_bond_lengths)

    def check_bond_lengths(self, *args):
        ele1 = self.ele1.text()
        ele2 = self.ele2.text()
        key = ORDER_BOND_ORDER.key(ele1, ele2)
        
        order = "%.1f" % self.bond_order.value()
        if key in ORDER_BOND_ORDER.bonds and order in ORDER_BOND_ORDER.bonds[key]:
            self.bond_distance.setValue(ORDER_BOND_ORDER.bonds[key][order])
            self.status.showMessage("")
        else:
            self.status.showMessage("no bond data for %s-%s %sx bonds" % (ele1, ele2, order))

    def change_bond_length(self, *args):
        dist = self.bond_distance.value()
        
        atom_pairs = []
        
        sel = selected_atoms(self.session)
        if len(sel) == 2 and sel[0].structure is sel[1].structure:
            atom_pairs.append(sel)
            
        for bond in selected_bonds(self.session):
            if not all(atom in sel for atom in bond.atoms):
                atom_pairs.append(bond.atoms)
        
        for bond in selected_pseudobonds(self.session):
            if not all(atom in sel for atom in bond.atoms):
                atom_pairs.append(bond.atoms)
        
        for pair in atom_pairs:
            atom1, atom2 = pair
            frag1 = get_fragment(atom1, stop=atom2, max_len=atom1.structure.num_atoms)
            frag2 = get_fragment(atom2, stop=atom1, max_len=atom1.structure.num_atoms)
            
            v = atom2.coord - atom1.coord
            
            cur_dist = np.linalg.norm(v)
            change = dist - cur_dist
            
            if self.move_fragment.currentText() == "both":
                change = 0.5 * change
                frag1.coords -= change * v / cur_dist 
                frag2.coords += change * v / cur_dist 
            elif self.move_fragment.currentText() == "smaller":
                if len(frag1) < len(frag2) or (
                    len(frag1) == len(frag2) and sum(frag1.elements.masses) < sum(frag2.elements.masses)
                ):
                    frag1.coords -= change * v / cur_dist
                else:
                    frag2.coords += change * v / cur_dist
            elif self.move_fragment.currentText() == "larger":
                if len(frag1) > len(frag2) or (
                    len(frag1) == len(frag2) and sum(frag1.elements.masses) > sum(frag2.elements.masses)
                ):
                    frag1.coords -= change * v / cur_dist
                else:
                    frag2.coords += change * v / cur_dist


class PTable2(PTable):
    def __init__(self, tool_instance, title, callback, *args,**kwargs):
        self.callback = callback
        super().__init__(tool_instance, title, *args, **kwargs)
    
    def element_changed(self, *args, **kwargs):
        super().element_changed(*args, **kwargs)
        
        self.callback()
        
        self.destroy()