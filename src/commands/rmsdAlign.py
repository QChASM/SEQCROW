import numpy as np

from chimerax.atomic import AtomicStructure
from chimerax.core.commands import BoolArg, ModelsArg, ModelArg, CmdDesc, Or

from SEQCROW.residue_collection import ResidueCollection

rmsdAlign_description = CmdDesc(required=[("reference", ModelArg)], \
                                keyword=[("toModels", Or(ModelsArg, ModelArg)), ("sort", BoolArg), ("align", BoolArg)], \
                                required_arguments=['toModels'])

def rmsdAlign(session, toModels, reference, align=True, sort=False):   
    ref = ResidueCollection(reference)
    if isinstance(toModels, AtomicStructure):
        models = [models]
    else:
        models = toModels
    
    for model in models:
        rescol = ResidueCollection(model)
        if align:
            rmsd = rescol.RMSD(ref, sort=sort, align=True)
            session.logger.info("rmsd between %s and %s: %.4f" % (ref.atomspec, model.atomspec, rmsd))
            for atom in rescol.atoms:
                atom.chix_atom.coord = atom.coords
        else:
            aligned_rmsd, order1, order2 = rescol.RMSD(ref, sort=sort, debug=True, align=True)
            
            rmsd = 0
            for a1, a2 in zip(order1, order2):
                atom1 = a1.chix_atom
                atom2 = a2.chix_atom
                v = atom1.coord - atom2.coord
                rmsd += np.dot(v, v)

            rmsd = np.sqrt(rmsd / len(rescol.atoms))

            session.logger.info("rmsd between %s and %s: %.4f" % (ref.atomspec, model.atomspec, rmsd))
    