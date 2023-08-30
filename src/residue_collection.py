import numpy as np

import re

from AaronTools.atoms import Atom as AaronToolsAtom
from AaronTools.const import METAL
from AaronTools.fileIO import FileReader
from AaronTools.geometry import Geometry
from AaronTools.ring import Ring
from AaronTools.finders import BondedTo

from chimerax.atomic import AtomicStructure, Element, Atoms
from chimerax.atomic import Residue as ChimeraResidue

from SEQCROW.finders import AtomSpec
from SEQCROW.managers.filereader_manager import apply_seqcrow_preset
from SEQCROW.commands.tsbond import tsbond

from warnings import warn


class _FauxAtomSelection:
    """for fooling SEQCROW functions"""
    def __init__(self, atoms=[], bonds=[]):
        self.atoms = atoms
        self.bonds = bonds


class Atom(AaronToolsAtom):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._atomspec = None
        self._chix_atom = None

    def __repr__(self):
        s = ""
        s += "{:>3s} ".format(self.element)
        for c in self.coords:
            s += " {: 13.8f}".format(c)
        s += "  {: 2d}".format(-1 if self.flag else 0)
        s += " {:>4s}".format(self.name)
        s += " ({:s})".format(self.atomspec) if self.atomspec is not None else "None"
        return s

    @property
    def chix_atom(self):
        return self._chix_atom

    @chix_atom.setter
    def chix_atom(self, atom):
        self._chix_atom = atom
        try:
            self._atomspec = atom.atomspec
        except AttributeError:
            pass

    @property
    def atomspec(self):
        return self._atomspec

    @atomspec.setter
    def atomspec(self, spec):
        self._atomspec = spec

    def copy(self):
        rv = Atom()
        for key, val in self.__dict__.items():
            if key == "connected":
                continue
            if key == "constraint":
                continue
            if key == "_hashed":
                continue
            if key == "chix_atom":
                continue
            try:
                rv.__dict__[key] = val.copy()
            except AttributeError:
                rv.__dict__[key] = val
                if re.search("chimerax", val.__class__.__module__):
                    continue
                if val.__class__.__module__ != "builtins":
                    self.LOG.warning(
                        "No copy method for {}: in-place changes may occur".format(
                            type(val)
                        )
                    )
        return rv


def fromChimAtom(atom=None, *args, use_scene=False, serial_number=None, atomspec=None, **kwargs):
    """get AaronTools Atom object from ChimeraX Atom"""
    if use_scene:
        coords = atom.scene_coord
    else:
        coords = atom.coord
    element = atom.element.name
    if element == "LP":
        element = "X"
    aarontools_atom = Atom(
        *args,
        name=str(atom.serial_number),
        element=element,
        coords=coords,
        **kwargs
    )
    
    aarontools_atom.chix_name = atom.name
    aarontools_atom.serial_number = atom.serial_number
    aarontools_atom.chix_atom = atom

    return aarontools_atom
   

class Residue(Geometry):
    """Residue is an intermediary between chimerax Residues and AaronTools Geometrys
    Residue has the following attributes:
    resnum      - same as chimerax Residue.number
    name        - same as chimerax Residue.name
    """
    def __init__(
            self,
            geom,
            resnum=None,
            atomspec=None,
            chain_id=None,
            name=None,
            use_scene=False,
            **kwargs
    ):
        object.__setattr__(self, "_hashed", False)
        if isinstance(geom, ChimeraResidue):
            aaron_atoms = []
            for atom in geom.atoms:
                if not atom.deleted:                      
                    aaron_atom = fromChimAtom(atom=atom, use_scene=use_scene)
                    aaron_atoms.append(aaron_atom)
            
            self.chix_residue = geom
            
            self.atomspec = None
            super().__init__(
                aaron_atoms,
                name=geom.name,
                refresh_connected=False,
                refresh_ranks=False,
                **kwargs
            )
            if resnum is None:
                self.resnum = geom.number
            else:
                self.resnum = resnum
                
            if atomspec is None and hasattr(geom, "atomspec"):
                self.atomspec = geom.atomspec
            else:
                self.atomspec = atomspec
                
            if chain_id is None:
                self.chain_id = geom.chain_id
            else:
                self.chain_id = chain_id
            
        else:
            if name is None:
                name = "UNK"
            super().__init__(geom, **kwargs)
            self.name = name
            self.resnum = resnum
            self.atomspec = atomspec
            self.chix_residue = None
            if chain_id is None:
                self.chain_id = "a"
            else:
                self.chain_id = chain_id

    def __repr__(self):
        s = "%s\n" % self.atomspec
        for atom in self.atoms:
            s += "%-2s    %6.3f    %6.3f    %6.3f    %s\n" % (atom.element, *atom.coords, atom.atomspec if hasattr(atom, "atomspec") else "")
        
        return s.strip()

    def get_element_count(self):
        """returns a dictionary with element symbols as keys and values corresponding to the
        occurences of an element in self's atoms"""
        out = {}
        for atom in self.atoms:
            if atom.element not in out:
                out[atom.element] = 1
            else:
                out[atom.element] += 1
                
        return out
    
    def update_chix(self, chix_residue, refresh_connected=True, apply_preset=True):
        """changes chimerax residue to match self"""
        known_atoms = []
        new_atoms = []

        # print("updating residue", self.name, chix_residue.name)

        chix_residue.name = self.name

        # print("updating residue:")
        # print(self.write(outfile=False))

        for atom in self.atoms:
            #print(atom, hasattr(atom, "chix_atom"))
            if (
                not hasattr(atom, "chix_atom") or \
                atom.chix_atom is None or \
                atom.chix_atom.deleted or
                atom.chix_atom not in chix_residue.atoms
            ):
                # if not hasattr(atom, "chix_atom"):
                #     print("no chix atom", atom)
                # elif atom.chix_atom is None:
                #     print("no chix atom yet", atom)
                # elif atom.chix_atom.deleted:
                #     print("chix_atom deleted", atom)
                # else:
                #     print("atoms do not match", atom.chix_atom)
                
                #print("new chix atom for", atom)
                
                if hasattr(atom, "chix_name"):
                    atom_name = atom.chix_name
                    # print("atom has chix name:", atom_name)
                else:
                    atom_name = atom.name
                    # print("atom does not have chix name:", atom_name)
                if "." in atom_name or len(atom_name) > 4:
                    # print("previous atom name was illegal, using", atom.element)
                    atom_name = atom.element
                
                new_atom = chix_residue.structure.new_atom(atom_name, atom.element)
                new_atom.coord = atom.coords
                
                chix_residue.add_atom(new_atom)
                atom.chix_atom = new_atom
                known_atoms.append(new_atom)
                new_atoms.append((atom, new_atom))

            else:
                if atom.chix_atom.element.name != atom.element:
                    atom.chix_atom.element = Element.get_element(atom.element)
                    new_atoms.append((atom, atom.chix_atom))

                atom.chix_atom.coord = atom.coords
                known_atoms.append(atom.chix_atom)
        
        for atom in chix_residue.atoms:
            if atom not in known_atoms:
                # print("deleting %s" % atom.atomspec)
                atom.delete()
        
        known_atoms = Atoms(known_atoms)
        
        known_atom_names = list(known_atoms.names)
        known_atom_names_set = set(known_atom_names)
        starting_name_ndx = dict()
        for (at_atom, atom) in new_atoms:
            # print("starting name:", atom.name)
            if (
                    atom.name in known_atom_names_set and
                    atom.name.startswith(atom.element.name) and
                    atom.name != atom.element.name and
                    "." not in atom.name and
                    known_atom_names.count(atom.name) == 1 
            ):
                # print("skipping", atom.name, atom.serial_number, atom.atomspec)
                continue
            if not atom.name.startswith(atom.element.name):
                atom.name = atom.element.name
            
            starting_name = atom.name
            
            try:
                k = starting_name_ndx[starting_name]
            except KeyError:
                k = 1
            atom_name = "%s%i" % (atom.name, k)
            while atom_name in known_atom_names_set:
                k += 1
                atom_name = "%s%i" % (atom.name, k)
                if len(atom_name) > 4:
                    if atom.name == atom.element.name:
                        print("breaking:", k, atom.name)
                        break
                    atom.name = atom.element.name
                    k = 1
            starting_name_ndx[starting_name] = k + 1
            
            # print("name:", atom_name)
            
            if len(atom_name) <= 4:
                atom.name = atom_name
            else:
                atom.name = atom.element.name
            
            known_atom_names_set.add(atom.name)
            known_atom_names.append(atom.name)

            at_atom.chix_name = atom.name
            at_atom.chix_atom = atom
            at_atom.serial_number = atom.serial_number

            # print("final name:", atom.name)

        if refresh_connected:
            self.refresh_chix_connected(chix_residue)

        for i, atom in enumerate(chix_residue.atoms):
            if atom.serial_number == -1:
                atom.serial_number = i + 1
        
        if apply_preset:
            apply_seqcrow_preset(chix_residue.structure, atoms=[atom[1] for atom in new_atoms])

    def refresh_chix_connected(self, chix_residue):
        known_bonds = []
        known_chix_bonds = []
        residue_bonds = set()
        for atom in chix_residue.atoms:
            for bond in atom.bonds:
                residue_bonds.add(bond)
        
        for i, aaron_atom1 in enumerate(self.atoms):
            atom1 = [atom for atom in chix_residue.atoms if aaron_atom1.chix_atom == atom][0]
            for aaron_atom2 in self.atoms[:i]:
                if aaron_atom2 not in aaron_atom1.connected:
                    continue

                if sorted((aaron_atom1, aaron_atom2,)) in known_bonds:
                    continue
                
                known_bonds.append(sorted((aaron_atom1, aaron_atom2,)))

                atom2 = [atom for atom in chix_residue.atoms if atom == aaron_atom2.chix_atom]
                if len(atom2) > 0:
                    atom2 = atom2[0]
                else:
                    #we cannot draw a bond to an atom that is not in the residue
                    #this could happen when previewing a substituent or w/e with the libadd tool
                    continue
                
                if atom1 not in atom2.neighbors:
                    new_bond = chix_residue.structure.new_bond(atom1, atom2)

                    if any([aaron_atom.element in METAL for aaron_atom in [aaron_atom1, aaron_atom2]]):
                        try:
                            pbg = chix_residue.structure.pseudobond_group(
                                chix_residue.structure.PBG_METAL_COORDINATION,
                                create_type=1,
                            )
                        except TypeError:
                            pbg = chix_residue.structure.pseudobond_group(
                                chix_residue.structure.PBG_METAL_COORDINATION,
                                create_type=2,
                            )
                        pbg.new_pseudobond(atom1, atom2)
                        new_bond.delete()
                    else:
                        known_chix_bonds.append(new_bond)
                
                else:
                    bond = [b for b in atom1.bonds if atom2 in b.atoms][0]
                    known_chix_bonds.append(bond)
        
        for bond in residue_bonds:
            if bond not in known_chix_bonds:
                # print("deleting bond %s" % str(bond))
                bond.delete()

    def substitute(self, sub, target, *args, attached_to=None, **kwargs):
        if attached_to is None:
            from SEQCROW.selectors import get_fragment
            
            frags = []
            target = self.find(target)[0]
            target_chix = target.chix_atom
            for bonded_atom in target_chix.neighbors:
                frags.append(get_fragment(bonded_atom, target_chix))
            
            attached_to = None
            longest_frag = None
            
            cyclic = np.zeros(len(frags), dtype=bool)
            for test_end, (i, frag1) in zip(target_chix.neighbors, enumerate(frags)):
                for j, frag2 in enumerate(frags[i + 1:]):
                    if cyclic[i + j + 1]:
                        continue
                    if frag1.intersects(frag2) or test_end in frag2:
                        cyclic[i] = True
                        cyclic[i + j + 1] = True
                        break
                
                if cyclic[i]:
                    if target.chix_atom and target.chix_atom.session:
                        target.chix_atom.session.logger.warning(
                            "trying to guess a fragment to replace for an atom in a ring"
                        )
                    continue
                
                if attached_to is None or len(longest_frag) < len(frag1):
                    longest_frag = frag1
                    attached_to = test_end
            
            if attached_to is not None:
                attached_to = self.find(AtomSpec(attached_to.atomspec))[0]
        
        return super().substitute(sub, target, *args, attached_to=attached_to, **kwargs)


class ResidueCollection(Geometry):
    """geometry object used for SEQCROW to easily convert to AaronTools but keep residue info"""
    def __init__(
        self,
        molecule,
        name="new",
        bonds_matter=True,
        convert_residues=None,
        use_scene=False,
        **kwargs
    ):
        """molecule       - chimerax AtomicStructure or AaronTools Geometry (for easy compatibility stuff)
        convert_residues  - None to convert everything or [chimerax.atomic.Residue] to convert only specific residues
                            this only applies to chimerax AtomicStructures
        bonds_matter      - False to skip adding bonds/determining connectivity based on ChimeraX AtomicStructure
        """
        object.__setattr__(self, "_hashed", False)
        self.convert_residues = convert_residues
        if isinstance(molecule, AtomicStructure):
            self.chix_atomicstructure = molecule
            self.residues = []
            self.atomspec = molecule.atomspec
            
            #convert chimerax stuff to AaronTools
            all_atoms = []
            if convert_residues is None:
                convert_residues = molecule.residues
            for i, residue in enumerate(convert_residues):  
                new_res = Residue(
                    residue,
                    comment=molecule.comment if hasattr(molecule, "comment") else None,
                    use_scene=use_scene,
                )
                
                self.residues.append(new_res)
                
                all_atoms.extend(new_res.atoms)

            refresh_ranks = False
            if "refresh_ranks" in kwargs:
                refresh_ranks = kwargs.pop("refresh_ranks")
            
            super().__init__(
                all_atoms, 
                name=molecule.name, 
                comment=molecule.comment if hasattr(molecule, "comment") else "", 
                refresh_connected=False, 
                refresh_ranks=refresh_ranks,
                **kwargs,
            )
        
            if not bonds_matter:
                return
        
            #update bonding to match that of the chimerax molecule
            for atom in all_atoms:
                atom.connected = set()
                for atom2 in all_atoms:
                    if atom2.chix_atom not in atom.chix_atom.neighbors:
                        continue
                    
                    atom.connected.add(atom2)
            
            #add bonds to metals
            tm_bonds = molecule.pseudobond_group(molecule.PBG_METAL_COORDINATION, create_type=None)
            if tm_bonds is not None:
                for pseudobond in tm_bonds.pseudobonds:
                    atom1, atom2 = pseudobond.atoms
                    if self.convert_residues is not None and (atom1.residue not in self.convert_residues or atom2.residue not in self.convert_residues):
                        continue
                    
                    aaron_atom1 = self.find(AtomSpec(atom1.atomspec))[0]
                    aaron_atom2 = self.find(AtomSpec(atom2.atomspec))[0]
                    aaron_atom1.connected.add(aaron_atom2)
                    aaron_atom2.connected.add(aaron_atom1)
            
            if use_scene:
                pos = molecule.session.main_view.camera.get_position().inverse()
                self.coords = pos * self.coords

        else:
            #assume whatever we got is something AaronTools can turn into a Geometry
            super().__init__(molecule, name=name, **kwargs)
            self.chix_atomicstructure = None
            self.atomspec = None
            try:
                kwargs.pop("refresh_connected")
            except KeyError:
                pass
            if "comment" in kwargs:
                self.residues = [Residue(molecule, resnum=1, name="UNK", refresh_connected=False, **kwargs)]
            elif hasattr(molecule, "comment"):
                self.residues = [Residue(molecule, resnum=1, name="UNK", comment=molecule.comment, refresh_connected=False, **kwargs)]
            else:
                self.residues = [Residue(molecule, resnum=1, name="UNK", refresh_connected=False, **kwargs)]

            return

    def __repr__(self):
        s = "%s\n" % self.atomspec
        for atom in self.atoms:
            s += "%-2s    %6.3f    %6.3f    %6.3f    %s\n" % (atom.element, *atom.coords, atom.atomspec if hasattr(atom, "atomspec") else "")
        
        return s.strip()

    def _atom_update(self):
        #old_atoms = [a for a in self.atoms]
        self.atoms = []
        for res in self.residues:
            self.atoms.extend(res.atoms)

    # def refresh_ranks(self, *args, useful=False, **kwargs):
    #     if useful:
    #         super().refresh_ranks(*args, **kwargs)

    def copy(self, atoms=None, name=None, comment=None, copy_atoms=True):
        """
        creates a new copy of the geometry
        parameters:
            atoms (list): defaults to all atoms
            name (str): defaults to NAME_copy
        """
        if name is None:
            name = self.name
        if comment is None:
            comment = self.comment
        atoms = self._fix_connectivity(atoms, copy=copy_atoms)
        if hasattr(self, "components") and self.components is not None and comment is None:
            self.fix_comment()
        return ResidueCollection(atoms, name, comment=comment, refresh_ranks=False, refresh_connected=False)

    def map_ligand(self, *args, **kwargs):
        """map_ligand, then put new atoms in the residue they are closest to"""
        super().map_ligand(*args, **kwargs)
        
        atoms_not_in_residue = []
        for atom in self.atoms:
            if not any(atom in residue for residue in self.residues):
                atoms_not_in_residue.append(atom)

        for residue in self.residues[::-1]:
            remove_atoms = []
            for atom in residue.atoms:
                if atom not in self.atoms:
                    remove_atoms.append(atom)
            
            for atom in remove_atoms:
                residue.atoms.remove(atom)
            
            if len(residue.atoms) == 0:
                self.residues.remove(residue)
        
        new_lig = Residue(atoms_not_in_residue, name="LIG", resnum=len([res for res in self.residues if len(res.atoms) > 0])+1)
        self.residues.append(new_lig)

    def substitute(
        self,
        sub,
        target,
        attached_to=None,
        *args,
        minimize=False,
        use_greek=False,
        new_residue=False,
        new_name=None,
        **kwargs
    ):
        """find the residue that target is on and substitute it for sub"""
        target = self.find_exact(target)[0]
        residue = self.find_residue(target)

        if len(residue) != 1:
            raise RuntimeError("multiple or no residues found containing %s" % str(target))
        else:
            residue = residue[0]
        
        if attached_to:
            attached_to = self.find_exact(attached_to)[0]        

        # call substitute on residue so atoms are added to that residue
        if attached_to and attached_to not in residue.atoms:
            residue.atoms.append(attached_to)
            new_sub = super().substitute(sub, target, attached_to=attached_to, *args, minimize=False, **kwargs)
            residue -= self.find(
                residue.atoms,
                residue.get_fragment(target, stop=sub)
            )
            residue += new_sub
        else:
            try:
                new_sub = residue.substitute(
                    sub, target, *args, attached_to=attached_to, minimize=False, **kwargs
                )
            except LookupError:
                new_sub = super().substitute(
                    sub, target, *args, attached_to=attached_to, minimize=False, **kwargs
                )
                residue -= self.find(
                    residue.atoms,
                    self.get_fragment(target, stop=sub)
                )
                residue += new_sub

        if new_name:
            residue.name = new_name

        if new_residue:
            residue -= new_sub
            new_sub.end.connected.add(new_sub.atoms[0])
            self.residues.append(
                Residue(
                    new_sub.atoms,
                    name=new_name,
                    resnum=target.chix_atom.structure.num_residues + 1,
                    chain_id=target.chix_atom.residue.chain_id,
                )
            )

        self._atom_update()

        # minimize on self so other residues can be taken into account
        if minimize:
            sub_start = sub.find_exact(BondedTo(sub.end))[0]
            self.minimize_torsion(
                sub.atoms, 
                sub_start.bond(sub.end), 
                sub.end,
                increment=10,
            )

        if use_greek:
            from AaronTools.finders import NotAny
            alphabet = [
                "A",
                "B",
                "G",
                "D",
                "E",
                "Z",
                "H",
                "Q",
                "I",
                "K",
                "L",
                "M",
                "N",
                "X",
                "R",
                "T",
                "U",
                "F",
                "C",
                "Y",
                "W",
            ]
            
            start_atom = sub.end
            start = ""
            if len(start_atom.chix_name) > len(start_atom.element):
                start = start_atom.chix_name[len(start_atom.element)]
            if not new_residue and any(letter == start for letter in alphabet):
                ndx = alphabet.index(start) + 1
            else:
                ndx = 0

            dist = 1
            cur_atoms = sub.find(list(start_atom.connected), BondedTo(sub.end))
            prev_atoms = [start_atom]
            stop = [start_atom]
            not_h = sub.find(NotAny("H"))
            while ndx < len(alphabet):
                if not cur_atoms:
                    break
                for i, atom in enumerate(cur_atoms):
                    atom.chix_name = "%s%s" % (atom.element, alphabet[ndx])
                    if len([a for a in cur_atoms if a.element == atom.element]) > 1:
                        neighbors = sub.find(BondedTo(atom), prev_atoms, not_h)
                        for neighbor in neighbors:
                            if not hasattr(neighbor, "chix_name"):
                                continue
                            match = re.search("(\d+)", neighbor.chix_name)
                            if match:
                                i = int(match.group(1)) - 1
                                break

                        atom.chix_name += "%i" % (i + 1)

                    h_atoms = sub.find("H", BondedTo(atom))

                    for j, h_atom in enumerate(h_atoms):
                        if len([a for a in cur_atoms if a.element == atom.element]) == 1 and len(h_atoms) > 1:
                            h_atom.chix_name = "%s%s%i" % ("H", alphabet[ndx], j + 1)
                        elif len(h_atoms) > 1:
                            h_atom.chix_name = "%s%s%i%i" % ("H", alphabet[ndx], i + 1, j + 1)
                        elif (
                                len([a for a in cur_atoms if a.element == atom.element]) > 1 and
                                len(sub.find("H", [BondedTo(a) for a in cur_atoms])) > 1
                        ):
                            h_atom.chix_name = "%s%s%i" % ("H", alphabet[ndx], i + 1)
                        else:
                            h_atom.chix_name = "%s%s" % ("H", alphabet[ndx])

                prev_atoms = cur_atoms
                stop.extend(cur_atoms)
                cur_atoms = self.find(
                    [BondedTo(atom) for atom in prev_atoms],
                    NotAny(stop),
                    NotAny("H"),
                )
                for atom in cur_atoms[::-1]:
                    if cur_atoms.count(atom) > 1:
                        cur_atoms.remove(atom)

                ndx += 1
                dist += 1

        return sub

    def ring_substitute(self, target, ring, *args, **kwargs):
        """put a ring on the given targets"""
        if not isinstance(ring, Ring):
            ring = Ring(ring)

        residue = self.find_residue(target[0])[0]
        
        super().ring_substitute(target, ring, *args, **kwargs)

        new_atoms = [atom for atom in self.atoms if not hasattr(atom, "chix_atom")]
        residue.atoms.extend(new_atoms)

        for res in self.residues:
            deleted_atoms = []
            for atom in res.atoms:
                if not hasattr(atom, "chix_atom"):
                    continue

                if atom.chix_atom.residue is not res.chix_residue and atom in self.atoms:
                    deleted_atoms.append(atom)
                elif atom not in self.atoms:
                    deleted_atoms.append(atom)
                
            for atom in deleted_atoms:
                res.atoms.remove(atom)

    def find_residue(self, target):
        """returns a list of residues containing the specified target"""
        atom = self.find(target)
        if len(atom) != 1:
            raise LookupError("multiple or no atoms found for %s" % target)
        else:
            atom = atom[0]
        
        out = []
        for residue in self.residues:
            if target in residue.atoms:
                out.append(residue)
                
        return out

    def difference(self, atomic_structure):
        """returns {'geom missing':[chimerax.atomic.Atom], 'chix missing':[ChimAtom]} 
        'geom missing' are atoms that are missing from self but are on the ChimeraX AtomicStructure
        'chix missing' are atoms that are on self but not on the ChimeraX AtomicStructure"""
        
        geom_missing = []
        chix_missing = []
        
        for atom in self.atoms:
            if not hasattr(atom, "chix_atom") or atom.chix_atom not in atomic_structure.atoms:
                chix_missing.append(atom)
               
        for atom in atomic_structure.atoms:
            if not any([atom == aaron_atom.chix_atom for aaron_atom in self.atoms if hasattr(aaron_atom, "chix_atom")]) \
                    and (atom.residue in self.convert_residues or self.convert_residues is None):
                geom_missing.append(atom)
                
        out = {'geom missing': geom_missing, 'chix missing': chix_missing}
        return out
    
    def change_element(self, target, *args, hold_steady=None, **kwargs):
        target = self.find_exact(target)[0]
        residue = self.find_residue(target)
        if hold_steady:
            hold_steady = self.find(hold_steady)

        if len(residue) != 1:
            raise RuntimeError("multiple or no residues found containing %s" % str(target))
        else:
            residue = residue[0]

        residue.change_element(
            target,
            *args,
            hold_steady=hold_steady,
            **kwargs,
        )
        self._atom_update()
    
    def update_chix(
        self,
        atomic_structure,
        refresh_connected=True,
        apply_preset=True,
        discard_residues=False,
    ):
        """
        update chimerax atomic structure to match self
        may also change residue numbers for self
        refresh_connected - False to skip updating connectivity
        """

        atomic_structure.comment = self.comment

        if not refresh_connected:
            for atom in self.atoms:
                if hasattr(atom, "chix_atom"):
                    atom.chix_atom.coord = atom.coords
            
            return

        if discard_residues:
            res = atomic_structure.new_residue(
                self.name,
                "a",
                1,
            )
            for res_2 in atomic_structure.residues[:-1]:
                res_2.delete()
            at_res = Residue(self)
            at_res.update_chix(res)
        
        else:
            for residue in self.residues:
                if (
                    residue.chix_residue is None or \
                    residue.chix_residue.deleted or \
                    residue.chix_residue not in atomic_structure.residues
                ):
                    res = atomic_structure.new_residue(residue.name, residue.chain_id, residue.resnum)
                    residue.chix_residue = res
                    if self.convert_residues is not None:
                        self.convert_residues.append(res)
                else:
                    res = residue.chix_residue
    
                try:
                    residue.update_chix(res, refresh_connected=False, apply_preset=apply_preset)
                except RuntimeError:
                    # somtimes I get an error saying the residue has already
                    # been deleted even though I checked if chix_residue.deleted...
                    # maybe all the atoms got deleted?
                    res = atomic_structure.new_residue(residue.name, residue.chain_id, residue.resnum)
                    residue.chix_residue = res
                    
            if self.convert_residues is None:
                for residue in atomic_structure.residues:
                    if not any(residue is res.chix_residue for res in self.residues):
                        residue.delete()
                
                for residue in atomic_structure.residues[len(self.residues):]:
                    residue.delete()
    
            else:
                for residue in atomic_structure.residues:
                    if residue in self.convert_residues and not any(residue is res.chix_residue for res in self.residues):
                        residue.delete()
    
            # if refresh_connected:
            #     self.refresh_chix_connected(atomic_structure, sanity_check=False)
            self.refresh_chix_connected(atomic_structure, sanity_check=False)

    def refresh_chix_connected(self, atomic_structure, sanity_check=True):
        """updates atomic_structure's bonds to match self's connectivity
        sanity_check - bool; check to make sure atomic_structure corresponds to self"""
        if sanity_check:
            diff = self.difference(atomic_structure)
            for key in diff:
                if len(diff[key]) != 0:
                    raise Exception("ResidueCollection does not correspond to AtomicStructure: \n%s\n\n%s" % \
                        (repr(self), repr(ResidueCollection(atomic_structure))))
                    
        known_bonds = set()
        for bond in atomic_structure.bonds:
            if self.convert_residues is None or all(atom.residue in self.convert_residues for atom in bond.atoms):
                a1, a2 = bond.atoms
                aaron_atom1 = self.find_exact(AtomSpec(a1.atomspec))[0]
                aaron_atom2 = self.find_exact(AtomSpec(a2.atomspec))[0]
                if aaron_atom1 in aaron_atom2.connected:
                    known_bonds.add((aaron_atom1, aaron_atom2,))
                    known_bonds.add((aaron_atom2, aaron_atom1,))
                else:
                    bond.delete()

        remaining_atoms = set(atomic_structure.atoms)

        for aaron_atom1 in self.atoms:
            atom1 = None
            for atom in remaining_atoms:
                if aaron_atom1.chix_atom is atom:
                    atom1 = atom
                    break
            
            remaining_atoms.remove(atom1)
            atom1_is_metal = aaron_atom1.element in METAL

            for aaron_atom2 in aaron_atom1.connected:
                if (aaron_atom1, aaron_atom2,) in known_bonds:
                    continue

                # if not hasattr(aaron_atom2, "chix_atom"):
                #     print(aaron_atom2, "has no chix_atom")
                
                known_bonds.add((aaron_atom1, aaron_atom2,))
                known_bonds.add((aaron_atom2, aaron_atom1,))

                for atom in remaining_atoms:
                    if atom is aaron_atom2.chix_atom:
                        atom2 = atom
                        break
                else:
                    #we cannot draw a bond to an atom that is not in the residue
                    #this could happen when previewing a substituent or w/e with the libadd tool
                    continue

                atom2_is_metal = aaron_atom2.element in METAL
                
                if atom2 not in atom1.neighbors:
                    if atom1_is_metal or atom2_is_metal:
                        try:
                            pbg = atomic_structure.pseudobond_group(
                                atomic_structure.PBG_METAL_COORDINATION,
                                create_type=1
                            ) 
                        except TypeError:
                            pbg = atomic_structure.pseudobond_group(
                                atomic_structure.PBG_METAL_COORDINATION,
                                create_type=2
                            ) 
                        pbg.new_pseudobond(atom1, atom2)
                    else:
                        new_bond = atomic_structure.new_bond(atom1, atom2)

    def all_geom_coordsets(self, filereader):
        if filereader.all_geom is None:
            warn("coordsets requested, but the file contains one or fewer sets of coordinates")
            coordsets = np.array([self.coords])
        elif isinstance(filereader.all_geom, np.ndarray):
            return filereader.all_geom
        else:
            coordsets = np.zeros((len(filereader.all_geom), len(self.atoms), 3))
            if isinstance(filereader.all_geom, np.ndarray):
                coordsets = filereader.all_geom
            else:
                for i, all_geom in enumerate(filereader.all_geom):
                    atom_list = all_geom["atoms"]
                    for j, atom in enumerate(atom_list):
                        coordsets[i][j] = atom.coords

        return coordsets                    
    
    def get_chimera(self, session, coordsets=False, filereader=None, discard_residues=False):
        """returns a chimerax equivalent of self"""
        struc = AtomicStructure(session, name=self.name)
        if filereader is not None:
            struc.filereaders = [{key: filereader[key] for key in filereader.keys()}]
        struc.comment = self.comment

        self.update_chix(struc, discard_residues=discard_residues)

        if coordsets and filereader is not None and filereader.all_geom is not None:
            #make a trajectory
            #each list of atoms in filereader.all_geom is a frame in the trajectory
            #replace previous coordinates
            #this matters when a filereader is given because the
            #geometry created from a filereader (which was probably passed as geom)
            #is the last geometry in the log or xyz file
            xyzs = self.all_geom_coordsets(filereader)
            struc.add_coordsets(xyzs, replace=True)
            struc.active_coordset_id = len(xyzs)

        # if it's a frequency file, draw TS bonds for imaginary modes
        if filereader is not None and "frequency" in filereader.other:
            for mode in filereader.other["frequency"].data:
                if mode.frequency < 0:
                    max_disp = max(np.linalg.norm(x) for x in mode.vector)
                    cur_coords = self.coords
                    coord_forward = self.coords + (0.4 / max_disp) * mode.vector
                    coord_reverse = self.coords - (0.4 / max_disp) * mode.vector
                    forward_connectivity = np.zeros((len(self.atoms), len(self.atoms)))
                    reverse_connectivity = np.zeros((len(self.atoms), len(self.atoms)))
                    self.update_geometry(coord_forward)
                    self.refresh_connected()
                    for i, atom1 in enumerate(self.atoms):
                        for j, atom2 in enumerate(self.atoms[:i]):
                            if atom1 in atom2.connected:
                                forward_connectivity[i, j] = 1
                                forward_connectivity[j, i] = 1
                    
                    self.update_geometry(coord_reverse)
                    self.refresh_connected()
                    for i, atom1 in enumerate(self.atoms):
                        for j, atom2 in enumerate(self.atoms[:i]):
                            if atom1 in atom2.connected:
                                reverse_connectivity[i, j] = 1
                                reverse_connectivity[j, i] = 1
                    
                    changes = forward_connectivity - reverse_connectivity
                    for i, atom1 in enumerate(self.atoms):
                        for j, atom1 in enumerate(self.atoms[:i]):
                            if changes[i,j] != 0:
                                sel = _FauxAtomSelection(
                                    atoms=(struc.atoms[i], struc.atoms[j])
                                )
                                tsbond(session, sel)
                    
                    self.update_geometry(cur_coords)
        
        if filereader is not None and "Löwdin Charges" in filereader.other:
            for atom, charge in zip(struc.atoms, filereader.other["Löwdin Charges"]):
                atom.loewdinCharge = charge
                atom.charge = charge

        if filereader is not None and "Mulliken Charges" in filereader.other:
            for atom, charge in zip(struc.atoms, filereader.other["Mulliken Charges"]):
                atom.mullikenCharge = charge
                atom.charge = charge

        if filereader is not None and "NPA Charges" in filereader.other:
            for atom, charge in zip(struc.atoms, filereader.other["NPA Charges"]):
                atom.npaCharge = charge
                atom.charge = charge

        if filereader is not None and "Nuclear ZEff" in filereader.other:
            for atom, zeff in zip(struc.atoms, filereader.other["Nuclear ZEff"]):
                atom.Zeff = zeff

        if filereader is not None and "Nuclear spins" in filereader.other:
            for atom, spin in zip(struc.atoms, filereader.other["Nuclear spins"]):
                atom.nuclearSpin = spin

        return struc
