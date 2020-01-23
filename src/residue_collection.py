import numpy as np

import re

from AaronTools.atoms import Atom
from AaronTools.catalyst import Catalyst
from AaronTools.const import TMETAL
from AaronTools.geometry import Geometry
from AaronTools.ring import Ring

from chimerax.atomic import AtomicStructure
from chimerax.atomic import Atom as ChixAtom
from chimerax.atomic.colors import element_color

from .managers.freqfile_manager import FREQ_FILE_REMOVED

class ChimAtom(Atom):
    """ChimAtom object allows for easy conversion between chimerax atoms and AaronTools Atoms
    several overloaded functions are different from AaronTools Atoms because 
    ChimAtom names can contain letters"""
    def __init__(self, atom=None, *args, serial_number=None, atomspec=None, **kwargs):
        """atom to go between chimerax Atom and AaronTools Atom"""
        if isinstance(atom, ChixAtom):          
            super().__init__(*args, name=atom.name, element=str(atom.element), coords=atom.scene_coord, **kwargs)
            
            self.add_tag(atom.atomspec)
            self.atomspec = atom.atomspec
            self.serial_number = atom.serial_number
            self.chix_atom = atom
        
        elif isinstance(atom, Atom):
            super().__init__(element=atom.element, coords=atom.coords, name=atom.name)
            
            if not hasattr(self, "chix_atom"):
                self.chix_atom = None
            
            if atomspec is not None:
                self.atomspec = str(atomspec)
                self.add_tag(str(atomspec))
            elif not hasattr(self, "atomspec"):
                self.atomspec = None
                
            if serial_number is not None:
                self.serial_number = serial_number
            elif not hasattr(self, "serial_number"):
                self.serial_number = None
    
        else:
            raise TypeError("atom is of type %s; expected AaronTools Atom or chimerax Atom" % type(atom))
    
    def __lt__(self, other):
        """
        sorts by canonical smiles invariant, then by name
            more connections first
            then, more non-H bonds first
            then, higher atomic number first
            then, higher number of attached hydrogens first
            then, lower sorting name first
        
        differs from Atom's __lt__ b/c ChimAtom names generally also include the element symbol
        """
        a = self.get_invariant()
        b = other.get_invariant()
        if a != b:
            return a > b


        #sometimes the name has a different element in it
        if re.match(r'[A-Za-z]', self.name):
            a = [str(self.serial_number)] + self.name.split(".")[1:]
        else:
            a = self.name.split('.')
            
        if re.match(r'[A-Za-z]', other.name):
            b = [str(other.serial_number)] + other.name.split(".")[1:]
        else:
            b = other.name.split('.')
            
        while '' in b:
            b.remove('')        
        while '' in a:
            a.remove('')
        while len(a) < len(b):
            a += ["0"]
        while len(b) < len(a):
            b += ["0"]
        for i, j in zip(a, b):
            if int(i) == int(j):
                continue
            return int(i) < int(j)
        else:
            return True

    def __repr__(self):
        return "%s    %f %f %f    %s    %s" % (self.name, *self.coords, self.element, self.atomspec)

    def __float__(self):
        """
        converts self.name from a string to a floating point number
        """
        if re.match(r'[A-Za-z]', self.name):
            rv = [str(self.serial_number)] + self.name.split(".")[1:]
        else:
            rv = self.name.split('.')

        if len(rv) == 0:
            return float(0)
        if len(rv) == 1:
            return float(rv[0])
        rv = "{}.{}".format(rv[0], rv[1])
        return float(rv)
        

class Residue(Geometry):
    """Residue is an intermediary between chimerax Residues and AaronTools Geometrys
    Residue has the following attributes:
    resnum      - same as chimerax Residue.number
    name        - same as chimerax Residue.name
    """
    def __init__(self, geom, resnum=None, name="UNK", **kwargs):
        super().__init__(geom, name=name, **kwargs)
        self.resnum = resnum

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


class ResidueCollection(Geometry):
    """geometry object used for ChimAARON to easily convert to AaronTools but keep residue info"""
    def __init__(self, molecule, refresh_connected=False, **kwargs):
        """molecule     - chimerax AtomicStructure or [AtomicStructure] or AaronTools Geometry (for easy compatibility stuff)"""
        if isinstance(molecule, Catalyst):
            super().__init__(molecule, refresh_connected=refresh_connected, comment=molecule.comment, **kwargs)
                
            self.residues = []
            i = 1
            for key in molecule.components:
                for comp in molecule.components[key]:
                    if key == 'ligand':
                        resname = "LIG"
                    else:
                        resname = "SUB"
                    
                    self.residues.append(Residue(comp, refresh_connected=refresh_connected, resnum=i, name=resname))
                    i += 1
                    
            self.residues.append(Residue(molecule.center, refresh_connected=refresh_connected, resnum=i, name="CENT"))
            self.session = None
            self._atom_update()
            return
        
        elif isinstance(molecule, AtomicStructure):
            self.residues = []
            
            #convert chimerax stuff to AaronTools
            all_atoms = []
            for i, residue in enumerate(molecule.residues):
                aaron_atoms = []
                for atom in residue.atoms:
                    if not atom.deleted:                      
                        aaron_atom = ChimAtom(atom=atom)
                        aaron_atoms.append(aaron_atom)
    
                self.residues.append(Residue(aaron_atoms, \
                                        name=residue.name, \
                                        resnum=residue.number, \
                                        comment=molecule.comment if hasattr(molecule, "comment") else "", \
                                        refresh_connected=False))
                
                all_atoms.extend(aaron_atoms)
            
            super().__init__(all_atoms, name=molecule.name, refresh_connected=refresh_connected, comment=molecule.comment if hasattr(molecule, "comment") else "", **kwargs)
        
            #update bonding to match that of the chimerax molecule
            for bond in molecule.bonds:
                atom1 = bond.atoms[0]
                atom2 = bond.atoms[1]
                
                aaron_atom1 = self.find(atom1.atomspec)
                if len(aaron_atom1) > 1:
                    raise RuntimeError("multiple atoms might have the same atomspec: %s" % \
                        " ".join([str(atom) for atom in aaron_atom1]))
                else:
                    aaron_atom1 = aaron_atom1[0]
                    
                aaron_atom2 = self.find(atom2.atomspec)
                if len(aaron_atom2) != 1:
                    raise RuntimeError("multiple atoms might have the same atomspec: %s" % \
                        " ".join([str(atom) for atom in aaron_atom2]))
                else:
                    aaron_atom2 = aaron_atom2[0]
                    
                aaron_atom1.connected.add(aaron_atom2)
                aaron_atom2.connected.add(aaron_atom1)
        
            for atom in self.atoms:
                for atom2 in atom.connected:
                    if not isinstance(atom2, ChimAtom):
                        atom.connected.remove(atom2)
            
            #add bonds to metals
            tm_bonds = molecule.pseudobond_group(molecule.PBG_METAL_COORDINATION, create_type=None)
            if tm_bonds is not None:
                for pseudobond in tm_bonds.pseudobonds:
                    atom1, atom2 = pseudobond.atoms
                    aaron_atom1 = self.find(atom1.atomspec)[0]
                    aaron_atom2 = self.find(atom2.atomspec)[0]
                    aaron_atom1.connected.add(aaron_atom2)
                    aaron_atom2.connected.add(aaron_atom1)
        
            self.session = molecule.session
            
        else:
            #assume whatever we got is something AaronTools can turn into a Geometry
            super().__init__(molecule, refresh_connected=refresh_connected, **kwargs)
            if "comment" in kwargs:
                self.residues = [Residue(molecule, resnum=1, name="UNK", refresh_connected=refresh_connected, comment=kwargs['comment'])]
            if hasattr(molecule, "comment"):
                self.residues = [Residue(molecule, resnum=1, name="UNK", refresh_connected=refresh_connected, comment=molecule.comment)]
            else:
                self.residues = [Residue(molecule, resnum=1, name="UNK", refresh_connected=refresh_connected)]
            self.session = None
            self._atom_update()
            return
                
    def _atom_update(self):
        """convert all atoms to ChimAtoms and make sure all atoms have the proper connectivity"""
        if hasattr(self, "residues"):
            self.atoms = []
            for residue in self.residues:
                self.atoms.extend(residue.atoms)
        
        connectivity_index = []
        for atom in self.atoms:
            connectivity_index.append([])
            for atom2 in atom.connected:
                if atom2 in self.atoms:
                    connectivity_index[-1].append(self.atoms.index(atom2))

        chim_atoms = {}
        for i, atom in enumerate(self.atoms):
            if not isinstance(atom, ChimAtom):
                chim_atoms[atom] = ChimAtom(atom=atom, serial_number=self.atoms.index(atom)+1)
                
        if hasattr(self, "residues"):
            for residue in self.residues:
                for i, atom in enumerate(residue.atoms):
                    if not isinstance(atom, ChimAtom):
                        residue.atoms[i] = chim_atoms[atom]
                    
            self.atoms = []
            for residue in self.residues:
                self.atoms.extend(residue.atoms)
        else:
            #structure is not a ResidueCollection
            for i, atom in enumerate(self.atoms):
                if not isinstance(atom, ChimAtom):
                    self.atoms[i] = chim_atoms[atom]
                
        for i in range(0, len(self.atoms)):
            self.atoms[i].connected = set([])
            for j in connectivity_index[i]:
                self.atoms[i].connected.add(self.atoms[j])
        
    def substitute(self, sub, target, *args, **kwargs):
        """find the residue that target is on and substitute it for sub"""
        target = self.find(target)
        if len(target) != 1:
            raise RuntimeError("substitute can only apply to one target at a time: %s" % ", ".join(str(t) for t in target))
        else:
            target = target[0]
            
        residue = self.find_residue(target)
        if len(residue) != 1:
            raise RuntimeError("multiple or no residues found containing %s" % str(target))
        else:
            residue = residue[0]

        ResidueCollection._atom_update(sub)
        
        residue.substitute(sub, target, *args, **kwargs)

        self._atom_update()

    def ring_substitute(self, target, ring, *args, **kwargs):
        """put a ring on the given targets"""
        target = self.find(target)
        if not isinstance(ring, Ring):
            ring = Ring(ring)
            
        if len(target) != 2:
            raise RuntimeError("can only specify two targets")
            
        residue_1 = self.find_residue(target[0])[0]
        residue_2 = self.find_residue(target[1])[0]
        
        #turn atoms into ChixAtoms
        ResidueCollection._atom_update(ring)
        
        #update ring end
        ring.end = ring.find(",".join(atom.name for atom in ring.end)) 
        
        if residue_1 is not residue_2:
            temp_res = Residue(residue_1.atoms + residue_2.atoms)
            temp_res.ring_substitute(target, ring, *args, **kwargs)
            
            for atom in temp_res.atoms:
                if atom not in residue_1.atoms and atom not in residue_2.atoms:
                    residue_1.atoms.append(atom)
                    
            for atom in residue_1.atoms + residue_2.atoms:
                if atom not in temp_res.atoms:
                    res = self.find_residue(atom)[0]
                    res -= atom
        
        else:
            residue_1.ring_substitute(target, ring, *args, **kwargs)   
                    
        self._atom_update()

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
            if not any([atom == aaron_atom.chix_atom for aaron_atom in self.atoms if hasattr(aaron_atom, "chix_atom")]):
                geom_missing.append(atom)
                
        out = {'geom missing': geom_missing, 'chix missing': chix_missing}
        return out
    
    def update_chix(self, atomic_structure):
        """update chimerax atomic structure to match self"""
        differences = self.difference(atomic_structure)
        
        for atom in differences['geom missing']:
            atom.delete()

        for atom in differences['chix missing']:
            self_res = self.find_residue(atom)

            if len(self_res) != 1:
                raise LookupError("multiple or no residues found for %s" % atom)
            else:
                self_res = self_res[0]
            
            res = [residue for residue in atomic_structure.residues if residue.number == self_res.resnum and residue.name == self_res.name]
            if len(res) != 1:
                res = atomic_structure.new_residue(self_res.name, "a", self_res.resnum)
            else:
                res = res[0]
            i = 1
            atom_name = "%s%i" % (atom.element, i)
            while any([chix_atom.name == "%s%i" % (atom.element, i) for chix_atom in res.atoms]):
                i += 1
                atom_name = "%s%i" % (atom.element, i)
            
            new_atom = atomic_structure.new_atom(atom_name, atom.element)
            new_atom.coord = atom.coords
            new_atom.draw_mode = ChixAtom.STICK_STYLE
            new_atom.color = element_color(new_atom.element.number)

            atom.chix_atom = new_atom

            res.add_atom(new_atom)
        
        for atom in self.atoms:
            atom.chix_atom.coord = atom.coords
        
        self.refresh_chix_connected(atomic_structure, sanity_check=False)
        
        #remove atomic_structure's filereaderZ
        if hasattr(atomic_structure, "aarontools_filereader"):
            del atomic_structure.aarontools_filereader
            atomic_structure.session.chimaaron_frequency_file_manager.triggers.activate_trigger(FREQ_FILE_REMOVED, [atomic_structure])
    
    def refresh_chix_connected(self, atomic_structure, sanity_check=True):
        """updates atomic_structure's bonds to match self's connectivity
        sanity_check - bool; check to make sure atomic_structure corresponds to self"""
        if sanity_check:
            diff = self.difference(atomic_structure)
            for key in diff:
                if len(diff[key]) != 0:
                    raise Exception("ResidueCollection does not correspond to AtomicStructure: \n%s\n\n%s" % \
                        (repr(self), repr(ResidueCollection(atomic_structure))))
                    
        #for bond in atomic_structure.bonds:
        #    bond.delete()
            
        known_bonds = []
        for i, aaron_atom1 in enumerate(self.atoms):
            atom1 = [atom for atom in atomic_structure.atoms if aaron_atom1.chix_atom == atom][0]
            for aaron_atom2 in aaron_atom1.connected:
                if sorted((aaron_atom1, aaron_atom2,)) in known_bonds:
                    continue
                
                known_bonds.append(sorted((aaron_atom1, aaron_atom2,)))

                atom2 = [atom for atom in atomic_structure.atoms if atom == aaron_atom2.chix_atom][0]

                ##this doesn't work for some reason?
                #if any([atom2 in bond.atoms for bond in atom1.bonds]):
                #    continue
                
                try:
                    new_bond = atomic_structure.new_bond(atom1, atom2)
                                        
                    if any([aaron_atom.element in TMETAL for aaron_atom in [aaron_atom1, aaron_atom2]]):
                        pbg = atomic_structure.pseudobond_group(atomic_structure.PBG_METAL_COORDINATION, create_type='normal') 
                        pbg.new_pseudobond(atom1, atom2)
                        new_bond.display = False        
                except:
                    pass

    def get_chimera(self, session, coordsets=False, filereader=None):
        """returns a chimerax equivalent of self"""
        struc = AtomicStructure(session, name=self.name)
        struc.comment = self.comment
        
        self.update_chix(struc)

        if coordsets:
            #make a trajectory
            if filereader is None:
                #list of geometries was given
                #each geometry is a different frame in the trajectory
                coordsets = np.zeros((len(geom_list), len(self.atoms), 3))
                for i, g in geom_list:
                    coordsets[i] = g.coords()
                    
            else:
                #filereader was given
                #each list of atoms in filereader.all_geom is a frame in the trajectory
                coordsets = np.zeros((len(filereader.all_geom), len(self.atoms), 3))
                for i, all_geom in enumerate(filereader.all_geom):
                    if not all([isinstance(a, Atom) for a in all_geom]):
                        atom_list = [l for l in all_geom if all([isinstance(a, Atom) for a in l])][0]
                    else:
                        atom_list = all_geom
                    for j, atom in enumerate(atom_list):
                        coordsets[i][j] = atom.coords
            
            #replace previous coordinates
            #this matters when a filereader is given because the
            #geometry created from a filereader (which was probably passed as geom)
            #is the last geometry in the log or xyz file
            struc.add_coordsets(coordsets, replace=True)
            
        #associate filereader with structure
        if filereader is not None:
            struc.aarontools_filereader = filereader

        return struc