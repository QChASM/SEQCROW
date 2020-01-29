from chimerax.core.toolshed import BundleAPI
import os


class _QChaSM_API(BundleAPI):

    api_version = 1
    
    @staticmethod
    def initialize(session, bundle_info):
        #TODO set AaronTools environment variables
        from . import settings
        settings.settings = settings._ChimAARONSettings(session, "ChimAARON")
        if session.ui.is_gui:
            from .presets import chimaaron_bse, chimaaron_s\
                ,indexLabel \
                ,blue_filter1, blue_filter2 \
                #,protanopia, protanomaly, deuteranopia, deuteranomaly, tritanopia, tritanomaly, achromatopsia, achromatomaly
                    
            session.presets.add_presets("ChimAARON", {"ball-stick-endcap":lambda p=chimaaron_bse: p(session)})
            session.presets.add_presets("ChimAARON", {"sticks":lambda p=chimaaron_s: p(session)})
            session.presets.add_presets("ChimAARON", {"index labels":lambda p=indexLabel: p(session)})
            session.presets.add_presets("Filters", {"blue filter 1":lambda p=blue_filter1: p(session)})
            session.presets.add_presets("Filters", {"blue filter 2":lambda p=blue_filter2: p(session)})
            #session.presets.add_presets("Filters", {"protanopia":lambda p=protanopia: p(session)})
            #session.presets.add_presets("Filters", {"protanomaly":lambda p=protanomaly: p(session)})
            #session.presets.add_presets("Filters", {"deuteranopia":lambda p=deuteranopia: p(session)})
            #session.presets.add_presets("Filters", {"deuteranomaly":lambda p=deuteranomaly: p(session)})
            #session.presets.add_presets("Filters", {"tritanopia":lambda p=tritanopia: p(session)})
            #session.presets.add_presets("Filters", {"tritanomaly":lambda p=tritanomaly: p(session)})
            #session.presets.add_presets("Filters", {"achromatopsia":lambda p=achromatopsia: p(session)})
            #session.presets.add_presets("Filters", {"achromatomaly":lambda p=achromatomaly: p(session)})

            session.ui.triggers.add_handler('ready',
                lambda *args, ses=session: settings.register_settings_options(ses))
        
        #apply AARONLIB setting
        if settings.settings.AARONLIB is not None:
            os.environ['AARONLIB'] = settings.settings.AARONLIB

    @staticmethod
    def open_file(session, path, format_name, coordsets=False):
        """
        open an AaronTools-readable structure (see AaronTools.fileIO.read_types)
        session     - chimerax Session 
        path        - str, path to file
        format_name - str, file format (see setup.py)
        coordsets   - bool, load as trajectory"""
        from .io import open_aarontools

        return open_aarontools(session, path, format_name=format_name, trajectory=coordsets)

    @staticmethod
    def save_file(session, path, format_name, **kw):
        #XML_TAG ChimeraX :: Save :: XYZ :: AaronTools :: false :: extra_keywords
        from .io import save_aarontools
        if format_name != "XYZ":
            raise NotImplementedError("ChimAARON can only save XYZ files, not %s files" % format_name)
            
        elif format_name == "XYZ":
            return save_aarontools(session, path, format_name, **kw)
        
    @staticmethod
    def register_selector(bundle_info, selector_info, logger):
        """select all transition metals with one easy `select` command!"""
        #XML_TAG ChimeraX :: Selector :: tm :: Transition metals
        
        from .selectors import register_selectors
        register_selectors(logger)

    @staticmethod
    def init_manager(session, bundle_info, name, **kw):
        """Initialize frequency_file manager"""
        if name == "chimaaron_frequency_file_manager":
            from .managers import FrequencyFileManager
            session.chimaaron_frequency_file_manager = FrequencyFileManager(session)
            return session.chimaaron_frequency_file_manager
        elif name == "chimaaron_ordered_selection_manager":
            from ChimAARON.managers import OrderedSelectionManager
            session.chimaaron_ordered_selection_manager = OrderedSelectionManager(session)
            return session.chimaaron_ordered_selection_manager
        else:
            raise RuntimeError("manager named '%s' is unknown to ChimAARON" % name)
  
    @staticmethod
    def start_tool(session, bi, ti):
        if ti.name == "Browse AaronTools Libraries":
            from .tools import AaronTools_Library
            tool = AaronTools_Library(session, ti.name)
            return tool        
        elif ti.name == "Visualize Normal Modes":
            from .tools import NormalModes
            tool = NormalModes(session, ti.name)
            return tool        
        elif ti.name == "Structure Modification":
            from .tools import EditStructure
            tool = EditStructure(session, ti.name)
            return tool        
        elif ti.name == "Add to Personal Library":
            from .tools import LibAdd
            tool = LibAdd(session, ti.name)
            return tool
        else:
            raise RuntimeError("tool named '%s' is unknown to ChimAARON" % ti.name)

bundle_api = _QChaSM_API()
