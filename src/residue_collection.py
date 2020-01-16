import numpy as np

import re

from AaronTools.atoms import Atom
from AaronTools.catalyst import Catalyst
from AaronTools.const import TMETAL
from AaronTools.geometry import Geometry

from chimerax.atomic import AtomicStructure
from chimerax.atomic import Atom as ChixAtom

class ChimAtom(Atom):
    def __init__(self, atom=None, *args, serial_number=None, atomspec=None, **kwargs):
        """atom to go between chimerax Atom and AaronTools Atom"""
        if isinstance(atom, ChixAtom):
            element = str(atom.element)
            coords = atom.coord
            name = atom.name
            
            super().__init__(*args, name=atom.name, element=element, coords=coords, **kwargs)
            
            self.add_tag(str(atom.atomspec))
            self.atomspec = str(atom.atomspec)
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
        a = re.sub(r'[A-Za-z]', '', self.name).split(".")
        b = re.sub(r'[A-Za-z]', '', other.name).split(".")
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
        rv = re.sub(r'[A-Za-z]', '', self.name).split(".")
        if len(rv) == 0:
            return float(0)
        if len(rv) == 1:
            return float(rv[0])
        rv = "{}.{}".format(rv[0], rv[1])
        return float(rv)
        

class Residue(Geometry):
    def __init__(self, geom, resnum=None, name="UNK", **kwargs):
        super().__init__(geom, name=name, **kwargs)
        self.resnum = resnum

    def get_element_count(self):
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
            super().__init__(molecule, refresh_connected=refresh_connected, **kwargs)
                
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
        
        elif isinstance(molecule, Geometry):
            super().__init__(molecule, refresh_connected=refresh_connected, **kwargs)
                
            self.residues = [Residue(molecule, resnum=1, name="UNK", refresh_connected=refresh_connected)]
            self.session = None
            self._atom_update()
            return
        
        if not isinstance(molecule, AtomicStructure):
            raise NotImplementedError("molecule must be a chimerax AtomicStructure or a list of AtomicStructures")
        else:
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
            
            super().__init__(all_atoms, name=molecule.name, refresh_connected=refresh_connected, **kwargs)
        
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
        
            self.session = molecule.session
    
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
        for i in range(0, len(self.atoms)):
            if not isinstance(self.atoms[i], ChimAtom):
                chim_atoms[self.atoms[i]] = ChimAtom(atom=self.atoms[i])
                
        if hasattr(self, "residues"):
            for residue in self.residues:
                for i, atom in enumerate(residue.atoms):
                    if not isinstance(atom, ChimAtom):
                        residue.atoms[i] = chim_atoms[atom]
                    
            self.atoms = []
            for residue in self.residues:
                self.atoms.extend(residue.atoms)
        else:
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

    def find_residue(self, target):
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
        
        atom_dict = {}
        for atom in atomic_structure.atoms:
            if str(atom.element) not in atom_dict:
                atom_dict[str(atom.element)] = 1
            else:
                atom_dict[str(atom.element)] += 1
                
            atom.name = "%s%i" % (str(atom.element), atom_dict[str(atom.element)])

        for atom in differences['chix missing']:
            if atom.element not in atom_dict:
                atom_dict[atom.element] = 1
            else:
                atom_dict[atom.element] += 1
                
            self_res = self.find_residue(atom)

            if len(self_res) != 1:
                raise LookupError("multiple or no residues found for %s" % atom)
            else:
                self_res = self_res[0]
            
            res = [residue for residue in atomic_structure.residues if residue.number == self_res.resnum and residue.name == self_res.name]
            if len(res) != 1:
                res = atomic_structure.new_residue(self_res.name, "a", 1)
            else:
                res = res[0]
                
            new_atom = atomic_structure.new_atom("%s%i" % (atom.element, atom_dict[atom.element]), atom.element)
            new_atom.coord = atom.coords

            atom.chix_atom = new_atom

            res.add_atom(new_atom)
        
        for atom in self.atoms:
            atom.chix_atom.coord = atom.coords
        
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
                    
        for bond in atomic_structure.bonds:
            bond.delete()
            
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
                        #TODO:
                        #figure out what the create_type parameter does
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

        #keep bonding consistent with AaronTools
        #self.refresh_chix_connected(struc, sanity_check=False)

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