"""
things used to construct input files for the QM Input File Builder and
run local jobs using the input files
"""

import re

from AaronTools.theory import *
from AaronTools.fileIO import FileWriter
from AaronTools.theory.implicit_solvent import (
    KNOWN_GAUSSIAN_SOLVENTS,
    KNOWN_ORCA_SOLVENTS,
    KNOWN_PSI4_SOLVENTS,
    KNOWN_XTB_SOLVENTS,
)

from SEQCROW.tools.input_generator import (
    KeywordOptions,
    OneLayerKeyWordOption,
    TwoLayerKeyWordOption,
)


class QMInputFileInfo:
    # name of program
    name = ""
    
    # whether or not this file type will work with raven
    # aka the TSS Finder tool
    allow_raven = False
    
    # preset settings for this software
    # dict with keys:
    #    theory - Theory instance
    #    use_other - bool, use Theory's kwargs attribute (assumed True if  
    #                 Theory.kwargs is not empty)
    #    hpmodes - bool, high-precision modes is checked
    #    raman - bool, raman intensities is checked (ignored unless theory 
    #            has a FrequencyJob)
    initial_presets = dict()
    
    # options to put in the 'previous' section of the stuff on the 'additional options' tab
    # although the user hasn't used these before, they can be used to build intuation
    # for how the KeywordOptions can be used to add whatever options they want
    initial_options = dict()
    
    # whether this software is capable of running parallel threads
    parallel = True
    
    # whether memory can be specified
    memory = True
    
    # whether optimization jobs are available
    optimization = True
    
    # whether TS optimization is available
    ts_optimization = True
    
    # whether constrained optimization is available
    const_optimization = True
        
    # whether coordinate scans are available
    coordinate_scan = True
    
    # whether frequency jobs are available
    frequency = True
    
    # whether NMR jobs are available
    nmr = False
    
    # only one job type per input file
    single_job_type = False
    
    # file filter for QFileDialog.getOpenFileName
    # if None, will be disabled when 'read checkpoint' is checked
    save_checkpoint_filter = None
    
    # file filter for QFileDialog.getSaveFileName
    # if None, will be disabled when 'read checkpoint' is unchecked
    read_checkpoint_filter = None
    
    # basis file filter
    basis_file_filter = None
    
    # filter for saving a file in this format
    save_file_filter = None
    
    # whether or not Raman intensities can be computed
    raman_available = False
    
    # whether or not high-precision vibrational mode dispacement vectors can be requested
    # basically Gaussian-only option
    hpmodes_available = False

    # availale solvents
    # dict with the models as the keys and the list of solvents available
    # for that model as the values
    solvents = None
    
    # availale methods - should be list
    # special methods:
    # SAPT - will show a layer widget for selecting SAPT type and defining monomers
    methods = []
    
    # methods available for Raven
    # will use methods if there aren't any
    raven_methods = None
    
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
            optimize,
            frequencies,
            raman,
            hpmodes,
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


class GaussianKeywordOptions(KeywordOptions):
    items = {
        'route': GAUSSIAN_ROUTE,
        'link 0': GAUSSIAN_PRE_ROUTE,
        'comment': GAUSSIAN_COMMENT,
        'end of file': GAUSSIAN_POST,
    }

    #the keys used to be an int map before this stuff got moved to AaronTools
    #old_items allows users to keep old settings
    old_items = {
        'link 0': "1",
        'comment': "8",
        'route': "2",
        'end of file': "7",
    }

    previous_option_name = "previous_gaussian_options"
    last_option_name = "last_gaussian_options"

    @classmethod
    def get_options_for(cls, name, last, previous):
        if name == "route":
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            return TwoLayerKeyWordOption(
                "keywords",
                last_dict,
                previous_dict,
                "double click to add %s=(%s)",
                one_opt_per_kw=False
            )

        elif name == "comment":
            if last is None:
                last_list = []
            else:
                last_list = last

            if previous is None:
                previous_list = []
            else:
                previous_list = previous

            return OneLayerKeyWordOption(
                "comment",
                last_list,
                previous_list,
                multiline=True
            )

        elif name == "end of file":
            if last is None:
                last_list = []
            else:
                last_list = last

            if previous is None:
                previous_list = []
            else:
                previous_list = previous

            return OneLayerKeyWordOption(
                "end of file",
                last_list, previous_list,
                multiline=True
            )

        elif name == "link 0":
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            return TwoLayerKeyWordOption(
                "link 0",
                last_dict,
                previous_dict,
                "double click to use %%%s=%s",
                one_opt_per_kw=False
            )


class ORCAKeywordOptions(KeywordOptions):
    items = {
        'simple keywords': ORCA_ROUTE,
        'blocks': ORCA_BLOCKS,
        'comment': ORCA_COMMENT,
    }

    old_items = {
        'simple keywords': "1",
        'comment': "4",
        'blocks': "2",
    }

    previous_option_name = "previous_orca_options"
    last_option_name = "last_orca_options"

    @classmethod
    def get_options_for(cls, name, last, previous):
        if name == "simple keywords":
            if last is None:
                last_list = []
            else:
                last_list = last

            if previous is None:
                previous_list = []
            else:
                previous_list = previous

            return OneLayerKeyWordOption("keyword", last_list, previous_list, multiline=False)

        elif name == "comment":
            if last is None:
                last_list = []
            else:
                last_list = last

            if previous is None:
                previous_list = []
            else:
                previous_list = previous

            return OneLayerKeyWordOption("comment", last_list, previous_list, multiline=True)

        elif name == "blocks":
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            return TwoLayerKeyWordOption("blocks", last_dict, previous_dict, "double click to use %%%s %s end", one_opt_per_kw=False)


class Psi4KeywordOptions(KeywordOptions):   
    items = {
        'settings': PSI4_SETTINGS, 
        'job': PSI4_JOB, 
        'molecule': PSI4_MOLECULE, 
        'before job': PSI4_BEFORE_JOB, 
        'after job': PSI4_AFTER_JOB, 
        'optking': PSI4_OPTKING, 
        'before molecule': PSI4_BEFORE_GEOM, 
        'PCM solver': PSI4_SOLVENT,
        'comment': PSI4_COMMENT, 
    }

    old_items = {'settings': "1", \
                 'before molecule': "2", \
                 'molecule': "5", \
                 'before job': "3", \
                 'comment': "4", \
                 'job': "6", \
                }

    previous_option_name = "previous_psi4_options"
    last_option_name = "last_psi4_options"

    @classmethod
    def get_options_for(cls, name, last, previous):
        if name == "job":
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            return TwoLayerKeyWordOption(
                "job",
                last_dict,
                previous_dict,
                "double click to use \"%s(%s)\"",
                one_opt_per_kw=False
            )

        if name == "after job":
            if last is None:
                last_list = []
            else:
                last_list = last

            if previous is None:
                previous_list = []
            else:
                previous_list = previous

            return OneLayerKeyWordOption("after job", last_list, previous_list, multiline=True)

        if name == "before job":
            if last is None:
                last_list = []
            else:
                last_list = last

            if previous is None:
                previous_list = []
            else:
                previous_list = previous

            return OneLayerKeyWordOption("after job", last_list, previous_list, multiline=True)

        elif name == "before molecule":
            if last is None:
                last_list = []
            else:
                last_list = last

            if previous is None:
                previous_list = []
            else:
                previous_list = previous

            return OneLayerKeyWordOption("before molecule", last_list, previous_list, multiline=True)

        elif name == "comment":
            if last is None:
                last_list = []
            else:
                last_list = last

            if previous is None:
                previous_list = []
            else:
                previous_list = previous

            return OneLayerKeyWordOption("comment", last_list, previous_list, multiline=True)

        elif name == "settings":
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            def check_single_kw(kw):
                return any(kw.strip().lower() == sk for sk in Theory.FORCED_PSI4_SINGLE)

            return TwoLayerKeyWordOption(
                "settings",
                last_dict,
                previous_dict,
                "double click to use \"set { %s %s }\"",
                one_opt_per_kw=check_single_kw,
                allow_dup=True,
            )

        elif name == "PCM solver":
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            def check_single_kw(kw):
                return any(kw.strip().lower() == sk for sk in Theory.FORCED_PSI4_SOLVENT_SINGLE)

            return TwoLayerKeyWordOption(
                "PCM solver",
                last_dict,
                previous_dict,
                "double click to use \"pcm = { %s = %s }\"",
                one_opt_per_kw=check_single_kw,
                allow_dup=False,
            )

        elif name == "optking":
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            return TwoLayerKeyWordOption(
                "optking settings",
                last_dict,
                previous_dict,
                "double click to use \"set optking { %s %s }\"",
                one_opt_per_kw=True
            )

        elif name == "molecule":
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            return TwoLayerKeyWordOption(
                "molecule options",
                last_dict,
                previous_dict,
                "double click to use \"%s %s\"",
                one_opt_per_kw=True
            )


class SQMKeywordOptions(KeywordOptions):
    items = {
        'settings': SQM_QMMM,
        'comment': SQM_COMMENT,
    }


    previous_option_name = "previous_sqm_options"
    last_option_name = "last_sqm_options"

    @classmethod
    def get_options_for(cls, name, last, previous):
        if name == 'settings':
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            return TwoLayerKeyWordOption(
                "settings",
                last_dict,
                previous_dict,
                "double click to use \"%s %s\"",
                one_opt_per_kw=True,
                allow_dup=False,
            )

        elif name == 'comment':
            if last is None:
                last_list = []
            else:
                last_list = last

            if previous is None:
                previous_list = []
            else:
                previous_list = previous

            return OneLayerKeyWordOption(
                "comment",
                last_list,
                previous_list,
                multiline=True,
            )


class QChemKeywordOptions(KeywordOptions):
    items = {
        'settings': QCHEM_REM,
        'sections': QCHEM_SETTINGS,
        'comment': QCHEM_COMMENT,
    }

    previous_option_name = "previous_qchem_options"
    last_option_name = "last_qchem_options"

    @classmethod
    def get_options_for(cls, name, last, previous):
        if name == 'settings':
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            return TwoLayerKeyWordOption(
                'settings',
                last_dict,
                previous_dict,
                "double click to use $rem\n\t%s = %s\n$end",
                one_opt_per_kw=True,
                allow_dup=False,
            )

        elif name == 'comment':
            if last is None:
                last_list = []
            else:
                last_list = last

            if previous is None:
                previous_list = []
            else:
                previous_list = previous

            return OneLayerKeyWordOption(
                'comment',
                last_list,
                previous_list,
                multiline=True,
            )

        elif name == 'sections':
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            return TwoLayerKeyWordOption(
                'sections',
                last_dict,
                previous_dict,
                "double click to use $%s\n\t%s\n$end",
                one_opt_per_kw=False,
                allow_dup=True,
                banned_settings=["rem"],
            )


class XTBKeywordOptions(KeywordOptions):
    items = {
        'xcontrol': XTB_CONTROL_BLOCKS,
        'command line': XTB_COMMAND_LINE,
    }

    previous_option_name = "previous_xtb_options"
    last_option_name = "last_xtb_options"

    @classmethod
    def get_options_for(cls, name, last, previous):
        if name == 'xcontrol':
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            return TwoLayerKeyWordOption(
                'xcontrol',
                last_dict,
                previous_dict,
                "double click to use $%s\n\t%s\n$end",
                one_opt_per_kw=True,
                allow_dup=False,
            )
            
        if name == 'command line':
            if last is None:
                last_dict = {}
            else:
                last_dict = last

            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous

            return TwoLayerKeyWordOption(
                'command line',
                last_dict,
                previous_dict,
                "double click to use --%s %s",
                one_opt_per_kw=True,
                allow_dup=False,
            )


class GaussianFileInfo(QMInputFileInfo):
    name = "Gaussian"

    nmr = True

    initial_options = {
        GAUSSIAN_ROUTE: {
            'opt': ['NoEigenTest', 'Tight', 'VeryTight'],
            'DensityFit': [],
            'pop': ['NBO', 'NBOREAD', 'NBO7'],
            'scrf': ['COSMORS'],
            'Integral': ['grid=99302'],
        },
        GAUSSIAN_COMMENT:[],
        GAUSSIAN_PRE_ROUTE: {
            'LindaWorkers':
                #I found this example online at
                # http://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/m_linda.htm
                #I don't know if it works (I don't use linda)
                ["spain", "hamlet:2", "ophelia:4"],
        },
        GAUSSIAN_POST: [
            '$nbo RESONANCE NBOSUM E2PERT=0.0 NLMO BNDIDX $end'
        ],
    }

    initial_presets = {
        "quick optimize": {
            "theory": Theory(
                job_type=OptimizationJob(),
                method="PM6",
            ),
            "use_other": True,
            "use_method": True,
            "use_job_type": True,     
            "use_basis": True,
        }
    }

    save_file_filter = "Gaussian input files (*.com *.gjf)"
    basis_file_filter = "Basis Set Files (*.gbs)"
    save_checkpoint_filter = "Gaussian checkpoint files (*.chk)"
    read_checkpoint_filter = "Gaussian checkpoint files (*.chk)"
    raman_available = True
    hpmodes_available = True
    solvents = KNOWN_GAUSSIAN_SOLVENTS
    methods = [
        "B3LYP",
        "M06",
        "M06-L",
        "M06-2X",
        "ωB97X-D",
        "B3PW91",
        "B97-D",
        "BP86",
        "PBE0",
        "PM6",
        "AM1"
    ]
    dispersion = [
        "Grimme D2",
        "Zero-damped Grimme D3",
        "Becke-Johnson damped Grimme D3",
        "Petersson-Frisch"
    ]
    grids = [
        "SuperFineGrid",
        "UltraFine",
        "FineGrid"
    ]
    basis_sets = [
        "def2-SVP",
        "def2-TZVP",
        "cc-pVDZ",
        "cc-pVTZ",
        "aug-cc-pVDZ",
        "aug-cc-pVTZ",
        "6-311+G**",
        "SDD",
        "LANL2DZ"
    ]
    ecps = ["SDD", "LANL2DZ"]
    keyword_options = GaussianKeywordOptions
    
    def get_file_contents(self, theory):
        """creates Gaussian input file using AaronTools"""
        header, header_warnings = theory.make_header(style="gaussian", return_warnings=True)
        molecule, mol_warnings = theory.make_molecule(style="gaussian", return_warnings=True)
        footer, footer_warnings = theory.make_footer(style="gaussian", return_warnings=True)
        contents = header + molecule + footer
        contents = re.sub("{{\s?name\s?}}", theory.geometry.name, contents)
        warnings = header_warnings + mol_warnings + footer_warnings
        return contents, warnings

    def get_job_kw_dict(
            self,
            optimize,
            frequencies,
            raman,
            hpmodes,
            read_checkpoint,
            checkpoint_file,
    ):
        route = {}
        if optimize:
            route['opt'] = []

        if frequencies:
            route['freq'] = []

            if raman:
                route['freq'].append("Raman")

            if hpmodes:
                route['freq'].append('HPModes')

        link0 = {}

        #XXX: Move to AaronTools theory
        if read_checkpoint:
            for kw in route:
                if kw == "opt":
                    route[kw].append("ReadFC")
                elif kw == "irc" :
                    #apparently, IRC can only read cartesian force constants and not interal coords
                    #opt can do ReadFC and ReadCartesianFC, but I'm just going to pick ReadCartesianFC
                    route[kw].append("ReadCartesianFC")

            route["guess"] = ["read"]

        if checkpoint_file:
            link0["chk"] = [checkpoint_file]

        return {GAUSSIAN_PRE_ROUTE:link0, GAUSSIAN_ROUTE:route}


class ORCAFileInfo(QMInputFileInfo):
    name = "ORCA"

    nmr = True

    initial_presets = {
        "quick optimize":{
            "theory": Theory(
                job_type=OptimizationJob(),
                method="HF-3c",
            ),
            "use_method": True,
            "use_job_type": True,
            "use_other": True,
            "use_basis": True,
        },
        "DLPNO single-point":{
            "theory": Theory(
                method="DLPNO-CCSD(T)",
                basis="cc-pVTZ aux C cc-pVTZ",
                simple=["TightSCF", "SP"],
            ),
            "use_method": True,
            "use_basis": True,
            "use_other": True,
            "use_job_type": True,
        },
    }
    
    initial_options = {
        ORCA_ROUTE: ['TightSCF'],
        ORCA_BLOCKS: {
            'basis': ['decontract true'],
            'elprop': ['Quadrupole True'],
            'freq': ['Increment 0.001'],
            'geom': ['Calc_Hess true'],
        },
    }
    
    save_file_filter = "ORCA input files (*.inp)"
    basis_file_filter = "Basis Set Files (*.basis)"
    read_checkpoint_filter = "ORCA orbital files (*.gbw);;ORCA Hessian files (*.hess)"
    raman_available = True
    solvents = KNOWN_ORCA_SOLVENTS
    methods = [
        "B3LYP",
        "M06",
        "M06-L",
        "M06-2X",
        "ωB97X-D3",
        "B3PW91",
        "B97-D3",
        "BP86",
        "PBE0",
        "HF-3c",
        "AM1"
    ]
    dispersion = [
        "Grimme D2",
        "Zero-damped Grimme D3",
        "Becke-Johnson damped Grimme D3",
        "Grimme D4"
    ]
    grids = {
        "DefGrid3 (ORCA 5)": "DefGrid3",
        "DefGrid2 (ORCA 5)": "DefGrid2",
        "DefGrid1 (ORCA 5)": "DefGrid1",
        "Grid7 (ORCA 4)": "Grid7",
        "Grid6 (ORCA 4)": "Grid6",
        "Grid5 (ORCA 4)": "Grid5",
        "Grid4 (ORCA 4)": "Grid4",
    }
    basis_sets = {
        "no": [
            "def2-SVP",
            "def2-TZVP",
            "cc-pVDZ",
            "cc-pVTZ",
            "aug-cc-pVDZ",
            "aug-cc-pVTZ",
            "6-311+G**",
            "ZORA-def2-SVP",
            "SARC-ZORA-SVP",
            "ZORA-def2-TZVP",
            "SARC-ZORA-TZVP",
            "DKH-def2-TZVP",
            "SARC-DKH-TZVP",
            "D95",
            "LANL2DZ",
        ],
        "C": [
            "def2-SVP",
            "def2-TZVP",
            "cc-pVDZ",
            "cc-pVTZ",
            "cc-pVDZ-PP",
            "cc-pVTZ-PP",
            "aug-cc-pVDZ",
            "aug-cc-pVTZ",
            "aug-cc-pVDZ-PP",
            "aug-cc-pVTZ-PP",
        ],
        "J": [
            "def2",
            "SARC",
        ],
        "JK": [
            "def2",
            "cc-pVDZ",
            "cc-pVTZ",
            "cc-pVQZ",
            "aug-cc-pVDZ",
            "aug-cc-pVTZ",
            "aug-cc-pVQZ",
        ],
        "CABS": [
            "cc-pVDZ-F12",
            "cc-pVTZ-F12",
            "cc-pVQZ-F12",
        ],
        "OptRI CABS": [
            "cc-pVDZ-F12",
            "cc-pVTZ-F12",
            "cc-pVQZ-F12",
            "aug-cc-pVDZ-F12",
            "aug-cc-pVTZ-F12",
            "aug-cc-pVQZ-F12",
            "aug-cc-pVDZ-PP-F12",
            "aug-cc-pVTZ-PP-F12",
        ],
    }
    aux_options = BasisSet.ORCA_AUX
    ecps = ["def2-ECP", "dhf-ECP", "SK-MCDHF-RSC", "HayWadt", "SDD"]
    keyword_options = ORCAKeywordOptions
    
    def get_file_contents(self, theory):
        """creates ORCA input file using AaronTools"""
        header, header_warnings = theory.make_header(style="orca", return_warnings=True)
        footer = theory.make_footer(style="orca", return_warnings=False)
        molecule = ""
        fmt = "{:<3s} {: 10.6f} {: 10.6f} {: 10.6f}\n"
        for atom in theory.geometry.atoms:
            if atom.is_dummy:
                molecule += fmt.format("DA", *atom.coords)
                continue
            molecule += fmt.format(atom.element, *atom.coords)

        molecule += "*\n"
        contents = header + molecule + footer
        contents = re.sub("{{\s?name\s?}}", theory.geometry.name, contents)
        warnings = header_warnings
        return contents, warnings

    def get_job_kw_dict(
            self,
            optimize,
            frequencies,
            raman,
            hpmodes,
            read_checkpoint,
            checkpoint_file,
    ):
        route = []
        blocks = {}

        if frequencies:
            if raman:
                blocks['elprop'] = ['Polar 1']

        if read_checkpoint:
            for chk_file in checkpoint_file.split(";"):
                chk_file = chk_file.strip()
                if chk_file and chk_file.endswith("gbw"):
                    blocks["scf"] = [
                        "guess MORead",
                        "MOInp \"%s\"" % chk_file,
                    ]
                
                elif chk_file and chk_file.endswith("hess"):
                    blocks["geom"] = [
                        "inHess Read",
                        "inHessName \"%s\"" % chk_file,
                    ]

        return {ORCA_ROUTE:route, ORCA_BLOCKS:blocks}


class Psi4FileInfo(QMInputFileInfo):
    name = "Psi4"
    coordinate_scan = False

    save_file_filter = "Psi4 input files (*.in)"
    basis_file_filter = "Basis Set Files (*.gbs)"
    initial_presets = {
        "quick optimize": {
            "theory": Theory(
                method="HF",
                basis="STO-3G",
                job_type=OptimizationJob(),
            ),
            "use_other": True,
            "use_method": True,
            "use_basis": True,
            "use_job_type": True,
        },
    }
    
    initial_options = {
        PSI4_SETTINGS: {
            'reference': ['rhf', 'rohf', 'uhf', 'cuhf', 'rks', 'uks'],
            'cubeprop_tasks': ["frontier_orbitals"],
        },
        PSI4_BEFORE_GEOM: [],
        PSI4_BEFORE_JOB: [
            'activate(auto_fragments())', "mol = get_active_molecule()"
        ],
        PSI4_JOB: {
            'energy': ['return_wfn=True'],
            'optimize': ['return_wfn=True', "engine='geometric'"],
            'gradient': ['return_wfn=True'],
            'frequencies': [
                'return_wfn=True',
                'dertype=\'gradient\'',
                'dertype=\'energy\'',
            ],
        },
        PSI4_COMMENT: [],
        PSI4_MOLECULE: {
            'units': ['angstrom', 'bohr'],
            'pubchem': ['benzene'],
            'symmetry': ['c1', 'c2', 'ci', 'cs', 'd2', 'c2h', 'c2v', 'd2h'],
            'no_reorient': [],
            'no_com': [],
        },
        PSI4_AFTER_JOB: [
            "fchk(wfn, '{{ name }}.fchk')",
            "cubeprop(wfn)",
        ],
    }
    
    raven_methods = [
        "B3LYP",
        "M06",
        "M06-L",
        "M06-2X",
        "ωB97X-D",
        "B3PW91",
        "B97-D",
        "BP86",
        "PBE0",
    ]    
    methods = [
        "B3LYP",
        "M06",
        "M06-L",
        "M06-2X",
        "ωB97X-D",
        "B3PW91",
        "B97-D",
        "BP86",
        "PBE0",
        "SAPT",
        "CCSD",
        "CCSD(T)"
    ]
    dispersion = [
        "Grimme D1",
        "Grimme D2",
        "Zero-damped Grimme D3",
        "Becke-Johnson damped Grimme D3",
        "Becke-Johnson damped modified Grimme D3",
        "Chai & Head-Gordon",
        "Nonlocal Approximation",
        "Pernal, Podeszwa, Patkowski, & Szalewicz",
        "Podeszwa, Katarzyna, Patkowski, & Szalewicz",
        "Řezác, Greenwell, & Beran",
        "Coupled-Cluster Doubles",
        "Coupled-Cluster Doubles + Řezác, Greenwell, & Beran",
    ]
    grids = [
        "(250, 974)",
        "(175, 974)",
        "(60, 770)",
        "(99, 590)",
        "(55, 590)",
        "(50, 434)",
        "(75, 302)",
    ]
    basis_sets = [
        "def2-SVP",
        "def2-TZVP",
        "cc-pVDZ",
        "cc-pVTZ",
        "aug-cc-pVDZ",
        "aug-cc-pVTZ",
        "6-311+G**",
    ]
    solvents = KNOWN_PSI4_SOLVENTS
    aux_options = BasisSet.PSI4_AUX
    keyword_options = Psi4KeywordOptions
    
    def get_file_contents(self, theory):
        """creates Psi4 input file using AaronTools"""
        header, header_warnings = theory.make_header(style="psi4", return_warnings=True)
        molecule, mol_warnings = theory.make_molecule(style="psi4", return_warnings=True)
        footer, footer_warnings = theory.make_footer(style="psi4", return_warnings=True)
        contents = header + molecule + footer
        contents = re.sub("{{\s?name\s?}}", theory.geometry.name, contents)
        warnings = header_warnings + mol_warnings + footer_warnings
        return contents, warnings


class SQMFileInfo(QMInputFileInfo):
    name = "SQM"
    
    parallel = False
    memory = False
    ts_optimization = False
    const_optimization = False
    coordinate_scan = False
    frequency = False
    save_file_filter = "AMBER input files (*.mdin)"
    basis_file_filter = None
    initial_presets = {
        "quick optimize" : {
            "theory": Theory(
                method="AM1",
                job_type=OptimizationJob(),
            ),
            "use_other": True,
            "use_method": True,
            "use_basis": True,
            "use_job_type": True,
        },
    }
    
    initial_options = {
        "qmmm": {
            "verbosity": ["0", "1", "2", "3", "4", "5"],
        }
    }

    methods = [
        "PM6",
        "AM1",
        "RM1",
        "PM3",
    ]

    basis_sets = None
    keyword_options = SQMKeywordOptions

    def get_job_kw_dict(
            self,
            optimize,
            frequencies,
            *args,
    ):
        if not optimize and not frequencies:
            return {SQM_QMMM: {"maxcyc": ["0"]}}
        return dict()

    def get_file_contents(self, theory):
        """gets contents for amber's sqm input file"""
        header, header_warnings = theory.make_header(style="sqm", return_warnings=True)
        molecule, mol_warnings = theory.make_molecule(style="sqm", return_warnings=True)
        contents = header + molecule
        contents = re.sub("{{\s?name\s?}}", theory.geometry.name, contents)
        warnings = header_warnings + mol_warnings
        return contents, warnings


class QChemFileInfo(QMInputFileInfo):
    name = "Q-Chem"

    single_job_type = True
    
    initial_presets = {
        "quick optimize":{
            "theory": Theory(
                job_type=OptimizationJob(),
                method="HF-3c",
                basis="MINIX",
            ),
            "use_method": True,
            "use_job_type": True,
            "use_other": True,
            "use_basis": True,
        },
    }
    
    initial_options = {
        QCHEM_REM: {
            "SCF_MAX_CYCLES": ["150"],
            "JOB_TYPE": ["NMR", "Force", "SP"],
            "IQMOL_FCHK": ["TRUE"],
        },
    }
    
    save_file_filter = "Q-Chem input files (*.inp *.inq)"
    basis_file_filter = "Basis Set Files (*.basis)"
    raman_available = True
    methods = [
        "B3LYP",
        "M06",
        "M06-L",
        "M06-2X",
        "ωB97X-D3",
        "B3PW91",
        "B97-D3",
        "BP86",
        "PBE0",
        "HF-3c",
    ]
    dispersion = [
        "Grimme D2",
        "Modified Zero-damped Grimme D3",
        "Zero-damped Grimme D3",
        "Becke-Johnson damped Grimme D3",
        "Becke-Johnson damped modified Grimme D3",
        "Chai & Head-Gordon",
    ]
    grids = [
        "SG-3", 
        "SG-2", 
        "SG-1", 
        "(250, 974)",
        "(175, 974)",
        "(60, 770)",
        "(99, 590)",
        "(55, 590)",
        "(50, 434)",
        "(75, 302)",
    ]
    basis_sets = {
        "no": [
            "def2-SVP",
            "def2-TZVP",
            "cc-pVDZ",
            "cc-pVTZ",
            "aug-cc-pVDZ",
            "aug-cc-pVTZ",
            "6-311+G**",
        ],
        "RI": [
            "RIMP2-def2-SVP",
            "RIMP2-def2-SVPD",
            "RIMP2-def2-TZVP",
            "RIMP2-def2-TZVPD",
            "RIMP2-aug-cc-pVDZ",
            "RIMP2-cc-pVTZ",
            "RIMP2-aug-cc-pVTZ",
        ],
        "corr": [
            "RIMP2-def2-SVP",
            "RIMP2-def2-SVPD",
            "RIMP2-def2-TZVP",
            "RIMP2-def2-TZVPD",
            "RIMP2-aug-cc-pVDZ",
            "RIMP2-cc-pVTZ",
            "RIMP2-aug-cc-pVTZ",
        ],
        "J": [
            "RIJ-def2-SVP",
            "RIJ-def2-SVPD",
            "RIJ-def2-TZVP",
            "RIJ-def2-TZVPD",
        ],
        "K": [
            "RIJK-def2-SVP",
            "RIJK-def2-SVPD",
            "RIJK-def2-TZVP",
            "RIJK-def2-TZVPD",
        ],
    }
    aux_options = BasisSet.QCHEM_AUX
    ecps = ["fit-LANL2DZ", "def2-ECP", "SRLC", "SRSC"]
    keyword_options = QChemKeywordOptions
    
    def get_file_contents(self, theory):
        """creates Q-Chem input file using AaronTools"""
        header, header_warnings = theory.make_header(
            style="qchem", return_warnings=True,
        )
        mol, mol_warnings = theory.make_molecule(
            style="qchem", return_warnings=True,
        )

        out = header + mol
        contents = re.sub("{{\s?name\s?}}", theory.geometry.name, out)
        warnings = header_warnings + mol_warnings
        
        return out, warnings

    def get_job_kw_dict(
            self,
            optimize,
            frequencies,
            raman,
            hpmodes,
            read_checkpoint,
            checkpoint_file,
    ):
        rem = {}

        if frequencies:
            if raman:
                rem['DORAMAN'] = 'TRUE'

        return {QCHEM_REM: rem}


class XTBFileInfo(QMInputFileInfo):
    name = "xTB"
    
    initial_presets = {}
    initial_options = {}
    
    save_file_filter = "xTB input file (*.xc)"
    memory = False
    solvents = KNOWN_XTB_SOLVENTS
    basis_sets = None
    keyword_options = XTBKeywordOptions
    methods = [
        "GFN-FF",
        "GFN1-xTB",
        "GFN2-xTB",
    ]

    single_job_type = True

    def get_file_contents(self, theory):
        contents, warnings = FileWriter.write_xtb(
            theory.geometry, theory, outfile=False, return_warnings=True,
        )
        return contents, warnings
    