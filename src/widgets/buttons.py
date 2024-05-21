from chimerax.core.models import ADD_MODELS, REMOVE_MODELS
from chimerax.atomic import AtomicStructure

from Qt.QtWidgets import (
    QPushButton, QMenu
)


class ModelsPushButton(QPushButton):
    def __init__(
        self,
        session,
        *args,
        modelTypes=[AtomicStructure],
        toggleButton=True,
        autoUpdate=True,
        selectedByDefault=True,
        **kwargs
    ):
        """
        modelTypes    - list(model subclasses) - types to show in the menu
        toggleButton  - bool - show "toggle selection" in menu
        autoUpdate    - bool - create handlers for when models are added or removed
                               these can be troublesome if deleteLater, destroy, or close 
                               are not called when this widget is discarded
        selectedByDefault - bool - true to select new models by default
        """
        super().__init__(*args, **kwargs)
        
        self._session = session
        self._mdl_types = modelTypes
        self._selectedByDefault = selectedByDefault
        
        menu = QMenu("select models")
        self.setMenu(menu)

        if toggleButton:
            action = self.menu().addAction("toggle selection")
            action.setCheckable(False)
            action.triggered.connect(self._toggle_selection)

        if autoUpdate:
            self._add_handler = session.triggers.add_handler(ADD_MODELS, self._add_models)
            self._del_handler = session.triggers.add_handler(REMOVE_MODELS, self._del_models)
        else:
            self._add_handler = None
            self._del_handler = None

        self._add_models("", self._session.models.list())

    def _toggle_selection(self):
        for action in self.menu().actions():
            if action.isCheckable():
                action.setChecked(not action.isChecked())

    def _add_models(self, trigger_name, models):
        menu = self.menu()
        for m in models:
            if any(isinstance(m, mdl_type) for mdl_type in self._mdl_types):
                action = menu.addAction(
                    "%s (%s)" % (m.name, m.atomspec),
                )
                action.setCheckable(True)
                if self._selectedByDefault:
                    action.setChecked(True)
                action.setData(m)
                menu.addAction(action)
    
    def _del_models(self, trigger_name, models):
        menu = self.menu()
        actions = menu.actions()
        for action in actions:
            if action.data() in models:
                menu.removeAction(action)
                action.deleteLater()
    
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

    def selectedModels(self):
        menu = self.menu()
        actions = menu.actions()
        out = []
        for action in actions:
            if action.isChecked() and action.data() is not None:
                out.append(action.data())

        return out

    def options_string(self):
        out = []
        for m in self.selectedModels():
            out.append(m.atomspec)
        
        if out:
            return "models " + " ".join(out)
        return ""
