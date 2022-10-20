from io import BytesIO

from chimerax.atomic import AtomicStructuresArg
from chimerax.bild.bild import read_bild
from chimerax.core.commands import ColorArg, CmdDesc, run, FloatArg

from AaronTools.const import UNIT

import numpy as np

force_description = CmdDesc(
    required=[("selection", AtomicStructuresArg)],
    keyword=[
        ("transparency", FloatArg),
        ("color", ColorArg),
    ],
    synopsis="draw a forming/breaking bond",
    url="https://github.com/QChASM/SEQCROW/wiki/Commands#tsbond",
)


def force(session, selection, transparency=100, color=[250, 50, 115, 255]):   
    if not isinstance(color, list):
        color = color.uint8x4()
    color = [c for c in color][:-1]
    color.append(int( 255 * ( transparency / 100.)))
    print(color)
    if transparency > 100 or transparency < 0:
        session.logger.error("transparency must be between 0 and 100")
        return
    
    for model in selection:
        fr = session.filereader_manager.filereader_dict[model][-1]
        try:
            forces = fr.other["forces"]
        except KeyError:
            session.logger.warning("no forces for %s (%s)" % (model.name, model.atomspec))
        
        s = ".color %f %f %f\n" % tuple(color[:-1])
        s += ".transparency %f\n" % max((1. - color[-1]), 0)
        i = 0
        for atom, dx in zip(model.atoms, forces):
            disp = atom.coord + dx * UNIT.HART_TO_EV
            n = np.linalg.norm(dx)
            r = n / (n + 0.75)
            s += ".arrow %10.6f %10.6f %10.6f   %10.6f %10.6f %10.6f  0.02 0.05 %5.3f\n" % (
                *atom.coord, *disp, r
            )
        
        print(s)
        
        stream = BytesIO(bytes(s, 'utf-8'))
        bild_obj, status = read_bild(session, stream, "force (eV/Bohr)")

        model.add(bild_obj)
