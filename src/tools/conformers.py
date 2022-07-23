import os.path
import re

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
    QMenuBar,
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
    

class ConformerTool(BuildQM):

    SESSION_ENDURING = False
    SESSION_SAVE = False

    def __init__(self, session, name):
        ToolInstance.__init__(self, session, name)

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
        if any(x == self.settings.last_program for x in self.session.conformer_search_manager.formats.keys()):
            init_form = self.session.conformer_search_manager.get_info(self.settings.last_program)
        else:
            init_form = self.session.conformer_search_manager.get_info(
                list(self.session.conformer_search_manager.formats.keys())[0]
            )

        layout = QGridLayout()

        basics_form = QWidget()
        form_layout = QFormLayout(basics_form)

        self.file_type = QComboBox()
        self.file_type.addItems(self.session.conformer_search_manager.formats.keys())
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
        tabs.addTab(self.job_widget, "job details")
        tabs.addTab(self.method_widget, "method")
        tabs.addTab(self.basis_widget, "basis functions")
        tabs.addTab(self.other_keywords_widget, "additional options")

        self.model_selector.currentIndexChanged.connect(self.change_model)

        layout.addWidget(tabs, 1, 0)
        self.tabs = tabs
        self.tabs.setTabEnabled(2, init_form.basis_sets is not None)

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
        save.triggered.connect(self.open_save_dialog)
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

        run = menu.addMenu("&Run")
        locally = QAction("&On this computer...", self.tool_window.ui_area)
        #remotely = QAction("R&emotely - coming eventually", self.tool_window.ui_area)
        locally.triggered.connect(self.show_local_job_prep)
        run.addAction(locally)
        #run.addAction(remotely)

        clusterly = QAction("&Submit to local cluster...", self.tool_window.ui_area)
        #remotely = QAction("R&emotely - coming eventually", self.tool_window.ui_area)
        clusterly.triggered.connect(self.show_cluster_job_prep)
        run.addAction(clusterly)
        #run.addAction(remotely)

        menu.setNativeMenuBar(False)

        self._menu = menu
        layout.setMenuBar(menu)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
        menu.setVisible(True)

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
        if file_info.basis_sets is None:
            self.tabs.setTabEnabled(2, False)
        else:
            self.tabs.setTabEnabled(2, True)
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
        program = self.file_type.currentText()
        file_info = self.session.conformer_search_manager.get_info(program)

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

    def get_file_contents(self, update_settings=False):
        self.update_theory(update_settings=update_settings)

        program = self.file_type.currentText()
        contents, warnings = self.session.conformer_search_manager.get_info(program).get_file_contents(self.theory)
        return contents, warnings


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
        job_form = QWidget()
        job_type_layout = QFormLayout(job_form)

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
        self.chk_file_path.setPlaceholderText(
            "{{ name }} will be replaced if file is saved"
        )
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

        self.job_type_opts.addTab(self.geom_opt, "constraints")

        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(True)
        splitter.addWidget(job_form)
        splitter.addWidget(self.job_type_opts)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        self.layout.addWidget(splitter)

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
        
        self.job_type_opts.setTabEnabled(1, bool(file_info.solvents))
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
    def __init__(self, session, settings, init_form, parent=None):
        QWidget.__init__(self, parent)
        self.settings = settings
        self.form = init_form

        self.layout = QGridLayout(self)

        self.widgets = {}
        for form in session.conformer_search_manager.formats:
            info = session.conformer_search_manager.get_info(form)
            if info.keyword_options:
                self.widgets[form] = info.keyword_options(info, settings)
                self.widgets[form].optionsChanged.connect(self.options_changed)
            else:
                self.widgets[form] = QWidget()
            
            self.widgets[form].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout.addWidget(self.widgets[form], 0, 0)

        self.setOptions(init_form)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
