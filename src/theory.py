import os

from AaronTools.utils.utils import combine_dicts
from AaronTools.atoms import Atom
from AaronTools.geometry import Geometry
from AaronTools.theory import *
from AaronTools.const import UNIT, ELEMENTS

from chimerax.atomic import AtomicStructure
from chimerax.atomic import Atom as ChixAtom

from SEQCROW.finders import AtomSpec

class SEQCROW_Theory(Theory):
    @staticmethod
    def get_gaussian_json(theory, **other_kw_dict):
        out = {}

        header = theory.make_header(theory.geometry,
                                  style='gaussian', 
                                  return_warnings=False, 
                                  **other_kw_dict)
        
        footer = theory.make_footer(theory.geometry,
                                  style='gaussian', 
                                  return_warnings=False, 
                                  **other_kw_dict)
        
        out['header'] = header
        out['footer'] = footer
        
        atoms = []
        for atom in theory.geometry.atoms:
            if isinstance(theory.geometry, AtomicStructure):
                atoms.append("%-2s %13.6f %13.6f %13.6f\n" % (atom.element.name, *atom.coord))
            
            elif isinstance(theory.geometry, Geometry):
                atoms.append("%-2s %13.6f %13.6f %13.6f\n" % (atom.element, *atom.coords))
        
        out['geometry'] = atoms

        return out

    @staticmethod
    def get_orca_json(theory, **other_kw_dict):
        out = {}
        header = theory.make_header(theory.geometry,
                                  style='orca', 
                                  return_warnings=False, 
                                  **other_kw_dict)

        out['header'] = header
        
        atoms = []
        for atom in theory.geometry.atoms:
            if isinstance(theory.geometry, AtomicStructure):
                atoms.append("%-2s %13.6f %13.6f %13.6f\n" % (atom.element.name, *atom.coord))
            
            elif isinstance(theory.geometry, Geometry):
                atoms.append("%-2s %13.6f %13.6f %13.6f\n" % (atom.element, *atom.coords))
        
        out['geometry'] = atoms
  
        return out

    @staticmethod
    def get_psi4_json(theory, **other_kw_dict):
        out = {}

        header, use_bohr = theory.make_header(theory.geometry,
                                            style='psi4', 
                                            return_warnings=False, 
                                            **other_kw_dict)
        
        footer = theory.make_footer(theory.geometry,
                                  style='psi4', 
                                  return_warnings=False, 
                                  **other_kw_dict)
        
        out['header'] = header
        out['footer'] = footer
        
        atoms = []
        for atom in theory.geometry.atoms:
            if isinstance(theory.geometry, AtomicStructure):
                coords = atom.coord
                ele = atom.element.name
            elif isinstance(theory.geometry, Geometry):
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