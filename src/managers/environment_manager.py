import os

from chimerax.core.toolshed import ProviderManager
from chimerax.core.triggerset import TriggerSet

class ChimAARONEnvironmentManager(ProviderManager):
    """reloads AaronTools when environment variable changes occur"""
    # XML_TAG ChimeraX :: Manager :: chimaaron_environment_manager
    def __init__(self, session):
        self.session = session
        from ChimAARON import settings
        settings.settings = settings._ChimAARONSettings(session, "chimaaron_environment_manager")
        settings.settings.triggers.add_handler("setting changed", self._new_custom_folder_cb)
        self._presets = {}
        from chimerax.core.triggerset import TriggerSet
        self.triggers = TriggerSet()
        self.triggers.add_trigger("chimaaron_environment_manager changed")
        self._new_custom_folder_cb()
        if session.ui.is_gui:
            session.ui.triggers.add_handler('ready',
                lambda *arg, ses=session: settings.register_settings_options(session))
        
    def _new_custom_folder_cb(self, *args):
        from ChimAARON.settings import settings, _ChimAARONSettings
        
        if not settings.AARONLIB:
            return
        else:
            for var in _ChimAARONSettings.EXPLICIT_SAVE:
                os.environ[var] = settings._cur_settings[var]
                print("set %s to %s" % (var, settings._cur_settings[var]))

    def add_provider(self, bundle_info, name, **kw):
        return