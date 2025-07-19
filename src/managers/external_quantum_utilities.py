from chimerax.core.toolshed import ProviderManager

from inspect import signature


class ExternalUtilitiesManager(ProviderManager):
    def __init__(self, session, *args, **kwargs):
        self.session = session
        self.utilities = {}
        params = signature(super().__init__).parameters
        if any("name" in param for param in params):
            super().__init__(*args, **kwargs)
        else:
            super().__init__()

    def add_provider(self, bundle_info, name):
        self.utilities[name] = bundle_info
    
    def get_utility_widget(self, name):
        return self.utilities[name].run_provider(
            self.session,
            name,
            self,
        )
