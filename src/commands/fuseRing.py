import numpy as np

from AaronTools.ring import Ring

from chimerax.atomic import OrderedAtomsArg, selected_atoms
from chimerax.core.commands import BoolArg, CmdDesc, StringArg, DynamicEnum, ListOf, NoArg, Or, EmptyArg

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec


fuseRing_description = CmdDesc(
    required=[("selection", Or(OrderedAtomsArg, EmptyArg))], \
    keyword=[
        (
            "rings",
            ListOf(
                DynamicEnum(
                    Ring.list,
                    name="ring",
                    case_sensitive=True,
                    #we don't have a page for these
                    #url="http://catalysttrends.wheelergroupresearch.com/AaronTools/rings.php"
                )
            )
        ),
        ("newName", ListOf(StringArg)), 
        ("modify", BoolArg),
        ("minimize", BoolArg),
        ("available", NoArg),
    ],
    synopsis="fuse a ring",
    url="https://github.com/QChASM/SEQCROW/wiki/Commands#fuseRing",
)

def minimal_ring_convert(atomic_structure, atom1, atom2, avoid=None):
    tm_bonds = atomic_structure.pseudobond_group(atomic_structure.PBG_METAL_COORDINATION, create_type=None)
    residues = [atom1.residue]
    if atom2.residue not in residues:
        residues.append(atom2.residue)
    
    if avoid is None:
        avoid = []
    
    max_iter = len(atomic_structure.atoms)
    start = atom1
    path = [atom1]
    i = 0
    while start != atom2:
        if start.residue not in residues:
            residues.append(start.residue)
            
        i += 1
        if i > max_iter:
            return atomic_structure.residues
            
        v1 = atom2.coord - start.coord
        max_overlap = None
        new_start = None
        pseudobonds = []
        if tm_bonds is not None:
            for bond in tm_bonds.pseudobonds:
                a1, a2 = bond.atoms
                if start is a1:
                    pseudobonds.append(a2)
                    
                if start is a2:
                    pseudobonds.append(a1)

        for atom in start.neighbors + pseudobonds:
            if atom not in path and atom not in avoid:
                v2 = atom.coord - start.coord
                overlap = np.dot(v1, v2)
                if max_overlap is None or overlap > max_overlap:
                    new_start = atom
                    max_overlap = overlap
        
        if new_start is None:
            path.remove(start)
            avoid.append(start)
            if len(path) > 1:
                start = path[-1]
            else:
                raise RuntimeError(
                    "could not determine bet path between %s and %s"
                    % (str(atom1), str(atom2))
                )
        else:
            path.append(new_start)
            start = new_start

    return residues


def fuseRing(session, selection=None, rings=None, newName=None, modify=True, minimize=False, available=False):
    if available:
        fuseRing_list(session)
        return
    
    if not selection:
        selection = selected_atoms(session)
    
    if not rings:
        session.logger.error("missing required \"rings\" argument")
        return
    
    if newName is None:
        pass
    elif any(len(name.strip()) > 4 for name in newName):
        raise RuntimeError("residue names must be 4 characters or less")
    elif not all(name.isalnum() for name in newName):
        raise RuntimeError("invalid residue name: %s" % newName)
    elif len(rings) != len(newName):
        raise RuntimeError("number of substituents is not the same as the number of new names")
    
    if len(selection) < 2:
        raise RuntimeWarning("two atoms must be selected per molecule")
    
    models = {}
    for atom in selection:
        if atom.structure not in models:
            models[atom.structure] = [atom]
        else:
            models[atom.structure].append(atom)
    
        if len(models[atom.structure]) > 2:
            raise RuntimeError("only two atoms can be selected on any model")
    
    first_pass = True
    new_structures = []
    for i, ringname in enumerate(rings):
        ringname = ringname.strip()
        
        for model in models:
            atom1 = models[model][0]
            atom2 = models[model][1]
            if modify and first_pass:
                convert = minimal_ring_convert(model, *models[model])
                if newName is not None:
                    for res in convert:
                        res.name = newName[i]

                rescol = ResidueCollection(model, convert_residues=convert)

                target = rescol.find([AtomSpec(atom1.atomspec), AtomSpec(atom2.atomspec)])

            elif modify and not first_pass:
                raise RuntimeError("only the first model can be replaced")
            else:
                model_copy = model.copy()
                a1 = model_copy.atoms[model.atoms.index(models[model][0])]
                a2 = model_copy.atoms[model.atoms.index(models[model][1])]
                convert = minimal_ring_convert(model_copy, a1, a2)
                if newName is not None:
                    for res in convert:
                        res.name = newName[i]

                rescol = ResidueCollection(model_copy, convert_residues=convert)

                target = rescol.find(
                    [
                        AtomSpec(a1.atomspec),
                        AtomSpec(a2.atomspec)
                    ]
                )

            rescol.ring_substitute(target, ringname, minimize=minimize)
            
            if modify:                    
                rescol.update_chix(model)
            else:
                rescol.update_chix(model_copy)
                new_structures.append(model_copy)
        
        first_pass = False
    
    if not modify:
        session.models.add(new_structures)


def fuseRing_list(session):
    s = ""
    for ringname in Ring.list():
        s += "%s\n" % ringname
    session.logger.info(s.strip())
