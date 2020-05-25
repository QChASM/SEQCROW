def open_aarontools(session, path, format_name=None, coordsets=False):
    from AaronTools.fileIO import FileReader
    from AaronTools.geometry import Geometry
    from SEQCROW.residue_collection import ResidueCollection
    from SEQCROW.managers import FILEREADER_ADDED
    from os.path import split as path_split
    from warnings import warn

    if format_name == "Gaussian input file":
        fmt = "com"
    elif format_name == "Gaussian output file":
        fmt = "log"    
    elif format_name == "ORCA output file":
        fmt = "out"
    elif format_name == "XYZ file":
        fmt = "xyz"
    else:
        fmt = path.split('.')[-1]
            
    f = FileReader((path, fmt, None), just_geom=False, get_all=True)

    geom = ResidueCollection(Geometry(f))
    geom.name = path_split(path)[-1]

    structure = geom.get_chimera(session, coordsets=(f.all_geom is not None and len(f.all_geom) > 1), filereader=f)

    #associate the AaronTools FileReader with each structure
    session.filereader_manager.triggers.activate_trigger(FILEREADER_ADDED, ([structure], [f]))

    if coordsets:
        from chimerax.std_commands.coordset_gui import CoordinateSetSlider
        from SEQCROW.tools import EnergyPlot
        
        slider = CoordinateSetSlider(session, structure)
        if "energy" in f.other:
            nrg_plot = EnergyPlot(session, structure)
            if not nrg_plot.opened:
                warn("energy plot could not be opened\n" + \
                     "there might be a mismatch between energy entries and structure entries in %s" % path)
                nrg_plot.delete()                    

    if f.all_geom is not None and len(f.all_geom) > 1:
        structure.active_coordset_id = len(f.all_geom)
        if coordsets:
            slider.set_slider(len(f.all_geom))

    status = "Opened %s as a %s %s" % (path, format_name, "movie" if coordsets else "")

    return [structure], status

def save_aarontools(session, path, format_name, **kwargs):
    """ 
    save XYZ file using AaronTools
    kwargs may be:
        comment - str
    """
    #XML: ChimeraX :: Save -> extra_keywords=models:Models
    #^ this doesn't do anything b/c save doesn't expect a 'comment' keyword
    from SEQCROW.residue_collection import ResidueCollection
    from AaronTools.geometry import Geometry
    from chimerax.atomic import AtomicStructure
    
    accepted_kwargs = ['comment', 'models']
    unknown_kwargs = [kw for kw in kwargs if kw not in accepted_kwargs]
    if len(unknown_kwargs) > 0:
        raise RuntimeWarning("unrecognized keyword%s %s?" % ("s" if len(unknown_kwargs) > 1 else "", ", ".join(unknown_kwargs)))
    
    if 'models' in kwargs:
        models = kwargs['models']
    else:
        models = None
    
    if models is None:
        models = session.models.list(type=AtomicStructure)

    models = [m for m in models if isinstance(m, AtomicStructure)]
    
    if len(models) < 1:
        raise RuntimeError('nothing to save')
    
    res_cols = [ResidueCollection(model) for model in models]
    atoms = []
    for res in res_cols:
        atoms.extend(res.atoms)
        
    geom = Geometry(atoms)
    
    if 'comment' in kwargs:
        geom.comment = kwargs[comment]
    
    geom.write(outfile=path)
