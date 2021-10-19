from io import BytesIO

from chimerax.atomic import AtomicStructuresArg
from chimerax.bild.bild import read_bild
from chimerax.core.commands import CmdDesc, FloatArg, BoolArg, IntArg

from SEQCROW.residue_collection import ResidueCollection

from AaronTools.atoms import Atom
from AaronTools.symmetry import (
    PointGroup,
    ProperRotation,
    ImproperRotation,
    MirrorPlane,
    InversionCenter,
)
from AaronTools.utils.utils import perp_vector

import numpy as np

pointGroup_description = CmdDesc(
    required=[("selection", AtomicStructuresArg)],
    keyword=[
        ("printElements", BoolArg),
        ("displayElements", BoolArg),
        ("residuesOnly", BoolArg),
        ("tolerance", FloatArg),
        ("axisTolerance", FloatArg),
        ("maxRotation", IntArg),
        ("symmetryNumber", BoolArg),
    ],
    synopsis="print the point group of atomic structures to the log",
    url="https://github.com/QChASM/SEQCROW/wiki/Commands#pointGroup",
)


def pointGroup(
        session,
        selection,
        printElements=False,
        displayElements=True,
        residuesOnly=False,
        tolerance=0.1,
        axisTolerance=0.5,
        maxRotation=6,
        symmetryNumber=False,
):

    out = []
    for model in selection:
        if not residuesOnly:
            rescol = ResidueCollection(model, refresh_ranks=False)
            pg = PointGroup(
                rescol,
                tolerance=tolerance,
                rotation_tolerance=np.deg2rad(axisTolerance),
                max_rotation=maxRotation,
            )
        else:
            atoms = []
            groups = []
            for residue in model.residues:
                atoms.append(Atom(element="H", coords=residue.center))
                groups.append(residue.name)
            rescol = ResidueCollection(atoms, refresh_ranks=False)
            pg = PointGroup(
                rescol,
                tolerance=tolerance,
                rotation_tolerance=np.deg2rad(axisTolerance),
                max_rotation=maxRotation,
                groups=groups,
            )
        session.logger.info("%s: %s" % (model.name, pg.name))
        out.append(pg.name)
        if symmetryNumber:
            session.logger.info(
                "the rotational symmetry number for this point group is %i" % pg.symmetry_number
            )
            out[-1] = (pg.name, pg.symmetry_number)

        if printElements:
            for ele in sorted(pg.elements, reverse=True):
                session.logger.info(repr(ele))
        
        if displayElements:
            for ele in sorted(pg.elements, reverse=True):
                if isinstance(ele, InversionCenter):
                    inv = ".note %s\n" % repr(ele)
                    inv += ".sphere   %.5f  %.5f  %.5f  0.1\n" % tuple(pg.center)
                    
                    stream = BytesIO(bytes(inv, "utf-8"))
                    bild_obj, status = read_bild(session, stream, repr(ele))
                    session.models.add(bild_obj, parent=model)

                elif isinstance(ele, ProperRotation):
                    prots = ".note %s\n" % repr(ele)
                    prots += ".color red\n"
                    prots += ".arrow   %.5f  %.5f  %.5f  " % tuple(pg.center)
                    end = pg.center + ele.n * np.sqrt(ele.exp) * ele.axis
                    prots += "%.5f  %.5f  %.5f  0.05\n"  % tuple(end)
                    
                    stream = BytesIO(bytes(prots, "utf-8"))
                    bild_obj, status = read_bild(session, stream, repr(ele))
                    session.models.add(bild_obj, parent=model)

                elif isinstance(ele, ImproperRotation):
                    irots = ".note %s\n" % repr(ele)
                    irots += ".color blue\n"
                    irots += ".arrow   %.5f  %.5f  %.5f  " % tuple(pg.center)
                    end = pg.center + np.sqrt(ele.n) * np.sqrt(ele.exp) * ele.axis
                    irots += "%.5f  %.5f  %.5f  0.05\n"  % tuple(end)
                    irots += ".transparency 25\n"
                    z = ele.axis
                    x = perp_vector(z)
                    y = np.cross(x, z)
                    for angle in np.linspace(0, 2 * np.pi, num=250):
                        pt2 = ele.n ** 0.9 * x * np.cos(angle)
                        pt2 += ele.n ** 0.9 * y * np.sin(angle)
                        pt2 += pg.center
                        if angle > 0:
                            irots += ".polygon  %6.3f  %6.3f  %6.3f" % tuple(pt1)
                            irots += "     %6.3f  %6.3f  %6.3f" % tuple(pg.center)
                            irots += "     %6.3f  %6.3f  %6.3f" % tuple(pt2)
                            irots += "\n"
                        pt1 = pt2
                    
                    stream = BytesIO(bytes(irots, "utf-8"))
                    bild_obj, status = read_bild(session, stream, repr(ele))
                    session.models.add(bild_obj, parent=model)
    
                elif isinstance(ele, MirrorPlane):
                    mirror = ".note %s\n" % repr(ele)
                    mirror += ".color purple\n"
                    mirror += ".transparency 25\n"
                    z = ele.axis
                    x = perp_vector(z)
                    y = np.cross(x, z)
                    for angle in np.linspace(0, 2 * np.pi, num=250):
                        pt2 = 5 * x * np.cos(angle)
                        pt2 += 5 * y * np.sin(angle)
                        pt2 += pg.center
                        if angle > 0:
                            mirror += ".polygon  %6.3f  %6.3f  %6.3f" % tuple(pt1)
                            mirror += "     %6.3f  %6.3f  %6.3f" % tuple(pg.center)
                            mirror += "     %6.3f  %6.3f  %6.3f" % tuple(pt2)
                            mirror += "\n"
                        pt1 = pt2
                    
                    stream = BytesIO(bytes(mirror, "utf-8"))
                    bild_obj, status = read_bild(session, stream, repr(ele))
                    session.models.add(bild_obj, parent=model)
    
    return out