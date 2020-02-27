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

from warnings import warn

def fromChimAtom(atom=None, *args, serial_number=None, atomspec=None, **kwargs):
    """get AaronTools Atom object from ChimeraX Atom"""
    aarontools_atom = Atom(*args, name=str(atom.serial_number), element=str(atom.element), coords=atom.coord, **kwargs)
    
    aarontools_atom.add_tag(atom.atomspec)
    aarontools_atom.atomspec = atom.atomspec
    aarontools_atom.serial_number = atom.serial_number
    aarontools_atom.chix_atom = atom

    return aarontools_atom
   


class Residue(Geometry):
    """Residue is an intermediary between chimerax Residues and AaronTools Geometrys
    Residue has the following attributes:
    resnum      - same as chimerax Residue.number
    name        - same as chimerax Residue.name
    """
    def __init__(self, geom, resnum=None, atomspec=None, name="UNK", **kwargs):
        super().__init__(geom, name=name, **kwargs)
        self.resnum = resnum
        self.atomspec = atomspec

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
            return
        
        elif isinstance(molecule, AtomicStructure):
            self.residues = []
            
            #convert chimerax stuff to AaronTools
            all_atoms = []
            for i, residue in enumerate(molecule.residues):
                aaron_atoms = []
                for atom in residue.atoms:
                    if not atom.deleted:                      
                        aaron_atom = fromChimAtom(atom=atom)
                        aaron_atoms.append(aaron_atom)
    
                self.residues.append(Residue(aaron_atoms, \
                                        name=residue.name, \
                                        resnum=residue.number, \
                                        atomspec=residue.atomspec, \
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
            
            #add bonds to metals
            tm_bonds = molecule.pseudobond_group(molecule.PBG_METAL_COORDINATION, create_type=None)
            if tm_bonds is not None:
                for pseudobond in tm_bonds.pseudobonds:
                    atom1, atom2 = pseudobond.atoms
                    aaron_atom1 = self.find(atom1.atomspec)[0]
                    aaron_atom2 = self.find(atom2.atomspec)[0]
                    aaron_atom1.connected.add(aaron_atom2)
                    aaron_atom2.connected.add(aaron_atom1)
                    
        else:
            #assume whatever we got is something AaronTools can turn into a Geometry
            super().__init__(molecule, refresh_connected=refresh_connected, **kwargs)
            if "comment" in kwargs:
                self.residues = [Residue(molecule, resnum=1, name="UNK", refresh_connected=refresh_connected, comment=kwargs['comment'])]
            elif hasattr(molecule, "comment"):
                self.residues = [Residue(molecule, resnum=1, name="UNK", refresh_connected=refresh_connected, comment=molecule.comment)]
            else:
                self.residues = [Residue(molecule, resnum=1, name="UNK", refresh_connected=refresh_connected)]
            return
  
    def _atom_update(self):
        self.atoms = []
        for res in self.residues:
            self.atoms.extend(res.atoms)
  
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
        """update chimerax atomic structure to match self
        may also change residue numbers for self"""
        differences = self.difference(atomic_structure)
        
        for atom in differences['geom missing']:
            atom.delete()

        for residue in self.residues:
            res = [res for res in atomic_structure.residues if res.number == residue.resnum and res.name == residue.name]
            if len(res) == 0:
                res = atomic_structure.new_residue(residue.name, "a", residue.resnum)
            else:
                res = res[0]
            for atom in residue.atoms:
                if atom in differences['chix missing']:                  
                    i = 1
                    atom_name = "%s%i" % (atom.element, i)
                    while any([chix_atom.name == "%s%i" % (atom.element, i) for chix_atom in res.atoms]):
                        i += 1
                        atom_name = "%s%i" % (atom.element, i)
                    
                    new_atom = atomic_structure.new_atom(atom_name, atom.element)
                    new_atom.draw_mode = ChixAtom.STICK_STYLE
                    new_atom.color = element_color(new_atom.element.number)
                    
                    res.add_atom(new_atom)
                    
                    atom.chix_atom = new_atom
        
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
                    
        #for bond in atomic_structure.bonds:
        #    bond.delete()
            
        known_bonds = []
        for i, aaron_atom1 in enumerate(self.atoms):
            atom1 = [atom for atom in atomic_structure.atoms if aaron_atom1.chix_atom == atom][0]
            for aaron_atom2 in aaron_atom1.connected:
                if sorted((aaron_atom1, aaron_atom2,)) in known_bonds:
                    continue
                
                known_bonds.append(sorted((aaron_atom1, aaron_atom2,)))

                atom2 = [atom for atom in atomic_structure.atoms if atom == aaron_atom2.chix_atom]
                if len(atom2) > 0:
                    atom2 = atom2[0]
                else:
                    #we cannot draw a bond to an atom that is not in the residue
                    #this could happen when previewing a substituent or w/e with the libadd tool
                    continue

                ##this doesn't work for some reason?
                #if any([atom2 in bond.atoms for bond in atom1.bonds]):
                #    continue
                
                try:
                    new_bond = atomic_structure.new_bond(atom1, atom2)
                                        
                    if any([aaron_atom.element in TMETAL for aaron_atom in [aaron_atom1, aaron_atom2]]):
                        pbg = atomic_structure.pseudobond_group(atomic_structure.PBG_METAL_COORDINATION, create_type='normal') 
                        pbg.new_pseudobond(atom1, atom2)
                        new_bond.delete()
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
                if filereader.all_geom is None:
                    warn("coordsets requested, but the file contains one or fewer sets of coordinates")
                    coordsets = struc.coordset(1)
                else:
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