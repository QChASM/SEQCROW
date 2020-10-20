import numpy as np

from AaronTools.substituent import Substituent

from chimerax.atomic import AtomsArg
from chimerax.core.commands import BoolArg, CmdDesc, StringArg, DynamicEnum, ListOf

from SEQCROW.finders import AtomSpec
from SEQCROW.residue_collection import ResidueCollection, Residue


substitute_description = CmdDesc(required=[("selection", AtomsArg)], \
                                 keyword=[("substituents", ListOf(DynamicEnum(Substituent.list, \
                                                                  name="substituent", \
                                                                  case_sensitive=True, \
                                                                  url="http://catalysttrends.wheelergroupresearch.com/AaronTools/substituents.php")
                                                           )), 
                                          ("newName", ListOf(StringArg)), 
                                          ("guessAttachment", BoolArg),
                                          ("modify", BoolArg),
                                          ("minimize", BoolArg),
                                         ], \
                                 required_arguments=['substituents'], 
                                 synopsis="modify substituents")


def guessAttachmentTargets(selection, session, allow_adjacent=True):
    models = {}
    
    for atom in selection:        
        if any(bonded_atom in selection for bonded_atom in atom.neighbors):
            if allow_adjacent:
                try:
                    models, attached = avoidTargets(selection)
                    session.logger.warning("two adjacent atoms are both selected; use \"guessAttachment true\"")
                    return models, attached
                except:
                    pass
            else:
                raise RuntimeError("cannot select adjacent atoms")

        if atom.structure not in models:
            models[atom.structure] = {atom.residue:[atom]}

        else:
            if atom.residue not in models[atom.structure]:
                models[atom.structure][atom.residue] = [atom]
            else:
                models[atom.structure][atom.residue].append(atom)
    
    return models, None

def avoidTargets(selection):
    models = {}
    attached = {}

    for atom in selection:
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
    
    return models, attached

def substitute(session, selection, substituents, newName=None, guessAttachment=True, modify=True, minimize=False):
    attached = {}
    
    if newName is None:
        pass
    elif any(len(name.strip()) > 4 for name in newName):
        raise RuntimeError("residue names must be 4 characters or less")
    elif any(x in "".join(newName) for x in "!@#$%^&*()\\/.<><;':\"[]{}|-=_+"):
        raise RuntimeError("invalid residue name: %s" % " ".join(newName))
    elif len(substituents) != len(newName):
        raise RuntimeError("number of substituents is not the same as the number of new names")

    if not guessAttachment:
        models, attached = avoidTargets(selection)
    else:
        models, attached = guessAttachmentTargets(selection, session)

    first_pass = True
    new_structures = []
    for ndx, subname in enumerate(substituents):
        subname = subname.strip()
        sub = Substituent(subname)
        for model in models:
            if modify and first_pass:
                conv_res = []
                for res in models[model]:
                    conv_res.append(res)
                    if minimize:
                        for chix_res in model.residues:
                            if chix_res in conv_res:
                                continue

                            added_res = False
                            for atom in chix_res.atoms:
                                for target in models[model][res]:
                                    d = np.linalg.norm(atom.coord - target.coord)
                                    if d < 5:
                                        conv_res.append(chix_res)
                                        added_res = True
                                        break

                                if added_res:
                                    break

                rescol = ResidueCollection(model, convert_residues=conv_res)
                for res in models[model]:
                    residue = [resi for resi in rescol.residues if resi.chix_residue is res][0]
                    if newName is not None:
                        residue.name = newName[ndx]

                    for target in models[model][res]:
                        if attached is not None:
                            end = AtomSpec(attached[target].atomspec)
                        else:
                            end = None 

                        # call substitute on the ResidueCollection b/c we need to see
                        # the other residues if minimize=True
                        rescol.substitute(sub.copy(), AtomSpec(target.atomspec), attached_to=end, minimize=minimize)

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
                        for res in models[model]:
                            for target in models[model][res]:
                                for atom in chix_res.atoms:
                                    d = np.linalg.norm(atom.coord - target.coord)
                                    if d < 5:
                                        conv_res.append(chix_res)
                                        added_res = True
                                        break
                                
                                if added_res:
                                    break
                            
                            if added_res:
                                break

                rescol = ResidueCollection(model_copy, convert_residues=conv_res)
                for residue, res in zip(rescol.residues, models[model]):                        
                    res_copy = residue.chix_residue
                    if newName is not None:
                        residue.name = newName[ndx]

                    for target in models[model][res]:
                        if attached is not None:
                            end = AtomSpec(model_copy.atoms[model.atoms.index(attached[target])].atomspec)
                        else:
                            end = None

                        rescol.substitute(sub.copy(), 
                                           AtomSpec(model_copy.atoms[model.atoms.index(target)].atomspec), 
                                           attached_to=end, 
                                           minimize=minimize,
                        )

                    residue.update_chix(res_copy)

                new_structures.append(model_copy)

        first_pass = False

    if not modify:
        session.models.add(new_structures)