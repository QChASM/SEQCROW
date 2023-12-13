"""
adds monitorBonds command to ChimeraX

the atoms will be checked for connectivity changes every time the coordinates change

example command usage: monitorBonds #1 guess true
to be added to seqcrow later
"""
from scipy.spatial import distance
import numpy as np

from chimerax.atomic import AtomicStructure, Atoms, AtomicStructuresArg
from chimerax.core.models import REMOVE_MODELS
from chimerax.core.commands import (
    FloatArg,
    ObjectsArg,
    BoolArg,
    CmdDesc,
    register,
)

from AaronTools.const import RADII, METAL

max_dist_arrays = {}
ts_dist_arrays = {}
tracked_atoms = {}
handlers = {}

def check_bonds(trigger_name, changes, tolerance, tsTolerance):
    """
    if the distance between two atoms is shorter than the sum of
    their covalent radii + tolerance, make sure a bond is drawn
    between them
    
    if the distance is longer, but still shorter than the sum
    of their covalent radii + tsTolerance, draw a TS bond
    """
    mdl, diff = changes
    if not diff.structure_reasons():
        return
    # squared distance between atoms
    D = distance.squareform(
        distance.pdist(
            mdl.coordset(mdl.active_coordset_id).xyzs[tracked_atoms[mdl], :],
            "sqeuclidean"
        )
    )
    try:
        max_connected_dist = max_dist_arrays[mdl]
        ts_connected_dist = ts_dist_arrays[mdl]
    except KeyError:
        # make an array for how far atoms can be and still be bonded
        # to each other
        max_connected_dist = np.zeros((len(tracked_atoms[mdl]), len(tracked_atoms[mdl])))
        ts_connected_dist = np.zeros((len(tracked_atoms[mdl]), len(tracked_atoms[mdl])))
        for i, ii in enumerate(tracked_atoms[mdl]):
            a1 = mdl.atoms[ii]
            for j, jj in enumerate(tracked_atoms[mdl][:i]):
                a2 = mdl.atoms[jj]
                max_connected_dist[i, j] = (
                    RADII[a1.element.name] +
                    RADII[a2.element.name] +
                    tolerance
                ) ** 2
                ts_connected_dist[i, j] = (
                    RADII[a1.element.name] +
                    RADII[a2.element.name] +
                    tsTolerance
                ) ** 2
        max_dist_arrays[mdl] = max_connected_dist
        ts_dist_arrays[mdl] = ts_connected_dist

    # these are bonded
    connected = np.tril(D < max_connected_dist)
    # these are not
    not_connected = np.tril(D > max_connected_dist)
    # almost bonded
    almost_connected = np.tril(np.logical_and(not_connected, D < ts_connected_dist))
    # way too long
    way_too_long = np.tril(D > ts_connected_dist)

    # add new bonds
    for (ndx1, ndx2) in zip(*connected.nonzero()):
        a1 = mdl.atoms[tracked_atoms[mdl][ndx1]]
        a2 = mdl.atoms[tracked_atoms[mdl][ndx2]]
        is_metal = False
        if (
            any(a1.element.name == ele for ele in METAL)
        ) or (
            any(a2.element.name == ele for ele in METAL)
        ):
            is_metal = True
        if not is_metal:
            try:
                b = mdl.new_bond(a1, a2)
                # set the bond radius to match other bonds
                radius = 0
                n_bonds = 0
                for bond in a1.bonds:
                    if bond is b:
                        continue
                    radius += bond.radius
                    n_bonds += 1
                if radius == 0:
                    b.radius = 0.16
                else:
                    b.radius = (radius / n_bonds)
            except TypeError:
                pass
        else:
            try:
                pbg = mdl.pseudobond_group(
                    mdl.PBG_METAL_COORDINATION,
                    create_type=1,
                )
            except TypeError:
                pbg = mdl.pseudobond_group(
                    mdl.PBG_METAL_COORDINATION,
                    create_type=2,
                )
            for pbond in pbg.pseudobonds:
                if a1 in pbond.atoms and a2 in pbond.atoms:
                    break
            else:
                pbg.new_pseudobond(a1, a2)

        ts_pbg = mdl.pseudobond_group(
            "TS bonds",
            create_type=0,
        )
        if ts_pbg is None:
            continue
        for pbond in ts_pbg.pseudobonds:
            if a1 in pbond.atoms and a2 in pbond.atoms:
                pbond.delete()
                break

    # delete bonds that are too long
    for (ndx1, ndx2) in zip(*not_connected.nonzero()):
        a1 = mdl.atoms[tracked_atoms[mdl][ndx1]]
        a2 = mdl.atoms[tracked_atoms[mdl][ndx2]]
        for bond in a1.bonds:
            if a2 in bond.atoms:
                bond.delete()
                break
        pbg = mdl.pseudobond_group(
            mdl.PBG_METAL_COORDINATION,
            create_type=0,
        )
        if pbg is None:
            continue
        for pbond in pbg.pseudobonds:
            if a1 in pbond.atoms and a2 in pbond.atoms:
                pbond.delete()
                break

    for (ndx1, ndx2) in zip(*almost_connected.nonzero()):
        a1 = mdl.atoms[tracked_atoms[mdl][ndx1]]
        a2 = mdl.atoms[tracked_atoms[mdl][ndx2]]
        ts_pbg = mdl.pseudobond_group(
            "TS bonds",
            create_type=1,
        )
        for pbond in ts_pbg.pseudobonds:
            if a1 in pbond.atoms and a2 in pbond.atoms:
                break
        else:
            ts_pbg.new_pseudobond(a1, a2)
        ts_pbg.dashes = 0
        ts_pbg.halfbond = False
        ts_pbg.color = [170, 255, 255, 128]
        ts_pbg.radius = 0.16
    
    for (ndx1, ndx2) in zip(*way_too_long.nonzero()):
        a1 = mdl.atoms[tracked_atoms[mdl][ndx1]]
        a2 = mdl.atoms[tracked_atoms[mdl][ndx2]]
        ts_pbg = mdl.pseudobond_group(
            "TS bonds",
            create_type=0,
        )
        if ts_pbg is None:
            break
        for pbond in ts_pbg.pseudobonds:
            if a1 in pbond.atoms and a2 in pbond.atoms:
                pbond.delete()
                break

def monitor_bonds(session, selection, tolerance=0.35, tsTolerance=0.6, guess=False):
    """
    check for bonding changes every time the coordinates change
    
    guess: determine which atoms to monitor based on whether their connectivity
        should is different between the first and later frame of the trajectory
    tolerance: add to covalent radii when determining connectivity
    tsTolerance: add to covalent radii to determine whether to draw a TS bond
    """
    for mdl in selection.models:
        if not isinstance(mdl, AtomicStructure):
            continue
        atoms = selection.atoms.intersect(mdl.atoms)
        remove_bond_monitor("command", [mdl])
        remove_monitor(session, [mdl])
        if guess:
            first_coords = mdl.coordset(mdl.coordset_ids[0]).xyzs
            last_coords = mdl.coordset(mdl.coordset_ids[-1]).xyzs
            bonds_changed = set()
            for i, a1 in enumerate(mdl.atoms):
                for j, a2 in enumerate(mdl.atoms[:i]):
                    expected_dist = (
                        RADII[a1.element.name] +
                        RADII[a2.element.name] +
                        tolerance
                    )
                    d0 = np.linalg.norm(first_coords[i] - first_coords[j])
                    d1 = np.linalg.norm(last_coords[i] - last_coords[j])
                    if (
                        d1 > expected_dist and d0 < expected_dist
                    ) or (
                        d1 < expected_dist and d0 > expected_dist
                    ):
                        bonds_changed.update((i, j))
            atoms = Atoms([atoms[b] for b in bonds_changed])
        ndx = [mdl.atoms.index(a) for a in atoms]
        tracked_atoms.setdefault(mdl, list())
        tracked_atoms[mdl].extend(ndx)
        hdlr = mdl.triggers.add_handler(
            "changes",
            lambda tn, changes, tolerance=tolerance, tsTolerance=tsTolerance: \
            check_bonds(tn, changes, tolerance, tsTolerance)
        )
        handlers[mdl] = hdlr

def remove_monitor(session, selection):
    """stop checking for bond changes"""
    for model in selection:
        try:
            hdlr = handlers[model]
            model.triggers.remove_handler(hdlr)
            del max_dist_arrays[model]
            del ts_dist_arrays[model]
            del tracked_atoms[model]
            del handlers[model]
        except KeyError:
            pass

monitor_bonds_description = CmdDesc(
    required=[("selection", ObjectsArg)],
    keyword=[
        ("tolerance", FloatArg),
        ("tsTolerance", FloatArg),
        ("guess", BoolArg),
    ],
    synopsis="show bonds breaking or forming during trajectory",
)

remove_monitor_description = CmdDesc(
    required=[("selection", AtomicStructuresArg)],
    synopsis="stop monitoring bond changes",
)

def remove_bond_monitor(trigger_name, models):
    for mdl in models:
        try:
            hdlr = handlers[mdl]
            del handlers[mdl]
            del max_dist_arrays[mdl]
            del ts_dist_arrays[mdl]
            del tracked_atoms[mdl]
            mdl.triggers.remove_handler(hdlr)
        except KeyError:
            pass
