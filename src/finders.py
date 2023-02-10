from AaronTools.finders import Finder

class AtomSpec(Finder):
    def __init__(self, atomspec):
        super().__init__()
        
        self.atomspec = atomspec
    
    def __repr__(self):
        return "atoms with atomspec %s" % self.atomspec
    
    def get_matching_atoms(self, atoms, geometry=None):
        matching_atoms = []
        for atom in atoms:
            try:
                if atom.atomspec == self.atomspec:
                    matching_atoms.append(atom)
            except AttributeError:
                pass
        
        return matching_atoms
        
class SerialNumber(Finder):
    def __init__(self, serial_number):
        super().__init__()
        
        self.serial_number = serial_number
    
    def __repr__(self):
        return "atoms with serial_number %s" % self.serial_number
    
    def get_matching_atoms(self, atoms, geometry=None):
        matching_atoms = []
        for atom in atoms:
            if hasattr(atom, "serial_number") and atom.serial_number == self.serial_number:
                matching_atoms.append(atom)
        
        return matching_atoms