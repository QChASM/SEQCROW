import numpy as np

from AaronTools.substituent import Substituent

from chimerax.atomic import OrderedAtomsArg
from chimerax.core.commands import BoolArg, CmdDesc


angle_description = CmdDesc(required=[("selection", OrderedAtomsArg)], \
                            keyword=[("radians", BoolArg)], \
                            synopsis="calculate angle defined by 3 atoms")


def angle(session, selection, radians=False):
    clicked_selection = session.seqcrow_ordered_selection_manager.selection
    
    if all(x in selection for x in clicked_selection) and all(x in clicked_selection for x in selection):
        selection = clicked_selection
    
    if len(selection) != 3:
        session.logger.error("must select 3 atoms (%i selected)" % len(selection))
        return

    a1, a2, a3 = selection

    v1 = a1.coord - a2.coord
    v2 = a3.coord - a2.coord
    
    dot = np.dot(v1, v2)
    theta = np.arccos(dot / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    if not radians:
        theta = np.rad2deg(theta)

    session.logger.info("%s-%s-%s angle: %.2f" % (a1.atomspec, a2.atomspec, a3.atomspec, theta))
    session.logger.status("%s-%s-%s angle: %.2f" % (a1.atomspec, a2.atomspec, a3.atomspec, theta))