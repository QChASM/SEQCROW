import numpy as np

from io import BytesIO

from chimerax.core.commands import BoolArg, CmdDesc, EnumOf, FloatArg
from chimerax.atomic import AtomsArg
from chimerax.bild.bild import read_bild

from AaronTools.substituent import Substituent
from AaronTools.const import VDW_RADII, BONDI_RADII

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec
from SEQCROW.commands.substitute import avoidTargets
from AaronTools.utils.utils import get_filename

sterimol_description = CmdDesc(
    required=[("selection", AtomsArg)], \
    keyword=[
        ("radii", EnumOf(["UMN", "Bondi"], case_sensitive=False)),
        ("showVectors", BoolArg),
        ("showRadii", BoolArg), 
        ("LCorrection", EnumOf(["FORTRAN", "AaronTools"], case_sensitive=False)), 
        ("at_L", FloatArg), 
    ],
    synopsis="calculate Sterimol B1-B5, and L",
    url="https://github.com/QChASM/SEQCROW/wiki/Commands#sterimol",
)

def sterimol(
        session,
        selection,
        radii="UMN",
        showVectors=True,
        showRadii=True,
        LCorrection="FORTRAN",
        at_L=None,
        return_values=False,
    ):
    models, attached = avoidTargets(session.logger, selection)
    
    radii = radii.lower()

    old_L = False
    if LCorrection.upper() == "FORTRAN":
        old_L = True

    model_names = []
    targets = []
    datas = []
    
    info = "<pre>%s\n" % "\t".join([
        "model",
        "substituent atom",
        "B<sub>1</sub>",
        "B<sub>2</sub>",
        "B<sub>3</sub>",
        "B<sub>4</sub>",
        "B<sub>5</sub>",
        "L",
        "B<sub>perp_big</sub>",
        "B<sub>perp_small</sub>",
    ])
    
    # if return_values:
        # if len(models.keys()) > 1:
        #     raise RuntimeError("only one substituent may be selected")
        
        # if any(len(models[key]) > 1 for key in models.keys()):
        #     raise RuntimeError("only one substituent may be selected")
    
    for model in models:
        rescol = ResidueCollection(model, refresh_ranks=False)
        for res in models[model]:
            for target in models[model][res]:
                end_atomspec = AtomSpec(attached[target].atomspec)
                start_atomspec = AtomSpec(target.atomspec)
                
                sub_atoms = rescol.get_fragment(start_atomspec, end_atomspec)
                sub = Substituent(
                    sub_atoms, 
                    end=rescol.find_exact(end_atomspec)[0], 
                    detect=False,
                )
                
                data = sub.sterimol(
                    return_vector=True,
                    radii=radii,
                    old_L=old_L,
                    at_L=at_L,
                )
                l = np.linalg.norm(data["L"][1] - data["L"][0])
                b1 = np.linalg.norm(data["B1"][1] - data["B1"][0])
                b2 = np.linalg.norm(data["B2"][1] - data["B2"][0])
                b3 = np.linalg.norm(data["B3"][1] - data["B3"][0])
                b4 = np.linalg.norm(data["B4"][1] - data["B4"][0])
                b5 = np.linalg.norm(data["B5"][1] - data["B5"][0])
                bperp_big = np.linalg.norm(data["Bperp_big"][1] - data["Bperp_big"][0])
                bperp_small = np.linalg.norm(data["Bperp_small"][1] - data["Bperp_small"][0])
                
                if showVectors:
                    for key, color in zip(
                            ["B1", "B2", "B3", "B4", "B5", "L"],
                            ["black", "green", "purple", "orange", "red", "blue"]
                    ):
                        start, end = data[key]
                        s = ".color %s\n" % color
                        s += ".note Sterimol %s\n" % key
                        s += ".arrow %6.3f %6.3f %6.3f   %6.3f %6.3f %6.3f\n" % (*start, *end)
                        
                        stream = BytesIO(bytes(s, "utf-8"))
                        bild_obj, status = read_bild(session, stream, "Sterimol %s" % key)
                        
                        session.models.add(bild_obj, parent=model)
                    
                if showRadii:
                    s = ".note radii\n"
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
                
                    stream = BytesIO(bytes(s, "utf-8"))
                    bild_obj, status = read_bild(session, stream, "Sterimol radii")
                    
                    session.models.add(bild_obj, parent=model)
                
                model_name = get_filename(model.name, include_parent_dir=False)
                
                info += "%-16s\t%-11s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (
                    model_name,
                    target.atomspec,
                    b1, b2, b3, b4, b5, l, bperp_big, bperp_small
                )
                model_names.append(model_name)
                targets.append(target.atomspec)
                datas.append(data)
    
    info = info.strip()
    info += "</pre>"
    if not return_values:
        session.logger.info(info, is_html=True)
    
    if return_values:
        return model_names, targets, datas