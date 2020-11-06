import os

from chimerax.core.toolshed import BundleAPI
from chimerax.core.toolshed.info import SelectorInfo
from chimerax.open_command import OpenerInfo
from chimerax.core.commands import BoolArg, ModelsArg, StringArg, register

from AaronTools.const import ELEMENTS
from AaronTools.substituent import Substituent


class _SEQCROW_API(BundleAPI):

    api_version = 1
    
    @staticmethod
    def initialize(session, bundle_info):
        #TODO set AaronTools environment variables
        from SEQCROW import settings as seqcrow_settings
        seqcrow_settings.settings = settings._SEQCROWSettings(session, "SEQCROW")
        if session.ui.is_gui:
            from .presets import seqcrow_bse, seqcrow_s, seqcrow_vdw, indexLabel

            session.presets.add_presets("SEQCROW", {"ball-stick-endcap":lambda p=seqcrow_bse: p(session)})
            session.presets.add_presets("SEQCROW", {"sticks":lambda p=seqcrow_s: p(session)})
            session.presets.add_presets("SEQCROW", {"VDW":lambda p=seqcrow_vdw: p(session)})
            session.presets.add_presets("SEQCROW", {"index labels":lambda p=indexLabel: p(session)})

            session.ui.triggers.add_handler('ready',
                lambda *args, ses=session: settings.register_settings_options(ses))
                    
            session.ui.triggers.add_handler('ready',
                lambda *args, ses=session: _SEQCROW_API.register_selector_menus(ses))
        
        #apply AARONLIB setting
        if seqcrow_settings.settings.AARONLIB is not None:
            os.environ['AARONLIB'] = seqcrow_settings.settings.AARONLIB

        session.seqcrow_settings = seqcrow_settings
        
        #XXX:
        #initialize is called after init_manager 
        session.seqcrow_job_manager.init_queue()

        #register selectors from the user's personal library
        for sub in Substituent.list():
            if sub not in ELEMENTS and sub.isalnum():
                if not any([selector.name == sub for selector in bundle_info.selectors]):
                    si = SelectorInfo(sub, atomic=True, synopsis="%s substituent" % sub)
                    bundle_info.selectors.append(si)

        #need to reregister selectors b/c ^ that bypassed the bundle_info.xml or something
        bundle_info._register_selectors(session.logger)

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
        from .selectors import register_selectors
        register_selectors(logger, selector_info.name)

    @staticmethod
    def init_manager(session, bundle_info, name, **kw):
        """Initialize filereader and ordered atom selection managers"""
        if name == "filereader_manager":
            from .managers import FileReaderManager
            session.filereader_manager = FileReaderManager(session, name)
            return session.filereader_manager
            
        elif name == "seqcrow_ordered_selection_manager":
            from SEQCROW.managers import OrderedSelectionManager
            session.seqcrow_ordered_selection_manager = OrderedSelectionManager(session, name)
            return session.seqcrow_ordered_selection_manager
            
        elif name == "seqcrow_job_manager":
            from SEQCROW.managers import JobManager
            session.seqcrow_job_manager = JobManager(session, name)
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
        
        elif ti.name == "Substituent Sterimol":
            from .tools import Sterimol
            for tool in session.tools.list():
                if isinstance(tool, Sterimol):
                    tool.display(True)
                    break
            else:
                tool = Sterimol(session, ti.name)
                return tool
        
        elif any(ti.name == name for name in ["Structure Modification", \
                                            "Change Substituents", \
                                            "Swap Transition Metal Ligands", \
                                            "Fuse Ring", \
                                            "Change Element", \
                                            ]):
            from .tools import EditStructure
            for tool in session.tools.list():
                if isinstance(tool, EditStructure):
                    tool.display(True)
                    if ti.name == "Change Substituents":
                        tool.alchemy_tabs.setCurrentIndex(0)                    
                    elif ti.name == "Swap Transition Metal Ligands":
                        tool.alchemy_tabs.setCurrentIndex(1)
                    elif ti.name == "Fuse Ring":
                        tool.alchemy_tabs.setCurrentIndex(2)                    
                    elif ti.name == "Change Element":
                        tool.alchemy_tabs.setCurrentIndex(3)
                    break
            else:
                tool = EditStructure(session, ti.name)

                if ti.name == "Change Substituents":
                    tool.alchemy_tabs.setCurrentIndex(0)
                elif ti.name == "Swap Transition Metal Ligands":
                    tool.alchemy_tabs.setCurrentIndex(1)
                elif ti.name == "Fuse Ring":
                    tool.alchemy_tabs.setCurrentIndex(2)                
                elif ti.name == "Change Element":
                    tool.alchemy_tabs.setCurrentIndex(3)

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
        
        elif ti.name == "AARON Input Builder":
            from .tools import AARONInputBuilder
            return AARONInputBuilder(session, ti.name)
        
        elif ti.name == "Bond Editor":
            from .tools import BondEditor
            return BondEditor(session, ti.name)
                
        elif ti.name == "Rotate":
            from .tools import PrecisionRotate
            return PrecisionRotate(session, ti.name)
        
        else:
            raise RuntimeError("tool named '%s' is unknown to SEQCROW" % ti.name)

    @staticmethod
    def run_provider(session, name, mgr, **kw):
        if mgr == session.open_command:
            from SEQCROW.io import open_aarontools
            #TODO:
            #make use of AaronTools' ability to read file-like objects
            
            if name == "Gaussian input file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(session, data, file_name, format_name="Gaussian input file", **kw)
            
                    @property
                    def open_args(self):
                        return {}
                        
                return Info()
                
            elif name == "Gaussian output file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(session, data, file_name, format_name="Gaussian output file", **kw)
            
                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}
                        
                return Info()
                            
            elif name == "ORCA output file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(session, data, file_name, format_name="ORCA output file", **kw)
            
                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}
                        
                return Info()
            elif name == "Psi4 output file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(session, data, file_name, format_name="Psi4 output file", **kw)
            
                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}
                        
                return Info()
                                           
            elif name == "XYZ file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(session, data, file_name, format_name="XYZ file", **kw)
            
                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}
                        
                return Info()            
            
            elif name == "FCHK file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(session, data, file_name, format_name="FCHK file", **kw)
            
                    @property
                    def open_args(self):
                        return {}
                        
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

        elif command_info.name == "fuseRing":
            from .commands.fuseRing import fuseRing, fuseRing_description
            register("fuseRing", fuseRing_description, fuseRing)
        
        elif command_info.name == "angle":
            from .commands.angle import angle, angle_description
            register("angle", angle_description, angle)
        
        elif command_info.name == "dihedral":
            from .commands.dihedral import dihedral, dihedral_description
            register("dihedral", dihedral_description, dihedral)
        
        elif command_info.name == "tsbond":
            from .commands.tsbond import tsbond, tsbond_description
            register("tsbond", tsbond_description, tsbond)        
        
        elif command_info.name == "~tsbond":
            from .commands.tsbond import erase_tsbond, erase_tsbond_description
            register("~tsbond", erase_tsbond_description, erase_tsbond)

        elif command_info.name == "sterimol":
            from .commands.sterimol import sterimol, sterimol_description
            register("sterimol", sterimol_description, sterimol)

    @staticmethod
    def register_selector_menus(session):
        add_submenu = session.ui.main_window.add_select_submenu
        add_selector = session.ui.main_window.add_menu_selector
        substituent_menu = add_submenu(['Che&mistry'], 'Substituents')
        for sub in Substituent.list():
            if sub not in ELEMENTS and sub.isalnum():
                add_selector(substituent_menu, sub, sub)


bundle_api = _SEQCROW_API()
