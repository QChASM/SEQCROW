import numpy as np

from chimerax.core.commands import CmdDesc, EnumOf, BoolArg
from chimerax.atomic import AtomsArg

from AaronTools.utils.utils import rotation_matrix

lookDown_description = CmdDesc(
    required=[
        ("atom1", AtomsArg),
    ],
    keyword=[
        ("atom2", AtomsArg),
        ("axis", EnumOf(["x", "y", "z"])), 
        ("printRotation", BoolArg),
    ],
    required_arguments=["atom2"],
    synopsis="orient the molecule such that the atom1-atom2 vector is out of the screen",
    url="https://github.com/QChASM/SEQCROW/wiki/Commands#lookdown",
)

def lookDown(session, atom1, atom2, axis="z", printRotation=False):
    models_g1 = dict()
    for atom in atom1:
        if atom.structure not in models_g1:
            models_g1[atom.structure] = []
        models_g1[atom.structure].append(atom)
    
    models_g2 = dict()
    for atom in atom2:
        if atom.structure not in models_g2:
            models_g2[atom.structure] = []
        models_g2[atom.structure].append(atom)
    
    if axis == "z":
        align_to = session.view.camera.get_position().axes()[2]
    if axis == "y":
        align_to = session.view.camera.get_position().axes()[1]
    if axis == "x":
        align_to = session.view.camera.get_position().axes()[0]
    
    for model in models_g1:
        if model not in models_g2:
            continue
        
        stop = sum([atom.coord for atom in models_g1[model]]) / len(models_g1[model])
        start = sum([atom.coord for atom in models_g2[model]]) / len(models_g2[model])
    
        v = stop - start
        if np.linalg.norm(v) < 1e-6:
            session.warning("short vector for model %s" % model.atomspec)
        v /= np.linalg.norm(v)
        
        rot_axis = np.cross(align_to, v)
        dot = np.dot(v, align_to)
        if dot > 1:
            dot = 1
        elif dot < -1:
            dot = -1
        angle = np.arccos(dot)
        
        rot_mat = rotation_matrix(-angle, rot_axis).T
        
        if printRotation:
            session.logger.info("rotation matrix:\n%s" % "\n".join([",".join(["%.3f" % x for x in r]) for r in rot_mat]))
            session.logger.info("rotation center: %s" % str(start))
        
        xyzs = model.active_coordset.xyzs
        xyzs -= start
        xyzs = np.dot(xyzs, rot_mat)
        xyzs += start
        for atom, coord in zip(model.atoms, xyzs):
            atom.coord = coord