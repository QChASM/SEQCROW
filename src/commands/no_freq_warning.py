from SEQCROW.tools.ir_plot import IRSpectrum
from chimerax.core.commands import CmdDesc

freq_warning_description = CmdDesc(
    synopsis="remove warning about imaginary frequencies on the IR tool",
)

def freq_warning(session):
    """
    """
    for tool in session.tools.list():
        if isinstance(tool, IRSpectrum):
            fig = tool.figure
            for ax in fig.axes:
                for t in ax.texts:
                    if t.get_text() == "warning: one or more imaginary frequencies":
                        t.remove()
            
            tool.canvas.draw()