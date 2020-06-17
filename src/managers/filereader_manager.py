from chimerax.core.toolshed import ProviderManager
from chimerax.core.models import REMOVE_MODELS
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
        self.triggers.add_handler(FILEREADER_REMOVED, self.remove_filereader)
        self.triggers.add_handler(FILEREADER_ADDED, self.add_filereader)

        #list of models with an associated FileReader object
        self.models = []
        self.filereaders = []
        
    def add_filereader(self, trigger_name, models_and_filereaders):
        """add models with filereader data to our list"""
        models, filereaders = models_and_filereaders
        for model, filereader in zip(models, filereaders):
            self.models.append(model)
            self.filereaders.append(filereader)
    
        self.triggers.activate_trigger(FILEREADER_CHANGE, self)

    def remove_filereader(self, trigger_name, models_and_filereaders):
        models, filereaders = models_and_filereaders
        for model, filereader in zip(models, filereaders):
            self.models.remove(model)
            self.filereaders.remove(filereader)
            
        self.triggers.activate_trigger(FILEREADER_CHANGE, self)
    
    def remove_models(self, trigger_name, models):
        """remove models with filereader data from our list when they are closed"""
        models_changed = False
        for model in models:
            while model in self.models:
                models_changed = True
                ndx = self.models.index(model)
                self.filereaders.pop(ndx)
                self.models.remove(model)
                
        if models_changed:
            self.triggers.activate_trigger(FILEREADER_CHANGE, self)

    def add_provider(self, bundle_info, name, **kw):
        #*buzz lightyear* ah yes, the models are models
        self.models = self.models
    
    def get_model(self, fr):
        dict = self.filereader_dict
        for mdl in dict:
            if fr in dict[mdl]:
                return mdl
    
    @property
    def frequency_models(self):
        """returns a list of models with frequency data"""
        return [model for model in self.filereader_dict.keys() if any('frequency' in fr.other for fr in self.filereader_dict[model])]
    
    @property
    def frequency_filereaders(self):
        return [filereader for filereader in self.filereaders if 'frequency' in filereader.other]

    @property
    def filereader_dict(self):
        """returns a dictionary with atomic structures:FileReader pairs"""
        out = {}
        for mdl in self.models:
            out[mdl] = []
            for i, fr in enumerate(self.filereaders):
                if self.models[i] is mdl:
                    out[mdl].append(fr)
                    
        return out
    