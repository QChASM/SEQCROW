from chimerax.atomic import selected_atoms, selected_bonds, AtomicStructure
from chimerax.bild.bild import read_bild
from chimerax.core.commands import BoolArg, FloatArg, ColorArg, ObjectsArg, CmdDesc
from chimerax.core.generic3d import Generic3DModel

from io import BytesIO

tsbond_description = CmdDesc(required=[("selection", ObjectsArg)],  \
                             keyword=[
                                      ("transparency", FloatArg), \
                                      ("halfbond", BoolArg),      \
                                      ("color", ColorArg),        \
                                      ("radius", FloatArg),       \
                                     ],
                             synopsis="draw a forming/breaking bond"
                    )
erase_tsbond_description = CmdDesc(required=[("selection", ObjectsArg)],  \
                                   synopsis="draw a forming/breaking bond"
                          )

# someone should totally make an acutal bond for this
def tsbond(session, selection, transparency=50, halfbond=None, color=None, radius=0.16):
    if color is None and halfbond is False:
        session.logger.error("color must be specified with `halfbond false`")
        return
    
    if color is not None and halfbond:
        session.logger.error("color cannot be specified with `halfbond true`")
        return
    
    if color is not None and halfbond is None:
        halfbond = False
    
    if color is not None:
        color = color.uint8x4()[:-1]
        color = tuple(c/255. for c in color)
    else:
        halfbond = True
    
    if transparency >= 100 or transparency <= 0:
        session.logger.error("transparency must be between 0 and 100")
        return
    
    transparency /= 100.
    ts_bond = None
    atoms = selection.atoms
    if len(atoms) != 2 and len(atoms) > 0:
        session.logger.error("2 atoms must be selected")
    
    elif len(atoms) == 2:
        if atoms[0].structure is not atoms[1].structure:
            session.logger.error("atoms must be on the same structure")
        
        else:
            structure = atoms[0].structure
            for bond in structure.bonds:
                if all(atom in bond.atoms for atom in atoms):
                    ts_bond = bond

            if ts_bond is None:
                ts_bond = structure.new_bond(*atoms)

    bonds = [bond for bond in selection.bonds]
    if ts_bond is not None and ts_bond not in bonds:
        bonds.append(ts_bond)
        
    for bond in bonds:       
        s = ""
        atom1, atom2 = bond.atoms
        for m in session.models.list(type=Generic3DModel):
            if hasattr(m, "_ts_bond_atoms") and atom1 in m._ts_bond_atoms and atom2 in m._ts_bond_atoms:
                m.delete()
        
        v = atom2.coord - atom1.coord
        ratio = 0.5
        mid = atom1.coord + ratio*v 
        
        if halfbond:
            color1 = tuple(x/255 for x in atom1.color[:-1])
            color2 = tuple(x/255 for x in atom2.color[:-1])

        s += ".transparency %f\n" % transparency
        
        if not halfbond:
            s += ".color %f %f %f\n" % color
        else:
            s += ".color %f %f %f\n" % color2
        
        s += ".cylinder %f %f %f " % tuple(atom2.coord)
        s += " %f %f %f " % tuple(mid)
        s += " %f open\n" % radius
        
        if not halfbond:
            s += ".color %f %f %f\n" % color
        else:
            s += ".color %f %f %f\n" % color1

        s += ".cylinder %f %f %f " % tuple(mid)
        s += " %f %f %f " % tuple(atom1.coord)
        s += " %f open\n" % radius

        stream = BytesIO(bytes(s, 'utf-8'))
        bild_obj, status = read_bild(session, stream, "tsbond %s-%s" % (atom1.atomspec, atom2.atomspec))
        for half in bild_obj:
            half._ts_bond_atoms = (atom1, atom2)
    
        session.models.add(bild_obj, parent=bond.structure)

        bond.delete()

def erase_tsbond(session, selection):
    atoms = selection.atoms
    for m in session.models.list(type=Generic3DModel):
        if not hasattr(m, "_ts_bond_atoms"):
            continue
            
        if m in selection.models:
            m.delete()
        
        elif sum(int(a in atoms and a in m._ts_bond_atoms) for a in atoms) == 2:
            m.delete()