from chimerax.atomic import AtomicStructure, selected_atoms, selected_bonds, selected_pseudobonds, get_triggers
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import StringArg, BoolArg, ListOf, IntArg
from chimerax.core.commands import run

from json import dumps, loads, dump, load

from configparser import ConfigParser

from Qt.QtCore import Qt, QRegularExpression, Signal
from Qt.QtGui import QKeySequence, QFontMetrics, QFontDatabase, QClipboard, QIcon
from Qt.QtWidgets import QCheckBox, QLabel, QGridLayout, QComboBox, QSplitter, QFrame, QLineEdit, \
                         QSpinBox, QMenuBar, QFileDialog, QAction, QApplication, QPushButton, \
                         QTabWidget, QWidget, QGroupBox, QListWidget, QTableWidget, QTableWidgetItem, \
                         QHBoxLayout, QFormLayout, QDoubleSpinBox, QHeaderView, QTextBrowser, \
                         QStatusBar, QTextEdit, QMessageBox, QTreeWidget, QTreeWidgetItem, QSizePolicy, \
                         QStyle

from SEQCROW.residue_collection import ResidueCollection, Residue
from SEQCROW.utils import iter2str
from SEQCROW.widgets import PeriodicTable, ModelComboBox
from SEQCROW.finders import AtomSpec

from AaronTools.config import Config
from AaronTools.const import TMETAL
from AaronTools.theory import *
from AaronTools.theory.method import KNOWN_SEMI_EMPIRICAL
from AaronTools.utils.utils import combine_dicts
from AaronTools.json_extension import ATDecoder, ATEncoder

# import cProfile


class _InputGeneratorSettings(Settings):
    EXPLICIT_SAVE = {
        'last_nproc': Value(0, IntArg),
        'last_mem': Value(0, IntArg),
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
        'previous_method': Value("B3LYP", StringArg),
        'previous_custom_func': Value("", StringArg),
        'previous_functional_names': Value([], ListOf(StringArg), iter2str),
        'previous_functional_needs_basis': Value([], ListOf(BoolArg), iter2str),
        'previous_dispersion': Value("None", StringArg),
        'previous_grid': Value("Default", StringArg),
        'previous_charge': Value(0, IntArg),
        'previous_mult': Value(1, IntArg),
        'previous_solvent_model': Value("None", StringArg),
        'previous_solvent_name': Value("", StringArg),
        # shh is just a json
        'last_options': Value(dumps(dict()), StringArg),
        'previous_options': Value(dumps(dict()), StringArg),
        'last_program': Value("Gaussian", StringArg),
    }

    AUTO_SAVE = {
        "presets": Value(dumps(dict(), cls=ATEncoder), StringArg),
        "on_finished": Value("do nothing", StringArg),
        "settings_version": 2,
    }

    # def save(self, *args, **kwargs):
    #     print("saved qm input settings")
    #     super().save(*args, **kwargs)


class BuildQM(ToolInstance):
    """tool for building input files for QM software (Gaussian, ORCA, Psi4)

    there are comboboxes for the file format (program) and the molecule

    then, THERE ARE FOUR LIGHTS:
    job details        - charge & multiplicity, job type, job-specific options, and solvent
    method             - dft functional or other method
    basis functions    - choose basis sets on a per-element basis
    additional options - generic (and uncurated) options
    """

    SESSION_ENDURING = False
    SESSION_SAVE = False

    help = "https://github.com/QChASM/SEQCROW/wiki/Build-QM-Input-Tool"

    def __init__(self, session, name):
        super().__init__(session, name)

        self.settings = _InputGeneratorSettings(session, name, version="3")

        self.display_name = "QM Input Generator"

        self.tool_window = MainToolWindow(self)
        self.preview_window = None
        self.warning_window = None
        self.preset_window = None
        self.job_local_prep = None
        self.remove_preset_window = None
        self.export_preset_window = None
        self.program = None

        self._build_ui()

        ndx = self.model_selector.currentIndex()
        if ndx != -1:
            self.change_model(ndx)

        self.presets = loads(self.settings.presets, cls=ATDecoder)
        for file_format in session.seqcrow_qm_input_manager.formats:
            if file_format not in self.presets:
                self.presets[file_format] = session.seqcrow_qm_input_manager.get_info(file_format).initial_presets

        if self.settings.settings_version == 2:
            self.migrate_settings_from_v2()
            self.session.logger.warning("settings migrated from version 2")
            # self.session.logger.warning("migration will occur until migration testing is completed")
            self.settings.settings_version = self.settings.settings_version + 1

        self.refresh_presets()

        global_triggers = get_triggers()

        self.changed = False
        self._changes = global_triggers.add_handler("changes", self.check_changes)
        self._changes_done = global_triggers.add_handler("changes done", self.struc_mod_update_preview)

        # this tool is big by default
        # unless the user has saved its position, make it small
        if name not in self.session.ui.settings.tool_positions['windows']:
            self.tool_window.shrink_to_fit()

    def _build_ui(self):
        #build an interface with a dropdown menu to select software package
        #change from one software widget to another when the dropdown menu changes
        #TODO: add a presets tab to save/load presets to aaronrc
        #      so it can easily be used in other tools (like one that makes AARON input files)
        if any(x == self.settings.last_program for x in self.session.seqcrow_qm_input_manager.formats.keys()):
            init_form = self.session.seqcrow_qm_input_manager.get_info(self.settings.last_program)
        else:
            init_form = self.session.seqcrow_qm_input_manager.get_info(
                list(self.session.seqcrow_qm_input_manager.formats.keys())[0]
            )

        layout = QGridLayout()

        basics_form = QWidget()
        form_layout = QFormLayout(basics_form)

        self.file_type = QComboBox()
        self.file_type.addItems(self.session.seqcrow_qm_input_manager.formats.keys())
        ndx = self.file_type.findText(init_form.name, Qt.MatchExactly)
        if ndx >= 0:
            self.file_type.setCurrentIndex(ndx)
        self.file_type.currentIndexChanged.connect(self.change_file_type)

        form_layout.addRow("file type:", self.file_type)

        self.model_selector = ModelComboBox(self.session)
        form_layout.addRow("structure:", self.model_selector)

        layout.addWidget(basics_form, 0, 0)

        #job type stuff
        self.job_widget = JobTypeOption(self.settings, self.session, init_form=init_form)
        self.job_widget.jobTypeChanged.connect(self.update_preview)

        #method stuff
        self.method_widget = MethodOption(self.settings, self.session, init_form=init_form)
        self.method_widget.methodChanged.connect(self.update_preview)

        #basis set stuff
        self.basis_widget = BasisWidget(self.settings, init_form=init_form)
        self.basis_widget.basisChanged.connect(self.update_preview)

        #other keywords
        self.other_keywords_widget = KeywordWidget(self.session, self.settings, init_form=init_form)
        self.other_keywords_widget.additionalOptionsChanged.connect(self.update_preview)

        tabs = QTabWidget()
        tabs.addTab(self.job_widget, "job details")
        tabs.addTab(self.method_widget, "method")
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
        self.copy = copy

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

        warnings = QAction("&Warnings", self.tool_window.ui_area)
        warnings.triggered.connect(self.show_warnings)
        view.addAction(warnings)
        
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
        # need to keep a reference to menu for Qt reasons...
        self._menu = menu
        layout.setMenuBar(menu)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def migrate_settings_from_v2(self):
        """
        import settings from version 2
        this was the version before seqcrow_qm_input_manager was added and
        everything was specific for Gaussian, ORCA, or Psi4
        """
        import os
        from configparser import ConfigParser
        from chimerax import app_dirs_unversioned
        
        filename = os.path.join(
            app_dirs_unversioned.user_config_dir,
            "Build QM Input-2"
        )
        
        if not os.access(filename, os.R_OK):
            return

        old_settings = ConfigParser()
        old_settings.read(filename)
        if old_settings.has_option("DEFAULT", "previous_basis_names"):
            previous_basis_names = old_settings.get("DEFAULT", "previous_basis_names")
            self.settings.previous_basis_names = eval("[%s]" % old_settings.get("DEFAULT", "previous_basis_names"))
        if old_settings.has_option("DEFAULT", "previous_basis_paths"):
            previous_basis_paths = eval("[%s]" % old_settings.get("DEFAULT", "previous_basis_paths"))
            self.settings.previous_basis_paths = previous_basis_paths
        if old_settings.has_option("DEFAULT", "previous_functional_names"):
            previous_functional_names = eval("[%s]" % old_settings.get("DEFAULT", "previous_functional_names"))
            self.settings.previous_functional_names = previous_functional_names
        if old_settings.has_option("DEFAULT", "previous_functional_needs_basis"):
            previous_functional_needs_basis = eval("[%s]" % old_settings.get("DEFAULT", "previous_functional_needs_basis"))
            self.settings.previous_functional_needs_basis = previous_functional_needs_basis
        
        if old_settings.has_option("DEFAULT", "previous_psi4_options"):
            previous_psi4_options = loads(eval(old_settings.get("DEFAULT", "previous_psi4_options")))
            previous_options = loads(self.settings.previous_options)
            if "Psi4" in previous_options:
                previous_options["Psi4"] = combine_dicts(
                    previous_psi4_options, previous_options["Psi4"]
                )
            else:
                previous_options["Psi4"] = previous_psi4_options
            self.settings.previous_options = dumps(previous_options)
        
        if old_settings.has_option("DEFAULT", "previous_gaussian_options"):
            previous_gaussian_options = loads(eval(old_settings.get("DEFAULT", "previous_gaussian_options")))
            previous_options = loads(self.settings.previous_options)
            if "Gaussian" in previous_options:
                previous_options["Gaussian"] = combine_dicts(
                    previous_gaussian_options, previous_options["Gaussian"]
                )
            else:
                previous_options["Gaussian"] = previous_gaussian_options
            self.settings.previous_options = dumps(previous_options)
        
        if old_settings.has_option("DEFAULT", "previous_orca_options"):
            previous_orca_options = loads(eval(old_settings.get("DEFAULT", "previous_orca_options")))
            previous_options = loads(self.settings.previous_options)
            if "ORCA" in previous_options:
                previous_options["ORCA"] = combine_dicts(
                    previous_orca_options, previous_options["ORCA"]
                )
            else:
                previous_options["ORCA"] = previous_orca_options
            self.settings.previous_options = dumps(previous_options)
            
        if old_settings.has_option("DEFAULT", "gaussian_presets"):
            gaussian_presets = loads(eval(old_settings.get("DEFAULT", "gaussian_presets")))
            for preset_name in gaussian_presets:
                theory = Theory()
                new_preset = dict()
                preset = gaussian_presets[preset_name]
                if "opt" in preset:
                    new_preset["use_job_type"] = True
                    if preset["opt"]:
                        job = OptimizationJob(transition_state=preset["ts"])
                        if not theory.job_type:
                            theory.job_type = job
                        else:
                            theory.job_type.append(job)
                if "freq" in preset:
                    new_preset["use_job_type"] = True
                    if preset["freq"]:
                        new_preset["raman"] = preset["raman"]
                        job = FrequencyJob(temperature=preset["temp"], numerical=preset["num_freq"])
                        if not theory.job_type:
                            theory.job_type = job
                        else:
                            theory.job_type.append(job)
                if "nproc" in preset:
                    new_preset["use_job_resources"] = True
                    theory.processors = preset["nproc"]
                if "mem" in preset:
                    new_preset["use_job_resources"] = True
                    theory.memory = preset["mem"]
                if "solvent" in preset:
                    new_preset["use_solvent"] = True
                    if preset["solvent model"] and preset["solvent model"] != "None":
                        theory.solvent = ImplicitSolvent(preset["solvent model"], preset["solvent"])
                if "method" in preset:
                    new_preset["use_method"] = True
                    theory.method = Method(preset["method"], preset["semi-empirical"])
                if "grid" in preset:
                    new_preset["use_method"] = True
                    if preset["grid"]:
                        theory.grid = IntegrationGrid(preset["grid"])
                if "disp" in preset:
                    new_preset["use_method"] = True
                    if preset["disp"]:
                        theory.dispersion = EmpiricalDispersion(preset["disp"])
                if "other" in preset:
                    new_preset["use_other"] = True
                    theory.kwargs = preset["other"]
                if "basis" in preset:
                    new_preset["use_basis"] = True
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
                    theory.basis = basis_set
                new_preset["theory"] = theory
                
                self.presets["Gaussian"][preset_name] = new_preset
                
        if old_settings.has_option("DEFAULT", "orca_presets"):
            orca_presets = loads(eval(old_settings.get("DEFAULT", "orca_presets")))
            for preset_name in orca_presets:
                theory = Theory()
                new_preset = dict()
                preset = orca_presets[preset_name]
                if "opt" in preset:
                    new_preset["use_job_type"] = True
                    if preset["opt"]:
                        job = OptimizationJob(transition_state=preset["ts"])
                        if not theory.job_type:
                            theory.job_type = job
                        else:
                            theory.job_type.append(job)
                if "freq" in preset:
                    new_preset["use_job_type"] = True
                    if preset["freq"]:
                        new_preset["raman"] = preset["raman"]
                        job = FrequencyJob(temperature=preset["temp"], numerical=preset["num_freq"])
                        if not theory.job_type:
                            theory.job_type = job
                        else:
                            theory.job_type.append(job)
                if "nproc" in preset:
                    new_preset["use_job_resources"] = True
                    theory.processors = preset["nproc"]
                if "mem" in preset:
                    new_preset["use_job_resources"] = True
                    theory.memory = preset["mem"]
                if "solvent" in preset:
                    new_preset["use_solvent"] = True
                    if preset["solvent model"] and preset["solvent model"] != "None":
                        theory.solvent = ImplicitSolvent(preset["solvent model"], preset["solvent"])
                if "method" in preset:
                    new_preset["use_method"] = True
                    theory.method = Method(preset["method"], preset["semi-empirical"])
                if "grid" in preset:
                    new_preset["use_method"] = True
                    if preset["grid"]:
                        theory.grid = IntegrationGrid(preset["grid"])
                if "disp" in preset:
                    new_preset["use_method"] = True
                    if preset["disp"]:
                        theory.dispersion = EmpiricalDispersion(preset["disp"])
                if "other" in preset:
                    new_preset["use_other"] = True
                    theory.kwargs = preset["other"]
                if "basis" in preset:
                    new_preset["use_basis"] = True
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
                    theory.basis = basis_set
                new_preset["theory"] = theory
                
                self.presets["ORCA"][preset_name] = new_preset
                
        if old_settings.has_option("DEFAULT", "psi4_presets"):
            psi4_presets = loads(eval(old_settings.get("DEFAULT", "psi4_presets")))
            for preset_name in psi4_presets:
                theory = Theory()
                new_preset = dict()
                preset = psi4_presets[preset_name]
                if "opt" in preset:
                    new_preset["use_job_type"] = True
                    if preset["opt"]:
                        job = OptimizationJob(transition_state=preset["ts"])
                        if not theory.job_type:
                            theory.job_type = job
                        else:
                            theory.job_type.append(job)
                if "freq" in preset:
                    new_preset["use_job_type"] = True
                    if preset["freq"]:
                        new_preset["raman"] = preset["raman"]
                        job = FrequencyJob(temperature=preset["temp"], numerical=preset["num_freq"])
                        if not theory.job_type:
                            theory.job_type = job
                        else:
                            theory.job_type.append(job)
                if "nproc" in preset:
                    new_preset["use_job_resources"] = True
                    theory.processors = preset["nproc"]
                if "mem" in preset:
                    new_preset["use_job_resources"] = True
                    theory.memory = preset["mem"]
                if "solvent" in preset:
                    new_preset["use_solvent"] = True
                    if preset["solvent model"] and preset["solvent model"] != "None":
                        theory.solvent = ImplicitSolvent(preset["solvent model"], preset["solvent"])
                if "method" in preset:
                    new_preset["use_method"] = True
                    theory.method = Method(preset["method"], preset["semi-empirical"])
                if "grid" in preset:
                    new_preset["use_method"] = True
                    if preset["grid"]:
                        theory.grid = IntegrationGrid(preset["grid"])
                if "disp" in preset:
                    new_preset["use_method"] = True
                    if preset["disp"]:
                        theory.dispersion = EmpiricalDispersion(preset["disp"])
                if "other" in preset:
                    new_preset["use_other"] = True
                    theory.kwargs = preset["other"]
                if "basis" in preset:
                    new_preset["use_basis"] = True
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
                    theory.basis = basis_set
                new_preset["theory"] = theory
                
                self.presets["Psi4"][preset_name] = new_preset

        self.settings.presets = dumps(self.presets, cls=ATEncoder)

        self.settings.save()

    def refresh_presets(self):
        """cleans and repopulates the "presets" dropdown on the tool's ribbon"""
        self.presets_menu.clear()

        for program in self.presets:
            program_submenu = self.presets_menu.addMenu(program)
            for preset in self.presets[program]:
                preset_action = QAction(preset, self.tool_window.ui_area)
                preset_action.triggered.connect(lambda *args, program=program, name=preset: self.apply_preset(program, name))
                program_submenu.addAction(preset_action)

        self.settings.presets = dumps(self.presets, cls=ATEncoder)

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
        else:
            self.preset_window.shown = True

    def apply_preset(self, program, preset_name):
        """apply preset named 'preset_name' for 'program'"""
        preset = self.presets[program][preset_name]

        ndx = self.file_type.findText(program, Qt.MatchExactly)
        self.file_type.setCurrentIndex(ndx)

        self.file_type.blockSignals(True)
        self.method_widget.blockSignals(True)
        self.basis_widget.blockSignals(True)
        self.job_widget.blockSignals(True)
        self.other_keywords_widget.blockSignals(True)

        theory = preset["theory"]

        if "use_job_type" in preset and preset["use_job_type"]:
            self.job_widget.do_geom_opt.setChecked(False)
            self.job_widget.do_freq.setChecked(False)
            if theory.job_type:
                for job in theory.job_type:
                    if isinstance(job, OptimizationJob):
                        self.job_widget.do_geom_opt.setChecked(True)
                        self.job_widget.ts_opt.setChecked(job.transition_state)
            
                    elif isinstance(job, FrequencyJob):
                        self.job_widget.do_freq.setChecked(True)
                        self.job_widget.temp.setValue(job.temperature)
                        self.job_widget.num_freq.setChecked(job.numerical)

            if 'raman' in preset:
                self.job_widget.raman.setChecked(preset['raman'])

        if "use_job_resources" in preset and preset["use_job_resources"]:
            if theory.processors:
                self.job_widget.setProcessors(theory.processors)
            else:
                self.job_widget.setProcessors(0)
            
            if theory.memory:
                self.job_widget.setMemory(theory.memory)
            else:
                self.job_widget.setMemory(0)
            

        if "use_solvent" in preset and preset["use_solvent"]:
            self.job_widget.setSolvent(theory.solvent)

        if "use_method" in preset and preset["use_method"]:
            self.method_widget.setMethod(theory.method)
            self.method_widget.setGrid(theory.grid)
            self.method_widget.setDispersion(theory.empirical_dispersion)

        if "use_basis" in preset and preset["use_basis"]:
            if self.model_selector.currentData():
                rescol = ResidueCollection(self.model_selector.currentData(), bonds_matter=False)
                if theory.basis:
                    theory.basis.refresh_elements(rescol)
            self.basis_widget.setBasis(theory.basis)

        if "use_other" in preset and preset["use_other"]:
            self.other_keywords_widget.setKeywords(theory.kwargs)

        self.file_type.blockSignals(False)
        self.method_widget.blockSignals(False)
        self.basis_widget.blockSignals(False)
        self.job_widget.blockSignals(False)
        self.other_keywords_widget.blockSignals(False)

        self.update_preview()

        self.session.logger.status("applied \"%s\" (%s)" % (preset_name, program))

        if self.preset_window is not None:
            self.preset_window.basis_elements.refresh_basis()

    def show_remove_preset(self):
        """shows the child window to remove a preset"""
        if self.remove_preset_window is None:
            self.remove_preset_window = self.tool_window.create_child_window("Remove Presets", window_class=RemovePreset)
        else:
            self.remove_preset_window.shown = True

    def show_export_preset(self):
        """shows child window to export preset json"""
        if self.export_preset_window is None:
            self.export_preset_window = self.tool_window.create_child_window("Export Presets", window_class=ExportPreset)
        else:
            self.export_preset_window.shown = True

    def import_preset_file(self):
        """open file browser, select file, and import presets"""
        filename, _ = QFileDialog.getOpenFileName(filter="JSON files (*.json);;INI files (*.ini)")

        if not filename:
            return

        if filename.lower().endswith("json"):
            with open(filename, 'r') as f:
                new_presets = load(f, cls=ATDecoder)

            for program in self.session.seqcrow_qm_input_manager.formats.keys():
                if program in new_presets:
                    for preset_name in new_presets[program]:
                        if preset_name in self.presets[program]:
                            yes = QMessageBox.question(
                                self.presets_menu,
                                "%s preset named \"%s\" already exists" % (program, preset_name),
                                "would you like to overwrite \"%s\"?" % preset_name,
                                QMessageBox.Yes | QMessageBox.No,
                            )

                            if yes != QMessageBox.Yes:
                                continue

                        self.presets[program][preset_name] = new_presets[program][preset_name]

                        self.session.logger.status("imported %s preset \"%s\"" % (program, preset_name))

        elif filename.lower().endswith("ini"):
            config = Config(filename, quiet=True)

            for section in config.sections():
                new_preset = {}

                program = config.get(section, "exec_type", fallback=False)
                if not program:
                    self.session.logger.info("skipping %s; no program was specified (exec_type)" % section)
                    continue
                
                for form in self.session.seqcrow_qm_input_manager.formats.keys():
                    if re.match(form, program, flags=re.IGNORECASE):
                        program = form
                        break
                else:
                    self.session.logger.warning("skipping %s; exec_type %s was not recognized" % (section, program))
                    continue

                if section in self.presets[program]:
                    yes = QMessageBox.question(
                        self.presets_menu,
                        "%s preset named \"%s\" already exists" % (program, section),
                        "would you like to overwrite \"%s\"?" % section,
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if yes != QMessageBox.Yes:
                        continue

                theory = config.get_theory(None, section=section)
                theory.kwargs = config.get_other_kwargs(section=section)
                new_preset["theory"] = theory
                new_preset["use_job_type"] = config.getboolean(section, "use_job_type", True)
                new_preset["use_job_resources"] = config.getboolean(section, "use_job_resources", True)
                new_preset["use_solvent"] = config.getboolean(section, "use_solvent", True)
                new_preset["use_method"] = config.getboolean(section, "use_method", True)
                new_preset["use_basis"] = config.getboolean(section, "use_basis", True)
                new_preset["use_other"] = config.getboolean(section, "use_other", True)
                new_preset["raman"] = config.getboolean(section, "raman", False)

                self.presets[program][section] = new_preset

        else:
            self.session.logger.error("file must have JSON or INI extention")

        self.refresh_presets()

    def show_queue(self):
        """show queue tool"""
        run(self.session, "ui tool show \"Job Queue\"")

    def show_preview(self):
        """open child tool that showns contents of input file"""
        if self.preview_window is None:
            self.preview_window = self.tool_window.create_child_window("Input Preview", window_class=InputPreview)
            self.update_preview()
        else:
            self.preview_window.shown = True

    def show_warnings(self):
        """open child tool that showns contents of input file"""
        if self.warning_window is None:
            self.warning_window = self.tool_window.create_child_window("Warnings", window_class=WarningPreview)
            self.update_preview()
        else:
            self.warning_window.shown = True

    def get_file_contents(self, update_settings=False):
        self.update_theory(update_settings=update_settings)

        program = self.file_type.currentText()
        contents, warnings = self.session.seqcrow_qm_input_manager.get_info(program).get_file_contents(self.theory)
        return contents, warnings

    def check_changes(self, trigger_name=None, changes=None):
        if changes is not None:
            mdl = self.model_selector.currentData()
            if mdl in changes.modified_atomic_structures():
                self.changed = True

    def struc_mod_update_preview(self, *args, **kwargs):
        """whenever a setting is changed, this should be called to update the preview"""
        if self.changed:
            self.update_preview()
            self.changed = False

    def update_preview(self):
        """whenever a setting is changed, this should be called to update the preview"""
        model = self.model_selector.currentData()
        if not model:
            return

        # profile = cProfile.Profile()
        # profile.enable()

        self.check_elements()
        if self.preview_window is not None or self.warning_window is not None:
            contents, warnings = self.get_file_contents(update_settings=False)
            if contents is not None and warnings is not None:
                if self.preview_window is not None:
                    self.preview_window.setPreview(contents, warnings)
                if self.warning_window is not None:
                    self.warning_window.setWarnings(warnings)

        # profile.disable()
        # profile.print_stats()

    def change_file_type(self, *args):
        """change the file type
        args are ignored, only the contents of self.file_type matters"""
        #if we don't block signals, the preview will try to update before all widgets
        #have been updated to give the proper info
        self.file_type.blockSignals(True)
        self.method_widget.blockSignals(True)
        self.basis_widget.blockSignals(True)
        self.job_widget.blockSignals(True)
        self.other_keywords_widget.blockSignals(True)

        program = self.file_type.currentText()
        file_info = self.session.seqcrow_qm_input_manager.get_info(program)
        self.settings.last_program = program
        self.method_widget.setOptions(file_info)
        self.basis_widget.setOptions(file_info)
        self.job_widget.setOptions(file_info)
        self.other_keywords_widget.setOptions(file_info)

        self.file_type.blockSignals(False)
        self.method_widget.blockSignals(False)
        self.basis_widget.blockSignals(False)
        self.job_widget.blockSignals(False)
        self.other_keywords_widget.blockSignals(False)

        self.update_preview()

    def update_theory(self, update_settings=False):
        """grabs the current settings and updates self.theory
        always called before creating an input file"""
        rescol = ResidueCollection(self.model_selector.currentData(), bonds_matter=False)

        meth = self.method_widget.getMethod(update_settings)
        basis = self.get_basis_set(update_settings)

        dispersion = self.method_widget.getDispersion(update_settings)

        grid = self.method_widget.getGrid(update_settings)
        charge = self.job_widget.getCharge(update_settings)
        mult = self.job_widget.getMultiplicity(update_settings)
        if isinstance(meth, SAPTMethod):
            charges = [widget.value() for widget in \
                [self.method_widget.sapt_layers.tabs.widget(i).charge for i in range(0, self.method_widget.sapt_layers.tabs.count())]
            ]
            multiplicities = [widget.value() for widget in \
                [self.method_widget.sapt_layers.tabs.widget(i).multiplicity for i in range(0, self.method_widget.sapt_layers.tabs.count())]
            ]

            charge = [charge]
            charge.extend(charges)

            mult = [mult]
            mult.extend(multiplicities)

            rescol.components = [
                Residue(
                    rescol.find([AtomSpec(atom.atomspec) for atom in layer]),
                    refresh_connected=False
                ) if layer else Residue([], refresh_ranks=False, refresh_connected=False)
                for layer in self.method_widget.sapt_layers.layers
            ]

        nproc = self.job_widget.getNProc(update_settings)
        mem = self.job_widget.getMem(update_settings)
        jobs = self.job_widget.getJobs() #job settings get updated during getKWDict

        solvent = self.job_widget.getSolvent(update_settings)
        
        kw_dict = self.job_widget.getKWDict(update_settings=update_settings)
        other_kw_dict = self.other_keywords_widget.getKWDict(update_settings=update_settings)
        if update_settings:
            self.settings.save()

        combined_dict = combine_dicts(kw_dict, other_kw_dict)

        self.theory = Theory(
            charge=charge,
            multiplicity=mult,
            method=meth,
            basis=basis,
            empirical_dispersion=dispersion,
            grid=grid,
            processors=nproc,
            memory=mem,
            job_type=jobs,
            solvent=solvent,
            geometry=rescol,
            **combined_dict
        )

    def change_model(self, index):
        """changes model to the one selected in self.model_selector (index is basically ignored"""
        if index == -1:
            self.basis_widget.setElements([])
            return

        mdl = self.model_selector.currentData()

        self.job_widget.setStructure(mdl)
        self.method_widget.sapt_layers.setStructure(mdl)
        self.check_elements()

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
            self.method_widget.sapt_layers.check_deleted_atoms()

    def get_basis_set(self, update_settings=False):
        """get BasisSet object from the basis widget"""
        basis, ecp = self.basis_widget.get_basis(update_settings)

        return BasisSet(basis, ecp)

    def show_local_job_prep(self):
        """open run local job child window"""
        if self.job_local_prep is None:
            self.job_local_prep = self.tool_window.create_child_window("Launch Job", window_class=PrepLocalJob)

    def run_local_job(self, *args, name="local_job", auto_update=False, auto_open=False):
        """run job"""
        self.update_theory(update_settings=True)

        # need to convert constraints to atoms so they can be encoded by the 
        # job manager
        for job in self.theory.job_type:
            if isinstance(job, OptimizationJob):
                if job.constraints:
                    for key in job.constraints:
                        if key == "atoms":
                            if not job.constraints["atoms"]:
                                continue
                            job.constraints["atoms"] = [
                                "%i" % (self.theory.geometry.atoms.index(atom) + 1)
                                for atom in self.theory.geometry.find(job.constraints["atoms"])
                            ]
                        else:
                            for i, con in enumerate(job.constraints[key]):
                                job.constraints[key][i] = [
                                    "%i" % (self.theory.geometry.atoms.index(atom) + 1)
                                    for atom in self.theory.geometry.find(con)
                                ]

        kw_dict = self.job_widget.getKWDict(update_settings=True)
        other_kw_dict = self.other_keywords_widget.getKWDict(update_settings=True)
        self.settings.save()

        combined_dict = combine_dicts(kw_dict, other_kw_dict)

        self.settings.last_program = self.file_type.currentText()

        program = self.file_type.currentText()
        if program in self.session.seqcrow_job_manager.formats:
            job_cls = self.session.seqcrow_job_manager.formats[program].run_provider(
                self.session,
                program,
                self.session.seqcrow_job_manager,
            )
            job = job_cls(name, self.session, self.theory, auto_update=auto_update, auto_open=auto_open)
    
            self.session.logger.status("adding %s to queue" % name)
    
            self.session.seqcrow_job_manager.add_job(job)
        else:
            raise NotImplementedError("no provider for running local %s jobs" % program)

        self.update_preview()

    def copy_input(self):
        """copies input file to the clipboard"""
        output, warnings = self.get_file_contents(update_settings=True)

        if isinstance(output, dict):
            s = ""
            for key, item in output.items():
                s += "<<- %s\n" % key
                s += item
                s += "%s\n\n\n" % key
            output = s

        for warning in warnings:
            self.session.logger.warning(warning)

        app = QApplication.instance()
        clipboard = app.clipboard()
        clipboard.setText(output)

        self.update_preview()

        self.session.logger.status("copied to clipboard")

    def save_input(self):
        """save input to a file
        a file dialog will open asking for a file location"""

        program = self.file_type.currentText()
        info = self.session.seqcrow_qm_input_manager.get_info(program)
        self.settings.last_program = program
        filename, _ = QFileDialog.getSaveFileName(filter=info.save_file_filer)

        if not filename:
            return

        contents, warnings = self.get_file_contents(update_settings=True)

        if isinstance(contents, dict):
            for key, item in contents.items():
                if "%" in key:
                    fname = key % filename
                else:
                    fname = filename
                with open(fname, "w") as f:
                    f.write(item)
        else:
            with open(filename, "w") as f:
                f.write(contents)

        for warning in warnings:
            self.session.logger.warning(warning)

        self.update_preview()

        self.session.logger.status("saved to %s" % filename)

    def delete(self):
        """deregister trigger handlers"""
        #overload delete to de-register handler
        global_triggers = get_triggers()
        global_triggers.remove_handler(self._changes)
        global_triggers.remove_handler(self._changes_done)

        self.model_selector.deleteLater()

        return super().delete()

    def close(self):
        """deregister trigger handlers"""
        #overload delete to de-register handler
        global_triggers = get_triggers()
        global_triggers.remove_handler(self._changes)
        global_triggers.remove_handler(self._changes_done)

        self.model_selector.deleteLater()

        return super().close()

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
    jobTypeChanged = Signal()

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
        job_type_layout.addRow("geometry optimization:", self.do_geom_opt)

        self.do_freq = QCheckBox()
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
        self.use_checkpoint.stateChanged.connect(self.chk_state_changed)
        runtime_layout.addRow("read checkpoint:", self.use_checkpoint)

        runtime_outer_shell_layout.addWidget(runtime_form, 0, 0, 1, 1, Qt.AlignTop)

        file_browse = QWidget()
        file_browse_layout = QGridLayout(file_browse)
        margins = file_browse_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        file_browse_layout.setContentsMargins(*new_margins)
        self.chk_file_path = QLineEdit()
        self.chk_file_path.textChanged.connect(self.something_changed)
        self.chk_browse_button = QPushButton("browse...")
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
        self.raman.setChecked(self.settings.last_raman)
        self.raman.stateChanged.connect(self.something_changed)
        freq_opt_form.addRow("Raman intensities:", self.raman)

        self.num_freq = QCheckBox()
        self.num_freq.setChecked(self.settings.last_num_freq)
        self.num_freq.stateChanged.connect(self.something_changed)
        self.num_freq.setToolTip("numerical vibrational frequency algorithms are often slower and less reliable than analytical algorithms\nusually requires less memory than analytical, but are available for methods where analytical frequencies are not")
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
        self.solvent_name.setText(self.settings.previous_solvent_name)
        self.solvent_name.textChanged.connect(self.filter_solvents)
        self.solvent_name.setClearButtonEnabled(True)
        solvent_form_layout.addRow(self.solvent_name_label, self.solvent_name)

        solvent_layout.addWidget(solvent_form, 0, 0, Qt.AlignTop)

        self.solvent_names = QListWidget()
        self.solvent_names.setSelectionMode(self.solvent_names.SingleSelection)
        self.solvent_names.itemSelectionChanged.connect(self.change_selected_solvent)
        self.solvent_names.itemDoubleClicked.connect(self.change_selected_solvent)

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

        self.do_geom_opt.stateChanged.connect(self.opt_checked)
        self.do_freq.stateChanged.connect(self.freq_checked)
        self.do_geom_opt.stateChanged.connect(self.change_job_type)
        self.do_freq.stateChanged.connect(self.change_job_type)

        self.do_geom_opt.setCheckState(Qt.Checked if self.settings.last_opt else Qt.Unchecked)
        self.ts_opt.setCheckState(Qt.Checked if self.settings.last_ts else Qt.Unchecked)
        self.do_freq.setCheckState(Qt.Checked if self.settings.last_freq else Qt.Unchecked)
        self.job_type_opts.setCurrentIndex(0)

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
        """open file dialog to locate chk/gbs/hess file"""
        if self.use_checkpoint.checkState() == Qt.Unchecked and not self.form.save_checkpoint_filter and self.form.read_checkpoint_filter:
            self.use_checkpoint.setCheckState(Qt.Checked)
        
        elif self.use_checkpoint.checkState() == Qt.Checked and not self.form.read_checkpoint_filter and self.form.save_checkpoint_filter:
            self.use_checkpoint.setCheckState(Qt.Unchecked)
            
        if self.use_checkpoint.checkState() == Qt.Checked and self.form.read_checkpoint_filter:
            filename, _ = QFileDialog.getOpenFileName(filter=self.form.read_checkpoint_filter)
        
        elif self.use_checkpoint.checkState() == Qt.Unchecked and self.form.save_checkpoint_filter:
            filename, _ = QFileDialog.getSaveFileName(filter=self.form.save_checkpoint_filter)
        else:
            return

        if filename:
            self.chk_file_path.setText(filename)

    def something_changed(self, *args, **kw):
        """called whenever a setting has changed to notify the main tool"""
        self.jobTypeChanged.emit()

    def opt_checked(self, state):
        """when optimization is checked, switch the tab widget to show optimization settings"""
        if state == Qt.Checked:
            self.job_type_opts.setCurrentIndex(1)
        elif self.job_type_opts.currentIndex() == 1:
            self.job_type_opts.setCurrentIndex(0)

    def freq_checked(self, state):
        """when frequency is checked, switch the tab widget to show freq settings"""
        if state == Qt.Checked:
            self.job_type_opts.setCurrentIndex(2)
        elif self.job_type_opts.currentIndex() == 2:
            self.job_type_opts.setCurrentIndex(0)

    def chk_state_changed(self, state):
        if state == Qt.Checked:
            self.chk_file_path.setEnabled(bool(self.form.read_checkpoint_filter))
            self.chk_browse_button.setEnabled(bool(self.form.read_checkpoint_filter))
        else:
            self.chk_file_path.setEnabled(bool(self.form.save_checkpoint_filter))
            self.chk_browse_button.setEnabled(bool(self.form.save_checkpoint_filter))

    def setOptions(self, file_info):
        """change all options to show the ones available for 'program'"""
        self.form = file_info
        self.solvent_option.clear()
        self.solvent_names.clear()
        self.solvent_option.addItems(["None"])
        if file_info.solvent_models is not None:
            self.solvent_option.addItems(file_info.solvent_models)
        self.hpmodes.setEnabled(file_info.hpmodes_available)
        self.raman.setToolTip("ask %s to compute Raman intensities" % file_info.name)
        self.raman.setEnabled(file_info.raman_available)
        if file_info.solvents:
            ndx = self.solvent_option.findText(self.settings.previous_solvent_model)
            if ndx >= 0:
                self.solvent_option.setCurrentIndex(ndx)
            if isinstance(file_info.solvents, dict) and self.solvent_option.currentText() in file_info.solvents:
                self.solvent_names.addItems(file_info.solvents[self.solvent_option.currentText()])
            else:
                self.solvent_names.addItems(file_info.solvents)
            self.solvent_name.setText(self.settings.previous_solvent_name)
        self.job_type_opts.setTabEnabled(3, bool(file_info.solvent_models))
        if not file_info.read_checkpoint_filter:
            self.use_checkpoint.setCheckState(Qt.Unchecked)
        self.use_checkpoint.setEnabled(
            bool(file_info.read_checkpoint_filter)
        )
        self.chk_file_path.setEnabled(
            (self.use_checkpoint.checkState() == Qt.Checked and bool(file_info.read_checkpoint_filter)) or 
            (self.use_checkpoint.checkState() == Qt.Unchecked and bool(file_info.save_checkpoint_filter))
        )
        self.chk_browse_button.setEnabled(
            (self.use_checkpoint.checkState() == Qt.Checked and bool(file_info.read_checkpoint_filter)) or 
            (self.use_checkpoint.checkState() == Qt.Unchecked and bool(file_info.save_checkpoint_filter))
        )

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

        if isinstance(self.form.solvents, dict) and self.solvent_option.currentText() in self.form.solvents:
            self.solvent_names.clear()
            self.solvent_names.addItems(self.form.solvents[self.solvent_option.currentText()])
            self.solvent_names.sortItems()
            self.filter_solvents(self.solvent_name.text())

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

    def getGeometryOptimization(self):
        """returns whether the job type is opt"""
        return self.do_geom_opt.checkState() == Qt.Checked

    def getTSOptimization(self):
        """returns whether the job is opt ts"""
        return self.ts_opt.checkState() == Qt.Checked

    def getFrequencyCalculation(self):
        """returns whether the job is freq"""
        return self.do_freq.checkState() == Qt.Checked

    def getJobs(self):
        """returns list(JobType) for the current jobs"""
        job_types = []
        if self.do_geom_opt.checkState() == Qt.Checked:
            if self.use_contraints.checkState() == Qt.Checked:
                constraints = self.getConstraints()

                new_constraints = {}
                if "atoms" in constraints:
                    new_constraints["atoms"] = [AtomSpec(atom.atomspec) for atom in constraints["atoms"]]
                    for key in ["bonds", "angles", "torsions"]:
                        if key in constraints:
                            if key in constraints:
                                new_constraints[key] = []
                                for constraint in constraints[key]:
                                    new_constraints[key].append([AtomSpec(atom.atomspec) for atom in constraint])

                constraints = new_constraints
            else:
                constraints = None


            job_types.append(OptimizationJob(transition_state=self.ts_opt.checkState() == Qt.Checked,
                                             constraints=constraints)
                            )

        if self.do_freq.checkState() == Qt.Checked:
            if self.form == "ORCA":
                job_types.append(FrequencyJob(numerical=(self.num_freq.checkState() == Qt.Checked or
                                                        self.raman.checkState() == Qt.Checked),
                                            temperature=self.temp.value())
                                )
            else:
                job_types.append(FrequencyJob(numerical=self.num_freq.checkState() == Qt.Checked,
                                              temperature=self.temp.value())
                                )

        return job_types

    def getSolvent(self, update_settings):
        """returns ImplicitSolvent for the current solvent settings"""
        model = self.solvent_option.currentText()
        if model == "None":
            if update_settings:
                self.settings.previous_solvent_model = "None"
            return None

        solvent = self.solvent_name.text()

        if update_settings:
            self.settings.previous_solvent_model = model
            self.settings.previous_solvent_name = solvent

        return ImplicitSolvent(model, solvent)

    def setSolvent(self, solvent):
        """sets solvent to match the given ImplicitSolvent"""
        if isinstance(solvent, ImplicitSolvent):
            ndx = self.solvent_option.findText(solvent.name)
            if ndx >= 0:
                self.solvent_option.setCurrentIndex(ndx)
    
            self.solvent_name.setText(solvent.solvent)
        else:
            self.solvent_option.setCurrentIndex(0)

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
        current_bonds.extend([bond for bond in selected_pseudobonds(self.session) if bond.group.structure is self.structure])
        for bond in current_bonds:
            atom1, atom2 = bond.atoms
            if any(atom1 in constrained_bond and atom2 in constrained_bond for constrained_bond in self.constrained_bonds):
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
        current_bonds.extend([bond for bond in selected_pseudobonds(self.session) if bond.group.structure is self.structure])
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
        current_bonds.extend([bond for bond in selected_pseudobonds(self.session) if bond.group.structure is self.structure])
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

                atom1 = [atom for atom in current_atoms if atom2 in atom.neighbors]
                if len(atom1) < 1:
                    for pbond in selected_pseudobonds(self.session):
                        if atom2 in pbond.atoms and any(atom in pbond.atoms for atom in current_atoms):
                            atom1 = pbond.other_atom(atom2)
                else:
                    atom1 = atom1[0]

                atom4 = [atom for atom in current_atoms if atom3 in atom.neighbors]
                if len(atom4) < 1:
                    for pbond in selected_pseudobonds(self.session):
                        if atom3 in pbond.atoms and any(atom in pbond.atoms for atom in current_atoms):
                            atom4 = pbond.other_atom(atom3)
                else:
                    atom4 = atom4[0]

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

    def getNProc(self, update_settings=False):
        """returns number of processors"""
        if update_settings:
            self.settings.last_nproc = self.nprocs.value()

        if self.nprocs.value() > 0:
            return self.nprocs.value()
        else:
            return None

    def getMem(self, update_settings=False):
        """returns memory"""
        if update_settings:
            self.settings.last_mem = self.mem.value()

        if self.mem.value() != 0:
            return self.mem.value()
        else:
            return None

    def getKWDict(self, update_settings=False):
        """returns dictiory specifying misc options for writing an input file"""
        if update_settings:
            self.settings.last_nproc = self.nprocs.value()
            self.settings.last_mem = self.mem.value()
            self.settings.last_opt = self.do_geom_opt.checkState() == Qt.Checked
            self.settings.last_ts = self.ts_opt.checkState() == Qt.Checked
            self.settings.last_freq = self.do_freq.checkState() == Qt.Checked
            self.settings.last_num_freq = self.num_freq.checkState() == Qt.Checked
            self.settings.last_raman = self.raman.checkState() == Qt.Checked

        return self.form.get_job_kw_dict(
            self.do_geom_opt.checkState() == Qt.Checked,
            self.do_freq.checkState() == Qt.Checked,
            self.raman.checkState() == Qt.Checked,
            self.hpmodes.checkState() == Qt.Checked,
            self.use_checkpoint.checkState() == Qt.Checked,
            self.chk_file_path.text(),
        )

    def check_deleted_atoms(self):
        """purge deleted atoms from constraints table and lists"""
        for atom in self.constrained_atoms[::-1]:
            if atom.deleted:
                self.constrained_atom_table.removeRow(self.constrained_atoms.index(atom))
                self.constrained_atoms.remove(atom)

        for bond in self.constrained_bonds:
            if any(atom.deleted for atom in bond):
                self.constrained_bond_table.removeRow(self.constrained_bonds.index(bond))
                self.constrained_bonds.remove(bond)

        for angle in self.constrained_angles:
            if any(atom.deleted for atom in angle):
                self.constrained_angle_table.removeRow(self.constrained_angles.index(angle))
                self.constrained_angles.remove(angle)

        for torsion in self.constrained_torsions:
            if any(atom.deleted for atom in torsion):
                self.constrained_torsion_table.removeRow(self.constrained_torsions.index(torsion))
                self.constrained_torsions.remove(torsion)


class LayerWidget(QWidget):
    something_changed = Signal()

    def __init__(self, settings, session, tab_text, parent=None):
        super().__init__(parent)

        self._session = session
        self.structure = None
        self.tab_text = tab_text

        self.layers = []

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.tab_close_clicked)
        self.tabs.tabCloseRequested.connect(lambda *args: self.something_changed.emit())
        layout.addWidget(self.tabs, 0, 0, 2, 1, Qt.AlignTop)

        set_layer_button = QPushButton("current %s selected" % tab_text)
        set_layer_button.clicked.connect(self.set_layer)
        layout.addWidget(set_layer_button, 0, 1, 1, 1, Qt.AlignBottom)

        add_layer_button = QPushButton("new %s" % tab_text)
        add_layer_button.clicked.connect(self.add_tab)
        layout.addWidget(add_layer_button, 1, 1, 1, 1, Qt.AlignTop)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)

        self.set_layer()

    def setStructure(self, structure):
        self.structure = structure
        self.tabs.clear()
        self.add_tab()
        self.set_layer(use_atoms=structure.atoms)

    def set_layer(self, *args, use_atoms=False):
        cur_ndx = self.tabs.currentIndex()
        if cur_ndx == -1:
            self.add_tab()
            return

        table = self.tabs.widget(cur_ndx).table
        table.setRowCount(0)
        self.layers[cur_ndx] = []

        if use_atoms:
            atoms = use_atoms
        else:
            atoms = selected_atoms(self._session)

        for atom in atoms:
            if atom.structure is self.structure:
                for i, layer in enumerate(self.layers):
                    if i == cur_ndx:
                        continue

                    other_layer_table = self.tabs.widget(i)
                    if other_layer_table is None:
                        continue
                    else:
                        other_layer_table = other_layer_table.table
                    for atom2 in layer[::-1]:
                        if atom is atom2:
                            ndx = layer.index(atom)
                            layer.pop(ndx)
                            other_layer_table.removeRow(ndx)

                row = table.rowCount()
                table.insertRow(row)

                atomspec = QTableWidgetItem()
                atomspec.setData(Qt.DisplayRole, atom.atomspec)
                table.setItem(row, 0, atomspec)

                self.layers[cur_ndx].append(atom)\

        self.something_changed.emit()

    def add_tab(self, *args):
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        table = QTableWidget()
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["atoms"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table, 0, 0, 3, 1, Qt.AlignTop)

        charge = QSpinBox()
        charge.setRange(-5, 5)
        charge.valueChanged.connect(lambda *args: self.something_changed.emit())
        layout.addWidget(QLabel("charge:"), 0, 1, 1, 1, Qt.AlignLeft)
        layout.addWidget(charge, 0, 2, 1, 1, Qt.AlignVCenter)

        multiplicity = QSpinBox()
        multiplicity.setRange(1, 3)
        multiplicity.valueChanged.connect(lambda *args: self.something_changed.emit())
        layout.addWidget(QLabel("multiplicity:"), 1, 1, 1, 1, Qt.AlignLeft)
        layout.addWidget(multiplicity, 1, 2, 1, 1, Qt.AlignTop)

        layout.addWidget(QWidget(), 2, 1, 1, 1, Qt.AlignTop)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 0)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 0)
        layout.setRowStretch(2, 1)

        self.layers.append([])

        widget.table = table
        widget.charge = charge
        widget.multiplicity = multiplicity

        self.tabs.addTab(widget, "%s %i" % (self.tab_text, self.tabs.count() + 1))
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

        if self.structure is not None:
            atoms = []
            for atom in self.structure.atoms:
                if not any(atom in layer for layer in self.layers):
                    atoms.append(atom)

            self.set_layer(use_atoms=atoms)

        # we'll have an empty monomer when we first open the input builder
        # before the molecule is set
        # this empty monomer would stick around until it is removed
        while len(self.layers) > self.tabs.count():
            self.layers.pop(-1)

        self.something_changed.emit()

    def check_deleted_atoms(self, *args):
        for i, layer in enumerate(self.layers):
            table = self.tabs.widget(i)
            if table is None:
                continue
            table = table.table
            for atom in layer[::-1]:
                if atom.deleted:
                    table.removeRow(layer.index(atom))
                    layer.remove(atom)

    def tab_close_clicked(self, ndx):
        self.tabs.removeTab(ndx)
        self.layers.pop(ndx)
        for i in range(0, self.tabs.count()):
            self.tabs.setTabText(i, "%s %i" % (self.tab_text, i + 1))


class MethodOption(QWidget):
    #TODO: make checking the "is_semiempirical" box disable the basis functions tab of the parent tab widget
    #      dispersion names can be moved to EmpiricalDispersion

    methodChanged = Signal()

    def __init__(self, settings, session, init_form, parent=None):
        super().__init__(parent)

        self.settings = settings
        self.form = init_form

        layout = QGridLayout(self)
        margins = layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        layout.setContentsMargins(*new_margins)

        method_form = QWidget()
        func_form_layout = QFormLayout(method_form)
        margins = func_form_layout.contentsMargins()
        new_margins = (margins.left(), margins.top(), margins.right(), 0)
        func_form_layout.setContentsMargins(*new_margins)

        self.method_option = QComboBox()
        func_form_layout.addRow(self.method_option)

        keyword_label = QLabel("keyword:")

        self.method_kw = QLineEdit()
        self.method_kw.setPlaceholderText("filter methods")
        self.method_kw.setText(self.settings.previous_custom_func)
        self.method_kw.setClearButtonEnabled(True)

        func_form_layout.addRow(keyword_label, self.method_kw)

        semi_empirical_label = QLabel("basis set is integral:")
        semi_empirical_label.setToolTip("check if basis set is integral to the method (e.g. semi-empirical methods)")

        self.is_semiempirical = QCheckBox()
        self.is_semiempirical.stateChanged.connect(self.something_changed)
        self.is_semiempirical.setToolTip("check if basis set is integral to the method (e.g. semi-empirical methods)")

        func_form_layout.addRow(semi_empirical_label, self.is_semiempirical)

        sapt_widget = QWidget()
        sapt_layout = QFormLayout(sapt_widget)
        sapt_layout.setContentsMargins(0, 0, 0, 0)

        self.sapt_type = QComboBox()
        self.sapt_type.addItems(["standard", "F/I", "spin-flip", "charge-transfer"])
        self.sapt_type.currentIndexChanged.connect(self.something_changed)
        sapt_layout.addRow("SAPT type:", self.sapt_type)

        self.sapt_level = QComboBox()
        self.sapt_level.addItems(["0", "2", "2+", "2+(3)", "2+3"])
        self.sapt_level.currentIndexChanged.connect(self.something_changed)
        sapt_layout.addRow("SAPT order:", self.sapt_level)

        self.sapt_type.currentTextChanged.connect(lambda text, widget=self.sapt_level: widget.setEnabled(text != "spin-flip"))

        self.sapt_layers = LayerWidget(self.settings, session, "monomer")
        sapt_layout.addRow(self.sapt_layers)
        self.sapt_layers.something_changed.connect(self.something_changed)
        func_form_layout.addRow(sapt_widget)

        layout.addWidget(method_form, 0, 0, Qt.AlignTop)

        self.previously_used_table = QTableWidget()
        self.previously_used_table.setColumnCount(3)
        self.previously_used_table.setHorizontalHeaderLabels(["name", "needs basis set", "trash"])
        self.previously_used_table.setSelectionBehavior(self.previously_used_table.SelectRows)
        self.previously_used_table.setEditTriggers(self.previously_used_table.NoEditTriggers)
        self.previously_used_table.setSelectionMode(self.previously_used_table.SingleSelection)
        self.previously_used_table.setSortingEnabled(True)

        for name, basis_required in zip(self.settings.previous_functional_names, self.settings.previous_functional_needs_basis):
            row = self.previously_used_table.rowCount()
            self.add_previously_used(row, name, basis_required)

        self.previously_used_table.cellActivated.connect(lambda *args, s=self: MethodOption.remove_saved_func(s, *args))

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
        self.dispersion.setToolTip("Dispersion correction for DFT methods without built-in dispersion\n" + \
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

        self.other_options = [keyword_label, self.method_kw, semi_empirical_label, self.is_semiempirical, self.previously_used_table]

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 0)
        layout.setRowStretch(2, 1)
        layout.setContentsMargins(0, 0, 0, 0)

        self.method_option.currentTextChanged.connect(self.method_changed)
        self.method_option.currentTextChanged.connect(lambda text: sapt_widget.setVisible(text == "SAPT"))
        self.setOptions(self.form)
        self.setPreviousStuff()
        self.method_kw.textChanged.connect(self.apply_filter)

    def something_changed(self, *args, **kw):
        """called whenever something changes - emits methodChanged"""
        self.methodChanged.emit()

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
        trash_button.setToolTip("double click to remove from stored methods")
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

    def method_changed(self, text):
        """called whenever the method kw changes - emits methodChanged"""
        for option in self.other_options:
            option.setVisible(text == "other")

        self.methodChanged.emit()

    def apply_filter(self, text):
        """filter previous method table when the user types in the custom kw box"""
        #text = self.method_kw.text()
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

    def setOptions(self, file_info):
        """change options to what's available in the specified program"""
        current_func = self.getMethod(update_settings=False).name
        self.method_option.clear()
        cur_disp = self.dispersion.currentText()
        self.dispersion.clear()
        self.grid.clear()
        self.form = file_info
        self.method_option.addItems(file_info.methods)
        self.method_option.addItem("other")

        self.dispersion.addItem("None")
        if file_info.dispersion:
            self.dispersion.addItems(file_info.dispersion)

        self.grid.addItem("Default")
        if file_info.grids:
            self.grid.addItems(file_info.grids)

        ndx = self.method_option.findText(current_func, Qt.MatchExactly)
        if ndx == -1:
            ndx = self.method_option.count() - 1
            self.method_kw.setText(current_func)
        self.method_option.setCurrentIndex(ndx)

        ndx = self.dispersion.findText(cur_disp, Qt.MatchExactly)
        if ndx != -1:
            self.dispersion.setCurrentIndex(ndx)

        self.methodChanged.emit()

    def setPreviousStuff(self):
        """grabs the method options from the last time this tool was used and set
        the current options ot that"""
        func = self.settings.previous_method
        disp = self.settings.previous_dispersion
        grid = self.settings.previous_grid
        self.setMethod(func)
        self.setGrid(grid)
        self.setDispersion(disp)

        self.methodChanged.emit()

    def use_previous_from_table(self, row):
        """grabs the method info from the table of previously used options and
        sets the current method name to that"""
        if row >= 0:
            name = self.previously_used_table.item(row, 0).text()
            self.method_kw.setText(name)

            needs_basis = self.previously_used_table.item(row, 1).text()
            if needs_basis == "yes":
                self.is_semiempirical.setCheckState(Qt.Unchecked)
            else:
                self.is_semiempirical.setCheckState(Qt.Checked)

        self.methodChanged.emit()

    def getMethod(self, update_settings=True):
        """returns Method corresponding to current settings"""
        if not any(self.method_option.currentText() == x for x in ["other", "SAPT"]):
            method = self.method_option.currentText()
            #omega doesn't get decoded right
            if update_settings:
                self.settings.previous_method = method.replace('ω', 'w')

            if any(method.upper() == x.upper() for x in KNOWN_SEMI_EMPIRICAL):
                is_semiempirical = True
            else:
                is_semiempirical = False

            return Method(method, is_semiempirical=is_semiempirical)

        elif self.method_option.currentText() == "SAPT":

            if self.sapt_type.currentText() == "standard" or self.sapt_type.currentText() == "charge-transfer":
                method = "sapt"
            elif self.sapt_type.currentText() == "F/I":
                method = "fisapt"
            elif self.sapt_type.currentText() == "spin-flip":
                method = "sf-sapt"

            if method != "sf-sapt":
                sapt_level = self.sapt_level.currentText()
                method += sapt_level

            if self.sapt_type.currentText() == "charge-transfer":
                method += "%s-ct"

            if update_settings:
                self.settings.previous_method = method

            return SAPTMethod(method, is_semiempirical=False)

        elif self.method_option.currentText() == "other":
            if update_settings:
                self.settings.previous_method = "other"

            method = self.method_kw.text()
            if update_settings:
                self.settings.previous_custom_func = method

            is_semiempirical = self.is_semiempirical.checkState() == Qt.Checked

            if len(method) > 0:
                found_func = False
                for i in range(0, len(self.settings.previous_functional_names)):
                    if self.settings.previous_functional_names[i] == method and \
                        self.settings.previous_functional_needs_basis[i] != is_semiempirical:
                        found_func = True

                if not found_func:
                    #append doesn't seem to call __setattr__, so the setting doesn't get updated
                    if update_settings:
                        self.settings.previous_functional_names = self.settings.previous_functional_names + [method]
                        self.settings.previous_functional_needs_basis = self.settings.previous_functional_needs_basis + [not is_semiempirical]

                        row = self.previously_used_table.rowCount()
                        self.add_previously_used(row, method, not is_semiempirical)

            return Method(method, is_semiempirical=is_semiempirical)

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
        elif isinstance(grid, str):
            ndx = self.grid.findText(grid)
        else:
            ndx = self.grid.findText(grid.name)

        self.grid.setCurrentIndex(ndx)

    def setDispersion(self, dispersion):
        """sets dispersion to what's specified"""
        if dispersion is None:
            ndx = self.dispersion.findText("None")
        else:
            ndx = self.dispersion.findText(dispersion)

        self.dispersion.setCurrentIndex(ndx)

    def setMethod(self, func):
        """sets method option to match the given Method"""
        if isinstance(func, Method):
            test_value = func.name
        else:
            test_value = func

        if test_value in ["wB97X-D", "wB97X-D3"]:
            test_value = test_value.replace('w', 'ω')

        if self.form == "Gaussian" and test_value == "Gaussian's B3LYP":
            test_value = "B3LYP"

        ndx = self.method_option.findText(test_value, Qt.MatchExactly)
        if ndx < 0 and "sapt" not in test_value:
            ndx = self.method_option.findText("other", Qt.MatchExactly)
            if isinstance(func, Method):
                self.method_kw.setText(func.name)
                self.is_semiempirical.setChecked(func.is_semiempirical)
            else:
                self.method_kw.setText(func)
                self.is_semiempirical.setChecked(any(func == semi_func.upper() for semi_func in KNOWN_SEMI_EMPIRICAL))

        elif "sapt" in test_value:
            ndx = self.method_option.findText("SAPT", Qt.MatchExactly)
            m = QRegularExpression("(.*)sapt(.*)(-ct)")
            match = m.match(test_value)
            sapt_type = match.captured(1)
            sapt_level = match.captured(2)
            charge_transfer = match.captured(3)

            if sapt_type == "sf-":
                type_ndx = self.sapt_type.findText("spin-flip", Qt.MatchExactly)
            elif sapt_type == "fi":
                type_ndx = self.sapt_type.findText("F/I", Qt.MatchExactly)
            elif charge_transfer:
                type_ndx = self.sapt_type.findText("charge-transfer", Qt.MatchExactly)
            else:
                type_ndx = 0

            self.sapt_type.setCurrentIndex(type_ndx)

            if sapt_level is not None:
                level_ndx = self.sapt_level.findText(sapt_level, Qt.MatchExactly)
                self.sapt_level.setCurrentIndex(level_ndx)

        self.method_option.setCurrentIndex(ndx)


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

    basisChanged = Signal()

    name_setting = "previous_basis_names"
    path_setting = "previous_basis_paths"
    last_used = "last_basis"
    last_custom = "last_custom_basis_kw"
    last_custom_builtin = "last_custom_basis_builtin"
    last_custom_path = "last_basis_path"
    last_elements = "last_basis_elements"
    aux_setting = "last_basis_aux"
    info_attribute = "basis_sets"

    toolbox_name = "basis_toolbox"

    aux_available = True

    basis_class = Basis

    def __init__(self, parent, settings, init_form):
        self.parent = parent
        self.settings = settings
        self.form = init_form
        super().__init__(parent)

        self.layout = QGridLayout(self)

        self.basis_names = QWidget()
        self.basis_name_options = QFormLayout(self.basis_names)
        self.basis_name_options.setContentsMargins(0, 0, 0, 0)

        self.basis_option = QComboBox()
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

        self.custom_basis_kw = QLineEdit()
        self.custom_basis_kw.textChanged.connect(self.apply_filter)
        self.custom_basis_kw.textChanged.connect(self.update_tooltab)
        self.custom_basis_kw.setPlaceholderText("filter basis sets")
        self.custom_basis_kw.setClearButtonEnabled(True)
        keyword_label = QLabel("name:")
        self.basis_name_options.addRow(keyword_label, self.custom_basis_kw)

        self.aux_type = QComboBox()
        self.aux_type.currentIndexChanged.connect(lambda *args, s=self: self.parent.check_elements(s))
        self.aux_type.addItem("no")
        aux_label = QLabel("auxiliary:")
        self.basis_name_options.addRow(aux_label, self.aux_type)

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

        #this doesn't seem to do anything?
        self.layout.setColumnStretch(0, 0)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 0)
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(4, 1)

        self.setOptions(self.form)
        self.aux_type.currentIndexChanged.connect(self.basis_changed)

    def setOptions(self, file_info):
        """display options that are available in the specified program"""
        self.blockSignals(True)
        self.form = file_info
        basis = self.currentBasis()
        basis.elements = []
        aux = self.aux_type.currentText()
        self.basis_option.clear()

        self.basis_option.addItems(getattr(file_info, self.info_attribute))
        self.basis_option.addItem("other")
        
        if not file_info.aux_options and self.getAuxType() != "no":
            self.destruct()
            return
        elif self.aux_available:
            for opt in self.aux_options:
                opt.setVisible(bool(file_info.aux_options))
        else:
            for opt in self.aux_options:
                opt.setVisible(False)
        
        self.aux_type.clear()
        self.aux_type.addItem("no")
        if file_info.aux_options:
            self.aux_type.addItems(file_info.aux_options)

        self.setAux(aux)
        self.setBasis(basis.name)

        self.blockSignals(False)

    def open_file_dialog(self):
        """ask user to locate external basis file on their computer"""
        filename, _ = QFileDialog.getOpenFileName(filter=self.form.basis_file_filter)

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
            return True
        return False

    def getAuxType(self):
        """returns aux type"""
        return self.aux_type.currentText()


class ECPOption(BasisOption):
    label_text = "ECP:"
    name_setting = "previous_ecp_names"
    path_setting = "previous_ecp_paths"
    last_used = "last_ecp"
    last_custom = "last_custom_ecp_kw"
    last_custom_builtin = "last_custom_ecp_builtin"
    last_custom_path = "last_ecp_path"
    last_elements = "last_ecp_elements"
    info_attribute = "ecps"

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

    basisChanged = Signal()

    def __init__(self, settings, init_form, parent=None):
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

        else:
            new_basis.setBasis()

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
        new_basis = BasisOption(self, self.settings, self.form)
        new_basis.setToolBox(self.basis_toolbox)
        new_basis.setElements(self.elements)
        new_basis.basisChanged.connect(self.something_changed)
        if use_saved is None:
            use_saved = len(self.basis_options)
        if use_saved < len(self.settings.last_basis):
            #must set auxiliary before selected elements
            #otherwise elements will be deselected on non-auxiliary basis
            #if they are selected on a new auxiliary basis
            if self.form.aux_options:
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

        if basis_set:
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

    def setOptions(self, file_info):
        """changes the basis set options to display what's available for the specified program"""
        self.form = file_info
        # reverse basis options because some might delete themselves
        # like if auxiliary basis sets aren't available in the program
        # also need to set elements after settings the options b/c things get changed and that could cause elements
        # of other basis sets to be cleared
        for basis, elements in zip(self.basis_options[::-1], [basis.currentElements() for basis in self.basis_options[::-1]]):
            basis.setOptions(file_info)
            basis.setSelectedElements(elements)

        if not file_info.ecps:
            self.ecp_widget.setVisible(False)
            for ecp in self.ecp_options:
                self.remove_basis(ecp)
        else:
            self.ecp_widget.setVisible(True)
            for ecp in self.ecp_options:
                ecp.setOptions(file_info)

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


#these table subclasses let me overwrite the dropEvent
#so you can drag and drop things to add options
class CurrentKWTable(QTableWidget):
    def __init__(self, origin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin = origin

    def dropEvent(self, event):
        other_table = event.source()
        if not isinstance(other_table, QTableWidget):
            return

        for item in other_table.selectedItems():
            if item.column() != 0:
                continue

            kw = item.text()
            if hasattr(self.origin, "last_dict"):
                if kw not in self.origin.last_dict:
                    self.origin.last_dict[kw] = []
                    self.origin.add_item_to_current_kw_table(kw)

            elif hasattr(self.origin, "last_list"):
                if not any(kw == x for x in self.origin.last_list):
                    self.origin.last_list.append(kw)
                    self.origin.add_item_to_current_kw_table(kw)


class CurrentOptTable(QTableWidget):
    def __init__(self, origin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin = origin

    def dropEvent(self, event):
        other_table = event.source()
        if not isinstance(other_table, QTableWidget):
            return

        for item in other_table.selectedItems():
            if item.column() != 0:
                continue

            opt = item.text()
            if hasattr(self.origin, "last_dict"):
                self.origin.add_item_to_current_opt_table(opt)


class OneLayerKeyWordOption(QWidget):
    """
    widget for 'one-layer' options
    """
    #TODO:
    #* add option to not save (who wants to save a comment? some people might, but I don't)
    optionChanged = Signal()
    settingsChanged = Signal()

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

        self.current_kw_table = CurrentKWTable(self)
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

        self.previous_kw_table.setDragDropMode(QTableWidget.DragOnly)
        self.current_kw_table.setDragDropMode(QTableWidget.DropOnly)

        layout.addWidget(self.previous_kw_table, 0, 0)
        layout.addWidget(self.current_kw_table, 0, 1)
        layout.addWidget(new_kw_widget, 1, 0, 1, 2)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 0)
        layout.setContentsMargins(0, 0, 0, 0)

    def add_item_to_previous_kw_table(self, kw):
        """adds kw to the table 'previous keyword' table"""
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
        """removes row from 'previous keyword' table and items from the settings"""
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
        """adds kw to the 'current keyword' table"""
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
        """'add' button was clicked
        grab the text and add it to the table"""
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
        """row was clicked in the 'previous' table
        remove row or add the item to 'current' table as appropriate"""
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
        """row in 'current' table was clicked - remove row if it was
        the 'remove' column"""
        if column == 1:
            item = self.current_kw_table.item(row, 0)
            kw = item.text()
            self.last_list.remove(kw)

            self.current_kw_table.removeRow(row)

            self.optionChanged.emit()

    def edit_current_kw(self, row, column):
        """item in 'current' table was clicked
        allow editing if column is a keyword
        newlines are also replaced with newlines"""
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
        """refresh self.previous_list"""
        for item in self.last_list:
            if item not in self.previous_list:
                self.previous_list.append(item)

    def apply_kw_filter(self, text=None):
        """filter keywords based on what's typed in to the 'add' text box"""
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
        """changes settings to match kw_list"""
        self.clearCurrentSettings()

        self.last_list = kw_list.copy()

        for kw in self.last_list:
            self.add_item_to_current_kw_table(kw)

    def clearCurrentSettings(self):
        """remove all 'current' items"""
        self.last_list = []

        for i in range(self.current_kw_table.rowCount(), -1, -1):
            self.current_kw_table.removeRow(i)


class TwoLayerKeyWordOption(QWidget):
    """
    widget for 'two-layer' options, useful when there are specific keywords and values
    """
    optionChanged = Signal()
    settingsChanged = Signal()

    def __init__(
            self,
            name,
            last_dict,
            previous_dict,
            opt_fmt,
            one_opt_per_kw=False,
            parent=None,
            allow_dup=False
    ):
        """
        name                    - name of the left groupbox
        last_dict               - dict of 'last' setting corresponding to just the target position (i.e. route, blocks)
        previous_dict           - dict of 'previous' setting
        one_opt_per_kw          - bool; multiple options per keyword like in Gaussian route
                                    or just one like Psi4 settings
                                - function; function takes selected keyword and determines if that
                                    keyword can accept > 1 option
        opt_fmt                 - str; format when displaying options for selected keyword
        allow_dup               - bool; allow duplicate values in the option table
        """

        self.name = name
        self.last_dict = last_dict
        self.previous_dict = previous_dict
        self.one_opt_per_kw = one_opt_per_kw
        self.opt_fmt = opt_fmt
        self.allow_dup = allow_dup

        super().__init__(parent)

        layout = QGridLayout(self)

        self.keyword_groupbox = QGroupBox(self.name)
        self.keyword_groupbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        keyword_layout = QGridLayout(self.keyword_groupbox)
        keyword_layout.setContentsMargins(0, 0, 0, 0)
        keyword_layout.setRowStretch(0, 1)
        keyword_layout.setRowStretch(1, 0)

        self.previous_kw_table = QTableWidget()
        self.previous_kw_table.setColumnCount(2)
        self.previous_kw_table.setHorizontalHeaderLabels(['previous', 'trash'])
        self.previous_kw_table.cellActivated.connect(self.clicked_route_keyword)
        self.previous_kw_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.previous_kw_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.previous_kw_table.verticalHeader().setVisible(False)
        self.previous_kw_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        keyword_layout.addWidget(self.previous_kw_table, 0, 0)

        self.current_kw_table = CurrentKWTable(self)
        self.current_kw_table.setColumnCount(2)
        self.current_kw_table.setHorizontalHeaderLabels(['current', 'remove'])
        self.current_kw_table.setSelectionMode(QTableWidget.SingleSelection)
        self.current_kw_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.current_kw_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.current_kw_table.verticalHeader().setVisible(False)
        self.current_kw_table.cellClicked.connect(self.clicked_current_route_keyword)
        self.current_kw_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        keyword_layout.addWidget(self.current_kw_table, 0, 1)

        new_kw_widget = QWidget()
        new_kw_widgets_layout = QGridLayout(new_kw_widget)
        new_kw_widgets_layout.setContentsMargins(4, 2, 4, 2)
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
        new_kw_widgets_layout.setColumnStretch(0, 0)
        new_kw_widgets_layout.setColumnStretch(1, 1)
        new_kw_widgets_layout.setColumnStretch(2, 0)
        keyword_layout.addWidget(new_kw_widget, 1, 0, 1, 2)


        self.option_groupbox = QGroupBox("options")
        self.option_groupbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        option_layout = QGridLayout(self.option_groupbox)
        option_layout.setContentsMargins(0, 0, 0, 0)
        option_layout.setRowStretch(0, 1)
        option_layout.setRowStretch(1, 0)

        self.previous_opt_table = QTableWidget()
        self.previous_opt_table.setColumnCount(2)
        self.previous_opt_table.setHorizontalHeaderLabels(['previous', 'trash'])
        self.previous_opt_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.previous_opt_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.previous_opt_table.verticalHeader().setVisible(False)
        self.previous_opt_table.cellActivated.connect(self.clicked_keyword_option)
        self.previous_opt_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        option_layout.addWidget(self.previous_opt_table, 0, 0)

        self.current_opt_table = CurrentOptTable(self)
        self.current_opt_table.setColumnCount(2)
        self.current_opt_table.setHorizontalHeaderLabels(['current', 'remove'])
        self.current_opt_table.setEditTriggers(QTableWidget.DoubleClicked)
        self.current_opt_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.current_opt_table.cellClicked.connect(self.clicked_current_keyword_option)
        self.current_opt_table.cellChanged.connect(self.edit_current_opt)
        self.current_opt_table.verticalHeader().setVisible(False)
        self.current_opt_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        option_layout.addWidget(self.current_opt_table, 0, 1)

        new_opt_widget = QWidget()
        new_opt_widgets_layout = QGridLayout(new_opt_widget)
        new_opt_widgets_layout.setContentsMargins(4, 2, 4, 2)
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
        new_opt_widgets_layout.setColumnStretch(0, 0)
        new_opt_widgets_layout.setColumnStretch(1, 1)
        new_opt_widgets_layout.setColumnStretch(2, 0)
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

        self.previous_kw_table.setDragDropMode(QTableWidget.DragOnly)
        self.current_kw_table.setDragDropMode(QTableWidget.DropOnly)

        self.previous_opt_table.setDragDropMode(QTableWidget.DragOnly)
        self.current_opt_table.setDragDropMode(QTableWidget.DropOnly)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(True)
        splitter.addWidget(self.keyword_groupbox)
        splitter.addWidget(self.option_groupbox)
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(splitter, 0, 0)
        layout.setContentsMargins(0, 0, 0, 0)

    def add_item_to_previous_kw_table(self, kw):
        """adds kw to 'previous keyword' table"""
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
        """remove row from 'previous keyword' table"""
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
        """add kw to 'current keyword' table"""
        row = self.current_kw_table.rowCount()
        self.current_kw_table.insertRow(row)
        item = QTableWidgetItem(kw)
        self.current_kw_table.setItem(row, 0, item)

        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        trash_button = QLabel()
        dim = int(1.5*self.fontMetrics().boundingRect("Q").height())
        trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)).pixmap(dim, dim))
        if self.name.endswith('s'):
            trash_button.setToolTip("click to not use this %s" % self.name[:-1])
        else:
            trash_button.setToolTip("click to not use this %s" % self.name)
        widget_layout.addWidget(trash_button, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(2, 2, 2, 2)
        self.current_kw_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)

        self.current_kw_table.resizeRowToContents(row)
        self.current_kw_table.resizeColumnToContents(0)
        self.current_kw_table.resizeColumnToContents(1)

        self.current_kw_table.selectRow(row)

        self.optionChanged.emit()

    def add_item_to_previous_opt_table(self, opt):
        """add opt to 'previous option' table"""
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
        """
        remove row from 'previous option' table
        will also remove it from 'current option' table
        """
        item = self.previous_opt_table.item(row, 0)
        opt = item.text()
        self.previous_dict[self.selected_kw].remove(opt)

        current_opt = self.current_opt_table.findItems(opt, Qt.MatchExactly)
        for opt_item in current_opt:
            cur_row = opt_item.row()
            self.clicked_current_keyword_option(cur_row, 1)

        self.settingsChanged.emit()

        self.previous_opt_table.removeRow(row)

    def add_item_to_current_opt_table(self, opt, refreshing=False):
        """add opt to 'current option' table"""
        #prevent edit signal from triggering
        #it shouldn't break anything, but we don't need it
        self.current_opt_table.blockSignals(True)

        #check keywords to see if opt is already one of them
        #this is really just for psi4, as they are basically the only one to use
        #a '=' for the 'job' options
        #though gaussian may also use this for some route options, but it should still
        #be fine as you can't specify e.g. grid=99302 and grid=superfinegrid
        #if the keyword is already on the table, remove that item
        known_kw = [self.current_opt_table.item(row, 0).data(Qt.DisplayRole).split('=')[0] \
                    for row in range(0, self.current_opt_table.rowCount())]
        kw = opt.split('=')[0].strip()
        if kw in known_kw and not self.allow_dup:
            for row in range(self.current_opt_table.rowCount() - 1, -1, -1):
                if self.current_opt_table.item(row, 0).data(Qt.DisplayRole).startswith(kw):
                    self.current_opt_table.removeRow(row)

            remove = 0
            for i, item in enumerate(self.last_dict[self.selected_kw]):
                if item.startswith(kw):
                    remove = i

            del self.last_dict[self.selected_kw][remove]

        if not refreshing:
            if self.one_opt_per_kw is True or (
                    callable(self.one_opt_per_kw) and self.one_opt_per_kw(self.selected_kw)
            ):
                self.last_dict[self.selected_kw] = [opt]
                for i in range(self.current_opt_table.rowCount() - 1, -1, -1):
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
        """add button was clicked for keyword
        add the text to the table"""
        kw = self.new_kw.text()
        if len(kw.strip()) == 0:
            return

        if kw not in self.last_dict:
            self.last_dict[kw] = []

            self.add_item_to_current_kw_table(kw)

    def add_opt(self):
        """add button was clicked for options
        add text to 'current options' table"""
        opt = self.new_opt.text()
        if len(opt.strip()) == 0:
            return

        kw = self.selected_kw
        if kw is None:
            raise RuntimeWarning("no keyword selected")
            return

        if opt not in self.last_dict[kw] or self.allow_dup:
            self.add_item_to_current_opt_table(opt)

    def update_route_opts(self):
        """keyword was clicked - update the 'options' to show what's
        available/used for that keyword
        e.g. if freq was selected, but the selection changed to opt
        stop showing freq options and bring up opt options"""
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

        known_opts = []
        if keyword in self.previous_dict:
            for opt in self.previous_dict[keyword]:
                if opt not in known_opts:
                    self.add_item_to_previous_opt_table(opt)
                    known_opts.append(opt)

        if keyword in self.last_dict:
            for opt in self.last_dict[keyword]:
                self.add_item_to_current_opt_table(opt, refreshing=True)

        self.previous_opt_table.resizeColumnToContents(0)
        self.previous_opt_table.resizeColumnToContents(1)
        self.current_opt_table.resizeColumnToContents(0)
        self.current_opt_table.resizeColumnToContents(1)

    def clicked_route_keyword(self, row, column):
        """item in previous keyword table was clicked - remove if
        column was the delete column, otherwise add it to current keywords"""
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
        """item in current keyword table was clicked
        remove that item if column if the delete column"""
        if column == 1:
            item = self.current_kw_table.item(row, 0)
            kw = item.text()
            del self.last_dict[kw]

            self.current_kw_table.removeRow(row)

            if kw == self.selected_kw:
                self.update_route_opts()

            self.optionChanged.emit()

    def clicked_keyword_option(self, row, column):
        """item was clicked in previous option table
        remove the option of column was delete column
        otherwise add it to the current option table"""
        if column == 1:
            self.remove_previous_opt_row(row)
        elif column == 0:
            item = self.previous_opt_table.item(row, column)
            option = item.text()

            keyword = self.selected_kw

            if option in self.last_dict[keyword] and not self.allow_dup:
                return

            self.add_item_to_current_opt_table(option)

    def clicked_current_keyword_option(self, row, column):
        """current option table item was clicked
        remove the item if column was delete column"""
        if column == 1:
            item = self.current_opt_table.item(row, 0)
            opt = item.text()
            self.last_dict[self.selected_kw].remove(opt)

            self.current_opt_table.removeRow(row)

            self.optionChanged.emit()

    def edit_current_opt(self, row, column):
        """option was edited - update dict"""
        if column == 0:
            self.last_dict[self.selected_kw][row] = self.current_opt_table.item(row, column).text()
            self.optionChanged.emit()

    def refresh_previous(self):
        """add items in current settings to previous settings"""
        for item in self.last_dict.keys():
            if item not in self.previous_dict:
                self.previous_dict[item] = []

            for opt in self.last_dict[item]:
                if opt not in self.previous_dict[item]:
                    self.previous_dict[item].append(opt)

    def apply_kw_filter(self, text):
        """filter keywords based on what's in the keyword text box"""
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
        """filter options based on what's in the option text box"""
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
        """change current keywords and options to match kw_dict"""
        self.clearCurrentSettings()

        self.last_dict = kw_dict.copy()

        for kw in self.last_dict:
            self.add_item_to_current_kw_table(kw)

    def clearCurrentSettings(self):
        """remove all options and keywords from the 'current' tables"""
        self.last_dict = {}
        for i in range(self.current_opt_table.rowCount(), -1, -1):
            self.current_opt_table.removeRow(i)

        for i in range(self.current_kw_table.rowCount(), -1, -1):
            self.current_kw_table.removeRow(i)


class KeywordOptions(QWidget):
    """
    should be subclassed for program-specific options
    subclass should set the following attributes:
    items                       dict  - keys are the name of the settings section
                                        the keys are used to get the widgets during KeywordOptions.get_options_for
                                        the values should be the map to specify the
                                        location in the input file (e.g. AaronTools.theory.GAUSSIAN_ROUTE for route)

    old_items                   depracated
    previous_option_name        name of the'previous' setting
    last_option_name            name of the 'last' setting
    one_route_opt_per_kw        bool; whether the route accepts multiple settings for keywords (who does this?)
    route_opt_fmt               str; % style formating to convert two strings (e.g. %s=(%s))
    comment_opt_fmt             str; % style formating to convert two strings (e.g. %s=(%s))
    """
    optionsChanged = Signal()
    settingsChanged = Signal()

    items = dict()
    old_items = dict()
    previous_option_name = None
    last_option_name = None
    one_route_opt_per_kw = False
    one_link0_opt_per_kw = False
    route_opt_fmt = "%s %s"
    comment_opt_fmt = "%s %s"

    def __init__(self, info, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        previous_options = loads(self.settings.previous_options)
        if self.previous_option_name in previous_options:
            self.previous_dict = previous_options[self.previous_option_name]
        else:
            self.previous_dict = info.initial_options
        
        last_options = loads(self.settings.last_options)
        if self.last_option_name in last_options:
            self.last_dict = last_options[self.last_option_name]
        else:
            self.last_dict = dict()

        self.layout = QGridLayout(self)

        position_widget = QWidget()
        position_widget_layout = QFormLayout(position_widget)
        position_selector = QComboBox()
        position_selector.addItems([x for x in self.items.keys()])
        position_widget_layout.addRow("position:", position_selector)

        self.layout.addWidget(position_widget, 0, 0, 1, 1, Qt.AlignTop)

        self.widgets = {}
        for item in self.items.keys():
            if self.items[item] in self.last_dict:
                last = self.last_dict[self.items[item]]
            elif item in self.old_items and self.old_items[item] in self.last_dict:
                last = self.last_dict[self.old_items[item]]
            else:
                last = None

            if self.items[item] in self.previous_dict:
                previous = self.previous_dict[self.items[item]]
            elif item in self.old_items and self.old_items[item] in self.previous_dict:
                previous = self.previous_dict[self.old_items[item]]
            else:
                previous = None

            self.widgets[item] = self.get_options_for(item, last, previous)
            self.widgets[item].optionChanged.connect(self.something_changed)
            self.widgets[item].settingsChanged.connect(self.settings_changed)
            self.layout.addWidget(self.widgets[item], 1, 0)

        position_selector.currentTextChanged.connect(self.change_widget)
        self.change_widget(position_selector.currentText())

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setKeywords(self, current_dict):
        """sets all option widgets to match current_dict"""
        for item in self.widgets.keys():
            if self.items[item] in current_dict:
                self.widgets[item].setCurrentSettings(current_dict[self.items[item]])

            elif hasattr(self, "old_items") and item in self.old_items and self.old_items[item] in current_dict:
                self.widgets[item].setCurrentSettings(current_dict[self.old_items[item]])

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

        self.previous_dict = previous_dict
        self.last_dict = last_dict

        previous_dict = loads(self.settings.previous_options)
        last_dict = loads(self.settings.last_options)
        previous_dict[self.previous_option_name] = self.previous_dict
        last_dict[self.last_option_name] = self.last_dict

        self.settings.previous_options = dumps(previous_dict)
        self.settings.last_options = dumps(last_dict)
        self.settings.save()

    def change_widget(self, name):
        """show only the widget for 'name' settings"""
        for widget_name in self.widgets.keys():
            if name != widget_name:
                self.widgets[widget_name].setVisible(False)

            else:
                self.widgets[widget_name].setVisible(True)

    def getKWDict(self, update_settings=False):
        """returns a dict for things that are currently in option widgets
        keys are defined by the values in KeywordOptions.items"""
        last_dict = {}
        for item in self.widgets.keys():
            if isinstance(self.widgets[item], TwoLayerKeyWordOption):
                if not self.widgets[item].last_dict:
                    continue
                last_dict[self.items[item]] = self.widgets[item].last_dict
                if update_settings:
                    for kw in self.widgets[item].last_dict:
                        if kw not in self.widgets[item].previous_dict:
                            self.widgets[item].previous_dict[kw] = [x for x in self.widgets[item].last_dict[kw]]
                            self.widgets[item].add_item_to_previous_kw_table(kw)

                            if self.widgets[item].selected_kw == kw:
                                known_opts = []
                                for opt in self.widgets[item].previous_dict[kw]:
                                    if opt not in known_opts:
                                        self.widgets[item].add_item_to_previous_opt_table(opt)
                                        known_opts.append(opt)

                        else:
                            for opt in self.widgets[item].last_dict[kw]:
                                if opt not in self.widgets[item].previous_dict[kw]:
                                    self.widgets[item].previous_dict[kw].append(opt)

                                    if self.widgets[item].selected_kw == kw:
                                        self.widgets[item].add_item_to_previous_opt_table(opt)

            elif isinstance(self.widgets[item], OneLayerKeyWordOption):
                if not self.widgets[item].last_list:
                    continue
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


class KeywordWidget(QWidget):
    """widget shown on 'additional options' tab"""
    additionalOptionsChanged = Signal()

    def __init__(self, session, settings, init_form, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.form = init_form

        self.layout = QGridLayout(self)

        self.widgets = {}
        for form in session.seqcrow_qm_input_manager.formats:
            info = session.seqcrow_qm_input_manager.get_info(form)
            if info.keyword_options:
                self.widgets[form] = info.keyword_options(info, settings)
                self.widgets[form].optionsChanged.connect(self.options_changed)
            else:
                self.widgets[form] = QWidget()
            
            self.widgets[form].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout.addWidget(self.widgets[form], 0, 0)

        self.setOptions(init_form)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setOptions(self, file_info):
        self.form = file_info
        for form in self.widgets:
            if form != file_info.name:
                self.widgets[form].setVisible(False)
            else:
                self.widgets[form].setVisible(True)

    def options_changed(self):
        self.additionalOptionsChanged.emit()

    def setKeywords(self, current_dict):
        self.widgets[self.form.name].setKeywords(current_dict)

    def getKWDict(self, update_settings=False):
        for form in self.widgets:
            if self.form.name == form and self.form.keyword_options:
                last_dict = self.widgets[form].getKWDict(update_settings)
                if update_settings:
                    self.widgets[form].settings_changed()
                return last_dict


class InputPreview(ChildToolWindow):
    """window showing input file"""
    def __init__(self, tool_instance, title, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)

        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()

        self.preview = QTextBrowser()
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.preview.setFont(font)
        layout.addWidget(self.preview, 0, 0, 1, 3)

        #chimera toolwindows can have a statusbar, but the message goes away after a few seconds
        #I'll just use a Qt statusbar
        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        self.status.setStyleSheet("color: red")
        layout.addWidget(self.status, 1, 2, 1, 1)

        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon(refresh_button.style().standardIcon(QStyle.SP_BrowserReload)))
        refresh_button.clicked.connect(self.tool_instance.update_preview)
        layout.addWidget(refresh_button, 1, 0, 1, 1, Qt.AlignLeft)

        self.warning_button = QPushButton()
        self.warning_button.setIcon(QIcon(self.warning_button.style().standardIcon(QStyle.SP_MessageBoxWarning)))
        self.warning_button.clicked.connect(self.tool_instance.show_warnings)
        self.warning_button.setToolTip("click to view warnings in a separate window")
        layout.addWidget(self.warning_button, 1, 1, 1, 1, Qt.AlignLeft)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 0)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 1)

        self.ui_area.setLayout(layout)

        self.manage(None)

    def setPreview(self, text, warnings_list):
        """sets preview to 'text' and shows warnings in the status bar"""
        if isinstance(text, dict):
            s = ""
            for key, item in text.items():
                s += "<<- %s\n" % key
                s += item
                s += "%s\n\n\n" % key
            text = s
        self.preview.setText(text)
        if len(warnings_list) > 0:
            self.status.setVisible(True)
            self.warning_button.setVisible(True)
            self.status.showMessage("; ".join(warnings_list))
        else:
            self.status.setVisible(False)
            self.warning_button.setVisible(False)

    def cleanup(self):
        self.tool_instance.preview_window = None

        super().cleanup()


class WarningPreview(ChildToolWindow):
    def __init__(self, tool_instance, title, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)

        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()

        self.preview = QTextBrowser()
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.preview.setFont(font)
        layout.addWidget(self.preview, 0, 0, 1, 2)

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

    def setWarnings(self, warnings_list):
        """display the listed warnings"""
        if warnings_list:
            self.preview.setText("\n---------\n".join(warnings_list))
        else:
            self.preview.setText("looks fine")

    def cleanup(self):
        self.tool_instance.warning_window = None

        super().cleanup()


class SavePreset(ChildToolWindow):
    """window for selecting what to save in a preset"""
    class BasisElements(QWidget):
        """widget to select what elements belong in which basis"""
        def __init__(self, parent=None, tool_instance=None):
            super().__init__(parent)
            self.tool_instance = tool_instance

            layout = QGridLayout(self)
            self.basis_box = QTabWidget()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.basis_box)

            self.basis_ptables = []
            self.ecp_ptables = []

        def refresh_basis(self):
            basis_set = self.tool_instance.basis_widget.getBasis(update_settings=False)
            self.setBasis(basis_set)

        def setBasis(self, basis_set):
            """display current basis sets and element selectors"""
            self.basis_ptables = []
            self.ecp_ptables = []

            for i in range(self.basis_box.count()-1, -1, -1):
                #self.basis_box.removeItem(i)
                self.basis_box.removeTab(i)

            if basis_set.basis is not None:
                for basis in basis_set.basis:
                    element_selector = PeriodicTable(initial_elements=basis.elements)
                    self.basis_ptables.append(element_selector)
                    basis_name = basis.name
                    aux = basis.aux_type
                    if aux is not None:
                        label = "%s/%s" % (basis_name, aux)
                    else:
                        label = "%s" % basis_name

                    #self.basis_box.addItem(element_selector, label)
                    self.basis_box.addTab(element_selector, label)

            if basis_set.ecp is not None:
                for ecp in basis_set.ecp:
                    element_selector = PeriodicTable(initial_elements=ecp.elements)
                    self.ecp_ptables.append(element_selector)
                    label = "ECP: %s" % ecp.name

                    #self.basis_box.addItem(element_selector, label)
                    self.basis_box.addTab(element_selector, label)

        def getElements(self):
            basis_elements = []
            ecp_elements = []
            for selector in self.basis_ptables:
                basis_elements.append(selector.selectedElements(abbreviate=True))

            for ecp in self.ecp_ptables:
                ecp_elements.append(selector.selectedElements(abbreviate=True))

            return basis_elements, ecp_elements


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

        self.method = QCheckBox()
        self.method.setChecked(True)
        self.method.setToolTip("method")
        layout.addRow("method:", self.method)


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
            yes = QMessageBox.question(
                self.preset_name, "\"%s\" is already saved" % name,
                "would you like to overwrite \"%s\"?" % name,
                QMessageBox.Yes | QMessageBox.No
            )

            if yes != QMessageBox.Yes:
                return

        preset["use_job_type"] = self.job_type.checkState() == Qt.Checked

        preset["use_job_resources"] = self.job_resources.checkState() == Qt.Checked

        preset["use_solvent"] = self.solvent.checkState() == Qt.Checked

        preset["use_method"] = self.method.checkState() == Qt.Checked

        preset["use_basis"] = self.basis.checkState() == Qt.Checked

        preset["use_other"] = self.additional.checkState() == Qt.Checked
        
        self.tool_instance.update_theory(update_settings=True)
        preset["theory"] = self.tool_instance.theory

        self.tool_instance.presets[program][name] = preset

        self.tool_instance.refresh_presets()
        if self.tool_instance.remove_preset_window is not None:
            self.tool_instance.remove_preset_window.fill_tree()

        if self.tool_instance.export_preset_window is not None:
            self.tool_instance.export_preset_window.fill_tree()


        self.status.showMessage("saved \"%s\"" % name)

        #sometimes destroy causes an error
        #I haven't seen any pattern
        #self.destroy()

    def cleanup(self):
        self.tool_instance.preset_window = None

        super().cleanup()


class RemovePreset(ChildToolWindow):
    """window for deleting saved presets"""
    def __init__(self, tool_instance, title, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)

        self._build_ui()

    def _build_ui(self):

        layout = QGridLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["program", "trash"])
        self.fill_tree()
        self.tree.resizeColumnToContents(1)
        self.tree.setColumnWidth(0, 200)
        layout.addWidget(self.tree)

        self.ui_area.setLayout(layout)
        self.manage(None)

    def fill_tree(self):
        self.tree.clear()
        root = self.tree.invisibleRootItem()

        for program in self.tool_instance.presets:
            section = QTreeWidgetItem(root)
            section.setData(0, Qt.DisplayRole, program)
            for preset in self.tool_instance.presets[program]:
                preset_item = QTreeWidgetItem(section)
                preset_item.setData(0, Qt.DisplayRole, preset)
                
                remove_widget = QWidget()
                remove_layout = QGridLayout(remove_widget)
                remove = QPushButton()
                remove.setIcon(QIcon(remove_widget.style().standardIcon(QStyle.SP_DialogDiscardButton)))
                remove.setFlat(True)
                remove.clicked.connect(
                    lambda *args, name=preset, form=program, tool=self.tool_instance: tool.presets[form].pop(name)
                )
                remove.clicked.connect(self.tool_instance.refresh_presets)
                remove.clicked.connect(lambda *args, item=preset_item, parent=section: parent.removeChild(item))
                remove_layout.addWidget(remove, 0, 0, 1, 1, Qt.AlignLeft)
                remove_layout.setColumnStretch(0, 0)
                remove_layout.setContentsMargins(0, 0, 0, 0)
                self.tree.setItemWidget(preset_item, 1, remove_widget)

    def cleanup(self):
        self.tool_instance.remove_preset_window = None

        super().cleanup()


class PrepLocalJob(ChildToolWindow):
    """window for running a local job"""
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

        if not job_name.replace(' ', '').replace('-', '').replace('_','').isalnum():
            self.session.logger.error("invalid job name: '%s'\nmust be alphanumeric" % job_name)
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
    """window for saving presets to a file"""
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

        self.preset_sections = {}
        for program in self.tool_instance.presets:
            preset_section = QTreeWidgetItem(root)
            self.preset_sections[program] = preset_section
            preset_section.setData(0, Qt.DisplayRole, program)
            for preset in self.tool_instance.presets[program]:
                preset_item = QTreeWidgetItem(preset_section)
                preset_item.setData(0, Qt.DisplayRole, preset)
                preset_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                preset_item.setCheckState(1, Qt.Unchecked)

    def save_presets(self):
        filename, _ = QFileDialog.getSaveFileName(filter="JSON files (*.json);;INI files (*.ini)")
        if not filename:
            return

        if filename.lower().endswith("json"):
            out = {}

            for program in self.preset_sections:
                for i in range(0, self.preset_sections[program].childCount()):
                    if self.preset_sections[program].child(i).checkState(1) == Qt.Checked:
                        if program not in out:
                            out[program] = {}
                        
                        preset_name = self.preset_sections[program].child(i).data(0, Qt.DisplayRole)
                        out[program][preset_name] = self.tool_instance.presets[program][preset_name]

            with open(filename, "w") as f:
                dump(out, f, cls=ATEncoder, indent=4)

        elif filename.lower().endswith("ini"):
            out = ConfigParser()
            
            for program in self.preset_sections:
                for i in range(0, self.preset_sections[program].childCount()):
                    if self.preset_sections[program].child(i).checkState(1) == Qt.Checked:
                        preset_name = self.preset_sections[program].child(i).data(0, Qt.DisplayRole)
                        preset = self.tool_instance.presets[program][preset_name]
                        if not out.has_section(preset_name):
                            out.add_section(preset_name)
                        
                        self.fill_preset(out, preset, preset_name, program)

            with open(filename, "w") as f:
                out.write(f)

        else:
            self.tool_instance.session.logger("use json or ini extention")
            return

        self.tool_instance.session.logger.status("saved presets to %s" % filename)

        self.destroy()

    def fill_preset(self, config, preset, section, program):
        config.set(section, "exec_type", program.lower())

        if "opt" in preset:
            job_type = ""
            if preset["opt"]:
                job_type += "optimze"
                if preset["ts"]:
                    job_type += ".ts"

            if preset["freq"]:
                if preset["opt"]:
                    job_type += ", "
                job_type += "frequencies"
                config.set(section, "temperature", str(preset["temp"]))

            if preset["freq"] or preset["opt"]:
                config.set(section, "type", job_type)

        if "nproc" in preset:
            config.set(section, "processors", str(preset["nproc"]))
            config.set(section, "memory", str(preset["mem"]))

        if "solvent" in preset and preset["solvent model"]:
            config.set(section, "solvent", preset["solvent"] if preset["solvent"] else "gas")
            if preset["solvent"] and not preset["solvent"] == "gas":
                config.set(section, "solvent_model", preset["solvent model"])

        if "method" in preset:
            config.set(section, "method", preset["method"].replace('ω', 'w'))
            # TODO: semi-empirical
            if "disp" in preset and preset["disp"] is not None:
                config.set(section, "empirical_dispersion", preset["disp"])

            if "grid" in preset and preset["grid"] is not None:
                config.set(section, "grid", preset["grid"])

        elif "functional" in preset:
            config.set(section, "method", preset["functional"].replace('ω', 'w'))
            # TODO: semi-empirical
            if "disp" in preset and preset["disp"] is not None:
                config.set(section, "empirical_dispersion", preset["disp"])

            if "grid" in preset and preset["grid"] is not None:
                config.set(section, "grid", preset["grid"])

        if "basis" in preset and len(preset["basis"]["name"]) > 0:
            basis_str = ""
            for elements, aux, file, name in zip(preset["basis"]["elements"], \
                                                 preset["basis"]["auxiliary"], \
                                                 preset["basis"]["file"], \
                                                 preset["basis"]["name"] \
                                            ):

                if isinstance(elements, str):
                    basis_str += elements
                else:
                    basis_str += " ".join(elements)

                if aux is not None:
                    basis_str += " aux %s" % aux

                basis_str += " %s" % name

                if file:
                    if " " in file:
                        self.tool_instance.session.logger.warning("basis file path contains whitespace and cannot be saved to ini format: %s" % file)
                    else:
                        basis_str += " %s" % file

                basis_str += "\n"

            config.set(section, "basis", basis_str.strip())

        if "ecp" in preset and len(preset["ecp"]["name"]) > 0:
            basis_str = ""
            for elements, file, name in zip(preset["ecp"]["elements"], \
                                                 preset["ecp"]["file"], \
                                                 preset["ecp"]["name"], \
                                            ):

                if isinstance(elements, str):
                    basis_str += elements
                else:
                    basis_str += " ".join(elements)

                basis_str += " %s" % name

                if file:
                    if " " in file:
                        self.tool_instance.session.logger.warning("basis file path contains whitespace and cannot be saved to ini format: %s" % file)
                    else:
                        basis_str += " %s" % file

                basis_str += "\n"

            config.set(section, "ecp", basis_str.strip())

        if "other" in preset:
            for option, setting in preset["other"].items():
                if option.isdigit():
                    self.tool_instance.session.logger.error("preset \"%s\" uses an old format\nif you have any \"additional options\" set, re-save the preset, and try exporting again" % section)
                    break
                s = ""
                if isinstance(setting, dict):
                    for key, values in setting.items():
                        s += "%s %s\n" % (key, ", ".join(values))

                elif isinstance(setting, list):
                    s += "\n".join(setting)

                if len(s) > 0:
                    config.set(section, option, s)

    def cleanup(self):
        self.tool_instance.export_preset_window = None

        super().cleanup()
