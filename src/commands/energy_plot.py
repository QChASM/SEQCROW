from chimerax.atomic import AtomicStructuresArg
from chimerax.core.commands import CmdDesc
from SEQCROW.tools.per_frame_plot import EnergyPlot

energy_plot_description = CmdDesc(
    required=[("selection", AtomicStructuresArg)],
    synopsis="open the energy vs step plot",
)


def energy_plot(session, selection):   
    for model in selection:
        try:
            fr = model.filereaders[-1]
            nrg_plot = EnergyPlot(
                session,
                model,
                fr,
            )
        except IndexError:
            session.logger.warning("no energies for %s" % model.name)
        


close_energy_plot_description = CmdDesc(
    required=[("selection", AtomicStructuresArg)],
    synopsis="close the energy vs step plot",
)


def close_energy_plot(session, selection):   
    for model in selection:
        for tool in session.tools.list():
            if isinstance(tool, EnergyPlot):
                    if tool.structure is model:
                        tool.delete()
                        break
        
