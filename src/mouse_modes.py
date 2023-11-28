from AaronTools.atoms import Atom
from AaronTools.const import RADII

from chimerax.atomic import Atoms, Bonds, AtomicStructure
from chimerax.atomic.structure import (
    PickedAtoms,
    PickedBonds,
    PickedAtom,
    PickedBond, 
    PickedResidue,
    PickedResidues,
    PickedPseudobond,
)
from chimerax.core.commands import run
from chimerax.core.tools import ToolInstance
from chimerax.markers import MarkerSet, create_link
from chimerax.mouse_modes import MouseMode
from chimerax.ui.gui import MainToolWindow

from Qt.QtCore import Qt
from Qt.QtWidgets import QPushButton, QComboBox, QFormLayout, QCheckBox, QLineEdit

from SEQCROW.managers.filereader_manager import apply_seqcrow_preset
from SEQCROW.finders import AtomSpec
from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.selectors import get_fragment, canonical_rank
from SEQCROW.widgets import PeriodicTable, ModelComboBox
from SEQCROW.libraries import SubstituentTable

import numpy as np


class SelectConnectedMouseMode(MouseMode):
    """select everything with a bonding path to clicked atoms"""
    name = "select fragment"
    icon_file = "icons/connected.png"
    
    def __init__(self, session):
        super().__init__(session)
        
        self.minimum_drag_pixels = 5
        self.drag_color = (100, 218, 76, 255)
        # self.drag_color = (155, 37, 179, 255)
        self._drawn_rectangle = None
        self._dragging = False
    
    def mouse_drag(self, event):
        if self._is_drag(event):
            self._undraw_drag_rectangle()
            self._draw_drag_rectangle(event)
    
    def mouse_up(self, event):
        self._undraw_drag_rectangle()
        self._dragging = False

        set_sel = event.shift_down()

        if self._is_drag(event):
            sx, sy = self.mouse_down_position
            x, y = event.position()
            pick = self.view.rectangle_pick(sx, sy, x, y)
            self.select_pick(pick, set_sel)
        
        else:
            x, y = event.position()
            pick = self.view.picked_object(x, y)
            self.select_pick(pick, set_sel)
        
        super().mouse_up(event)

    def _is_drag(self, event):
        dp = self.mouse_down_position
        if dp is None:
            return False
        
        if self._dragging:
            return True
        
        dx, dy = dp
        x, y = event.position()
        self._dragging = abs(x - dx) + abs(y - dy) > self.minimum_drag_pixels

        return self._dragging

    def _draw_drag_rectangle(self, event):
        dx, dy = self.mouse_down_position
        x, y = event.position()
        view = self.session.main_view
        w, h = view.window_size
        view.draw_xor_rectangle(dx, h - dy, x, h - y, self.drag_color)
        self._drawn_rectangle = ((dx, dy), (x, y))

    def _undraw_drag_rectangle(self):
        dr = self._drawn_rectangle
        if dr:
            (dx, dy), (x, y) = dr
            view = self.session.main_view
            w, h = view.window_size
            view.draw_xor_rectangle(dx, h - dy, x, h - y, self.drag_color)
            self._drawn_rectangle = None

    def vr_press(self, event):
        # Virtual reality hand controller button press.
        pick = event.picked_object(self.view)
        self.select_pick(pick, False)

    def select_pick(self, pick, set_sel):
        if set_sel:
            self.session.selection.clear()

        if pick:
            atoms = Atoms()
            bonds = Bonds()
            if not hasattr(pick, "__iter__"):
                pick = [pick]

            first_selected = None
            for p in pick:
                if isinstance(p, PickedAtoms):
                    for atom in p.atoms:
                        if atom in atoms:
                            continue
                        connected_atoms = get_fragment(atom, max_len=atom.structure.num_atoms)
                        atoms = atoms.merge(connected_atoms)
                        if first_selected is None:
                            first_selected = atoms[0].selected

                elif isinstance(p, PickedAtom):
                    if p.atom in atoms:
                        continue
                    connected_atoms = get_fragment(
                        p.atom,
                        max_len=p.atom.structure.num_atoms
                    )
                    atoms = atoms.merge(connected_atoms)
                    if first_selected is None:
                        first_selected = atoms[0].selected

                elif isinstance(p, PickedBonds):
                    for bond in p.bonds:
                        if bond.atoms[0] in atoms:
                            continue
                        connected_atoms = get_fragment(
                            bond.atoms[0],
                            max_len=bond.structure.num_atoms
                        )
                        atoms = atoms.merge(connected_atoms)
                        if first_selected is None:
                            first_selected = atoms[0].selected

                elif isinstance(p, PickedBond):
                    if p.bond.atoms[0] in atoms:
                        continue
                    connected_atoms = get_fragment(
                        p.bond.atoms[0],
                        max_len=p.bond.structure.num_atoms
                    )
                    atoms = atoms.merge(connected_atoms)
                    if first_selected is None:
                        first_selected = atoms[0].selected

                elif isinstance(p, PickedResidues):
                    for res in p.residues:
                        for atom in res.atoms:
                            if atom in atoms:
                                continue
                            connected_atoms = get_fragment(
                                atom,
                                max_len=res.structure.num_atoms
                            )
                            atoms = atoms.merge(connected_atoms)
                            if first_selected is None:
                                first_selected = atoms[0].selected

                elif isinstance(p, PickedResidue):
                    for atom in p.residue.atoms:
                        if atoms in atoms:
                            continue
                        connected_atoms = get_fragment(
                            atom,
                            max_len=p.residue.structure.num_atoms
                        )
                        atoms = atoms.merge(connected_atoms)
                        if first_selected is None:
                            first_selected = atoms[0].selected

            for atom in atoms:
                for neighbor, bond in zip(atom.neighbors, atom.bonds):
                    bonds = bonds.merge(Bonds([bond]))
            
            if first_selected is not None:
                atoms.selected = not first_selected
                bonds.selected = not first_selected
        else:
            run(self.session, "select clear")


class _BondMarkers(MarkerSet):
    def create_marker(self, atom):
        mark = super().create_marker(atom.coord, atom.color, 1e-8)
        return mark
    
    def create_marker_from_point(self, *args):
        mark = super().create_marker(*args)
        return mark


class _TSBondMarkers(MarkerSet):
    def create_marker(self, atom):
        mark = super().create_marker(atom.coord, (170, 255, 255, 127), 1e-8)
        return mark

    def create_marker_from_point(self, pt, rgba, rad):
        super().create_marker(pt, (170, 255, 255, 127), rad)


class DrawBondMouseMode(MouseMode):
    name = "bond"
    ms_cls = _BondMarkers
    scale = 1.0

    def __init__(self, session):
        super().__init__(session)
        
        self._markerset = None
        self._atom1 = None
        self._atom2 = None
        self._dragging = False
        self.minimum_drag_pixels = 5

    # def mouse_down(self, event):
    #     super().mouse_down(event)
    #     x, y = event.position()
    #     pick = self.view.picked_object(x, y)
    #     if not isinstance(pick, PickedAtom):
    #         return
    #     
    #     self._atom1 = pick.atom
    
    # def _is_drag(self, event):
    #     dp = self.mouse_down_position
    #     if dp is None:
    #         return False
    #     
    #     if self._dragging:
    #         return True
    #     
    #     dx, dy = dp
    #     x, y = event.position()
    #     self._dragging = abs(x - dx) + abs(y - dy) > self.minimum_drag_pixels
    # 
    #     return self._dragging

    # def mouse_drag(self, event):
    #     if not self._dragging and self._atom1:
    #         if self._is_drag(event):
    #             self._markerset = self.ms_cls(self.session, "bond")
    #             self._markerset.create_marker(self._atom1)
    #             self._atom1.structure.add([self._markerset])
    #             return
    # 
    #     if self._markerset:
    #         x, y = event.position()
    #         pick = self.view.picked_object(x, y)
    #         if isinstance(pick, PickedAtom) and pick.atom.structure is self._atom1.structure:
    #             atom2 = pick.atom
    #             if atom2 is self._atom1:
    #                 return
    #             if self._markerset.num_atoms > 1:
    #                 self._markerset.atoms[1].delete()
    #             self._atom2 = atom2
    #             self._markerset.create_marker(atom2)
    #             fake_bond = create_link(*self._markerset.atoms)
    #             fake_bond.halfbond = True
    #             avg_radius = self.avg_bond_radius(self._atom1, self._atom2)
    #             fake_bond.radius = avg_radius
    #         
    #         elif self._atom1:
    #             self._atom2 = None
    #             x1, x2 = self.session.main_view.clip_plane_points(x, y)
    #             v = x2 - x1
    #             v /= np.linalg.norm(v)
    #             p = np.dot(self._atom1.coord - self._atom1.scene_coord - x1, v)
    #             pt = x1 + p * v + (self._atom1.coord - self._atom1.scene_coord)
    #             if self._markerset.num_atoms > 1:
    #                 self._markerset.atoms[1].delete()
    # 
    #             avg_radius = self.avg_bond_radius(self._atom1)
    # 
    #             self._markerset.create_marker_from_point(
    #                 pt,
    #                 self._atom1.color,
    #                 avg_radius,
    #             )
    #             fake_bond = create_link(*self._markerset.atoms)
    #             fake_bond.halfbond = True
    # 
    #             fake_bond.radius = avg_radius

    def reset(self):
        if self._markerset:
            self._markerset.delete()
        self._markerset = None
        self._atom1 = None
        self._atom = None
        self._dragging = False

    def avg_bond_radius(self, *args):
        count = 0
        avg = 0
        for atom in args:
            for bond in atom.bonds:
                avg += bond.radius
                count += 1
        
        if count:
            avg /= count
        else:
            avg = 0.2
        
        return self.scale * avg

    def vr_press(self, event):
        self.mouse_up(event)

    def mouse_up(self, event):
        atom = False
        super().mouse_up(event)
        if self._atom1 is not None and self._atom1.deleted:
            self._atom1 = None

        x, y = event.position()
        pick = self.view.picked_object(x, y)

        
        if isinstance(pick, PickedBond) and not self._markerset:
            bond = pick.bond
            run(self.session, "~bond %s" % bond.atomspec)
            self.reset()
            return

        if isinstance(pick, PickedAtom) and not self._atom1:
            self._atom1 = pick.atom
            self.session.logger.status("drawing bond between %s and..." % self._atom1.atomspec)
            return

        if (
            isinstance(pick, PickedAtom) and
            pick.atom.structure is self._atom1.structure and
            pick.atom is not self._atom1
        ):
            atom = pick.atom
        
        if not atom:
            self.session.logger.status("no atom clicked - not drawing a new bond")
            return

        if atom.structure is self._atom1.structure and atom is not self._atom1:
            if atom not in self._atom1.neighbors:
                avg_radius = self.avg_bond_radius(self._atom1, atom)
                new_bond = atom.structure.new_bond(atom, self._atom1)
                self.session.logger.status(
                    "drew bond between %s and %s" % (self._atom1.atomspec, atom.atomspec)
                )
                new_bond.radius = avg_radius

        self.reset()


class DrawTSBondMouseMode(DrawBondMouseMode):
    name = "tsbond"
    scale = 1.0
    ms_cls = _TSBondMarkers


    def vr_press(self, event):
        self.mouse_up(event)

    def mouse_up(self, event):
        atom = False
        MouseMode.mouse_up(self, event)
        if self._atom1 is not None and self._atom1.deleted:
            self._atom1 = None

        x, y = event.position()
        pick = self.view.picked_object(x, y)
        
        if isinstance(pick, PickedPseudobond):
            bond = pick.pbond
            if bond.group.name == "TS bonds":
                atom1, atom2 = bond.atoms
                run(self.session, "~tsbond %s %s" % (atom1.atomspec, atom2.atomspec))
                self.reset()
            return

        if isinstance(pick, PickedBond):
            bond = pick.bond
            run(self.session, "tsbond %s" % bond.atomspec)
            self.reset()
            return

        if isinstance(pick, PickedAtom) and not self._atom1:
            self._atom1 = pick.atom
            self.session.logger.status("drawing TS bond between %s and..." % self._atom1.atomspec)
            return

        if (
            isinstance(pick, PickedAtom) and
            pick.atom.structure is self._atom1.structure and
            pick.atom is not self._atom1
        ):
            atom = pick.atom
        
        if not atom:
            self.session.logger.status("not atom clicked - not drawing a new TS bond")
            return

        if atom.structure is self._atom1.structure and atom is not self._atom1:
            avg_radius = self.avg_bond_radius(self._atom1, atom)
            self.session.logger.status(
                "drew TS bond between %s and %s" % (self._atom1.atomspec, atom.atomspec)
            )

            run(
                self.session,
                "tsbond %s %s radius %.3f" % (
                    self._atom1.atomspec,
                    atom.atomspec,
                    avg_radius,
                )
            )

        self.reset()


class DrawCoordinationBondMouseMode(DrawBondMouseMode):
    name = "coordinationbond"
    scale = 1.0

    def vr_press(self, event):
        self.mouse_up(event)

    def mouse_up(self, event):
        atom = False
        MouseMode.mouse_up(self, event)
        if self._atom1 is not None and self._atom1.deleted:
            self._atom1 = None

        x, y = event.position()
        pick = self.view.picked_object(x, y)
        
        if isinstance(pick, PickedPseudobond):
            bond = pick.pbond
            if bond.group.name == bond.atoms[0].structure.PBG_METAL_COORDINATION:
                # run(self.session, "bond %s %s" % (bond.atoms[0].atomspec, bond.atoms[1].atomspec))
                bond.delete()
                self.reset()
            return

        if isinstance(pick, PickedBond):
            bond = pick.bond
            self.draw_new_pbond(*bond.atoms)
            bond.delete()
            self.reset()
            return

        if isinstance(pick, PickedAtom) and not self._atom1:
            self._atom1 = pick.atom
            self.session.logger.status("drawing coordination bond between %s and..." % self._atom1.atomspec)
            return

        if (
            isinstance(pick, PickedAtom) and
            pick.atom.structure is self._atom1.structure and
            pick.atom is not self._atom1
        ):
            atom = pick.atom
        
        if not atom:
            self.session.logger.status("not atom clicked - not drawing a new coordination bond")
            return

        if atom.structure is self._atom1.structure and atom is not self._atom1:
            self.draw_new_pbond(self._atom1, atom)
            self.session.logger.status("drew new coordination bond between %s and %s" % (
                atom.atomspec, self._atom1.atomspec,
            ))
            for bond in self._atom1.bonds:
                if atom in bond.atoms:
                    bond.delete()
                    break
            self.reset()

    def draw_new_pbond(self, atom1, atom2):
        try:
            pbg = atom1.structure.pseudobond_group(
                atom1.structure.PBG_METAL_COORDINATION,
                create_type=1
            )
        except TypeError:
            pbg = atom1.structure.pseudobond_group(
                atom1.structure.PBG_METAL_COORDINATION,
                create_type=2
            )
        pbg.new_pseudobond(atom1, atom2)
        # bug in older versions of ChimeraX where new pseudobonds aren't 
        # displayed until something else changes
        # change the number of dashes
        pbg.dashes += 2
        pbg.dashes -= 2


class _ElementPicker(ToolInstance):
    def __init__(self, *args):
        super().__init__(*args)
        
        self.tool_window = MainToolWindow(self)
        self._build_ui()
    
    def _build_ui(self):
        layout = QFormLayout()
        
        initial_elements = []
        if ChangeElementMouseMode.element:
            initial_elements = [ChangeElementMouseMode.element]
        else:
            initial_elements = ["C"]
        
        self.periodic_table = PeriodicTable(
            select_multiple=False,
            initial_elements=initial_elements
        )
        self.periodic_table.elementSelectionChanged.connect(self.element_changed)
        layout.addRow(self.periodic_table)
        
        self.vsepr = QComboBox()
        self.vsepr.addItems([
            "do not change",                  # 0
            
            "linear (1 bond)",                # 1
            
            "linear (2 bonds)",               # 2 
            "trigonal planar (2 bonds)",      # 3
            "tetrahedral (2 bonds)",          # 4 
            
            "trigonal planar",                # 5
            "tetrahedral (3 bonds)",          # 6
            "T-shaped",                       # 7
            
            "trigonal pyramidal",             # 8
            "tetrahedral",                    # 9
            "sawhorse",                       #10
            "seesaw",                         #11
            "square planar",                  #12
            
            "trigonal bipyramidal",           #13
            "square pyramidal",               #14
            "pentagonal",                     #15
            
            "octahedral",                     #16
            "hexagonal",                      #17
            "trigonal prismatic",             #18
            "pentagonal pyramidal",           #19
            
            "capped octahedral",              #20
            "capped trigonal prismatic",      #21
            "heptagonal",                     #22
            "hexagonal pyramidal",            #23
            "pentagonal bipyramidal",         #24
            
            "biaugmented trigonal prismatic", #25
            "cubic",                          #26
            "elongated trigonal bipyramidal", #27
            "hexagonal bipyramidal",          #28
            "heptagonal pyramidal",           #29
            "octagonal",                      #30
            "square antiprismatic",           #31
            "trigonal dodecahedral",          #32
            
            "capped cube",                    #33
            "capped square antiprismatic",    #34
            "enneagonal",                     #35
            "heptagonal bipyramidal",         #36
            "hula-hoop",                      #37
            "triangular cupola",              #38
            "tridiminished icosahedral",      #39
            "muffin",                         #40
            "octagonal pyramidal",            #41
            "tricapped trigonal prismatic",   #42
        ])
        self.vsepr.setCurrentIndex(9)
        
        self.vsepr.insertSeparator(33)
        self.vsepr.insertSeparator(25)
        self.vsepr.insertSeparator(20)
        self.vsepr.insertSeparator(16)
        self.vsepr.insertSeparator(13)
        self.vsepr.insertSeparator(8)
        self.vsepr.insertSeparator(5)
        self.vsepr.insertSeparator(2)
        self.vsepr.insertSeparator(1)
        self.vsepr.insertSeparator(0)
        self.vsepr.currentTextChanged.connect(self.element_changed)
        layout.addRow("shape:", self.vsepr)
        
        self.keep_open = QCheckBox()
        layout.addRow("keep table open:", self.keep_open)
        
        if ChangeElementMouseMode.vsepr:
            ndx = self.vsepr.findText(ChangeElementMouseMode.vsepr, Qt.MatchExactly)
            if ndx != -1:
                self.vsepr.setCurrentIndex(ndx)
        
        do_it = QPushButton("set element and shape")
        do_it.clicked.connect(self.set_selected)
        layout.addRow(do_it)

        self.keep_open.stateChanged.connect(
            lambda state: do_it.setVisible(Qt.CheckState(state) != Qt.Checked)
        )
        self.keep_open.stateChanged.connect(self.element_changed)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
    
    def element_changed(self):
        if self.keep_open.checkState() != Qt.Checked:
            return
        element = self.periodic_table.selectedElements()
        if element:
            ChangeElementMouseMode.element = element[0]
            ChangeElementMouseMode.vsepr = self.vsepr.currentText()
            self.session.logger.status("change element mouse mode set to use %s %s" % (ChangeElementMouseMode.vsepr, ChangeElementMouseMode.element))
    
    def set_selected(self, *args):
        element = self.periodic_table.selectedElements()
        if element:
            ChangeElementMouseMode.element = element[0]
            ChangeElementMouseMode.vsepr = self.vsepr.currentText()
            self.session.logger.status("change element mouse mode set to use %s %s" % (ChangeElementMouseMode.vsepr, ChangeElementMouseMode.element))
        
        if self.keep_open.checkState() != Qt.Checked:
            self.delete()


class _ModelSelector(ToolInstance):
    def __init__(self, session, name, coords):
        super().__init__(session, name)
        self._coords = coords
        self.tool_window = MainToolWindow(self)
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout()
        
        self.model_selector = ModelComboBox(self.session, addNew=True)
        layout.addRow("model:", self.model_selector)
        
        do_it = QPushButton(
            "add %s %s to selected model" % (
                ChangeElementMouseMode.vsepr,
                ChangeElementMouseMode.element
            )
        )
        do_it.clicked.connect(self.new_atom)
        layout.addRow(do_it)
        
        open_ele_sel = QPushButton("open element picker")
        open_ele_sel.clicked.connect(self.show_ele_sel)
        layout.addRow(open_ele_sel)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
    
    def show_ele_sel(self, *args):
        _ElementPicker(self.session, "pick element")
        self.delete()
    
    def new_atom(self):
        element = ChangeElementMouseMode.element
        adjust_bonds = True
        vsepr = ChangeElementMouseMode.vsepr
        
        if vsepr == "do not change":
            vsepr = False
        elif vsepr == "linear (1 bond)":
            vsepr = "linear 1"
        elif vsepr == "linear (2 bonds)":
            vsepr = "linear 2"
        elif vsepr == "trigonal planar (2 bonds)":
            vsepr = "bent 2 planar"
        elif vsepr == "tetrahedral (2 bonds)":
            vsepr = "bent 2 tetrahedral"
        elif vsepr == "tetrahedral (3 bonds)":
            vsepr = "bent 3 tetrahedral"
        
        if vsepr:
            coords = Atom.get_shape(vsepr)
            elements = [element] + (len(coords) - 1) * ["H"]
            atoms = [Atom(ele, coords=coord) for ele, coord in zip(elements, coords)]
            if adjust_bonds:
                # this works b/c all atoms are 1 angstrom from the center
                # just multiply by the distance we want
                expected_dist = RADII[element] + RADII["H"]
                for atom in atoms[1:]:
                    atom.coords *= expected_dist
            for atom in atoms[1:]:
                atoms[0].connected.add(atom)
                atom.connected.add(atoms[0])
        else:
            atoms = [Atom(element=element, coords=np.zeros(3))]

        rescol = ResidueCollection(atoms, name="new", refresh_connected=False)
        rescol.coord_shift(self._coords)

        model = self.model_selector.currentData()
        if model is None:
            chix = rescol.get_chimera(self.session)
            self.session.models.add([chix])
            apply_seqcrow_preset(chix, fallback="Ball-Stick-Endcap")

        else:
            res = model.new_residue("new", "a", len(model.residues)+1)
            rescol.residues[0].update_chix(res)
            run(self.session, "select add %s" % " ".join([atom.atomspec for atom in res.atoms]))

        self.delete()

    def delete(self):
        self.model_selector.deleteLater()
        return super().delete()

    def close(self):
        self.model_selector.deleteLater()
        return super().close()


class ChangeElementMouseMode(MouseMode):
    name = "change element"
    element = None
    vsepr = None
    
    def mouse_up(self, event):
        if event.shift_down():
            _ElementPicker(self.session, "pick element")
            return
            
        if not self.element:
            self.session.logger.warning("no element selected; shift-click to set element")
            self.session.logger.status("no element selected; shift-click to set element")
            _ElementPicker(self.session, "pick element")
            return
            
        x, y = event.position()
        pick = self.view.picked_object(x, y)

        if not pick:
            x1, x2 = self.session.main_view.clip_plane_points(x, y)
            coords = (x1 + x2) / 2
            new_fragment = _ModelSelector(self.session, "place atom in model", coords)
            if new_fragment.model_selector.count() == 1:
                new_fragment.new_atom()
            return
        
        # import cProfile
        # 
        # profile = cProfile.Profile()
        # profile.enable()
        
        vsepr = self.vsepr
        
        if vsepr == "do not change":
            vsepr = False
        elif vsepr == "linear (1 bond)":
            vsepr = "linear 1"
            goal = 1
        elif vsepr == "linear (2 bonds)":
            vsepr = "linear 2"
            goal = 2
        elif vsepr == "trigonal planar (2 bonds)":
            vsepr = "bent 2 planar"
            goal = 2
        elif vsepr == "tetrahedral (2 bonds)":
            vsepr = "bent 2 tetrahedral"
            goal = 2
        elif vsepr == "trigonal planar":
            goal = 3
        elif vsepr == "tetrahedral (3 bonds)":
            vsepr = "bent 3 tetrahedral"
            goal = 3
        elif vsepr == "tetrahedral":
            goal = 4
        else:
            goal = len(Atom.get_shape(vsepr)) - 1

        if not isinstance(pick, PickedAtom):
            return
        
        atom = pick.atom
        # # use built-in ChimeraX command for some of the more common things
        # # because it's faster for proteins
        # if False:
        #     run(
        #         self.session,
        #         "build modify %s %s %i geometry %s" % (
        #             atom.atomspec,
        #             self.element,
        #             goal,
        #             vsepr,
        #         )
        #     )
        # 
        
        frags = []
        for neighbor in atom.neighbors:
            frags.append(get_fragment(neighbor, stop=atom, max_len=atom.structure.num_atoms))
        
        residues = [atom.residue]
        hold_steady = None
        for i, frag in enumerate(sorted(frags, key=len)):
            if i == len(frags) - 1:
                hold_steady = AtomSpec(frag[0].atomspec)
                residues.append(frag[0].residue)
                continue
            residues.extend(frag.residues)
        
        rescol = ResidueCollection(
            atom.structure,
            convert_residues=set(residues),
            refresh_ranks=False
        )
        res = [residue for residue in rescol.residues if residue.chix_residue is atom.residue][0]
        target = res.find_exact(AtomSpec(atom.atomspec))[0]
        adjust_hydrogens = vsepr
        if vsepr is not False:
            cur_bonds = len(target.connected)
            change_Hs = goal - cur_bonds
            adjust_hydrogens = (change_Hs, vsepr)

        rescol.change_element(
            target,
            self.element,
            adjust_bonds=True,
            adjust_hydrogens=adjust_hydrogens,
            hold_steady=hold_steady,
        )
        
        res.update_chix(res.chix_residue, apply_preset=True, refresh_connected=True)
        rescol.update_chix(atom.structure, apply_preset=False, refresh_connected=False)
        
        # profile.disable()
        # profile.print_stats()


class EraserMouseMode(MouseMode):
    name = "structure eraser"

    def vr_press(self, event):
        self.mouse_up(event)

    def mouse_drag(self, event):
        self.do_erase(event)

    def mouse_up(self, event):
        super().mouse_up(event)
        self.do_erase(event)
    
    def do_erase(self, event):
        x, y = event.position()
        pick = self.view.picked_object(x, y)
        
        if isinstance(pick, PickedBond):
            pick.bond.delete()
        
        elif isinstance(pick, PickedAtom):
            pick.atom.delete()
        
        elif isinstance(pick, PickedPseudobond):
            pick.pbond.delete()


class _SubstituentSelector(ToolInstance):
    def __init__(self, session, name):
        super().__init__(session, name)
        self.tool_window = MainToolWindow(self)
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout()
        
        self.substituent_table = SubstituentTable(singleSelect=True)
        layout.addRow(self.substituent_table)

        self.new_residue = QCheckBox()
        self.new_residue.setCheckState(
            Qt.Checked if SubstituteMouseMode.newRes else Qt.Unchecked
        )
        layout.addRow("new residue:", self.new_residue)
        
        self.res_name = QLineEdit()
        self.res_name.setPlaceholderText("leave blank to keep current")
        layout.addRow("set residue name:", self.res_name)

        self.distance_names = QCheckBox()
        self.distance_names.setCheckState(
            Qt.Checked if SubstituteMouseMode.useRemoteness else Qt.Unchecked
        )
        layout.addRow("distance atom names:", self.distance_names)

        self.keep_open = QCheckBox()
        layout.addRow("keep list open:", self.keep_open)

        do_it = QPushButton("set substituent")
        do_it.clicked.connect(self.set_sub)
        layout.addRow(do_it)

        self.keep_open.stateChanged.connect(
            lambda state: do_it.setVisible(Qt.CheckState(state) != Qt.Checked)
        )
        self.keep_open.stateChanged.connect(self.sub_changed)

        self.substituent_table.table.itemSelectionChanged.connect(self.sub_changed)
        self.new_residue.stateChanged.connect(self.sub_changed)
        self.res_name.textChanged.connect(self.sub_changed)
        self.distance_names.stateChanged.connect(self.sub_changed)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
    
    def sub_changed(self):
        if self.keep_open.checkState() == Qt.Checked:
            self.set_sub()

    def set_sub(self):
        sub_names = []
        for row in self.substituent_table.table.selectionModel().selectedRows():
            if self.substituent_table.table.isRowHidden(row.row()):
                continue

            sub_names.append(row.data())

        if sub_names:
            SubstituteMouseMode.substituent = sub_names[0]
            SubstituteMouseMode.newRes = self.new_residue.checkState() == Qt.Checked
            SubstituteMouseMode.useRemoteness = self.distance_names.checkState() == Qt.Checked
            sub_name = self.res_name.text()
            SubstituteMouseMode.resName = sub_name

        if self.keep_open.checkState() != Qt.Checked:
            self.delete()

    def close(self):
        sub_names = []
        for row in self.substituent_table.table.selectionModel().selectedRows():
            if self.substituent_table.table.isRowHidden(row.row()):
                continue

            sub_names.append(row.data())

        if sub_names:
            SubstituteMouseMode.substituent = sub_names[0]
            SubstituteMouseMode.newRes = self.new_residue.checkState() == Qt.Checked
            SubstituteMouseMode.useRemoteness = self.distance_names.checkState() == Qt.Checked
            sub_name = self.res_name.text()
            SubstituteMouseMode.resName = sub_name

        super().close()


class SubstituteMouseMode(MouseMode):
    name = "substitute"
    newRes = False
    resName = None
    substituent = None
    useRemoteness = False
    
    def mouse_up(self, event):
        x, y = event.position()
        pick = self.view.picked_object(x, y)
        
        if not self.substituent or event.shift_down() or not pick:
            _SubstituentSelector(self.session, "pick substituent")
            return

        if isinstance(pick, PickedAtom):
            atom = pick.atom
            if SubstituteMouseMode.resName:
                run(
                    self.session,
                    "substitute %s substituent %s minimize true newName %s newResidue %s useRemoteness %s" % (
                        atom.atomspec,
                        self.substituent,
                        self.resName,
                        repr(self.newRes),
                        repr(self.useRemoteness),
                    )
                )
            else:
                run(
                    self.session,
                    "substitute %s substituent %s minimize true newResidue %s useRemoteness %s" % (
                        atom.atomspec,
                        self.substituent,
                        repr(self.newRes),
                        repr(self.useRemoteness),
                    )
                )


class SelectSimilarFragments(MouseMode):
    """select everything with a bonding path to clicked atoms"""
    name = "select similar fragments"
    icon_file = "icons/sel_group_icon.png"
    
    def __init__(self, session):
        super().__init__(session)
        
        self.minimum_drag_pixels = 5
        self.drag_color = (100, 218, 76, 255)
        # self.drag_color = (155, 37, 179, 255)
        self._drawn_rectangle = None
        self._dragging = False
    
    def mouse_drag(self, event):
        if self._is_drag(event):
            self._undraw_drag_rectangle()
            self._draw_drag_rectangle(event)
    
    def mouse_up(self, event):
        self._undraw_drag_rectangle()
        self._dragging = False

        set_sel = event.shift_down()

        if self._is_drag(event):
            sx, sy = self.mouse_down_position
            x, y = event.position()
            pick = self.view.rectangle_pick(sx, sy, x, y)
            self.select_pick(pick, set_sel)
        
        else:
            x, y = event.position()
            pick = self.view.picked_object(x, y)
            self.select_pick(pick, set_sel)
        
        super().mouse_up(event)

    def _is_drag(self, event):
        dp = self.mouse_down_position
        if dp is None:
            return False
        
        if self._dragging:
            return True
        
        dx, dy = dp
        x, y = event.position()
        self._dragging = abs(x - dx) + abs(y - dy) > self.minimum_drag_pixels

        return self._dragging

    def _draw_drag_rectangle(self, event):
        dx, dy = self.mouse_down_position
        x, y = event.position()
        view = self.session.main_view
        w, h = view.window_size
        view.draw_xor_rectangle(dx, h - dy, x, h - y, self.drag_color)
        self._drawn_rectangle = ((dx, dy), (x, y))

    def _undraw_drag_rectangle(self):
        dr = self._drawn_rectangle
        if dr:
            (dx, dy), (x, y) = dr
            view = self.session.main_view
            w, h = view.window_size
            view.draw_xor_rectangle(dx, h - dy, x, h - y, self.drag_color)
            self._drawn_rectangle = None

    def vr_press(self, event):
        # Virtual reality hand controller button press.
        pick = event.picked_object(self.view)
        self.select_pick(pick, False)

    def select_pick(self, pick, set_sel):
        if set_sel:
            self.session.selection.clear()

        if pick:
            atoms = Atoms()
            bonds = Bonds()
            if not hasattr(pick, "__iter__"):
                pick = [pick]

            first_selected = None
            
            fragments = []
            frag_ranks = dict()

            for m in self.session.models.list(type=AtomicStructure):
                mdl_atoms = Atoms(m.atoms)
                new_frag = True
                while new_frag:
                    new_frag = False
                    for i, atom in enumerate(mdl_atoms):
                        frag = get_fragment(atom)
                        new_frag = True
                        mdl_atoms = mdl_atoms.subtract(frag)
                        fragments.append(frag)
                        break
        
            frag_lengths = [len(frag) for frag in fragments]
            frag_elements = [sorted(frag.elements.names) for frag in fragments]
            frag_added = [False for frag in fragments]

            args = [
                fragments, frag_ranks, frag_lengths, frag_elements, frag_added
            ]


            def add_similar_fragments(
                fragment, atoms, fragments, frag_ranks, frag_lengths, frag_elements, frag_added
            ):
                ranks = canonical_rank(fragment, break_ties=False)
                length = len(fragment)
                elements = sorted(fragment.elements.names)
                sorted_frag_atoms = [x for _, x in sorted(zip(ranks, fragment), key=lambda pair: pair[0])]
                for i, other_frag in enumerate(fragments):
                    if frag_added[i]:
                        continue
                        
                    if frag_lengths[i] != length:
                        continue
                    
                    if any(frag_elements[i][j] != elements[j] for j in range(0, length)):
                        continue
                    
                    try:
                        ranks = frag_ranks[i]
                    except KeyError:
                        ranks = canonical_rank(other_frag, break_ties=False)
                        frag_ranks[i] = ranks
                    
                    sorted_other_frag_atoms = [
                        x for _, x in sorted(zip(ranks, other_frag.instances()), key=lambda pair: pair[0])
                    ]
                    for a, b in zip(sorted_frag_atoms, sorted_other_frag_atoms):
                        if a.element.name != b.element.name:
                            break
                        
                        if len(a.neighbors) != len(b.neighbors):
                            break
                        
                        failed = False
                        for j, k in zip(
                            sorted([aa.element.name for aa in a.neighbors]),
                            sorted([bb.element.name for bb in b.neighbors]),
                        ):
                            if j != k:
                                failed = True
                                break
                    
                        if failed:
                            break
                    
                    else:
                        atoms = atoms.merge(other_frag)
                        frag_added[i] = True
                
                return atoms


            for p in pick:
                if isinstance(p, PickedAtoms):
                    for atom in p.atoms:
                        if atom in atoms:
                            continue
                        connected_atoms = get_fragment(atom, max_len=atom.structure.num_atoms)
                        atoms = atoms.merge(connected_atoms)
                        atoms = add_similar_fragments(connected_atoms, atoms, *args)
                        if first_selected is None:
                            first_selected = atoms[0].selected

                elif isinstance(p, PickedAtom):
                    if p.atom in atoms:
                        continue
                    connected_atoms = get_fragment(
                        p.atom,
                        max_len=p.atom.structure.num_atoms
                    )
                    atoms = atoms.merge(connected_atoms)
                    atoms = add_similar_fragments(connected_atoms, atoms, *args)
                    if first_selected is None:
                        first_selected = atoms[0].selected

                elif isinstance(p, PickedBonds):
                    for bond in p.bonds:
                        if bond.atoms[0] in atoms:
                            continue
                        connected_atoms = get_fragment(
                            bond.atoms[0],
                            max_len=bond.structure.num_atoms
                        )
                        atoms = atoms.merge(connected_atoms)
                        atoms = add_similar_fragments(connected_atoms, atoms, *args)
                        if first_selected is None:
                            first_selected = atoms[0].selected

                elif isinstance(p, PickedBond):
                    if p.bond.atoms[0] in atoms:
                        continue
                    connected_atoms = get_fragment(
                        p.bond.atoms[0],
                        max_len=p.bond.structure.num_atoms
                    )
                    atoms = atoms.merge(connected_atoms)
                    atoms = add_similar_fragments(connected_atoms, atoms, *args)
                    if first_selected is None:
                        first_selected = atoms[0].selected

                elif isinstance(p, PickedResidues):
                    for res in p.residues:
                        for atom in res.atoms:
                            if atom in atoms:
                                continue
                            connected_atoms = get_fragment(
                                atom,
                                max_len=res.structure.num_atoms
                            )
                            atoms = atoms.merge(connected_atoms)
                            atoms = add_similar_fragments(connected_atoms, atoms, *args)
                            if first_selected is None:
                                first_selected = atoms[0].selected

                elif isinstance(p, PickedResidue):
                    for atom in p.residue.atoms:
                        if atoms in atoms:
                            continue
                        connected_atoms = get_fragment(
                            atom,
                            max_len=p.residue.structure.num_atoms
                        )
                        atoms = atoms.merge(connected_atoms)
                        atoms = add_similar_fragments(connected_atoms, atoms, *args)
                        if first_selected is None:
                            first_selected = atoms[0].selected

                else:
                    continue

            for atom in atoms:
                for neighbor, bond in zip(atom.neighbors, atom.bonds):
                    bonds = bonds.merge(Bonds([bond]))
            
            if first_selected is not None:
                atoms.selected = not first_selected
                bonds.selected = not first_selected
        else:
            run(self.session, "select clear")


class DrawHydrogenBondMouseMode(DrawBondMouseMode):
    name = "hbonds"
    scale = 1.0

    def vr_press(self, event):
        self.mouse_up(event)

    def mouse_up(self, event):
        atom = False
        MouseMode.mouse_up(self, event)
        if self._atom1 is not None and self._atom1.deleted:
            self._atom1 = None

        x, y = event.position()
        pick = self.view.picked_object(x, y)
        
        if isinstance(pick, PickedPseudobond):
            bond = pick.pbond
            if bond.group.name == bond.atoms[0].structure.PBG_HYDROGEN_BONDS:
                # run(self.session, "bond %s %s" % (bond.atoms[0].atomspec, bond.atoms[1].atomspec))
                bond.delete()
                self.reset()
            return

        if isinstance(pick, PickedBond):
            bond = pick.bond
            self.draw_new_pbond(*bond.atoms)
            bond.delete()
            self.reset()
            return

        if isinstance(pick, PickedAtom) and not self._atom1:
            self._atom1 = pick.atom
            self.session.logger.status("drawing hydrogen bond between %s and..." % self._atom1.atomspec)
            return

        if (
            isinstance(pick, PickedAtom) and
            pick.atom.structure is self._atom1.structure and
            pick.atom is not self._atom1
        ):
            atom = pick.atom
        
        if not atom:
            self.session.logger.status("not atom clicked - not drawing a new hydrogen bond")
            return

        if atom.structure is self._atom1.structure and atom is not self._atom1:
            self.draw_new_pbond(self._atom1, atom)
            self.session.logger.status("drew new hydrogen bond between %s and %s" % (
                atom.atomspec, self._atom1.atomspec,
            ))
            for bond in self._atom1.bonds:
                if atom in bond.atoms:
                    bond.delete()
                    break
            self.reset()

    def draw_new_pbond(self, atom1, atom2):
        try:
            pbg = atom1.structure.pseudobond_group(
                atom1.structure.PBG_HYDROGEN_BONDS,
                create_type=1
            )
        except TypeError:
            pbg = atom1.structure.pseudobond_group(
                atom1.structure.PBG_HYDROGEN_BONDS,
                create_type=2
            )
        pbg.new_pseudobond(atom1, atom2)
        # bug in older versions of ChimeraX where new pseudobonds aren't 
        # displayed until something else changes
        # change the number of dashes
        pbg.dashes += 2
        pbg.dashes -= 2