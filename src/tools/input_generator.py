from chimerax.atomic import AtomicStructure, selected_atoms, selected_bonds, get_triggers
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import StringArg, BoolArg, ListOf, IntArg
from chimerax.core.commands import run
from chimerax.core.models import ADD_MODELS, REMOVE_MODELS

from json import dumps, loads, dump, load

from PyQt5.Qt import QClipboard, QStyle, QIcon
from PyQt5.QtCore import Qt, QRegularExpression, pyqtSignal
from PyQt5.QtGui import QKeySequence, QFontMetrics, QFontDatabase
from PyQt5.QtWidgets import QCheckBox, QLabel, QGridLayout, QComboBox, QSplitter, QFrame, QLineEdit, \
                            QSpinBox, QMenuBar, QFileDialog, QAction, QApplication, QPushButton, \
                            QTabWidget, QWidget, QGroupBox, QListWidget, QTableWidget, QTableWidgetItem, \
                            QHBoxLayout, QFormLayout, QDoubleSpinBox, QHeaderView, QTextBrowser, \
                            QStatusBar, QTextEdit, QMessageBox, QTreeWidget, QTreeWidgetItem 

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.theory import *
from SEQCROW.utils import iter2str, combine_dicts
from SEQCROW.jobs import ORCAJob, GaussianJob, Psi4Job

from AaronTools.const import TMETAL

class _InputGeneratorSettings(Settings):
    EXPLICIT_SAVE = {
        'last_nproc': Value(6, IntArg), 
        'last_mem': Value(12, IntArg), 
        'last_opt': Value(False, BoolArg), 
        'last_ts': Value(False, BoolArg), 
        'last_freq': Value(False, BoolArg), 
        'last_raman': Value(False, BoolArg), 
        'last_num_freq': Value(False, BoolArg), 
        'previous_basis_names': Value([], ListOf(StringArg), iter2str),
        'previous_basis_paths': Value([], ListOf(StringArg), iter2str),
        'previous_ecp_names': Value([], ListOf(StringArg), iter2str),
        'previous_ecp_paths': Value([], ListOf(StringArg), iter2str),
        'last_basis': Value(["def2-SVP"], ListOf(StringArg), iter2str),
        'last_basis_aux': Value(["no"], ListOf(StringArg), iter2str),
        'last_custom_basis_kw': Value([""], ListOf(StringArg), iter2str),
        'last_custom_basis_builtin': Value([""], ListOf(StringArg), iter2str),
        'last_basis_elements': Value([""], ListOf(StringArg), iter2str),
        'last_basis_path': Value("", StringArg),
        'last_number_basis': Value(1, IntArg),
        'last_ecp': Value([], ListOf(StringArg), iter2str),
        'last_custom_ecp_kw': Value([], ListOf(StringArg), iter2str),
        'last_custom_ecp_builtin': Value([], ListOf(StringArg), iter2str),
        'last_ecp_elements': Value([], ListOf(StringArg), iter2str),
        'last_ecp_path': Value("", StringArg),
        'last_number_ecp': Value(0, IntArg),
        'previous_functional': Value("", StringArg),
        'previous_custom_func': Value("", StringArg),
        'previous_functional_names': Value([], ListOf(StringArg), iter2str),
        'previous_functional_needs_basis': Value([], ListOf(BoolArg), iter2str),
        'previous_dispersion': Value("None", StringArg),
        'previous_grid': Value("Default", StringArg),
        'previous_charge': Value(0, IntArg),
        'previous_mult': Value(1, IntArg),
        'previous_gaussian_solvent_model': Value("None", StringArg),
        'previous_gaussian_solvent_name': Value("", StringArg),
        #shh these are just jsons
        'previous_gaussian_options': Value(dumps({Method.GAUSSIAN_ROUTE: {'opt': \
                                                                                ['NoEigenTest', 'Tight', 'VeryTight'], \
                                                                        'DensityFit': \
                                                                                [], \
                                                                        'pop': \
                                                                                ['NBO', 'NBOREAD', 'NBO7'] \
                                                                        }, \
                                                  Method.GAUSSIAN_COMMENT:[], \
                                                  Method.GAUSSIAN_PRE_ROUTE: {'LindaWorkers':
                                                                                #I found this example online at http://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/m_linda.htm
                                                                                #I don't know if it works (I don't use linda)
                                                                                ["spain", "hamlet:2", "ophelia:4"], \
                                                                             }, \
                                                  Method.GAUSSIAN_POST: ['$nbo RESONANCE NBOSUM E2PERT=0.0 NLMO BNDIDX $end'], \
                                                 }), StringArg),
        'last_gaussian_options': Value(dumps({Method.GAUSSIAN_ROUTE:{}}), StringArg),
        'previous_orca_solvent_model': Value("None", StringArg),
        'previous_orca_solvent_name': Value("", StringArg),
        #shh these are just jsons
        'previous_orca_options': Value(dumps({Method.ORCA_ROUTE:['TightSCF'], \
                                              Method.ORCA_BLOCKS:{'basis':['decontract true'], 'elprop':[], 'freq':[], 'geom':[]}}), StringArg),
        #just the blocks that are used by the tool
        'last_orca_options': Value(dumps({}), StringArg),
        'previous_psi4_options': Value(dumps({Method.PSI4_SETTINGS:{'reference': \
                                                                                ['rhf', 'rohf', 'uhf', 'cuhf', 'rks', 'uks'], \
                                                                    'diag_method': \
                                                                                #the psi4 manual seems to imply that davidson and sem are
                                                                                #the same and different
                                                                                ['rsp', 'olsen', 'mitrushenkov', 'davidson', 'sem'], \
                                                                    'ex_level': \
                                                                                ['1', '2', '3'], \
                                                                    'fci': \
                                                                                ['true', 'false'], \
                                                                   }, \
                                                                   Method.PSI4_BEFORE_GEOM: [], \
                                                                   Method.PSI4_AFTER_GEOM: ["nrg, wfn = energy('$FUNCTIONAL', return_wfn=True)"], \
                                                                   Method.PSI4_COMMENT: [], \
                                                                   Method.PSI4_COORDINATES: {'units':['angstrom', 'bohr'], 
                                                                                             'pubchem':['benzene'], 
                                                                                             'symmetry':['c1', 'c2', 'ci', 'cs', 'd2', 'c2h', 'c2v', 'd2h'], 
                                                                                             'no_reorient':[], 
                                                                                             'no_com':[], 
                                                                                            }, \
                                             }), StringArg),
        'last_psi4_options': Value(dumps({}), StringArg),
        'last_program': Value("Gaussian", StringArg),
        }
        
    AUTO_SAVE = {
        'gaussian_presets': Value(dumps({
                                       "quick optimize":{"nproc":1, \
                                                           "mem":0, \
                                                           "opt":True, \
                                                           "ts":False, \
                                                           "freq":False, \
                                                           "semi-empirical":False, \
                                                           "solvent model":'None', \
                                                           "solvent":'', \
                                                           "functional":'PM6', \
                                                           "grid":None, \
                                                           "disp":None, \
                                                           "basis": {'name':[], 'auxiliary':[], 'file':[], 'elements':[]}, \
                                                           "ecp": {'name':[], 'file':[], 'elements':[]}, \
                                                           "other": {}, \
                                                         }, \
                                        }), StringArg), \
        'orca_presets': Value(dumps({
                                       "quick optimize":{"nproc":1, \
                                                       "mem":0, \
                                                       "opt":True, \
                                                       "ts":False, \
                                                       "freq":False, \
                                                       "semi-empirical":False, \
                                                       "solvent model":'None', \
                                                       "solvent":'', \
                                                       "functional":'HF-3c', \
                                                       "grid":None, \
                                                       "disp":None, \
                                                       "basis": {'name':[], 'auxiliary':[], 'file':[], 'elements':[]}, \
                                                       "ecp": {'name':[], 'file':[], 'elements':[]}, \
                                                       "other": {}, \
                                                      }, \
                                       "DLPNO single-point":{"nproc":2, \
                                                   "mem":12, \
                                                   "opt":False, \
                                                   "ts":False, \
                                                   "freq":False, \
                                                   "semi-empirical":False, \
                                                   "solvent model":'None', \
                                                   "solvent":'', \
                                                   "functional":'DLPNO-CCSD(T)', \
                                                   "grid":None, \
                                                   "disp":None, \
                                                   "basis": {'name':["cc-pVTZ", "cc-pVTZ"], 'auxiliary':[None, "C"], 'file':[False, False], 'elements':['all', 'all']}, \
                                                   "ecp": {'name':[], 'file':[], 'elements':['all']}, \
                                                   "other": {Method.ORCA_ROUTE:['TightSCF']}, \
                                                  }, \
                                       }), StringArg), \
        'psi4_presets': Value(dumps({
                                       "quick optimize":{"nproc":1, \
                                                       "mem":0, \
                                                       "opt":True, \
                                                       "ts":False, \
                                                       "freq":False, \
                                                       "semi-empirical":False, \
                                                       "solvent model":'None', \
                                                       "solvent":'', \
                                                       "functional":'HF', \
                                                       "grid":None, \
                                                       "disp":None, \
                                                       "basis": {'name':['sto-3g'], 'auxiliary':[None], 'file':[False], 'elements':['all']}, \
                                                       "ecp": {'name':[], 'file':[], 'elements':[]}, \
                                                       "other": {}, \
                                                      }, \
                                        },\
                                ), StringArg),
        'on_finished': Value('do nothing', StringArg), 
    }
    
    #def save(self, *args, **kwargs):
    #    print("saved qm input settings")
    #    super().save(*args, **kwargs)


class BuildQM(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         

    help = "https://github.com/QChASM/SEQCROW/wiki/Build-QM-Input-Tool"

    def __init__(self, session, name):       
        super().__init__(session, name)

        self.settings = _InputGeneratorSettings(session, name, version="2")
        
        self.display_name = "QM Input Generator"
        
        self.tool_window = MainToolWindow(self)        
        self.preview_window = None
        self.preset_window = None
        self.job_local_prep = None
        self.remove_preset_window = None
        self.export_preset_window = None

        self._build_ui()

        self.models = []
        
        self.presets = {}
        self.presets['Gaussian'] = loads(self.settings.gaussian_presets)
        self.presets['ORCA'] = loads(self.settings.orca_presets)
        self.presets['Psi4'] = loads(self.settings.psi4_presets)
        
        self.refresh_models()
        self.refresh_presets()

        global_triggers = get_triggers()

        self._add_handler = self.session.triggers.add_handler(ADD_MODELS, self.refresh_models)
        self._remove_handler = self.session.triggers.add_handler(REMOVE_MODELS, self.refresh_models)
        #TODO: 
        #find a better trigger - only need changes to coordinates and elements
        #'changes done' fires when other things happen like selecting atoms
        self._changes = global_triggers.add_handler("changes done", self.update_preview)

    def _build_ui(self):
        #build an interface with a dropdown menu to select software package
        #change from one software widget to another when the dropdown menu changes
        #TODO: add a presets tab to save/load presets to aaronrc
        #      so it can easily be used in other tools (like one that makes AARON input files)
        init_form = self.settings.last_program

        layout = QGridLayout()
        
        basics_form = QWidget()
        form_layout = QFormLayout(basics_form)
                
        self.file_type = QComboBox()
        self.file_type.addItems(['Gaussian', 'ORCA', 'Psi4'])
        ndx = self.file_type.findText(init_form, Qt.MatchExactly)
        self.file_type.setCurrentIndex(ndx)
        self.file_type.currentIndexChanged.connect(self.change_file_type)

        form_layout.addRow("file type:", self.file_type)
        
        self.model_selector = QComboBox()
        form_layout.addRow("structure:", self.model_selector)
        
        layout.addWidget(basics_form, 0, 0)
        
        #job type stuff
        self.job_widget = JobTypeOption(self.settings, self.session, init_form=init_form)
        self.job_widget.jobTypeChanged.connect(self.update_preview)
        
        #functional stuff
        self.functional_widget = FunctionalOption(self.settings, init_form=init_form)
        self.functional_widget.functionalChanged.connect(self.update_preview)

        #basis set stuff
        self.basis_widget = BasisWidget(self.settings, init_form=init_form)
        self.basis_widget.basisChanged.connect(self.update_preview)
        
        #other keywords
        self.other_keywords_widget = KeywordWidget(self.settings, init_form=init_form)
        self.other_keywords_widget.additionalOptionsChanged.connect(self.update_preview)
        
        tabs = QTabWidget()
        tabs.addTab(self.job_widget, "job details")
        tabs.addTab(self.functional_widget, "functional")
        tabs.addTab(self.basis_widget, "basis functions")
        tabs.addTab(self.other_keywords_widget, "additional options")
        
        self.model_selector.currentIndexChanged.connect(self.change_model)

        layout.addWidget(tabs, 1, 0)
      
        #menu stuff
        menu = QMenuBar()
        
        export = menu.addMenu("&Export")
        copy = QAction("&Copy input to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_input)
        shortcut = QKeySequence(QKeySequence.Copy)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        
        save = QAction("&Save Input", self.tool_window.ui_area)
        save.triggered.connect(self.save_input)
        #this shortcut interferes with main window's save shortcut
        #I've tried different shortcut contexts to no avail
        #thanks Qt...
        #shortcut = QKeySequence(Qt.CTRL + Qt.Key_S)
        #save.setShortcut(shortcut)
        #save.setShortcutContext(Qt.WidgetShortcut)
        export.addAction(save)
        
        view = menu.addMenu("&View")
        preview = QAction("&Preview", self.tool_window.ui_area)
        preview.triggered.connect(self.show_preview)
        view.addAction(preview)
        queue = QAction("&Queue", self.tool_window.ui_area)
        queue.triggered.connect(self.show_queue)
        view.addAction(queue)
        
        #TODO:
        #add Run ->
        #       Locally
        #       Remotely ->
        #           list of places?
        #               look at how AARON does jobs

        #batch = menu.addMenu("&Batch")
        #multistructure = QAction("&Multiple structures - coming eventually", self.tool_window.ui_area)
        #focal_point = QAction("&Focal point table - coming eventually", self.tool_window.ui_area)
        #batch.addAction(multistructure)
        #batch.addAction(focal_point)

        self.presets_menu = menu.addMenu("Presets")

        self.new_preset = QAction("Save Preset...", self.tool_window.ui_area)
        self.new_preset.triggered.connect(self.show_new_preset)
        self.presets_menu.addAction(self.new_preset)

        self.remove_preset = QAction("Remove Presets...")
        self.remove_preset.triggered.connect(self.show_remove_preset)
        self.presets_menu.addAction(self.remove_preset)

        self.import_preset = QAction("Import Presets...", self.tool_window.ui_area)
        self.import_preset.triggered.connect(self.import_preset_file)
        self.presets_menu.addAction(self.import_preset)

        self.export_preset = QAction("Export Presets...", self.tool_window.ui_area)
        self.export_preset.triggered.connect(self.show_export_preset)
        self.presets_menu.addAction(self.export_preset)

        run = menu.addMenu("&Run")
        locally = QAction("&Locally", self.tool_window.ui_area)
        #remotely = QAction("R&emotely - coming eventually", self.tool_window.ui_area)
        locally.triggered.connect(self.show_local_job_prep)
        run.addAction(locally)
        #run.addAction(remotely)
        
        menu.setNativeMenuBar(False)
        layout.setMenuBar(menu)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def refresh_presets(self):
        """cleans and repopulates the "presets" dropdown on the tool's ribbon"""
        self.presets_menu.clear()
        
        for program in self.presets:
            program_submenu = self.presets_menu.addMenu(program)
            for preset in self.presets[program]:
                preset_action = QAction(preset, self.tool_window.ui_area)
                preset_action.triggered.connect(lambda *args, program=program, name=preset: self.apply_preset(program, name))
                program_submenu.addAction(preset_action)
                
        self.settings.gaussian_presets = dumps(self.presets['Gaussian'])
        self.settings.orca_presets = dumps(self.presets['ORCA'])
        self.settings.psi4_presets = dumps(self.presets['Psi4'])

        sep = self.presets_menu.addSeparator()
        self.presets_menu.addAction(sep)
        self.presets_menu.addAction(self.new_preset)
        self.presets_menu.addAction(self.remove_preset)
        self.presets_menu.addAction(self.import_preset)
        self.presets_menu.addAction(self.export_preset)

    def show_new_preset(self):
        """open 'save preset' child tool"""
        if self.preset_window is None:
            self.preset_window = self.tool_window.create_child_window("New Preset", window_class=SavePreset)

    def apply_preset(self, program, preset_name):
        """apply preset named 'preset_name' for 'program'"""
        preset = self.presets[program][preset_name]
        
        ndx = self.file_type.findText(program, Qt.MatchExactly)
        self.file_type.setCurrentIndex(ndx)
        
        self.file_type.blockSignals(True)
        self.functional_widget.blockSignals(True)
        self.basis_widget.blockSignals(True)
        self.job_widget.blockSignals(True)
        self.other_keywords_widget.blockSignals(True)
    
        if 'opt' in preset:
            self.job_widget.do_geom_opt.setChecked(preset['opt'])
            self.job_widget.ts_opt.setChecked(preset['ts'])
            self.job_widget.do_freq.setChecked(preset['freq'])
            
        if 'temp' in preset:
            self.job_widget.temp.setValue(float(preset['temp']))
        
        if 'raman' in preset:
            self.job_widget.raman.setChecked(preset['raman'])
        
        if 'num_freq' in preset:
            self.job_widget.num_freq.setChecked(preset['num_freq'])
        
        if 'nproc' in preset:
            self.job_widget.setProcessors(preset['nproc'])
            self.job_widget.setMemory(preset['mem'])
        
        if 'solvent' in preset:
            solvent = ImplicitSolvent(preset['solvent model'], preset['solvent'])
            self.job_widget.setSolvent(solvent)
        
        if 'functional' in preset:
            func = Functional(preset['functional'], preset['semi-empirical'])
            self.functional_widget.setFunctional(func)
        
            self.functional_widget.setGrid(preset['grid'])
            self.functional_widget.setDispersion(preset['disp'])

        if 'basis' in preset:
            basis_list = []
            for i, name in enumerate(preset['basis']['name']):
                elements = preset['basis']['elements'][i]
                aux_type = preset['basis']['auxiliary'][i]
                user_defined = preset['basis']['file'][i]
                
                basis_list.append(Basis(name, elements, aux_type=aux_type, user_defined=user_defined))
                
            ecp_list = []
            for i, name in enumerate(preset['ecp']['name']):
                elements = preset['ecp']['elements'][i]
                user_defined = preset['ecp']['file'][i]
                
                ecp_list.append(ECP(name, elements, user_defined=user_defined))
    
            basis_set = BasisSet(basis_list, ecp_list)
            
            self.basis_widget.setBasis(basis_set)
        
        if 'other' in preset:
            raw_kw_dict = preset['other']
            kw_dict = {}
            for kw in raw_kw_dict.keys():
                kw_dict[int(kw)] = raw_kw_dict[kw]
            
            self.other_keywords_widget.setKeywords(kw_dict)
        
        self.file_type.blockSignals(False)
        self.functional_widget.blockSignals(False)
        self.basis_widget.blockSignals(False)
        self.job_widget.blockSignals(False)
        self.other_keywords_widget.blockSignals(False)
    
        self.update_preview()
        
        self.session.logger.info("applied \"%s\" (%s)" % (preset_name, program))
        
        if self.preset_window is not None:
            self.preset_window.basis_elements.refresh_basis()

    def show_remove_preset(self):
        if self.remove_preset_window is None:
            self.remove_preset_window = self.tool_window.create_child_window("Remove Presets", window_class=RemovePreset)

    def show_export_preset(self):
        if self.export_preset_window is None:
            self.export_preset_window = self.tool_window.create_child_window("Export Presets", window_class=ExportPreset)

    def import_preset_file(self):
        filename, _ = QFileDialog.getOpenFileName(filter="JSON files (*.json)")

        if not filename:
            return
            
        with open(filename, 'r') as f:
            new_presets = load(f)
            
        for program in ["Gaussian", "ORCA", "Psi4"]:
            if program in new_presets:
                for preset_name in new_presets[program]:
                    if preset_name in self.presets[program]:
                        yes = QMessageBox.question(self.presets_menu, \
                                                    "%s preset named \"%s\" already exists" % (program, preset_name), \
                                                    "would you like to overwrite \"%s\"?" % preset_name, \
                                                    QMessageBox.Yes | QMessageBox.No)

                        if yes != QMessageBox.Yes:
                            continue

                    self.presets[program][preset_name] = new_presets[program][preset_name]

                    self.session.logger.info("imported %s preset \"%s\"" % (program, preset_name))

                    if 'basis' in self.presets[program][preset_name]:
                        #print(any(file is not False for file in self.presets[program][preset_name]['basis']['file']))
                        if any(file is not False for file in self.presets[program][preset_name]['basis']['file']):
                            self.session.logger.warning("preset contains a basis set that is not built-in\n" +
                                                        "the external basis file location may need to be updated")

                    if 'ecp' in self.presets[program][preset_name]:
                        if any(file is not False for file in self.presets[program][preset_name]['ecp']['file']):
                            self.session.logger.warning("preset contains an ECP that is not built-in\n" +
                                                        "the external ECP file location may need to be updated")

        self.refresh_presets()

    def show_queue(self):
        run(self.session, "ui tool show \"Job Queue\"")

    def show_preview(self):
        """open child tool that showns contents of input file"""
        if self.preview_window is None:
            self.preview_window = self.tool_window.create_child_window("Input Preview", window_class=InputPreview)
            self.update_preview()

    def update_preview(self, *args, **kw):
        """whenever a setting is changed, this should be called to update the preview"""
        self.check_elements()
        if self.preview_window is not None:
            self.update_theory(False)
        
            kw_dict = self.job_widget.getKWDict(False)
            other_kw_dict = self.other_keywords_widget.getKWDict(False)
        
            combined_dict = combine_dicts(kw_dict, other_kw_dict)
            
            if self.file_type.currentText() == "Gaussian":
                output, warnings = self.theory.write_gaussian_input(combined_dict)
            elif self.file_type.currentText() == "ORCA":
                output, warnings = self.theory.write_orca_input(combined_dict)
            elif self.file_type.currentText() == "Psi4":
                output, warnings = self.theory.write_psi4_input(combined_dict)

            self.preview_window.setPreview(output, warnings)

    def change_file_type(self, *args):
        """change the file type
        args are ignored, only the contents of self.file_type matters"""
        #if we don't block signals, the preview will try to update before all widgets 
        #have been updated to give the proper info
        self.file_type.blockSignals(True)
        self.functional_widget.blockSignals(True)
        self.basis_widget.blockSignals(True)
        self.job_widget.blockSignals(True)
        self.other_keywords_widget.blockSignals(True)
    
        program = self.file_type.currentText()
        self.settings.last_program = program
        self.functional_widget.setOptions(program)
        self.basis_widget.setOptions(program)
        self.job_widget.setOptions(program)
        self.other_keywords_widget.setOptions(program)
        
        self.file_type.blockSignals(False)
        self.functional_widget.blockSignals(False)
        self.basis_widget.blockSignals(False)
        self.job_widget.blockSignals(False)
        self.other_keywords_widget.blockSignals(False)
        
        self.update_preview()
    
    def refresh_models(self, *args, **kwargs):
        """refresh the list of models on the model selector"""
        models = [mdl for mdl in self.session.models if isinstance(mdl, AtomicStructure)]
        
        #purge old models
        models_to_del = [mdl for mdl in self.models if mdl not in models]
    
        for mdl in models_to_del:
            if mdl in self.models:
                self.models.remove(mdl)
        
        #figure out new models
        new_models = [model for model in models if model not in self.models]
        self.models.extend(new_models)
        
        #remove models in reverse order b/c  0 -> count() can cause some to not get removed
        #if multiple models are closed at once
        for i in range(self.model_selector.count(), -1, -1):
            if self.model_selector.itemData(i) not in self.models:
                self.model_selector.removeItem(i)
                
        for model in self.models:
            if self.model_selector.findData(model) == -1:
                self.model_selector.addItem("%s (%s)" % (model.name, model.atomspec), model)

    def update_theory(self, update_settings=True):
        """grabs the current settings and updates self.theory
        always called before creating an input file"""
        if self.model_selector.currentIndex() >= 0 and \
            self.model_selector.currentIndex() < len(self.models):
            model = self.models[self.model_selector.currentIndex()]
        else:
            model = None

        func = self.functional_widget.getFunctional(update_settings)        
        basis = self.get_basis_set(update_settings)
        
        if self.file_type.currentText() != "Psi4":
            dispersion = self.functional_widget.getDispersion(update_settings)
        else:
            dispersion = None
        
        grid = self.functional_widget.getGrid(update_settings)      
        charge = self.job_widget.getCharge(update_settings)
        mult = self.job_widget.getMultiplicity(update_settings)
        nproc = self.job_widget.getNProc(update_settings)
        mem = self.job_widget.getMem(update_settings)

        if update_settings:
            self.settings.save()

        constraints = self.job_widget.getConstraints()
        
        self.theory = Method(structure=model, charge=charge, multiplicity=mult, \
                             functional=func, basis=basis, empirical_dispersion=dispersion, \
                             grid=grid, constraints=constraints, \
                             processors=nproc, memory=mem)
    
    def change_model(self, index):
        """changes model to the one selected in self.model_selector (index is basically ignored"""
        if index == -1:
            self.basis_widget.setElements([])
            return
        
        mdl = self.model_selector.currentData()

        self.check_elements()
        self.job_widget.setStructure(mdl)

        if mdl in self.session.filereader_manager.filereader_dict:
            for fr in self.session.filereader_manager.filereader_dict[mdl]:
                if 'charge' in fr.other:
                    self.job_widget.setCharge(fr.other['charge'])
            
                if 'multiplicity' in fr.other:
                    self.job_widget.setMultiplicity(fr.other['multiplicity'])
                    
                if 'temperature' in fr.other:
                    self.job_widget.setTemperature(fr.other['temperature'])

    def check_elements(self, *args, **kw):
        """ask self.basis_widget to check the elements"""
        mdl = self.model_selector.currentData()
        if mdl is not None:
            elements = set(mdl.atoms.elements.names)
            self.basis_widget.setElements(elements)
            self.job_widget.check_deleted_atoms()
    
    def get_basis_set(self, update_settings=False):
        """get BasisSet object from the basis widget"""
        basis, ecp = self.basis_widget.get_basis(update_settings)
        
        return BasisSet(basis, ecp)

    def show_local_job_prep(self):
        if self.job_local_prep is None:
            self.job_local_prep = self.tool_window.create_child_window("Launch Job", window_class=PrepLocalJob)

    def run_local_job(self, *args, name="local_job", auto_update=False, auto_open=False):
        self.update_theory()
        
        kw_dict = self.job_widget.getKWDict()
        other_kw_dict = self.other_keywords_widget.getKWDict()
        self.settings.save()
        
        combined_dict = combine_dicts(kw_dict, other_kw_dict)
        
        self.settings.last_program = self.file_type.currentText()
        
        program = self.file_type.currentText()
        if program == "Gaussian":
            job = GaussianJob(name, self.session, self.theory, combined_dict, auto_update=auto_update, auto_open=auto_open)
        elif program == "ORCA":
            job = ORCAJob(name, self.session, self.theory, combined_dict, auto_update=auto_update, auto_open=auto_open)
        elif program == "Psi4":
            job = Psi4Job(name, self.session, self.theory, combined_dict, auto_update=auto_update, auto_open=auto_open)
        
        self.session.logger.info("adding %s to queue" % name)   

        self.session.seqcrow_job_manager.add_job(job)

        self.update_preview()

    def copy_input(self):
        """copies input file to the clipboard"""
        self.update_theory()
        
        kw_dict = self.job_widget.getKWDict()
        other_kw_dict = self.other_keywords_widget.getKWDict()
        self.settings.save()
        
        combined_dict = combine_dicts(kw_dict, other_kw_dict)
        
        self.settings.last_program = self.file_type.currentText()
        
        program = self.file_type.currentText()
        if program == "Gaussian":
            output, warnings = self.theory.write_gaussian_input(combined_dict)
        elif program == "ORCA":
            output, warnings = self.theory.write_orca_input(combined_dict)
        elif program == "Psi4":
            output, warnings = self.theory.write_psi4_input(combined_dict)

        for warning in warnings:
            self.session.logger.warning(warning)

        app = QApplication.instance()
        clipboard = app.clipboard()
        clipboard.setText(output)
    
        self.update_preview()
    
        self.session.logger.info("copied to clipboard")
    
    def save_input(self):
        """save input to a file
        a file dialog will open asking for a file location"""
        self.update_theory()
        
        kw_dict = self.job_widget.getKWDict()
        other_kw_dict = self.other_keywords_widget.getKWDict()
        self.settings.save()
        
        combined_dict = combine_dicts(kw_dict, other_kw_dict)
        
        self.settings.last_program = self.file_type.currentText()

        warnings = []

        program = self.file_type.currentText()
        if program == "Gaussian":
            filename, _ = QFileDialog.getSaveFileName(filter="Gaussian input files (*.com *.gjf)")
            if filename:
                output, warnings = self.theory.write_gaussian_input(combined_dict, fname=filename)
        
        elif program == "ORCA":
            filename, _ = QFileDialog.getSaveFileName(filter="ORCA input files (*.inp)")
            if filename:
                output, warnings = self.theory.write_orca_input(combined_dict, fname=filename)
        
        elif program == "Psi4":
            filename, _ = QFileDialog.getSaveFileName(filter="Psi4 input files (*.in)")
            if filename:
                output, warnings = self.theory.write_psi4_input(combined_dict, fname=filename)

        for warning in warnings:
            self.session.logger.warning(warning)
            
        self.update_preview()
            
        self.session.logger.info("saved to %s" % filename)
    
    def delete(self):
        """deregister trigger handlers"""
        #overload delete to de-register handler
        self.session.triggers.remove_handler(self._add_handler)
        self.session.triggers.remove_handler(self._remove_handler)
        
        global_triggers = get_triggers()
        global_triggers.remove_handler(self._changes)
        
        super().delete()  

    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
    

class JobTypeOption(QWidget):
    """widget that controls job type and misc. options
        - charge & multiplicity
        - job resources
        - optimization/frequencies
        - contrained optimization
        - solvent
    """
    jobTypeChanged = pyqtSignal()
    
    GAUSSIAN_SOLVENT_MODELS = ["PCM", "SMD", "CPCM", "Dipole", "IPCM", "SCIPCM"]
    ORCA_SOLVENT_MODELS = ["SMD", "CPCM"]
    
    #TODO:
    #make selecting a row in one of the contraints tables select the atoms
    
    def __init__(self, settings, session, init_form, parent=None):
        """layout has charge, multiplicity, and job type options up top
        with more detailed options in the lower half on a tab widget
            - execution
                - job resources
                - checkpoint
            - optimization
                - ts?
                - contrained?
                - table of contraints
            - frequencies
                - temperature
                - raman?
            - solvent"""
        super().__init__(parent)
        
        self.settings = settings
        self.session = session
        self.form = init_form
        self.structure = None
        self.constrained_atoms = []
        self.constrained_bonds = []
        self.constrained_angles = []
        self.constrained_torsions = []
        
        self.layout = QGridLayout(self)
        
        job_form = QWidget()
        job_type_layout = QFormLayout(job_form)
        
        self.charge = QSpinBox()
        self.charge.setRange(-5, 5)
        self.charge.setSingleStep(1)
        self.charge.setValue(self.settings.previous_charge)
        self.charge.valueChanged.connect(self.something_changed)
        
        job_type_layout.addRow("charge:", self.charge)
                
        self.multiplicity = QSpinBox()
        self.multiplicity.setRange(1, 3)
        self.multiplicity.setSingleStep(1)
        self.multiplicity.setValue(self.settings.previous_mult)
        self.multiplicity.valueChanged.connect(self.something_changed)
        
        job_type_layout.addRow("multiplicity:", self.multiplicity)
        
        self.do_geom_opt = QCheckBox()
        self.do_geom_opt.stateChanged.connect(self.change_job_type)
        job_type_layout.addRow("geometry optimization:", self.do_geom_opt)
        
        self.do_freq = QCheckBox()
        self.do_freq.stateChanged.connect(self.change_job_type)
        job_type_layout.addRow("frequency calculation:", self.do_freq)

        self.job_type_opts = QTabWidget()
        
        self.runtime = QWidget()
        #the lineedit + button aligns poorly with a formlayout's label
        runtime_outer_shell_layout = QGridLayout(self.runtime)
        runtime_form = QWidget()
        runtime_layout = QFormLayout(runtime_form)
        margins = runtime_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        runtime_layout.setContentsMargins(*new_margins)
        
        self.nprocs = QSpinBox()
        self.nprocs.setRange(0, 128)
        self.nprocs.setSingleStep(1)
        self.nprocs.setToolTip("set to 0 to not specify")
        self.nprocs.setValue(self.settings.last_nproc)
        self.nprocs.valueChanged.connect(self.something_changed)
        runtime_layout.addRow("processors:", self.nprocs)
        
        self.mem = QSpinBox()
        self.mem.setRange(0, 512)
        self.mem.setSingleStep(2)
        self.mem.setSuffix(' GB')
        self.mem.setToolTip("set to 0 to not specify")
        self.mem.setValue(self.settings.last_mem)
        self.mem.valueChanged.connect(self.something_changed)
        runtime_layout.addRow("memory:", self.mem)
        
        self.use_checkpoint = QCheckBox()
        self.use_checkpoint.stateChanged.connect(self.something_changed)
        runtime_layout.addRow("read checkpoint:", self.use_checkpoint)
        
        runtime_outer_shell_layout.addWidget(runtime_form, 0, 0, 1, 1, Qt.AlignTop)
        
        file_browse = QWidget()
        file_browse_layout = QGridLayout(file_browse)
        margins = file_browse_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        file_browse_layout.setContentsMargins(*new_margins)
        self.chk_file_path = QLineEdit()
        self.chk_file_path.textChanged.connect(self.something_changed)
        self.chk_browse_button = QPushButton("browse")
        self.chk_browse_button.clicked.connect(self.open_chk_save)
        label = QLabel("checkpoint path:")
        file_browse_layout.addWidget(label, 0, 0, Qt.AlignVCenter)
        file_browse_layout.addWidget(self.chk_file_path, 0, 1, Qt.AlignVCenter)
        file_browse_layout.addWidget(self.chk_browse_button, 0, 2, Qt.AlignVCenter)
        file_browse_layout.setColumnStretch(0, 0)
        file_browse_layout.setColumnStretch(1, 1)
        file_browse_layout.setColumnStretch(2, 0)
        runtime_outer_shell_layout.addWidget(file_browse, 1, 0, Qt.AlignTop)
        
        align_widget = QWidget()
        runtime_outer_shell_layout.addWidget(align_widget, 2, 0, Qt.AlignTop)
        
        runtime_outer_shell_layout.setRowStretch(0, 0)
        runtime_outer_shell_layout.setRowStretch(1, 0)
        runtime_outer_shell_layout.setRowStretch(2, 1)
        
        self.job_type_opts.addTab(self.runtime, "execution")
        
        self.geom_opt = QWidget()
        geom_opt_layout = QGridLayout(self.geom_opt)
        geom_opt_layout.setContentsMargins(0, 0, 0, 0)
        geom_opt_form_widget = QWidget()
        geom_opt_form = QFormLayout(geom_opt_form_widget)
        
        self.ts_opt = QCheckBox()
        self.ts_opt.stateChanged.connect(self.something_changed)
        geom_opt_form.addRow("transition state structure:", self.ts_opt)
        
        self.use_contraints = QCheckBox()
        self.use_contraints.stateChanged.connect(self.show_contraints)
        geom_opt_form.addRow("constrained:", self.use_contraints)
        
        self.constraints_widget = QWidget()
        constraints_layout = QGridLayout(self.constraints_widget)
        
        geom_opt_layout.addWidget(geom_opt_form_widget, 0, 0, Qt.AlignTop)
        
        atom_constraints = QWidget()
        atom_constraints_layout = QGridLayout(atom_constraints)
        atom_constraints_layout.setContentsMargins(0, 0, 0, 0)
        
        freeze_atoms = QPushButton("constrain selected atoms")
        freeze_atoms.clicked.connect(self.constrain_atoms)
        freeze_atoms.clicked.connect(self.something_changed)
        atom_constraints_layout.addWidget(freeze_atoms, 0, 0)

        self.constrained_atom_table = QTableWidget()
        self.constrained_atom_table.setColumnCount(2)
        self.constrained_atom_table.cellClicked.connect(self.clicked_atom_table)
        self.constrained_atom_table.setHorizontalHeaderLabels(["atom", "unfreeze"])
        self.constrained_atom_table.setEditTriggers(QTableWidget.NoEditTriggers)
        atom_constraints_layout.addWidget(self.constrained_atom_table, 1, 0)
        
        bond_constraints = QWidget()
        bond_constraints_layout = QGridLayout(bond_constraints)
        bond_constraints_layout.setContentsMargins(0, 0, 0, 0)

        freeze_bonds = QPushButton("constrain selected bonds or atom pair")
        freeze_bonds.clicked.connect(self.constrain_bonds)
        freeze_bonds.clicked.connect(self.something_changed)
        bond_constraints_layout.addWidget(freeze_bonds, 0, 0)

        self.constrained_bond_table = QTableWidget()
        self.constrained_bond_table.setColumnCount(3)
        self.constrained_bond_table.cellClicked.connect(self.clicked_bond_table)
        self.constrained_bond_table.setHorizontalHeaderLabels(["atom 1", "atom 2", "unfreeze"])
        self.constrained_bond_table.setEditTriggers(QTableWidget.NoEditTriggers)
        bond_constraints_layout.addWidget(self.constrained_bond_table, 1, 0)
        
        angle_constraints = QWidget()
        angle_constraints_layout = QGridLayout(angle_constraints)
        angle_constraints_layout.setContentsMargins(0, 0, 0, 0)

        freeze_bond_pair = QPushButton("constrain selected bond pair or atom trio")
        freeze_bond_pair.clicked.connect(self.constrain_angles)
        freeze_bond_pair.clicked.connect(self.something_changed)
        angle_constraints_layout.addWidget(freeze_bond_pair, 0, 0)

        self.constrained_angle_table = QTableWidget()
        self.constrained_angle_table.setColumnCount(4)
        self.constrained_angle_table.cellClicked.connect(self.clicked_angle_table)
        self.constrained_angle_table.setHorizontalHeaderLabels(["atom 1", "atom 2", "atom 3", "unfreeze"])
        self.constrained_angle_table.setEditTriggers(QTableWidget.NoEditTriggers)
        angle_constraints_layout.addWidget(self.constrained_angle_table, 1, 0)

        torsion_constrains = QWidget()
        torsion_constrains_layout = QGridLayout(torsion_constrains)
        torsion_constrains_layout.setContentsMargins(0, 0, 0, 0)

        freeze_bond_trio = QPushButton("constrain selected bond trio or atom quartet")
        freeze_bond_trio.clicked.connect(self.constrain_torsions)
        freeze_bond_trio.clicked.connect(self.something_changed)
        torsion_constrains_layout.addWidget(freeze_bond_trio, 0, 0)


        self.constrained_torsion_table = QTableWidget()
        self.constrained_torsion_table.setColumnCount(5)
        self.constrained_torsion_table.cellClicked.connect(self.clicked_torsion_table)
        self.constrained_torsion_table.setHorizontalHeaderLabels(["atom 1", "atom 2", "atom 3", "atom 4", "unfreeze"])
        self.constrained_torsion_table.setEditTriggers(QTableWidget.NoEditTriggers)
        torsion_constrains_layout.addWidget(self.constrained_torsion_table, 1, 0)

        constraints_viewer = QTabWidget()

        constraints_viewer.addTab(atom_constraints, "atoms")
        constraints_viewer.addTab(bond_constraints, "bonds")
        constraints_viewer.addTab(angle_constraints, "angles")
        constraints_viewer.addTab(torsion_constrains, "torsions")
        constraints_viewer.setStyleSheet('QTabWidget::pane {border: 1px;}')

        constraints_layout.addWidget(constraints_viewer, 1, 0, 1, 2, Qt.AlignTop)

        constraints_layout.setRowStretch(0, 0)
        constraints_layout.setRowStretch(1, 1)
        constraints_layout.setContentsMargins(0, 0, 0, 0)
        
        self.constraints_widget.setEnabled(self.use_contraints.checkState() == Qt.Checked)

        geom_opt_layout.addWidget(self.constraints_widget, 1, 0, Qt.AlignTop)
        geom_opt_layout.setRowStretch(0, 0)
        geom_opt_layout.setRowStretch(1, 1)
        
        self.job_type_opts.addTab(self.geom_opt, "optimization settings")
        
        self.freq_opt = QWidget()
        freq_opt_form = QFormLayout(self.freq_opt)
        
        self.temp = QDoubleSpinBox()
        self.temp.setRange(0, 10000)
        self.temp.setValue(298.15)
        self.temp.setSuffix(" K")
        self.temp.setSingleStep(10)
        self.temp.valueChanged.connect(self.something_changed)
        
        freq_opt_form.addRow("temperature:", self.temp)
        
        self.hpmodes = QCheckBox()
        self.hpmodes.setCheckState(Qt.Checked)
        self.hpmodes.stateChanged.connect(self.something_changed)
        self.hpmodes.setToolTip("ask Gaussian to print extra precision on normal mode displacements")
        freq_opt_form.addRow("high-precision modes:", self.hpmodes)

        self.raman = QCheckBox()
        self.raman.setCheckState(self.settings.last_raman)
        self.raman.stateChanged.connect(self.something_changed)
        freq_opt_form.addRow("Raman intensities:", self.raman)

        self.num_freq = QCheckBox()
        self.num_freq.setChecked(self.settings.last_num_freq)
        self.num_freq.stateChanged.connect(self.something_changed)
        self.num_freq.setToolTip("numerical vibrational frequency algorithms are often slower than analytical algorithms,\nusually require less memory and available for functionals where analytical methods are not")
        freq_opt_form.addRow("Numerical frequencies:", self.num_freq)

        self.job_type_opts.addTab(self.freq_opt, "frequency settings")
        
        solvent_widget = QWidget()
        solvent_layout = QGridLayout(solvent_widget)
        
        solvent_form = QWidget()
        solvent_form_layout = QFormLayout(solvent_form)
        
        self.solvent_option = QComboBox()
        self.solvent_option.currentTextChanged.connect(self.change_solvent_model)
        solvent_form_layout.addRow("implicit solvent model:", self.solvent_option)
        
        self.solvent_name_label = QLabel("solvent:")
        self.solvent_name = QLineEdit()
        self.solvent_name.setText(self.settings.previous_gaussian_solvent_name)
        self.solvent_name.textChanged.connect(self.filter_solvents)
        self.solvent_name.setClearButtonEnabled(True)
        solvent_form_layout.addRow(self.solvent_name_label, self.solvent_name)
        
        solvent_layout.addWidget(solvent_form, 0, 0, Qt.AlignTop)
        
        self.solvent_names = QListWidget()
        self.solvent_names.setSelectionMode(self.solvent_names.SingleSelection)
        self.solvent_names.itemSelectionChanged.connect(self.change_selected_solvent)
        
        solvent_layout.addWidget(self.solvent_names)
        
        self.job_type_opts.addTab(solvent_widget, "solvent")
        
        self.job_type_opts.tabBarDoubleClicked.connect(self.tab_dble_click)
        
        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(True)
        splitter.addWidget(job_form)
        splitter.addWidget(self.job_type_opts)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        self.layout.addWidget(splitter)
        
        #self.layout.addWidget(job_form, 0, 0, Qt.AlignTop)
        #self.layout.addWidget(self.job_type_opts, 1, 0, Qt.AlignTop)

        self.setOptions(self.form)
        
        self.change_job_type()
        
        self.do_geom_opt.setCheckState(Qt.Checked if self.settings.last_opt else Qt.Unchecked)
        self.ts_opt.setCheckState(Qt.Checked if self.settings.last_ts else Qt.Unchecked)
        self.do_freq.setCheckState(Qt.Checked if self.settings.last_freq else Qt.Unchecked)
        
        self.do_geom_opt.stateChanged.connect(self.opt_checked)
        self.do_freq.stateChanged.connect(self.freq_checked)
        
        self.constrained_atom_table.resizeColumnToContents(1)
        self.constrained_atom_table.horizontalHeader().setStretchLastSection(False)            
        self.constrained_atom_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.constrained_atom_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)

        self.constrained_bond_table.resizeColumnToContents(2)
        self.constrained_bond_table.horizontalHeader().setStretchLastSection(False)            
        self.constrained_bond_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.constrained_bond_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.constrained_bond_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)

        self.constrained_angle_table.resizeColumnToContents(3)
        self.constrained_angle_table.horizontalHeader().setStretchLastSection(False)            
        self.constrained_angle_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.constrained_angle_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.constrained_angle_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.constrained_angle_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)

        self.constrained_torsion_table.resizeColumnToContents(4)
        self.constrained_torsion_table.horizontalHeader().setStretchLastSection(False)            
        self.constrained_torsion_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.constrained_torsion_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.constrained_torsion_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.constrained_torsion_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.constrained_torsion_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
    
    def tab_dble_click(self, ndx):
        """toggle job type when optimization or frequency tab is clicked
        this is done so that the job type can be changed when the top half has been collapsed"""
        if ndx == 1:
            self.do_geom_opt.setChecked(not self.do_geom_opt.checkState() == Qt.Checked)
        
        elif ndx == 2:
            self.do_freq.setChecked(not self.do_freq.checkState() == Qt.Checked)
    
    def open_chk_save(self):
        """open file dialog to locate chk file"""
        if self.form == "Gaussian":
            filename, _ = QFileDialog.getSaveFileName(filter="Gaussian checkpoint files (*.chk)")
        
        if filename:
            self.chk_file_path.setText(filename)
    
    def something_changed(self, *args, **kw):
        """called whenever a setting has changed to notify the main tool"""
        self.jobTypeChanged.emit()
    
    def opt_checked(self, state):
        """when optimization is checked, switch the tab widget to show optimization settings"""
        if state == Qt.Checked:
            self.job_type_opts.setCurrentIndex(1)    
    
    def freq_checked(self, state):
        """when frequency is checked, switch the tab widget to show freq settings"""
        if state == Qt.Checked:
            self.job_type_opts.setCurrentIndex(2)
    
    def setOptions(self, program):
        """change all options to show the ones available for 'program'"""
        self.form = program
        self.solvent_option.clear()
        self.solvent_names.clear()
        if program == "Gaussian":
            self.solvent_option.addItems(["None"])
            self.solvent_option.addItems(self.GAUSSIAN_SOLVENT_MODELS)
            self.hpmodes.setEnabled(True)
            self.raman.setToolTip("ask Gaussian to compute Raman intensities")
            self.raman.setEnabled(True)
            self.solvent_names.addItems(ImplicitSolvent.KNOWN_GAUSSIAN_SOLVENTS)
            ndx = self.solvent_option.findText(self.settings.previous_gaussian_solvent_model)
            if ndx >= 0:
                self.solvent_option.setCurrentIndex(ndx)
            self.job_type_opts.setTabEnabled(3, True)
            self.use_checkpoint.setEnabled(True)
            self.chk_file_path.setEnabled(True)
            self.chk_browse_button.setEnabled(True)
        
        elif program == "ORCA":
            self.solvent_option.addItems(["None"])
            self.solvent_option.addItems(self.ORCA_SOLVENT_MODELS)
            self.hpmodes.setEnabled(False)
            self.raman.setToolTip("ask ORCA to compute Raman intensities")
            self.raman.setEnabled(True)
            self.solvent_names.addItems(ImplicitSolvent.KNOWN_ORCA_SOLVENTS)
            ndx = self.solvent_option.findText(self.settings.previous_orca_solvent_model)
            if ndx >= 0:
                self.solvent_option.setCurrentIndex(ndx)
            self.solvent_name.setText(self.settings.previous_orca_solvent_name)
            self.job_type_opts.setTabEnabled(3, True)
            self.use_checkpoint.setEnabled(False)
            self.chk_file_path.setEnabled(False)
            self.chk_browse_button.setEnabled(False)
            
        elif program == "Psi4":
            self.solvent_option.addItems(["None"])
            self.job_type_opts.setTabEnabled(3, False)
            self.hpmodes.setEnabled(False)
            self.raman.setEnabled(False)
            self.use_checkpoint.setEnabled(False)
            self.chk_file_path.setEnabled(False)
            self.chk_browse_button.setEnabled(False)

        self.solvent_names.sortItems()

    def change_selected_solvent(self):
        """when a solvent is selected in the list, the solvent is set to that"""
        item = self.solvent_names.selectedItems()
        if len(item) == 1:
            name = item[0].text()
            self.solvent_name.setText(name)
            
        self.jobTypeChanged.emit()
    
    def filter_solvents(self, text):
        """case-insensitive regex to filter solvent list based on what the user
        has typed for a solvent name"""
        if text:
            #the user doesn't need capturing groups
            text = text.replace('(', '\(')
            text = text.replace(')', '\)')
            m = QRegularExpression(text)
            if m.isValid():
                m.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
                
                m.optimize()
                filter = lambda row_num: m.match(self.solvent_names.item(row_num).text()).hasMatch()
            else:
                return
        
        else:
            filter = lambda row: True
            
        for i in range(0, self.solvent_names.count()):
            self.solvent_names.setRowHidden(i, not filter(i))        

    def change_solvent_model(self):
        """hide solvent options when solvent model changes to 'None'"""
        if self.solvent_option.currentText() != "None":
            self.solvent_name_label.setVisible(True)
            self.solvent_name.setVisible(True)
            self.solvent_names.setVisible(True)
        else:
            self.solvent_name_label.setVisible(False)
            self.solvent_name.setVisible(False)
            self.solvent_names.setVisible(False)

        self.jobTypeChanged.emit()
    
    def change_job_type(self, *args):
        """disables tabs when they don't apply to the job type"""
        self.job_type_opts.setTabEnabled(1, self.do_geom_opt.checkState() == Qt.Checked)
        self.job_type_opts.setTabEnabled(2, self.do_freq.checkState() == Qt.Checked)
        
        self.jobTypeChanged.emit()

    def show_contraints(self, value):
        """enable contraints table when doing contrainted optimization"""
        self.constraints_widget.setEnabled(bool(value))
        self.jobTypeChanged.emit()

    def getCharge(self, update_settings=True):
        """returns charge"""
        charge = self.charge.value()
        if update_settings:
            self.settings.previous_charge = charge
        
        return charge

    def setCharge(self, value):
        """sets charge"""
        self.charge.setValue(value)

    def getMultiplicity(self, update_settings=True):
        """returns multiplicity"""
        mult = self.multiplicity.value()
        if update_settings:
            self.settings.previous_mult = mult
        
        return mult

    def setMultiplicity(self, value):
        """sets multiplicity"""
        self.multiplicity.setValue(value)

    def setTemperature(self, value):
        """sets temperature"""
        self.temp.setValue(value)
        self.jobTypeChanged.emit()

    def getTemperature(self):
        """returns temperature"""
        return self.temp.value()

    def setStructure(self, structure):
        """changes the structure and clears contraints"""
        self.structure = structure
        self.constrained_atoms = []
        self.constrained_bonds = []
        self.constrained_angles = []
        self.constrained_torsions = []
        
        for i in range(self.constrained_atom_table.rowCount(), -1, -1):
            self.constrained_atom_table.removeRow(i)    
        
        for i in range(self.constrained_bond_table.rowCount(), -1, -1):
            self.constrained_bond_table.removeRow(i)    
        
        for i in range(self.constrained_angle_table.rowCount(), -1, -1):
            self.constrained_angle_table.removeRow(i)    
        
        for i in range(self.constrained_torsion_table.rowCount(), -1, -1):
            self.constrained_torsion_table.removeRow(i)    

        self.jobTypeChanged.emit()

    def setGeometryOptimization(self, value):
        """changes job type to opt"""
        self.do_geom_opt.setChecked(value)
    
    def setTSOptimization(self, value):
        """sets job type to ts opt"""
        self.ts_opt.setChecked(value)
    
    def setFrequencyCalculation(self, value):
        """sets job type to freq"""
        self.do_freq.setChecked(value)

    def setProcessors(self, value):
        """sets nproc"""
        self.nprocs.setValue(value)

    def setMemory(self, value):
        """sets memory"""
        self.mem.setValue(value)

    def setSolventModel(self, value):
        """sets solvent model if model is available"""
        ndx = self.solvent_option.findText(value, Qt.MatchExactly)
        if ndx >= 0:
            self.solvent_option.setCurrentIndex(ndx)

    def setSolvent(self, value):
        """sets solvent to value"""
        self.solvent_name.setText(value)

    def getGeometryOptimization(self):
        """returns whether the job type is opt"""
        return self.do_geom_opt.checkState() == Qt.Checked
    
    def getTSOptimization(self):
        """returns whether the job is opt ts"""
        return self.ts_opt.checkState() == Qt.Checked
    
    def getFrequencyCalculation(self):
        """returns whether the job is freq"""
        return self.do_freq.checkState() == Qt.Checked

    def getSolvent(self):
        """returns ImplicitSolvent for the current solvent settings"""
        model = self.solvent_option.currentText()
        solvent = self.solvent_name.text()
        
        return ImplicitSolvent(model, solvent)

    def setSolvent(self, solvent):
        """sets solvent to match the given ImplicitSolvent"""
        ndx = self.solvent_option.findText(solvent.name)
        if ndx >= 0:
            self.solvent_option.setCurrentIndex(ndx)
            
        self.solvent_name.setText(solvent.solvent)

    def constrain_atoms(self):
        """add selected atoms to list of contrained atoms"""
        current_atoms = [atom for atom in selected_atoms(self.session) if atom.structure is self.structure]
        for atom in current_atoms:
            #ignore atoms already constrained
            if atom in self.constrained_atoms:
                continue

            self.constrained_atoms.append(atom)

            row = self.constrained_atom_table.rowCount()
            self.constrained_atom_table.insertRow(row)
            item = QTableWidgetItem()
            item.setData(Qt.DisplayRole, atom.atomspec)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_atom_table.setItem(row, 0, item)
        
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            trash_button = QLabel()
            dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
            trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)).pixmap(dim, dim))
            trash_button.setToolTip("click to unfreeze")
            widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
            widget_layout.setContentsMargins(2, 2, 2, 2)
            self.constrained_atom_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)

            self.constrained_atom_table.resizeRowToContents(row)

        self.jobTypeChanged.emit()

    def constrain_bonds(self):
        """adds selected bonds to list of constrained bonds"""
        current_bonds = [bond for bond in selected_bonds(self.session) if bond.structure is self.structure]
        for bond in current_bonds:
            atom1, atom2 = bond.atoms
            for bond in self.constrained_bonds:
                if atom1 in bond and atom2 in bond:
                    continue

            self.constrained_bonds.append((atom1, atom2))
            
            row = self.constrained_bond_table.rowCount()
            self.constrained_bond_table.insertRow(row)

            item1 = QTableWidgetItem()
            item1.setData(Qt.DisplayRole, atom1.atomspec)
            item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_bond_table.setItem(row, 0, item1)
            
            item2 = QTableWidgetItem()
            item2.setData(Qt.DisplayRole, atom2.atomspec)
            item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_bond_table.setItem(row, 1, item2)
        
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            trash_button = QLabel()
            dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
            trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)).pixmap(dim, dim))
            trash_button.setToolTip("click to unfreeze")
            widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
            widget_layout.setContentsMargins(2, 2, 2, 2)
            self.constrained_bond_table.setCellWidget(row, 2, widget_that_lets_me_horizontally_align_an_icon)

            self.constrained_bond_table.resizeRowToContents(row)

        current_atoms = [atom for atom in selected_atoms(self.session) if atom.structure is self.structure]
        if len(current_atoms) > 2 or len(current_atoms) == 1:
            self.session.logger.error("can only select two atoms on %s" % self.structure.atomspec)
            return
        elif len(current_atoms) == 2:
            atom1, atom2 = sorted(current_atoms)
            for bond in self.constrained_bonds:
                if atom1 in bond and atom2 in bond:
                    return
    
            self.constrained_bonds.append((atom1, atom2))
    
            row = self.constrained_bond_table.rowCount()
            self.constrained_bond_table.insertRow(row)
            
            item1 = QTableWidgetItem()
            item1.setData(Qt.DisplayRole, atom1.atomspec)
            item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_bond_table.setItem(row, 0, item1)
    
            item2 = QTableWidgetItem()
            item2.setData(Qt.DisplayRole, atom2.atomspec)
            item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_bond_table.setItem(row, 1, item2)
            
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            trash_button = QLabel()
            dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
            trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)).pixmap(dim, dim))
            trash_button.setToolTip("click to unfreeze")
            widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
            widget_layout.setContentsMargins(2, 2, 2, 2)
            self.constrained_bond_table.setCellWidget(row, 2, widget_that_lets_me_horizontally_align_an_icon)
    
            self.constrained_bond_table.resizeRowToContents(row)

        self.jobTypeChanged.emit()
   
    def constrain_angles(self):
        """adds selected bonds to list of contrained angles"""
        #try to use ordered selection so that if the user selected 1 -> 2 -> 3, they appear in that order
        current_bonds = [bond for bond in selected_bonds(self.session) if bond.structure is self.structure]
        #if the user didn't pick the atoms one by one, fall back on selected_atoms
        if len(current_bonds) != 2 and len(current_bonds) != 0:
            self.session.logger.error("can only select two bonds on %s" % self.structure.atomspec)
            return
        elif len(current_bonds) == 2:
            current_atoms = []
            atom2 = None
            for bond in current_bonds:
                for atom in bond.atoms:
                    if atom not in current_atoms:
                        current_atoms.append(atom)
                        
                    else:
                        atom2 = atom
                        
            if atom2 is None:
                self.session.logger.error("bonds must have one atom in common")
                return
            
            current_atoms.remove(atom2)
    
            atom1, atom3 = sorted(current_atoms)
            for angle in self.constrained_angles:
                if atom1 is angle[0] and atom2 is angle[1] and atom3 is angle[2]:
                    return
                
                if atom1 is angle[2] and atom2 is angle[1] and atom3 is angle[0]:
                    return
    
            self.constrained_angles.append((atom1, atom2, atom3))
    
            row = self.constrained_angle_table.rowCount()
            self.constrained_angle_table.insertRow(row)
            
            item1 = QTableWidgetItem()
            item1.setData(Qt.DisplayRole, atom1.atomspec)
            item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_angle_table.setItem(row, 0, item1)
    
            item2 = QTableWidgetItem()
            item2.setData(Qt.DisplayRole, atom2.atomspec)
            item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_angle_table.setItem(row, 1, item2)
    
            item3 = QTableWidgetItem()
            item3.setData(Qt.DisplayRole, atom3.atomspec)
            item3.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_angle_table.setItem(row, 2, item3)
            
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            trash_button = QLabel()
            dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
            trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)).pixmap(dim, dim))
            trash_button.setToolTip("click to unfreeze")
            widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
            widget_layout.setContentsMargins(2, 2, 2, 2)
            self.constrained_angle_table.setCellWidget(row, 3, widget_that_lets_me_horizontally_align_an_icon)
    
            self.constrained_angle_table.resizeRowToContents(row)
        
        #try to use ordered selection so that if the user selected 1 -> 2 -> 3, they appear in that order
        current_atoms = [atom for atom in self.session.seqcrow_ordered_selection_manager.selection if atom.structure is self.structure]
        #if the user didn't pick the atoms one by one, fall back on selected_atoms
        if len(current_atoms) != 3:
            current_atoms = [atom for atom in selected_atoms(self.session) if atom.structure is self.structure]
        
        if len(current_atoms) != 3 and len(current_atoms) != 0:
            self.session.logger.error("can only select three atoms on %s" % self.structure.atomspec)
            return
        elif len(current_atoms) == 3:
            atom1, atom2, atom3 = current_atoms
            for angle in self.constrained_angles:
                if atom1 is angle[0] and atom2 is angle[1] and atom3 is angle[2]:
                    return
                
                if atom1 is angle[2] and atom2 is angle[1] and atom3 is angle[0]:
                    return
    
            self.constrained_angles.append((atom1, atom2, atom3))
    
            row = self.constrained_angle_table.rowCount()
            self.constrained_angle_table.insertRow(row)
            
            item1 = QTableWidgetItem()
            item1.setData(Qt.DisplayRole, atom1.atomspec)
            item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_angle_table.setItem(row, 0, item1)
    
            item2 = QTableWidgetItem()
            item2.setData(Qt.DisplayRole, atom2.atomspec)
            item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_angle_table.setItem(row, 1, item2)
    
            item3 = QTableWidgetItem()
            item3.setData(Qt.DisplayRole, atom3.atomspec)
            item3.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_angle_table.setItem(row, 2, item3)
            
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            trash_button = QLabel()
            dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
            trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)).pixmap(dim, dim))
            trash_button.setToolTip("click to unfreeze")
            widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
            widget_layout.setContentsMargins(2, 2, 2, 2)
            self.constrained_angle_table.setCellWidget(row, 3, widget_that_lets_me_horizontally_align_an_icon)
    
            self.constrained_angle_table.resizeRowToContents(row)

        self.jobTypeChanged.emit()
    
    def constrain_torsions(self):
        """adds selected bonds/atoms to list of constrained torsions"""
        current_bonds = [bond for bond in selected_bonds(self.session) if bond.structure is self.structure]
        #if the user didn't pick the atoms one by one, fall back on selected_atoms
        if len(current_bonds) != 3 and len(current_bonds) != 0:
            self.session.logger.error("can only select three bonds on %s" % self.structure.atomspec)
            return
        elif len(current_bonds) == 3:
            current_atoms = []
            atom2 = None
            atom3 = None
            for bond in current_bonds:
                for atom in bond.atoms:
                    if atom not in current_atoms:
                        current_atoms.append(atom)
                    else:
                        if atom2 is None:
                            atom2 = atom
                        elif atom3 is None:
                            atom3 = atom
                            
            if atom3 is None or atom3 == atom2:
                #improper torsion
                atom1, atom2, atom3, atom4 = current_atoms
            
            else:
                current_atoms.remove(atom2)
                current_atoms.remove(atom3)
                
                atom1 = [atom for atom in current_atoms if atom2 in atom.neighbors][0]
                atom4 = [atom for atom in current_atoms if atom3 in atom.neighbors][0]
                
            for torsion in self.constrained_torsions:
                if atom1 is torsion[0] and atom2 is torsion[1] and atom3 is torsion[2] and atom4 is torsion[3]:
                    return
                
                if atom1 is torsion[3] and atom2 is torsion[2] and atom3 is torsion[1] and atom4 is torsion[0]:
                    return
    
            self.constrained_torsions.append((atom1, atom2, atom3, atom4))
    
            row = self.constrained_torsion_table.rowCount()
            self.constrained_torsion_table.insertRow(row)
            
            item1 = QTableWidgetItem()
            item1.setData(Qt.DisplayRole, atom1.atomspec)
            item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_torsion_table.setItem(row, 0, item1)
    
            item2 = QTableWidgetItem()
            item2.setData(Qt.DisplayRole, atom2.atomspec)
            item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_torsion_table.setItem(row, 1, item2)
    
            item3 = QTableWidgetItem()
            item3.setData(Qt.DisplayRole, atom3.atomspec)
            item3.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_torsion_table.setItem(row, 2, item3)
            
            item4 = QTableWidgetItem()
            item4.setData(Qt.DisplayRole, atom4.atomspec)
            item4.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_torsion_table.setItem(row, 3, item4)
            
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            trash_button = QLabel()
            dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
            trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)).pixmap(dim, dim))
            trash_button.setToolTip("click to unfreeze")
            widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
            widget_layout.setContentsMargins(2, 2, 2, 2)
            self.constrained_torsion_table.setCellWidget(row, 4, widget_that_lets_me_horizontally_align_an_icon)
            
            self.constrained_torsion_table.resizeRowToContents(row)

        current_atoms = [atom for atom in self.session.seqcrow_ordered_selection_manager.selection if atom.structure is self.structure]
        #if the user didn't pick the atoms one by one, fall back on selected_atoms
        if len(current_atoms) != 4:
            current_atoms = [atom for atom in selected_atoms(self.session) if atom.structure is self.structure]
        
        if len(current_atoms) != 4 and len(current_atoms) != 0:
            self.session.logger.error("can only select four atoms on %s" % self.structure.atomspec)
            return
        elif len(current_atoms) == 4:
            atom1, atom2, atom3, atom4 = current_atoms
            for torsion in self.constrained_torsions:
                if atom1 is torsion[0] and atom2 is torsion[1] and atom3 is torsion[2] and atom4 is torsion[3]:
                    return
                
                if atom1 is torsion[3] and atom2 is torsion[2] and atom3 is torsion[1] and atom4 is torsion[0]:
                    return
    
            self.constrained_torsions.append((atom1, atom2, atom3, atom4))
    
            row = self.constrained_torsion_table.rowCount()
            self.constrained_torsion_table.insertRow(row)
            
            item1 = QTableWidgetItem()
            item1.setData(Qt.DisplayRole, atom1.atomspec)
            item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_torsion_table.setItem(row, 0, item1)
    
            item2 = QTableWidgetItem()
            item2.setData(Qt.DisplayRole, atom2.atomspec)
            item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_torsion_table.setItem(row, 1, item2)
    
            item3 = QTableWidgetItem()
            item3.setData(Qt.DisplayRole, atom3.atomspec)
            item3.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_torsion_table.setItem(row, 2, item3)
            
            item4 = QTableWidgetItem()
            item4.setData(Qt.DisplayRole, atom4.atomspec)
            item4.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.constrained_torsion_table.setItem(row, 3, item4)
            
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            trash_button = QLabel()
            dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
            trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)).pixmap(dim, dim))
            trash_button.setToolTip("click to unfreeze")
            widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
            widget_layout.setContentsMargins(2, 2, 2, 2)
            self.constrained_torsion_table.setCellWidget(row, 4, widget_that_lets_me_horizontally_align_an_icon)
    
            self.constrained_torsion_table.resizeRowToContents(row)

        self.jobTypeChanged.emit()

    def clicked_atom_table(self, row, column):
        """remove atom from constraints if 'X' is clicked"""
        if column == 1:
            self.constrained_atoms.pop(row)
            self.constrained_atom_table.removeRow(row)
            
            self.jobTypeChanged.emit()

    def clicked_bond_table(self, row, column):
        """remove bond from constraints if 'X' is clicked"""
        if column == 2:
            self.constrained_bonds.pop(row)
            self.constrained_bond_table.removeRow(row)

            self.jobTypeChanged.emit()

    def clicked_angle_table(self, row, column):
        """remove angle from constraints if 'X' is clicked"""
        if column == 3:
            self.constrained_angles.pop(row)
            self.constrained_angle_table.removeRow(row)

            self.jobTypeChanged.emit()

    def clicked_torsion_table(self, row, column):
        """remove torsion from constraints if 'X' is clicked"""
        if column == 4:
            self.constrained_torsions.pop(row)
            self.constrained_torsion_table.removeRow(row)

            self.jobTypeChanged.emit()

    def getConstraints(self):
        """returns dictionary with contraints
        keys are:
            atoms
            bonds
            angles
            torsions"""
        if self.do_geom_opt.checkState() != Qt.Checked:
            return None
            
        elif self.use_contraints.checkState() == Qt.Unchecked:
            return None
            
        else:
            return {'atoms':self.constrained_atoms, \
                    'bonds':self.constrained_bonds, \
                    'angles':self.constrained_angles, \
                    'torsions':self.constrained_torsions}

    def getNProc(self, update_settings=True):
        """returns number of processors"""
        if update_settings:
            self.settings.last_nproc = self.nprocs.value()
        
        if self.nprocs.value() != 0:
            return self.nprocs.value()
        else:
            return None
    
    def getMem(self, update_settings=True):
        """returns memory"""
        if update_settings:
            self.settings.last_mem = self.mem.value()
        
        if self.mem.value() != 0:
            return self.mem.value()
        else:
            return None
    
    def getKWDict(self, update_settings=True):
        """returns dictiory specifying misc options for writing an input file"""
        if self.form == "Gaussian":
            route = {}
            if self.do_geom_opt.checkState() == Qt.Checked:
                route['opt'] = []
                if self.use_contraints.checkState() == Qt.Checked:
                    if len(self.constrained_atoms + self.constrained_bonds) > 0:
                        route['opt'].append("ModRedundant")
                    
                if self.ts_opt.checkState() == Qt.Checked:
                    route['opt'].append("TS")
                    route['opt'].append("CalcFC")
                    
            if self.do_freq.checkState() == Qt.Checked:
                route['freq'] = []
                temp = self.temp.value()
                route['freq'].append("temperature=%.2f" % temp)
                
                if self.num_freq.checkState() == Qt.Checked:
                    route['freq'].append('Numerical')
                
                if self.raman.checkState() == Qt.Unchecked:
                    route['freq'].append("NoRaman")
                else:
                    route['freq'].append("Raman")
                    
                if self.hpmodes.checkState() == Qt.Checked:
                    route['freq'].append('HPModes')
                    
            if self.solvent_option.currentText() != "None":
                solvent_scrf = self.solvent_option.currentText()
                if update_settings:
                    self.settings.previous_gaussian_solvent_model = solvent_scrf
                
                route['scrf'] = [solvent_scrf]
                
                solvent_name = self.solvent_name.text()
                if update_settings:
                    self.settings.previous_gaussian_solvent_name = solvent_name
                
                route['scrf'].append("solvent=%s" % solvent_name)
                
            else:
                if update_settings:
                    self.settings.previous_gaussian_solvent_model = "None"

            link0 = {}


            if self.use_checkpoint.checkState() == Qt.Checked:
                for kw in route:
                    if "CalcFC" in route[kw]:
                        if kw == "opt" or kw == "irc" :
                            #apparently, IRC can only read cartesian force constants and not interal coords
                            #opt can do ReadFC and ReadCartesianFC, but I'm just going to pick ReadCartesianFC
                            route[kw].remove("CalcFC")
                            route[kw].append("ReadCartesianFC")
                            
            if self.chk_file_path.text() != "":
                link0["chk"] = [self.chk_file_path.text()]

            if update_settings:
                self.settings.last_nproc = self.nprocs.value()
                self.settings.last_mem = self.mem.value()
                self.settings.last_opt = self.do_geom_opt.checkState() == Qt.Checked
                self.settings.last_ts = self.ts_opt.checkState() == Qt.Checked
                self.settings.last_freq = self.do_freq.checkState() == Qt.Checked
                self.settings.last_num_freq = self.num_freq.checkState() == Qt.Checked
                self.settings.last_raman = self.raman.checkState() == Qt.Checked

            return {Method.GAUSSIAN_PRE_ROUTE:link0, Method.GAUSSIAN_ROUTE:route}

        if self.form == "ORCA":
            route = []
            blocks = {}
            if self.do_geom_opt.checkState() == Qt.Checked:
                if self.ts_opt.checkState() == Qt.Checked:
                    route.append("OptTS")
                else:
                    route.append("Opt")

            if self.do_freq.checkState() == Qt.Checked:
                if self.raman.checkState() == Qt.Unchecked and self.num_freq.checkState() == Qt.Unchecked:
                    route.append("Freq")
                elif self.raman.checkState() == Qt.Checked:
                    route.append("NumFreq")
                    blocks['elprop'] = ['Polar 1']
                else:
                    route.append("NumFreq")
                    
                temp = self.temp.value()
                blocks['freq'] = ["Temp    %.2f" % temp]
 
            if self.solvent_option.currentText() != "None":
                solvent_scrf = self.solvent_option.currentText()
                if update_settings:
                    self.settings.previous_gaussian_solvent_model = solvent_scrf

                solvent_name = self.solvent_name.text()
                if update_settings:
                    self.settings.previous_gaussian_solvent_name = solvent_name
                
                if len(solvent_name) > 0:
                    route.append("%s(%s)" % (solvent_scrf, solvent_name))
                else:
                    route.append("%s" % (solvent_scrf))

            else:
                if update_settings:
                    self.settings.previous_gaussian_solvent_model = "None"

            if update_settings:
                self.settings.last_nproc = self.nprocs.value()
                self.settings.last_mem = self.mem.value()
                self.settings.last_opt = self.do_geom_opt.checkState() == Qt.Checked
                self.settings.last_ts = self.ts_opt.checkState() == Qt.Checked
                self.settings.last_freq = self.do_freq.checkState() == Qt.Checked
                self.settings.last_num_freq = self.num_freq.checkState() == Qt.Checked
                self.settings.last_raman = self.raman.checkState() == Qt.Checked

            return {Method.ORCA_ROUTE:route, Method.ORCA_BLOCKS:blocks}
            
        elif self.form == "Psi4":
            settings = {}
            after_geom = []
            
            if self.do_geom_opt.checkState() == Qt.Checked:
                after_geom.append("nrg, wfn = optimize('$FUNCTIONAL', return_wfn=True)")
                
                if self.ts_opt.checkState() == Qt.Checked:
                    settings['opt_type'] = ['ts']
                    
            
            if self.do_freq.checkState() == Qt.Checked:
                if self.num_freq.checkState() == Qt.Checked:
                    after_geom.append("nrg, wfn = frequencies('$FUNCTIONAL', return_wfn=True, dertype='gradient')")
                else:
                    after_geom.append("nrg, wfn = frequencies('$FUNCTIONAL', return_wfn=True)")

            if update_settings:
                self.settings.last_nproc = self.nprocs.value()
                self.settings.last_mem = self.mem.value()
                self.settings.last_opt = self.do_geom_opt.checkState() == Qt.Checked
                self.settings.last_ts = self.ts_opt.checkState() == Qt.Checked
                self.settings.last_freq = self.do_freq.checkState() == Qt.Checked
                self.settings.last_num_freq = self.num_freq.checkState() == Qt.Checked
                self.settings.last_raman = self.raman.checkState() == Qt.Checked
                
            info = {Method.PSI4_AFTER_GEOM:after_geom}
            if len(settings.keys()) > 0:
                info[Method.PSI4_SETTINGS] = settings
            
            return info

    def check_deleted_atoms(self):
        for atom in self.constrained_atoms[::-1]:
            if atom.deleted:
                self.constrained_atom_table.removeRow(self.constrained_atoms.index(atom))
                self.constrained_atoms.remove(atom)

        for bond in self.constrained_bonds:
            if any (atom.deleted for atom in bond):
                self.constrained_bond_table.removeRow(self.constrained_bonds.index(bond))
                self.constrained_bonds.remove(bond)

        for angle in self.constrained_angles:
            if any (atom.deleted for atom in angle):
                self.constrained_angle_table.removeRow(self.constrained_angles.index(angle))
                self.constrained_angles.remove(angle)

        for torsion in self.constrained_torsions:
            if any (atom.deleted for atom in torsion):
                self.constrained_torsion_table.removeRow(self.constrained_torsions.index(torsion))
                self.constrained_torsions.remove(torsion)


class FunctionalOption(QWidget):
    #TODO: make checking the "is_semiempirical" box disable the basis functions tab of the parent tab widget
    GAUSSIAN_FUNCTIONALS = ["B3LYP", "M06", "M06-L", "M06-2X", "ωB97X-D", "B3PW91", "B97-D", "BP86", "PBE0", "PM6", "AM1"]
    GAUSSIAN_DISPERSION = ["Grimme D2", "Grimme D3", "Becke-Johnson damped Grimme D3", "Petersson-Frisch"]
    GAUSSIAN_GRIDS = ["Default", "SuperFineGrid", "UltraFine", "FineGrid"]
    
    ORCA_FUNCTIONALS = ["B3LYP", "M06", "M06-L", "M06-2X", "ωB97X-D3", "B3PW91", "B97-D", "BP86", "PBE0", "HF-3c", "AM1"]
    ORCA_DISPERSION = ["Grimme D2", "Undamped Grimme D3", "Becke-Johnson damped Grimme D3", "Grimme D4"]
    ORCA_GRIDS = ["Default", "Grid7", "Grid6", "Grid5", "Grid4"]

    PSI4_FUNCTIONALS = ["B3LYP", "M06", "M06-L", "M06-2X", "ωB97X-D", "B3PW91", "B97-D", "BP86", "PBE0", "CCSD", "CCSD(T)"]
    PSI4_GRIDS = ["Default", "(175, 974)", "(60, 770)", "(99, 590)", "(55, 590)", "(50, 434)", "(75, 302)"]

    functionalChanged = pyqtSignal()
    
    def __init__(self, settings, init_form, parent=None):
        super().__init__(parent)

        self.settings = settings
        self.form = init_form
        
        layout = QGridLayout(self)
        margins = layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        layout.setContentsMargins(*new_margins)

        functional_form = QWidget()
        func_form_layout = QFormLayout(functional_form)
        margins = func_form_layout.contentsMargins()
        new_margins = (margins.left(), margins.top(), margins.right(), 0)
        func_form_layout.setContentsMargins(*new_margins)
        
        self.functional_option = QComboBox()
        func_form_layout.addRow(self.functional_option)
        
        keyword_label = QLabel("keyword:")
        
        self.functional_kw = QLineEdit()
        self.functional_kw.setPlaceholderText("filter functionals")
        self.functional_kw.setText(self.settings.previous_custom_func)
        self.functional_kw.setClearButtonEnabled(True)
        
        func_form_layout.addRow(keyword_label, self.functional_kw)
        
        semi_empirical_label = QLabel("basis set is integral:")
        semi_empirical_label.setToolTip("check if basis set is integral to the functional (e.g. semi-empirical methods)")
        
        self.is_semiempirical = QCheckBox()
        self.is_semiempirical.stateChanged.connect(self.something_changed) 
        self.is_semiempirical.setToolTip("check if basis set is integral to the functional (e.g. semi-empirical methods)")

        func_form_layout.addRow(semi_empirical_label, self.is_semiempirical)

        layout.addWidget(functional_form, 0, 0, Qt.AlignTop)

        self.previously_used_table = QTableWidget()
        self.previously_used_table.setColumnCount(3)
        self.previously_used_table.setHorizontalHeaderLabels(["name", "needs basis set", "trash"])
        self.previously_used_table.setSelectionBehavior(self.previously_used_table.SelectRows)
        self.previously_used_table.setEditTriggers(self.previously_used_table.NoEditTriggers)
        self.previously_used_table.setSelectionMode(self.previously_used_table.SingleSelection)
        self.previously_used_table.setSortingEnabled(True)
        for i, (name, basis_required) in enumerate(zip(self.settings.previous_functional_names, self.settings.previous_functional_needs_basis)):
            row = self.previously_used_table.rowCount()
            self.add_previously_used(row, name, basis_required)

        self.previously_used_table.cellActivated.connect(lambda *args, s=self: FunctionalOption.remove_saved_func(s, *args))
        
        self.previously_used_table.verticalHeader().setVisible(False)
        self.previously_used_table.resizeColumnToContents(0)
        self.previously_used_table.resizeColumnToContents(1)
        self.previously_used_table.resizeColumnToContents(2)
        self.previously_used_table.horizontalHeader().setStretchLastSection(False)            
        self.previously_used_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.previously_used_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.previously_used_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        
        layout.addWidget(self.previously_used_table, 1, 0, Qt.AlignTop)

        dft_form = QWidget()
        disp_form_layout = QFormLayout(dft_form)
        margins = disp_form_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        disp_form_layout.setContentsMargins(*new_margins)
        
        self.dispersion = QComboBox()
        self.dispersion.setToolTip("Dispersion correction for DFT functionals without built-in dispersion\n" + \
                                   "Important for long- or medium-range noncovalent interactions")
        self.dispersion.currentIndexChanged.connect(self.something_changed)

        disp_form_layout.addRow("empirical dispersion:", self.dispersion)
        
        self.grid = QComboBox()
        self.grid.currentIndexChanged.connect(self.something_changed)
        self.grid.setToolTip("Integration grid for methods without analytical exchange\n" + \
                             "Finer grids result in more trustworthy results\n" + \
                             "Analysis calculations should be performed on a structure that\n" + \
                             "was optimized with the same grid")
        
        disp_form_layout.addRow("integration grid:", self.grid)
        
        layout.addWidget(dft_form, 2, 0, Qt.AlignTop)
        
        self.other_options = [keyword_label, self.functional_kw, semi_empirical_label, self.is_semiempirical, self.previously_used_table]
        
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 0)
        layout.setRowStretch(2, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.functional_option.currentTextChanged.connect(self.functional_changed)
        self.setOptions(self.form)
        self.setPreviousStuff()
        self.functional_kw.textChanged.connect(self.apply_filter)

    def something_changed(self, *args, **kw):
        """called whenever something changes - emits functionalChanged"""
        self.functionalChanged.emit()

    def add_previously_used(self, row, name, basis_required):
        """add a basis set to the table of previously used options
        name            - name of basis set
        path            - path to external basis set file"""

        self.previously_used_table.insertRow(row)
        
        func = QTableWidgetItem()
        func.setData(Qt.DisplayRole, name)
        func.setToolTip("double click to use")
        self.previously_used_table.setItem(row, 0, func)
        
        needs_basis = QTableWidgetItem()
        needs_basis.setToolTip("double click to use")
        if not basis_required:
            needs_basis.setData(Qt.DisplayRole, "no")
        else:
            needs_basis.setData(Qt.DisplayRole, "yes")
        needs_basis.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.previously_used_table.setItem(row, 1, needs_basis)
        
        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        trash_button = QLabel()
        dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
        trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(dim, dim))
        trash_button.setToolTip("double click to remove from stored functionals")
        widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(2, 2, 2, 2)
        self.previously_used_table.setCellWidget(row, 2, widget_that_lets_me_horizontally_align_an_icon)
        
        self.previously_used_table.resizeRowToContents(row)
    
    def remove_saved_func(self, row, column):
        """removes the row from the table of previously used basis sets
        also deletes the corresponding entry in the settings"""              
        if column != 2:
            self.use_previous_from_table(row)
            return
        
        #XXX: make sure to call __setattr__
        cur_funcs = self.settings.previous_functional_names
        cur_semis = self.settings.previous_functional_needs_basis
    
        cur_funcs.pop(row)
        cur_semis.pop(row)
        
        self.settings.previous_functional_names = cur_funcs
        self.settings.previous_functional_needs_basis = cur_semis
        
        self.settings.save()
        
        self.previously_used_table.removeRow(row)

    def functional_changed(self, text):
        """called whenever the functional kw changes - emits functionalChanged"""
        for option in self.other_options:
            option.setVisible(text == "other")
        
        self.functionalChanged.emit()

    def apply_filter(self, text):
        """filter previous functional table when the user types in the custom kw box"""
        #text = self.functional_kw.text()
        if text:
            #the user doesn't need capturing groups
            text = text.replace('(', '\(')
            text = text.replace(')', '\)')
            m = QRegularExpression(text)
            if m.isValid():
                m.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
                
                m.optimize()
                filter = lambda row_num: m.match(self.previously_used_table.item(row_num, 0).text()).hasMatch()
            else:
                return
        
        else:
            filter = lambda row: True
            
        for i in range(0, self.previously_used_table.rowCount()):
            self.previously_used_table.setRowHidden(i, not filter(i))        

    def setOptions(self, program):
        """change options to what's available in the specified program"""
        current_func = self.functional_option.currentText()
        self.functional_option.clear()
        self.dispersion.clear()
        self.grid.clear()
        self.form = program
        if program == "Gaussian":
            self.functional_option.addItems(self.GAUSSIAN_FUNCTIONALS)
            self.functional_option.addItem("other")
            
            self.dispersion.setEnabled(True)
            self.dispersion.addItem("None")
            self.dispersion.addItems(self.GAUSSIAN_DISPERSION)
            
            self.grid.addItems(self.GAUSSIAN_GRIDS)
            
        elif program == "ORCA":
            self.functional_option.addItems(self.ORCA_FUNCTIONALS)
            self.functional_option.addItem("other")
            
            self.dispersion.setEnabled(True)
            self.dispersion.addItem("None")
            self.dispersion.addItems(self.ORCA_DISPERSION)
            
            self.grid.addItems(self.ORCA_GRIDS)
            
        elif program == "Psi4":
            self.functional_option.addItems(self.PSI4_FUNCTIONALS)
            self.functional_option.addItem("other")
            #Psi4 doesn't seem to have an 'empirical dispersion' keyword like Gaussian or ORCA
            self.dispersion.setEnabled(False)
            
            self.grid.addItems(self.PSI4_GRIDS)
            
        ndx = self.functional_option.findText(current_func, Qt.MatchExactly)
        if ndx == -1:
            ndx = self.functional_option.findText(self.settings.previous_functional, Qt.MatchExactly)
            
        if ndx != -1:
            self.functional_option.setCurrentIndex(ndx)
        
        self.functionalChanged.emit()

    def setPreviousStuff(self):
        """grabs the functional options from the last time this tool was used and set
        the current options ot that"""
        func = self.settings.previous_functional
        disp = self.settings.previous_dispersion
        grid = self.settings.previous_grid
        self.setFunctional(func)
        self.setGrid(grid)
        self.setDispersion(disp)
        
        self.functionalChanged.emit()

    def use_previous_from_table(self, row):
        """grabs the functional info from the table of previously used options and 
        sets the current functional name to that"""
        if row >= 0:
            name = self.previously_used_table.item(row, 0).text()
            self.functional_kw.setText(name)
            
            needs_basis = self.previously_used_table.item(row, 1).text()
            if needs_basis == "yes":
                self.is_semiempirical.setCheckState(Qt.Unchecked)
            else:
                self.is_semiempirical.setCheckState(Qt.Checked)            

        self.functionalChanged.emit()

    def getFunctional(self, update_settings=True):
        """returns Functional corresponding to current settings"""
        if self.form == "Gaussian":
            if self.functional_option.currentText() == "B3LYP":
                if update_settings:
                    self.settings.previous_functional = "Gaussian's B3LYP"
                
                return Functional("Gaussian's B3LYP", False)
            
        if self.functional_option.currentText() != "other":
            functional = self.functional_option.currentText()
            #omega doesn't get decoded right
            if update_settings:
                self.settings.previous_functional = functional.replace('ω', 'w')
            
            if functional in KNOWN_SEMI_EMPIRICAL:
                is_semiempirical = True
            else:
                is_semiempirical = False
                
            return Functional(functional, is_semiempirical)
            
        else:
            if update_settings:
                self.settings.previous_functional = "other"
            
            functional = self.functional_kw.text()
            if update_settings:
                self.settings.previous_custom_func = functional
            
            is_semiempirical = self.is_semiempirical.checkState() == Qt.Checked
            
            if len(functional) > 0:
                found_func = False
                for i in range(0, len(self.settings.previous_functional_names)):
                    if self.settings.previous_functional_names[i] == functional and \
                        self.settings.previous_functional_needs_basis[i] != is_semiempirical:
                        found_func = True
                
                if not found_func:
                    #append doesn't seem to call __setattr__, so the setting doesn't get updated
                    if update_settings:
                        self.settings.previous_functional_names = self.settings.previous_functional_names + [functional]
                        self.settings.previous_functional_needs_basis = self.settings.previous_functional_needs_basis + [not is_semiempirical]
                    
                        row = self.previously_used_table.rowCount()
                        self.add_previously_used(row, functional, not is_semiempirical)

            return Functional(functional, is_semiempirical)

    def getDispersion(self, update_settings=True):
        """returns EmpiricalDispersion corresponding to current settings"""
        disp = self.dispersion.currentText()
        if update_settings:
            self.settings.previous_dispersion = disp
        
        if disp == 'None':
            dispersion = None
        else:
            dispersion = EmpiricalDispersion(disp)
            
        return dispersion   

    def getGrid(self, update_settings=True):
        """returns IntegrationGrid corresponding to current settings"""
        grid = self.grid.currentText()
        if update_settings:
            self.settings.previous_grid = grid
        
        if grid == "Default":
            return None
        else:
            return IntegrationGrid(grid)

    def setGrid(self, grid):
        """sets grid option to the specified grid"""
        if grid is None:
            ndx = self.grid.findText("Default")
        else:
            ndx = self.grid.findText(grid)

        self.grid.setCurrentIndex(ndx)

    def setDispersion(self, dispersion):
        """sets dispersion to what's specified"""
        if dispersion is None:
            ndx = self.dispersion.findText("None")
        else:
            ndx = self.dispersion.findText(dispersion)

        self.dispersion.setCurrentIndex(ndx)

    def setFunctional(self, func):
        """sets functional option to match the given Functional"""
        if isinstance(func, Functional):
            test_value = func.name
        else:
            test_value = func

        if test_value in ["wB97X-D", "wB97X-D3"]:
            test_value = test_value.replace('w', 'ω')
        
        if self.form == "Gaussian" and test_value == "Gaussian's B3LYP":
            test_value = "B3LYP"
        
        ndx = self.functional_option.findText(test_value, Qt.MatchExactly)
        if ndx < 0:
            ndx = self.functional_option.findText("other", Qt.MatchExactly)
            if isinstance(func, Functional):
                self.functional_kw.setText(func.name)
                self.is_semiempirical.setChecked(func.is_semiempirical)
            else:
                self.functional_kw.setText(func)
                self.is_semiempirical.setChecked(func in KNOWN_SEMI_EMPIRICAL)

        self.functional_option.setCurrentIndex(ndx)


class BasisOption(QWidget):
    """widget for basis set options
    requires a parent object and a Settings object with 
    self.name_setting
    self.path_setting
    self.last_used
    self.last_custom
    self.last_custom_builtin
    self.last_custom_path
    
    layout has a combocox for basis options (self.options)
    if basis is "other", the widget will show a lineedit to enter a keyword for a different basis
    a table will also appear to show the previously-used basis sets
    double clicking an item on the table will set the basis set to that
    
    if the "other" basis set is not built-in, a lineedit will appear asking for a path to a basis set file
    
    if multiple BasisOptions are present in one BasisWidget, a list of elements will appear
    selecting an element on the list will deselect it on lists for other BasisOptions
    """
    
    basisChanged = pyqtSignal()

    #for psi4, ECP's are included in basis set definitions
    options = ["def2-SVP", "def2-TZVP", "aug-cc-pVDZ", "aug-cc-pVTZ", "6-311+G**", "SDD", "LANL2DZ", "other"]
    psi4_options = ["def2-SVP", "def2-TZVP", "aug-cc-pVDZ", "aug-cc-pVTZ", "6-311+G**", "other"]
    
    name_setting = "previous_basis_names"
    path_setting = "previous_basis_paths"
    last_used = "last_basis"
    last_custom = "last_custom_basis_kw"
    last_custom_builtin = "last_custom_basis_builtin"
    last_custom_path = "last_basis_path"
    last_elements = "last_basis_elements"
    aux_setting = "last_basis_aux"

    toolbox_name = "basis_toolbox"
    
    aux_available = True
    
    basis_class = Basis

    def __init__(self, parent, settings, form):
        self.parent = parent
        self.settings = settings
        self.form = form
        super().__init__(parent)

        self.layout = QGridLayout(self)
        
        self.basis_names = QWidget()
        self.basis_name_options = QFormLayout(self.basis_names)
        self.basis_name_options.setContentsMargins(0, 0, 0, 0)
        
        self.basis_option = QComboBox()
        self.basis_option.addItems(self.options)
        self.basis_option.currentIndexChanged.connect(self.basis_changed)
        self.basis_name_options.addRow(self.basis_option)

        self.elements = QListWidget()
        #make element list roughly as wide as two characters + a scroll bar
        #this keeps the widget as narrow as possible so it doesn't take up the entire screen
        scroll_width = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        self.elements.setMinimumWidth(scroll_width + int(1.5*self.fontMetrics().boundingRect("QQ").width()))
        self.elements.setMaximumWidth(scroll_width + int(2*self.fontMetrics().boundingRect("QQ").width()))
        #set the max. height too b/c I can't seem to get it to respect setRowStretch
        self.elements.setMaximumHeight(int(6*self.fontMetrics().boundingRect("QQ").height()))
        self.elements.setSelectionMode(QListWidget.MultiSelection)
        self.elements.itemSelectionChanged.connect(lambda *args, s=self: self.parent.check_elements(s))
        self.elements.itemSelectionChanged.connect(lambda *args, s=self: self.parent.something_changed())
        self.layout.addWidget(self.elements, 0, 2, 3, 1, Qt.AlignTop)
        
        self.aux_type = QComboBox()
        self.aux_type.currentIndexChanged.connect(lambda *args, s=self: self.parent.check_elements(s))
        self.aux_type.addItem("no")
        aux_label = QLabel("auxiliary:")
        self.basis_name_options.addRow(aux_label, self.aux_type)
    
        self.custom_basis_kw = QLineEdit()
        self.custom_basis_kw.textChanged.connect(self.apply_filter)
        self.custom_basis_kw.textChanged.connect(self.update_tooltab)
        self.custom_basis_kw.setPlaceholderText("filter basis sets")
        self.custom_basis_kw.setClearButtonEnabled(True)
        
        keyword_label = QLabel("keyword:")
        self.basis_name_options.addRow(keyword_label, self.custom_basis_kw)

        self.is_builtin = QCheckBox()
        self.is_builtin.setToolTip("checked: basis set is avaiable in the software with a keyword\n" + \
                                   "unchecked: basis set is stored in an external file")
        self.is_builtin.stateChanged.connect(self.show_gen_path)
        
        is_builtin_label = QLabel("built-in:")
        self.basis_name_options.addRow(is_builtin_label, self.is_builtin)
    
        self.layout.addWidget(self.basis_names, 0, 0, 4, 2)
        
        gen_path_label = QLabel("basis file:")
        self.layout.addWidget(gen_path_label, 3, 0, 1, 1, Qt.AlignVCenter | Qt.AlignLeft)
        
        self.path_to_basis_file = QLineEdit()
        self.layout.addWidget(self.path_to_basis_file, 3, 1, 1, 1, Qt.AlignVCenter)
        
        browse_button = QPushButton("browse...")
        browse_button.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(browse_button, 3, 2, 1, 1, Qt.AlignVCenter)
        
        self.previously_used_table = QTableWidget()
        self.previously_used_table.setColumnCount(3)
        self.previously_used_table.setHorizontalHeaderLabels(["name", "basis file", "trash"])
        self.previously_used_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.previously_used_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.previously_used_table.setSelectionMode(QTableWidget.SingleSelection)
        #this sometimes causes an empty row to be added to the 'previous' table when the file is exported
        #don't know why
        #self.previously_used_table.setSortingEnabled(True)
        self.previously_used_table.verticalHeader().setVisible(False)
        for i, (name, path) in enumerate(zip(self.settings.__getattr__(self.name_setting), self.settings.__getattr__(self.path_setting))):
            row = self.previously_used_table.rowCount()
            self.add_previously_used(row, name, path, False)
        
        self.previously_used_table.resizeColumnToContents(0)
        self.previously_used_table.resizeColumnToContents(1)
        self.previously_used_table.resizeColumnToContents(2)
        self.previously_used_table.horizontalHeader().setStretchLastSection(False)            
        self.previously_used_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.previously_used_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.previously_used_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
            
        self.previously_used_table.cellActivated.connect(lambda *args, s=self: BasisOption.remove_saved_basis(s, *args))
        self.layout.addWidget(self.previously_used_table, 4, 0, 1, 3, Qt.AlignTop)

        self.custom_basis_options = [keyword_label, self.custom_basis_kw, is_builtin_label, self.is_builtin, self.previously_used_table]
        self.gen_options = [gen_path_label, self.path_to_basis_file, browse_button]

        self.aux_options = [aux_label, self.aux_type]
        
        if not self.aux_available:
            for opt in self.aux_options:
                opt.setVisible(False)

        #this doesn't seem to do anything?
        self.layout.setColumnStretch(0, 0)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 0)
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(4, 1)
        
        self.setOptions(self.form)
        self.aux_type.currentIndexChanged.connect(self.basis_changed)

    def setOptions(self, program):
        """display options that are available in the specified program"""
        self.blockSignals(True)
        
        basis = self.basis_option.currentText()
        aux = self.aux_type.currentText()
        self.basis_option.clear()
        
        elements = self.currentElements()
        
        if program == "Gaussian":
            self.basis_option.addItems(self.options)
            ndx = self.basis_option.findText(basis, Qt.MatchExactly)
            if ndx != -1:
                self.basis_option.setCurrentIndex(ndx)
            else:
                self.basis_option.setCurrentIndex(len(self.options) - 1)
                
            if self.getAuxType() != "no":
                self.destruct()
                return 
                
            for opt in self.aux_options:
                opt.setVisible(False)

        elif program == "ORCA":
            self.basis_option.addItems(self.options)
            ndx = self.basis_option.findText(basis, Qt.MatchExactly)
            if ndx != -1:
                self.basis_option.setCurrentIndex(ndx)
            else:
                self.basis_option.setCurrentIndex(len(self.options) - 1)
                
            self.aux_type.clear()
            if self.aux_available:
                for opt in self.aux_options:
                    opt.setVisible(True)
            
            self.aux_type.addItem("no")
            self.aux_type.addItems(BasisSet.ORCA_AUX)

        elif program == "Psi4":
            self.basis_option.addItems(self.psi4_options)
            ndx = self.basis_option.findText(basis, Qt.MatchExactly)
            if ndx != -1:
                self.basis_option.setCurrentIndex(ndx)
            else:
                self.basis_option.setCurrentIndex(len(self.psi4_options) - 1)
                
            self.aux_type.clear()
            if self.aux_available:
                for opt in self.aux_options:
                    opt.setVisible(True)
                
            self.aux_type.addItem("no")
            self.aux_type.addItems(BasisSet.PSI4_AUX)
        
        self.setAux(aux)
        self.setSelectedElements(elements)
        
        self.blockSignals(False)

    def open_file_dialog(self):
        """ask user to locate external basis file on their computer"""
        if self.form == "Gaussian":
            filename, _ = QFileDialog.getOpenFileName(filter="Basis Set Files (*.gbs)")
        elif self.form == "Psi4":
            filename, _ = QFileDialog.getOpenFileName(filter="Basis Set Files (*.gbs)")
        elif self.form == "ORCA":
            filename, _ = QFileDialog.getOpenFileName(filter="Basis Set Files (*.basis)")
        
        if filename:
            self.path_to_basis_file.setText(filename)

    def apply_filter(self, text):
        """filter list of previously used basis sets when the user types in the custom kw box"""
        #text = self.custom_basis_kw.text()
        if text:
            #the user doesn't need capturing groups
            text = text.replace('(', '\(')
            text = text.replace(')', '\)')
            m = QRegularExpression(text)
            if m.isValid():
                m.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
                
                m.optimize()
                filter = lambda row_num: m.match(self.previously_used_table.item(row_num, 0).text()).hasMatch()
            else:
                return
        
        else:
            filter = lambda row: True
            
        for i in range(0, self.previously_used_table.rowCount()):
            self.previously_used_table.setRowHidden(i, not filter(i))        
        
        self.previously_used_table.resizeColumnToContents(0)

    def show_gen_path(self, state):
        """show/hide the path to external basis file when the 'builtin' checkbox is toggled"""
        for option in self.gen_options:
            option.setVisible(state == Qt.Unchecked)
    
    def basis_changed(self):
        """tracks changes to basis set dropdown menu
        if option changed from/to "other", make some options [in]visible"""
        for option in self.custom_basis_options:
            option.setVisible(self.basis_option.currentText() == "other")
            
        for option in self.gen_options:
            option.setVisible(self.is_builtin.checkState() == Qt.Unchecked and \
                              self.basis_option.currentText() == "other")
        
        if self.basis_option.currentText() == "other":
            #if the previous basis sets are shown, only the basis set table should stretch
            self.layout.setRowStretch(0, 0)
            self.layout.setRowStretch(1, 0)
            self.layout.setRowStretch(2, 0)       
            self.layout.setRowStretch(3, 0)
            self.layout.setRowStretch(4, 1)
        else:
            #otherwise, the element list should stretch
            self.layout.setRowStretch(0, 1)
            self.layout.setRowStretch(1, 0)
            self.layout.setRowStretch(2, 0)       
            self.layout.setRowStretch(3, 0)
                
        if hasattr(self, "parent_toolbox"):
            self.update_tooltab()
            
        self.basisChanged.emit()
    
    def setToolBox(self, toolbox):
        """toolbox should be either the container that holds basis options or ecp options"""
        self.parent_toolbox = toolbox
    
    def update_tooltab(self):
        """sets the name of self's tab"""
        basis_name = self.currentBasis().name
        ndx = self.parent_toolbox.indexOf(self)
        if len(self.parent.basis_options) != 1 or len(self.parent.ecp_options) != 0:
            elements = "(%s)" % ", ".join(self.currentElements())
        else:
            elements = ""
        
        if self.aux_available and self.getAuxType() != "no":
            basis_name += "/%s" % self.getAuxType()

        self.parent_toolbox.setTabText(ndx, "%s %s" % (basis_name, elements))

    def show_elements(self, value):
        """hides/shows element list"""
        if value:
            self.layout.addWidget(self.basis_names, 0, 0, 3, 2)
        else:
            self.layout.addWidget(self.basis_names, 0, 0, 3, 3)
        self.elements.setVisible(value)

    def destruct(self):
        """removes self from parent
        calls parent.remove_basis(self)"""
        self.parent.remove_basis(self)
    
    def currentElements(self):
        """returns a list of element names that are selected"""
        return [self.elements.item(i).text() for i in range(0, self.elements.count()) if self.elements.item(i).isSelected()]

    def allElements(self):
        """returns a list of all available element names"""
        return [self.elements.item(i).text() for i in range(0, self.elements.count())]
    
    def currentBasis(self, update_settings=False, index=0):
        """get current basis info
        if basis is user-defined, this will also update the basis settings
        """
        #XXX: don't use append when updating list settings
        basis = self.basis_option.currentText()
        if update_settings:
            cur_last_used = [x for x in self.settings.__getattr__(self.last_used)]
            cur_last_cust = [x for x in self.settings.__getattr__(self.last_custom)]
            cur_last_builtin = [x for x in self.settings.__getattr__(self.last_custom_builtin)]
            cur_last_elements = [x for x in self.settings.__getattr__(self.last_elements)]
            while len(cur_last_used) <= index:
                cur_last_used.append(basis)
                cur_last_cust.append(basis)
                cur_last_builtin.append("" if self.is_builtin.checkState() == Qt.Checked else self.path_to_basis_file.text())
                cur_last_elements.append(",".join(self.currentElements()))
                        
            cur_last_used[index] = basis
            cur_last_cust[index] = self.custom_basis_kw.text()
            cur_last_builtin[index] = "" if self.is_builtin.checkState() == Qt.Checked else self.path_to_basis_file.text()
            cur_last_elements[index] = ",".join(self.currentElements())

            self.settings.__setattr__(self.last_used, cur_last_used)
            self.settings.__setattr__(self.last_custom, cur_last_cust)
            self.settings.__setattr__(self.last_custom_builtin, cur_last_builtin)
            self.settings.__setattr__(self.last_elements, cur_last_elements)

        if self.aux_available:
            aux = self.getAuxType()
            
            if update_settings:
                cur_last_aux = [x for x in self.settings.__getattr__(self.aux_setting)]
                while len(cur_last_aux) <= index:
                    cur_last_aux.append(aux)
                
                cur_last_aux[index] = aux
                
                self.settings.__setattr__(self.aux_setting, cur_last_aux)

            if aux == "no":
                aux = None
                
        else:
            aux = None

        if basis != "other":
            basis_obj = self.basis_class(basis, self.currentElements(), aux_type=aux)
            return basis_obj
        else:
            basis = self.custom_basis_kw.text()
            if update_settings:
                cur_settings = self.settings.__getattr__(self.last_custom)

            if self.is_builtin.checkState() == Qt.Checked:
                gen_path = False
            else:
                gen_path = self.path_to_basis_file.text()
                
                if update_settings:
                    self.settings.__setattr__(self.last_custom_path, gen_path)

            if update_settings:
                cur_last_used = [x for x in self.settings.__getattr__(self.last_used)]
                cur_last_cust = [x for x in self.settings.__getattr__(self.last_custom)]
                cur_last_builtin = [x for x in self.settings.__getattr__(self.last_custom_builtin)]
                while len(cur_last_used) <= index:
                    cur_last_used.append("other")
                    cur_last_cust.append(basis)
                    cur_last_builtin.append("" if self.is_builtin.checkState() == Qt.Checked else self.path_to_basis_file.text())
                    cur_last_elements.append(",".join(self.currentElements()))
            
                cur_last_used[index] = "other"
                cur_last_cust[index] = basis
                cur_last_builtin[index] = "" if self.is_builtin.checkState() == Qt.Checked else self.path_to_basis_file.text()
                cur_last_elements[index] = ",".join(self.currentElements())
        
                self.settings.__setattr__(self.last_used, cur_last_used)
                self.settings.__setattr__(self.last_custom, cur_last_cust)
                self.settings.__setattr__(self.last_custom_builtin, cur_last_builtin)
                self.settings.__setattr__(self.last_elements, cur_last_elements)

                found_in_previous = False
                for i in range(0, len(self.settings.__getattr__(self.name_setting))):
                    if basis == self.settings.__getattr__(self.name_setting)[i] and \
                        (gen_path == self.settings.__getattr__(self.path_setting)[i] or gen_path is False):
                        found_in_previous = True
                        break
                        
                if not found_in_previous:
                    row = self.previously_used_table.rowCount()
                    self.add_previously_used(row, basis, gen_path if gen_path else "")
                    #XXX: calling setattr will update the setting
                    new_names = self.settings.__getattr__(self.name_setting) + [basis if basis != "" else "user-defined"]
                    new_paths = self.settings.__getattr__(self.path_setting) + [gen_path if gen_path else ""]
                    self.settings.__setattr__(self.name_setting, new_names)
                    self.settings.__setattr__(self.path_setting, new_paths)
               
                    self.previously_used_table.resizeColumnToContents(0)
                    self.previously_used_table.resizeColumnToContents(2)

            basis_obj = self.basis_class(basis, self.currentElements(), aux_type=aux, user_defined=gen_path)
            return basis_obj

    def add_previously_used(self, row, name, path, add_to_others=True):
        """add a basis set to the table of previously used options
        name            - name of basis set
        path            - path to external basis set file
        add_to_others   - also add the option to siblings (should be False when a new 
                            BasisOption is created in the BasisWidget to avoid duplicates)"""
        if add_to_others:
            self.parent.add_to_all_but(self, row, name, path)
        
        self.previously_used_table.insertRow(row)
        
        basis = QTableWidgetItem()
        basis.setData(Qt.DisplayRole, name)
        basis.setToolTip("double click to use")
        self.previously_used_table.setItem(row, 0, basis)

        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        trash_button = QLabel()
        dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
        trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(dim, dim))
        trash_button.setToolTip("double click to remove from stored basis sets")
        widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(2, 2, 2, 2)
        self.previously_used_table.setCellWidget(row, 2, widget_that_lets_me_horizontally_align_an_icon)
        
        self.previously_used_table.resizeRowToContents(row)
        
        gbs_file = QTableWidgetItem()
        gbs_file.setData(Qt.DisplayRole, path)
        gbs_file.setToolTip("double click to use")
        self.previously_used_table.setItem(row, 1, gbs_file)
        
        self.previously_used_table.resizeColumnToContents(0)
        self.previously_used_table.resizeColumnToContents(1)
        self.previously_used_table.resizeColumnToContents(2)

    def setElements(self, elements):
        """sets the available elements"""
        for i in range(self.elements.count(), -1, -1):
            self.elements.takeItem(i)
        
        self.elements.addItems(elements)
        self.elements.sortItems()

    def setSelectedElements(self, elements):
        """sets the selected elements"""
        for i in range(0, self.elements.count()):
            row = self.elements.item(i)
            row.setSelected(False)
            
        for element in elements:
            if element not in self.allElements():
                if element.lower() == "tm" or elements == "tm":
                    #all transition metals
                    for element in TMETAL.keys():
                        items = self.elements.findItems(element, Qt.MatchExactly)
                        if len(items) > 0:
                            for item in items:
                                item.setSelected(True)
                                
                elif element.lower() == "!tm" or elements == "!tm":
                    for i in range(0, self.elements.count()):
                        item = self.elements.item(i)
                        if item.text() not in TMETAL:
                            item.setSelected(True)
                
                elif element.lower() == "all" or elements == "all":
                    for i in range(0, self.elements.count()):
                        item = self.elements.item(i)
                        item.setSelected(True)
            
                continue
            
            row = self.elements.findItems(element, Qt.MatchExactly)[0]
            row.setSelected(True)

    def remove_saved_basis(self, row, column):
        """removes the row from the table of previously used basis sets
        also deletes the corresponding entry in the settings"""              
        if column != 2:
            self.use_previous_from_table(row)
            return
                                        
        cur_basis = self.settings.__getattr__(self.name_setting)
        cur_paths = self.settings.__getattr__(self.path_setting)
    
        cur_basis.pop(row)
        cur_paths.pop(row)
        
        self.settings.__setattr__(self.name_setting, cur_basis)
        self.settings.__setattr__(self.path_setting, cur_paths)
        
        self.settings.save()
        
        self.previously_used_table.removeRow(row)
        
        self.parent.remove_from_all_but(self, row)
    
    def use_previous_from_table(self, row):
        """grabs the basis info from the table of previously used options and 
        sets the current basis name/path to that"""
        if row >= 0:
            name = self.previously_used_table.item(row, 0).text()
            self.custom_basis_kw.setText(name)
            
            path = self.previously_used_table.item(row, 1).text()
            if path == "":
                self.is_builtin.setCheckState(Qt.Checked)
            else:
                self.is_builtin.setCheckState(Qt.Unchecked)            
                self.path_to_basis_file.setText(path)

    def setBasis(self, name=None, custom_kw=None, basis_path=False):
        """set options to match these options"""
        if name is not None:
            ndx = self.basis_option.findData(name, Qt.MatchExactly)
            if ndx < 0:
                ndx = self.basis_option.findData("other", Qt.MatchExactly)
                self.custom_basis_kw.setText(name)
            
            self.basis_option.setCurrentIndex(ndx)

        if custom_kw is not None:
            self.custom_basis_kw.setText(custom_kw)

        if basis_path is False:
            self.is_builtin.setCheckState(Qt.Checked)
        elif len(basis_path) > 0:
            self.is_builtin.setCheckState(Qt.Unchecked)
            self.path_to_basis_file.setText(basis_path)
        else:
            self.is_builtin.setCheckState(Qt.Checked)
            self.path_to_basis_file.setText(self.settings.__getattr__(self.last_custom_path))

    def setAux(self, name):
        """set auxiliary type to 'name'"""
        if name is None:
            name = "no"

        ndx = self.aux_type.findData(name, Qt.MatchExactly)
        if ndx >= 0:
            self.aux_type.setCurrentIndex(ndx)

    def getAuxType(self):
        """returns aux type"""
        return self.aux_type.currentText()


class ECPOption(BasisOption):
    options = ["SDD", "LANL2DZ", "other"]
    psi4_options = options
    label_text = "ECP:"
    name_setting = "previous_ecp_names"
    path_setting = "previous_ecp_paths"
    last_used = "last_ecp"
    last_custom = "last_custom_ecp_kw"
    last_custom_builtin = "last_custom_ecp_builtin"
    last_custom_path = "last_ecp_path"
    last_elements = "last_ecp_elements"

    aux_available = False

    basis_class = ECP

    def update_tooltab(self):
        """renames the tab for this ecp"""
        basis_name = self.currentBasis().name
        elements = "(%s)" % ", ".join(self.currentElements())
        ndx = self.parent_toolbox.indexOf(self)
        
        self.parent_toolbox.setTabText(ndx, "%s %s" % (basis_name, elements))


class BasisWidget(QWidget):
    """widget to store and manage BasisOptions and ECPOptions"""
    
    basisChanged = pyqtSignal()
    
    def __init__(self, settings, init_form="Gaussian", parent=None):
        super().__init__(parent)
        self.form = init_form
        self.settings = settings
        
        self.basis_options = []
        self.ecp_options = []
        self.elements = []
        
        self.layout = QGridLayout(self)
        
        valence_side = QWidget()
        valence_side_layout = QGridLayout(valence_side)
        valence_basis_area = QGroupBox("basis set")
        valence_layout = QGridLayout(valence_basis_area)
        self.basis_toolbox = QTabWidget()
        self.basis_toolbox.setTabsClosable(True)
        self.basis_toolbox.tabCloseRequested.connect(self.close_basis_tab)
        self.basis_toolbox.setStyleSheet('QTabWidget::pane {border: 1px;}')
        valence_layout.addWidget(self.basis_toolbox, 0, 0)
        
        self.basis_warning = QStatusBar()
        self.basis_warning.setSizeGripEnabled(False)
        self.basis_warning.setStyleSheet("color : red")
        self.layout.addWidget(self.basis_warning, 1, 0, 1, 1)
        
        ecp_side = QWidget()
        self.ecp_widget = ecp_side
        ecp_side_layout = QGridLayout(ecp_side)
        ecp_basis_area = QGroupBox("effective core potential")        
        ecp_layout = QGridLayout(ecp_basis_area)
        self.ecp_toolbox = QTabWidget()
        self.ecp_toolbox.setTabsClosable(True)
        self.ecp_toolbox.tabCloseRequested.connect(self.close_ecp_tab)
        self.ecp_toolbox.setStyleSheet('QTabWidget::pane {border: 1px;}')
        ecp_layout.addWidget(self.ecp_toolbox, 0, 0)

        valence_side_layout.addWidget(valence_basis_area, 0, 0)
        ecp_side_layout.addWidget(ecp_basis_area, 0, 0)
        
        self.new_basis_button = QPushButton("new basis")
        self.new_basis_button.clicked.connect(self.new_basis)
        valence_side_layout.addWidget(self.new_basis_button, 1, 0)
                
        self.new_ecp_button = QPushButton("new ECP")
        self.new_ecp_button.clicked.connect(self.new_ecp)
        ecp_side_layout.addWidget(self.new_ecp_button, 1, 0)
        
        valence_layout.setContentsMargins(0, 0, 0, 0)
        ecp_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(True)
        splitter.addWidget(valence_side)
        splitter.addWidget(ecp_side)
        
        self.layout.addWidget(splitter, 0, 0, 1, 1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 0)
        
        for i in range(0, self.settings.last_number_basis):
            self.new_basis(use_saved=i)        
        
        for i in range(0, self.settings.last_number_ecp):
            self.new_ecp(use_saved=i)
            
        self.setOptions(self.form)

    def something_changed(self, *args, **kw):
        """called whenever something changes - emits basisChanged"""
        self.basisChanged.emit()

    def close_ecp_tab(self, index):
        """the 'x' was clicked on an ecp tab - delete that ecp"""
        self.remove_basis(self.ecp_options[index])
        
        self.basisChanged.emit()
    
    def close_basis_tab(self, index):
        """the 'x' was clicked on one of the basis tabs - delete that basis"""
        self.remove_basis(self.basis_options[index])

        self.basisChanged.emit()

    def new_ecp(self, checked=None, use_saved=None):
        """add an ECPOption"""
        new_basis = ECPOption(self, self.settings, self.form)
        new_basis.setToolBox(self.ecp_toolbox)
        new_basis.setElements(self.elements)
        new_basis.basisChanged.connect(self.something_changed)
        if use_saved is None:
            use_saved = len(self.ecp_options)
        if use_saved < len(self.settings.last_ecp):
            name = self.settings.last_ecp[use_saved]
            custom = self.settings.last_custom_ecp_kw[use_saved]
            builtin = self.settings.last_custom_ecp_builtin[use_saved]
            new_basis.setBasis(name, custom, builtin)
            #new_basis.setSelectedElements(self.settings.last_ecp_elements[use_saved].split(','))
            
        new_basis.basis_changed()
        
        self.ecp_options.append(new_basis)
        
        self.check_elements()

        self.ecp_toolbox.addTab(new_basis, "")
        self.ecp_toolbox.setCurrentWidget(new_basis)

        self.refresh_ecp()
        self.refresh_basis()

        self.basisChanged.emit()

    def new_basis(self, checked=None, use_saved=None):
        """add a BasisOption"""
        new_basis = BasisOption(self, self.settings, form=self.form)
        new_basis.setToolBox(self.basis_toolbox)
        new_basis.setElements(self.elements)
        new_basis.basisChanged.connect(self.something_changed)
        if use_saved is None:
            use_saved = len(self.basis_options)
        if use_saved < len(self.settings.last_basis):
            #must set auxiliary before selected elements
            #otherwise elements will be deselected on non-auxiliary basis
            #if they are selected on a new auxiliary basis
            if self.form != "Gaussian":
                aux = self.settings.last_basis_aux[use_saved]
                new_basis.setAux(aux)

            name = self.settings.last_basis[use_saved]
            custom = self.settings.last_custom_basis_kw[use_saved]
            builtin = self.settings.last_custom_basis_builtin[use_saved]
            new_basis.setBasis(name, custom, builtin)
            #new_basis.setSelectedElements(self.settings.last_basis_elements[use_saved].split(','))
        
        else:
            new_basis.setBasis()
        
        new_aux = new_basis.getAuxType()

        elements_without_basis = []
        for element in self.elements:
            if not any([element in basis.currentElements() for basis in self.basis_options if basis.getAuxType() == new_aux]):
                elements_without_basis.append(element)
        
        new_basis.setSelectedElements(elements_without_basis)

        self.basis_options.append(new_basis)
        #set options needs to be after appending to basis_options
        #if the basis is not available for whatever program, the
        #basis might try to delete itself
        #new_basis.setOptions(self.form)
        new_basis.basis_changed()

        if len(self.basis_options) == 1 and len(self.ecp_options) == 0:
            self.basis_options[0].setSelectedElements(self.elements)
            self.basis_warning.setVisible(False)

        self.check_elements()

        self.basis_toolbox.addTab(new_basis, "")
        self.basis_toolbox.setCurrentWidget(new_basis)

        self.refresh_basis()
    
        self.basisChanged.emit()
    
    def remove_basis(self, basis):
        """removes basis (BasisOption or ECPOption)"""
        if isinstance(basis, ECPOption):
            self.ecp_toolbox.removeTab(self.ecp_toolbox.indexOf(basis))
            basis.deleteLater()
            self.ecp_options.remove(basis)
            self.refresh_ecp()
        
        elif isinstance(basis, BasisOption):
            self.basis_toolbox.removeTab(self.basis_toolbox.indexOf(basis))
            basis.deleteLater()
            self.basis_options.remove(basis)
            self.refresh_basis()
            
        if len(self.basis_options) == 1 and len(self.ecp_options) == 0:
            self.basis_options[0].setSelectedElements(self.elements)
            self.basis_options[0].update_tooltab()
            self.basis_options[0].show_elements(False)
            
        self.check_elements()
        
        self.basisChanged.emit()

    def refresh_basis(self):
        """repositions all BasisOptions and shows element lists if appropriate
        if only one BasisOption (and not ECPOptions) remain, sets the elements too"""
        for i, basis in enumerate(self.basis_options):
            basis.update_tooltab()
            
            basis.show_elements(not (len(self.basis_options) == 1 and len(self.ecp_options) == 0))

    def check_elements(self, child=None):
        """check to see if any elements don't have a (valence) basis set
        if child is not None, all selected elements from child will be deselected from
        other children of the same type (calls remove_elements_from_all_but)"""
        if child is not None:
            self.remove_elements_from_all_but(child, child.currentElements())

        elements_without_basis = {"no":self.elements.copy()}
        for basis in self.basis_options:
            aux = basis.getAuxType()
            if aux not in elements_without_basis:
                elements_without_basis[aux] = self.elements.copy()    
            
            for element in basis.currentElements():
                if element in elements_without_basis[aux]:
                    elements_without_basis[aux].remove(element)
        
        for basis in self.basis_options + self.ecp_options:
            basis.update_tooltab()
        
        if any(len(elements_without_basis[aux]) != 0 for aux in elements_without_basis):
            s = ""
            for aux in elements_without_basis.keys():
                if len(elements_without_basis[aux]) != 0:
                    if aux == "no":
                        s += "elements with no basis: %s" % ", ".join(elements_without_basis[aux])
                    
                    else:
                        s += "elements with no %s auxiliary basis: %s" %  (aux, ", ".join(elements_without_basis[aux]))
                    
                    if len(s) != 0:
                        s += '; \n'
            
            self.basis_warning.showMessage(s.strip('; \n'))
            self.basis_warning.setVisible(True)
        else:
            self.basis_warning.showMessage("elements with no basis: None")
            self.basis_warning.setVisible(False)

    def refresh_ecp(self):
        """repositions ecp options
        may be called after one option is removed"""
        for i, basis in enumerate(self.ecp_options):
            basis.update_tooltab()
            
            basis.show_elements(not (len(self.basis_options) == 1 and len(self.ecp_options) == 0))

    def get_basis(self, update_settings=True):
        """returns ([Basis], [ECP]) corresponding to the current settings"""
        basis_set = []
        ecp = []
        for i, basis in enumerate(self.basis_options):
            basis_obj = basis.currentBasis(update_settings, index=i)
            basis_set.append(basis_obj)

        if update_settings:
            self.settings.last_number_basis = len(self.basis_options)
        
        if len(basis_set) == 0:
            basis_set = None
                
        for i, basis in enumerate(self.ecp_options):
            basis_obj = basis.currentBasis(update_settings, index=i)
            ecp.append(basis_obj)

        if len(ecp) == 0:
            ecp = None

        if update_settings:
            self.settings.last_number_ecp = len(self.ecp_options)
        
        return basis_set, ecp

    def getBasis(self, update_settings=True):
        """returns BasisSet object corresponding to the current settings"""
        basis, ecp = self.get_basis(update_settings=update_settings)
        
        return BasisSet(basis, ecp)

    def setBasis(self, basis_set):
        """sets basis to match input BasisSet"""
        for i in range(len(self.basis_options)-1, -1, -1):
            self.close_basis_tab(i)        
        
        for i in range(len(self.ecp_options)-1, -1, -1):
            self.close_ecp_tab(i)

        for i, basis in enumerate(basis_set.basis):
            self.new_basis()

            self.basis_options[i].setBasis(basis.name, basis_path=basis.user_defined)
            self.basis_options[i].setAux(basis.aux_type)
            if len(basis_set.basis) == 1 and (basis_set.ecp is None or len(basis_set.ecp) == 0):
                #a preset might have only saved one basis set
                #we'll use it for all elements
                self.basis_options[i].setSelectedElements(['all'])
            else:
                self.basis_options[i].setSelectedElements(basis.elements)
            
        if basis_set.ecp is not None:
            for i, basis in enumerate(basis_set.ecp):
                self.new_ecp()
    
                self.ecp_options[i].setBasis(basis.name, basis_path=basis.user_defined)
                self.ecp_options[i].setSelectedElements(basis.elements)

    def add_to_all_but(self, exclude_option, row, name, path):
        """called by child BasisOption
        adds a previously-used basis set to the previously-used basis set table of all other child BasisOptions"""
        if isinstance(exclude_option, ECPOption):
            for option in self.ecp_options:
                if option is not exclude_option:
                    option.add_previously_used(row, name, path, False)         
        
        else:
            for option in self.basis_options:
                if option is not exclude_option:
                    option.add_previously_used(row, name, path, False)     

    def remove_from_all_but(self, exclude_option, row):
        """called by child BasisOption
        removes row (int) from all other child BasisOption's table of previously-used basis sets"""
        if isinstance(exclude_option, ECPOption):
            for option in self.ecp_options:
                if option is not exclude_option:
                    option.previously_used_table.removeRow(row)
        
        else:
            for option in self.basis_options:
                if option is not exclude_option:
                    option.previously_used_table.removeRow(row)  

    def remove_elements_from_all_but(self, exclude_option, element_list):
        """deselects element in other BasisOptions (or ECPOptions)"""
        if isinstance(exclude_option, ECPOption):
            for option in self.ecp_options:
                if option is not exclude_option:
                    for i in range(0, option.elements.count()):
                        if option.elements.item(i).text() in element_list:
                            option.elements.item(i).setSelected(False)
                                
        else:
            aux = exclude_option.getAuxType()
            for option in self.basis_options:
                if option is not exclude_option and option.getAuxType() == aux:
                    for i in range(0, option.elements.count()):
                        if option.elements.item(i).text() in element_list:
                            option.elements.item(i).setSelected(False)

    def setOptions(self, program):
        """changes the basis set options to display what's available for the specified program"""
        self.form = program
        #reverse basis options because some might delete themselves
        #like if auxiliary basis sets aren't available in the program
        for basis in self.basis_options[::-1]:
            basis.setOptions(program)
            
        for basis in self.ecp_options:
            basis.setOptions(program)
            
        if program == "Psi4":
            self.ecp_widget.setVisible(False)
            for ecp in self.ecp_options:
                self.remove_basis(ecp)
        else:
            self.ecp_widget.setVisible(True)

    def setElements(self, element_list):
        """sets the available elements in all child BasisOptions
        if an element is already available, it will not be removed"""
        previous_elements = self.elements
        self.elements = element_list
        
        new_elements = [element for element in element_list if element not in previous_elements]
        del_elements = [element for element in previous_elements if element not in element_list]

        if len(new_elements) == 0 and len(del_elements) == 0:
            return

        for j, basis in enumerate(self.basis_options):
            aux = basis.getAuxType()
            elements_with_different_basis = []
            for other_basis in self.basis_options:
                if other_basis is not basis and other_basis.getAuxType() == aux:
                    elements_with_different_basis.extend(other_basis.currentElements())

            if len(del_elements) > 0:
                for i in range(basis.elements.count()-1, -1, -1):
                    if basis.elements.item(i).text() in del_elements:
                        basis.elements.takeItem(i)
            
            if len(new_elements) > 0:
                basis.elements.addItems(new_elements)
                basis.elements.sortItems()
                if j < len(self.settings.last_basis_elements):
                    previous_elements = self.settings.last_basis_elements[j].split(",")
                    if len(previous_elements) > 0:
                        basis.setSelectedElements([x for x in previous_elements + basis.currentElements() if x not in elements_with_different_basis])

        for j, basis in enumerate(self.ecp_options):
            elements_with_different_basis = []
            for other_basis in self.ecp_options:
                if other_basis is not basis:
                    elements_with_different_basis.extend(other_basis.currentElements())
                    
            if len(del_elements) > 0:
                for i in range(basis.elements.count()-1, -1, -1):
                    if basis.elements.item(i).text() in del_elements:
                        basis.elements.takeItem(i)
            
            if len(new_elements) > 0:
                basis.elements.addItems(new_elements)
                basis.elements.sortItems()
                if j < len(self.settings.last_ecp_elements):
                    previous_elements = self.settings.last_ecp_elements[j].split(",")
                    if len(previous_elements) > 0:
                        basis.setSelectedElements([x for x in previous_elements + basis.currentElements() if x not in elements_with_different_basis])  

        if len(self.basis_options) == 1 and len(self.ecp_options) == 0:
            self.basis_options[0].setSelectedElements(self.elements)
                
        self.check_elements()
        
        self.basisChanged.emit()


class OneLayerKeyWordOption(QWidget):
    #TODO:
    #* add option to not save (who wants to save a comment? some people might, but I don't)
    optionChanged = pyqtSignal()
    settingsChanged = pyqtSignal()
    
    def __init__(self, name, last_list=[], previous_list=[], multiline=False, parent=None):
        """
        name                    - name of the left groupbox
        last_list               - list of 'last' setting corresponding to just the target position (i.e. route, blocks)
        previous_list           - list of 'previous' setting
        """
        
        self.name = name
        self.last_list = last_list
        self.previous_list = previous_list
        self.multiline = multiline
        
        super().__init__(parent)

        layout = QGridLayout(self)        

        self.previous_kw_table = QTableWidget()
        self.previous_kw_table.setColumnCount(2)
        self.previous_kw_table.setHorizontalHeaderLabels(['previous', 'trash'])
        self.previous_kw_table.cellActivated.connect(self.clicked_route_keyword)
        self.previous_kw_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.previous_kw_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.previous_kw_table.verticalHeader().setVisible(False)
        
        self.current_kw_table = QTableWidget()
        self.current_kw_table.setColumnCount(2)
        self.current_kw_table.setHorizontalHeaderLabels(['current', 'remove'])
        self.current_kw_table.setSelectionMode(QTableWidget.SingleSelection)
        self.current_kw_table.setEditTriggers(QTableWidget.DoubleClicked)
        self.current_kw_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.current_kw_table.verticalHeader().setVisible(False)
        self.current_kw_table.cellClicked.connect(self.clicked_current_route_keyword)
        self.current_kw_table.cellChanged.connect(self.edit_current_kw)

        new_kw_widget = QWidget()
        new_kw_widgets_layout = QGridLayout(new_kw_widget)
        if self.multiline:
            self.new_kw = QTextEdit()
            self.new_kw.setAcceptRichText(False)
            self.new_kw.setMaximumHeight(int(6*self.fontMetrics().boundingRect("QQ").height()))
        else:
            self.new_kw = QLineEdit()
            self.new_kw.setClearButtonEnabled(True)
            self.new_kw.returnPressed.connect(self.add_kw)
          
        self.new_kw.setPlaceholderText("filter %s%s" % (self.name[:-1], self.name[-1] + "s" if self.name[-1] != 'y' else "ies"))
        self.new_kw.textChanged.connect(self.apply_kw_filter)
        add_kw_button = QPushButton("add")
        add_kw_button.clicked.connect(self.add_kw)
        if not self.multiline:
            new_kw_widgets_layout.addWidget(QLabel("%s:" % self.name), 0, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        else:
            new_kw_widgets_layout.addWidget(QLabel("%s:" % self.name), 0, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        new_kw_widgets_layout.addWidget(self.new_kw, 0, 1)
        new_kw_widgets_layout.addWidget(add_kw_button, 0, 2, 1, 1, Qt.AlignTop)

        for kw in self.previous_list:
            self.add_item_to_previous_kw_table(kw)
                
        for kw in self.last_list:
            self.add_item_to_current_kw_table(kw)
        
        #columns of tables will get resized so that the trash/remove column has a fixed size 
        #and the keyword/option stretches
        self.previous_kw_table.resizeColumnToContents(1)
        self.previous_kw_table.horizontalHeader().setStretchLastSection(False)            
        self.previous_kw_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.previous_kw_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.current_kw_table.resizeColumnToContents(1)
        self.current_kw_table.horizontalHeader().setStretchLastSection(False)            
        self.current_kw_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.current_kw_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
    
        layout.addWidget(self.previous_kw_table, 0, 0)
        layout.addWidget(self.current_kw_table, 0, 1)
        layout.addWidget(new_kw_widget, 1, 0, 1, 2)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 0)
        layout.setContentsMargins(0, 0, 0, 0)

    def add_item_to_previous_kw_table(self, kw):
        row = self.previous_kw_table.rowCount()
        self.previous_kw_table.insertRow(row)
    
        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        trash_button = QLabel()
        dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
        trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(dim, dim))
        trash_button.setToolTip("double click to remove from stored keywords")
        widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(2, 2, 2, 2)
        self.previous_kw_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)
    
        item = QTableWidgetItem(kw)
        item.setToolTip("double click to use \"%s\"" % kw)
        self.previous_kw_table.setItem(row, 0, item)
        
        self.previous_kw_table.resizeRowToContents(row)

    def remove_previous_kw_row(self, row):
        item = self.previous_kw_table.item(row, 0)
        kw = item.text()
        self.previous_list.remove(kw)
        
        current_kw = self.current_kw_table.findItems(kw, Qt.MatchExactly)
        if len(current_kw) == 1:
            kw_item = current_kw[0]
            cur_row = kw_item.row()
            self.clicked_current_route_keyword(cur_row, 1)
        
        self.settingsChanged.emit()
        
        self.previous_kw_table.removeRow(row)
    
    def add_item_to_current_kw_table(self, kw):
        self.current_kw_table.blockSignals(True)
        
        row = self.current_kw_table.rowCount()
        self.current_kw_table.insertRow(row)

        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        trash_button = QLabel()
        dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
        trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)).pixmap(dim, dim))
        trash_button.setToolTip("click to not use this %s" % self.name)
        widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(2, 2, 2, 2)
        self.current_kw_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)

        item = QTableWidgetItem(kw)
        if self.multiline:
            item.setToolTip("double click to edit\n'\\n' will be replaced with newline")
        else:
            item.setToolTip("double click to edit")
        
        self.current_kw_table.setItem(row, 0, item)
        
        self.current_kw_table.resizeRowToContents(row)

        self.optionChanged.emit()
        
        self.current_kw_table.blockSignals(False)

    def add_kw(self):
        if self.multiline:
            kw = self.new_kw.toPlainText()
        else:
            kw = self.new_kw.text()

        if len(kw.strip()) == 0:
            return

        if kw not in self.last_list:
            self.last_list.append(kw)
        
            self.add_item_to_current_kw_table(kw)

    def clicked_route_keyword(self, row, column):
        if column == 1:
            self.remove_previous_kw_row(row)
        elif column == 0:
            item = self.previous_kw_table.item(row, column)

            keyword = item.text()
            if keyword in self.last_list:
                return
            
            self.last_list.append(keyword)
            
            self.add_item_to_current_kw_table(keyword)

    def clicked_current_route_keyword(self, row, column):
        if column == 1:
            item = self.current_kw_table.item(row, 0)
            kw = item.text()
            self.last_list.remove(kw)

            self.current_kw_table.removeRow(row)

            self.optionChanged.emit()
 
    def edit_current_kw(self, row, column):
        if column == 0:
            if self.multiline:
                self.last_list[row] = self.current_kw_table.item(row, column).text().replace('\\n', '\n')
                self.current_kw_table.blockSignals(True)
                self.current_kw_table.item(row, column).setText(self.last_list[row])
                self.current_kw_table.resizeRowToContents(row)
                self.current_kw_table.blockSignals(False)
            else:
                self.last_list[row] = self.current_kw_table.item(row, column).text()
            
            self.optionChanged.emit()

    def refresh_previous(self):
        for item in self.last_list:
            if item not in self.previous_list:
                self.previous_list.append(item)
    
    def apply_kw_filter(self, text=None):
        if text is None:
            #QTextEdit's textChanged doesn't give you the text
            text = self.new_kw.toPlainText()
        
        if text:
            #the user doesn't need capturing groups
            text = text.replace('(', '\(')
            text = text.replace(')', '\)')
            m = QRegularExpression(text)
            if m.isValid():
                m.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
                
                m.optimize()
                filter = lambda row_num: m.match(self.previous_kw_table.item(row_num, 0).text()).hasMatch()
            else:
                return
        
        else:
            filter = lambda row: True
            
        for i in range(0, self.previous_kw_table.rowCount()):
            self.previous_kw_table.setRowHidden(i, not filter(i))        
        
        self.previous_kw_table.resizeColumnToContents(0)    
    
    def setCurrentSettings(self, kw_list):
        self.clearCurrentSettings()

        self.last_list = kw_list.copy()        
        
        for kw in self.last_list:
            self.add_item_to_current_kw_table(kw)

    def clearCurrentSettings(self):
        self.last_list = []

        for i in range(self.current_kw_table.rowCount(), -1, -1):
            self.current_kw_table.removeRow(i)


class TwoLayerKeyWordOption(QWidget):
    optionChanged = pyqtSignal()
    settingsChanged = pyqtSignal()
    
    def __init__(self, name, last_dict, previous_dict, opt_fmt, \
                 one_opt_per_kw=False, parent=None):
        """
        name                    - name of the left groupbox
        last_dict               - dict of 'last' setting corresponding to just the target position (i.e. route, blocks)
        previous_dict           - dict of 'previous' setting
        one_opt_per_kw          - bool; multiple options per keyword like in Gaussian route
                                    or just one like Psi4 settings
        opt_fmt                 - str; format when displaying options for selected keyword
        """
        
        self.name = name
        self.last_dict = last_dict
        self.previous_dict = previous_dict
        self.one_opt_per_kw = one_opt_per_kw
        self.opt_fmt = opt_fmt
        
        super().__init__(parent)

        layout = QGridLayout(self)        
        
        self.keyword_groupbox = QGroupBox(self.name)
        self.keyword_layout = QGridLayout(self.keyword_groupbox)
        
        self.previous_kw_table = QTableWidget()
        self.previous_kw_table.setColumnCount(2)
        self.previous_kw_table.setHorizontalHeaderLabels(['previous', 'trash'])
        self.previous_kw_table.cellActivated.connect(self.clicked_route_keyword)
        self.previous_kw_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.previous_kw_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.previous_kw_table.verticalHeader().setVisible(False)
        self.keyword_layout.addWidget(self.previous_kw_table, 0, 0)
        
        self.current_kw_table = QTableWidget()
        self.current_kw_table.setColumnCount(2)
        self.current_kw_table.setHorizontalHeaderLabels(['current', 'remove'])
        self.current_kw_table.setSelectionMode(QTableWidget.SingleSelection)
        self.current_kw_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.current_kw_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.current_kw_table.verticalHeader().setVisible(False)
        self.current_kw_table.cellClicked.connect(self.clicked_current_route_keyword)
        self.keyword_layout.addWidget(self.current_kw_table, 0, 1)

        new_kw_widget = QWidget()
        new_kw_widgets_layout = QGridLayout(new_kw_widget)
        self.new_kw = QLineEdit()
        self.new_kw.setPlaceholderText("filter %s" % self.name)
        self.new_kw.textChanged.connect(self.apply_kw_filter)
        self.new_kw.returnPressed.connect(self.add_kw)
        self.new_kw.setClearButtonEnabled(True)
        add_kw_button = QPushButton("add")
        add_kw_button.clicked.connect(self.add_kw)
        if self.name.endswith('s'):
            new_kw_widgets_layout.addWidget(QLabel("%s:" % self.name[:-1]), 0, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        else:
            new_kw_widgets_layout.addWidget(QLabel("%s:" % self.name), 0, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        new_kw_widgets_layout.addWidget(self.new_kw, 0, 1)
        new_kw_widgets_layout.addWidget(add_kw_button, 0, 2)
        self.keyword_layout.addWidget(new_kw_widget, 1, 0, 1, 2)
        

        self.option_groupbox = QGroupBox("options")
        option_layout = QGridLayout(self.option_groupbox)
        
        self.previous_opt_table = QTableWidget()
        self.previous_opt_table.setColumnCount(2)
        self.previous_opt_table.setHorizontalHeaderLabels(['previous', 'trash'])
        self.previous_opt_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.previous_opt_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.previous_opt_table.verticalHeader().setVisible(False)
        self.previous_opt_table.cellActivated.connect(self.clicked_keyword_option)
        option_layout.addWidget(self.previous_opt_table, 0, 0)
        
        self.current_opt_table = QTableWidget()
        self.current_opt_table.setColumnCount(2)
        self.current_opt_table.setHorizontalHeaderLabels(['current', 'remove'])
        self.current_opt_table.setEditTriggers(QTableWidget.DoubleClicked)
        self.current_opt_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.current_opt_table.cellClicked.connect(self.clicked_current_keyword_option)
        self.current_opt_table.cellChanged.connect(self.edit_current_opt)
        self.current_opt_table.verticalHeader().setVisible(False)
        option_layout.addWidget(self.current_opt_table, 0, 1)

        new_opt_widget = QWidget()
        new_opt_widgets_layout = QGridLayout(new_opt_widget)
        self.new_opt = QLineEdit()
        self.new_opt.setPlaceholderText("filter options")
        self.new_opt.textChanged.connect(self.apply_opt_filter)
        self.new_opt.returnPressed.connect(self.add_opt)
        self.new_opt.setClearButtonEnabled(True)
        add_opt_button = QPushButton("add")
        add_opt_button.clicked.connect(self.add_opt)
        new_opt_widgets_layout.addWidget(QLabel("option:"), 0, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        new_opt_widgets_layout.addWidget(self.new_opt, 0, 1)
        new_opt_widgets_layout.addWidget(add_opt_button, 0, 2)
        option_layout.addWidget(new_opt_widget, 1, 0, 1, 2)

        self.current_kw_table.itemSelectionChanged.connect(self.update_route_opts)

        self.selected_kw = None
        for kw in self.previous_dict:
            self.add_item_to_previous_kw_table(kw)
            self.selected_kw = kw
                
        for kw in self.last_dict:
            self.add_item_to_current_kw_table(kw)
        
        #columns of tables will get resized so that the trash/remove column has a fixed size 
        #and the keyword/option stretches
        self.previous_kw_table.resizeColumnToContents(1)
        self.previous_kw_table.horizontalHeader().setStretchLastSection(False)            
        self.previous_kw_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.previous_kw_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.current_kw_table.resizeColumnToContents(1)
        self.current_kw_table.horizontalHeader().setStretchLastSection(False)            
        self.current_kw_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.current_kw_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.previous_opt_table.resizeColumnToContents(1)
        self.previous_opt_table.horizontalHeader().setStretchLastSection(False)            
        self.previous_opt_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.previous_opt_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.current_opt_table.resizeColumnToContents(1)
        self.current_opt_table.horizontalHeader().setStretchLastSection(False)            
        self.current_opt_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.current_opt_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
    
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(True)
        splitter.addWidget(self.keyword_groupbox)
        splitter.addWidget(self.option_groupbox)
        layout.addWidget(splitter, 0, 0, 1, 1, Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

    def add_item_to_previous_kw_table(self, kw):
        row = self.previous_kw_table.rowCount()
        self.previous_kw_table.insertRow(row)
        item = QTableWidgetItem(kw)
        item.setToolTip("double click to use %s" % kw)
        self.previous_kw_table.setItem(row, 0, item)
    
        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        trash_button = QLabel()
        dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
        trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(dim, dim))
        trash_button.setToolTip("double click to remove from stored keywords")
        widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(2, 2, 2, 2)
        self.previous_kw_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)
    
        self.previous_kw_table.resizeRowToContents(row)

    def remove_previous_kw_row(self, row):
        item = self.previous_kw_table.item(row, 0)
        kw = item.text()
        del self.previous_dict[kw]
        
        current_kw = self.current_kw_table.findItems(kw, Qt.MatchExactly)
        if len(current_kw) == 1:
            kw_item = current_kw[0]
            cur_row = kw_item.row()
            self.clicked_current_route_keyword(cur_row, 1)
        
        self.settingsChanged.emit()
        
        self.previous_kw_table.removeRow(row)
    
    def add_item_to_current_kw_table(self, kw):
        row = self.current_kw_table.rowCount()
        self.current_kw_table.insertRow(row)
        item = QTableWidgetItem(kw)
        self.current_kw_table.setItem(row, 0, item)
    
        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        trash_button = QLabel()
        dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
        trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)).pixmap(dim, dim))
        trash_button.setToolTip("click to not use this %s" % self.name[:-1])
        widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(2, 2, 2, 2)
        self.current_kw_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)
    
        self.current_kw_table.resizeRowToContents(row)
        self.current_kw_table.resizeColumnToContents(0)
        self.current_kw_table.resizeColumnToContents(1)
        
        self.current_kw_table.selectRow(row)

        self.optionChanged.emit()

    def add_item_to_previous_opt_table(self, opt):
        row = self.previous_opt_table.rowCount()
        self.previous_opt_table.insertRow(row)
        item = QTableWidgetItem(opt)
        item.setToolTip(self.opt_fmt % (self.selected_kw, opt))
        self.previous_opt_table.setItem(row, 0, item)
        
        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        trash_button = QLabel()
        dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
        trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(dim, dim))
        trash_button.setToolTip("double click to remove from stored options")
        widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(2, 2, 2, 2)
        self.previous_opt_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)
    
        self.previous_opt_table.resizeRowToContents(row)
    
    def remove_previous_opt_row(self, row):
        item = self.previous_opt_table.item(row, 0)
        opt = item.text()
        self.previous_dict[self.selected_kw].remove(opt)
        
        current_opt = self.current_opt_table.findItems(opt, Qt.MatchExactly)
        if len(current_opt) == 1:
            opt_item = current_opt[0]
            cur_row = opt_item.row()
            self.clicked_current_keyword_option(cur_row, 1)
        
        self.settingsChanged.emit()

        self.previous_opt_table.removeRow(row)

    def add_item_to_current_opt_table(self, opt):
        #prevent edit signal from triggering
        #it should break anything, but we don't need it
        self.current_opt_table.blockSignals(True)
        if opt not in self.last_dict[self.selected_kw]:
            if self.one_opt_per_kw:
                self.last_dict[self.selected_kw] = [opt]
                for i in range(self.current_opt_table.rowCount(), -1, -1):
                    self.current_opt_table.removeRow(i)
            
            else:
                self.last_dict[self.selected_kw].append(opt)
        
            self.optionChanged.emit()

        row = self.current_opt_table.rowCount()
        self.current_opt_table.insertRow(row)
        item = QTableWidgetItem(opt)
        item.setToolTip("double click to edit")
        self.current_opt_table.setItem(row, 0, item)
        
        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        trash_button = QLabel()
        dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
        trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)).pixmap(dim, dim))
        trash_button.setToolTip("click to not use this option")
        widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(2, 2, 2, 2)
        self.current_opt_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)
    
        self.current_opt_table.resizeRowToContents(row)
        self.current_opt_table.resizeColumnToContents(0)
        self.current_opt_table.resizeColumnToContents(1)
        
        self.current_opt_table.blockSignals(False)

    def add_kw(self):
        kw = self.new_kw.text()
        if len(kw.strip()) == 0:
            return
        
        if kw not in self.last_dict:
            self.last_dict[kw] = []
        
            self.add_item_to_current_kw_table(kw)

    def add_opt(self):
        opt = self.new_opt.text()
        if len(opt.strip()) == 0:
            return

        kw = self.selected_kw
        if kw is None:
            raise RuntimeWarning("no keyword selected")
            return

        if opt not in self.last_dict[kw]:
            self.add_item_to_current_opt_table(opt)

    def update_route_opts(self):
        for i in range(self.previous_opt_table.rowCount(), -1, -1):
            self.previous_opt_table.removeRow(i)    
            
        for i in range(self.current_opt_table.rowCount(), -1, -1):
            self.current_opt_table.removeRow(i)
        
        selected_items = self.current_kw_table.selectedItems()
        if len(selected_items) != 1:
            self.option_groupbox.setTitle("options")
            self.selected_kw = None
            return
        
        keyword = selected_items[0].text()              
        self.selected_kw = keyword
        
        self.option_groupbox.setTitle("'%s' options" % keyword)

        if keyword in self.previous_dict:
            for opt in self.previous_dict[keyword]:
                self.add_item_to_previous_opt_table(opt)
            
        if keyword in self.last_dict:
            for opt in self.last_dict[keyword]:
                self.add_item_to_current_opt_table(opt)
        
        self.previous_opt_table.resizeColumnToContents(0)
        self.previous_opt_table.resizeColumnToContents(1)
        self.current_opt_table.resizeColumnToContents(0)
        self.current_opt_table.resizeColumnToContents(1)

    def clicked_route_keyword(self, row, column):
        if column == 1:
            self.remove_previous_kw_row(row)
        elif column == 0:
            item = self.previous_kw_table.item(row, column)

            keyword = item.text()
            if any(keyword == kw for kw in self.last_dict.keys()):
                return
            
            else:
                self.last_dict[keyword] = []
                self.add_item_to_current_kw_table(keyword)

    def clicked_current_route_keyword(self, row, column):
        if column == 1:
            item = self.current_kw_table.item(row, 0)
            kw = item.text()
            del self.last_dict[kw]

            self.current_kw_table.removeRow(row)
            
            if kw == self.selected_kw:
                self.update_route_opts()
                
            self.optionChanged.emit()

    def clicked_keyword_option(self, row, column):
        if column == 1:
            self.remove_previous_opt_row(row)
        elif column == 0:
            item = self.previous_opt_table.item(row, column)
            option = item.text()

            keyword = self.selected_kw
            
            if option in self.last_dict[keyword]:
                return

            self.add_item_to_current_opt_table(option)
  
    def clicked_current_keyword_option(self, row, column):
        if column == 1:
            item = self.current_opt_table.item(row, 0)
            opt = item.text()
            self.last_dict[self.selected_kw].remove(opt)
                        
            self.current_opt_table.removeRow(row)
            
            self.optionChanged.emit()
    
    def edit_current_opt(self, row, column):
        if column == 0:
            self.last_dict[self.selected_kw][row] = self.current_opt_table.item(row, column).text()
            self.optionChanged.emit()

    def refresh_previous(self):
        for item in self.last_dict.keys():
            if item not in self.previous_dict:
                self.previous_dict[item] = []
                
            for opt in self.last_dict[item]:
                if opt not in self.previous_dict[item]:
                    self.previous_dict[item].append(opt)
    
    def apply_kw_filter(self, text):
        #text = self.custom_basis_kw.text()
        if text:
            #the user doesn't need capturing groups
            text = text.replace('(', '\(')
            text = text.replace(')', '\)')
            m = QRegularExpression(text)
            if m.isValid():
                m.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
                
                m.optimize()
                filter = lambda row_num: m.match(self.previous_kw_table.item(row_num, 0).text()).hasMatch()
            else:
                return
        
        else:
            filter = lambda row: True
            
        for i in range(0, self.previous_kw_table.rowCount()):
            self.previous_kw_table.setRowHidden(i, not filter(i))        
        
        self.previous_kw_table.resizeColumnToContents(0)    
    
    def apply_opt_filter(self, text):
        #text = self.custom_basis_kw.text()
        if text:
            #the user doesn't need capturing groups
            text = text.replace('(', '\(')
            text = text.replace(')', '\)')
            m = QRegularExpression(text)
            if m.isValid():
                m.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
                
                m.optimize()
                filter = lambda row_num: m.match(self.previous_opt_table.item(row_num, 0).text()).hasMatch()
            else:
                return
        
        else:
            filter = lambda row: True
            
        for i in range(0, self.previous_opt_table.rowCount()):
            self.previous_opt_table.setRowHidden(i, not filter(i))        
        
        self.previous_opt_table.resizeColumnToContents(0)
    
    def setCurrentSettings(self, kw_dict):
        self.clearCurrentSettings()

        self.last_dict = kw_dict.copy()

        for kw in self.last_dict:
            self.add_item_to_current_kw_table(kw)

    def clearCurrentSettings(self):
        self.last_dict = {}
        for i in range(self.current_opt_table.rowCount(), -1, -1):
            self.current_opt_table.removeRow(i)
            
        for i in range(self.current_kw_table.rowCount(), -1, -1):
            self.current_kw_table.removeRow(i)


class KeywordOptions(QWidget):
    """
    items is a dict that can include
        route       - enables widget to display route options a la Gaussian or ORCA 
        comment     - comment 
        link 0      - enables Gaussian's Link 0 commands
        settings    - enables setting specifications a la Psi4
        blocks      - enables settings like ORCA's namespace-style options
        end of file - some programs throw stuff at the end of the file
        
        the values should be the int map to specify the location in the input file
        
    previous_option_name        name of the'previous' setting
    last_option_name            name of the 'last' setting
    one_route_opt_per_kw        bool; whether the route accepts multiple settings for keywords (who does this?)
    route_opt_fmt               str; % style formating to convert two strings (e.g. %s=(%s))
    comment_opt_fmt             str; % style formating to convert two strings (e.g. %s=(%s))
    """
    optionsChanged = pyqtSignal()
    settingsChanged = pyqtSignal()
    
    items = {}
    previous_option_name = None
    last_option_name = None
    one_route_opt_per_kw = False
    one_link0_opt_per_kw = False
    route_opt_fmt = "%s %s"
    comment_opt_fmt = "%s %s"

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        
        self.previous_dict = {}
        previous_dict = loads(self.settings.__getattr__(self.previous_option_name))
        for key in previous_dict.keys():
            self.previous_dict[int(key)] = previous_dict[key]
        
        self.last_dict = {}
        last_dict = loads(self.settings.__getattr__(self.last_option_name))
        for key in last_dict.keys():
            self.last_dict[int(key)] = last_dict[key]
                    
        self.layout = QGridLayout(self)
        
        position_widget = QWidget()
        position_widget_layout = QFormLayout(position_widget)
        position_selector = QComboBox()
        position_selector.addItems([x for x in self.items.keys()])
        position_widget_layout.addRow("position:", position_selector)
        
        self.layout.addWidget(position_widget, 0, 0, 1, 1, Qt.AlignTop)
        
        self.widgets = {}
        for item in self.items.keys():
            if self.items[item] not in self.last_dict:
                last = None
            else:
                last = self.last_dict[self.items[item]]
            
            if self.items[item] not in self.previous_dict:
                previous = None
            else:
                previous = self.previous_dict[self.items[item]]
            
            self.widgets[item] = self.get_options_for(item, last, previous)
            self.widgets[item].optionChanged.connect(self.something_changed)
            self.widgets[item].settingsChanged.connect(self.settings_changed)
            self.layout.addWidget(self.widgets[item], 1, 0, Qt.AlignTop)

        position_selector.currentTextChanged.connect(self.change_widget)            
        self.change_widget(position_selector.currentText())

        self.layout.setContentsMargins(0, 0, 0, 0)        
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)
    
    def setKeywords(self, current_dict):
        for item in self.widgets.keys():
            if self.items[item] in current_dict:
                self.widgets[item].setCurrentSettings(current_dict[self.items[item]])
                
            else:
                self.widgets[item].clearCurrentSettings()
    
    def something_changed(self, *args, **kw):
        """just for updating the preview"""
        self.optionsChanged.emit()

    def settings_changed(self, *args, **kw):
        """update settings"""
        last_dict = {}
        previous_dict = {}
        for item in self.widgets.keys():
            self.widgets[item].refresh_previous()
            if isinstance(self.widgets[item], TwoLayerKeyWordOption):
                last_dict[self.items[item]] = self.widgets[item].last_dict
                previous_dict[self.items[item]] = self.widgets[item].previous_dict
            
            elif isinstance(self.widgets[item], OneLayerKeyWordOption):
                last_dict[self.items[item]] = self.widgets[item].last_list
                previous_dict[self.items[item]] = self.widgets[item].previous_list
                
        self.settings.__setattr__(self.last_option_name, dumps(last_dict))
        self.settings.__setattr__(self.previous_option_name, dumps(previous_dict))
        self.settings.save()

    def change_widget(self, name):
        for widget_name in self.widgets.keys():
            if name != widget_name:
                self.widgets[widget_name].setVisible(False)
                
            else:
                self.widgets[widget_name].setVisible(True)

    def getKWDict(self, update_settings=True):
        last_dict = {}
        for item in self.widgets.keys():
            if isinstance(self.widgets[item], TwoLayerKeyWordOption):
                last_dict[self.items[item]] = self.widgets[item].last_dict
                if update_settings:
                    for kw in self.widgets[item].last_dict:
                        if kw not in self.widgets[item].previous_dict:
                            self.widgets[item].previous_dict[kw] = [x for x in self.widgets[item].last_dict[kw]]
                            self.widgets[item].add_item_to_previous_kw_table(kw)
                            
                            if self.widgets[item].selected_kw == kw:
                                for opt in self.widgets[item].previous_dict[kw]:
                                    self.widgets[item].add_item_to_previous_opt_table(opt)

                        else:
                            for opt in self.widgets[item].last_dict[kw]:
                                if opt not in self.widgets[item].previous_dict[kw]:
                                    self.widgets[item].previous_dict[kw].append(opt)
                                    
                                    if self.widgets[item].selected_kw == kw:
                                        self.widgets[item].add_item_to_previous_opt_table(opt)
            
            elif isinstance(self.widgets[item], OneLayerKeyWordOption):
                last_dict[self.items[item]] = self.widgets[item].last_list
                if update_settings:
                    for kw in self.widgets[item].last_list:
                        if kw not in self.widgets[item].previous_list:
                            self.widgets[item].previous_list.append(kw)
                            self.widgets[item].add_item_to_previous_kw_table(kw)

        if update_settings:
            self.settings_changed()
        
        return last_dict
    
    @classmethod
    def get_options_for(cls, item):
        """returns a OneLayerKeyWordOption or TwoLayerKeyWordOption instance that is 
        appropriate for item
        should be overridden by subclasses"""
        pass


class GaussianKeywordOptions(KeywordOptions):
    items = {'link 0': Method.GAUSSIAN_PRE_ROUTE, \
             'comment': Method.GAUSSIAN_COMMENT, \
             'route': Method.GAUSSIAN_ROUTE, \
             'end of file': Method.GAUSSIAN_POST, \
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
                
            return TwoLayerKeyWordOption("keywords", last_dict, previous_dict, "double click to add %s=(%s)", one_opt_per_kw=False)
            
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
            
        elif name == "end of file":
            if last is None:
                last_list = []
            else:
                last_list = last            
                
            if previous is None:
                previous_list = []
            else:
                previous_list = previous
                
            return OneLayerKeyWordOption("end of file", last_list, previous_list, multiline=True)

        elif name == "link 0":
            if last is None:
                last_dict = {}
            else:
                last_dict = last            
                
            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous
                
            return TwoLayerKeyWordOption("link 0", last_dict, previous_dict, "double click to use %%%s=%s", one_opt_per_kw=False)
    

class ORCAKeywordOptions(KeywordOptions):
    items = {'simple keywords': Method.ORCA_ROUTE, \
             'comment': Method.ORCA_COMMENT, \
             'blocks': Method.ORCA_BLOCKS, \
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
    items = {'settings': Method.PSI4_SETTINGS, \
             'before geometry': Method.PSI4_BEFORE_GEOM, \
             'after job': Method.PSI4_AFTER_GEOM, \
             'comment': Method.PSI4_COMMENT, \
             'molecule': Method.PSI4_COORDINATES, \
            }

    previous_option_name = "previous_psi4_options"
    last_option_name = "last_psi4_options"

    @classmethod
    def get_options_for(cls, name, last, previous):
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
            
        elif name == "before geometry":
            if last is None:
                last_list = []
            else:
                last_list = last            
                
            if previous is None:
                previous_list = []
            else:
                previous_list = previous
                
            return OneLayerKeyWordOption("before geometry", last_list, previous_list, multiline=True)
            
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
                
            return TwoLayerKeyWordOption("settings", last_dict, previous_dict, "double click to use \"set { %s %s }\"", one_opt_per_kw=True)

        elif name == "molecule":
            if last is None:
                last_dict = {}
            else:
                last_dict = last
            
            if previous is None:
                previous_dict = {}
            else:
                previous_dict = previous
            
            return TwoLayerKeyWordOption("molecule", last_dict, previous_dict, "double click to use \"%s %s\"", one_opt_per_kw=True)


class KeywordWidget(QWidget):
    additionalOptionsChanged = pyqtSignal()

    def __init__(self, settings, init_form, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.form = init_form
        
        self.layout = QGridLayout(self)
        
        self.gaussian_widget = GaussianKeywordOptions(self.settings)
        self.gaussian_widget.optionsChanged.connect(self.options_changed)
        self.layout.addWidget(self.gaussian_widget, 0, 0)
        
        self.orca_widget = ORCAKeywordOptions(self.settings)
        self.orca_widget.optionsChanged.connect(self.options_changed)
        self.layout.addWidget(self.orca_widget, 0, 0)

        self.psi4_widget = Psi4KeywordOptions(self.settings)
        self.psi4_widget.optionsChanged.connect(self.options_changed)
        self.layout.addWidget(self.psi4_widget, 0, 0)

        self.setOptions(init_form)
    
    def setOptions(self, program):
        self.form = program
        if program == "Gaussian":
            self.gaussian_widget.setVisible(True)
            self.orca_widget.setVisible(False)
            self.psi4_widget.setVisible(False)
        
        elif program == "ORCA":
            self.gaussian_widget.setVisible(False)
            self.orca_widget.setVisible(True)
            self.psi4_widget.setVisible(False)
        
        elif program == "Psi4":
            self.gaussian_widget.setVisible(False)
            self.orca_widget.setVisible(False)
            self.psi4_widget.setVisible(True)

    def options_changed(self):
        self.additionalOptionsChanged.emit()

    def setKeywords(self, current_dict):
        if self.form == "Gaussian":
            self.gaussian_widget.setKeywords(current_dict)
        
        elif self.form == "ORCA":
            self.orca_widget.setKeywords(current_dict)        
        
        elif self.form == "Psi4":
            self.psi4_widget.setKeywords(current_dict)
    
    def getKWDict(self, update_settings=True):
        if self.form == "Gaussian":
            last_dict = self.gaussian_widget.getKWDict(update_settings)

            if update_settings:
                self.gaussian_widget.settings_changed()

            return last_dict        
        
        elif self.form == "ORCA":
            last_dict = self.orca_widget.getKWDict(update_settings)

            if update_settings:
                self.orca_widget.settings_changed()

            return last_dict        
        
        elif self.form == "Psi4":
            last_dict = self.psi4_widget.getKWDict(update_settings)

            if update_settings:
                self.psi4_widget.settings_changed()

            return last_dict

 
class InputPreview(ChildToolWindow):
    def __init__(self, tool_instance, title, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)
        
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()
        
        self.preview = QTextBrowser()
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.preview.setFont(font)
        layout.addWidget(self.preview, 0, 0, 1, 2)
        
        #chimera toolwindows can have a statusbar, but the message goes away after a few seconds
        #I'll just use a Qt statusbar        
        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        self.status.setStyleSheet("color: red")
        layout.addWidget(self.status, 1, 1, 1, 1)
        
        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon(refresh_button.style().standardIcon(QStyle.SP_BrowserReload)))
        refresh_button.clicked.connect(self.tool_instance.update_preview)
        layout.addWidget(refresh_button, 1, 0, 1, 1, Qt.AlignLeft)
        
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 0)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        
        self.ui_area.setLayout(layout)
        
        self.manage(None)

    def setPreview(self, text, warnings_list):
        self.preview.setText(text)
        if len(warnings_list) > 0:
            self.status.setVisible(True)
            self.status.showMessage("; ".join(warnings_list))
        else:
            self.status.setVisible(False)

    def cleanup(self):
        self.tool_instance.preview_window = None
        
        super().cleanup()


class SavePreset(ChildToolWindow):
    class BasisElements(QWidget):
        """widget to select what elements belong in which basis"""
        def __init__(self, parent=None, tool_instance=None):
            super().__init__(parent)
            self.tool_instance = tool_instance

            self.basis_form = QFormLayout(self)
            
            self.basis_elements = []
            self.ecp_elements = []
            
            self.basis_form.setContentsMargins(0, 0, 0, 0)

        def refresh_basis(self):
            basis_set = self.tool_instance.basis_widget.getBasis(update_settings=False)
            self.setBasis(basis_set)
            
        def setBasis(self, basis_set):
            """display current basis sets and element selectors"""
            self.basis_elements = []
            self.ecp_elements = []
            for i in range(self.basis_form.rowCount()-1, -1, -1):
                self.basis_form.removeRow(i)
            
            if basis_set.basis is not None:
                for basis in basis_set.basis:
                    element_selector = QComboBox()
                    self.basis_elements.append(element_selector)
                    element_selector.addItems(["current elements", "all elements", "transition metals", "non-transition metals"])
                    basis_name = basis.name
                    aux = basis.aux_type
                    if aux is not None:
                        label = "    %s/%s" % (basis_name, aux)
                    else:
                        label = "    %s" % basis_name

                    #if there's only one basis, it should only be used for all elements
                    if len(basis_set.basis) == 1 and (basis_set.ecp is None or len(basis_set.ecp) == 0):
                        element_selector.setCurrentIndex(1)
                        element_selector.setEnabled(False)

                    self.basis_form.addRow(label, element_selector)

            if basis_set.ecp is not None:
                for ecp in basis_set.ecp:
                    element_selector = QComboBox()
                    self.ecp_elements.append(element_selector)
                    element_selector.addItems(["current elements", "all elements", "transition metals", "non-transition metals"])
                    basis_name = ecp.name
                    aux = basis.aux_type
                    label = "    %s" % basis_name

                    self.basis_form.addRow(label, element_selector)

        def getElements(self):
            basis = []
            ecp = []
            for selector in self.basis_elements:
                elements = selector.currentText()
                if elements == "current elements":
                    basis.append("current")
                
                elif elements == "all elements":
                    basis.append("all")
                
                elif elements == "transition metals":
                    basis.append("tm")
                    
                elif elements == "non-transition metals":
                    basis.append("!tm")
            
            for selector in self.ecp_elements:
                elements = selector.currentText()
                if elements == "current elements":
                    ecp.append("current")
                
                elif elements == "all elements":
                    ecp.append("all")
                
                elif elements == "transition metals":
                    ecp.append("tm")
                    
                elif elements == "non-transition metals":
                    ecp.append("!tm")
                    
            return basis, ecp


    def __init__(self, tool_instance, title, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)
        
        self._build_ui()

    def _build_ui(self):
        
        layout = QFormLayout()
        
        layout.addRow(QLabel("select what to save in the preset and enter a name"))
        
        self.job_type = QCheckBox()
        self.job_type.setChecked(True)
        self.job_type.setToolTip("geometry optimization and frequency calculation settings")
        layout.addRow("job type:", self.job_type)
        
        self.job_resources = QCheckBox()
        self.job_resources.setChecked(True)
        self.job_resources.setToolTip("processors and memory")
        layout.addRow("job resources:", self.job_resources)
        
        self.solvent = QCheckBox()
        self.solvent.setChecked(True)
        self.solvent.setToolTip("implicit solvent")
        layout.addRow("solvent:", self.solvent)
        
        self.functional = QCheckBox()
        self.functional.setChecked(True)
        self.functional.setToolTip("functional")
        layout.addRow("functional:", self.functional)
        
        
        self.basis = QCheckBox()
        self.basis.setChecked(True)
        self.basis.setToolTip("basis functions and ECP")
        layout.addRow("basis set:", self.basis)
        
        self.basis_elements = self.BasisElements(tool_instance=self.tool_instance)
        self.tool_instance.basis_widget.basisChanged.connect(self.basis_elements.refresh_basis)
        self.basis_elements.refresh_basis()
        layout.addRow(self.basis_elements)

        self.basis.stateChanged.connect(lambda state, widget=self.basis_elements: widget.setEnabled(state == Qt.Checked))

        self.additional = QCheckBox()
        self.additional.setChecked(True)
        self.additional.setToolTip("options, keywords, etc. on the 'additional options' tab")
        layout.addRow("additional options:", self.additional)

        self.preset_name = QLineEdit()
        self.preset_name.setPlaceholderText("preset name")
        self.preset_name.returnPressed.connect(self.add_preset)
        
        layout.addRow("name:", self.preset_name)
        
        add_preset_button = QPushButton("add")
        add_preset_button.clicked.connect(self.add_preset)
        layout.addRow(add_preset_button)
        
        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        layout.addRow(self.status)
        
        self.ui_area.setLayout(layout)
        self.manage(None)

    def add_preset(self):
        preset = {}
        program = self.tool_instance.file_type.currentText()

        name = self.preset_name.text()
        if len(name.strip()) == 0:
            raise RuntimeError("no preset name")
            return
            
        elif name in self.tool_instance.presets[program]:
            yes = QMessageBox.question(self.preset_name, "\"%s\" is already saved" % name, \
                                        "would you like to overwrite \"%s\"?" % name, \
                                        QMessageBox.Yes | QMessageBox.No)
                                                
            if yes != QMessageBox.Yes:
                return
        
        if self.job_type.checkState() == Qt.Checked:
            geom_opt = self.tool_instance.job_widget.getGeometryOptimization()
            preset['opt'] = geom_opt
            
            ts_opt = self.tool_instance.job_widget.getTSOptimization()
            preset['ts'] = ts_opt
            
            freq = self.tool_instance.job_widget.getFrequencyCalculation()
            preset['freq'] = freq            
            
            num_freq = self.tool_instance.job_widget.num_freq.checkState() == Qt.Checked
            preset['num_freq'] = num_freq
            
            raman = self.tool_instance.job_widget.raman.checkState() == Qt.Checked
            preset['raman'] = raman
            
            temp = self.tool_instance.job_widget.temp.value()
            preset['temp'] = temp
        
        if self.job_resources.checkState() == Qt.Checked:
            nproc = self.tool_instance.job_widget.getNProc()
            if nproc is None:
                nproc = 0
            preset['nproc'] = nproc
            
            mem = self.tool_instance.job_widget.getMem()
            if mem is None:
                mem = 0
            preset['mem'] = mem
        
        if self.solvent.checkState() == Qt.Checked:
            solvent = self.tool_instance.job_widget.getSolvent()
            preset['solvent model'] = solvent.name
            preset['solvent'] = solvent.solvent
        
        if self.functional.checkState() == Qt.Checked:
            functional = self.tool_instance.functional_widget.getFunctional(update_settings=False)
            preset['functional'] = functional.name
            preset['semi-empirical'] = functional.is_semiempirical
            
            dispersion = self.tool_instance.functional_widget.getDispersion(update_settings=False)
            if dispersion is not None:
                preset['disp'] = dispersion.name
            else:
                preset['disp'] = dispersion
            
            grid = self.tool_instance.functional_widget.getGrid(update_settings=False)
            if grid is not None:
                preset['grid'] = grid.name
            else:
                preset['grid'] = grid
        
        if self.basis.checkState() == Qt.Checked:
            basis_elements, ecp_elements = self.basis_elements.getElements()
            
            basis_set = self.tool_instance.basis_widget.getBasis(update_settings=False)
            preset['basis'] = {'name':[], 'file':[], 'auxiliary':[], 'elements':[]}
            for basis, elements in zip(basis_set.basis, basis_elements):
                preset['basis']['name'].append(basis.name)
                preset['basis']['file'].append(basis.user_defined)
                preset['basis']['auxiliary'].append(basis.aux_type)
                if elements == "current":
                    preset['basis']['elements'].append(basis.elements)
                else:
                    preset['basis']['elements'].append([elements])
                        
            preset['ecp'] = {'name':[], 'file':[], 'elements':[]}
            if basis_set.ecp is not None:
                for basis, elements in zip(basis_set.ecp, ecp_elements):
                    preset['ecp']['name'].append(basis.name)
                    preset['ecp']['file'].append(basis.user_defined)
                    if elements == "current":
                        preset['ecp']['elements'].append(basis.elements)
                    else:
                        preset['ecp']['elements'].append([elements])
        
        if self.additional.checkState() == Qt.Checked:
            preset["other"] = self.tool_instance.other_keywords_widget.getKWDict(update_settings=False)
        
        self.tool_instance.presets[program][name] = preset

        self.tool_instance.refresh_presets()
        if self.tool_instance.remove_preset_window is not None:
            self.tool_instance.remove_preset_window.fill_tree()
        
        if self.tool_instance.export_preset_window is not None:
            self.tool_instance.export_preset_window.fill_tree()

        
        self.status.showMessage("saved \"%s\"" % name)
        
        #sometimes this causes an error
        #I haven't seen any pattern
        #self.destroy()

    def cleanup(self):
        self.tool_instance.preset_window = None
        
        super().cleanup()


class RemovePreset(ChildToolWindow):
    def __init__(self, tool_instance, title, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)
        
        self._build_ui()

    def _build_ui(self):
        
        layout = QGridLayout()
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["", "trash"])
        self.fill_tree()
        self.tree.resizeColumnToContents(1)
        self.tree.setColumnWidth(0, 200)
        layout.addWidget(self.tree)

        self.ui_area.setLayout(layout)
        self.manage(None)

    def fill_tree(self):
        self.tree.clear()
        root = self.tree.invisibleRootItem()
        
        gaussian_preset = QTreeWidgetItem(root)
        gaussian_preset.setData(0, Qt.DisplayRole, "Gaussian")
        for preset in self.tool_instance.presets['Gaussian']:
            preset_item = QTreeWidgetItem(gaussian_preset)
            preset_item.setData(0, Qt.DisplayRole, preset)
            
            remove_widget = QWidget()
            remove_layout = QGridLayout(remove_widget)
            remove = QPushButton()
            remove.setIcon(QIcon(remove_widget.style().standardIcon(QStyle.SP_DialogDiscardButton)))
            remove.setFlat(True)
            remove.clicked.connect(lambda *args, name=preset, tool=self.tool_instance: tool.presets['Gaussian'].pop(name))
            remove.clicked.connect(self.tool_instance.refresh_presets)
            remove.clicked.connect(lambda *args, item=preset_item, parent=gaussian_preset: parent.removeChild(item))
            remove_layout.addWidget(remove, 0, 0, 1, 1, Qt.AlignLeft)
            remove_layout.setColumnStretch(0, 0)
            remove_layout.setContentsMargins(0, 0, 0, 0)
            self.tree.setItemWidget(preset_item, 1, remove_widget)
        
        orca_preset = QTreeWidgetItem(root)
        orca_preset.setData(0, Qt.DisplayRole, "ORCA")
        for preset in self.tool_instance.presets['ORCA']:
            preset_item = QTreeWidgetItem(orca_preset)
            preset_item.setData(0, Qt.DisplayRole, preset)
            
            remove_widget = QWidget()
            remove_layout = QGridLayout(remove_widget)
            remove = QPushButton()
            remove.setIcon(QIcon(remove_widget.style().standardIcon(QStyle.SP_DialogDiscardButton)))
            remove.setFlat(True)
            remove.clicked.connect(lambda *args, name=preset, tool=self.tool_instance: tool.presets['ORCA'].pop(name))
            remove.clicked.connect(self.tool_instance.refresh_presets)
            remove.clicked.connect(lambda *args, item=preset_item, parent=orca_preset: parent.removeChild(item))
            remove_layout.addWidget(remove, 0, 0, 1, 1, Qt.AlignLeft)
            remove_layout.setColumnStretch(0, 0)
            remove_layout.setContentsMargins(0, 0, 0, 0)
            self.tree.setItemWidget(preset_item, 1, remove_widget)
        
        psi4_preset = QTreeWidgetItem(root)
        psi4_preset.setData(0, Qt.DisplayRole, "Psi4")
        for preset in self.tool_instance.presets['Psi4']:
            preset_item = QTreeWidgetItem(psi4_preset)
            preset_item.setData(0, Qt.DisplayRole, preset)
            
            remove_widget = QWidget()
            remove_layout = QGridLayout(remove_widget)
            remove = QPushButton()
            remove.setIcon(QIcon(remove_widget.style().standardIcon(QStyle.SP_DialogDiscardButton)))
            remove.setFlat(True)
            remove.clicked.connect(lambda *args, name=preset, tool=self.tool_instance: tool.presets['Psi4'].pop(name))
            remove.clicked.connect(self.tool_instance.refresh_presets)
            remove.clicked.connect(lambda *args, item=preset_item, parent=psi4_preset: parent.removeChild(item))
            remove_layout.addWidget(remove, 0, 0, 1, 1, Qt.AlignLeft)
            remove_layout.setColumnStretch(0, 0)
            remove_layout.setContentsMargins(0, 0, 0, 0)
            self.tree.setItemWidget(preset_item, 1, remove_widget)

    def cleanup(self):
        self.tool_instance.remove_preset_window = None
        
        super().cleanup()


class PrepLocalJob(ChildToolWindow):
    def __init__(self, tool_instance, title, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)
        
        self._build_ui()
    
        self.form = self.tool_instance.file_type.currentText()
        self.tool_instance.file_type.currentTextChanged.connect(lambda program, widget=self: widget.__setattr__("form", program))
    
    def _build_ui(self):
        layout = QFormLayout()
        
        self.auto_update = QComboBox()
        self.auto_update.addItems(['do nothing', 'open structure', 'change model'])
        ndx = self.auto_update.findText(self.tool_instance.settings.on_finished)
        self.auto_update.setCurrentIndex(ndx)
        layout.addRow("when finished:", self.auto_update)
        
        self.job_name = QLineEdit()
        self.job_name.returnPressed.connect(self.run_job)
        layout.addRow("job name:", self.job_name)

        run = QPushButton("run")
        run.clicked.connect(self.run_job)
        layout.addRow(run)
        
        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        layout.addRow(self.status)
        
        self.ui_area.setLayout(layout)
        self.manage(None)

    def run_job(self):
        job_name = self.job_name.text().strip()
        
        if len(job_name.strip()) == 0 or any(x in job_name for x in "\\/;'\"?<>,`~!@#$%^&*"):
            self.session.logger.error("invalid job name: '%s'" % job_name)
            return

        auto_update = self.auto_update.currentText() == 'change model'
        auto_open = self.auto_update.currentText() == 'open structure'
        self.tool_instance.settings.on_finished = self.auto_update.currentText()

        self.tool_instance.run_local_job(name=job_name, auto_update=auto_update, auto_open=auto_open)
        
        self.status.showMessage("queued \"%s\"; see the log for any details" % job_name)

    def cleanup(self):
        self.tool_instance.job_local_prep = None
        
        super().cleanup()


class ExportPreset(ChildToolWindow):
    def __init__(self, tool_instance, title, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)
        
        self._build_ui()

    def _build_ui(self):
        
        layout = QGridLayout()
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["", "save"])
        self.fill_tree()
        self.tree.resizeColumnToContents(1)
        self.tree.setColumnWidth(0, 200)
        layout.addWidget(self.tree, 0, 0, 1, 2)
        
        save_button = QPushButton("save")
        save_button.clicked.connect(self.save_presets)
        layout.addWidget(save_button, 1, 0, 1, 2, Qt.AlignTop)
        
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 0)
        
        self.ui_area.setLayout(layout)
        self.manage(None)

    def fill_tree(self):
        self.tree.clear()
        root = self.tree.invisibleRootItem()
        
        self.gaussian_preset = QTreeWidgetItem(root)
        self.gaussian_preset.setData(0, Qt.DisplayRole, "Gaussian")
        for preset in self.tool_instance.presets['Gaussian']:
            preset_item = QTreeWidgetItem(self.gaussian_preset)
            preset_item.setData(0, Qt.DisplayRole, preset)
            preset_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            preset_item.setCheckState(1, Qt.Unchecked)
        
        self.orca_preset = QTreeWidgetItem(root)
        self.orca_preset.setData(0, Qt.DisplayRole, "ORCA")
        for preset in self.tool_instance.presets['ORCA']:
            preset_item = QTreeWidgetItem(self.orca_preset)
            preset_item.setData(0, Qt.DisplayRole, preset)
            preset_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            preset_item.setCheckState(1, Qt.Unchecked)
        
        self.psi4_preset = QTreeWidgetItem(root)
        self.psi4_preset.setData(0, Qt.DisplayRole, "Psi4")
        for preset in self.tool_instance.presets['Psi4']:
            preset_item = QTreeWidgetItem(self.psi4_preset)
            preset_item.setData(0, Qt.DisplayRole, preset)
            preset_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            preset_item.setCheckState(1, Qt.Unchecked)

    def save_presets(self):
        filename, _ = QFileDialog.getSaveFileName(filter="JSON files (*.json)")
        if not filename:
            return

        out = {}
        
        for i in range(0, self.gaussian_preset.childCount()):
            if self.gaussian_preset.child(i).checkState(1) == Qt.Checked:
                if "Gaussian" not in out:
                    out["Gaussian"] = {}
                    
                preset_name = self.gaussian_preset.child(i).data(0, Qt.DisplayRole)
                out["Gaussian"][preset_name] = self.tool_instance.presets["Gaussian"][preset_name]

        for i in range(0, self.orca_preset.childCount()):
            if self.orca_preset.child(i).checkState(1) == Qt.Checked:
                if "ORCA" not in out:
                    out["ORCA"] = {}
                    
                preset_name = self.orca_preset.child(i).data(0, Qt.DisplayRole)
                out["ORCA"][preset_name] = self.tool_instance.presets["ORCA"][preset_name]

        for i in range(0, self.psi4_preset.childCount()):
            if self.psi4_preset.child(i).checkState(1) == Qt.Checked:
                if "Psi4" not in out:
                    out["Psi4"] = {}
                    
                preset_name = self.psi4_preset.child(i).data(0, Qt.DisplayRole)
                out["Psi4"][preset_name] = self.tool_instance.presets["Psi4"][preset_name]

        with open(filename, "w") as f:
            dump(out, f, indent=4)
            
        self.tool_instance.session.logger.status("saved presets to %s" % filename)

        self.destroy()

    def cleanup(self):
        self.tool_instance.export_preset_window = None
        
        super().cleanup()