def open_aarontools(session, path, format_name=None, trajectory=False):
    from AaronTools.fileIO import FileReader
    from AaronTools.geometry import Geometry
    from ChimAARON.residue_collection import ResidueCollection
    from ChimAARON.managers import FILEREADER_ADDED
    from os.path import split as path_split
    from warnings import warn
    #XML_TAG ChimeraX :: DataFormat :: XYZ :: XYZ :: Molecular structure :: .xyz :: :: :: :: :: XYZ Format :: utf-8
    #XML_TAG ChimeraX :: Open :: XYZ :: AaronTools :: false :: coordsets:Bool
    #XML_TAG ChimeraX :: DataFormat :: COM :: Gaussian input file :: Molecular structure :: .com,.gjf :: :: :: :: :: Gaussian input file :: utf-8
    #XML_TAG ChimeraX :: Open :: COM :: Gaussian input file ::
    #XML_TAG ChimeraX :: DataFormat :: LOG :: Gaussian output file :: Molecular structure :: .log :: :: :: :: :: Gaussian output file :: utf-8
    #XML_TAG ChimeraX :: Open :: LOG :: Gaussian output file :: false :: coordsets:Bool
    #XML_TAG ChimeraX :: DataFormat :: OUT :: Orca output file :: Molecular structure :: .out :: :: :: :: :: Orca output file :: utf-8
    #XML_TAG ChimeraX :: Open :: OUT :: Orca output file :: false :: coordsets:Bool
    if format_name == "Gaussian input file":
        fmt = "com"
    elif format_name == "Gaussian output file":
        fmt = "log"    
    elif format_name == "Orca output file":
        fmt = "out"
    elif format_name == "XYZ":
        fmt = "xyz"
    else:
        fmt = path.split('.')[-1]
            
    f = FileReader((path, fmt, None), just_geom=False, get_all=True)

    geom = ResidueCollection(Geometry(f).copy())
    geom.name = path_split(path)[-1]

    structure = geom.get_chimera(session, coordsets=(len(f.all_geom) > 1), filereader=f)

    #associate the AaronTools FileReader with each structure
    session.filereader_manager.triggers.activate_trigger(FILEREADER_ADDED, ([structure], [f]))

    if trajectory:
        from chimerax.std_commands.coordset_gui import CoordinateSetSlider
        from ChimAARON.tools import EnergyPlot
        
        CoordinateSetSlider(session, structure)
        if "energy" in f.other:
            nrg_plot = EnergyPlot(session, structure)
            if not nrg_plot.opened:
                warn("energy plot could not be opened\n" + \
                     "there might be a mismatch between energy entries and structure entries in %s" % path)
                nrg_plot.delete()                    

    status = "Opened %s as a %s %s" % (path, fmt, "trajectory" if trajectory else "file")

    return [structure], status

def save_aarontools(session, path, format_name, **kwargs):
    """ 
    save XYZ file using AaronTools
    kwargs may be:
        comment - str
    """
    #XML: ChimeraX :: Save -> extra_keywords=models:Models
    #^ this doesn't do anything b/c save doesn't expect a 'comment' keyword
    from ChimAARON.residue_collection import ResidueCollection
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