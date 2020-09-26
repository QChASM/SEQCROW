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
            if hasattr(atom, "atomspec") and atom.atomspec == self.atomspec:
                matching_atoms.append(atom)
        
        return matching_atoms