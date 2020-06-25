import numpy as np

from chimerax.core.commands import BoolArg, ModelsArg, ModelArg, CmdDesc

from SEQCROW.residue_collection import ResidueCollection

rmsdAlign_description = CmdDesc(required=[("models", ModelsArg)], \
                                keyword=[("reference", ModelArg), ("sort", BoolArg), ("align", BoolArg)], \
                                required_arguments=['reference'], synopsis=\
                                "calculate the RMSD between the reference model and other models, " + \
                                "with or without sorting the atoms or aligning the structures")

def rmsdAlign(session, models, reference, align=True, sort=False):   
    ref = ResidueCollection(reference)
    order1 = None
    
    for model in models:
        rescol = ResidueCollection(model)
        if align:
            rmsd = rescol.RMSD(ref, sort=sort, align=True)
            session.logger.info("rmsd between %s and %s: %.4f" % (ref.atomspec, model.atomspec, rmsd))
            for atom in rescol.atoms:
                #update coordinates (without rescol.update_chix - that's slower b/c it checks bonds)
                atom.chix_atom.coord = atom.coords
        else:
            #get ordering of atoms
            #XXX: RMSD returns early (without giving ordered atoms) if align=False (which is the default)
            if order1 is None:
                if sort:
                    order1, _ = ref.reorder(canonical=True)
                else:
                    order1 = ref.atoms

            if sort:
                order2, _ = rescol.reorder(canonical=True)
            else:
                order2 = rescol.atoms
            
            #recompute rmsd using untranslated coordinates (from original AtomicStructures)
            rmsd = 0
            for a1, a2 in zip(order1, order2):
                atom1 = a1.chix_atom
                atom2 = a2.chix_atom
                v = atom1.coord - atom2.coord
                rmsd += np.dot(v, v)

            rmsd = np.sqrt(rmsd / len(rescol.atoms))

            session.logger.info("rmsd between %s and %s: %.4f" % (ref.atomspec, model.atomspec, rmsd))
    