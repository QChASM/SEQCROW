from chimerax.core.toolshed import ProviderManager
from chimerax.core.models import REMOVE_MODELS, ADD_MODELS
from chimerax.core.triggerset import TriggerSet

FILEREADER_CHANGE = "AaronTools file opened or closed"
FILEREADER_REMOVED = "AaronTools file closed"
FILEREADER_ADDED = "AaronTools file opened"

class FileReaderManager(ProviderManager):
    """keeps track of frequency files that have been opened"""
    # XML_TAG ChimeraX :: Manager :: filereader_manager
    def __init__(self, session):
        self.triggers = TriggerSet()
        self.triggers.add_trigger(FILEREADER_CHANGE)
        self.triggers.add_trigger(FILEREADER_ADDED)
        self.triggers.add_trigger(FILEREADER_REMOVED)
                
        session.triggers.add_handler(REMOVE_MODELS, self.remove_models)
        session.triggers.add_handler(ADD_MODELS, self.add_models)        
        self.triggers.add_handler(FILEREADER_REMOVED, self.remove_models)
        self.triggers.add_handler(FILEREADER_ADDED, self.add_models)

        #list of models with an associated FileReader object
        self.models = []
        
    def add_models(self, trigger_name, models):
        """add models with filereader data to our list"""
        for model in models:
            if hasattr(model, "aarontools_filereader"):
                self.models.append(model)
                self.triggers.activate_trigger(FILEREADER_CHANGE, self)
                
    def remove_models(self, trigger_name, models):
        """remove models with frequency data from out list when they are closed"""
        for model in models:
            if model in self.models:
                self.models.remove(model)
                self.triggers.activate_trigger(FILEREADER_CHANGE, self)

    def add_provider(self, bundle_info, name, **kw):
        #*buzz lightyear* ah yes, the models are models
        self.models = self.models
    
    @property
    def frequency_models(self):
        """returns a list of models with frequency data"""
        return [model for model in self.models if 'frequency' in model.aarontools_filereader.other]
    