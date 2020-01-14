from chimerax.core.toolshed import ProviderManager
from chimerax.core.models import REMOVE_MODELS, ADD_MODELS
from chimerax.core.triggerset import TriggerSet

FREQ_FILE_CHANGE = "frequency file opened or closed"

class FrequencyFileManager(ProviderManager):
    """keeps track of frequency files that have been opened"""
    # XML_TAG ChimeraX :: Manager :: chimaaron_frequency_file_manager
    def __init__(self, session):
        
        self.triggers = TriggerSet()
        self.triggers.add_trigger(FREQ_FILE_CHANGE)
                
        session.triggers.add_handler(REMOVE_MODELS, self.remove_models)
        session.triggers.add_handler(ADD_MODELS, self.add_models)
                
        #list of models with an associated FileReader object
        self.frequency_models = []
        
    def add_models(self, trigger_name, models):
        """add models with frequency data to our list"""
        for model in models:
            if hasattr(model, "aarontools_filereader") and 'frequency' in model.aarontools_filereader.other:
                self.frequency_models.append(model)
                self.triggers.activate_trigger(FREQ_FILE_CHANGE, self)
                
    def remove_models(self, trigger_name, models):
        """remove models with frequency data from out list when they are closed"""
        for model in models:
            if model in self.frequency_models:
                self.frequency_models.remove(model)
                self.triggers.activate_trigger(FREQ_FILE_CHANGE, self)

    def add_provider(self, bundle_info, name, **kw):
        self.frequency_models = self.frequency_models