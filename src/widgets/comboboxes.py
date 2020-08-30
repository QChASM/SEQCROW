from chimerax.core.models import ADD_MODELS, REMOVE_MODELS
from chimerax.atomic import AtomicStructure

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox

from SEQCROW.managers import FILEREADER_REMOVED, FILEREADER_ADDED

from os.path import basename


class ModelComboBox(QComboBox):
    """combobox for models 
    items will appear as "model.name (model id)"
    a tool's delete method should call deleteLater on instances of ModelComboBox
    """
    def __init__(self, session, *args, modelTypes=AtomicStructure, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._session = session
        self._mdl_types = modelTypes
        self._add_handler = session.triggers.add_handler(ADD_MODELS, self._add_models)
        self._del_handler = session.triggers.add_handler(REMOVE_MODELS, self._del_models)
    
        self._refresh_models()

    def deleteLater(self, *args, **kwargs):
        self._session.triggers.remove_handler(self._add_handler)
        self._session.triggers.remove_handler(self._del_handler)
        
        return super().deleteLater(*args, **kwargs)

    def destroy(self, *args, **kwargs):
        self._session.triggers.remove_handler(self._add_handler)
        self._session.triggers.remove_handler(self._del_handler)
        
        return super().destroy(*args, **kwargs)

    def close(self, *args, **kwargs):
        self._session.triggers.remove_handler(self._add_handler)
        self._session.triggers.remove_handler(self._del_handler)
        
        return super().close(*args, **kwargs)

    def _refresh_models(self):
        for i in range(self.count(), -1, -1):
            if self.itemData(i) not in self._session.models.list(type=self._mdl_types):
                self.removeItem(i)
        
        for mdl in self._session.models.list(type=self._mdl_types):
            ndx = self.findData(mdl)
            if ndx == -1:
                self.addItem("%s (%s)" % (mdl.name, mdl.atomspec), mdl)
    
    def _add_models(self, trigger_name, models):
        for mdl in models:
            self.addItem("%s (%s)" % (mdl.name, mdl.atomspec), mdl)
    
    def _del_models(self, trigger_name, models):
        for mdl in models:
            ndx = self.findData(mdl)
            if ndx != -1:
                self.removeItem(ndx)


class FilereaderComboBox(QComboBox):
    """combobox for filereaders
    items will appear as "filereader.name (corresponding model id)"
    a tool's delete method should call deleteLater on instances of FilereaderComboBox
    """
    def __init__(self, session, *args, otherItems=None, **kwargs):
        """otherItems: list(str) - filereaders will be limited to those with 
                                   these keys in their 'other' dict
        """
        super().__init__(*args, **kwargs)
        
        self._session = session
        self._other = otherItems
        
        self._add_handler = session.filereader_manager.triggers.add_handler(FILEREADER_ADDED, self._add_filereaders)
        self._del_handler = session.filereader_manager.triggers.add_handler(FILEREADER_REMOVED, self._del_filereaders)
        
        self._refresh_models()

    def _refresh_models(self):
        for i in range(self.count(), -1, -1):
            if self.itemData(i) not in self._session.filereader_manager.list(other=self._other):
                self.removeItem(i)
        
        for fr in self._session.filereader_manager.list(other=self._other):
            ndx = self.findData(fr)
            if ndx == -1:
                mdl = self._session.filereader_manager.get_model(fr)
                self.addItem("%s (%s)" % (basename(fr.name), mdl.atomspec), fr)

    def _add_filereaders(self, trigger_name, filereaders):
        for fr in filereaders:
            mdl = self._session.filereader_manager.get_model(fr)
            self.addItem("%s (%s)" % (basename(fr.name), mdl.atomspec), fr)
            
    def _del_filereaders(self, trigger_name, filereaders):
        for fr in filereaders:
            ndx = self.findData(fr)
            if ndx != -1:
                self.removeItem(ndx)

    def deleteLater(self, *args, **kwargs):
        self._session.filereader_manager.triggers.remove_handler(self._add_handler)
        self._session.filereader_manager.triggers.remove_handler(self._del_handler)
        
        return super().deleteLater(*args, **kwargs)
 
    def destroy(self, *args, **kwargs):
        self._session.triggers.remove_handler(self._add_handler)
        self._session.triggers.remove_handler(self._del_handler)
        
        return super().destroy(*args, **kwargs)

    def close(self, *args, **kwargs):
        self._session.triggers.remove_handler(self._add_handler)
        self._session.triggers.remove_handler(self._del_handler)
        
        return super().close(*args, **kwargs)       