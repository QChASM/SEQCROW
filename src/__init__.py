import os

from chimerax.core.commands import run
from chimerax.core.toolshed import BundleAPI
from chimerax.core.toolshed.info import SelectorInfo
from chimerax.core.models import ADD_MODELS
from chimerax.open_command import OpenerInfo
from chimerax.core.commands import BoolArg, ModelsArg, StringArg, register, OpenFileNameArg

class _SEQCROW_API(BundleAPI):

    api_version = 1

    @staticmethod
    def initialize(session, bundle_info):
        """
        custom initialization sets settings, applies AaronTools environment
        variables, registers substituent selectors, menu stuff, 
        mouse modes, and changes the output destination for AaronTools loggers
        """
        from SEQCROW import settings as seqcrow_settings
        seqcrow_settings.settings = settings._SEQCROWSettings(session, "SEQCROW")
        if session.ui.is_gui:
            from .presets import seqcrow_bse, seqcrow_s, seqcrow_vdw, indexLabel

            session.presets.add_presets("SEQCROW", {"ball-stick-endcap":lambda p=seqcrow_bse: p(session)})
            session.presets.add_presets("SEQCROW", {"sticks":lambda p=seqcrow_s: p(session)})
            session.presets.add_presets("SEQCROW", {"VDW":lambda p=seqcrow_vdw: p(session)})
            session.presets.add_presets("SEQCROW", {"index labels":lambda p=indexLabel: p(session)})

            session.ui.triggers.add_handler(
                'ready',
                lambda *args, ses=session: settings.register_settings_options(ses)
            )

            session.ui.triggers.add_handler(
                'ready',
                lambda *args, ses=session: _SEQCROW_API.register_selector_menus(ses)
            )

            session.ui.triggers.add_handler(
                'ready',
                lambda *args, ses=session: _SEQCROW_API.register_tutorials(ses)
            )

            # session.ui.triggers.add_handler(
            #     'ready',
            #     lambda *args, ses=session: _SEQCROW_API.add_toolbar(ses)
            # )

            from SEQCROW.mouse_modes import (
                SelectConnectedMouseMode,
                DrawBondMouseMode,
                DrawTSBondMouseMode,
                ChangeElementMouseMode,
                EraserMouseMode,
                SubstituteMouseMode,
            )

            session.ui.mouse_modes.add_mode(SelectConnectedMouseMode(session))
            session.ui.mouse_modes.add_mode(DrawBondMouseMode(session))
            session.ui.mouse_modes.add_mode(DrawTSBondMouseMode(session))
            session.ui.mouse_modes.add_mode(ChangeElementMouseMode(session))
            session.ui.mouse_modes.add_mode(EraserMouseMode(session))
            session.ui.mouse_modes.add_mode(SubstituteMouseMode(session))
            
            session.triggers.add_handler(ADD_MODELS, _SEQCROW_API.open_useful_tools)

        #apply AARONLIB setting
        if seqcrow_settings.settings.AARONLIB is not None:
            os.environ['AARONLIB'] = seqcrow_settings.settings.AARONLIB

        session.seqcrow_settings = seqcrow_settings

        from AaronTools.const import ELEMENTS
        from AaronTools.substituent import Substituent

        #register selectors from the user's personal library
        for sub in Substituent.list():
            if sub in ELEMENTS:
                # print(sub, "in ELEMENTS")
                continue
            if not sub[0].isalpha():
                # print(sub, "startswith non-alpha")
                continue
            if len(sub) > 1 and any(not (c.isalnum() or c in "+-") for c in sub[1:]):
                # print(sub, "contains non-alphanumeric character")
                continue
            if not any([selector.name == sub for selector in bundle_info.selectors]):
                si = SelectorInfo(sub, atomic=True, synopsis="%s substituent" % sub)
                bundle_info.selectors.append(si)

        #need to reregister selectors b/c ^ that bypassed the bundle_info.xml or something
        bundle_info._register_selectors(session.logger)

        # set stream of AaronTools logger to the ChimeraX log
        from SEQCROW.logging_logger import LoggingLogger
        from AaronTools.geometry import Geometry
        from AaronTools.job_control import SubmitProcess
        from AaronTools.fileIO import Frequency, Orbitals, FileReader
        from AaronTools.config import Config
        from AaronTools.atoms import Atom

        log = LoggingLogger(session)

        for hdlr in Geometry.LOG.handlers:
            hdlr.setStream(log)
        for hdlr in Substituent.LOG.handlers:
            hdlr.setStream(log)
        for hdlr in SubmitProcess.LOG.handlers:
            hdlr.setStream(log)
        for hdlr in Frequency.LOG.handlers:
            hdlr.setStream(log)
        for hdlr in Config.LOG.handlers:
            hdlr.setStream(log)
        for hdlr in Atom.LOG.handlers:
            hdlr.setStream(log)
        for hdlr in Orbitals.LOG.handlers:
            hdlr.setStream(log)
        for hdlr in FileReader.LOG.handlers:
            hdlr.setStream(log)

    @staticmethod
    def open_file(session, path, format_name, coordsets=False):
        """
        open an AaronTools-readable structure (see AaronTools.fileIO.read_types)
        session     - chimerax Session
        path        - str, path to file
        format_name - str, file format
        coordsets   - bool, load as trajectory
        """
        if format_name != "NBO file":
            from .io import open_aarontools

            return open_aarontools(session, path, format_name=format_name, coordsets=coordsets)
        else:
            from .io import open_nbo
            
            return open_nbo(session, path, format_name=format_name, )

    @staticmethod
    def save_file(session, path, format_name, **kw):
        """
        save an XYZ file
        """
        from .io import save_aarontools
        if format_name != "XYZ":
            raise NotImplementedError("SEQCROW can only save XYZ files, not %s files" % format_name)

        return save_aarontools(session, path, format_name, **kw)

    @staticmethod
    def register_selector(bundle_info, selector_info, logger):
        """
        register selectors
        """
        from .selectors import register_selectors
        register_selectors(logger, selector_info.name)

    @staticmethod
    def init_manager(session, bundle_info, name, **kw):
        """Initialize filereader and ordered atom selection managers"""
        if name == "filereader_manager":
            from .managers import FileReaderManager
            session.filereader_manager = FileReaderManager(session, name)
            return session.filereader_manager

        elif name == "seqcrow_job_manager":
            from SEQCROW.managers import JobManager
            session.seqcrow_job_manager = JobManager(session, name)
            return session.seqcrow_job_manager

        elif name == "seqcrow_qm_input_manager":
            from SEQCROW.managers import QMInputManager
            session.seqcrow_qm_input_manager = QMInputManager(session, name)
            return session.seqcrow_qm_input_manager

        else:
            raise RuntimeError("manager named '%s' is unknown to SEQCROW" % name)

    @staticmethod
    def start_tool(session, bi, ti):
        """
        start tools
        """
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

        elif any(ti.name == name for name in [
                "Structure Modification",
                "Change Substituents",
                "Swap Transition Metal Ligands",
                "Fuse Ring",
                "Change Element",
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

        elif ti.name == "AaronJr Input Builder":
            from .tools import AARONInputBuilder
            return AARONInputBuilder(session, ti.name)

        elif ti.name == "Bond Editor":
            from .tools import BondEditor
            return BondEditor(session, ti.name)

        elif ti.name == "Rotate Atoms":
            from .tools import PrecisionRotate
            return PrecisionRotate(session, ti.name)

        elif ti.name == "Buried Volume":
            from .tools import PercentVolumeBuried
            return PercentVolumeBuried(session, ti.name)

        elif ti.name == "File Info":
            from .tools import Info
            return Info(session, ti.name)

        elif ti.name == "Cone Angle":
            from .tools import ConeAngle
            return ConeAngle(session, ti.name)

        elif ti.name == "Coordination Complex Generator":
            from .tools import CoordinationComplexVomit
            return CoordinationComplexVomit(session, ti.name)

        elif ti.name == "Orbital Viewer":
            from .tools import OrbitalViewer
            return OrbitalViewer(session, ti.name)

        elif ti.name == "Ligand Sterimol":
            from .tools import LigandSterimol
            return LigandSterimol(session, ti.name)

        elif ti.name == "IR Spectrum":
            from .tools import IRSpectrum
            return IRSpectrum(session, ti.name)

        elif ti.name == "UV/Vis Spectrum":
            from .tools import UVVisSpectrum
            return UVVisSpectrum(session, ti.name)

        elif ti.name == "Molecule Builder":
            from .tools import MolBuilder
            return MolBuilder(session, ti.name)

        else:
            raise RuntimeError("tool named '%s' is unknown to SEQCROW" % ti.name)

    @staticmethod
    def run_provider(session, name, mgr, **kw):
        """
        run providers
        provider might be open_command, save_command,
        QM input or job-related stuff, or the 
        test manager
        """
        if mgr is session.open_command:
            from SEQCROW.io import open_aarontools

            if name == "Gaussian input file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(
                            session,
                            data,
                            file_name,
                            format_name="Gaussian input file",
                            **kw
                        )

                    @property
                    def open_args(self):
                        return {}

                return Info()

            elif name == "Gaussian output file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(
                            session,
                            data,
                            file_name,
                            format_name="Gaussian output file",
                            **kw
                        )

                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}

                return Info()

            elif name == "ORCA output file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(
                            session,
                            data,
                            file_name,
                            format_name="ORCA output file",
                            **kw
                        )

                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}

                return Info()

            elif name == "Psi4 output file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(
                            session,
                            data,
                            file_name,
                            format_name="Psi4 output file",
                            **kw
                        )

                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}

                return Info()

            elif name == "XYZ file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(
                            session,
                            data,
                            file_name,
                            format_name="XYZ file",
                            **kw
                        )

                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}

                return Info()

            elif name == "FCHK file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(
                            session,
                            data,
                            file_name,
                            format_name="FCHK file",
                            **kw
                        )

                    @property
                    def open_args(self):
                        return {}

                return Info()

            elif name == "sqm output file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(
                            session,
                            data,
                            file_name,
                            format_name="sqm output file",
                            **kw
                        )

                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}

                return Info()
            
            elif name == "NBO input file" or name == "NBO output file":
                from .io import open_nbo
                
                class NBOOrbitalFile(OpenFileNameArg):
                    name_filter = "NBO coefficient files (*.32 *.33 *.34 *.35 *.36 *.37 *.38 *.39 *.40 *.41);;"
                    "PNAO file (*.32);;"
                    "NAO file (*.33);;"
                    "PNHO file (*.34);;"
                    "NHO file(*.35);;"
                    "PNBO file (*.36);;"
                    "NBO file (*.37);;"
                    "PNLMO file (*.38);;"
                    "NLMO file (*.39);;"
                    "MO file (*.40);;"
                    "NO file (*.41)"

                class Info(OpenerInfo):
                    def open(self, session, data, file_name, orbitals="browse", **kw):
                        return open_nbo(
                            session,
                            data,
                            file_name,
                            format_name=name,
                            orbitals=orbitals,
                            **kw
                        )

                    @property
                    def open_args(self):
                        return {'orbitals': NBOOrbitalFile}

                return Info()

        elif mgr is session.save_command:
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

                    def save_args_widget(self, session):
                        from .widgets import ModelComboBox
                        return ModelComboBox(session, autoUpdate=False)

                    def save_args_string_from_widget(self, widget):
                        return widget.options_string()

                return Info()

        elif mgr is session.seqcrow_qm_input_manager:
            if name == "Gaussian":
                from SEQCROW.input_file_formats import GaussianFileInfo
                return GaussianFileInfo()
            elif name == "ORCA":
                from SEQCROW.input_file_formats import ORCAFileInfo
                return ORCAFileInfo()
            elif name == "Psi4":
                from SEQCROW.input_file_formats import Psi4FileInfo
                return Psi4FileInfo()
            elif name == "SQM":
                from SEQCROW.input_file_formats import SQMFileInfo
                return SQMFileInfo()

        elif mgr is session.seqcrow_job_manager:
            if name == "Gaussian":
                from SEQCROW.jobs import GaussianJob
                return GaussianJob
            elif name == "ORCA":
                from SEQCROW.jobs import ORCAJob
                return ORCAJob
            elif name == "Psi4":
                from SEQCROW.jobs import Psi4Job
                return Psi4Job
            elif name == "SQM":
                from SEQCROW.jobs import SQMJob
                return SQMJob

        elif mgr is session.test_manager:
            if name == "fuseRing_command":
                from .tests.fuseRing_command import FuseRingCmdTest
                return FuseRingCmdTest

            elif name == "normal_modes":
                from .tests.normal_modes import NormalModesToolTest
                return NormalModesToolTest

            elif name == "substitute_command":
                from .tests.substitute_command import SubstituteCmdTest
                return SubstituteCmdTest

            elif name == "input_builder":
                from .tests.input_builder import QMInputBuilderToolTest
                return QMInputBuilderToolTest

            elif name == "buried_volume":
                from .tests.buried_volume import BuriedVolumeToolTest
                return BuriedVolumeToolTest

            elif name == "lookDown_command":
                from .tests.lookDown_command import LookDownCmdTest
                return LookDownCmdTest

            elif name == "cone_angle":
                from .tests.cone_angle import ConeAngleToolTest
                return ConeAngleToolTest

    @staticmethod
    def register_command(bundle_info, command_info, logger):
        """
        register commands
        """
        if command_info.name == "rmsdAlign":
            from .commands.rmsdAlign import rmsdAlign, rmsdAlign_description
            register("rmsdAlign", rmsdAlign_description, rmsdAlign)

        elif command_info.name == "substitute":
            from .commands.substitute import substitute, substitute_description
            register("substitute", substitute_description, substitute)

        elif command_info.name == "fuseRing":
            from .commands.fuseRing import fuseRing, fuseRing_description
            register("fuseRing", fuseRing_description, fuseRing)

        elif command_info.name == "tsbond":
            from .commands.tsbond import tsbond, tsbond_description
            register("tsbond", tsbond_description, tsbond)

        elif command_info.name == "~tsbond":
            from .commands.tsbond import erase_tsbond, erase_tsbond_description
            register("~tsbond", erase_tsbond_description, erase_tsbond)

        elif command_info.name == "sterimol":
            from .commands.sterimol import sterimol, sterimol_description
            register("sterimol", sterimol_description, sterimol)

        elif command_info.name == "percentVolumeBuried":
            from .commands.percent_Vbur import percent_vbur, vbur_description
            register("percentVolumeBuried", vbur_description, percent_vbur)

        elif command_info.name == "highlight":
            from .commands.highlight import highlight, highlight_description
            register("highlight", highlight_description, highlight)

        elif command_info.name == "~highlight":
            from .commands.highlight import erase_highlight, erase_highlight_description
            register("~highlight", erase_highlight_description, erase_highlight)

        elif command_info.name == "lookDown":
            from .commands.lookDown import lookDown, lookDown_description
            register("lookDown", lookDown_description, lookDown)

        elif command_info.name == "pointGroup":
            from .commands.point_group import pointGroup, pointGroup_description
            register("pointGroup", pointGroup_description, pointGroup)

        elif command_info.name == "ligandSterimol":
            from .commands.ligand_sterimol import ligandSterimol, sterimol_description
            register("ligandSterimol", sterimol_description, ligandSterimol)

    @staticmethod
    def register_selector_menus(session):
        """
        add selector menus
        """
        from Qt.QtWidgets import QAction

        from AaronTools.const import ELEMENTS
        from AaronTools.substituent import Substituent

        # substituent selectors
        add_submenu = session.ui.main_window.add_select_submenu
        add_selector = session.ui.main_window.add_menu_selector
        substituent_menu = add_submenu(['Che&mistry'], 'Substituents')
        for sub in Substituent.list():
            if sub in ELEMENTS:
                # print(sub, "in ELEMENTS")
                continue
            if not sub[0].isalpha():
                # print(sub, "startswith non-alpha")
                continue
            if len(sub) > 1 and any(not (c.isalnum() or c in "+-") for c in sub[1:]):
                # print(sub, "contains non-alphanumeric character")
                continue
            add_selector(substituent_menu, sub, sub)

        # connected selector
        mw = session.ui.main_window
        structure_menu = add_submenu([], '&Structure')
        structure_menu.addAction(QAction("Connected", mw))

    @staticmethod
    def register_tutorials(session):
        """
        add tutorial to help menu
        """
        from Qt.QtWidgets import QMenu, QAction
        from chimerax.core.commands import run
        mb = session.ui.main_window.menuBar()
        help_menu = mb.findChild(QMenu, "Help")
        seqcrow_tutorials = QAction("SEQCROW Tutorials", session.ui.main_window)
        seqcrow_tutorials.setToolTip("Tutorials for the SEQCROW bundle")
        seqcrow_tutorials.triggered.connect(
            lambda *args: run(session, "help help:seqcrow/tutorials.html")
        )
        help_menu.addAction(seqcrow_tutorials)

    @staticmethod
    def add_toolbar(session):
        """adds stuff to the toolbar"""
        from chimerax.toolbar.tool import get_toolbar_singleton
        from chimerax.ui.widgets.tabbedtoolbar import TabbedToolbar
        from Qt.QtWidgets import QWidget

        toolbar = get_toolbar_singleton(session)

        for child in toolbar.tool_window.ui_area.children():
            if isinstance(child, TabbedToolbar):
                tabs = child
                break

        tabs.addTab(QWidget(), "test")

    @staticmethod
    def get_class(name):
        print(name)
        """AaronTools/SEQCROW classes for saving things"""
        if name == "FileReader":
            from AaronTools.fileIO import FileReader
            return FileReader
        elif name == "Orbitals":
            from AaronTools.fileIO import Orbitals
            return Orbitals
        elif name == "Frequency":
            from AaronTools.spectra import Frequency
            return Frequency
        elif name == "ValenceExcitations":
            from AaronTools.spectra import ValenceExcitations
            return ValenceExcitations
        elif name == "HarmonicVibration":
            from AaronTools.spectra import HarmonicVibration
            return HarmonicVibration
        elif name == "AnharmonicVibration":
            from AaronTools.spectra import AnharmonicVibration
            return AnharmonicVibration
        elif name == "ValenceExcitation":
            from AaronTools.spectra import ValenceExcitation
            return ValenceExcitation
        elif name == "Atom":
            from AaronTools.atoms import Atom
            return Atom


    @staticmethod
    def finish(session, bundle_info):
        """remove managers"""
        del session.filereader_manager
        del session.seqcrow_qm_input_manager
        del session.seqcrow_job_manager

    @classmethod
    def open_useful_tools(cls, trigger_name, models):
        for model in models:
            if hasattr(model, "filereader") and model.filereader is not None:
                fr = model.filereader
                if (
                    "orbitals" in fr.other and
                    model.session.seqcrow_settings.settings.ORBIT_OPEN != "do nothing"
                ):
                    run(model.session, "ui tool show \"Orbital Viewer\"")
                if (
                    "frequency" in fr.other and
                    model.session.seqcrow_settings.settings.FREQ_OPEN != "do nothing"
                ):
                    run(model.session, "ui tool show \"Visualize Normal Modes\"")

bundle_api = _SEQCROW_API()
