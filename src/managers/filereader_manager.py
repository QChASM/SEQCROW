from chimerax.core.commands import run
from chimerax.core.toolshed import ProviderManager
from chimerax.core.models import REMOVE_MODELS, ADD_MODELS
from chimerax.core.triggerset import TriggerSet

from os import path

import re

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
        filereaders = []
        for fr, mdl in zip(self.waiting_filereaders, self.waiting_models):
            if mdl in models:
                filereaders.append(fr)
        
        if len(filereaders) > 0:
            self.triggers.activate_trigger(FILEREADER_ADDED, filereaders)

    def apply_preset(self, trigger_name, models):
        """if a graphical preset is set in SEQCROW settings, apply that preset to models"""
        for model in models:
            if model in self.models:
                if model.session.ui.is_gui:
                    apply_seqcrow_preset(model)
            
            apply_non_seqcrow_preset(model)

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
            while model in self.models:
                ndx = self.models.index(model)
                removed_frs.append(self.filereaders.pop(ndx))
                self.models.remove(model)
                
        if len(removed_frs) > 0:
            self.triggers.activate_trigger(FILEREADER_REMOVED, removed_frs)

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

fmt_only = re.compile("(\S*):(.*)")

def apply_non_seqcrow_preset(model):
    preset = model.session.seqcrow_settings.settings.NON_SEQCROW_IO_PRESET
    atomspec = model.atomspec
    for line in preset:
        cmd = line.replace("<model>", atomspec)
        fmt = fmt_only.match(cmd)
        if fmt is not None and hasattr(model, "filename") and isinstance(model.filename, str):
            file_types = fmt.group(1).split(",")
            root, ext = path.splitext(model.filename)
            ext = ext.strip(".")
            if any(ext.lower() == e.lower() or model.name.lower().startswith("%s:" % e.lower()) for e in file_types):
                run(model.session, fmt.group(2).strip())
        
        elif fmt is not None:
            file_types = fmt.group(1).split(",")
            root, ext = path.splitext(model.name)
            ext = ext.strip(".")
            if any(ext.lower() == e.lower() or model.name.lower().startswith("%s:" % e.lower()) for e in file_types):
                run(model.session, fmt.group(2).strip())
            
        else:
            run(model.session, cmd)
    