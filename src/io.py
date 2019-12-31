def open_aarontools(session, path, format_name=None, trajectory=False):
    from AaronTools.fileIO import FileReader
    from AaronTools.geometry import Geometry
    from ChimAARON.residue_collection import ResidueCollection
    

    if trajectory:
        #load movie
        all_geom = True
        if format_name == "Gaussian output trajectory":
            fmt = "log"
        elif format_name == "XYZ trajectory":
            fmt = "xyz"
    else:
        #load structure
        all_geom = False
        if format_name == "Gaussian input file":
            fmt = "com"
        elif format_name == "Gaussian output file":
            fmt = "log"
        elif format_name == "XYZ":
            fmt = "xyz"
        else:
            fmt = path.split('.')[-1]
            
    with open(path, 'r') as x:
        f = FileReader((path, fmt, x), just_geom=False, get_all=all_geom)
    
    geom = Geometry(f)
    
    structures = [ResidueCollection.get_chimera(session, geom)]

    #associate the AaronTools FileReader with each structure
    for res_coll in structures:
        res_coll.aarontools_filereader = f

    status = "Opened file"

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