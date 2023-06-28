import os

from chimerax.core.commands import run
from chimerax.core.toolshed import BundleAPI
from chimerax.core.toolshed.info import SelectorInfo
from chimerax.core.models import ADD_MODELS
from chimerax.open_command import OpenerInfo
from chimerax.core.commands import BoolArg, IntArg, ModelsArg, StringArg, register, OpenFileNameArg

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
            from .presets import (
                seqcrow_bse,
                seqcrow_bse_cartoon,
                seqcrow_s,
                seqcrow_s_cartoon,
                seqcrow_vdw,
                indexLabel,
            )

            session.presets.add_presets("SEQCROW", {"ball-stick-endcap":lambda p=seqcrow_bse: p(session)})
            session.presets.add_presets("SEQCROW", {"ball-stick-endcap 2":lambda p=seqcrow_bse_cartoon: p(session)})
            session.presets.add_presets("SEQCROW", {"sticks":lambda p=seqcrow_s: p(session)})
            session.presets.add_presets("SEQCROW", {"sticks 2":lambda p=seqcrow_s_cartoon: p(session)})
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
                SelectSimilarFragments,
                DrawCoordinationBondMouseMode,
                DrawHydrogenBondMouseMode,
            )

            session.ui.mouse_modes.add_mode(SelectConnectedMouseMode(session))
            session.ui.mouse_modes.add_mode(DrawBondMouseMode(session))
            session.ui.mouse_modes.add_mode(DrawTSBondMouseMode(session))
            session.ui.mouse_modes.add_mode(ChangeElementMouseMode(session))
            session.ui.mouse_modes.add_mode(EraserMouseMode(session))
            session.ui.mouse_modes.add_mode(SubstituteMouseMode(session))
            session.ui.mouse_modes.add_mode(SelectSimilarFragments(session))
            session.ui.mouse_modes.add_mode(DrawCoordinationBondMouseMode(session))
            session.ui.mouse_modes.add_mode(DrawHydrogenBondMouseMode(session))
            
            session.triggers.add_handler(ADD_MODELS, _SEQCROW_API.open_useful_tools)

        #apply AARONLIB setting
        if seqcrow_settings.settings.AARONLIB is not None:
            os.environ['AARONLIB'] = seqcrow_settings.settings.AARONLIB
            import AaronTools.const
            AaronTools.const.AARONLIB = seqcrow_settings.settings.AARONLIB

        # set queue type
        if seqcrow_settings.settings.QUEUE_TYPE != "None":
            os.environ['QUEUE_TYPE'] = seqcrow_settings.settings.QUEUE_TYPE
            import AaronTools.job_control
            AaronTools.job_control.QUEUE_TYPE = seqcrow_settings.settings.QUEUE_TYPE.upper()

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

        _SEQCROW_API.register_class_snapshot_map(session)

    @staticmethod
    def register_class_snapshot_map(session):
        import json
    
        from chimerax.core.state import State
        
        from AaronTools.atoms import Atom
        from AaronTools.const import UNIT
        from AaronTools.orbitals import Orbitals
        from AaronTools.theory import Theory
        from AaronTools.json_extension import ATEncoder, ATDecoder
        from AaronTools.spectra import Frequency, ValenceExcitations
        
        class _ATState:
            @staticmethod
            def take_snapshot(obj, session, flags):
                return {"aarontools object": json.dumps(obj, cls=ATEncoder)}
            
            @staticmethod
            def restore_snapshot(session, data):
                return json.loads(data["aarontools object"], cls=ATDecoder)
        
        class _Orbitals:
            @staticmethod
            def take_snapshot(obj, session, flags):
                data = dict()
                if obj.fmt == "fchk":
                    data = {
                        "file_type": "fchk",
                        "Coordinates of each shell": obj.shell_coords / UNIT.A0_TO_BOHR,
                        "Shell types": [
                            _Orbitals.fchk_shell_map(x) for x in obj.shell_types
                        ],
                        "Contraction coefficients": obj.contraction_coeff,
                        "P(S=P) Contraction coefficients": obj.sp_contraction_coeff,
                        "Primitive exponents": obj.exponents,
                        "Number of primitives per shell": obj.n_prim_per_shell,
                        "Alpha Orbital Energies": obj.alpha_nrgs,
                        "Beta Orbital Energies": obj.beta_nrgs,
                        "Alpha MO coefficients": obj.alpha_coefficients,
                        "Number of alpha electrons": obj.n_alpha,
                    }
                    if obj.beta_coefficients:
                        data["Beta MO coefficients"] = obj.beta_coefficients

                    try:
                        data["Number of beta electrons"] = obj.n_beta
                    except AttributeError:
                        pass

                elif obj.fmt == "nbo":
                    data = {
                        "file_type": "47",
                        "exponents": obj.exponents,
                        "alpha_coefficients": obj.alpha_coefficients,
                        "n_prim_per_shell": obj.n_shell,
                        "funcs_per_shell": obj.funcs_per_shell,
                        "start_ndx": obj.start_ndx,
                        "momentum_label": obj.momentum_label,
                        **obj.coeffs_by_type,
                    }
                
                elif obj.fmt == "orca":
                    data = {
                        "file_type": "out",
                        "atoms": obj.atoms,
                        "basis_set_by_ele": obj.basis_set_by_ele,
                        "alpha_nrgs": obj.alpha_nrgs,
                        "beta_nrgs": obj.beta_nrgs,
                        "alpha_coefficients": obj.alpha_coefficients,
                        "beta_coefficients": obj.beta_coefficientsbeta_nrgs,
                        "n_alpha": obj.n_alpha,
                        "n_beta": obj.n_beta,
                    }
                    try:
                        data["alpha_occupancies"] = obj.alpha_occupancies
                    except AttributeError:
                        pass
                    try:
                        data["beta_occupancies"] = obj.beta_occupancies
                    except AttributeError:
                        pass
                
                return data
            
            @staticmethod
            def fchk_shell_map(x):
                return {
                    "s": 0,
                    "p": 1,
                    "sp": -1,
                    "6d": 2,
                    "5d": -2,
                    "10f": 3,
                    "7f": -3,
                    "9g": -4,
                    "11h": -5,
                    "13i": -6,
                }[x]
            
            @staticmethod
            def restore_snapshot(session, data):
                return Orbitals(data)

        methods = {
            Orbitals: _Orbitals,
            Atom: _ATState,
            Theory: _ATState,
            Frequency: _ATState,
            ValenceExcitations: _ATState,
        }
        
        session.register_snapshot_methods(methods)

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

        elif name == "seqcrow_cluster_scheduling_software_manager":
            from SEQCROW.managers import ClusterSchedulingSoftwareManager
            session.seqcrow_cluster_scheduling_software_manager = ClusterSchedulingSoftwareManager(session, name)
            return session.seqcrow_cluster_scheduling_software_manager

        elif name == "Slurm":
            from SEQCROW.managers import SlurmDefault
            session.seqcrow_slurm_manager = SlurmDefault(session, name)
            return session.seqcrow_slurm_manager

        elif name == "SGE":
            from SEQCROW.managers import SGEDefault
            session.seqcrow_sge_manager = SGEDefault(session, name)
            return session.seqcrow_sge_manager

        elif name == "PBS":
            from SEQCROW.managers import PBSDefault
            session.seqcrow_pbs_manager =  PBSDefault(session, name)
            return session.seqcrow_pbs_manager

        elif name == "LSF":
            from SEQCROW.managers import LSFDefault
            session.seqcrow_lsf_manager = LSFDefault(session, name)
            return session.seqcrow_lsf_manager

        elif name == "tss_finder_manager":
            from SEQCROW.managers import TSSFinderManager
            session.tss_finder_manager = TSSFinderManager(session, name)
            return session.tss_finder_manager
        
        elif name == "conformer_search_manager":
            from SEQCROW.managers import ConformerSearch
            session.conformer_search_manager = ConformerSearch(session, name)
            return session.conformer_search_manager

        else:
            raise RuntimeError("manager named '%s' is unknown to SEQCROW" % name)

    @staticmethod
    def start_tool(session, bi, ti):
        """
        start tools
        """
        if ti.name == "AaronTools Fragment Library":
            from .tools.browse_aarontools import AaronTools_Library
            tool = AaronTools_Library(session, ti.name)
            return tool

        elif ti.name == "Visualize Normal Modes":
            from .tools.normal_modes import NormalModes
            tool = NormalModes(session, ti.name)
            return tool

        elif ti.name == "Substituent Sterimol":
            from .tools.sterimol import Sterimol
            tool = Sterimol(session, ti.name)
            return tool

        elif any(ti.name == name for name in [
                "Structure Modification",
                "Change Substituents",
                "Swap Transition Metal Ligands",
                "Fuse Ring",
                "Change Element",
        ]):
            from .tools.structure_editing import EditStructure
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
            from .tools.libadd import LibAdd
            tool = LibAdd(session, ti.name)
            return tool

        elif ti.name == "Managed Models":
            from .tools.filereader_panel import FileReaderPanel
            tool = FileReaderPanel(session, ti.name)
            return tool

        elif ti.name == "Thermochemistry":
            from .tools.compute_thermo import Thermochem
            tool = Thermochem(session, ti.name)
            return tool

        elif ti.name == "Build QM Input":
            from .tools.input_generator import BuildQM
            tool = BuildQM(session, ti.name)
            return tool

        elif ti.name == "Job Queue":
            from .tools.job_manager_tool import JobQueue
            return JobQueue(session, ti.name)

        elif ti.name == "Bond Editor":
            from .tools.bond_editor import BondEditor
            return BondEditor(session, ti.name)

        elif ti.name == "Rotate Atoms":
            from .tools.precision_rotate import PrecisionRotate
            return PrecisionRotate(session, ti.name)

        elif ti.name == "Buried Volume":
            from .tools.percent_Vbur import PercentVolumeBuried
            return PercentVolumeBuried(session, ti.name)

        elif ti.name == "File Info":
            from .tools.info import Info
            return Info(session, ti.name)

        elif ti.name == "Cone Angle":
            from .tools.cone_angle import ConeAngle
            return ConeAngle(session, ti.name)

        elif ti.name == "Coordination Complex Generator":
            from .tools.coordination_complexes import CoordinationComplexVomit
            return CoordinationComplexVomit(session, ti.name)

        elif ti.name == "Orbital Viewer":
            from .tools.mo_viewer import OrbitalViewer
            return OrbitalViewer(session, ti.name)

        elif ti.name == "Ligand Sterimol":
            from .tools.ligand_sterimol import LigandSterimol
            return LigandSterimol(session, ti.name)

        elif ti.name == "IR Spectrum":
            from .tools.ir_plot import IRSpectrum
            return IRSpectrum(session, ti.name)

        elif ti.name == "UV/Vis Spectrum":
            from .tools.uvvis_plot import UVVisSpectrum
            return UVVisSpectrum(session, ti.name)

        elif ti.name == "2D Builder":
            from .tools.mol_builder import MolBuilder
            return MolBuilder(session, ti.name)

        elif ti.name == "Transition State Structures":
            from .tools.raven_setup import BuildRaven
            return BuildRaven(session, ti.name)
        
        elif ti.name == "Ligand Solid Angle":
            from .tools.solid_angle import SolidAngle
            return SolidAngle(session, ti.name)
        
        elif ti.name == "Conformer Search":
            from .tools.conformers import ConformerTool
            return ConformerTool(session, ti.name)
        
        elif ti.name == "Z-Matrix Builder":
            from .tools.zmat_builder import ZMatrixBuilder
            return ZMatrixBuilder(session, ti.name)

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
            from SEQCROW.io import open_aarontools, open_xyz

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

            elif name == "Q-Chem output file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_aarontools(
                            session,
                            data,
                            file_name,
                            format_name="Q-Chem output file",
                            **kw
                        )

                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg}

                return Info()

            elif name == "XYZ file" or name == "XYZ trajectory file":
                class Info(OpenerInfo):
                    def open(self, session, data, file_name, **kw):
                        return open_xyz(
                            session,
                            data,
                            file_name,
                            **kw
                        )

                    @property
                    def open_args(self):
                        return {'coordsets': BoolArg, 'maxModels': IntArg}

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
            elif name == "Q-Chem":
                from SEQCROW.input_file_formats import QChemFileInfo
                return QChemFileInfo()
            elif name == "xTB":
                from SEQCROW.input_file_formats import XTBFileInfo
                return XTBFileInfo()

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
            elif name == "Q-Chem":
                from SEQCROW.jobs import QChemJob
                return QChemJob
            elif name == "xTB":
                from SEQCROW.jobs import XTBJob
                return XTBJob
            elif name == "Raven":
                from SEQCROW.jobs import SerialRavenJob
                return SerialRavenJob
            elif name == "ParallelRaven":
                from SEQCROW.jobs import ParallelRavenJob
                return ParallelRavenJob
            elif name == "Gaussian STQN":
                from SEQCROW.jobs import GaussianSTQNJob
                return GaussianSTQNJob
            elif name == "ORCA NEB":
                from SEQCROW.jobs import ORCANEBJob
                return ORCANEBJob
            elif name == "Q-Chem FSM":
                from SEQCROW.jobs import QChemFSMJob
                return QChemFSMJob
            elif name == "CREST":
                from SEQCROW.jobs import CRESTJob
                return CRESTJob

        elif mgr is session.seqcrow_cluster_scheduling_software_manager:
            if name == "Slurm":
                return session.seqcrow_slurm_manager
            elif name == "SGE":
                return session.seqcrow_sge_manager
            elif name == "PBS":
                return session.seqcrow_pbs_manager
            elif name == "LSF":
                return session.seqcrow_lsf_manager

        elif mgr is session.seqcrow_slurm_manager:
            if name == "Gaussian":
                from .managers.cluster_template_manager import GaussianSlurmTemplate
                return GaussianSlurmTemplate
            
            elif name == "ORCA":
                from .managers.cluster_template_manager import ORCASlurmTemplate
                return ORCASlurmTemplate
            
            elif name == "Psi4":
                from .managers.cluster_template_manager import Psi4SlurmTemplate
                return Psi4SlurmTemplate
             
            elif name == "Q-Chem":
                from .managers.cluster_template_manager import QChemSlurmTemplate
                return QChemSlurmTemplate
            
            elif name == "SQM":
                from .managers.cluster_template_manager import SQMSlurmTemplate
                return SQMSlurmTemplate
             
            elif name == "xTB":
                from .managers.cluster_template_manager import XTBSlurmTemplate
                return XTBSlurmTemplate
 
            elif name == "CREST":
                from .managers.cluster_template_manager import CRESTSlurmTemplate
                return CRESTSlurmTemplate
 
        elif mgr is session.seqcrow_pbs_manager:
            if name == "Gaussian":
                from .managers.cluster_template_manager import GaussianPBSTemplate
                return GaussianPBSTemplate
            
            elif name == "ORCA":
                from .managers.cluster_template_manager import ORCAPBSTemplate
                return ORCAPBSTemplate
            
            elif name == "Psi4":
                from .managers.cluster_template_manager import Psi4PBSTemplate
                return Psi4PBSTemplate
             
            elif name == "Q-Chem":
                from .managers.cluster_template_manager import QChemPBSTemplate
                return QChemPBSTemplate
            
            elif name == "SQM":
                from .managers.cluster_template_manager import SQMPBSTemplate
                return SQMPBSTemplate
            
            elif name == "xTB":
                from .managers.cluster_template_manager import XTBPBSTemplate
                return XTBPBSTemplate

            elif name == "CREST":
                from .managers.cluster_template_manager import CRESTPBSTemplate
                return CRESTPBSTemplate

        elif mgr is session.seqcrow_sge_manager:
            if name == "Gaussian":
                from .managers.cluster_template_manager import GaussianSGETemplate
                return GaussianSGETemplate
            
            elif name == "ORCA":
                from .managers.cluster_template_manager import ORCASGETemplate
                return ORCASGETemplate
            
            elif name == "Psi4":
                from .managers.cluster_template_manager import Psi4SGETemplate
                return Psi4SGETemplate
             
            elif name == "Q-Chem":
                from .managers.cluster_template_manager import QChemSGETemplate
                return QChemSGETemplate
            
            elif name == "SQM":
                from .managers.cluster_template_manager import SQMSGETemplate
                return SQMSGETemplate
            
            elif name == "xTB":
                from .managers.cluster_template_manager import XTBSGETemplate
                return XTBSGETemplate

            elif name == "CREST":
                from .managers.cluster_template_manager import CRESTSGETemplate
                return CRESTSGETemplate

        elif mgr is session.seqcrow_lsf_manager:
            if name == "Gaussian":
                from .managers.cluster_template_manager import GaussianLSFTemplate
                return GaussianLSFTemplate
            
            elif name == "ORCA":
                from .managers.cluster_template_manager import ORCALSFTemplate
                return ORCALSFTemplate
            
            elif name == "Psi4":
                from .managers.cluster_template_manager import Psi4LSFTemplate
                return Psi4LSFTemplate
             
            elif name == "Q-Chem":
                from .managers.cluster_template_manager import QChemLSFTemplate
                return QChemLSFTemplate
            
            elif name == "SQM":
                from .managers.cluster_template_manager import SQMLSFTemplate
                return SQMLSFTemplate
            
            elif name == "xTB":
                from .managers.cluster_template_manager import XTBLSFTemplate
                return XTBLSFTemplate

            elif name == "CREST":
                from .managers.cluster_template_manager import CRESTLSFTemplate
                return CRESTLSFTemplate

        elif mgr is session.tss_finder_manager:
            if name == "GPR growing string method":
                from .tss_finder_methods import GPRGSM
                return GPRGSM()
            elif name == "synchornous transit-guided quasi-Newton":
                from .tss_finder_methods import STQN
                return STQN()
            elif name == "nudged elastic band":
                from .tss_finder_methods import NEB
                return NEB()
            elif name == "freezing string method":
                from .tss_finder_methods import FSM
                return FSM()
            elif name == "metadynamics pathfinding":
                from .tss_finder_methods import MDPF
                return MDPF()
        
        elif mgr is session.conformer_search_manager:
            if name == "CREST":
                from .conformer_search_formats import CREST
                return CREST()
            
            if name == "CREST QCG":
                from .conformer_search_formats import CRESTQCG
                return CRESTQCG()
 
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

            elif name == "substituent_sterimol":
                from .tests.substituent_sterimol import SubstituentSterimolToolTest
                return SubstituentSterimolToolTest

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
        
        elif command_info.name == "solidAngle":
            from .commands.solid_angle import solid_angle, solid_angle_description
            register("solidAngle", solid_angle_description, solid_angle)
        
        elif command_info.name == "force":
            from .commands.force import force, force_description
            register("force", force_description, force)

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
            add_selector(substituent_menu, sub)

        # connected selector
        mw = session.ui.main_window
        structure_menu = add_submenu([], '&Structure')
        structure_menu.addAction(QAction("Connected", mw))
        structure_menu.addAction(QAction("Chiral centers", mw))
        structure_menu.addAction(QAction("Spiro centers", mw))
        structure_menu.addAction(QAction("Bridgehead", mw))
        structure_menu.addAction(QAction("Rings", mw))
        
        vsepr_menu = add_submenu(['Che&mistry'], 'Shape')
        for vsepr in [
            "linear",
            "bent",
            "planar",
            "t-shaped",
            "trigonal planar",
            "tetrahedral",
            "sawhorse",
            "seesaw",
            "square planar",
            "trigonal pyramidal",
            "trigonal bipyramidal",
            "square pyramidal",
            "pentagonal",
            "octahedral",
            "hexagonal",
            "trigonal prismatic",
            "pentagonal pyramidal",
            "capped octahedral",
            "capped trigonal prismatic",
            "heptagonal",
            "hexagonal pyramidal",
            "pentagonal bipyramidal",
            "biaugmented trigonal prismatic",
            "cubic",
            "elongated trigonal bipyramidal",
            "hexagonal bipyramidal",
            "heptagonal pyramidal",
            "octagonal",
            "square antiprismatic",
            "trigonal dodecahedral",
            "capped cube",
            "capped square antiprismatic",
            "enneagonal",
            "hula-hoop",
            "tridiminished icosahedral",
            "muffin",
            "octagonal pyramidal",
            "tricapped trigonal prismatic",
        ]:
            add_selector(vsepr_menu, vsepr, selector_text=vsepr.replace(" ", "-"))

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
            print("yes")
            return FileReader
        elif name == "Orbitals":
            from AaronTools.fileIO import Orbitals
            print("yes")
            return Orbitals
        elif name == "Frequency":
            from AaronTools.spectra import Frequency
            print("yes")
            return Frequency
        elif name == "ValenceExcitations":
            from AaronTools.spectra import ValenceExcitations
            print("yes")
            return ValenceExcitations
        elif name == "HarmonicVibration":
            from AaronTools.spectra import HarmonicVibration
            print("yes")
            return HarmonicVibration
        elif name == "AnharmonicVibration":
            from AaronTools.spectra import AnharmonicVibration
            print("yes")
            return AnharmonicVibration
        elif name == "ValenceExcitation":
            from AaronTools.spectra import ValenceExcitation
            print("yes")
            return ValenceExcitation
        elif name == "Atom":
            from AaronTools.atoms import Atom
            print("yes")
            return Atom
        elif name == "Highlight":
            from SEQCROW.commands.highlight import Highlight
            print("yes")
            return Highlight
        elif name == "Theory":
            from AaronTools.theory import Theory
            print("yes")
            return Theory

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
                if model.session.seqcrow_settings.settings.ORBIT_OPEN != "do nothing":
                    try:
                        fr["orbitals"]
                        run(model.session, "ui tool show \"Orbital Viewer\"")
                        model.session.logger.info(
                            "automaticly opening the orbital tool can be disabled in the settings"
                        )
                    except Exception:
                        pass

                if model.session.seqcrow_settings.settings.FREQ_OPEN != "do nothing":
                    try:
                        fr["frequency"]
                        run(model.session, "ui tool show \"Visualize Normal Modes\"")
                        model.session.logger.info(
                            "automaticly opening the vibrations tool can be disabled in the settings"
                        )
                    except Exception:
                        pass

bundle_api = _SEQCROW_API()
