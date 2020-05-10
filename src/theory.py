import os

from SEQCROW.utils import combine_dicts

KNOWN_SEMI_EMPIRICAL = ["AM1", "PM3", "PM6", "PM7", "HF-3c"]


class Method:
    """a Method object can be used to create an input file for different QM software
    The creation of a Method object does not depend on the specific QM software - that is determined when the file is written
    valid initialization key words are:
    structure               -   AaronTools Geometry or ChimeraX AtomicStructure
    charge                  -   total charge
    multiplicity            -   electronic multiplicity
    
    functional              -   Functional object
    basis                   -   BasisSet object
    constraints             -   dictionary of bond, angle, and torsional constraints (keys: atoms, bonds, angles, torsions)
                                    currently, only atoms and bonds are enabled. bonds are only enabled if structure is an AtomicStructure.
    empirical_dispersion    -   EmpiricalDispersion object
    grid                    -   IntegrationGrid object
    
    comment                 -   comment
    
    memory                  -   allocated memory (GB)
    processors              -   allocated cores
        """
    
    ORCA_ROUTE = 1
    ORCA_BLOCKS = 2
    ORCA_COORDINATES = 3
    ORCA_COMMENT = 4
    
    GAUSSIAN_PRE_ROUTE = 1 #can be used for things like %chk=some.chk
    GAUSSIAN_ROUTE = 2 #route specifies most options, e.g. #n B3LYP/3-21G opt 
    GAUSSIAN_COORDINATES = 3 #coordinate section
    GAUSSIAN_CONSTRAINTS = 4 #constraints section (e.g. B 1 2 F)
    GAUSSIAN_GEN_BASIS = 5 #gen or genecp basis section
    GAUSSIAN_GEN_ECP = 6 #genecp ECP section
    GAUSSIAN_POST = 7 #after everything else (e.g. NBO options)
    GAUSSIAN_COMMENT = 8 #comment line after the route

    ACCEPTED_INIT_KW = ['functional', \
                        'basis', \
                        'structure', \
                        'constraints', \
                        'memory', \
                        'processors', \
                        'empirical_dispersion', \
                        'comment', \
                        'charge', \
                        'multiplicity', \
                        'grid']

    def __init__(self, **kw):
        for key in self.ACCEPTED_INIT_KW:
            if key in kw:
                #print("%s in kw" % key)
                self.__setattr__(key, kw[key])
            else:
                #print("%s not in kw" % key)
                self.__setattr__(key, None)

    def write_gaussian_input(self, other_kw_dict, fname=None):
        """write Gaussian09/16 input file
        other_kw_dict is a dictionary with file positions (using GAUSSIAN_* int map)
        corresponding to options/keywords
        returns warnings if a certain feature is not available in Gaussian"""

        from AaronTools.geometry import Geometry
        from chimerax.atomic import AtomicStructure

        warnings = []
        s = ""
        
        if self.processors is not None:
            s += "%%NProcShared=%i\n" % self.processors
            
        if self.memory is not None:
            s += "%%Mem=%iGB\n" % self.memory
        
        if self.GAUSSIAN_PRE_ROUTE in other_kw_dict:
            for key in other_kw_dict[self.GAUSSIAN_PRE_ROUTE]:
                s += "%%%s" % key
                if len(other_kw_dict[self.GAUSSIAN_PRE_ROUTE][key]) > 0:
                    s += "=%s" % ",".join(other_kw_dict[self.GAUSSIAN_PRE_ROUTE][key])

                if not s.endswith('\n'):
                    s += '\n'
        
        #start route line with functional
        func, warning = self.functional.get_gaussian09()
        if warning is not None:
            warnings.append(warning)
        s += "#n %s" % func
        if not self.functional.is_semiempirical:
            basis_info = self.basis.get_gaussian09_basis_info()
            basis_elements = self.basis.elements_in_basis
            #check if any element is in multiple basis sets
            for element in basis_elements:
                if basis_elements.count(element) > 1:
                    warnings.append("%s is in basis set multiple times" % element)
                    
            #check to make sure all elements have a basis set
            if self.structure is not None:
                if isinstance(self.structure, Geometry):
                    struc_elements = set([atom.element for atom in self.structure.atoms])
                elif isinstance(self.structure, AtomicStructure):
                    struc_elements = set(self.structure.atoms.elements.names)

                elements_wo_basis = []
                for ele in struc_elements:
                    if ele not in basis_elements:
                        elements_wo_basis.append(ele)
                        
                if len(elements_wo_basis) > 0:
                    warnings.append("no basis set for %s" % ", ".join(elements_wo_basis))
            
            if self.GAUSSIAN_ROUTE in basis_info:
                s += "%s" % basis_info[self.GAUSSIAN_ROUTE]
        
        s += " "
        
        if self.empirical_dispersion is not None:
            disp, warning = self.empirical_dispersion.get_gaussian09()
            s += disp + " "
            if warning is not None:
                warnings.append(warning)
        
        if self.grid is not None:
            grid, warning = self.grid.get_gaussian09()
            if warning is not None:
                warnings.append(warning)
            s += grid
            s += " "
        
        if self.GAUSSIAN_ROUTE in other_kw_dict:
            for option in other_kw_dict[self.GAUSSIAN_ROUTE]:
                s += option
                if len(other_kw_dict[self.GAUSSIAN_ROUTE][option]) > 0:
                    s += "=(%s)" % ",".join(other_kw_dict[self.GAUSSIAN_ROUTE][option])
                s += " "
        
        s += "\n\n"
        
        if self.GAUSSIAN_COMMENT in other_kw_dict:
            if len(other_kw_dict[self.GAUSSIAN_COMMENT]) > 0:
                #TODO: make it impossible to break up te comment with newlines
                s += "\n".join([x.rstrip() for x in other_kw_dict[self.GAUSSIAN_COMMENT]])
            else:
                s += "comment"
                
            if not s.endswith('\n'):
                s += '\n'
        
        else:
            if self.comment is None:
                s += "comment\n"
            else:
                s += "%s\n" % self.comment
            
        s += "\n"
        
        s += "%i %i\n" % (self.charge, self.multiplicity)
        if self.structure is not None:
            if self.constraints is not None and len(self.constraints['atoms']) > 0:
                if isinstance(self.structure, Geometry):
                    for atom in self.structure.atoms:
                        if atom in self.constraints['atoms']:
                            flag = -1
                        else:
                            flag = 0
                        s += "%-2s %2i %13.6f %13.6f %13.6f\n" % (atom.element, flag, *atom.coords)
                elif isinstance(self.structure, AtomicStructure):
                    for atom in self.structure.atoms:
                        if atom in self.constraints['atoms']:
                            flag = -1
                        else:
                            flag = 0
                        s += "%-2s %2i %12.6f %12.6f %12.6f\n" % (atom.element.name, flag, *atom.coord)
            
            else:    
                if isinstance(self.structure, Geometry):
                    for atom in self.structure.atoms:
                        s += "%-2s %13.6f %13.6f %13.6f\n" % (atom.element, *atom.coords)
                elif isinstance(self.structure, AtomicStructure):
                    for atom in self.structure.atoms:
                        s += "%-2s %12.6f %12.6f %12.6f\n" % (atom.element.name, *atom.coord)
        else:
            s += "None\n"
        
        s += "\n"
        
        if self.constraints is not None and self.structure is not None:
            for constraint in self.constraints['bonds']:
                atom1, atom2 = constraint
                ndx1 = self.structure.atoms.index(atom1) + 1
                ndx2 = self.structure.atoms.index(atom2) + 1
                s += "B %2i %2i F\n" % (ndx1, ndx2)

            for constraint in self.constraints['angles']:
                atom1, atom2, atom3 = constraint
                ndx1 = self.structure.atoms.index(atom1) + 1
                ndx2 = self.structure.atoms.index(atom2) + 1
                ndx3 = self.structure.atoms.index(atom3) + 1
                s += "A %2i %2i %2i F\n" % (ndx1, ndx2, ndx3)
            
            for constraint in self.constraints['torsions']:
                atom1, atom2, atom3, atom4 = constraint
                ndx1 = self.structure.atoms.index(atom1) + 1
                ndx2 = self.structure.atoms.index(atom2) + 1
                ndx3 = self.structure.atoms.index(atom3) + 1
                ndx4 = self.structure.atoms.index(atom4) + 1
                s += "D %2i %2i %2i %2i F\n" % (ndx1, ndx2, ndx3, ndx4)
                
            s += '\n'
        
        if not self.functional.is_semiempirical:
            if self.GAUSSIAN_GEN_BASIS in basis_info:
                s += basis_info[self.GAUSSIAN_GEN_BASIS]
            
                s += "\n"
            
            if self.GAUSSIAN_GEN_ECP in basis_info:
                s += basis_info[self.GAUSSIAN_GEN_ECP]
                
                s += '\n'
                
        if self.GAUSSIAN_POST in other_kw_dict:
            for item in other_kw_dict[self.GAUSSIAN_POST]:
                s += item
                s += " "
                
            s += '\n'
        
        s += '\n\n'
        
        if fname is not None:
            with open(fname, "w") as f:
                f.write(s)
                
        return s, warnings

    def write_orca_input(self, other_kw_dict, fname=None):
        """write Gaussian09/16 input file
        other_kw_dict is a dictionary with file positions (using GAUSSIAN_* int map)
        corresponding to options/keywords
        returns warnings if a certain feature is not available in Gaussian"""
        #TODO:
        #add constraints
        #allow structure to be Geometry
        #probably other stuff

        from AaronTools.geometry import Geometry
        from chimerax.atomic import AtomicStructure

        warnings = []
        
        if not self.functional.is_semiempirical:
            basis_info = self.basis.get_orca_basis_info()
            if self.structure is not None:
                if isinstance(self.structure, Geometry):
                    struc_elements = set([atom.element for atom in self.structure.atoms])
                elif isinstance(self.structure, AtomicStructure):
                    struc_elements = set(self.structure.atoms.elements.names)
            
                warning = self.basis.check_for_elements(struc_elements)
                if warning is not None:
                    warnings.append(warning)
        
        else:
            basis_info = {}
        
        combined_dict = combine_dicts(other_kw_dict, basis_info)

        if self.constraints is not None and self.structure is not None:
            if 'geom' not in combined_dict[self.ORCA_BLOCKS]:
                combined_dict[self.ORCA_BLOCKS]['geom'] = []

            combined_dict[self.ORCA_BLOCKS]['geom'].append("constraints")
            for constraint in self.constraints['atoms']:
                atom1 = constraint
                ndx1 = self.structure.atoms.index(atom1)
                s = "    {C %2i C}" % (ndx1)
                combined_dict[self.ORCA_BLOCKS]['geom'].append(s)

            for constraint in self.constraints['bonds']:
                atom1, atom2 = constraint
                ndx1 = self.structure.atoms.index(atom1)
                ndx2 = self.structure.atoms.index(atom2)
                s = "    {B %2i %2i C}" % (ndx1, ndx2)
                combined_dict[self.ORCA_BLOCKS]['geom'].append(s)

            for constraint in self.constraints['angles']:
                atom1, atom2, atom3 = constraint
                ndx1 = self.structure.atoms.index(atom1)
                ndx2 = self.structure.atoms.index(atom2)
                ndx3 = self.structure.atoms.index(atom3)
                s = "    {A %2i %2i %2i C}" % (ndx1, ndx2, ndx3)
                combined_dict[self.ORCA_BLOCKS]['geom'].append(s)

            for constraint in self.constraints['torsions']:
                atom1, atom2, atom3, atom4 = constraint
                ndx1 = self.structure.atoms.index(atom1)
                ndx2 = self.structure.atoms.index(atom2)
                ndx3 = self.structure.atoms.index(atom3)
                ndx4 = self.structure.atoms.index(atom4)
                s = "    {D %2i %2i %2i %2i C}" % (ndx1, ndx2, ndx3, ndx4)
                combined_dict[self.ORCA_BLOCKS]['geom'].append(s)

            combined_dict[self.ORCA_BLOCKS]['geom'].append("end")

        s = ""

        if self.ORCA_COMMENT in combined_dict:
            for comment in combined_dict[self.ORCA_COMMENT]:
                for line in comment.split('\n'):
                    s += "#%s\n" % line

        s += "!"
        if self.functional is not None:
            func, warning = self.functional.get_orca()
            if warning is not None:
                warnings.append(warning)
            s += " %s" % func
        

        if self.empirical_dispersion is not None:
            if not s.endswith(' '):
                s += " "
                
            dispersion, warning = self.empirical_dispersion.get_orca()
            if warning is not None:
                warnings.append(warning)

            s += "%s" % dispersion

        if self.grid is not None:
            if not s.endswith(' '):
                s += " "
                
            grid, warning = self.grid.get_orca()
            if warning is not None:
                warnings.append(warning)

            s += "%s" % grid

        if self.ORCA_ROUTE in combined_dict:
            if not s.endswith(' '):
                s += " "
                
                s += " ".join(combined_dict[self.ORCA_ROUTE])
        
        s += "\n"
        
        if self.processors is not None:
            s += "%%pal\n    nprocs %i\nend\n" % self.processors
            
            if self.memory is not None:
                s += "%%MaxCore %i\n" % (int(1000 * self.memory / self.processors))
        
        if self.ORCA_BLOCKS in combined_dict:
            for kw in combined_dict[self.ORCA_BLOCKS]:
                s += "%%%s\n" % kw
                for opt in combined_dict[self.ORCA_BLOCKS][kw]:
                    s += "    %s\n" % opt
                s += "end\n"
                
            s += "\n"
            
        s += "*xyz %i %i\n" % (self.charge, self.multiplicity)
        if self.structure is not None:
            if isinstance(self.structure, AtomicStructure):
                for atom in self.structure.atoms:
                    s += "%-2s %12.6f %12.6f %12.6f\n" % (atom.element.name, *atom.coord)
                    
        s += "*\n"
        
        if fname is not None:
            with open(fname, "w") as f:
                f.write(s)
                
        return s, warnings


class Functional:
    def __init__(self, name, is_semiempirical):
        self.name = name
        self.is_semiempirical = is_semiempirical

    def get_gaussian09(self):
        """maps proper functional name to one Gaussian accepts
        the following methods are available in other software, but not Gaussian:
        B3LYP (as originally reported)
        ωB97X-D3
        some others that hopefully won't be an issue"""
        if self.name == "ωB97X-D":
            return ("wB97XD", None)
        elif self.name == "Gaussian's B3LYP":
            return ("B3LYP", None)
        elif self.name == "B97X-D":
            return ("B97D", None)
        elif self.name.startswith("M06-"):
            return (self.name.replace("M06-", "M06", 1), None)
        
        #methods available in ORCA but not Gaussian
        elif self.name == "𝜔ωB97X-D3":
            return ("wB97XD", "ωB97X-D3 is not available in Gaussian, switching to ωB97X-D2")
        elif self.name == "B3LYP":
            return ("B3LYP", "Gaussian's B3LYP uses a different LDA")
        
        else:
            return self.name, None

    def get_orca(self):
        """maps proper functional name to one ORCA accepts"""
        if self.name == "ωB97X-D":
            return ("wB97X-D3", "ωB97X-D may refer to ωB97X-D2 or ωB97X-D3 - using the latter")
        elif self.name == "ωB97X-D3":
            return ("wB97X-D3", None)
        elif self.name == "B97-D":
            return ("B97-D2", "B97-D may refer to B97-D2 or B97-D3 - using the former")
        elif self.name == "Gaussian's B3LYP":
            return ("B3LYP/G", None)
        elif self.name == "M06-L":
            #why does M06-2X get a hyphen but not M06-L? 
            return ("M06L", None)
        
        else:
            return self.name.replace('ω', 'w'), None


class BasisSet:
    def __init__(self, basis, ecp=None):
        self.basis = basis
        self.ecp = ecp

    @property
    def elements_in_basis(self):
        elements = []
        if self.basis is not None:
            for basis in self.basis:
                elements.extend(basis.elements)
            
        return elements
    
    def get_gaussian09_basis_info(self):
        info = {}

        if self.basis is not None:
            if all([basis == self.basis[0] for basis in self.basis]) and not self.basis[0].user_defined and self.ecp is None:
                info[Method.GAUSSIAN_ROUTE] = "/%s" % Basis.map_gaussian09_basis(self.basis[0].name)
            else:
                if self.ecp is None:
                    info[Method.GAUSSIAN_ROUTE] = "/gen"
                else:
                    info[Method.GAUSSIAN_ROUTE] = "/genecp"
                    
                s = ""
                for basis in self.basis:
                    if len(basis.elements) > 0 and not basis.user_defined:
                        s += " ".join([ele for ele in basis.elements])
                        s += " 0\n"
                        s += Basis.map_gaussian09_basis(basis.get_basis_name())
                        s += "\n****\n"
                    
                for basis in self.basis:
                    if len(basis.elements) > 0:
                        if basis.user_defined:
                            if os.path.exists(basis.user_defined):
                                with open(basis.user_defined, "r") as f:
                                    lines = f.readlines()
                                
                                for line in lines:
                                    if not line.startswith('!') and not len(line.strip()) == 0:
                                        s += line
                            else:
                                s += "@%s\n" % basis.user_defined
                        
                    info[Method.GAUSSIAN_GEN_BASIS] = s
                    
        if self.ecp is not None:
            s = ""
            for basis in self.ecp:
                if len(basis.elements) > 0 and not basis.user_defined:
                    s += " ".join([ele for ele in basis.elements])
                    s += " 0\n"
                    s += Basis.map_gaussian09_basis(basis.get_basis_name())
                    s += "\n"
                
            for basis in self.ecp:
                if len(basis.elements) > 0:
                    if basis.user_defined:
                        if os.path.exists(basis.user_defined):
                            with open(basis.user_defined, "r") as f:
                                lines = f.readlines()
                            
                            for line in lines:
                                if not line.startswith('!') and not len(line.strip()) == 0:
                                    s += line
                        else:
                            s += "@%s\n" % basis.user_defined
                            
            info[Method.GAUSSIAN_GEN_ECP] = s
            
            if self.basis is None:
                info[Method.GAUSSIAN_ROUTE] = " Pseudo=Read"
            
        return info    
    
    def get_orca_basis_info(self):
        #TODO: warn if basis should be f12
        info = {Method.ORCA_BLOCKS:{'basis':[]}, Method.ORCA_ROUTE:[]}

        first_basis = []

        if self.basis is not None:
            for basis in self.basis:
                if len(basis.elements) > 0 and not basis.user_defined:
                    if basis.aux_type is None:
                        if basis.aux_type not in first_basis:
                            s = Basis.map_orca_basis(basis.get_basis_name())
                            info[Method.ORCA_ROUTE].append(s)
                            first_basis.append(basis.aux_type)
                            
                        else:
                            for ele in basis.elements:
                                s = "newGTO            %-2s " % ele
                                s += "\"%s\" end" % Basis.map_orca_basis(basis.get_basis_name())
                    
                                info[Method.ORCA_BLOCKS]['basis'].append(s)
                        
                    elif basis.aux_type == "C":
                        if basis.aux_type not in first_basis:
                            s = "%s/C" % Basis.map_orca_basis(basis.get_basis_name())
                            info[Method.ORCA_ROUTE].append(s)
                            first_basis.append(basis.aux_type)
                        
                        else:
                            for ele in basis.elements:
                                s = "newAuxCGTO        %-2s " % ele
                                s += "\"%s/C\" end" % Basis.map_orca_basis(basis.get_basis_name())
                    
                                info[Method.ORCA_BLOCKS]['basis'].append(s)
                    
                    elif basis.aux_type == "J":
                        if basis.aux_type not in first_basis:
                            s = "%s/J" % Basis.map_orca_basis(basis.get_basis_name())
                            info[Method.ORCA_ROUTE].append(s)
                            first_basis.append(basis.aux_type)
                        
                        else:
                            for ele in basis.elements:
                                s = "newAuxJGTO        %-2s " % ele
                                s += "\"%s/J\" end" % Basis.map_orca_basis(basis.get_basis_name())
                    
                                info[Method.ORCA_BLOCKS]['basis'].append(s)

                    elif basis.aux_type == "JK":
                        if basis.aux_type not in first_basis:
                            s = "%s/JK" % Basis.map_orca_basis(basis.get_basis_name())
                            info[Method.ORCA_ROUTE].append(s)
                            first_basis.append(basis.aux_type)
                        
                        else:
                            for ele in basis.elements:
                                s = "newAuxJKGTO       %-2s " % ele
                                s += "\"%s/JK\" end" % Basis.map_orca_basis(basis.get_basis_name())
                    
                                info[Method.ORCA_BLOCKS]['basis'].append(s)

                    elif basis.aux_type == "CABS":
                        if basis.aux_type not in first_basis:
                            s = "%s-CABS" % Basis.map_orca_basis(basis.get_basis_name())
                            info[Method.ORCA_ROUTE].append(s)
                            first_basis.append(basis.aux_type)
                            
                        else:
                            for ele in basis.elements:
                                s = "newCABSGTO        %-2s " % ele
                                s += "\"%s-CABS\" end" % Basis.map_orca_basis(basis.get_basis_name())
                    
                                info[Method.ORCA_BLOCKS]['basis'].append(s)

                    elif basis.aux_type == "OptRI CABS":
                        if basis.aux_type not in first_basis:
                            s = "%s-OptRI" % Basis.map_orca_basis(basis.get_basis_name())
                            info[Method.ORCA_ROUTE].append(s)
                            first_basis.append(basis.aux_type)
                        
                        else:
                            for ele in basis.elements:
                                s = "newCABSGTO        %-2s " % ele
                                s += "\"%s-OptRI\" end" % Basis.map_orca_basis(basis.get_basis_name())
                    
                                info[Method.ORCA_BLOCKS]['basis'].append(s)

                elif len(basis.elements) > 0 and basis.user_defined:
                    #I'm not going to insert file contents for ORCA b/c the format BSE uses for a file
                    #seems to be different than what ORCA expects in the %basis block
                    #BSE puts element names where orca expects symbols
                    s += "GTOName \"%s\"" % basis.user_defined
                
                    if len(basis.elements) > 0:
                        info[Method.ORCA_BLOCKS]['basis'].append(s)
                
        if self.ecp is not None:
            for basis in self.ecp:
                if len(basis.elements) > 0 and not basis.user_defined:
                    for ele in basis.elements:
                        s = "newECP            %-2s " % ele
                        s += "\"%s\" end" % Basis.map_orca_basis(basis.get_basis_name())
                    
                        info[Method.ORCA_BLOCKS]['basis'].append(s)
 
                elif len(basis.elements) > 0 and basis.user_defined:
                    #TODO: check if this works
                    s = "GTOName \"%s\"" % basis.user_defined                            
            
                    info[Method.ORCA_BLOCKS]['basis'].append(s)
            
        return info

    def check_for_elements(self, elements):
        warning = ""
        if self.basis is not None:
            elements_without_basis = {}
            for basis in self.basis:
                if basis.aux_type not in elements_without_basis:
                    elements_without_basis[basis.aux_type] = elements.copy()
                    
                for element in basis.elements:
                    if element in elements_without_basis[basis.aux_type]:
                        elements_without_basis[basis.aux_type].remove(element)
            
            if any(len(elements_without_basis[aux]) != 0 for aux in elements_without_basis.keys()):
                for aux in elements_without_basis.keys():
                    if len(elements_without_basis[aux]) != 0:
                        if aux != "no":
                            warning += "%s ha%s no auxiliary %s basis; " % (", ".join(elements_without_basis[aux]), "s" if len(elements_without_basis[aux]) == 1 else "ve", aux)
                        else:
                            warning += "%s ha%s no basis; " % (", ".join(elements_without_basis[aux]), "s" if len(elements_without_basis[aux]) == 1 else "ve")
                            
                return warning.strip('; ')
            
            else:
                return None


class Basis:
    def __init__(self, name, elements, aux_type=None, diffuse=None, polarization=0, user_defined=False):
        """
        name         -   basis set base name (e.g. 6-31G)
        elements     -   list of element symbols the basis set applies to
        diffuse      -   diffusion level (i.e. int (2 for **)/tuple(dict(non-H), dict(H)) (e.g. ({'d':1}, {'p':1})) for 6-31G**, aug, jun, etc. for Dunning
        polarization -   number of polarization functions
        user_defined -   file containing basis info/False for builtin basis sets
        
        diffuse and polarization should only be used if the specs are not included in name
        i.e. name=6-31G* and diffuse=1 results in 6-31G**
        """
        self.name = name
        self.elements = elements
        self.aux_type = aux_type
        self.diffuse = diffuse
        self.polarization = polarization
        self.user_defined = user_defined

    def __repr__(self):
        return "%s(%s)" % (self.get_basis_name(), " ".join(self.elements))

    def __eq__(self, other):
        if not isinstance(other, Basis):
            return False
        
        return self.get_basis_name() == other.get_basis_name()
            
    def get_basis_name(self):
        """returns basis set name taking into account diffusion and polarization"""
        name = self.name
        upper_name = name.upper()
        if self.diffuse is not None:
            if upper_name.startswith("CC-PV"):
                name = "-".join([self.diffuse, self.name])
            else:
                if upper_name.endswith("G"):
                    name = name[:-1] + (self.diffuse * "+") + "G"
                else:
                    name += (self.diffuse * "+")
                    
        if self.polarization != 0:
            if isinstance(self.polarization, int):
                name += (self.polarization * "*")
            else:
                name += "("
                for key in self.polarization[0]:
                    if self.polarization[0][key] != 1:
                        name += "%i%s" % (self.polarization[0][key], key)
                    else:
                        name += key                
                
                name += ","
                
                for key in self.polarization[0]:
                    if self.polarization[0][key] != 1:
                        name += "%i%s" % (self.polarization[0][key], key)
                    else:
                        name += key
                
                name += ")"
            
        return name
            
    @staticmethod
    def map_gaussian09_basis(name):
        """returns the Gaussian09/16 name of the basis set
        currently just removed the hyphen from the Karlsruhe def2 sets"""
        if name.startswith('def2-'):
            return name.replace('def2-', 'def2', 1)
        else:
            return name    
            
    @staticmethod
    def map_orca_basis(name):
        """returns the ORCA name of the basis set
        currently doesn't do anything"""
        return name
        
    @staticmethod
    def max_gaussian09_polarizable(name):
        name = name.upper()
        if name == "6-21G":
            return 2
        elif name == "4-31G":
            return 2
        elif name == "6-31G":
            return 2
        elif name == "6-311G":
            return 2
        
        else:
            return 0
    
    @staticmethod
    def max_gaussian09_diffuse(name):
        name = name.upper()
        if name == "3-21G":
            return 1
        elif name == "6-31G":
            return 2
        elif name == "6-311G":
            return 2
        elif name == "CBSB7":
            return 2
        elif name.startswith("CC-PV"):
            return 1
        
        else:
            return 0


class ECP(Basis):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        
    def __eq__(self, other):
        if not isinstance(other, ECP):
            return False
            
        return super().__eq__(other) 
 
 
class EmpiricalDispersion:
    def __init__(self, name):
        self.name = name
        
    def get_gaussian09(self):
        """Acceptable dispersion methods for Gaussian are:
        Grimme D2
        Grimme D3
        Becke-Johnson damped Grimme D3
        Petersson-Frisch
        
        Dispersion methods available in other software that will be modified are:
        Grimme D4
        undampened Grimme D3
        
        other methods will raise RuntimeError"""
        
        if self.name == "Grimme D2":
            return ("EmpiricalDispersion=GD2", None)
        elif self.name == "Grimme D3":
            return ("EmpiricalDispersion=GD3", None)
        elif self.name == "Becke-Johnson damped Grimme D3":
            return ("EmpiricalDispersion=GD3BJ", None)
        elif self.name == "Petersson-Frisch":
            return ("EmpiricalDispersion=PFD", None)
            
        #dispersions in ORCA but not Gaussian
        elif self.name == "Grimme D4":
            return ("EmpiricalDispersion=GD3BJ", "Grimme's D4 has no keyword in Gaussian, switching to GD3BJ")
        elif self.name == "undampened Grimme D3":
            return ("EmpiricalDispersion=GD3", "undampened Grimme's D3 is unavailable in Gaussian, switching to GD3")
        
        #unrecognized
        else:
            raise RuntimeError("unrecognized emperical dispersion: %s" % self.name)

    def get_orca(self):
        if self.name == "Grimme D2":
            return ("D2", None)
        elif self.name == "Undamped Grimme D3":
            return ("D3", None)
        elif self.name == "Becke-Johnson damped Grimme D3":
            return ("D3BJ", None)
        elif self.name == "Grimme D4":
            return ("D4", None)


class ImplicitSolvent:
    #solvent names look weird, but I'm leaving them this way to make them easier to read 
    #many look similar (dichloromethane and dichloroethane, etc)
    KNOWN_GAUSSIAN_SOLVENTS = ["Water", 
                               "Acetonitrile", 
                               "Methanol", 
                               "Ethanol", 
                               "IsoQuinoline", 
                               "Quinoline", 
                               "Chloroform", 
                               "DiethylEther", 
                               "DichloroMethane", 
                               "DiChloroEthane", 
                               "CarbonTetraChloride", 
                               "Benzene", 
                               "Toluene", 
                               "ChloroBenzene", 
                               "NitroMethane", 
                               "Heptane", 
                               "CycloHexane", 
                               "Aniline", 
                               "Acetone", 
                               "TetraHydroFuran", 
                               "DiMethylSulfoxide", 
                               "Argon", 
                               "Krypton", 
                               "Xenon", 
                               "n-Octanol", 
                               "1,1,1-TriChloroEthane", 
                               "1,1,2-TriChloroEthane", 
                               "1,2,4-TriMethylBenzene", 
                               "1,2-DiBromoEthane", 
                               "1,2-EthaneDiol", 
                               "1,4-Dioxane", 
                               "1-Bromo-2-MethylPropane", 
                               "1-BromoOctane", 
                               "1-BromoPentane", 
                               "1-BromoPropane", 
                               "1-Butanol", 
                               "1-ChloroHexane", 
                               "1-ChloroPentane", 
                               "1-ChloroPropane", 
                               "1-Decanol", 
                               "1-FluoroOctane", 
                               "1-Heptanol", 
                               "1-Hexanol", 
                               "1-Hexene", 
                               "1-Hexyne", 
                               "1-IodoButane", 
                               "1-IodoHexaDecane", 
                               "1-IodoPentane", 
                               "1-IodoPropane", 
                               "1-NitroPropane", 
                               "1-Nonanol", 
                               "1-Pentanol", 
                               "1-Pentene", 
                               "1-Propanol", 
                               "2,2,2-TriFluoroEthanol", 
                               "2,2,4-TriMethylPentane", 
                               "2,4-DiMethylPentane", 
                               "2,4-DiMethylPyridine", 
                               "2,6-DiMethylPyridine", 
                               "2-BromoPropane", 
                               "2-Butanol", 
                               "2-ChloroButane", 
                               "2-Heptanone", 
                               "2-Hexanone", 
                               "2-MethoxyEthanol", 
                               "2-Methyl-1-Propanol", 
                               "2-Methyl-2-Propanol", 
                               "2-MethylPentane", 
                               "2-MethylPyridine", 
                               "2-NitroPropane", 
                               "2-Octanone", 
                               "2-Pentanone", 
                               "2-Propanol", 
                               "2-Propen-1-ol", 
                               "3-MethylPyridine", 
                               "3-Pentanone", 
                               "4-Heptanone", 
                               "4-Methyl-2-Pentanone", 
                               "4-MethylPyridine", 
                               "5-Nonanone", 
                               "AceticAcid", 
                               "AcetoPhenone", 
                               "a-ChloroToluene", 
                               "Anisole", 
                               "Benzaldehyde", 
                               "BenzoNitrile", 
                               "BenzylAlcohol", 
                               "BromoBenzene", 
                               "BromoEthane", 
                               "Bromoform", 
                               "Butanal", 
                               "ButanoicAcid", 
                               "Butanone", 
                               "ButanoNitrile", 
                               "ButylAmine", 
                               "ButylEthanoate", 
                               "CarbonDiSulfide", 
                               "Cis-1,2-DiMethylCycloHexane", 
                               "Cis-Decalin", 
                               "CycloHexanone", 
                               "CycloPentane", 
                               "CycloPentanol", 
                               "CycloPentanone", 
                               "Decalin-mixture", 
                               "DiBromomEthane", 
                               "DiButylEther", 
                               "DiEthylAmine", 
                               "DiEthylSulfide", 
                               "DiIodoMethane", 
                               "DiIsoPropylEther", 
                               "DiMethylDiSulfide", 
                               "DiPhenylEther", 
                               "DiPropylAmine", 
                               "E-1,2-DiChloroEthene", 
                               "E-2-Pentene", 
                               "EthaneThiol", 
                               "EthylBenzene", 
                               "EthylEthanoate", 
                               "EthylMethanoate", 
                               "EthylPhenylEther", 
                               "FluoroBenzene", 
                               "Formamide", 
                               "FormicAcid", 
                               "HexanoicAcid", 
                               "IodoBenzene", 
                               "IodoEthane", 
                               "IodoMethane", 
                               "IsoPropylBenzene", 
                               "m-Cresol", 
                               "Mesitylene", 
                               "MethylBenzoate", 
                               "MethylButanoate", 
                               "MethylCycloHexane", 
                               "MethylEthanoate", 
                               "MethylMethanoate", 
                               "MethylPropanoate", 
                               "m-Xylene", 
                               "n-ButylBenzene", 
                               "n-Decane", 
                               "n-Dodecane", 
                               "n-Hexadecane", 
                               "n-Hexane", 
                               "NitroBenzene", 
                               "NitroEthane", 
                               "n-MethylAniline", 
                               "n-MethylFormamide-mixture", 
                               "n,n-DiMethylAcetamide", 
                               "n,n-DiMethylFormamide", 
                               "n-Nonane", 
                               "n-Octane", 
                               "n-Pentadecane", 
                               "n-Pentane", 
                               "n-Undecane", 
                               "o-ChloroToluene", 
                               "o-Cresol", 
                               "o-DiChloroBenzene", 
                               "o-NitroToluene", 
                               "o-Xylene", 
                               "Pentanal", 
                               "PentanoicAcid", 
                               "PentylAmine", 
                               "PentylEthanoate", 
                               "PerFluoroBenzene", 
                               "p-IsoPropylToluene", 
                               "Propanal", 
                               "PropanoicAcid", 
                               "PropanoNitrile", 
                               "PropylAmine", 
                               "PropylEthanoate", 
                               "p-Xylene", 
                               "Pyridine", 
                               "sec-ButylBenzene", 
                               "tert-ButylBenzene", 
                               "TetraChloroEthene", 
                               "TetraHydroThiophene-s,s-dioxide", 
                               "Tetralin", 
                               "Thiophene", 
                               "Thiophenol", 
                               "trans-Decalin", 
                               "TriButylPhosphate", 
                               "TriChloroEthene", 
                               "TriEthylAmine", 
                               "Xylene-mixture", 
                               "Z-1,2-DiChloroEthene"]

    KNOWN_ORCA_SOLVENTS = ["Water",
                           "Acetonitrile", 
                           "Acetone", 
                           "Ammonia", 
                           "Ethanol", 
                           "Methanol", 
                           "CH2Cl2", 
                           "CCl4", 
                           "DMF", 
                           "DMSO", 
                           "Pyridine", 
                           "THF", 
                           "Chloroform", 
                           "Hexane", 
                           "Benzene", 
                           "CycloHexane",
                           "Octanol", 
                           "Toluene"]

    def __init__(self, name, solvent):
        self.name = name
        self.solvent = solvent
        
    def get_gaussian09(self):
        warning = None
        s = "scrf=("
        if self.name == "Polarizable Continuum Model":
            s += "PCM, "
        elif self.name == "Continuum Solvent with Solute Electron Density":
            s += "SMD, "
        #I think this is CPCM...
        elif self.name == "Conductor-like PCM":
            s += "CPCM, "
            
        else:
            s += "%s, " % self.name
            
        s += "solvent=%s)" % self.solvent

        if not any(self.solvent.lower() == x.lower() for x in self.KNOWN_GAUSSIAN_SOLVENTS):
            warning = ["%s might not be a Gaussian solvent"]

        return (s, warning)


class IntegrationGrid:
    def __init__(self, name):
        self.name = name
        
    def get_gaussian09(self):
        if self.name == "UltraFine":
            return ("Integral=(grid=UltraFine)", None)
        elif self.name == "FineGrid":
            return ("Integral=(grid=FineGrid)", None)
        elif self.name == "SuperFineGrid":
            return ("Integral=(grid=SuperFineGrid)", None)
            
        #Grids available in ORCA but not Gaussian
        #uses n_rad from K-Kr as specified in ORCA 4.2.1 manual (section 9.3)
        #XXX: there's probably IOp's that can get closer
        elif self.name == "Grid 2":
            n_rad = 45
            return ("Integral=(grid=%i110)" % n_rad, "Approximating ORCA Grid 2")
        elif self.name == "Grid 3":
            n_rad = 45
            return ("Integral=(grid=%i194)" % n_rad, "Approximating ORCA Grid 3")
        elif self.name == "Grid 4":
            n_rad = 45
            return ("Integral=(grid=%i302)" % n_rad, "Approximating ORCA Grid 4")
        elif self.name == "Grid 5":
            n_rad = 50
            return ("Integral=(grid=%i434)" % n_rad, "Approximating ORCA Grid 5")
        elif self.name == "Grid 6":
            n_rad = 55
            return ("Integral=(grid=%i590)" % n_rad, "Approximating ORCA Grid 6")
        elif self.name == "Grid 7":
            n_rad = 60
            return ("Integral=(grid=%i770)" % n_rad, "Approximating ORCA Grid 7")
            
        else:
            return ("Integral=(grid=%s)" % self.name, "grid may not be available in Gaussian")
            
    def get_orca(self):
        """translates grid to something ORCA accepts
        current just returns self.name"""
        return (self.name, None)
        