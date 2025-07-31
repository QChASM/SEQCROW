from chimerax.core.commands import run
from chimerax.core.toolshed import ProviderManager
from chimerax.core.models import REMOVE_MODELS, ADD_MODELS
from chimerax.core.triggerset import TriggerSet

from os import path

import re

from AaronTools.fileIO import FileReader

FILEREADER_CHANGE = "AaronTools file opened or closed"
FILEREADER_REMOVED = "AaronTools file closed"
FILEREADER_ADDED = "AaronTools file opened"
ADD_FILEREADER = "adding AaronTools FileReader"

class FileReaderManager(ProviderManager):
    """keeps track of frequency files that have been opened"""
    def __init__(self, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.triggers = TriggerSet()
        self.triggers.add_trigger(FILEREADER_CHANGE)
        self.triggers.add_trigger(FILEREADER_ADDED)
        self.triggers.add_trigger(FILEREADER_REMOVED)
        self.triggers.add_trigger(ADD_FILEREADER)

        session.triggers.add_handler(REMOVE_MODELS, self.remove_models)
        session.triggers.add_handler(ADD_MODELS, self.apply_preset)
        session.triggers.add_handler(ADD_MODELS, self.trigger_fr_add)
        self.triggers.add_handler(ADD_FILEREADER, self.add_filereader)

        #list of models with an associated FileReader object
        self.models = []
        self.filereaders = []
        self.waiting_models = []
        self.waiting_filereaders = []

    def trigger_fr_add(self, trigger_name, models):
        """FILEREADER_ADDED should not get triggered until the model is loaded"""
        models_and_filereaders = []
        for model in models:
            filereaders = []
            try:
                filereaders.extend([fr for fr in model.filereaders if fr])
            except AttributeError:
                pass
            if filereaders:
                models_and_filereaders.append((model, filereaders))
        
        if len(models_and_filereaders) > 0:
            self.triggers.activate_trigger(
                FILEREADER_ADDED, models_and_filereaders
            )

    def apply_preset(self, trigger_name, models):
        """if a graphical preset is set in SEQCROW settings, apply that preset to models"""
        for model in models:
            try:
                if model.session.ui.is_gui:
                    try:
                        model.filereaders[-1]
                        apply_seqcrow_preset(model)
                    except (AttributeError, IndexError):
                        # either the model doesn't have a filereaders attribute
                        # or there are no associated filereaders
                        pass
            except AttributeError:
                # model probably doesn't have a session
                # this can happen when a command (i.e. morph) creates a model
                # the model is created, the ADD_MODELS trigger fires, then
                # the model gets added to the session
                pass

    def add_filereader(self, trigger_name, models_and_filereaders):
        """add models with filereader data to our list"""
        models, filereaders = models_and_filereaders
        wait = False
        for model, filereader in zip(models, filereaders):
            self.models.append(model)
            self.filereaders.append(filereader)
            if model.atomspec == '#':
                wait = True
                self.waiting_models.append(model)
                self.waiting_filereaders.append(filereader)
                
        if not wait:
            self.triggers.activate_trigger(FILEREADER_ADDED, filereaders)
            
        self.triggers.activate_trigger(FILEREADER_CHANGE, filereaders)

    def remove_filereader(self, trigger_name, models_and_filereaders):
        models, filereaders = models_and_filereaders
        for model, filereader in zip(models, filereaders):
            self.models.remove(model)
            self.filereaders.remove(filereader)
            
        self.triggers.activate_trigger(FILEREADER_CHANGE, filereaders)
        self.triggers.activate_trigger(FILEREADER_REMOVED, filereaders)
    
    def remove_models(self, trigger_name, models):
        """remove models with filereader data from our list when they are closed"""
        removed_frs = []
        for model in models:
            try:
                removed_frs.extend(model.filereaders)
            except AttributeError:
                pass
        
        if len(removed_frs) > 0:
            self.triggers.activate_trigger(FILEREADER_REMOVED, removed_frs)
            self.triggers.activate_trigger(FILEREADER_CHANGE, removed_frs)
        
        # try to remove references to parsed data
        for fr in removed_frs:
            d = fr
            if isinstance(fr, FileReader):
                d = fr.__dict__
            for (key, attr) in list(d.items()):
                try:
                    delattr(fr, key)
                except AttributeError:
                    pass
                del attr
            del fr

    def add_provider(self, bundle_info, name, **kw):
        #*buzz lightyear* ah yes, the models are models
        self.models = self.models
    
    def get_model(self, fr):
        dict = self.filereader_dict
        for mdl in dict:
            if fr in dict[mdl]:
                return mdl
    
    def list(self, other=None):
        if other is None:
            return [fr for fr in self.filereaders]
        else:
            return [fr for fr in self.filereaders if all(x in fr.other for x in other)]
    
    @property
    def frequency_models(self):
        """returns a list of models with frequency data"""
        return [model for model in self.filereader_dict.keys() if any('frequency' in fr.other for fr in self.filereader_dict[model])]

    @property
    def energy_models(self):
        """returns a list of models with frequency data"""
        return [model for model in self.filereader_dict.keys() if any('energy' in fr.other for fr in self.filereader_dict[model])]

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

def apply_seqcrow_preset(model, atoms=None, fallback=None):
    preset = model.session.seqcrow_settings.settings.SEQCROW_IO_PRESET
    if fallback is not None and preset == "None":
        preset = fallback
    if "Ball-Stick-Endcap" in preset:
        from SEQCROW.presets import seqcrow_bse
        seqcrow_bse(model.session, models=[model], atoms=atoms)
    if "Sticks" in preset:
        from SEQCROW.presets import seqcrow_s
        seqcrow_s(model.session, models=[model], atoms=atoms)
    if "VDW" in preset:
        from SEQCROW.presets import seqcrow_vdw
        seqcrow_vdw(model.session, models=[model], atoms=atoms)
    if "Index Labels" in preset:
        from SEQCROW.presets import indexLabel
        indexLabel(model.session, models=[model])
