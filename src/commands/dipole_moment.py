from io import BytesIO

from chimerax.atomic import AtomicStructuresArg
from chimerax.bild.bild import read_bild
from chimerax.core.commands import ColorArg, CmdDesc, run, FloatArg, EnumOf, IntArg

from AaronTools.const import UNIT

from SEQCROW.residue_collection import ResidueCollection

import numpy as np

dipole_moment_description = CmdDesc(
    required=[("selection", AtomicStructuresArg)],
    keyword=[
        ("transparency", FloatArg),
        ("kind",
            EnumOf([
                # "charge",
                "transitionElectric", 
                "transitionVelocity",
                "transitionMagnetic",
            ])
        ),
        ("origin",
            EnumOf([
                "nuclearCharge", 
                "centerOfMass",
                "centroid",
                "zero",
            ])
        ),
        ("scale", FloatArg),
        ("color", ColorArg),
        ("state", IntArg),
    ],
    synopsis="draw a forming/breaking bond",
)


def dipole_moment(
    session,
    selection,
    kind="transitionElectric",
    transparency=100,
    color=[250, 50, 115, 255],
    origin="nuclearCharge",
    state=1,
    scale=1,
):   
    if not isinstance(color, list):
        color = color.uint8x4()
    color = [c / 255. for c in color][:-1]
    color.append(int( 255 * ( transparency / 100.)))
    if transparency > 100 or transparency < 0:
        session.logger.error("transparency must be between 0 and 100")
        return
    
    for model in selection:
        fr = model.filereaders[-1]
        try:
            uv_vis = fr["uv_vis"]
        except KeyError:
            session.logger.warning("no UV/vis for %s (%s)" % (model.name, model.atomspec))
            return
        
        s = ".color %f %f %f\n" % tuple(color[:-1])
        s += ".transparency %f\n" % max((1. - color[-1]), 0)
        if origin == "zero":
            x0 = np.zeros(3)
        else:
            rescol = ResidueCollection(model, bonds_matter=False)
            x0 = rescol.COM(mass_weight=origin == "centerOfMass", charge_weight=origin == "nuclearCharge")
        
        try:
            if kind == "transitionElectric":
                label = "transition electric"
                v = uv_vis.data[state - 1].dipole_len_vec
            elif kind == "transitionVelocity":
                label = "transition velocity"
                v = uv_vis.data[state - 1].dipole_vel_vec
            elif kind == "transitionMagnetic":
                label = "transition magnetic"
                v = uv_vis.data[state - 1].magnetic_mom

        except IndexError:
            session.logger.warning("no state %i for %s (%s)" % (state, model.name, model.atomspec))
            return
        
        v = scale * np.array(v)
        n = np.linalg.norm(v)
        v = v + x0
        r = n / (n + 0.75)
        s += ".arrow %10.6f %10.6f %10.6f   %10.6f %10.6f %10.6f  0.02 0.05 %5.3f\n" % (
            *x0, *v, r
        )

        print(s)

        stream = BytesIO(bytes(s, 'utf-8'))
        bild_obj, status = read_bild(session, stream, label + " dipole moment for state %i" % state)

        model.add(bild_obj)
