def open_aarontools(session, stream, file_name, format_name=None, coordsets=None):
    from AaronTools.fileIO import FileReader
    from AaronTools.theory.job_types import suggested_fix
    from AaronTools.utils.utils import get_filename
    from SEQCROW.residue_collection import ResidueCollection
    from SEQCROW.managers import ADD_FILEREADER
    from warnings import warn
    
    # from cProfile import Profile
    # profile = Profile()
    # profile.enable()

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
    elif format_name == "sqm output file":
        fmt = "sqmout"
    elif format_name == "Q-Chem output file":
        fmt = "qout"

    max_length = session.seqcrow_settings.settings.MAX_FCHK_ARRAY

    try:
        fr = FileReader(
            (file_name, fmt, stream),
            just_geom=False,
            get_all=True,
            max_length=max_length,
            log=session.logger,
        )
    except UnicodeDecodeError as e:
        session.logger.error("unable to open %s as a %s" % (file_name, format_name))
        raise e

    except Exception as e:
        session.logger.error("unable to open %s as a %s" % (file_name, format_name))
        raise e
    finally:
        if hasattr(stream, "close") and callable(stream.close):
            stream.close()

    try:
        session.logger.warning("error or warning in %s:\n %s" % (
            file_name, fr["error_msg"]
        ))
        fix = suggested_fix(fr["error"])
        if fix:
            session.logger.warning("possible hint: %s" % fix)
    except KeyError:
        pass

    try:
        freq = fr["frequency"]
        imag = [data.frequency for data in freq.data if data.frequency < 0]
        session.logger.info("%s has %i imaginary harmonic vibrational mode%s" % (
            file_name, len(imag), "" if len(imag) == 1 else "s"
        ))
        for freq in imag:
            session.logger.info("%.2f<i>i</i>" % -freq, is_html=True)
    except KeyError:
        pass

    if fr.file_type == "dat":
        format_name = "Psi4 output file"
    elif fr.file_type == "out":
        format_name = "ORCA output file"
    elif fr.file_type == "qout":
        format_name = "Q-Chem output file"

    if fr.file_type == "xyz" and fr.all_geom and not all(
        len(atoms[1]) == len(fr.atoms) for atoms in fr.all_geom
    ):
        geoms = []
        for struc in fr.all_geom:
            geoms.append(ResidueCollection(struc[1], refresh_ranks=False).copy(
                comment=struc[0], copy_atoms=True,
            ))
        geoms.append(ResidueCollection(fr.atoms, refresh_ranks=False).copy(
            comment=fr.comment, copy_atoms=True,
        ))
        structures = []
        for rescol in geoms:
            structures.append(rescol.get_chimera(session, coordsets=False))
            structures[-1].name = rescol.comment
        
        return structures, "opened multi-structure file"
    
    atoms = fr
    if hasattr(fr, "full_atoms"):
        atoms = fr.full_atoms
    try:
        geom = ResidueCollection(atoms, refresh_ranks=False).copy(
            comment=fr.comment, copy_atoms=True,
        )
    except Exception as e:
        s = "could not open %s" % file_name
        if "error" in fr.other and fr.other["error"]:
            s += "\n%s contains an error (%s):\n%s" % (format_name, fr.other["error"], fr.other["error_msg"])
        
        session.logger.error(s)
        session.logger.error(repr(e))
        return [], "SEQCROW failed to open %s" % file_name

    for frame in fr.all_geom:
        if len(frame["atoms"]) != len(fr["atoms"]):
            return split_open(session, file_name, format_name, fr)
    else:
        structure = geom.get_chimera(
            session,
            coordsets=bool(fr.all_geom),
            filereader=fr,
            apply_preset=False,
            
        )

    if fr.all_geom and "energy" in fr.other and coordsets is not False:
        try:
            from SEQCROW.tools.per_frame_plot import EnergyPlot
            nrg_plot = EnergyPlot(session, structure, fr)
            if not nrg_plot.opened:
                warn("energy plot could not be opened\n" + \
                    "there might be a mismatch between energy entries and structure entries in %s" % file_name)
                nrg_plot.delete()
        except Exception as e:
            session.logger.warning(repr(e))

    if coordsets:
        from chimerax.std_commands.coordset_gui import CoordinateSetSlider

        slider = CoordinateSetSlider(session, structure)

        if fr.all_geom:
            structure.active_coordset_id = structure.num_coordsets
            if coordsets:
                slider.set_slider(structure.num_coordsets)

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
    elif format_name == "sqm output file":
        a_or_an = "an"
    elif format_name == "Q-Chem output file":
        a_or_an = "a"

    status = "Opened %s as %s %s %s" % (file_name, a_or_an, format_name, "movie" if coordsets else "")

    structure.name = get_filename(file_name, include_parent_dir=False)
    structure.filename = file_name

    # profile.disable()
    # profile.print_stats()

    return [structure], status


def split_open(session, file_name, format_name, filereader):
    from AaronTools.utils.utils import get_filename
    from SEQCROW.residue_collection import ResidueCollection

    structures = []
    for frame in filereader.all_geom:
        geom = ResidueCollection(frame["atoms"], refresh_ranks=False).copy(
            comment=None, copy_atoms=True,
        )
        structure = geom.get_chimera(
            session,
            coordsets=False,
            filereader=frame["data"],
            apply_preset=False,
            
        )
        structures.append(structure)

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
    elif format_name == "sqm output file":
        a_or_an = "an"
    elif format_name == "Q-Chem output file":
        a_or_an = "a"

    status = "Opened  %s as %s %s multi-structure file" % (file_name, a_or_an, format_name)

    for structure in structures:
        name = get_filename(file_name, include_parent_dir=False)
        structure.name = name
        structure.filereaders[-1]["name"] = name
        structure.filename = file_name

    # profile.disable()
    # profile.print_stats()

    return structures, status

def get_structure(session, elements, coordinates, name, comment, bonded_threshold=0.3):
    from chimerax.atomic import AtomicStructure, Element, Atoms
    from chimerax.atomic import Residue
    import numpy as np
    from AaronTools.const import RADII, TMETAL, ELEMENTS

    struc = AtomicStructure(session)
    struc.name = name
    struc.comment = comment
    struc.filereaders = [{
        "name": name,
        "comment": comment,
    }]
    res = struc.new_residue("UNK", "a", 1)
    ele_counts = dict()
    if all(x.isdigit() for x in elements):
        elements = np.vectorize(lambda x: ELEMENTS[int(x)] if int(x) > 0 and int(x) < len(ELEMENTS) else "X")(elements)
    radii = np.vectorize(lambda x: RADII.get(x, 0))(elements)
    for i, ele, coord in zip(range(0, len(elements)), elements, coordinates):
        try:
            ele = ELEMENTS[int(ele)]
        except ValueError:
            pass
        except IndexError:
            raise RuntimeError(
                "error while trying to convert atomic number to symbol: %s" % ele
            )
        dist = np.zeros(i)
        max_connected_dist = np.zeros(i)
        ele_counts.setdefault(ele, 0)
        ele_counts[ele] += 1
        name = "%s%i" % (ele, ele_counts[ele])
        atom = struc.new_atom(name, ele)
        atom.coord = coord
        atom.serial_number = i + 1
        res.add_atom(atom)
        if i == 0:
            continue
        max_connected_dist = (radii[i] + radii[:i] + bonded_threshold) ** 2
        dist = np.sum((coordinates[:i] - coord) ** 2, axis=1)

        connected = (dist < max_connected_dist).nonzero()[0]
        for ndx in connected:
            if ele in TMETAL or elements[ndx] in TMETAL:
                pbg = struc.pseudobond_group(
                    struc.PBG_METAL_COORDINATION,
                    create_type=1
                )
                pbg.new_pseudobond(
                    atom, struc.atoms[ndx]
                )
                continue
            bond = struc.new_bond(
                atom, struc.atoms[ndx]
            )
    return struc


def open_xyz(session, stream, file_name, coordsets=None, maxModels=None):
    """
    open XYZ files
    """
    import os
    import re
    import numpy as np
    from SEQCROW.managers import ADD_FILEREADER
    from AaronTools.utils import utils
    
    # from cProfile import Profile
    # profile = Profile()
    # profile.enable() filereaders

    if file_name.lower().endswith(".allxyz") and coordsets is None:
        coordsets = True

    try:
        all_coordsets = []
        ele_sets = []
        line = stream.readline()
        structures = []
        comments = []
        fr = {}
        fr["name"] = file_name
        fr["all_geom"] = None
        fr["other"] = dict()
        comment = ""
        while line.strip():
            try:
                if line.strip() == ">":
                    line = stream.readline()
                n_atoms = int(line)
            except ValueError:
                try:
                    error_msg = get_error_msg(
                        file_name,
                        ele_sets,
                        all_coordsets,
                        eles,
                        comments,
                        n_atoms,
                        comment,
                        coord_data,
                    )
                except UnboundLocalError:
                    error_msg = "no data read"
                error_msg += "\nlast line read:\n"
                error_msg += line
                error_msg += "\n expected number of atoms here"
                session.logger.error(error_msg)
                return
            comment = stream.readline().strip()
            comments.append(comment)
            coords = np.zeros((n_atoms, 3))
            coord_data = ""
            eles = []
            for i in range(0, n_atoms):
                line = stream.readline()
                info = line.split(maxsplit=1)
                try:
                    eles.append(info[0])
                except IndexError:
                    coord_data += line
                    error_msg = get_error_msg(
                        file_name,
                        ele_sets,
                        all_coordsets,
                        eles,
                        comments,
                        n_atoms,
                        comment,
                        coord_data,
                    )
                    error_msg += "\nlast line read:\n"
                    error_msg += line
                    error_msg += "\n expected element symbol/number and coordinates here"
                    raise RuntimeError(error_msg)
                try:
                    coord_data += "%s %s %s\n" % tuple(info[1].split()[:3])
                except IndexError:
                    coord_data += line
                    error_msg = get_error_msg(
                        file_name,
                        ele_sets,
                        all_coordsets,
                        eles,
                        comments,
                        n_atoms,
                        comment,
                        coord_data,
                    )
                    error_msg += "\nlast line read:\n"
                    error_msg += line
                    error_msg += "\n expected atom data here"
                    raise RuntimeError(error_msg)
            line = stream.readline()
            coords = np.reshape(
                np.fromstring(coord_data, count=3 * n_atoms, sep=" "),
                (n_atoms, 3),
            )
            all_coordsets.append(coords)
            ele_sets.append(eles)
            if maxModels is not None:
                struc = get_structure(session, eles, coords, comment, comment)
                structures.append(struc)
                if len(structures) == maxModels:
                    break
        
        fr["comment"] = comment
    except Exception as e:
        stream.close()
        raise e

    stream.close()
    
    if not all_coordsets or not ele_sets:
        session.logger.error(
            "no structures found in %s\nlast line read:\n%s" % 
            (file_name, line)
        )
        return [], "failed"
    
    if maxModels is not None:
        return structures, "opened %i structures from %s" % (len(structures), file_name)
    
    if not all(len(ele_set) == len(ele_sets[0]) for ele_set in ele_sets):
        structures = [
            get_structure(session, eles, coords, name, name) for (eles, coords, name) in
            zip(ele_sets, all_coordsets, comments)
        ]
        for struc in structures:
            struc.filename = file_name
        return structures, "opened %i structures from %s" % (len(structures), file_name)
    
    name, ext = os.path.splitext(file_name)
    struc = get_structure(session, ele_sets[-1], all_coordsets[-1], name, comment)
    all_coordsets = np.array(all_coordsets)
    struc.add_coordsets(np.array(all_coordsets), replace=True)
    status = "opened %s as an XYZ coordinate file" % file_name
    struc.active_coordset_id = struc.num_coordsets
    struc.filereaders[0]["all_geom"] = None
    if len(all_coordsets) > 1:
        fr["all_geom"] = all_coordsets
        struc.filereaders[0]["all_geom"] = fr["all_geom"]
        if (
            "multiframe .xyz" in session.seqcrow_settings.settings.XYZ_OPEN
            and coordsets is None
        ):
            coordsets = True
        if coordsets:
            from chimerax.std_commands.coordset_gui import CoordinateSetSlider
            status += " movie"
            slider = CoordinateSetSlider(session, struc)
            slider.set_slider(struc.num_coordsets)
        data = []
        for comment in comments:
            value = re.search("-?\d+(?:(?:\.\d+)|(?:[Ee]-?\d+))", comment)
            if value:
                data.append(float(value.group(0)))
            else:
                break
        else:
            try:
                from SEQCROW.tools.per_frame_plot import EnergyPlot
                nrg_plot = EnergyPlot(
                    session,
                    struc,
                    fr,
                    ylabel="comment value",
                    y_data=data,
                )
                if not nrg_plot.opened:
                    nrg_plot.delete()
                else:
                    struc.filereaders[0]["y_data"] = data
            except Exception as e:
                session.logger.warning(repr(e))

    struc.filename = file_name
    
    # profile.disable()
    # profile.print_stats()
    
    return [struc], status


def get_error_msg(
    file_name,
    ele_sets,
    coordsets,
    eles,
    comments,
    n_atoms,
    comment,
    coord_data
):
    error_msg = "could not parse coordinates while reading %s\n" % file_name
    if len(coordsets) > 0:
        error_msg += "last structure read:\n"
        error_msg += "%i\n%s\n" % (
            len(coordsets[-1]), comments[-1],
        )
        for ele, coord in zip(ele_sets[-1], coordsets[-1]):
            error_msg += "%-2s     %11.5f   %11.5f   %11.5f\n" % (
                ele, *coord,
            )
    error_msg += "error occured while reading structure %i:\n" % (
        len(coordsets) + 1
    )
    error_msg += "%i\n%s\n" % (n_atoms, comment)
    error_msg += "\n".join(
        ["%-2s   %s" % (ele, coord) for ele, coord in zip(
            eles, coord_data.splitlines(),
        )]
    )
    
    return error_msg


def open_nbo(session, path, file_name, format_name=None, orbitals=None):
    import os.path
    
    from AaronTools.fileIO import FileReader
    from SEQCROW.residue_collection import ResidueCollection
    from SEQCROW.managers import ADD_FILEREADER

    # print(file_name)

    if orbitals == "browse":
        if not session.ui.is_gui:
            raise RuntimeError("cannot browse for orbital file without gui")
        
        from Qt.QtWidgets import QFileDialog
        
        # print(os.path.dirname(path))
        
        orbitals, _ = QFileDialog.getOpenFileName(
            caption="NBO orbital file",
            directory=os.path.dirname(path),
            filter="NBO coefficient files (*.32 *.33 *.34 *.35 *.36 *.37 *.38 *.39 *.40 *.41);;"
            "PNAO file (*.32);;"
            "NAO file (*.33);;"
            "PNHO file (*.34);;"
            "NHO file(*.35);;"
            "PNBO file (*.36);;"
            "NBO file (*.37);;"
            "PNLMO file (*.38);;"
            "NLMO file (*.39);;"
            "MO file (*.40);;"
            "NO file (*.41)"
        )
        if not orbitals:
            orbitals = None
    
    if format_name == "NBO input file":
        fmt = "47"
    elif format_name == "NBO output file":
        fmt = "31"
    
    # print(orbitals)

    fr = FileReader((path, fmt, None), nbo_name=orbitals)

    try:
        geom = ResidueCollection(fr, refresh_ranks=False).copy(comment=fr.comment, copy_atoms=True)
    except Exception as e:
        s = "could not open %s" % file_name
        if "error" in fr.other and fr.other["error"]:
            s += "\n%s contains an error (%s):\n%s" % (format_name, fr.other["error"], fr.other["error_msg"])
        
        session.logger.error(s)
        session.logger.error(repr(e))
        return [], "SEQCROW failed to open %s" % file_name

    structure = geom.get_chimera(session, filereader=fr)
    #associate the AaronTools FileReader with each structure

    status = "Opened %s as an %s" % (file_name, format_name)

    structure.filename = file_name

    return [structure], status


def save_xyz(session, path, **kwargs):
    """ 
    save XYZ file
    kwargs may be:
        comment - str
    """
    from chimerax.atomic import AtomicStructure
    
    accepted_kwargs = ['comment', 'models', 'coordsets']
    unknown_kwargs = [kw for kw in kwargs if kw not in accepted_kwargs]
    if len(unknown_kwargs) > 0:
        raise RuntimeWarning("unrecognized keyword%s %s?" % ("s" if len(unknown_kwargs) > 1 else "", ", ".join(unknown_kwargs)))
    
    if 'models' in kwargs:
        models = kwargs['models']
    else:
        models = None
        
    if 'coordsets' in kwargs:
        coordsets = kwargs['coordsets']
    else:
        coordsets = False
        
    if 'append' in kwargs:
        append = kwargs['append']
        if append:
            mode = "a"
        else:
            mode = "w"
    else:
        mode = "w"

    if 'comment' in kwargs:
        comment = kwargs['comment']
    else:
        comment = ""
    
    if models is None:
        models = session.models.list(type=AtomicStructure)

    models = [m for m in models if isinstance(m, AtomicStructure)]
    
    if len(models) < 1:
        raise RuntimeError('nothing to save')
        
    for model in models:
        with open(path, mode) as f:
            if coordsets:
                for cs in model.coordset_ids:
                    f.write("%i\n%s\n" % (model.num_atoms, comment if comment else model.name))
                    coords = model.coordset(cs).xyzs
                    for atom, xyz in zip(model.atoms, coords):
                        f.write("%2s    %9.5f    %9.5f     %9.5f\n" % (
                            atom.element.name, *xyz
                        ))
            else:
                f.write("%i\n%s\n" % (model.num_atoms, comment if comment else model.name))
                for atom in model.atoms:
                    f.write(
                        "%2s    %9.5f    %9.5f     %9.5f\n" % (
                            atom.element.name, *atom.coord
                        )
                    )