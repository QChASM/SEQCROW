def open_aarontools(session, stream, file_name, format_name=None, coordsets=False):
    from AaronTools.fileIO import FileReader
    from AaronTools.geometry import Geometry
    from SEQCROW.residue_collection import ResidueCollection
    from SEQCROW.managers import ADD_FILEREADER
    from os.path import split as path_split
    from warnings import warn

    if format_name == "Gaussian input file":
        fmt = "com"
    elif format_name == "Gaussian output file":
        fmt = "log"    
    elif format_name == "ORCA output file":
        fmt = "out"
    elif format_name == "Psi4 output file":
        fmt = "dat"
    elif format_name == "XYZ file":
        fmt = "xyz"
    elif format_name == "FCHK file":
        fmt = "fchk"

    fr = FileReader((file_name, fmt, stream), just_geom=False, get_all=True)

    if hasattr(stream, "close") and callable(stream.close):
        stream.close()

    geom = ResidueCollection(fr)

    structure = geom.get_chimera(session, coordsets=(fr.all_geom is not None and len(fr.all_geom) > 1), filereader=fr)
    #associate the AaronTools FileReader with each structure
    session.filereader_manager.triggers.activate_trigger(ADD_FILEREADER, ([structure], [fr]))

    if coordsets:
        from chimerax.std_commands.coordset_gui import CoordinateSetSlider
        from SEQCROW.tools import EnergyPlot
        
        slider = CoordinateSetSlider(session, structure)
        if "energy" in fr.other:
            nrg_plot = EnergyPlot(session, structure, fr)
            if not nrg_plot.opened:
                warn("energy plot could not be opened\n" + \
                     "there might be a mismatch between energy entries and structure entries in %s" % file_name)
                nrg_plot.delete()                    

    if fr.all_geom is not None and len(fr.all_geom) > 1:
        structure.active_coordset_id = len(fr.all_geom)
        if coordsets:
            slider.set_slider(len(fr.all_geom))

    if fr.file_type == "dat":
        format_name = "Psi4 output file"
    elif fr.file_type == "out":
        format_name = "ORCA output file"

    if format_name == "Gaussian input file":
        a_or_an = "a"
    elif format_name == "Gaussian output file":
        a_or_an = "a"    
    elif format_name == "ORCA output file":
        a_or_an = "an"
    elif format_name == "Psi4 output file":
        a_or_an = "a"
    elif format_name == "XYZ file":
        a_or_an = "an"
    elif format_name == "FCHK file":
        a_or_an = "an"
        
    status = "Opened %s as %s %s %s" % (file_name, a_or_an, format_name, "movie" if coordsets else "")

    return [structure], status

def save_aarontools(session, path, format_name, **kwargs):
    """ 
    save XYZ file using AaronTools
    kwargs may be:
        comment - str
    """
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