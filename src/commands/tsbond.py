from chimerax.atomic import selected_atoms, selected_bonds, AtomicStructure, PseudobondGroup
from chimerax.core.commands import BoolArg, FloatArg, ColorArg, ObjectsArg, CmdDesc, run


tsbond_description = CmdDesc(
    required=[("selection", ObjectsArg)],
    keyword=[
        ("transparency", FloatArg),
        ("color", ColorArg),
        ("radius", FloatArg),
    ],
    synopsis="draw a forming/breaking bond",
    url="https://github.com/QChASM/SEQCROW/wiki/Commands#tsbond",
)

erase_tsbond_description = CmdDesc(
    required=[("selection", ObjectsArg)],
    synopsis="draw a forming/breaking bond",
    url="https://github.com/QChASM/SEQCROW/wiki/Commands#tsbond",
)

# someone should totally make an acutal bond for this
def tsbond(session, selection, transparency=50, color=[170, 255, 255, 255], radius=0.16):   
    if not isinstance(color, list):
        color = color.uint8x4()
    color = [c for c in color][:-1]
    color.append(int( 255 * ( transparency / 100.)))
    
    if transparency >= 100 or transparency <= 0:
        session.logger.error("transparency must be between 0 and 100")
        return
    
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
        
        pbg = bond.structure.pseudobond_group("TS bonds", create_type=1)
        if not any(all(atom in pb.atoms for atom in bond.atoms) for pb in pbg.pseudobonds):
            pbg.new_pseudobond(*bond.atoms)
        
        pbg.dashes = 0
        pbg.halfbond = False
        pbg.radius = radius 
        pbg.color = color

        if pbg not in bond.structure.child_models():
            bond.structure.add([pbg])

        bond.delete()


def erase_tsbond(session, selection):
    atoms = selection.atoms
    pbonds = selection.pseudobonds
    for pbg in session.models.list(type=PseudobondGroup):
        if pbg.name != "TS bonds":
            continue
        for bond in pbg.pseudobonds:
            if all(atom in atoms for atom in bond.atoms) or bond in pbonds:
                atom1, atom2 = bond.atoms
                bond.delete()
                run(
                    session,
                    "bond %s %s reasonable true" % (atom1.atomspec, atom2.atomspec),
                    log=False
                )