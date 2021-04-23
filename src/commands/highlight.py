from chimerax.atomic import selected_atoms, selected_bonds, get_triggers, Element
from chimerax.markers import MarkerSet, create_link
from chimerax.core.commands import BoolArg, FloatArg, ColorArg, ObjectsArg, CmdDesc


highlight_description = CmdDesc(
    required=[("selection", ObjectsArg)],
    keyword=[
        ("transparency", FloatArg),
        ("color", ColorArg),
        ("scale", FloatArg),
    ],
    synopsis="make atoms or bonds stand out a bit more"
)

erase_highlight_description = CmdDesc(
    required=[("selection", ObjectsArg)],
    synopsis="erase a highlight"
)


class Highlight(MarkerSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        global_triggers = get_triggers()
        self._changes = global_triggers.add_handler("changes", self.check_changes)

    def create_marker(self, atom, rgba, scale):
        for a in self.atoms:
            if a._follow is atom:
                a.color = rgba
                a.radius = scale * atom.radius
                break
        else:
            a = super().create_marker(atom.coord, rgba, scale * atom.radius)
            a.element = Element.get_element(atom.element.name)
            a._follow = atom
            a.hide = atom.hide
            a.display = atom.display
            a.draw_mode = atom.draw_mode

        a._scale = scale
        if atom.draw_mode == atom.STICK_STYLE and atom.neighbors:
            radius = scale * atom.bonds[-1].radius
        return a
    
    def check_changes(self, trigger_name=None, changes=None):
        if changes:
            changed_models = changes.modified_atomic_structures()
            for atom in self.atoms:
                if atom._follow.deleted:
                    atom.delete()

                elif atom._follow.structure in changed_models:
                    atom.radius = atom._scale * atom._follow.radius
                    if atom._follow.draw_mode == atom.STICK_STYLE and atom._follow.neighbors:
                        atom.radius = atom._scale * atom._follow.bonds[-1].radius
                    atom.coord = atom._follow.coord
                    atom.hide = atom._follow.hide
                    atom.display = atom._follow.display
                    atom.draw_mode = atom._follow.draw_mode

    def delete(self):
        global_triggers = get_triggers()
        global_triggers.remove_handler(self._changes)
        super().delete()


def highlight(session, selection, transparency=50, color=(0, 255, 0), scale=1.5):
    if not isinstance(color, tuple):
        color = color.uint8x4()

    selected_atoms = selection.atoms
    selected_bonds = selection.bonds
    
    color = [c for c in color[:3]]
    color.append(int(transparency * 255. / 100))
    
    models = {}
    for atom in selected_atoms:
        if isinstance(atom.structure, Highlight):
            continue
        if atom.structure not in models:
            models[atom.structure] = ([atom], [])
        else:
            models[atom.structure][0].append(atom)
    
    for bond in selected_bonds:
        if isinstance(bond.structure, Highlight):
            continue
        if bond.structure not in models:
            models[bond.structure] = ([], [bond])
        else:
            models[bond.structure][1].append(bond)
    
    for model in models:
        for child in model.child_models():
            if isinstance(child, Highlight):
                ms = child
                break
        else:
            ms = Highlight(session, name="highlight")

        ms.ball_scale = model.ball_scale
        atoms = models[model][0]
        for atom in atoms:
            m = ms.create_marker(atom, color, scale)
            m.draw_mode = atom.draw_mode
        
        bonds = models[model][1]
        for bond in bonds:
            markers = []
            for atom in bond.atoms:
                if not any(atom is a._follow for a in ms.atoms):
                    # we want to hide the atom
                    m = ms.create_marker(atom, color, 1e-16)
                    markers.append(m)
                else:
                    markers.extend([a for a in ms.atoms if a._follow is atom])
            
            m1, m2 = markers
            
            for b in ms.bonds:
                if m1 in b.atoms and m2 in b.atoms:
                    b.radius = scale * bond.radius
                    break
            else:
                b = create_link(m1, m2, rgba=None, radius=scale * bond.radius)
            b.halfbond = True 
            b.display = True
            b.hide = False

        model.add([ms])

def erase_highlight(session, selection):
    for atom in selection.atoms:
        for child in atom.structure.child_models():
            if isinstance(child, Highlight):
                for a in child.atoms:
                    if a._follow is atom:
                        a.delete()    
    
    for bond in selection.bonds:
        for child in bond.structure.child_models():
            if isinstance(child, Highlight):
                for b in child.bonds:
                    a1, a2 = b.atoms
                    if a1._follow in bond.atoms and a2._follow in bond.atoms:
                        b.delete()
                        