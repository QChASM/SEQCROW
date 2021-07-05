import numpy as np

from io import BytesIO

from chimerax.core.commands import BoolArg, CmdDesc, EnumOf, FloatArg
from chimerax.atomic import AtomsArg
from chimerax.bild.bild import read_bild

from AaronTools.component import Component
from AaronTools.const import VDW_RADII, BONDI_RADII
from AaronTools.utils.utils import get_filename

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec


def avoidTargets(logger, selection):
    models = {}
    center = {}
    key_atoms = {}

    for atom in selection:
        for bond in atom.bonds:
            atom2 = bond.other_atom(atom)
            if atom2 not in selection:
                # if atom in attached:
                #     logger.warning(
                #         "cannot determine previous substituent\n" +
                #         "substituents should have one bond to the rest of the molecule\n" +
                #         "it is assumed that the substituent(s) is/are selected and the rest of the molecule is not\n" +
                #         "this selection has at least two bonds to the rest of the molecule:\n" +
                #         "%s-%s\n%s-%s" % (atom.atomspec, attached[atom].atomspec, atom.atomspec, atom2.atomspec)
                #     )
    
                if atom.structure not in key_atoms:
                    key_atoms[atom.structure] = []
                key_atoms[atom.structure].append(atom)
                
                if atom2.structure in center and atom2 in center[atom2.structure]:
                    continue
                if atom2.structure not in center:
                    center[atom2.structure] = []
                center[atom2.structure].append(atom2)

        pbg = atom.structure.pseudobond_group(atom.structure.PBG_METAL_COORDINATION, create_type='normal')
        for pbond in pbg.pseudobonds:
            if atom in pbond.atoms:
                atom2 = [a for a in pbond.atoms if a is not atom][0]
                if atom2 not in selection:
                    # if atom in attached:
                    #     logger.warning(
                    #         "cannot determine previous substituent\n" +
                    #         "substituents should have one bond to the rest of the molecule\n" +
                    #         "it is assumed that the substituent(s) is/are selected and the rest of the molecule is not\n" +
                    #         "this selection has at least two bonds to the rest of the molecule:\n" +
                    #         "%s-%s\n%s-%s" % (atom.atomspec, attached[atom].atomspec, atom.atomspec, atom2.atomspec)
                    #     )
        
                    if atom.structure not in key_atoms:
                        key_atoms[atom.structure] = []
                    key_atoms[atom.structure].append(atom)
        
                    if atom2.structure in center and atom2 in center[atom2.structure]:
                        continue
                    if atom2.structure not in center:
                        center[atom2.structure] = []
                    center[atom2.structure].append(atom2)

        if atom.structure not in models:
            models[atom.structure] = [atom]
        
        models[atom.structure].append(atom)

    return models, center, key_atoms



sterimol_description = CmdDesc(
    required=[("selection", AtomsArg)], \
    keyword=[
        ("radii", EnumOf(["UMN", "Bondi"], case_sensitive=False)),
        ("showVectors", BoolArg),
        ("showRadii", BoolArg), 
        ("bisect_L", BoolArg),
        ("at_L", FloatArg), 
    ],
    synopsis="calculate Sterimol B1-B5, and L for a ligand on a metal center",
    url="https://github.com/QChASM/SEQCROW/wiki/Commands#ligandSterimol",
)

def ligandSterimol(
        session,
        selection,
        radii="UMN",
        showVectors=True,
        showRadii=True,
        at_L=None,
        bisect_L=False,
        return_values=False
    ):
    models, center, key_atoms = avoidTargets(session.logger, selection)
    
    radii = radii.lower()

    targets = []
    coord_atoms = []
    datas = []
    
    info = "<pre>model\tcoord. atoms\tB1\tB2\tB3\tB4\tB5\tL\n"
    
    # if return_values:
        # if len(models.keys()) > 1:
        #     raise RuntimeError("only one substituent may be selected")
        
        # if any(len(models[key]) > 1 for key in models.keys()):
        #     raise RuntimeError("only one substituent may be selected")
    
    for model in models:
        rescol = ResidueCollection(model)
        comp_atoms = [AtomSpec(at.atomspec) for at in models[model]]
        key_atomspec = [AtomSpec(at.atomspec) for at in key_atoms[model]]
        center_atomspec = [AtomSpec(at.atomspec) for at in center[model]]
        if len(center_atomspec) != 1:
            session.logger.error(
                "ligand sterimol requires one central atom to which " + \
                "the ligand is coordinated\n" + \
                "%i were found on model %s:\n" % (len(center_atomspec), model.atomspec) + \
                "\n".join([at.atomspec for at in center[model]])
            )
            continue
        
        comp = Component(
            rescol.find(comp_atoms), 
            to_center=rescol.find(center_atomspec), 
            key_atoms=rescol.find(key_atomspec),
        )
        
        data = comp.sterimol(
            return_vector=True,
            radii=radii,
            at_L=at_L,
            to_center=rescol.find(center_atomspec),
            bisect_L=bisect_L,
        )
        l = np.linalg.norm(data["L"][1] - data["L"][0])
        b1 = np.linalg.norm(data["B1"][1] - data["B1"][0])
        b2 = np.linalg.norm(data["B2"][1] - data["B2"][0])
        b3 = np.linalg.norm(data["B3"][1] - data["B3"][0])
        b4 = np.linalg.norm(data["B4"][1] - data["B4"][0])
        b5 = np.linalg.norm(data["B5"][1] - data["B5"][0])
        
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
            for atom in comp.atoms:
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
        
        name = get_filename(model.name, include_parent_dir=False)
        
        info += "%-16s\t%-11s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (
            name,
            ", ".join(at.atomspec for at in key_atoms[model]),
            b1, b2, b3, b4, b5, l
        )
        targets.append(name)
        coord_atoms.append([at.atomspec for at in key_atoms[model]])
        datas.append(data)
    
    info = info.strip()
    info += "</pre>"
    if not return_values:
        session.logger.info(info, is_html=True)
    
    if return_values:
        return targets, coord_atoms, datas