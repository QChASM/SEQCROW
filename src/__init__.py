import os

from chimerax.core.toolshed import BundleAPI
from chimerax.core.toolshed.info import SelectorInfo
from chimerax.core.commands import BoolArg, ModelsArg, StringArg, register


class _SEQCROW_API(BundleAPI):

    api_version = 1
    
    @staticmethod
    def initialize(session, bundle_info):
        #TODO set AaronTools environment variables
        from SEQCROW import settings as seqcrow_settings
        seqcrow_settings.settings = settings._SEQCROWSettings(session, "SEQCROW")
        if session.ui.is_gui:
            from .presets import seqcrow_bse, seqcrow_s\
                ,indexLabel \
                    
            session.presets.add_presets("SEQCROW", {"ball-stick-endcap":lambda p=seqcrow_bse: p(session)})
            session.presets.add_presets("SEQCROW", {"sticks":lambda p=seqcrow_s: p(session)})
            session.presets.add_presets("SEQCROW", {"index labels":lambda p=indexLabel: p(session)})

            session.ui.triggers.add_handler('ready',
                lambda *args, ses=session: settings.register_settings_options(ses))
        
        #apply AARONLIB setting
        if seqcrow_settings.settings.AARONLIB is not None:
            os.environ['AARONLIB'] = seqcrow_settings.settings.AARONLIB

        session.seqcrow_settings = seqcrow_settings
        
        #XXX:
        #initialize is called after init_manager 
        session.seqcrow_job_manager.init_queue()

        ##register selectors from the user's personal library
        #from AaronTools.substituent import Substituent
        #for sub in Substituent.list():  
        #    if not any([selector.name == sub for selector in bundle_info.selectors]):
        #        si = SelectorInfo(sub, atomic=True, synopsis="%s substituent" % sub)
        #        bundle_info.selectors.append(si)

    @staticmethod
    def open_file(session, path, format_name, coordsets=False):
        """
        open an AaronTools-readable structure (see AaronTools.fileIO.read_types)
        session     - chimerax Session 
        path        - str, path to file
        format_name - str, file format (see setup.py)
        coordsets   - bool, load as trajectory"""
        from .io import open_aarontools

        return open_aarontools(session, path, format_name=format_name, coordsets=coordsets)

    @staticmethod
    def save_file(session, path, format_name, **kw):
        from .io import save_aarontools
        if format_name != "XYZ":
            raise NotImplementedError("SEQCROW can only save XYZ files, not %s files" % format_name)
            
        elif format_name == "XYZ":
            return save_aarontools(session, path, format_name, **kw)
        
    @staticmethod
    def register_selector(bundle_info, selector_info, logger):
        """select all transition metals with one easy `select` command!"""

        from .selectors import register_selectors
        register_selectors(logger)

    @staticmethod
    def init_manager(session, bundle_info, name, **kw):
        """Initialize filereader and ordered atom selection managers"""
        if name == "filereader_manager":
            from .managers import FileReaderManager
            session.filereader_manager = FileReaderManager(session)
            return session.filereader_manager
            
        elif name == "seqcrow_ordered_selection_manager":
            from SEQCROW.managers import OrderedSelectionManager
            session.seqcrow_ordered_selection_manager = OrderedSelectionManager(session)
            return session.seqcrow_ordered_selection_manager
            
        elif name == "seqcrow_job_manager":
            from SEQCROW.managers import JobManager
            session.seqcrow_job_manager = JobManager(session)
            return session.seqcrow_job_manager
            
        else:
            raise RuntimeError("manager named '%s' is unknown to SEQCROW" % name)
  
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
        elif ti.name == "Managed Models":
            from .tools import FileReaderPanel
            tool = FileReaderPanel(session, ti.name)
            return tool        
        elif ti.name == "Process QM Thermochemistry":
            from .tools import Thermochem
            tool = Thermochem(session, ti.name)
            return tool
        elif ti.name == "Build QM Input":
            from .tools import BuildQM
            tool = BuildQM(session, ti.name)
            return tool
        elif ti.name == "Job Queue":
            from .tools import JobQueue
            return JobQueue(session, ti.name)
        else:
            raise RuntimeError("tool named '%s' is unknown to SEQCROW" % ti.name)

    @staticmethod
    def run_provider(session, name, mgr, **kw):
        if mgr == session.open_command:
            from chimerax.open_command import OpenerInfo
            from SEQCROW.io import open_aarontools
            #TODO:
            #make use of AaronTools' ability to read file-like objects
            
            if name == "Gaussian input file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(session, data, format_name="Gaussian input file", **kw)
            
                    @property
                    def open_args(self):
                        return {}
                        
                return Info()
                
            elif name == "Gaussian output file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(session, data, format_name="Gaussian output file", **kw)
            
                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}
                        
                return Info()
                            
            elif name == "ORCA output file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(session, data, format_name="ORCA output file", **kw)
            
                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}
                        
                return Info()
            elif name == "Psi4 output file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(session, data, format_name="Psi4 output file", **kw)
            
                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}
                        
                return Info()
                                           
            elif name == "XYZ file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(session, data, format_name="XYZ file", **kw)
            
                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}
                        
                return Info()
                
        elif mgr == session.save_command:
            from chimerax.save_command import SaverInfo
            from SEQCROW.io import save_aarontools
            
            if name == "XYZ file":
                class Info(SaverInfo):
                    def save(self, session, path, **kw):
                        #save_aarontools doesn't actually pay attention to format_name yet
                        save_aarontools(session, path, "XYZ file", **kw)
                        
                    @property
                    def save_args(self):
                        return {'models': ModelsArg, 'comment': StringArg}
                        
                return Info()

    @staticmethod
    def register_command(bundle_info, command_info, logger):
        if command_info.name == "rmsdAlign":
            from .commands.rmsdAlign import rmsdAlign, rmsdAlign_description
            register("rmsdAlign", rmsdAlign_description, rmsdAlign)
        
        elif command_info.name == "substitute":
            from .commands.substitute import substitute, substitute_description
            register("substitute", substitute_description, substitute)


bundle_api = _SEQCROW_API()
