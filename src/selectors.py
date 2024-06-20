import numpy as np

from chimerax.atomic import AtomicStructure, Atoms, selected_atoms, selected_bonds
from chimerax.core.commands import register_selector

from AaronTools.atoms import BondOrder
from AaronTools.finders import ChiralCenters, VSEPR, Bridgehead, SpiroCenters
from AaronTools.geometry import Geometry
from AaronTools.substituent import Substituent
from AaronTools.const import TMETAL
from AaronTools.utils.prime_numbers import Primes
from AaronTools.utils.utils import shortest_path

from SEQCROW.residue_collection import ResidueCollection

from collections import deque

from warnings import warn

Primes()
BondOrder()

def register_selectors(logger, name):
    if name == "tm":
        register_selector("tm", tm_selector, logger, desc="transition metals")

    elif name == "rings":
        register_selector(
            name,
            select_rings,
            logger,
            desc="select atoms in rings",
        )

    elif any(name == sub for sub in Substituent.list()):
        register_selector(
            name, 
            lambda sess, models, results, sub_name=name: substituent_selection(
                sess,
                sub_name,
                models,
                results
            ),
            logger,
            desc="substituent %s" % name
        )
    
    elif name == "connected":
        register_selector("connected", all_connected_selector, logger, desc="fragment connected to selected atoms")
    
    elif any(name == vsepr for vsepr in [
        "t-shaped",
        "trigonal-planar",
        "tetrahedral",
        "sawhorse",
        "seesaw",
        "square-planar",
        "trigonal-pyramidal",
        "trigonal-bipyramidal",
        "square-pyramidal",
        "pentagonal",
        "octahedral",
        "hexagonal",
        "trigonal-prismatic",
        "pentagonal-pyramidal",
        "capped-octahedral",
        "capped-trigonal-prismatic",
        "heptagonal",
        "hexagonal-pyramidal",
        "pentagonal-bipyramidal",
        "biaugmented-trigonal-prismatic",
        "cubic",
        "elongated-trigonal-bipyramidal",
        "hexagonal-bipyramidal",
        "heptagonal-pyramidal",
        "octagonal",
        "square-antiprismatic",
        "trigonal-dodecahedral",
        "capped-cube",
        "capped-square-antiprismatic",
        "enneagonal",
        "heptagonal-bipyramidal",
        "hula-hoop",
        "triangular-cupola",
        "tridiminished-icosahedral",
        "muffin",
        "octagonal-pyramidal",
        "tricapped-trigonal-prismatic",
    ]):
        new_name = name
        if name != "hula-hoop":
            new_name = name.replace("-", " ")
        register_selector(
            name, 
            lambda sess, models, results, vsepr_name=new_name: vsepr_selection(
                sess,
                vsepr_name,
                models,
                results
            ),
            logger,
            desc="%s shape" % name
        )
    
    elif any(name == vsepr for vsepr in [
        "linear",
        "bent",
        "planar",
    ]):
        name_map = {
            "linear": ["linear 1", "linear 2"],
            "bent": [
                "bent 2 planar",
                "bent 2 tetrahedral",
                "bent 3 tetrahedral",
            ],
            "planar": [
                "trigonal planar",
                "square planar",
            ],
        }
        finders = name_map[name]
        register_selector(
            name, 
            lambda sess, models, results, vsepr_name=finders: vsepr_selection(
                sess,
                vsepr_name,
                models,
                results
            ),
            logger,
            desc="%s shape" % name
        )

    elif name == "bridgehead":
        register_selector(
            name, 
            lambda sess, models, results, finder=Bridgehead(): finder_selection(
                sess,
                finder,
                models,
                results
            ),
            logger,
            desc="%s atoms" % name.replace("-", " ")
        )

    elif name == "spiro-centers":
        register_selector(
            name, 
            lambda sess, models, results, finder=SpiroCenters(): finder_selection(
                sess,
                finder,
                models,
                results
            ),
            logger,
            desc="%s" % name.replace("-", " ")
        )

    elif name == "chiral-centers":
        register_selector(
            name, 
            lambda sess, models, results, finder=ChiralCenters(): finder_selection(
                sess,
                finder,
                models,
                results
            ),
            logger,
            desc="%s" % name.replace("-", " ")
        )

    elif any(name == solvent for solvent in ResidueCollection.list_solvents()):
        register_selector(
            name,
            lambda sess, models, results, solvent_name=name: solvent_selection(
                sess,
                solvent_name,
                models,
                results
            ),
            logger,
            desc="solvent %s" % name
        )

def tm_selector(session, models, results):
    """select transition metals using AaronTools' TMETAL dictionary"""
        
    atoms = []
    for model in models:
        if isinstance(model, AtomicStructure):
            for atom in model.atoms:
                if atom.element.name in TMETAL:
                    atoms.append(atom)
    
    #need to add a Collection, not just a list of atoms
    results.add_atoms(Atoms(atoms))

def vsepr_selection(session, vsepr_name, models, results):
    atoms = []
    if isinstance(vsepr_name, str):
        finders = VSEPR(vsepr_name)
    else:
        finders = [VSEPR(name) for name in vsepr_name]
    
    for model in models:
        if isinstance(model, AtomicStructure):
            rescol = ResidueCollection(model)
            try:
                rescol_atoms = rescol.find(finders)
                atoms.extend([atom.chix_atom for atom in rescol_atoms])
            except LookupError:
                continue
    
    #need to add a Collection, not just a list of atoms
    results.add_atoms(Atoms(atoms))

def finder_selection(self, finder, models, results):
    atoms = []
    
    for model in models:
        if isinstance(model, AtomicStructure):
            rescol = ResidueCollection(
                model, refresh_ranks=False,
            )
            try:
                rescol_atoms = rescol.find(finder)
                atoms.extend([atom.chix_atom for atom in rescol_atoms])
            except LookupError:
                continue
    
    #need to add a Collection, not just a list of atoms
    results.add_atoms(Atoms(atoms))

#reimplemented some AaronTools but with chimerax stuff because of 
#performace reasons
def substituent_selection(session, sub_name, models, results): 
    #TODO: optimize - or cheat and use cython or something
    #TODO: make it so it doesn't select things with just an H bonded to them
    #      e.g. sel OH should not select water molecules
    #      probably do a get_all_connected for each fragment and
    #      check if all_connected.subtract(Atoms[atom]).subtract(frag) leave just an H
    atoms = Atoms()
    
    sub = Substituent(sub_name)
    chix_sub = ResidueCollection(sub).get_chimera(session)
    sub_elements = sorted(chix_sub.atoms.elements.names)
    sub_ranks = canonical_rank(Atoms(chix_sub.atoms))
    sorted_sub_atoms = [x for _, x in sorted(zip(sub_ranks, chix_sub.atoms), key = lambda pair: pair[0])]
    
    length = len(sub.atoms)

    #rank_time = 0
    #frag_time = 0
    
    for model in models:
        if isinstance(model, AtomicStructure):
            for atom in model.atoms:
                #session.logger.info("checking groups on %s" % atom.atomspec)
                for bonded_atom in atom.neighbors:
                    if bonded_atom.element.name != sub.atoms[0].element:
                        continue
                    #session.logger.info("fragment for %s" % bonded_atom.atomspec)
                    #frag_start = perf_counter()
                    frag = get_fragment(bonded_atom, atom, length)
                    #frag_stop = perf_counter()
                    #frag_time += frag_stop - frag_start
                    
                    if frag.intersects(atoms):
                        continue
                    
                    frag = frag.subtract(Atoms([atom]))

                    if len(frag) != length:
                        continue

                    elements = sorted(frag.elements.names)
                    
                    if sub_elements != elements:
                        #session.logger.info("wrong elements")
                        continue

                    #rank_start = perf_counter()
                    frag_ranks = canonical_rank(frag)
                    #rank_stop = perf_counter()
                    #rank_time += rank_stop - rank_start
                    
                    #session.logger.warning(", ".join(sub_elements))
                    #session.logger.warning("%s;\n%s" % (", ".join(str(x) for x in sorted(frag_ranks)), ", ".join(str(x) for x in sorted(sub_ranks))))
                    
                    sorted_frag_atoms = [x for _, x in sorted(zip(frag_ranks, frag.instances()), key = lambda pair: pair[0])]
                    #session.logger.warning("%s;\n%s" % (", ".join(x.atomspec for x in sorted_frag_atoms), ", ".join(x.name for x in sorted_sub_atoms)))
                    for a, b in zip(sorted_frag_atoms, sorted_sub_atoms):
                        #session.logger.info("%s %s" % (a.atomspec, b.name))
                        if a.element.name != b.element.name:
                            #session.logger.info("different elements")
                            break

                        #session.logger.info("bonded: %s; other: %s" % (bonded_atom.atomspec, atom.atomspec))

                        if a is not bonded_atom and len(a.neighbors) != len(b.neighbors):
                            #session.logger.info("different num neighbors")
                            #session.logger.info("%s and %s" % (a.atomspec, b.name))
                            #session.logger.info("%i vs %i" % (len(a.neighbors), len(b.neighbors)))
                            break
                        elif a is bonded_atom and (len(a.neighbors) - 1) != len(b.neighbors):
                            #session.logger.info("first atom, different num neighbors")
                            #session.logger.info("%s and %s" % (a.atomspec, b.name))
                            #session.logger.info("%i vs %i" % (len(a.neighbors) - 1, len(b.neighbors)))
                            break
                            
                        failed = False
                        for i, j, k in zip(
                            sorted([aa.element.name for aa in a.neighbors if ((aa is not atom and a is bonded_atom) or a is not bonded_atom)]), 
                            sorted([bb.element.name for bb in b.neighbors]), 
                            sorted([aa for aa in a.neighbors if ((aa is not atom and a is bonded_atom) or a is not bonded_atom)]), 
                        ):
                            if i != j:
                                #session.logger.info("failed %s %s, %s" % (i, j, k.atomspec))
                                failed = True
                                break
                            
                        if failed:
                            break
                    
                    else:
                        atoms = atoms.merge(frag)
    
    #session.logger.info("spent %f time fragmenting" % frag_time)
    #session.logger.info("spent %f time ranking atoms" % rank_time)
    results.add_atoms(atoms)

def all_connected_selector(session, models, results):
    """select all atoms connected to the current selection"""
    # TODO: right mouse mode for this
    cur_sel = selected_atoms(session)
    bond_sel = selected_bonds(session)
    for bond in bond_sel:
        cur_sel = cur_sel.merge(Atoms(bond.atoms))
    atoms = Atoms()
    for atom in cur_sel:
        if atom in atoms:
            continue
        elif atom.structure not in models:
            continue
        connected_atoms = get_fragment(atom, max_len=len(atom.structure.atoms))
        atoms = atoms.merge(connected_atoms)

    results.add_atoms(atoms)

def select_rings(session, models, results):
    """
    select atoms in rings
    does not check the size of the ring
    """
    # from cProfile import Profile
    # profile = Profile()
    # profile.enable()
    
    for model in models:
        if not isinstance(model, AtomicStructure):
            continue
        
        ring_atoms = set()

        # index map to quickly get indices of atoms
        ndx = {a: i for i, a in enumerate(model.atoms)}
        # we use a connectivity path to look for rings
        graph = [[ndx[n] for n in a.neighbors] for a in ndx]
        # remove nodes that only have 1 neighbor, as it is not
        # possible for these to be in a ring
        prune_branches(graph)

        # for each atom, we look for a path from one of its neighbors
        # to another that does not include the atom itself
        # if we can find such a path, the atom is in a ring
        for a in range(0, len(graph)):
            # skip atoms with no valid neighbors
            if not graph[a]:
                continue
            
            # skip atoms we've already found
            if a in ring_atoms:
                continue
            
            found_ring = False
            # look for a path to each pair of neighbors
            for a2 in graph[a]:
                if found_ring and a2 in ring_atoms:
                    continue
                # copy the graph, but remove the node for this atom
                graph[a].remove(a2)
                path = shortest_path(graph, a, a2)
                if path is not None:
                    ring_atoms.update(path)
                    found_ring = True
                    graph[a].append(a2)
                else:
                    # this pair of atoms is not in a ring
                    # we will not need to revisit
                    graph[a2].remove(a)
            
            # if this atom is not in a ring, we will not
            # need to visit it again - remove it's connections
            # from the graph
            if not found_ring:
                for a2 in graph[a]:
                    graph[a2].remove(a)
                graph[a] = []
                prune_branches(graph)
        
        results.add_atoms(Atoms([model.atoms[i] for i in ring_atoms]))

    # profile.disable()
    # profile.print_stats()

def solvent_selection(session, solvent_name, models, results):
    # from time import perf_counter
    # frag_time = 0
    # rank_time = 0
    
    atoms = Atoms()

    solvent = ResidueCollection(Geometry.get_solvent(solvent_name))
    chix_solvent = solvent.get_chimera(session)
    solv_elements = sorted(chix_solvent.atoms.elements.names)
    solv_ranks = canonical_rank(Atoms(chix_solvent.atoms), break_ties=False)
    # print(solv_ranks)
    sorted_solv_atoms = [x for _, x in sorted(zip(solv_ranks, chix_solvent.atoms), key = lambda pair: pair[0])]
    length = len(solvent.atoms)
    # print(length)
    # print(solv_elements)

    for mdl in models:
        if not isinstance(mdl, AtomicStructure):
            continue
        # frag_start = perf_counter()
        
        mdl_atoms = Atoms(mdl.atoms)
        new_frag = True
        fragments = []
        frag_ranks = dict()
        while new_frag:
            new_frag = False
            for i, atom in enumerate(mdl_atoms):
                frag = get_fragment(atom)
                new_frag = True
                mdl_atoms = mdl_atoms.subtract(frag)
                if len(frag) == length:
                    fragments.append(frag)
                break
        
        # frag_stop = perf_counter()
        # frag_time += frag_stop - frag_start
        
        # print(fragments)
        # print(len(fragments))
        
        for frag in fragments:
            # print(len(frag))
            frag_elements = sorted(frag.elements.names)
            # print(frag_elements)
            if not all([solv_elements[i] == frag_elements[i] for i in range(0, length)]):
                continue
            
            # rank_start = perf_counter()
            ranks = canonical_rank(frag, break_ties=False)
            # rank_stop = perf_counter()
            # rank_time += rank_stop - rank_start
            sorted_frag_atoms = [x for _, x in sorted(zip(ranks, frag.instances()), key=lambda pair: pair[0])]
            # print(ranks)
            # print(sorted_solv_atoms)
            # print(sorted_frag_atoms)
            for a, b in zip(sorted_solv_atoms, sorted_frag_atoms):
                if a.element.name != b.element.name:
                    # print("element", a.element.name, b.element.name)
                    break
                
                if len(a.neighbors) != len(b.neighbors):
                    # print("num neighbors", len(a.neighbors), len(b.neighbors))
                    break
                
                failed = False
                for j, k in zip(
                    sorted([aa.element.name for aa in a.neighbors]),
                    sorted([bb.element.name for bb in b.neighbors]),
                ):
                    if j != k:
                        # print("neighbor element", j, k)
                        failed = True
                        break
                if failed:
                    break
            else:
                # print("selecting frag")
                atoms = atoms.merge(frag)

    # session.logger.info("spent %f time fragmenting" % frag_time)
    # session.logger.info("spent %f time ranking atoms" % rank_time)
    results.add_atoms(atoms)

def get_fragment(start, stop=None, max_len=None):
    """
    see AaronTools.geometry.Geometry.get_fragment
    """

    if max_len is None:
        max_len = start.structure.num_atoms

    stack = deque([start])
    frag = deque([start])
    if stop is not None:
        stop = set([stop])
        while len(stack) > 0 and len(frag) <= max_len:
            connected = stack.popleft()
            connected = set(connected.neighbors) - stop - set(frag)
            stack.extend(connected)
            frag.extend(connected)

    else:
        while len(stack) > 0 and len(frag) <= max_len:
            connected = stack.popleft()
            connected = set(connected.neighbors) - set(frag)
            stack.extend(connected)
            frag.extend(connected)

    return Atoms(frag)

def get_invariant(atom, atoms):
    """
    gets initial invariant based on self's element and the element of 
    the atoms connected to self
    same as AaronTools.Atom.get_neighbor_id
    """
    # atomic number
    z = atom.element.number
    s = "%03i" % z
    #atom is chimerax atom
    heavy = [x.element.number for x in atom.neighbors if x.element.name != "H" and x in atoms]
    # number of non-hydrogen connections:
    s += "%02i" % len(heavy)
    # number of bonds with heavy atoms
    for h in sorted(set(heavy)):
        s += "%03i" % h
        s += "%02i" % heavy.count(h)
    # number of connected hydrogens
    nH = len([x for x in atom.neighbors if x in atoms]) - len(heavy)
    s += "%02i" % nH
    
    return s

def canonical_rank(structure, heavy_only=False, break_ties=True):
    """
    see AaronTools.geometry.Geometry.canonical_rank
    structure is Atoms collection
    """
    primes = Primes.list(len(structure.instances()))
    atoms = []
    indices = dict()
    atoms_set = set()
    ranks = []

    def neighbors_rank(ranks):
        # partitions key is product of rank and neighbors' rank
        # use prime numbers for product so products are distinct
        # eg: primes[2]*primes[2] != primes[1]*primes[4]
        partitions = {}
        for i, a in enumerate(atoms):
            key = primes[ranks[i]]
            for b in atoms_set.intersection(a.neighbors):
                key *= primes[ranks[indices[b]]]
            partitions.setdefault(ranks[i], {})
            partitions[ranks[i]].setdefault(key, [])
            partitions[ranks[i]][key] += [i]

        return update_ranks(ranks, partitions)

    def update_ranks(ranks, partitions):
        new_ranks = ranks.copy()
        for rank, key_dict in partitions.items():
            if len(key_dict) == 1:
                continue
            for key in sorted(key_dict.keys()):
                for idx in key_dict[key]:
                    new_ranks[idx] = rank
                rank += len(key_dict[key])
        return new_ranks

    def tie_break(ranks):
        """
        Uses atom angles around COM -> shared_atom axis to break ties[
        Does not break symmetry (eg: pentane carbons still [0, 2, 4, 2, 0]
        because C2 and C4 are ~180 deg apart relative to COM-C5 axis)
        """

        def get_angle(vi, vj, norm):
            dot = np.dot(vi, vj)
            cross = np.cross(vi, vj)
            det = np.dot(norm, cross)
            rv = np.arctan2(det, dot)
            return round(rv, 1)

        partitions = {}
        for i, rank in enumerate(ranks):
            partitions.setdefault(rank, {})
            partitions[rank].setdefault(rank, [])
            partitions[rank][rank] += [i]

        new_partitions = partitions.copy()
        for rank, rank_dict in partitions.items():
            idx_list = rank_dict[rank]
            if len(idx_list) == 1:
                continue
            # split ties into groups connected to same atom
            groups = {}
            for i in idx_list[:-1]:
                a = atoms[i]
                for j in idx_list[1:]:
                    b = atoms[j]
                    connected = [x for x in a.neighbors if x in b.neighbors]
                    #connected = sorted(connected, key=lambda x, atoms=atoms: get_invariant(x, atoms))
                    if len(connected) == 1:
                        k = connected.pop()
                        if k in atoms:
                            k = indices[k]
                        else:
                            continue
                        groups.setdefault(k, set([i]))
                        groups[k] |= set([j])
            # atoms in each group sorted in counter clockwise order
            # around axis between shared atom and COM
            for shared_idx, connected in groups.items():
                shared = atoms[shared_idx]
                connected = sorted(connected)
                center = np.mean(structure.coords, axis=0)
                norm = shared.coord - center
                start_idx = None
                min_dist = None
                for c in connected:
                    this = np.linalg.norm(atoms[c].coord - center)
                    if min_dist is None or this < min_dist:
                        min_dist = this
                        start_idx = c
                start = atoms[start_idx].coord - shared.coord
                angles = {0: [start_idx]}
                for c in connected:
                    if c == start_idx:
                        continue
                    this = atoms[c].coord - shared.coord
                    angle = get_angle(start, this, norm)
                    angles.setdefault(angle, [])
                    angles[angle] += [c]
                for i, angle in enumerate(sorted(angles.keys())):
                    new_partitions[rank].setdefault(rank + i, [])
                    new_partitions[rank][rank + i] += angles[angle]
                    for idx in angles[angle]:
                        new_partitions[rank][rank].remove(idx)
                break
        return update_ranks(ranks, new_partitions)

    # rank all atoms the same initially
    c = 0
    for a in structure:
        if heavy_only and a.element.name == "H":
            continue
        atoms += [a]
        ranks += [0]
        indices[a] = c
        c += 1
    atoms_set = set(atoms)

    # partition and re-rank using invariants
    partitions = {}
    for i, a in enumerate(atoms):
        invariant = get_invariant(a, atoms)
        partitions.setdefault(invariant, [])
        partitions[invariant] += [i]
    new_rank = 0
    for key in sorted(partitions.keys(), key=int):
        idx_list = partitions[key]
        for idx in idx_list:
            ranks[idx] = new_rank
        new_rank += len(idx_list)

    # re-rank using neighbors until no change
    for i in range(0, len(ranks)):
        new_ranks = neighbors_rank(ranks)
        if ranks == new_ranks:
            break
        ranks = new_ranks
    else:
        warn("Max cycles reached in canonical sorting (neighbor-ranks)")

    # break ties using spatial positions
    # AND update neighbors until no change
    if break_ties:
        for i in range(0, len(ranks)):
            new_ranks = tie_break(ranks)
            new_ranks = neighbors_rank(new_ranks)
            if ranks == new_ranks:
                break
            ranks = new_ranks
        else:
            warn("Max cycles reached in canonical sorting (tie-breaking)")

    return ranks
    
def prune_branches(graph):
    trimmed_leaves = True
    while trimmed_leaves:
        trimmed_leaves = False
        for i in range(0, len(graph)):
            if len(graph[i]) == 1:
                graph[graph[i][0]].remove(i)
                graph[i] = []
                trimmed_leaves = True

    