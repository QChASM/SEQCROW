import numpy as np

from AaronTools.substituent import Substituent

from chimerax.atomic import OrderedAtomsArg
from chimerax.core.commands import BoolArg, CmdDesc


dihedral_description = CmdDesc(required=[("selection", OrderedAtomsArg)], \
                            keyword=[("radians", BoolArg)], \
                            synopsis="calculate dihedral angle defined by 4 atoms")


def dihedral(session, selection, radians=False):
    clicked_selection = session.seqcrow_ordered_selection_manager.selection
    
    if all(x in selection for x in clicked_selection) and all(x in clicked_selection for x in selection):
        selection = clicked_selection
    
    if len(selection) != 4:
        session.logger.error("must select 4 atoms (%i selected)" % len(selection))
        return

    a1, a2, a3, a4 = selection

    b12 = a2.coord - a1.coord
    b23 = a3.coord - a2.coord
    b34 = a4.coord - a3.coord

    dihedral = np.cross(np.cross(b12, b23), np.cross(b23, b34))
    dihedral = np.dot(dihedral, b23) / np.linalg.norm(b23)
    dihedral = np.arctan2(
        dihedral, np.dot(np.cross(b12, b23), np.cross(b23, b34))
    )
        
    if not radians:
        dihedral = np.rad2deg(dihedral)

    session.logger.info("%s-%s-%s-%s diheral angle: %.2f" % (a1.atomspec, a2.atomspec, a3.atomspec, a4.atomspec, dihedral))
    session.logger.status("%s-%s-%s-%s dihedral angle: %.2f" % (a1.atomspec, a2.atomspec, a3.atomspec, a4.atomspec, dihedral))