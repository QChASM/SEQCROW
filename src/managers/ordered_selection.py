from chimerax.core.toolshed import ProviderManager
from chimerax.core.selection import SELECTION_CHANGED
from chimerax.atomic import selected_atoms, Atoms


class OrderedSelectionManager(ProviderManager):
    """keeps track of the order atoms were selected"""
    def __init__(self, session):
        session.triggers.add_handler(SELECTION_CHANGED, self.selection_changed)
        
        self.session = session
        self._selection = []
    
    @property
    def selection(self):
        return Atoms(self._selection)  
    
    def selection_changed(self, *args):
        selection = selected_atoms(self.session)
        
        new_atoms = [atom for atom in selection if atom not in self._selection]
        if len(new_atoms) > 1:
            self._selection = []
            
        else:
            for atom in self._selection:
                if atom not in selection:
                    self._selection.remove(atom)

            self._selection.extend(new_atoms)
        
    def add_provider(self, bundle_info, name, **kw):
        self._selection = self._selection
