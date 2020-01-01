def open_aarontools(session, path, format_name=None, trajectory=False):
    from AaronTools.fileIO import FileReader
    from AaronTools.geometry import Geometry
    from ChimAARON.residue_collection import ResidueCollection
        
    if format_name == "Gaussian input file":
        fmt = "com"
    elif format_name == "Gaussian output file":
        fmt = "log"
    elif format_name == "XYZ":
        fmt = "xyz"
    else:
        fmt = path.split('.')[-1]
            
    f = FileReader(path, just_geom=False, get_all=trajectory)

    geom = Geometry(f)

    structures = [ResidueCollection.get_chimera(session, geom, coordsets=trajectory, filereader=f)]

    #associate the AaronTools FileReader with each structure
    for res_coll in structures:
        res_coll.aarontools_filereader = f

    if trajectory:
        from chimerax.std_commands.coordset_gui import CoordinateSetSlider
        for structure in structures:
            CoordinateSetSlider(session, structure)

    status = "Opened %s as a %s %s" % (path, fmt, "trajectory" if trajectory else "file")

    return structures, status

def save_aarontools(session, path, format_name, models=None, atoms=None, skip_atoms=None):
    from ChimAARON.residue_collection import ResidueCollection
    from chimerax.atomic import AtomicStructure
    
    if models is None and atoms is None:
        models = session.models.list(type=AtomicStructure)
    elif models is None and atoms is not None:
        models = session.models.list(type=AtomicStructure)
        targets = [atom.atomspec for atom in atoms]
    elif models is None and skip_atoms is not None:
        models = session.models.list(type=AtomicStructure)
        skip_atoms = [atom.atomspec for atom in skip_atoms]
    elif not isinstance(models, AtomicStructure):
        raise NotImplementedError("models must be chimerax AtomicStructure")
    
    res_coll = ResidueCollection(models)
    
    res_coll.write(targets=atoms, ignore_atoms=skip_atoms, outfile=path)