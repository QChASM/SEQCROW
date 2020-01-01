from chimerax.core.toolshed import BundleAPI


class _MyAPI(BundleAPI):

    api_version = 1
    
    @staticmethod
    def initialize(session, bundle_info):
        """add some presets"""
        #TODO set AaronTools environment variables
        from .presets import preset1
                
        session.presets.add_presets("ChimAARON", {"ChimAARON BSE":lambda p=preset1: p(session)})

    @staticmethod
    def open_file(session, path, format_name, coordsets=False):
        """
        open an AaronTools-readable structure (see AaronTools.fileIO.read_types)
        session     - chimerax Session 
        path        - str, path to file
        format_name - str, file format (see setup.py)
        if coordsets is true, this might open a trajectory?
        XML_TAG ChimeraX :: DataFormat :: XYZ :: XYZ :: Molecular structure :: .xyz :: :: :: :: :: XYZ Format :: utf-8
        XML_TAG ChimeraX :: Open :: XYZ :: AaronTools :: :: coordsets:Bool
        XML_TAG ChimeraX :: DataFormat :: COM :: Gaussian input file :: Molecular structure :: .com,.gjf :: :: :: :: :: Gaussian input file :: utf-8
        XML_TAG ChimeraX :: Open :: COM :: Gaussian input file ::
        XML_TAG ChimeraX :: DataFormat :: LOG :: Gaussian output file :: Molecular structure :: .log :: :: :: :: :: Gaussian output file :: utf-8
        XML_TAG ChimeraX :: Open :: LOG :: Gaussian output file :: :: coordsets:Bool
        """
        from .io import open_aarontools

        return open_aarontools(session, path, format_name=format_name, trajectory=coordsets)


    @staticmethod
    def save_file(session, path, format_name, models=None, atoms=None, skip_atoms=None):
        """
        XML_TAG ChimeraX :: Save :: XYZ :: AaronTools ::
        """
        from .io import save_aarontools
        if format_name != "XYZ":
            raise NotImplementedError("ChimAARON can only save XYZ files, not %s files" % format_name)
            
        elif format_name == "XYZ":
            return save_aarontools(session, path, format_name, models, atoms, skip_atoms)
        

bundle_api = _MyAPI()
