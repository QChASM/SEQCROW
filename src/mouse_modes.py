from chimerax.atomic import Atoms, Bonds
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
from chimerax.markers import MarkerSet, create_link
from chimerax.mouse_modes import MouseMode

from SEQCROW.selectors import get_fragment

import numpy as np


class SelectConnectedMouseMode(MouseMode):
    """select everything with a bonding path to clicked atoms"""
    name = "select connected"
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
                        for atom in res:
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
        mark = super().create_marker(pt, (170, 255, 255, 127), rad)

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

    def mouse_down(self, event):
        super().mouse_down(event)
        x, y = event.position()
        pick = self.view.picked_object(x, y)
        if not isinstance(pick, PickedAtom):
            return
        
        self._atom1 = pick.atom
    
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

    def mouse_drag(self, event):
        if not self._dragging and self._atom1:
            if self._is_drag(event):
                self._markerset = self.ms_cls(self.session, "bond")
                self._markerset.create_marker(self._atom1)
                self._atom1.structure.add([self._markerset])
                return

        if self._markerset:
            x, y = event.position()
            pick = self.view.picked_object(x, y)
            if isinstance(pick, PickedAtom) and pick.atom.structure is self._atom1.structure:
                atom2 = pick.atom
                if atom2 is self._atom1:
                    return
                if self._markerset.num_atoms > 1:
                    self._markerset.atoms[1].delete()
                self._atom2 = atom2
                self._markerset.create_marker(atom2)
                fake_bond = create_link(*self._markerset.atoms)
                fake_bond.halfbond = True
                avg_radius = self.avg_bond_radius(self._atom1, self._atom2)
                fake_bond.radius = avg_radius
            
            elif self._atom1:
                self._atom2 = None
                x1, x2 = self.session.main_view.clip_plane_points(x, y)
                v = x2 - x1
                v /= np.linalg.norm(v)
                p = np.dot(self._atom1.scene_coord - x1, v)
                pt = x1 + p * v + (self._atom1.coord - self._atom1.scene_coord)
                if self._markerset.num_atoms > 1:
                    self._markerset.atoms[1].delete()

                avg_radius = self.avg_bond_radius(self._atom1)

                mark = self._markerset.create_marker_from_point(
                    pt,
                    self._atom1.color,
                    avg_radius,
                )
                fake_bond = create_link(*self._markerset.atoms)
                fake_bond.halfbond = True

                fake_bond.radius = avg_radius

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

    def mouse_up(self, event):
        super().mouse_up(event)
        x, y = event.position()
        pick = self.view.picked_object(x, y)

        
        if isinstance(pick, PickedBond) and not self._markerset:
            bond = pick.bond
            run(self.session, "~bond %s" % bond.atomspec)
            self.reset()
            return

        if not isinstance(pick, PickedAtom) and not self._atom2:
            self.reset()
            return

        if not self._atom1:
            self.reset()
            return

        if isinstance(pick, PickedAtom) and pick.atom.structure is self._atom1.structure:
            atom = pick.atom
        else:
            atom = self._atom2
        
        if not atom:
            self.reset()
            return
        
        if atom.structure is self._atom1.structure and atom is not self._atom1:
            if atom not in self._atom1.neighbors:
                avg_radius = self.avg_bond_radius(self._atom1, atom)
                new_bond = atom.structure.new_bond(atom, self._atom1)
                new_bond.radius = avg_radius

        self.reset()


class DrawTSBondMouseMode(DrawBondMouseMode):
    name = "tsbond"
    scale = 1.0
    ms_cls = _TSBondMarkers

    def mouse_up(self, event):
        MouseMode.mouse_up(self, event)
        
        self._dragging = False
        
        x, y = event.position()
        pick = self.view.picked_object(x, y)

        
        if isinstance(pick, PickedPseudobond) and not self._markerset:
            bond = pick.pbond
            if bond.group.name == "TS bonds":
                atom1, atom2 = bond.atoms
                run(self.session, "~tsbond %s %s" % (atom1.atomspec, atom2.atomspec))
                self.reset()
            return

        if isinstance(pick, PickedBond) and not self._markerset:
            bond = pick.bond
            run(self.session, "tsbond %s" % bond.atomspec)
            self.reset()
            return

        if not self._atom1:
            return

        if isinstance(pick, PickedAtom) and pick.atom.structure is self._atom1.structure:
            atom = pick.atom
        else:
            atom = self._atom2
        
        if not atom:
            self.reset()
            return
        
        if atom.structure is self._atom1.structure and atom is not self._atom1:
            avg_radius = self.avg_bond_radius(self._atom1, atom)
            
            run(
                self.session,
                "tsbond %s %s radius %.3f" % (
                    self._atom1.atomspec,
                    atom.atomspec,
                    avg_radius,
                )
            )

        self.reset()

