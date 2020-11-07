import os

from AaronTools.utils.utils import combine_dicts
from AaronTools.atoms import Atom
from AaronTools.geometry import Geometry
from AaronTools.theory import *
from AaronTools.const import UNIT

from chimerax.atomic import AtomicStructure
from chimerax.atomic import Atom as ChixAtom

from SEQCROW.finders import AtomSpec

class SEQCROW_Theory(Theory):
    def write_gaussian_input(self, fname=None, **other_kw_dict):
        geometry = self.geometry
        warnings = []
        header, header_warnings = self.make_header(geometry, 
                                                   style='gaussian', 
                                                   return_warnings=True, 
                                                   **other_kw_dict)
        
        warnings.extend(header_warnings)

        s = header

        if geometry is not None:
            if isinstance(geometry, Geometry):
                for atom in geometry.atoms:
                    s += "%-2s %13.6f %13.6f %13.6f\n" % (atom.element, *atom.coords)
            elif isinstance(geometry, AtomicStructure):
                for atom in geometry.atoms:
                    s += "%-2s %12.6f %12.6f %12.6f\n" % (atom.element.name, *atom.coord)
        else:
            s += "None\n"

        footer, footer_warnings = self.make_footer(geometry, 
                                                   style='gaussian', 
                                                   return_warnings=True, 
                                                   **other_kw_dict)
        warnings.extend(footer_warnings)
        
        s += footer
        
        if fname is not None:
            with open(fname, "w") as f:
                f.write(s)
        
        warnings = [warning for warning in warnings if warning is not None]

        return s, warnings

    def write_orca_input(self, fname=None, **other_kw_dict):
        geometry = self.geometry
        warnings = []
        
        header, header_warnings = self.make_header(geometry,
                                                   style='orca', 
                                                   return_warnings=True, 
                                                   **other_kw_dict)
        
        warnings.extend(header_warnings)

        s = header
    
        if geometry is not None:
            if isinstance(geometry, AtomicStructure):
                for atom in geometry.atoms:
                    s += "%-2s %12.6f %12.6f %12.6f\n" % (atom.element.name, *atom.coord)

            elif isinstance(geometry, Geometry):
                for atom in geometry.atoms:
                    s += "%-2s %12.6f %12.6f %12.6f\n" % (atom.element, *atom.coords)

            s += "*\n"

        if fname is not None:
            with open(fname, "w") as f:
                f.write(s)

        warnings = [warning for warning in warnings if warning is not None]

        return s, warnings

    def write_psi4_input(self, fname=None, monomers=None, **other_kw_dict):
        geometry = self.geometry
        warnings = []
        
        header, use_bohr, header_warnings = self.make_header(geometry, 
                                                             style='psi4', 
                                                             return_warnings=True, 
                                                             **other_kw_dict)
        
        warnings.extend(header_warnings)

        s = header

        if geometry is not None:
            if self.method.sapt:
                atoms_not_in_monomer = [a for a in geometry.atoms]
                for monomer, charge, mult in zip(monomers, self.charge[1:], self.multiplicity[1:]):
                    s += "--\n"
                    s += "%2i %i\n" % (charge, mult)
                    if isinstance(self.geometry, AtomicStructure):
                        for atom in monomer:
                            if atom in atoms_not_in_monomer:
                                atoms_not_in_monomer.remove(atom)
                            
                            if use_bohr:
                                #this is the angstrom-bohr conversion that psi4 uses
                                coords = [x / UNIT.A0_TO_BOHR for x in atom.coord]
                            else:
                                coords = atom.coord
                            s += "%-2s %12.6f %12.6f %12.6f\n" % (atom.element.name, *coords)
                
                    elif isinstance(self.geometry, Geometry):
                        for atom in monomer:
                            atoms_not_in_monomer.remove(atom)
                            if isinstance(atom, ChixAtom):
                                atom = self.geometry.find_exact(AtomSpec(atom.atomspec))[0]
                            if use_bohr:
                                coords = [x / UNIT.A0_TO_BOHR for x in atom.coords]
                            else:
                                coords = atom.coords
                            s += "%-2s %12.6f %12.6f %12.6f\n" % (atom.element, *coords)
                
                if len(atoms_not_in_monomer) > 0:
                    warnings.append("there are %i atoms not in a monomer" % len(atoms_not_in_monomer))
                
            else:
                if isinstance(self.geometry, AtomicStructure):
                    for atom in self.geometry.atoms:
                        if use_bohr:
                            #this is the angstrom-bohr conversion that psi4 uses
                            coords = [x / UNIT.A0_TO_BOHR for x in atom.coord]
                        else:
                            coords = atom.coord
                        s += "%-2s %12.6f %12.6f %12.6f\n" % (atom.element.name, *coords)
                
                elif isinstance(self.geometry, Geometry):
                    for atom in self.geometry.atoms:
                        if use_bohr:
                            coords = [x / UNIT.A0_TO_BOHR for x in atom.coords]
                        else:
                            coords = atom.coords
                        s += "%-2s %12.6f %12.6f %12.6f\n" % (atom.element, *coords)

        footer, footer_warnings = self.make_footer(geometry,
                                                   style='psi4', 
                                                   return_warnings=True, 
                                                   **other_kw_dict)
        warnings.extend(footer_warnings)
        
        s += footer
        
        if fname is not None:
            with open(fname, "w") as f:
                f.write(s)
        
        warnings = [warning for warning in warnings if warning is not None]

        return s, warnings

    def get_gaussian_json(self, **other_kw_dict):
        out = {}

        header = self.make_header(self.geometry,
                                  style='gaussian', 
                                  return_warnings=False, 
                                  **other_kw_dict)
        
        footer = self.make_footer(self.geometry,
                                  style='gaussian', 
                                  return_warnings=False, 
                                  **other_kw_dict)
        
        out['header'] = header
        out['footer'] = footer
        
        atoms = []
        for atom in self.geometry.atoms:
            if isinstance(self.geometry, AtomicStructure):
                atoms.append("%-2s %13.6f %13.6f %13.6f\n" % (atom.element.name, *atom.coord))
            
            elif isinstance(self.geometry, Geometry):
                atoms.append("%-2s %13.6f %13.6f %13.6f\n" % (atom.element, *atom.coords))
        
        out['geometry'] = atoms

        return out

    def get_orca_json(self, **other_kw_dict):
        out = {}
        header = self.make_header(self.geometry,
                                  style='orca', 
                                  return_warnings=False, 
                                  **other_kw_dict)

        out['header'] = header
        
        atoms = []
        for atom in self.geometry.atoms:
            if isinstance(self.geometry, AtomicStructure):
                atoms.append("%-2s %13.6f %13.6f %13.6f\n" % (atom.element.name, *atom.coord))
            
            elif isinstance(self.geometry, Geometry):
                atoms.append("%-2s %13.6f %13.6f %13.6f\n" % (atom.element, *atom.coords))
        
        out['geometry'] = atoms
  
        return out

    def get_psi4_json(self, **other_kw_dict):
        out = {}

        header, use_bohr = self.make_header(self.geometry,
                                            style='psi4', 
                                            return_warnings=False, 
                                            **other_kw_dict)
        
        footer = self.make_footer(self.geometry,
                                  style='psi4', 
                                  return_warnings=False, 
                                  **other_kw_dict)
        
        out['header'] = header
        out['footer'] = footer
        
        atoms = []
        for atom in self.geometry.atoms:
            if isinstance(self.geometry, AtomicStructure):
                coords = atom.coord
                ele = atom.element.name
            elif isinstance(self.geometry, Geometry):
                coords = atom.coords
                ele = atom.element
            
            if use_bohr:
                coords /= UNIT.A0_TO_BOHR
            
            atoms.append("%-2s %13.6f %13.6f %13.6f\n" % (ele, *coords))
        
        out['geometry'] = atoms

        return out

    @classmethod
    def gaussian_input_from_dict(cls, json_dict, fname=None):
        """write gaussian input file to fname using info in dict
        any keys (self.GAUSSIAN_*) should be strings instead of integers"""
        s = ""

        s += json_dict['header']

        if json_dict['geometry'] is not None:
            atoms = []
            for atom in json_dict['geometry']:
                atom_info = atom.split()
                atoms.append(Atom(element=atom_info[0], coords=[float(x) for x in atom_info[1:]]))
            
            geometry = Geometry(atoms)

            for atom in geometry.atoms:
                s += "%-2s %13.6f %13.6f %13.6f\n" % (atom.element, *atom.coords)

        s += json_dict['footer']

        if fname is not None:
            with open(fname, "w") as f:
                f.write(s)

        return s

    @classmethod
    def orca_input_from_dict(cls, json_dict, fname=None):
        """write orca input file to fname using info in dict
        any keys (self.ORCA_*) should be strings instead of integers"""

        s = ""
        
        s += json_dict['header']

        atoms = []
        for atom in json_dict['geometry']:
            atom_info = atom.split()
            atoms.append(Atom(element=atom_info[0], coords=[float(x) for x in atom_info[1:]]))
        
        geometry = Geometry(atoms)

        for atom in geometry.atoms:
            s += "%-2s %12.6f %12.6f %12.6f\n" % (atom.element, *atom.coords)

        s += "*\n"

        if fname is not None:
            with open(fname, "w") as f:
                f.write(s)

        return s

    @classmethod
    def psi4_input_from_dict(cls, json_dict, fname=None):        
        s = ""
        
        s += json_dict['header']

        atoms = []
        for atom in json_dict['geometry']:
            atom_info = atom.split()
            atoms.append(Atom(element=atom_info[0], coords=[float(x) for x in atom_info[1:]]))
        
        geometry = Geometry(atoms)

        for atom in geometry.atoms:
            if use_bohr:
                coords = [x / 0.52917720859 for x in atom.coords]
            else:
                coords = atom.coords
            s += "%-2s %12.6f %12.6f %12.6f\n" % (atom.element, *coords)

        s += json_dict['footer']

        if fname is not None:
            with open(fname, "w") as f:
                f.write(s)

        return s


class SEQCROW_Basis(Basis):
    def refresh_elements(self, geometry):
        if isinstance(geometry, Geometry):
            super().refresh_elements(geometry)
        elif geometry is not None:
            self.elements = set([str(atom.element) for atom in geometry.atoms if str(atom.element) in self.ele_selection])


class SEQCROW_ECP(SEQCROW_Basis, ECP):
    def __init__(self, *args, **kwargs):
        super(SEQCROW_Basis, self).__init__(*args, **kwargs)
        super(ECP, self).__init__(*args, **kwargs)
        
        if not hasattr(self.ele_selection, "__iter__"):
            self.ele_selection = [self.ele_selection]
        
    def refresh_elements(self, geometry):
        if isinstance(geometry, Geometry):
            super().refresh_elements(geometry)
        elif geometry is not None:
            self.elements = set([str(atom.element) for atom in geometry.atoms if str(atom.element) in self.ele_selection])

 
