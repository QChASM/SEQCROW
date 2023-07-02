from chimerax.core.models import ADD_MODELS, REMOVE_MODELS
from chimerax.atomic import AtomicStructure

from Qt.QtWidgets import QComboBox

from SEQCROW.managers import FILEREADER_REMOVED, FILEREADER_ADDED

from os.path import basename


class ModelComboBox(QComboBox):
    """
    combobox for models 
    items will appear as "model.name (model.atomspec)"
    a tool's delete method should call deleteLater on instances of ModelComboBox
    """
    def __init__(self, session, *args, modelTypes=[AtomicStructure], addNew=False, autoUpdate=True, **kwargs):
        """
        modelTypes - list(model subclasses) - types to show in the combobox
        addNew        - bool - show "add new" in combobox
        autoUpdate    - bool - create handlers for when models are added or removed
                               these can be troublesome if deleteLater, destroy, or close 
                               are not called when this widget is discarded 
        """
        super().__init__(*args, **kwargs)
        
        self._session = session
        self._mdl_types = modelTypes
        if autoUpdate:
            self._add_handler = session.triggers.add_handler(ADD_MODELS, self._add_models)
            self._del_handler = session.triggers.add_handler(REMOVE_MODELS, self._del_models)
        else:
            self._add_handler = None
            self._del_handler = None
    
        self.setSizeAdjustPolicy(self.AdjustToMinimumContentsLengthWithIcon)
        
        if addNew:
            self.addItem("new structure", None)
    
        self._refresh_models()

    def deleteLater(self, *args, **kwargs):
        if self._add_handler is not None:
            self._session.triggers.remove_handler(self._add_handler)
            self._session.triggers.remove_handler(self._del_handler)
        
        return super().deleteLater(*args, **kwargs)

    def destroy(self, *args, **kwargs):
        if self._add_handler is not None:
            self._session.triggers.remove_handler(self._add_handler)
            self._session.triggers.remove_handler(self._del_handler)
        
        return super().destroy(*args, **kwargs)

    def close(self, *args, **kwargs):
        if self._add_handler is not None:
            self._session.triggers.remove_handler(self._add_handler)
            self._session.triggers.remove_handler(self._del_handler)
        
        return super().close(*args, **kwargs)

    def options_string(self):
        mdl = self.currentData()
        if mdl is not None:
            return "models %s" % mdl.atomspec

    def _refresh_models(self):
        valid_mdls = []
        for x in self._mdl_types:
            valid_mdls.extend(self._session.models.list(type=x))

        for i in range(self.count(), -1, -1):
            if self.itemData(i) not in valid_mdls and self.itemData(i) is not None:
                self.removeItem(i)
        
        for x in self._mdl_types:
            for mdl in self._session.models.list(type=x):
                ndx = self.findData(mdl)
                if ndx == -1:
                    self.addItem("%s (%s)" % (mdl.name, mdl.atomspec), mdl)
    
    def _add_models(self, trigger_name, models):
        for mdl in models:
            if any(isinstance(mdl, x) for x in self._mdl_types):
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
        
        self._add_handler = session.triggers.add_handler(ADD_MODELS, self._add_filereaders)
        self._del_handler = session.triggers.add_handler(REMOVE_MODELS, self._del_filereaders)
        
        self.setSizeAdjustPolicy(self.AdjustToMinimumContentsLengthWithIcon)
        
        self._refresh_models()

    def _refresh_models(self):
        filereaders = []
        for mdl in self._session.models.list():
            try:
                filereaders = mdl.filereaders
            except AttributeError:
                continue
            
            for fr in filereaders:
                if self._other and not all(x in fr for x in self._other):
                    continue
                ndx = self.findData((fr, mdl))
                if ndx == -1:
                    self.addItem(
                        "%s (%s)" % (basename(fr["name"]), mdl.atomspec),
                        (fr, mdl),
                    )

    def _add_filereaders(self, trigger_name, models):
        for mdl in models:
            try:
                for fr in mdl.filereaders:
                    if self._other and not all(x in fr for x in self._other):
                        continue
                    if self._other is None or all(x in fr for x in self._other):
                        self.addItem(
                            "%s (%s)" % (basename(fr["name"]), mdl.atomspec),
                            (fr, mdl),
                        )
            
            except AttributeError as e:
                pass

    def _del_filereaders(self, trigger_name, models):
        removed = True
        last_i = 0
        while removed:
            removed = False
            for i in range(last_i, self.count()):
                fr, mdl = self.itemData(i)
                last_i = i
                if mdl in models:
                    self.removeItem(i)
                    removed = True
                    break


    def deleteLater(self, *args, **kwargs):
        self._session.triggers.remove_handler(self._add_handler)
        self._session.triggers.remove_handler(self._del_handler)
        
        return super().deleteLater(*args, **kwargs)
    