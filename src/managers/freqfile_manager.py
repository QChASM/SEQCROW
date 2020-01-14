from chimerax.core.toolshed import ProviderManager
from chimerax.core.models import REMOVE_MODELS, ADD_MODELS

class FrequencyFileManager(ProviderManager):
    """keeps track of frequency files that have been opened"""
    # XML_TAG ChimeraX :: Manager :: chimaaron_frequency_file_manager
    def __init__(self, session):

        self._session = session
        
        self._session.triggers.add_handler(REMOVE_MODELS, self.refresh_models)
        self._session.triggers.add_handler(ADD_MODELS, self.refresh_models)
        
        #list of models with an associated FileReader object
        self.frequency_models = []
        
    def refresh_models(self, trigger_name, models):
        """refresh the list of models with associated frequency data"""
        self.frequency_models = []

        for model in self._session.models:
            if hasattr(model, "aarontools_filereader") and 'frequency' in model.aarontools_filereader.other:
                self.frequency_models.append(model)

    def add_provider(self, bundle_info, name, **kw):
        self.frequency_models = self.frequency_models