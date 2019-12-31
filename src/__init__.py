from chimerax.core.toolshed import BundleAPI


class _MyAPI(BundleAPI):

    api_version = 1

    @staticmethod
    def open_file(session, path, format_name, coordsets=False):
        """
        open an AaronTools-readable structure (see AaronTools.fileIO.read_types)
        session     - chimerax Session 
        path        - str, path to file
        format_name - str, file format (see setup.py)
        if coordsets is true, this might open a trajectory?"""
        from .io import open_aarontools
        print(path)
        print(format_name)
        print(coordsets)
        return open_aarontools(session, path, format_name=format_name)

    @staticmethod
    def save_file(session, path, format_name, models=None, atoms=None, skip_atoms=None):
        from .io import save_aarontools
        if format_name != "XYZ":
            raise NotImplementedError("ChimAARON can only save XYZ files, not %s files" % format_name)
            
        elif format_name == "XYZ":
            return save_aarontools(session, path, format_name, models, atoms, skip_atoms)
        

bundle_api = _MyAPI()
