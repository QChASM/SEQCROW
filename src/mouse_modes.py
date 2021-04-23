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
from chimerax.mouse_modes import MouseMode

from SEQCROW.selectors import get_fragment


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
        self._dragging = abs(x-dx) + abs(y-dy) > self.minimum_drag_pixels

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


class DrawBondMouseMode(MouseMode):
    name = "bond"

    def __init__(self, session):
        super().__init__(session)
        
        self._atom1 = None
    
    def mouse_up(self, event):
        x, y = event.position()
        pick = self.view.picked_object(x, y)

        if event.shift_down() and not pick:
            self._atom1 = None
        
        if isinstance(pick, PickedBond):
            bond = pick.bond
            run(self.session, "~bond %s" % bond.atomspec)
            return

        if not isinstance(pick, PickedAtom):
            return
        
        atom = pick.atom
        
        if self._atom1 is None or self._atom1.deleted or self._atom1 is atom:
            self._atom1 = atom
            return
        
        if atom.structure is self._atom1.structure:
            run(self.session, "bond %s %s reasonable false" % (
                atom.atomspec, self._atom1.atomspec
            ))
            self._atom1 = None
        else:
            self._atom1 = atom


class DrawTSBondMouseMode(MouseMode):
    name = "tsbond"

    def __init__(self, session):
        super().__init__(session)
        
        self._atom1 = None
    
    def mouse_up(self, event):
        x, y = event.position()
        pick = self.view.picked_object(x, y)

        if event.shift_down() and not pick:
            self._atom1 = None
        
        if isinstance(pick, PickedPseudobond):
            bond = pick.pbond
            if bond.group.name == "TS bonds":
                atom1, atom2 = bond.atoms
                run(self.session, "~tsbond %s %s" % (atom1.atomspec, atom2.atomspec))
                run(self.session, "bond %s %s reasonable true" % (atom1.atomspec, atom2.atomspec))
                return

        if isinstance(pick, PickedBond):
            bond = pick.bond
            run(self.session, "tsbond %s" % bond.atomspec)
            return

        if not isinstance(pick, PickedAtom):
            return
        
        atom = pick.atom
        
        if self._atom1 is None or self._atom1.deleted or self._atom1 is atom:
            self._atom1 = atom
            return
        
        if atom.structure is self._atom1.structure:
            run(self.session, "tsbond %s %s" % (atom.atomspec, self._atom1.atomspec))
            self._atom1 = None
        else:
            self._atom1 = atom

