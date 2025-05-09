from glob import glob
import os

from AaronTools.const import AARONLIB, AARONTOOLS
from AaronTools.theory import *
from AaronTools.fileIO import FileWriter
from AaronTools.theory.implicit_solvent import KNOWN_XTB_SOLVENTS, KNOWN_ORCA_SOLVENTS

from SEQCROW.tools.input_generator import (
    KeywordOptions,
    OneLayerKeyWordOption,
    TwoLayerKeyWordOption,
)
from SEQCROW.input_file_formats import XTBKeywordOptions, ORCAKeywordOptions

from chimerax.ui.options import FloatOption, IntOption, BooleanOption, EnumOption


class ConformerSearchInfo:
    # name of program
    name = ""
    
    # options to put in the 'previous' section of the stuff on the 'additional options' tab
    # although the user hasn't used these before, they can be used to build intuation
    # for how the KeywordOptions can be used to add whatever options they want
    initial_options = dict()
    
    # whether this software is capable of running parallel threads
    parallel = True
    
    # whether memory can be specified
    memory = True

    # whether constrained search is available
    use_constraints = True

    # file filter for QFileDialog.getOpenFileName
    restart_filter = None
    
    # basis file filter
    basis_file_filter = None
    
    # filter for saving a file in this format
    save_file_filter = None

    # availale solvents
    # dict with the models as the keys and the list of solvents available
    # for that model as the values
    solvents = None
    
    # availale methods - should be list
    # special methods:
    # SAPT - will show a layer widget for selecting SAPT type and defining monomers
    methods = []

    # availale empirical dispersion
    # if there are no dispersion methods, the widget will be disabled
    # will be prepended with "None", the corresponding Theory for which will
    # have no emp dispersion
    dispersion = None
    
    # availale integration grids
    # if there are none, the widget will be disabled
    # will automatically be prepended with "Default", the corresponding
    # Theory for which will have no grid
    grids = None
    
    # availale basis sets
    # will be appended with 'other', allowing the user to enter basis set info
    basis_sets = []
    
    # auxiliary basis set types
    aux_options = None
    
    # availale ECP's
    # if there are no ECP's, the ECP widget will be hidden
    # will be appended with "other", which allows users to enter ECP info
    ecps = None
    
    # ECP differs (or can be specified separate from) valence basis set
    # if this is false, putting an element in an ECP will remove it
    # from the basis set and vice versa
    valence_basis_differs_from_ecp = True
    
    # misc. options
    # should be None ('additional options' tab will be disabled) or
    # a KeywordOptions subclass (not an instance, just the class)
    keyword_options = None

    def get_file_contents(self, theory):
        """
        returns file contents (str) and warnings (list of str)
        theory - AaronTools.theory Theory instance
        """
        raise NotImplementedError("cannot generate file contents for %s" % self.name)
    
    def get_local_job(self, session, name, theory, auto_update, auto_open):
        """
        get SEQCROW.jobs LocalJob instance for running a job on computer running ChimeraX
        session - ChimeraX session
        name - str, job name
        theory - AaronTools.theory Theory instance
        auto_update - bool, update the structure that was used to create the job once it is completed
        auto_open - bool, open the output file of the job when it completes
        """
        raise NotImplementedError("cannot run local jobs for %s" % self.name)

    def get_job_kw_dict(
            self,
            read_checkpoint,
            checkpoint_file,
    ):
        """
        get a keyword dictionary given the settings on the 'job details' tab
        optimize - bool, geometry optimization is checked
        frequencies - bool, frequency calculation is checked
        raman - bool, Raman intensities is checked
        hpmodes - bool, high-precision modes is checked
        read_checkpoint - bool, read checkpoint is checked
        checkpoint_file - str, path to checkpoint file
        """
        return dict()

    @staticmethod
    def fixup_theory(theory, restart_file=None):
        """
        modify the input theory to run the necessary job type
        if this is a dictionary, programs are keys
        and the values are callable
        otherwise, this is callable and works for all programs
        
        restart_file - path to file that can be used to restart
            the job
        """
        return theory


class ProtomersOption(EnumOption):
    values = ("deprotonate", "protonate", "tautomerize", "none")


class QCGOption(EnumOption):
    values = ("grow", "ensemble", "solvation free energy")


solvent_libs = [
    os.path.join(AARONTOOLS, "Solvents"),
    os.path.join(AARONLIB, "Solvents"),
]
solvents = []
for solvent_lib in solvent_libs:
    if not os.path.exists(solvent_lib):
        continue
    solvent_files = glob(os.path.join(solvent_lib, "*.xyz"))
    solvents.extend([os.path.basename(x[:-4]) for x in solvent_files])


class SolventOption(EnumOption):
    values = tuple(solvents)


class UphillMethodOption(EnumOption):
    values = ("Default", "GFNFF", "GFN0XTB", "GFN1XTB", "GFN2XTB")


class CREST(ConformerSearchInfo):
    # name of program
    name = "CREST"
    options = {
        "energy_window": (
            FloatOption, {
                "min": 2,
                "max": 100,
                "decimal_places": 1,
                "step": 1,
                "default": 6,
                "name": "energy threshold",
            }
        ),
        "RMSD_threshold": (
            FloatOption, {
                "min": 0.05,
                "max": 1.00,
                "step": 0.1,
                "default": 0.125,
                "name": "RMSD threshold",
            }
        ),
        "non_covalent_complex": (
            BooleanOption, {
                "default": False,
                "name": "non-covalent complex",
            }
        ),
        "tautomer_search": (
            ProtomersOption, {
                "default": "none",
                "name": "protonation screening",
            }
        ),
    }

    parallel = True
    memory = False
    save_file_filter = "xTB input file (*.xc)"
    solvents = KNOWN_XTB_SOLVENTS
    keyword_options = XTBKeywordOptions
    methods = [
        "GFN-FF",
        "GFN1-xTB",
        "GFN2-xTB",
        "GFN2-xTB//GFN-FF",
    ]
    basis_sets = None

    def get_file_contents(self, theory):
        contents, warnings = FileWriter.write_crest(
            theory.geometry, theory, outfile=False, return_warnings=True,
        )
        return contents, warnings   

    def fixup_theory(
        self,
        theory,
        energy_window=6,
        RMSD_threshold=0.125,
        non_covalent_complex=False,
        tautomer_search="none",
        restart_file=None,
    ):
        new_dict = {
            "command_line": {
                "ewin": ["%.1f" % energy_window],
                "rthr": ["%.3f" % RMSD_threshold],
            }
        }
        if non_covalent_complex:
            new_dict["command_line"]["nci"] = []
        if tautomer_search != "none":
            new_dict["command_line"][tautomer_search] = []
        
        theory.kwargs = combine_dicts(
            new_dict, theory.kwargs,
        )
        
        return theory

    def get_job_kw_dict(
        self,
        read_checkpoint,
        checkpoint_file,
    ):
        """
        get a keyword dictionary given the settings on the 'job details' tab
        read_checkpoint - bool, read checkpoint is checked
        checkpoint_file - str, path to checkpoint file
        """
        return dict()


class CRESTQCG(ConformerSearchInfo):
    # name of program
    name = "CREST QCG"
    options = {
        "number_of_solvents": (
            IntOption, {
                "min": 1,
                "max": 300,
                "default": 10,
                "name": "number of solvent mols",
            }
        ),
        "algorithm": (
            QCGOption, {
                "default": "grow",
                "name": "solvation algorithm",
            }
        ),
        "solvent": (
            SolventOption, {
                "default": "water",
                "name": "solvent",
            }
        ),
    }

    parallel = True
    memory = False
    save_file_filter = "xTB input file (*.xc)"
    solvents = KNOWN_XTB_SOLVENTS
    keyword_options = XTBKeywordOptions
    methods = [
        "GFN-FF",
        "GFN1-xTB",
        "GFN2-xTB",
    ]
    basis_sets = None

    def get_file_contents(self, theory):
        contents, warnings = FileWriter.write_crest(
            theory.geometry, theory, outfile=False, return_warnings=True,
        )
        solvent_name = theory.kwargs["command_line"]["qcg"][0]
        for solvent_lib in solvent_libs:
            if not os.path.exists(solvent_lib):
                continue
            
            solvent_files = glob(os.path.join(solvent_lib, "*.xyz"))
            for sol_file in solvent_files:
                fname = os.path.basename(sol_file)
                if fname == solvent_name:
                    with open(sol_file, "r") as f:
                        solvent_xyz = f.read()
                    contents[solvent_name] = solvent_xyz
                    break
        
        return contents, warnings   

    def fixup_theory(
        self,
        theory,
        algorithm="grow",
        number_of_solvents=10,
        solvent="water",
        restart_file=None,
    ):
        new_dict = {"command_line": {}}
        
        algo_name = {
            "grow": "grow",
            "ensemble": "ensemble",
            "solvation free energy": "gsolv",
        }[algorithm]
        
        new_dict["command_line"][algo_name] = []
        new_dict["command_line"]["nsolv"] = [str(number_of_solvents)]
        new_dict["command_line"]["qcg"] = [solvent + ".xyz"]

        theory.kwargs = combine_dicts(
            new_dict, theory.kwargs,
        )
        theory.job_type = []
        
        return theory

    def get_job_kw_dict(
        self,
        read_checkpoint,
        checkpoint_file,
    ):
        """
        get a keyword dictionary given the settings on the 'job details' tab
        read_checkpoint - bool, read checkpoint is checked
        checkpoint_file - str, path to checkpoint file
        """
        return dict()


class GOAT(ConformerSearchInfo):
    # name of program
    name = "ORCA"
    options = {
        "energy_window": (
            FloatOption, {
                "min": 2,
                "max": 100,
                "decimal_places": 1,
                "step": 1,
                "default": 6,
                "name": "energy threshold",
            }
        ),
        "use_topology": (
            BooleanOption, {
                "default": True,
                "name": "use topology",
            }
        ),
        "workers": (
            IntOption, {
                "min": 0,
                "max": 64,
                "default": 8,
                "name": "workers",
            }
        ),
        "optimization_cores": (
            IntOption, {
                "min": 1,
                "max": 128,
                "default": 8,
                "name": "preopt. cores",
            }
        ),
        "uphill_method": (
            UphillMethodOption, {
                "default": "Default",
                "name": "uphill push L.O.T.",
            }
        )
    }

    parallel = True
    memory = True
    save_file_filter = "ORCA input file (*.inp)"
    solvents = KNOWN_ORCA_SOLVENTS
    keyword_options = ORCAKeywordOptions
    methods = [
        "xTB",
        "AM1",
        "HF-3c",
        "B3LYP",
        "r2SCAN-3c",
    ]
    basis_sets = [
        "STO-3G",
        "def2-SVP",
    ]

    def get_file_contents(self, theory):
        contents, warnings = FileWriter.write_file(
            theory.geometry, theory=theory, style="orca", outfile=False, return_warnings=True,
        )
        return contents, warnings   

    def fixup_theory(
        self,
        theory,
        energy_window=6,
        use_topology=True,
        workers=8,
        optimization_cores=8,
        uphill_method=None,
        restart_file=None,
    ):
        for job in theory.job_type:
            if hasattr(job, "use_topology"):
                job.use_topology = use_topology
                
        new_dict = {
            ORCA_BLOCKS: {
                "goat": [
                    "MaxEn %.1f" % energy_window,
                    "MaxCoresOpt %i" % optimization_cores,
                ],
            }
        }
        if uphill_method and uphill_method != "Default":
            new_dict[ORCA_BLOCKS]["goat"].append("GFNUphill %s" % uphill_method)
        if workers == 0:
            new_dict[ORCA_BLOCKS]["goat"].append("NWorkers Auto")
        else:
            new_dict[ORCA_BLOCKS]["goat"].append("NWorkers %i" % workers)
        
        new_dict[ORCA_BLOCKS]["goat"].append("Align True")

        theory.kwargs = combine_dicts(
            new_dict, theory.kwargs,
        )
        
        return theory

    def get_job_kw_dict(
        self,
        read_checkpoint,
        checkpoint_file,
    ):
        """
        get a keyword dictionary given the settings on the 'job details' tab
        read_checkpoint - bool, read checkpoint is checked
        checkpoint_file - str, path to checkpoint file
        """
        return dict()


class AaronToolsConf(ConformerSearchInfo):
    # name of program
    name = "AaronTools Conformer Generation"
    options = {
        "RMSD_threshold": (
            FloatOption, {
                "min": 0.05,
                "max": 1.00,
                "step": 0.1,
                "default": 0.125,
                "name": "RMSD threshold",
            }
        ),
        "search_rings": (
            BooleanOption, {
                "default": True,
                "name": "simple ring conformers",
            }
        ),
        "relax": (
            BooleanOption, {
                "default": True,
                "name": "relax steric clashes",
            }
        ),
        "optimization_cores": (
            IntOption, {
                "min": 1,
                "max": 128,
                "default": 8,
                "name": "preopt. cores",
            }
        ),
    }
    
    solvents = None
    parallel = True
    memory = True
    basis_sets = None
    methods = [
        "None",
        # TODO: run opt right after conf search
        # "AM1 (SQM)",
        # "RM1 (SQM)",
        # "PM3 (ORCA)",
        # "PM3 (Gaussian)",
        # "PM6 (SQM)",
        # "PM6 (Gaussian)",
        # "PM7 (Gaussian)",
        # "HF-3c (ORCA)",
        # "GFNFF (xTB)",
        # "GFN1XTB (xTB)",
        # "GFN2XTB (xTB)",
        # "r2SCAN-3c (ORCA)",
    ]

    def get_file_contents(self, theory):
        try:
            method, program = theory.method.name.split()
            program = program[1:-1]
            theory.method = method
            theory.job_type = OptimizationJob()
            theory.kwargs["comment"] = ["input file shown for optimization of each conformer"]
            contents, warnings = FileWriter.write_file(
                theory.geometry, theory=theory, style=program, outfile=False, return_warnings=True,
            )
            return contents, warnings
        except ValueError:
            return "Python API will be used to generate conformers", []

    def fixup_theory(
        self,
        theory,
        RMSD_threshold=0.125,
        search_rings=True,
        relax=True,
        restart_file=None,
    ):
        theory.kwargs = {
            "RMSD_threshold": RMSD_threshold,
            "search_rings": search_rings,
            "relax": relax,
        }
        return theory

    def get_job_kw_dict(
        self,
        read_checkpoint,
        checkpoint_file,
    ):
        """
        get a keyword dictionary given the settings on the 'job details' tab
        read_checkpoint - bool, read checkpoint is checked
        checkpoint_file - str, path to checkpoint file
        """
        return dict()

