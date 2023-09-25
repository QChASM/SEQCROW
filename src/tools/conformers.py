import inspect

from jinja2 import Template

from chimerax.atomic import selected_atoms, selected_bonds, selected_pseudobonds, get_triggers
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import StringArg, BoolArg, ListOf, IntArg
from chimerax.core.commands import run

from json import dumps, loads, dump, load

from configparser import ConfigParser

from Qt.QtCore import Qt, QRegularExpression, Signal, QTime
from Qt.QtGui import QKeySequence, QFontDatabase, QIcon, QPixmap
from Qt.QtWidgets import (
    QCheckBox,
    QLabel,
    QGridLayout,
    QComboBox,
    QSplitter,
    QLineEdit,
    QSpinBox,
    QFileDialog,
    QAction,
    QApplication,
    QPushButton,
    QTabWidget,
    QWidget,
    QGroupBox,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QHeaderView,
    QTextBrowser,
    QStatusBar,
    QTextEdit,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QSizePolicy,
    QStyle,
)

from SEQCROW.jobs import LocalClusterJob
from SEQCROW.residue_collection import ResidueCollection, Residue
from SEQCROW.utils import iter2str
from SEQCROW.widgets.periodic_table import PeriodicTable, ElementButton
from SEQCROW.widgets.comboboxes import ModelComboBox
from SEQCROW.widgets.menu import FakeMenu
from SEQCROW.finders import AtomSpec
from SEQCROW.tools.input_generator import (
    _InputGeneratorSettings,
    BuildQM,
    MethodOption,
    BasisWidget,
    InputPreview,
    WarningPreview,
    PrepLocalJob,
    PrepClusterJob,
    NewTemplate,
    KeywordWidget,
    JobTypeOption,
)

from AaronTools.config import Config
from AaronTools.const import TMETAL, ELEMENTS
from AaronTools.theory import *
from AaronTools.theory.method import KNOWN_SEMI_EMPIRICAL
from AaronTools.utils.utils import combine_dicts
from AaronTools.json_extension import ATDecoder, ATEncoder


class _ConformerSettings(Settings):
    EXPLICIT_SAVE = {
        'last_nproc': Value(0, IntArg),
        'last_mem': Value(0, IntArg),
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
        'previous_method': Value("GFN2-xTB", StringArg),
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
        'queue_kwargs': Value(dumps({"queue": ["general", "batch", "all.q"]}), StringArg),
        'last_queue_kwargs': Value(dumps(dict()), StringArg),
        'templates': Value(dumps(dict()), StringArg),
        'last_template': Value(dumps(dict()), StringArg),
        'last_walltime': 4,
        'last_submit_memory': 4,
    }
    AUTO_SAVE = {
        "on_finished": Value("do nothing", StringArg),
        "stored_defaults": "{}",
    }
    

class ConformerTool(BuildQM):

    SESSION_ENDURING = False
    SESSION_SAVE = False

    manager_name = "conformer_search_manager"

    def __init__(self, session, name):
        ToolInstance.__init__(self, session, name)
        self.manager = getattr(session, self.manager_name)

        self.settings = _ConformerSettings(
            session, name
        )
        
        self.tool_window = MainToolWindow(self)
        self.preview_window = None
        self.warning_window = None
        self.job_local_prep = None
        self.job_cluster_prep = None
        self.program = None
        self.templates = loads(self.settings.templates)

        self._build_ui()
        
        ndx = self.model_selector.currentIndex()
        if ndx != -1:
            self.change_model(ndx)

        global_triggers = get_triggers()

        self.changed = False
        self._changes = global_triggers.add_handler("changes", self.check_changes)
        self._changes_done = global_triggers.add_handler(
            "changes done", self.struc_mod_update_preview
        )

        # this tool is big by default
        # unless the user has saved its position, make it small
        if name not in self.session.ui.settings.tool_positions['windows']:
            self.tool_window.shrink_to_fit()

    def _build_ui(self):
        if any(x == self.settings.last_program for x in self.manager.formats.keys()):
            init_form = self.manager.get_info(self.settings.last_program)
        else:
            init_form = self.manager.get_info(
                list(self.manager.formats.keys())[0]
            )

        layout = QGridLayout()

        basics_form = QWidget()
        form_layout = QFormLayout(basics_form)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.file_type = QComboBox()
        self.file_type.addItems(self.manager.formats.keys())
        ndx = self.file_type.findText(init_form.name, Qt.MatchExactly)
        if ndx >= 0:
            self.file_type.setCurrentIndex(ndx)
        self.file_type.currentIndexChanged.connect(self.change_file_type)

        form_layout.addRow("search tool:", self.file_type)

        self.model_selector = ModelComboBox(self.session)
        form_layout.addRow("structure:", self.model_selector)

        layout.addWidget(basics_form, 0, 0)

        #job type stuff
        self.job_widget = ConformerJob(self.settings, self.session, init_form=init_form)
        self.job_widget.jobTypeChanged.connect(self.update_preview)

        #method stuff
        self.method_widget = MethodOption(self.settings, self.session, init_form=init_form)
        self.method_widget.methodChanged.connect(self.update_preview)

        #basis set stuff
        self.basis_widget = BasisWidget(self.settings, init_form=init_form)
        self.basis_widget.basisChanged.connect(self.update_preview)

        #other keywords
        self.other_keywords_widget = ConformerKeywordWidget(self.session, self.settings, init_form=init_form)
        self.other_keywords_widget.additionalOptionsChanged.connect(self.update_preview)

        tabs = QTabWidget()
        tabs.addTab(self.job_widget, "conf. search options")
        tabs.addTab(self.method_widget, "method")
        tabs.addTab(self.basis_widget, "basis functions")
        tabs.addTab(self.other_keywords_widget, "additional options")

        self.model_selector.currentIndexChanged.connect(self.change_model)

        layout.addWidget(tabs, 1, 0)
        self.tabs = tabs
        self.tabs.setTabEnabled(2, init_form.basis_sets is not None)

        #menu stuff
        menu = FakeMenu()

        export = menu.addMenu("Export")
        copy = QAction("Copy input to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_input)
        shortcut = QKeySequence(QKeySequence.Copy)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        self.copy = copy

        save = QAction("Save Input", self.tool_window.ui_area)
        save.triggered.connect(self.open_save_dialog)
        export.addAction(save)

        view = menu.addMenu("View")
        
        preview = QAction("Preview", self.tool_window.ui_area)
        preview.triggered.connect(self.show_preview)
        view.addAction(preview)

        warnings = QAction("Warnings", self.tool_window.ui_area)
        warnings.triggered.connect(self.show_warnings)
        view.addAction(warnings)
        
        queue = QAction("Queue", self.tool_window.ui_area)
        queue.triggered.connect(self.show_queue)
        view.addAction(queue)

        run = menu.addMenu("Run")
        locally = QAction("On this computer...", self.tool_window.ui_area)
        #remotely = QAction("R&emotely - coming eventually", self.tool_window.ui_area)
        locally.triggered.connect(self.show_local_job_prep)
        run.addAction(locally)
        #run.addAction(remotely)

        clusterly = QAction("Submit to local cluster...", self.tool_window.ui_area)
        #remotely = QAction("R&emotely - coming eventually", self.tool_window.ui_area)
        clusterly.triggered.connect(self.show_cluster_job_prep)
        run.addAction(clusterly)
        #run.addAction(remotely)

        self._menu = menu
        layout.setMenuBar(menu)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def change_model(self, index):
        """changes model to the one selected in self.model_selector (index is basically ignored"""
        if index == -1:
            self.basis_widget.setElements([])
            return

        mdl = self.model_selector.currentData()

        self.job_widget.setStructure(mdl)
        self.check_elements()

        if hasattr(mdl, "filereaders") and mdl.filereaders:
            fr = mdl.filereaders[-1]
            try:
                self.job_widget.setCharge(fr["charge"])
            except KeyError:
                pass
            try:
                self.job_widget.setCharge(fr["multiplicity"])
            except KeyError:
                pass

    def update_theory(self, update_settings=False):
        """grabs the current settings and updates self.theory
        always called before creating an input file"""
        program = self.file_type.currentText()
        file_info = self.manager.get_info(program)

        rescol = ResidueCollection(self.model_selector.currentData(), bonds_matter=False)

        meth = self.method_widget.getMethod(update_settings)
        if file_info.basis_sets is not None:
            basis = self.get_basis_set(update_settings)
        else:
            basis = None

        dispersion = self.method_widget.getDispersion(update_settings)

        grid = self.method_widget.getGrid(update_settings)
        charge = self.job_widget.getCharge(update_settings)
        mult = self.job_widget.getMultiplicity(update_settings)
        nproc = self.job_widget.getNProc(update_settings)
        mem = self.job_widget.getMem(update_settings)
        jobs = self.job_widget.getJobs()

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

        fixup_func = None
        if file_info.fixup_theory:
            if callable(file_info.fixup_theory):
                fixup_func = file_info.fixup_theory
            else:
                fixup_func = file_info.fixup_theory[program]

        kwargs = dict()
        defaults = loads(self.settings.stored_defaults)
        for option, widget in self.job_widget.options.items():
            defaults[option] = widget.value
        self.settings.stored_defaults = dumps(defaults)
            
        if fixup_func:
            sig = inspect.signature(fixup_func)
            
            for param in sig.parameters.values():
                if param.name not in self.job_widget.options:
                    continue
                value = self.job_widget.options[param.name].get_value()
                kwargs[param.name] = value
            
            self.theory = fixup_func(
                self.theory,
                restart_file=self.job_widget.restart.text(),
                **kwargs,
            )


class ConformerJob(JobTypeOption):
    def __init__(self, settings, session, init_form, parent=None):
        QWidget.__init__(self, parent)
        self.settings = settings
        self.session = session
        self.form = init_form
        self.structure = None
        self.constrained_atoms = []
        self.constrained_bonds = []
        self.constrained_angles = []
        self.constrained_torsions = []

        self.layout = QGridLayout(self)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs, 0, 0)
        
        job_form = QWidget()
        job_type_layout = QFormLayout(job_form)
        job_type_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)


        self.charge = QSpinBox()
        self.charge.setRange(-5, 5)
        self.charge.setSingleStep(1)
        self.charge.setValue(self.settings.previous_charge)
        self.charge.setToolTip(
            "net charge of the system"
        )
        self.charge.valueChanged.connect(self.something_changed)

        job_type_layout.addRow("charge:", self.charge)

        self.multiplicity = QSpinBox()
        self.multiplicity.setRange(1, 10)
        self.multiplicity.setSingleStep(1)
        self.multiplicity.setValue(self.settings.previous_mult)
        self.multiplicity.setToolTip(
            "one plus the number of unpaired electrons\n"
            "e.g. a methylene radical would have a multiplicity of 2"
        )
        self.multiplicity.valueChanged.connect(self.something_changed)
        job_type_layout.addRow("multiplicity:", self.multiplicity)

        self.nprocs = QSpinBox()
        self.nprocs.setRange(0, 128)
        self.nprocs.setSingleStep(1)
        self.nprocs.setToolTip("set to 0 to not specify")
        self.nprocs.setValue(self.settings.last_nproc)
        self.nprocs.valueChanged.connect(self.something_changed)
        job_type_layout.addRow("processors:", self.nprocs)

        self.mem = QSpinBox()
        self.mem.setRange(0, 512)
        self.mem.setSingleStep(2)
        self.mem.setSuffix(' GB')
        self.mem.setToolTip("set to 0 to not specify")
        self.mem.setValue(self.settings.last_mem)
        self.mem.valueChanged.connect(self.something_changed)
        job_type_layout.addRow("memory:", self.mem)
        
        self.restart = QLineEdit()
        self.browse = QPushButton("browse...")
        self.browse.clicked.connect(self.browse_restart)
        restart_widget = QWidget()
        restart_layout = QHBoxLayout(restart_widget)
        restart_layout.setContentsMargins(0, 0, 4, 0)
        restart_layout.insertWidget(0, self.restart, 1)
        restart_layout.insertWidget(1, self.browse, 0)
        job_type_layout.addRow(
            "restart file:", restart_widget,
        )
        
        self.tabs.addTab(job_form, "job details")


        # algorithm-specific options
        algorithm_widget = QWidget()
        self.algorithm_layout = QFormLayout(algorithm_widget)
        self.algorithm_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.tabs.addTab(algorithm_widget, "algorithm options")
        self.options = dict()


        # implicit solvent
        solvent_widget = QWidget()
        solvent_layout = QGridLayout(solvent_widget)

        solvent_form = QWidget()
        solvent_form_layout = QFormLayout(solvent_form)
        solvent_form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

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

        self.tabs.addTab(solvent_widget, "solvent")


        self.geom_opt = QWidget()
        geom_opt_layout = QGridLayout(self.geom_opt)
        geom_opt_layout.setContentsMargins(0, 0, 0, 0)

        self.constraints_widget = QWidget()
        constraints_layout = QGridLayout(self.constraints_widget)

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

        constraints_layout.addWidget(constraints_viewer, 0, 0, 1, 2, Qt.AlignTop)

        constraints_layout.setRowStretch(0, 0)
        constraints_layout.setRowStretch(1, 1)
        constraints_layout.setContentsMargins(0, 0, 0, 0)

        self.constraints_widget.setEnabled(self.form.use_constraints)

        geom_opt_layout.addWidget(self.constraints_widget, 1, 0, Qt.AlignTop)
        geom_opt_layout.setRowStretch(0, 0)
        geom_opt_layout.setRowStretch(1, 1)

        self.tabs.addTab(self.geom_opt, "constraints")

        self.setOptions(self.form)

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

    def setOptions(self, file_info):
        """change all options to show the ones available for 'program'"""
        self.form = file_info
        self.solvent_option.clear()
        self.solvent_names.clear()
        self.solvent_option.addItems(["None"])
        self.nprocs.setEnabled(file_info.parallel)
        self.mem.setEnabled(file_info.memory)
        self.constraints_widget.setEnabled(file_info.use_constraints)

        if file_info.solvents is not None:
            self.solvent_option.addItems(list(file_info.solvents.keys()))

        if file_info.solvents:
            ndx = self.solvent_option.findText(self.settings.previous_solvent_model)
            if ndx >= 0:
                self.solvent_option.setCurrentIndex(ndx)
            if isinstance(file_info.solvents, dict) and self.solvent_option.currentText() in file_info.solvents:
                self.solvent_names.addItems(file_info.solvents[self.solvent_option.currentText()])
            else:
                self.solvent_names.addItems(file_info.solvents)
            self.solvent_name.setText(self.settings.previous_solvent_name)
        
        self.tabs.setTabEnabled(1, bool(file_info.solvents))
        self.restart.setEnabled(bool(file_info.restart_filter))
        self.browse.setEnabled(bool(file_info.restart_filter))

        self.solvent_names.sortItems()
        
        self.options = dict()
        for i in range(0, self.algorithm_layout.rowCount()):
            self.algorithm_layout.removeRow(0)
        
        defaults = loads(self.settings.stored_defaults)
        
        for name, option in file_info.options.items():
            cls = option[0]
            kwargs = option[1]
            if "callback" not in kwargs:
                kwargs["callback"] = None
            if "default" not in kwargs:
                kwargs["default"] = None
            if "name" not in kwargs:
                kwargs["name"] = name
            obj = cls(**kwargs)
            default_value = defaults.get(name, None)
            if default_value is not None and (
                not hasattr(obj, "values") or
                default_value in obj.values
            ):
                obj.set_value(default_value)
            self.algorithm_layout.addRow(
                "%s:" % kwargs["name"].replace("_", " "),
                obj.widget
            )
            self.options[name] = obj

    def set_algorithm_options(self, algorithm_dict):
        for key, value in algorithm_dict.items():
            try:
                self.options[key].set_value(value)
            except KeyError:
                continue
    
    def browse_restart(self):
        filename, _ = QFileDialog.getOpenFileName(
            filter=self.tss_info.restart_filter
        )

        if filename:
            self.restart.setText(filename)

    def getConstraints(self):
        """returns dictionary with contraints
        keys are:
            atoms
            bonds
            angles
            torsions"""

        return {
            'atoms': self.constrained_atoms,
            'bonds': self.constrained_bonds,
            'angles': self.constrained_angles,
            'torsions': self.constrained_torsions,
        }
    
    def getKWDict(self, update_settings=False):
        return dict()

    def getJobs(self):
        """returns list(JobType) for the current jobs"""
        job_types = []
        constraints = self.getConstraints()
        new_constraints = {}
        if self.form.use_constraints:
            if "atoms" in constraints:
                new_constraints["atoms"] = []
                for atom in constraints["atoms"]:
                    if atom.deleted:
                        continue
                    new_constraints["atoms"].append(AtomSpec(atom.atomspec))
    
                for key in ["bonds", "angles", "torsions"]:
                    if key in constraints:
                        if key in constraints:
                            new_constraints[key] = []
                            for constraint in constraints[key]:
                                for atom in constraint:
                                    if atom.deleted:
                                        break
                                
                                else:
                                    new_constraints[key].append(
                                        [AtomSpec(atom.atomspec) for atom in constraint]
                                    )

        constraints = new_constraints

        job_types.append(
            ConformerSearchJob(
                constraints=constraints
            )
        )

        return job_types


class ConformerKeywordWidget(KeywordWidget):
    manager_name = "conformer_search_manager"
