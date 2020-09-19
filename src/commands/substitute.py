import numpy as np

from AaronTools.substituent import Substituent

from chimerax.atomic import AtomsArg
from chimerax.core.commands import BoolArg, CmdDesc, StringArg, DynamicEnum, ListOf

from SEQCROW.residue_collection import ResidueCollection, Residue


substitute_description = CmdDesc(required=[("selection", AtomsArg)], \
                                 keyword=[("substituents", ListOf(DynamicEnum(Substituent.list, \
                                                                  name="substituent", \
                                                                  case_sensitive=True, \
                                                                  url="http://catalysttrends.wheelergroupresearch.com/AaronTools/substituents.php")
                                                           )), 
                                          ("newName", ListOf(StringArg)), 
                                          ("guessAvoid", BoolArg),
                                          ("modify", BoolArg),
                                          ("minimize", BoolArg),
                                         ], \
                                 required_arguments=['substituents'], 
                                 synopsis="modify substituents")


def substitute(session, selection, substituents, newName=None, guessAvoid=True, modify=True, minimize=False):
    models = {}
    attached = {}
    
    if newName is None:
        pass
    elif any(len(name.strip()) > 4 for name in newName):
        raise RuntimeError("residue names must be 4 characters or less")
    elif any(x in "".join(newName) for x in "!@#$%^&*()\\/.<><;':\"[]{}|-=_+"):
        raise RuntimeError("invalid residue name: %s" % " ".join(newName))
    elif len(substituents) != len(newName):
        raise RuntimeError("number of substituents is not the same as the number of new names")

    for atom in selection:
        if not guessAvoid:
            for bond in atom.bonds:
                atom2 = bond.other_atom(atom)
                if atom2 not in selection:
                    if atom in attached:
                        raise RuntimeError("cannot determine previous substituent; multiple fragments unselected")

                    attached[atom] = atom2

                    if atom.structure not in models:
                        models[atom.structure] = {atom.residue:[atom]}

                    else:
                        if atom.residue not in models[atom.structure]:
                            models[atom.structure][atom.residue] = [atom]
                        else:
                            models[atom.structure][atom.residue].append(atom)

        else:
            if atom.structure not in models:
                models[atom.structure] = {atom.residue:[atom]}

            else:
                if atom.residue not in models[atom.structure]:
                    models[atom.structure][atom.residue] = [atom]
                else:
                    models[atom.structure][atom.residue].append(atom)

    first_pass = True
    new_structures = []
    for ndx, subname in enumerate(substituents):
        subname = subname.strip()
        sub = Substituent(subname)
        for model in models:
            if modify and first_pass:
                for res in models[model]:
                    conv_res = [res]
                    if minimize:
                        for chix_res in model.residues:
                            if chix_res in conv_res:
                                continue

                            added_res = False
                            for atom in chix_res.atoms:
                                for target in models[model][res]:
                                    d = np.linalg.norm(atom.coord - target.coord)
                                    if d < 15:
                                        conv_res.append(chix_res)
                                        added_res = True
                                        break

                                if added_res:
                                    break

                rescol = ResidueCollection(model, convert_residues=conv_res)
                for res  in models[model]:
                    residue = [resi for resi in rescol.residues if resi.chix_residue is res][0]
                    if newName is not None:
                        residue.name = newName[ndx]

                    for target in models[model][res]:
                        if not guessAvoid:
                            end = attached[target].atomspec
                        else:
                            end = None 

                        residue.substitute(sub.copy(), target.atomspec, attached_to=end, minimize=minimize)

                    if minimize:
                        residue.minimize_sub_torsion()

                    residue.update_chix(res)

            elif modify and not first_pass:
                raise RuntimeError("only the first model can be replaced")
            else:
                model_copy = model.copy()

                conv_res = [model_copy.residues[i] for i in [model.residues.index(res) for res in models[model]]]

                if minimize:
                    for chix_res in model_copy.residues:
                        if chix_res in conv_res:
                            continue
                        
                        added_res = False
                        for atom in chix_res.atoms:
                            for target in models[model][model.residues[model_copy.residues.index(chix_res)]]:
                                d = np.linalg.norm(atom.coord - target.coord)
                                if d < 15:
                                    conv_res.append(chix_res)
                                    added_res = True
                                    break
                            
                            if added_res:
                                break

                rescol = ResidueCollection(model_copy, convert_residues=conv_res)
                for residue, res in zip(rescol.residues, models[model]):                        
                    res_copy = residue.chix_residue
                    if newName is not None:
                        residue.name = newName[ndx]

                    for target in models[model][res]:
                        if not guessAvoid:
                            end = attached[target].atomspec
                        else:
                            end = None

                        residue.substitute(sub.copy(), model_copy.atoms[model.atoms.index(target)].atomspec, attached_to=end, minimize=minimize)

                    #if minimize:
                    #    residue.minimize_sub_torsion()

                    residue.update_chix(res_copy)

                new_structures.append(model_copy)

        first_pass = False

    if not modify:
        session.models.add(new_structures)