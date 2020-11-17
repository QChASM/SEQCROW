import numpy as np

from io import BytesIO

from chimerax.core.commands import BoolArg, StringArg, CmdDesc, EnumOf
from chimerax.atomic import AtomsArg
from chimerax.bild.bild import read_bild

from AaronTools.substituent import Substituent
from AaronTools.const import VDW_RADII, BONDI_RADII

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec
from SEQCROW.commands.substitute import avoidTargets

sterimol_description = CmdDesc(required=[("selection", AtomsArg)], \
                               keyword=[("radii", EnumOf(["UMN", "Bondi"], 
                                                         case_sensitive=False,
                                                  ),
                                        ),
                                        ("showVectors", BoolArg),
                                        ("showRadii", BoolArg), 
                               ],
                               synopsis="calculate Sterimol B1, B5, and L"
                       )

def sterimol(session, selection, radii="UMN", showVectors=True, showRadii=True, return_values=False):
    models, attached = avoidTargets(selection)
    
    radii = radii.lower()
    
    l = None
    b1 = None
    b5 = None
    targets = []
    neighbors = []
    ls = []
    b1s = []
    b5s = []
    
    info = "<pre>substituent atom\tbonded atom\tL\tB1\tB5\n"
    
    if return_values:
        if len(models.keys()) > 1:
            raise RuntimeError("only one substituent may be selected")
        
        if any(len(models[key]) > 1 for key in models.keys()):
            raise RuntimeError("only one substituent may be selected")
    
    for model in models:
        rescol = ResidueCollection(model)
        for res in models[model]:
            for target in models[model][res]:
                end_atomspec = AtomSpec(attached[target].atomspec)
                start_atomspec = AtomSpec(target.atomspec)
                
                sub_atoms = rescol.get_fragment(start_atomspec, end_atomspec)
                sub = Substituent(sub_atoms, 
                                  end=rescol.find_exact(end_atomspec)[0], 
                                  detect=False,
                      )
                
                l_start, l_end = sub.sterimol("L", return_vector=True, radii=radii)
                l = np.linalg.norm(l_end - l_start)
                
                b1_start, b1_end = sub.sterimol("B1", return_vector=True, radii=radii)
                b1 = np.linalg.norm(b1_end - b1_start)
                
                b5_start, b5_end = sub.sterimol("B5", return_vector=True, radii=radii)
                b5 = np.linalg.norm(b5_end - b5_start)
                
                s = ""
                if showVectors:
                    s += ".color black\n"
                    s += ".note Sterimol B1\n"
                    s += ".arrow %6.3f %6.3f %6.3f   %6.3f %6.3f %6.3f   0.1 0.25 %f\n" % (*b1_start, *b1_end, b1/(b1 + 0.75))
                    s += ".color red\n"
                    s += ".note Sterimol B5\n"
                    s += ".arrow %6.3f %6.3f %6.3f   %6.3f %6.3f %6.3f   0.1 0.25 %f\n" % (*b5_start, *b5_end, b5/(b5 + 0.75))
                    s += ".color blue\n"
                    s += ".note Sterimol L\n"
                    s += ".arrow %6.3f %6.3f %6.3f   %6.3f %6.3f %6.3f   0.1 0.25 %f\n" % (*l_start, *l_end, l/(l + 0.75))
                
                if showRadii:
                    s += ".note radii\n"
                    s += ".transparency 75\n"
                    color = None
                    for atom in sub.atoms:
                        chix_atom = atom.chix_atom
                        if radii == "umn":
                            r = VDW_RADII[chix_atom.element.name]
                        elif radii == "bondi":
                            r = BONDI_RADII[chix_atom.element.name]
                        
                        if color is None or chix_atom.color != color:
                            color = chix_atom.color
                            rgb = [x/255. for x in chix_atom.color]
                            rgb.pop(-1)
                            
                            s += ".color %f %f %f\n" % tuple(rgb)
                        
                        s += ".sphere %f %f %f %f\n" % (*chix_atom.coord, r)
                
                if showVectors or showRadii:
                    stream = BytesIO(bytes(s, "utf-8"))
                    bild_obj, status = read_bild(session, stream, "Sterimol")
                    
                    session.models.add(bild_obj, parent=model)
                
                info += "%-16s\t%-11s\t%.2f\t%.2f\t%.2f\n" % (target.atomspec, attached[target].atomspec, l, b1, b5)
                targets.append(target.atomspec)
                neighbors.append(attached[target].atomspec)
                ls.append(l)
                b1s.append(b1)
                b5s.append(b5)
    
    info = info.strip()
    info += "</pre>"
    if not return_values:
        session.logger.info(info, is_html=True)
    
    if return_values:
        return targets, neighbors, ls, b1s, b5s