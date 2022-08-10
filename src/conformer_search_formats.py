from AaronTools.theory import *
from AaronTools.fileIO import FileWriter
from AaronTools.theory.implicit_solvent import KNOWN_XTB_SOLVENTS

from SEQCROW.tools.input_generator import (
    KeywordOptions,
    OneLayerKeyWordOption,
    TwoLayerKeyWordOption,
)
from SEQCROW.input_file_formats import XTBKeywordOptions


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
    # if None, will be disabled when 'read checkpoint' is checked
    save_checkpoint_filter = None
    
    # file filter for QFileDialog.getSaveFileName
    # if None, will be disabled when 'read checkpoint' is unchecked
    read_checkpoint_filter = None
    
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


class CREST(ConformerSearchInfo):
    # name of program
    name = "CREST"
    initial_options = {
        "command_line": {"ewin": ["6", "15", "25"]}
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