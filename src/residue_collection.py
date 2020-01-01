import numpy as np

from AaronTools.atoms import Atom
from AaronTools.catalyst import Catalyst
from AaronTools.const import TMETAL
from AaronTools.geometry import Geometry
from chimerax.atomic.structure import AtomicStructure

class ResidueCollection(Geometry):
    """geometry object used for ChimAARON to easily convert to AaronTools but keep residue info"""
    def __init__(self, molecule):
        """molecule     - chimerax AtomicStructure or [AtomicStructure]"""
        if not isinstance(molecule, AtomicStructure) and not hasattr(molecule, "__iter__"):
            raise NotImplementedError("molecule must be a chimerax AtomicStructure or a list of AtomicStructures")
        
        elif isinstance(molecule, AtomicStructure):
            molecules = [molecule]
        else:
            molecules = molecule
        
        for molecule in molecules:
            #convert chimerax stuff to AaronTools
            aaron_atoms = []
            for i, residue in enumerate(molecule.residues):
                resname = residue.name
                for atom in residue.atoms:
                    if not atom.deleted:
                        element = str(atom.element)
                        coords = atom.coord
                        name = atom.name
                        
                        aaron_atom = Atom(name=str(atom.serial_number + 1), element=element, coords=coords)
                        aaron_atom.resname = resname
                        aaron_atom.resnum = i
                        aaron_atom.add_tag(atom.name)
                        aaron_atom.add_tag(str(atom.atomspec))
                        aaron_atom.add_tag(resname)
                        
                        aaron_atoms.append(aaron_atom)

        super().__init__(structure=aaron_atoms, name=molecule.name, comment=molecule.comment, refresh_connected=False)

        for molecule in molecules:
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
    
    def __repr__(self):
        s = ""
        for atom in self.atoms:
            s += "%s   %s\n" % (repr(atom), atom.atomspec)
            
        return s.strip()
    
    def write(self, *args, targets=None, ignore_atoms=None, **kwargs):
        """write geometry to file
        targets         - [Atom] atoms to write, default is all non-ghost atoms
        ignore_atoms    - [Atom] atoms to ignore, default is ghost atoms (False will write ghost atoms)"""
        if targets is None and ignore_atoms is None:
            try:
                ignore_atoms = self.find('ghost')
            except:
                ignore_atoms = []
            atoms = [atom for atom in self.atoms if atom not in ignore_atoms]
        elif targets is not None and ignore_atoms is None:
            atoms = self.find(targets)
        elif targets is None and ignore_atoms is not None:
            try:
                ignore_atoms = self.file(ignore_atoms)
            except:
                ignore_atoms = []
            atoms = [atom for atom in self.atoms if atom not in ignore_atoms]
        else:
            raise NotImplementedError("targets and ignore_atoms combination is not allowed")
        
        #create a scratch geometry with only the requested atoms
        temp = Geometry(atoms, comment=self.comment, name=self.name)
            
        out = temp.write(*args, **kwargs)
        
        return out

    @staticmethod
    def get_chimera(session, geom, coordsets=False, filereader=None):
        """returns a chimerax equivalent of an AaronTools Geometry
        supported geometry subclasses include:
            Catalyst - adds residues or ligand, substrate, and center; adds atom tags for substituents
        """
        
        #a list of geometries can translate to a trajectory
        if isinstance(geom, list):
            geom_list = geom
            geom = geom_list[0]
            
        if isinstance(geom, Catalyst):
            i = 1
            for component in geom.components:
                for part in geom.components[component]:
                    for atom in part.atoms:
                        if component == 'ligand':
                            atom.resname = "LIG"
                        elif component == 'substrate':
                            atom.resname = "SUB"
                        
                        atom.resnum = i
                    
                    if hasattr(part, "substituents"):
                        for sub in part.substituents:
                            for atom in sub.atoms:
                                atom.substituent = sub.name
                            
                            sub.end.end = sub.name

                    i += 1

            for atom in geom.center:
                atom.resname = "CENT"
                atom.resnum = i

        elif isinstance(geom, Geometry):
            if not any(hasattr(atom, "resname") for atom in geom.atoms):
                atoms_with_resname = [atom for atom in geom.atoms if hasattr(atom, "resname")]
                if any(atom.resname == "UNK" for atom in atoms_with_resname):
                    i = atoms_with_resname[0].resnum
                else:
                    i = 1
                    atoms_with_resnum = [atom for atom in geom.atoms if hasattr(atom, "resnum")]
                    while any(atom.resnum == i for atom in atoms_with_resnum):
                        i += 1
    
                for atom in geom.atoms:
                    if not hasattr(atom, "resname"):
                        atom.resnum = i
                        atom.resname = "UNK"
        
        struc = AtomicStructure(session, name=geom.name)
        struc.comment = geom.comment
        
        residue = None
        resnum = None
        for aaron_atom in geom.atoms:           
            #add all the new residues
            if residue is None or aaron_atom.resnum != resnum:
                residue = struc.new_residue(aaron_atom.resname, 'aarontools', 1)
                elements = {}
                resnum = aaron_atom.resnum
            
            if aaron_atom.element not in elements:
                elements[aaron_atom.element] = 1
            else:
                elements[aaron_atom.element] += 1
            

            atom = struc.new_atom("%s%i" % (aaron_atom.element, elements[aaron_atom.element]), aaron_atom.element)
            atom.coord = aaron_atom.coords
            aaron_atom.add_tag(atom.name)

            #transfer some more AaronTools info that might be present
            if hasattr(aaron_atom, "substituent"):
                atom.substituent = aaron_atom.substituent
                
            if hasattr(aaron_atom, "end"):
                atom.end = aaron_atom.end
            
            atom.serial_number = geom.atoms.index(aaron_atom) + 1
            
            residue.add_atom(atom)
        
        #keep bonding consistent with AaronTools
        known_bonds = []
        for i, aaron_atom1 in enumerate(geom.atoms):
            atom1 = struc.atoms[i]
            for aaron_atom2 in aaron_atom1.connected:
                if sorted((aaron_atom1, aaron_atom2,)) in known_bonds:
                    continue
                
                known_bonds.append(sorted((aaron_atom1, aaron_atom2,)))
                                
                atom2 = struc.atoms[geom.atoms.index(aaron_atom2)]

                ##this doesn't work for some reason?
                #if any([atom2 in bond.atoms for bond in atom1.bonds]):
                #    continue

                new_bond = struc.new_bond(atom1, atom2)
                                    
                if any([aaron_atom.element in TMETAL for aaron_atom in [aaron_atom1, aaron_atom2]]):
                    #TODO:
                    #figure out what the create_type parameter does
                    pbg = struc.pseudobond_group(struc.PBG_METAL_COORDINATION, create_type='normal') 
                    pbg.new_pseudobond(atom1, atom2)
                    new_bond.display = False

        if coordsets:
            #make a trajectory
            if filereader is None:
                #list of geometries was given
                #each geometry is a different frame in the trajectory
                coordsets = np.zeros((len(geom_list), len(geom.atoms), 3))
                for i, g in geom_list:
                    coordsets[i] = g.coords()
                    
            else:
                #filereader was given
                #each list of atoms in filereader.all_geom is a frame in the trajectory
                coordsets = np.zeros((len(filereader.all_geom), len(geom.atoms), 3))
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

        return struc