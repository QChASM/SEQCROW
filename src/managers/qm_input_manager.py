from chimerax.core.toolshed import ProviderManager

from inspect import signature


class QMInputManager(ProviderManager):
    def __init__(self, session, *args, **kwargs):
        self.session = session
        self.formats = {}
        self.file_info = {}
        params = signature(super().__init__).parameters
        if any("name" in param for param in params):
            super().__init__(*args, **kwargs)
        else:
            super().__init__()

    def add_provider(self, bundle_info, name):
        print("adding %s format" % name)
        if name in self.formats:
            self.session.logger.warning(
                "file format %s from %s supplanted that from %s" % (
                    name, bundle_info.name, self.formats[name].name
                )
            )
        self.formats[name] = bundle_info
    
    def get_info(self, name):
        if name not in self.file_info:
            self.file_info[name] = self.formats[name].run_provider(
                self.session,
                name,
                self
            )
        return self.file_info[name]
    
