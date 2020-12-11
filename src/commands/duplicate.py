from chimerax.atomic import AtomsArg, AtomicStructure
from chimerax.core.commands import BoolArg, CmdDesc
from chimerax.core.selection import SELECTION_CHANGED

duplicate_description = CmdDesc(required=[("selection", AtomsArg)],
                             keyword=[
                                      ("newModel", BoolArg),
                                     ],
                             synopsis="duplicate a portion of an atomic structure"
)

def duplicate(session, selection, newModel=True):
    # dict for unique models, residues, and atoms
    models = {}
    # dict for just models and atoms
    atom_list = {}
    for atom in selection:
        if atom.structure not in models:
            models[atom.structure] = {}
            atom_list[atom.structure] = []
        
        if atom.residue not in models[atom.structure]:
            models[atom.structure][atom.residue] = []
        
        models[atom.structure][atom.residue].append(atom)
        atom_list[atom.structure].append(atom)
    
    for model in models:
        if newModel:
            struc = AtomicStructure(session, name="copy of %s" % model.atomspec)
        else:
            struc = model
            offset = len(model.atoms)
        for res in models[model]:
            residue = struc.new_residue(res.name, res.chain_id, res.number)
            for atom in models[model][res]:
                dup_atom = struc.new_atom(atom.name, atom.element)
                dup_atom.coord = atom.coord
                dup_atom.serial_number = len(struc.atoms)
                res.add_atom(dup_atom)

        for i, atom1 in enumerate(atom_list[model]):
            atom1.selected = False
            if newModel:
                struc.atoms[i].selected = True
                struc.atoms[i].color = atom1.color
                struc.atoms[i].radius = atom1.radius
                struc.atoms[i].draw_mode = atom1.draw_mode
            else:
                struc.atoms[i + offset].selected = True
                struc.atoms[i + offset].color = atom1.color
                struc.atoms[i + offset].radius = atom1.radius
                struc.atoms[i + offset].draw_mode = atom1.draw_mode
                
            for j, atom2 in enumerate(atom_list[model][:i]):
                if atom2 in atom1.neighbors:
                    if newModel:
                        struc.new_bond(struc.atoms[i], struc.atoms[j])
                    else:
                        struc.new_bond(struc.atoms[i + offset], struc.atoms[j + offset])

        if newModel:
            session.models.add([struc])
        
    session.triggers.activate_trigger(SELECTION_CHANGED, None)
