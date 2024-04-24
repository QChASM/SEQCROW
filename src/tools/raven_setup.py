import inspect

import numpy as np

from jinja2 import Template
from json import loads, dumps

from chimerax.atomic import get_triggers
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.commands import run
from chimerax.core.settings import Settings
from chimerax.std_commands.coordset_gui import CoordinateSetSlider

from Qt.QtCore import Qt, QRegularExpression, Signal, QTime
from Qt.QtGui import (
    QKeySequence,
    QFontDatabase,
    QIcon,
    QPixmap,
    QDoubleValidator,
)
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
    QVBoxLayout,
)


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
)
from SEQCROW.jobs import LocalClusterJob
from SEQCROW.residue_collection import ResidueCollection, Residue
from SEQCROW.utils import iter2str
from SEQCROW.widgets.comboboxes import ModelComboBox
from SEQCROW.widgets.menu import FakeMenu
from SEQCROW.finders import AtomSpec
from SEQCROW.presets import seqcrow_bse


from AaronTools.const import ELEMENTS
from AaronTools.theory import *
from AaronTools.theory.method import KNOWN_SEMI_EMPIRICAL
from AaronTools.utils.utils import combine_dicts
from AaronTools.json_extension import ATDecoder, ATEncoder
from AaronTools.pathway import Pathway
from AaronTools.internal_coordinates import InternalCoordinateSet


# from cProfile import Profile


class _NoScrollComboBox(QComboBox):
    def wheelEvent(self, *args, **kwargs):
        pass


def ele_order(name):
    if name == "C":
        return 0
    try:
        return ELEMENTS.index(name)
    except KeyError:
        return len(ELEMENTS)


class _RavenSettings(Settings):
    AUTO_SAVE = {
        "stored_defaults": "{}",
    }


class BuildRaven(BuildQM, ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False

    def __init__(self, session, name):
        # p = Profile()
        # p.enable()
        
        ToolInstance.__init__(self, session, name)

        self.settings = _InputGeneratorSettings(
            session, "Build QM Input", version="3"
        )
        
        self.raven_settings = _RavenSettings(
            session, name,
        )
        
        self.tool_window = MainToolWindow(self)
        self.preview_window = None
        self.warning_window = None
        self.job_local_prep = None
        self.job_cluster_prep = None
        self.program = None
        self.templates = loads(self.settings.templates)

        self._build_ui()

        ndx = self.reactant_selector.currentIndex()
        if ndx != -1:
            self.change_reactant(ndx)
        ndx = self.product_selector.currentIndex()
        if ndx != -1:
            self.change_product(ndx)

        available_programs = []
        for algorithm in self.session.tss_finder_manager.formats:
            info = self.session.tss_finder_manager.get_info(algorithm)
            available_programs.extend(info.available_for)
        available_programs = set(available_programs)

        self.presets = dict()
        cached = loads(self.settings.presets, cls=ATDecoder)

        for file_format in session.seqcrow_qm_input_manager.formats:
            info = session.seqcrow_qm_input_manager.get_info(file_format)
            if not any(p == info.name for p in available_programs):
                continue
            if file_format not in cached:
                self.presets[file_format] = info.initial_presets
            else:
                self.presets[file_format] = cached[file_format]

        if self.settings.settings_version == 2:
            self.migrate_settings_from_v2()
            self.session.logger.warning("settings migrated from version 2")
            self.settings.settings_version = self.settings.settings_version + 1

        self.refresh_presets(save_presets=False)

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
        
        # p.disable()
        # p.print_stats()

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
        layout.setContentsMargins(0, 0, 0, 0)

        self._menu = FakeMenu()

        basics_form = QWidget()
        form_layout = QFormLayout(basics_form)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.tss_algorithm = QComboBox()
        self.tss_algorithm.addItems(
            self.session.tss_finder_manager.formats.keys()
        )
        
        form_layout.addRow("algorithm:", self.tss_algorithm)
        

        tss_info = self.session.tss_finder_manager.get_info(
            self.tss_algorithm.currentText()
        )

        self.file_type = QComboBox()
        for item in tss_info.available_for:
            info = self.session.seqcrow_qm_input_manager.get_info(
                item
            )
            self.file_type.addItem(item)

        self.tss_algorithm.currentTextChanged.connect(
            self.change_tss_algorithm
        )

        ndx = self.file_type.findText(init_form.name, Qt.MatchExactly)
        if ndx == -1:
            init_form = self.session.seqcrow_qm_input_manager.get_info(tss_info.available_for[0])
        if ndx >= 0:
            self.file_type.setCurrentIndex(ndx)
        self.file_type.currentIndexChanged.connect(self.change_file_type)

        form_layout.addRow("file type:", self.file_type)

        self.reactant_selector = ModelComboBox(self.session)
        form_layout.addRow("reactant:", self.reactant_selector)

        self.product_selector = ModelComboBox(self.session)
        form_layout.addRow("product:", self.product_selector)

        layout.addWidget(basics_form, 0, 0)

        self.job_widget = TSSWidget(
            self.raven_settings,
            self.settings,
            self.session,
            init_form,
            tss_info,
        )

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
        tabs.addTab(self.job_widget, "TS search options")
        tabs.addTab(self.method_widget, "method")
        tabs.addTab(self.basis_widget, "basis functions")
        tabs.addTab(self.other_keywords_widget, "additional options")

        # self.reactant_selector.blockSignals(True)
        # self.product_selector.blockSignals(True)
        self.reactant_selector.currentIndexChanged.connect(self.change_reactant)
        self.product_selector.currentIndexChanged.connect(self.change_product)

        layout.addWidget(tabs, 1, 0)
        self.tabs = tabs
        self.tabs.setTabEnabled(2, init_form.basis_sets is not None)

        #menu stuff
        export = self._menu.addMenu("Export")
        copy = QAction("Copy input to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_input)
        shortcut = QKeySequence(QKeySequence.Copy)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        self.copy = copy

        save = QAction("Save Input", self.tool_window.ui_area)
        save.triggered.connect(self.open_save_dialog)
        #this shortcut interferes with main window's save shortcut
        #I've tried different shortcut contexts to no avail
        #thanks Qt...
        #shortcut = QKeySequence(Qt.CTRL + Qt.Key_S)
        #save.setShortcut(shortcut)
        #save.setShortcutContext(Qt.WidgetShortcut)
        export.addAction(save)

        view = self._menu.addMenu("View")
        
        preview = QAction("Preview", self.tool_window.ui_area)
        preview.triggered.connect(self.show_preview)
        view.addAction(preview)

        warnings = QAction("Warnings", self.tool_window.ui_area)
        warnings.triggered.connect(self.show_warnings)
        view.addAction(warnings)
        
        show_lin_cart = QAction("Linear Cartesian path", self.tool_window.ui_area)
        show_lin_cart.triggered.connect(self.load_initial_path)
        view.addAction(show_lin_cart)

        show_lin_ic = QAction("Linear RIC path (experimental)", self.tool_window.ui_area)
        show_lin_ic.triggered.connect(self.load_initial_ric_path)
        view.addAction(show_lin_ic)
        
        queue = QAction("Queue", self.tool_window.ui_area)
        queue.triggered.connect(self.show_queue)
        view.addAction(queue)

        self.presets_menu = self._menu.addMenu("Presets")

        run_jobs = self._menu.addMenu("Run")
        locally = QAction("On this computer...", self.tool_window.ui_area)
        #remotely = QAction("R&emotely - coming eventually", self.tool_window.ui_area)
        locally.triggered.connect(self.show_local_job_prep)
        run_jobs.addAction(locally)
        #run_jobs.addAction(remotely)

        clusterly = QAction("Submit to local cluster...", self.tool_window.ui_area)
        #remotely = QAction("R&emotely - coming eventually", self.tool_window.ui_area)
        clusterly.triggered.connect(self.show_cluster_job_prep)
        run_jobs.addAction(clusterly)
        #run_jobs.addAction(remotely)

        layout.setMenuBar(self._menu)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def load_initial_path(self):
        """
        show the initial path to make sure the atoms are ordered correctly
        """
        reactant = self.reactant_selector.currentData()
        product = self.product_selector.currentData()
        if not reactant or not product:
            self.session.logger.warning("reactant or product not set")
            return 

        reactant = ResidueCollection(
            reactant,
            bonds_matter=True
        )
        reactant_ndx = self.job_widget.reactant_order()
        reactant.atoms = [reactant.atoms[i] for i in reactant_ndx]

        product = ResidueCollection(
            product,
            bonds_matter=True
        )
        product_ndx = self.job_widget.product_order()
        product.atoms = [product.atoms[i] for i in product_ndx]
        product.RMSD(reactant, align=True, sort=False)
        
        broken, formed = reactant.compare_connectivity(product, return_idx=True)
        
        if np.linalg.norm(reactant.coords - product.coords) < 1e-3:
            self.session.logger.error("reactant and product are the same")
            return
        
        path = Pathway([reactant.coords, product.coords])
        new_mol = reactant.get_chimera(self.session, discard_residues=True)
        new_mol.name = "linear cartesian interpolation"
        
        coordsets = np.zeros((51, len(reactant.atoms), 3))
        for i, t in enumerate(np.linspace(0, 1, num=51)):
            coordsets[i] = path.interpolate_coords(t)
        new_mol.add_coordsets(coordsets, replace=True)
        self.session.models.add([new_mol])
        seqcrow_bse(self.session, models=[new_mol])
        for (a1, a2) in [*broken, *formed]:
            run(
                self.session,
                "monitorBonds %s %s" % (
                    new_mol.atoms[a1].atomspec,
                    new_mol.atoms[a2].atomspec,
                ),
                log=False
            )
            
        css = CoordinateSetSlider(self.session, new_mol)
        css.play_cb()

    def load_initial_ric_path(self):
        """
        show the initial path to make sure the atoms are ordered correctly
        """
        reactant = self.reactant_selector.currentData()
        product = self.product_selector.currentData()
        if not reactant or not product:
            self.session.logger.warning("reactant or product not set")
            return 

        reactant = ResidueCollection(
            reactant,
            bonds_matter=True
        )
        reactant_ndx = self.job_widget.reactant_order()
        reactant.atoms = [reactant.atoms[i] for i in reactant_ndx]

        product = ResidueCollection(
            product,
            bonds_matter=True
        )
        product_ndx = self.job_widget.product_order()
        product.atoms = [product.atoms[i] for i in product_ndx]
        product.RMSD(reactant, align=True, sort=False)
        
        ric = InternalCoordinateSet(reactant, torsion_type="all")
        ric.determine_coordinates(product, torsion_type="all")

        if np.linalg.norm(reactant.coords - product.coords) < 1e-3:
            self.session.logger.error("reactant and product are the same")
            return
        
        new_mol = reactant.get_chimera(self.session, discard_residues=True)
        new_mol.name = "linear RIC interpolation"
        
        dq = ric.difference(reactant.coords, product.coords)
        n = 21
        coordsets = np.zeros((n, len(reactant.atoms), 3))
        for i, t in enumerate(np.linspace(0, 1, num=n)):
            if i == n - 1:
                reactant.coords = coordsets[i-1]
                product.RMSD(reactant, align=True, sort=False)
                coordsets[i] = product.coords
                break
            if i == 0:
                coordsets[i] = reactant.coords
                continue
            # if t <= 0.5:
            new_coords, err = ric.apply_change(
                reactant.coords,
                t * dq,
                debug=False,
            )
            # else:
            #     new_coords, err = ric.apply_change(
            #         product.coords,
            #         (1 - t * dq),
            #     )

            if err > 1e-3:
                target_dq = t * dq - ric.difference(reactant.coords, coordsets[i-1])
                B = ric.B_matrix(coordsets[i-1])
                B_inv = np.linalg.pinv(B)
                dx = np.matmul(B_inv, target_dq)
                new_coords = np.reshape(dx, (len(reactant.atoms), 3))
                new_coords += coordsets[i-1]

            # print(i, err)
            coordsets[i] = new_coords
            
        new_mol.add_coordsets(coordsets, replace=True)
        self.session.models.add([new_mol])
        seqcrow_bse(self.session, models=[new_mol])
        run(
            self.session,
            "monitorBonds %s guess True" % new_mol.atomspec,
            log=False
        )
            
        css = CoordinateSetSlider(self.session, new_mol, pause_frames=3)
        css.play_cb()

    def change_tss_algorithm(self, text):
        self.file_type.blockSignals(True)
        cur_file_type = self.file_type.currentText()
        self.file_type.clear()

        tss_info = self.session.tss_finder_manager.get_info(
            self.tss_algorithm.currentText()
        )

        self.file_type.addItems(tss_info.available_for)
        ndx = self.file_type.findText(cur_file_type, Qt.MatchExactly)
        if ndx >= 0:
            self.file_type.setCurrentIndex(ndx)

        self.job_widget.set_tss_method(tss_info)
        self.file_type.blockSignals(False)
        self.change_file_type()

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

    def change_product(self, index):
        if index == -1:
            self.basis_widget.setElements([])
            return

        product = self.product_selector.currentData()
        self.check_elements()

        if hasattr(product, "filereaders") and product.filereaders:
            fr = product.filereaders[-1]
            try:
                self.job_widget.setCharge(fr["charge"])
            except KeyError:
                pass
            try:
                self.job_widget.setMultiplicity(fr["multiplicity"])
            except KeyError:
                pass

    def change_reactant(self, index):
        if index == -1:
            self.basis_widget.setElements([])
            return 

        reactant = self.reactant_selector.currentData()
        self.check_elements()

        if reactant in self.session.filereader_manager.filereader_dict:
            for fr in self.session.filereader_manager.filereader_dict[reactant]:
                if 'charge' in fr.other:
                    self.job_widget.setCharge(fr.other['charge'])

                if 'multiplicity' in fr.other:
                    self.job_widget.setMultiplicity(fr.other['multiplicity'])

    def check_elements(self, *args, **kw):
        reactant = self.reactant_selector.currentData()
        product = self.product_selector.currentData()
        if reactant is not None and product is not None:
            self.job_widget.fill_atom_table(reactant, product)
            react_eles = dict()
            prod_eles = dict()
            if reactant.num_atoms != product.num_atoms:
                self.session.logger.warning(
                    "reactant and product don't have the same number of atoms:\n" +
                    "%s - %i\n" % (reactant.name, reactant.num_atoms) +
                    "%s - %i\n" % (product.name, product.num_atoms)
                )
            
            for a1, a2 in zip(reactant.atoms, product.atoms):
                if a1.element.name not in react_eles:
                    react_eles[a1.element.name] = 0
                if a2.element.name not in prod_eles:
                    prod_eles[a2.element.name] = 0
                react_eles[a1.element.name] += 1
                prod_eles[a2.element.name] += 1
    
            if react_eles != prod_eles:
                react_formula = "".join(
                    [
                        "%s<sub>%i</sub>" % (ele, num) if num > 1 else ele for (ele, num) in sorted(
                            react_eles.items(), key=lambda item: ele_order(item[0])
                        )
                    ]
                )
                prod_formula = "".join(
                    [
                        "%s<sub>%i</sub>" % (ele, num) if num > 1 else ele for (ele, num) in sorted(
                            prod_eles.items(), key=lambda item: ele_order(item[0])
                        )
                    ]
                )
                self.session.logger.warning(
                    "reactant and product don't have the same formula:<br>" +
                    "%s: %s<br>" % (reactant.name, react_formula) +
                    "%s: %s<br>" % (product.name, prod_formula),
                    is_html=True
                )

        if reactant is not None:
            elements = set(reactant.atoms.elements.names)
            self.basis_widget.setElements(elements)
            self.method_widget.sapt_layers.check_deleted_atoms()
    
    def get_file_contents(self, update_settings=False):
        self.update_theory(update_settings=update_settings)

        tss_algorithm = self.tss_algorithm.currentText()
        tss_info = self.session.tss_finder_manager.get_info(tss_algorithm)
        program = self.file_type.currentText()
        
        reactant = self.reactant_selector.currentData()
        product = self.product_selector.currentData()
        if not reactant or not product:
            return ""
        
        reactant = ResidueCollection(
            reactant,
            bonds_matter=False
        )
        reactant_ndx = self.job_widget.reactant_order()
        reactant.atoms = [reactant.atoms[i] for i in reactant_ndx]

        product = ResidueCollection(
            product,
            bonds_matter=False
        )
        product_ndx = self.job_widget.product_order()
        product.atoms = [product.atoms[i] for i in product_ndx]

        if tss_info.get_file_contents:
            if callable(tss_info.get_file_contents):
                kwargs = dict()
                sig = inspect.signature(tss_info.get_file_contents)
                defaults = loads(self.raven_settings.stored_defaults)
                for option, widget in self.job_widget.options.items():
                    defaults[option] = widget.value
                    if any(
                        param.name == option or
                        param.kind == param.VAR_KEYWORD
                        for param in sig.parameters.values()
                    ):
                        kwargs[option] = defaults[option]
                
                contents, warnings = tss_info.get_file_contents(
                    reactant,
                    product,
                    self.theory,
                    **kwargs,
                )
            
            else:
                kwargs = dict()
                sig = inspect.signature(tss_info.get_file_contents[program])
                defaults = loads(self.raven_settings.stored_defaults)
                for option, widget in self.job_widget.options.items():
                    defaults[option] = widget.value
                    if any(
                        param.name == option or
                        param.kind == param.VAR_KEYWORD
                        for param in sig.parameters.values()
                    ):
                        kwargs[option] = defaults[option]
                
                contents, warnings = tss_info.get_file_contents[program](
                    reactant,
                    product,
                    self.theory,
                    **kwargs,
                )
        
        else:
            contents, warnings = self.session.seqcrow_qm_input_manager.get_info(program).get_file_contents(
                self.theory,
            )
        
        return contents, warnings

    def update_preview(self):
        model = self.product_selector.currentData()
        if not model:
            return
        model = self.reactant_selector.currentData()
        if not model:
            return

        self.check_elements()
        if self.preview_window is not None or self.warning_window is not None:
            contents, warnings = self.get_file_contents(update_settings=False)
            if contents is not None and warnings is not None:
                if self.preview_window is not None:
                    self.preview_window.setPreview(contents, warnings)
                if self.warning_window is not None:
                    self.warning_window.setWarnings(warnings)

    def check_changes(self, trigger_name=None, changes=None):
        if changes is not None:
            reactant = self.reactant_selector.currentData()
            product = self.product_selector.currentData()
            if any(mdl in changes.modified_atomic_structures() for mdl in [reactant, product]):
                self.changed = True

    def apply_preset(self, program, preset_name):
        """apply preset named 'preset_name' for 'program'"""
        preset = self.presets[program][preset_name]

        ndx = self.file_type.findText(program, Qt.MatchExactly)
        if ndx < 0:
            self.session.logger.warning(
                "%s is not available for %s; change algorithms before applying this preset" % (
                    self.tss_algorithm.currentText(), program,
                )
            )
            return
        self.file_type.setCurrentIndex(ndx)

        self.file_type.blockSignals(True)
        self.method_widget.blockSignals(True)
        self.basis_widget.blockSignals(True)
        self.job_widget.blockSignals(True)
        self.other_keywords_widget.blockSignals(True)

        theory = preset["theory"].copy()

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
            if self.reactant_selector.currentData():
                rescol = ResidueCollection(
                    self.reactant_selector.currentData(), bonds_matter=False
                )
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

    def update_theory(self, update_settings=False):
        """grabs the current settings and updates self.theory
        always called before creating an input file"""
        program = self.file_type.currentText()
        file_info = self.session.seqcrow_qm_input_manager.get_info(program)

        rescol = ResidueCollection(self.reactant_selector.currentData(), bonds_matter=False)

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
            solvent=solvent,
            geometry=rescol,
            **combined_dict
        )

        tss_info = self.session.tss_finder_manager.get_info(
            self.tss_algorithm.currentText()
        )
        
        fixup_func = None
        if tss_info.fixup_theory:
            if callable(tss_info.fixup_theory):
                fixup_func = tss_info.fixup_theory
            else:
                fixup_func = tss_info.fixup_theory[program]

        kwargs = dict()
        defaults = loads(self.raven_settings.stored_defaults)
        for option, widget in self.job_widget.options.items():
            defaults[option] = widget.value
        self.raven_settings.stored_defaults = dumps(defaults)
            
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

    def close(self):
        """deregister trigger handlers"""
        #overload delete to de-register handler
        global_triggers = get_triggers()
        global_triggers.remove_handler(self._changes)
        global_triggers.remove_handler(self._changes_done)

        self.reactant_selector.deleteLater()
        self.product_selector.deleteLater()

        return ToolInstance.close(self)

    def delete(self):
        """deregister trigger handlers"""
        #overload delete to de-register handler
        global_triggers = get_triggers()
        global_triggers.remove_handler(self._changes)
        global_triggers.remove_handler(self._changes_done)

        self.reactant_selector.deleteLater()
        self.product_selector.deleteLater()

        return ToolInstance.delete(self)

    def struc_mod_update_preview(self, *args, **kwargs):
        """whenever a setting is changed, this should be called to update the preview"""
        if self.changed:
            self.update_preview()
            self.changed = False

    def open_save_dialog(self):
        """
        open a dialog to select the save file location
        """

        program = self.file_type.currentText()
        tss_algorithm = self.tss_algorithm.currentText()
        info = self.session.tss_finder_manager.get_info(tss_algorithm)
        if not info.save_file_filter:
            info = self.session.seqcrow_qm_input_manager.get_info(program)
        self.settings.last_program = program
        filename, _ = QFileDialog.getSaveFileName(filter=info.save_file_filter)

        if not filename:
            return
        
        self.save_file(filename)

    def run_cluster_job(
        self,
        memory,
        template_name,
        walltime,
        name="cluster_job",
        auto_update=False,
        auto_open=False,
        template_kwargs=None,
    ):
        """run job"""
        self.update_theory(update_settings=True)

        self.settings.last_program = self.file_type.currentText()

        restart = self.job_widget.restart.text()

        self.raven_settings.save()

        program = self.file_type.currentText()
        tss_info = self.tss_algorithm.currentText()
        queue_type = self.session.seqcrow_settings.settings.QUEUE_TYPE
        cluster_type = self.session.seqcrow_cluster_scheduling_software_manager.get_queue_manager(queue_type).get_template(program)()
        template = self.templates[queue_type][program][template_name]
 
        reactant = ResidueCollection(self.reactant_selector.currentData())
        reactant_ndx = self.job_widget.reactant_order()
        reactant.atoms = [reactant.atoms[i] for i in reactant_ndx]
        
        product = ResidueCollection(self.product_selector.currentData())
        product_ndx = self.job_widget.product_order()
        product.atoms = [product.atoms[i] for i in product_ndx]

        if program in self.session.seqcrow_job_manager.formats:
            job_cls = self.session.tss_finder_manager.get_info(tss_info).cluster_job_cls[program]

            defaults = loads(self.raven_settings.stored_defaults)
            for option, widget in self.job_widget.options.items():
                defaults[option] = widget.value
            self.raven_settings.stored_defaults = dumps(defaults)
                
            sig = inspect.signature(job_cls.__init__)
            algorithm_kwargs = dict()
            defaults = loads(self.raven_settings.stored_defaults)
            for option, widget in self.job_widget.options.items():
                defaults[option] = widget.value
                if any(
                    param.name == option or
                    param.kind == param.VAR_KEYWORD
                    for param in sig.parameters.values()
                ):
                    algorithm_kwargs[option] = defaults[option]
            self.raven_settings.stored_defaults = dumps(defaults)
        
            if restart and any(
                param.name == "restart" or 
                param.kind == param.VAR_KEYWORD
                for param in sig.parameters.values()
            ):
                algorithm_kwargs["restart"] = restart

            job = job_cls(
                name,
                self.session,
                self.theory,
                reactant,
                product,
                program,
                tss_info,
                algorithm_kwargs,
                queue_type=queue_type,
                template=template,
                template_kwargs=template_kwargs,
                processors=self.job_widget.getNProc(),
                memory=memory,
                auto_update=auto_update,
                auto_open=auto_open,
            )
    
            self.session.logger.status("adding %s to queue" % name)
    
            self.session.seqcrow_job_manager.add_job(job)
        else:
            raise NotImplementedError("no provider for running local %s jobs" % program)

        self.update_preview()
    
    def get_local_job_type(self):
        program = self.file_type.currentText()
        tss_info = self.tss_algorithm.currentText()

        if program in self.session.seqcrow_job_manager.formats:
            job_cls = self.session.tss_finder_manager.get_info(tss_info).local_job_cls[program]
        
        else:
            raise NotImplementedError("no provider for running local %s jobs" % program)
        
        return job_cls
    
    def run_local_job(
        self,
        *args,
        name="local_job",
        **job_kwargs,
    ):
        """run job"""
        self.update_theory(update_settings=True)

        self.settings.last_program = self.file_type.currentText()

        restart = self.job_widget.restart.text()

        self.raven_settings.save()

        reactant = ResidueCollection(self.reactant_selector.currentData())
        reactant_ndx = self.job_widget.reactant_order()
        reactant.atoms = [reactant.atoms[i] for i in reactant_ndx]
        
        product = ResidueCollection(self.product_selector.currentData())
        product_ndx = self.job_widget.product_order()
        product.atoms = [product.atoms[i] for i in product_ndx]

        program = self.file_type.currentText()
        tss_info = self.tss_algorithm.currentText()

        if program in self.session.seqcrow_job_manager.formats:
            job_cls = self.session.tss_finder_manager.get_info(tss_info).local_job_cls[program]
        
            sig = inspect.signature(job_cls.__init__)
            algorithm_kwargs = dict()
            defaults = loads(self.raven_settings.stored_defaults)
            for option, widget in self.job_widget.options.items():
                defaults[option] = widget.value
                if any(
                    param.name == option or
                    param.kind == param.VAR_KEYWORD
                    for param in sig.parameters.values()
                ):
                    algorithm_kwargs[option] = defaults[option]
            self.raven_settings.stored_defaults = dumps(defaults)
        
            if restart and any(
                param.name == "restart" or 
                param.kind == param.VAR_KEYWORD
                for param in sig.parameters.values()
            ):
                algorithm_kwargs["restart"] = restart
            else:
                algorithm_kwargs["restart"] = None

            job = job_cls(
                name,
                self.session,
                self.theory,
                reactant,
                product,
                program,
                algorithm_kwargs,
                **job_kwargs,
            )
    
            self.session.logger.status("adding %s to queue" % name)
    
            self.session.seqcrow_job_manager.add_job(job)
        else:
            raise NotImplementedError("no provider for running local %s jobs" % program)

        self.update_preview()


class TSSWidget(QWidget):
    jobTypeChanged = Signal()

    def __init__(
        self,
        settings,
        job_settings,
        session,
        init_form,
        init_tss_method,
        parent=None,
    ):
        super().__init__(parent)
        self.structure = None
        self.settings = settings
        self.job_settings = job_settings
        self.form = init_form
        self.session = session
        
        self.layout = QGridLayout(self)
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs, 0, 0)
        
        job_form = QWidget()
        job_type_layout = QFormLayout(job_form)
        job_type_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)


        self.charge = QSpinBox()
        self.charge.setRange(-5, 5)
        self.charge.setSingleStep(1)
        self.charge.setValue(self.job_settings.previous_charge)
        self.charge.setToolTip(
            "net charge of the system"
        )
        self.charge.valueChanged.connect(self.something_changed)

        job_type_layout.addRow("charge:", self.charge)

        self.multiplicity = QSpinBox()
        self.multiplicity.setRange(1, 10)
        self.multiplicity.setSingleStep(1)
        self.multiplicity.setValue(self.job_settings.previous_mult)
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
        self.nprocs.setValue(self.job_settings.last_nproc)
        self.nprocs.valueChanged.connect(self.something_changed)
        job_type_layout.addRow("processors:", self.nprocs)

        self.mem = QSpinBox()
        self.mem.setRange(0, 512)
        self.mem.setSingleStep(2)
        self.mem.setSuffix(' GB')
        self.mem.setToolTip("set to 0 to not specify")
        self.mem.setValue(self.job_settings.last_mem)
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

        algorithm_widget = QWidget()
        self.algorithm_layout = QFormLayout(algorithm_widget)
        self.algorithm_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.tabs.addTab(algorithm_widget, "algorithm options")
        self.options = dict()
        self.set_tss_method(init_tss_method)


        solvent_widget = QWidget()
        solvent_layout = QFormLayout(solvent_widget)
        solvent_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.solvent_option = QComboBox()
        self.solvent_option.currentTextChanged.connect(self.change_solvent_model)
        solvent_layout.addRow("implicit solvent model:", self.solvent_option)

        self.solvent_name_label = QLabel("solvent:")
        self.solvent_name = QLineEdit()
        self.solvent_name.setText(self.job_settings.previous_solvent_name)
        self.solvent_name.textChanged.connect(self.filter_solvents)
        self.solvent_name.setClearButtonEnabled(True)
        solvent_layout.addRow(self.solvent_name_label, self.solvent_name)

        self.solvent_names = QListWidget()
        self.solvent_names.setSelectionMode(self.solvent_names.SingleSelection)
        self.solvent_names.itemSelectionChanged.connect(self.change_selected_solvent)
        self.solvent_names.itemDoubleClicked.connect(self.change_selected_solvent)

        solvent_layout.addRow(self.solvent_names)
        
        self.tabs.addTab(solvent_widget, "implicit solvent")

        atom_order = QWidget()
        atom_order_layout = QVBoxLayout(atom_order)

        self.atom_order_table = QTableWidget()
        self.atom_order_table.setColumnCount(2)
        self.atom_order_table.setHorizontalHeaderLabels(["reactant", "product"])
        self.atom_order_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.atom_order_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.atom_order_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.atom_order_table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        atom_order_layout.insertWidget(0, self.atom_order_table, 1)
        
        apply_consistent_order = QPushButton("use systematic ordering")
        apply_consistent_order.clicked.connect(self.canonical_reorder)
        # atom_order_layout.insertWidget(1, apply_consistent_order, 0)

        self.tabs.addTab(atom_order, "atom order")

        self.setOptions(self.form)

    def fill_atom_table(self, reactant, product):
        self.reactant = reactant
        self.product = product
        if not reactant or not product:
            return
        
        if len(reactant.atoms) != len(product.atoms):
            return
        
        reactant_order = [
            self.atom_order_table.cellWidget(i, 0).currentText() for i in range(
                0, self.atom_order_table.rowCount()
            )
        ]
        product_order = [
            self.atom_order_table.cellWidget(i, 1).currentText() for i in range(
                0, self.atom_order_table.rowCount()
            )
        ]
        self.atom_order_table.setRowCount(0)

        r_atomspecs = [atom.atomspec for atom in reactant.atoms]
        p_atomspecs = [atom.atomspec for atom in product.atoms]

        for atom1, atom2 in zip(reactant.atoms, product.atoms):
            row = self.atom_order_table.rowCount()
            
            self.atom_order_table.insertRow(row)
            r_combobox = _NoScrollComboBox()
            r_combobox.addItems(r_atomspecs)
            ndx = -1
            if row < len(reactant_order):
                ndx = r_combobox.findText(reactant_order[row])
            if ndx < 0:
                ndx = r_combobox.findText(atom1.atomspec)
            r_combobox.setCurrentIndex(ndx)
            self.atom_order_table.setCellWidget(row, 0, r_combobox)
            
            p_combobox = _NoScrollComboBox()
            p_combobox.addItems(p_atomspecs)
            ndx = -1
            if row < len(product_order):
                ndx = p_combobox.findText(product_order[row])
            if ndx < 0:
                ndx = p_combobox.findText(atom2.atomspec)
            p_combobox.setCurrentIndex(ndx)
            self.atom_order_table.setCellWidget(row, 1, p_combobox)

    def canonical_reorder(self):
        if not self.reactant or not self.product:
            self.session.logger.error("reactant or product not set")
        
        rescol = ResidueCollection(self.reactant)
        reactant_invar = set([a.get_neighbor_id() for a in rescol.atoms])
        ranks = rescol.canonical_rank(invariant=False)
        for i, rank in enumerate(ranks):
            combobox = self.atom_order_table.cellWidget(i, 0)
            combobox.setCurrentIndex(rank)
    
        rescol = ResidueCollection(self.product)
        product_invar = set([a.get_neighbor_id() for a in rescol.atoms])
        ranks = rescol.canonical_rank(invariant=False)
        for i, rank in enumerate(ranks):
            combobox = self.atom_order_table.cellWidget(i, 1)
            combobox.setCurrentIndex(rank)
    
        if reactant_invar != product_invar:
            self.session.logger.warning(
                "reactant and product do not have the same bonding pattern\n"
                "systematic ordering may not be the same for both"
            )
            self.session.logger.warning(
                "it is recommended that you add all bonds that are present in "
                "the reactant or product to both structures (even if they are "
                "unreasonable)"
            )
    
    def reactant_order(self):
        order = np.zeros(self.atom_order_table.rowCount(), dtype=int)
        for i in range(0, self.atom_order_table.rowCount()):
            combobox = self.atom_order_table.cellWidget(i, 0)
            order[i] = combobox.currentIndex()
        
        if len(order) != len(np.unique(order)):
            for i in order:
                ndx = np.where(order == i)
                if len(ndx) > 1:
                    atomspec = self.atom_order_table.cellWidget(ndx[0], 0).currentText()
                    self.session.logger.warning(
                            "reactant atom %s specified multiple times: %s" % (
                                atomspec, ", ".join(["%s" % n for n in (ndx + 1)])
                        )
                    )
            self.session.logger.error("some reactant atom has been specified multiple times")
        
        return order

    def product_order(self):
        order = np.zeros(self.atom_order_table.rowCount(), dtype=int)
        for i in range(0, self.atom_order_table.rowCount()):
            combobox = self.atom_order_table.cellWidget(i, 1)
            order[i] = combobox.currentIndex()
        
        if len(order) != len(np.unique(order)):
            for i in order:
                ndx = np.where(order == i)
                if len(ndx) > 1:
                    atomspec = self.atom_order_table.cellWidget(ndx[0], 1).currentText()
                    self.session.logger.warning(
                            "product atom %s specified multiple times: %s" % (
                                atomspec, ", ".join(["%s" % n for n in (ndx + 1)])
                        )
                    )
            self.session.logger.error("some product atom has been specified multiple times")
        
        return order
    
    def browse_restart(self):
        filename, _ = QFileDialog.getOpenFileName(
            filter=self.tss_info.restart_filter
        )

        if filename:
            self.restart.setText(filename)

    def setStructure(self, mdl):
        self.structure = mdl
    
    def setOptions(self, file_info):
        self.form = file_info
        self.solvent_option.clear()
        self.solvent_names.clear()
        self.solvent_option.addItems(["None"])
        
        if file_info.solvents is not None:
            self.solvent_option.addItems(list(file_info.solvents.keys()))
        if file_info.solvents:
            ndx = self.solvent_option.findText(self.job_settings.previous_solvent_model)
            if ndx >= 0:
                self.solvent_option.setCurrentIndex(ndx)
            if isinstance(file_info.solvents, dict) and self.solvent_option.currentText() in file_info.solvents:
                self.solvent_names.addItems(file_info.solvents[self.solvent_option.currentText()])
            else:
                self.solvent_names.addItems(file_info.solvents)
            self.solvent_name.setText(self.job_settings.previous_solvent_name)

        self.solvent_names.sortItems()
    
    def set_tss_method(self, tss_info):
        self.tss_info = tss_info
        self.restart.setEnabled(bool(tss_info.restart_filter))
        self.browse.setEnabled(bool(tss_info.restart_filter))
    
        self.options = dict()
        for i in range(0, self.algorithm_layout.rowCount()):
            self.algorithm_layout.removeRow(0)
        
        defaults = loads(self.settings.stored_defaults)
        
        for name, option in tss_info.options.items():
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

    def setSolventModel(self, value):
        """sets solvent model if model is available"""
        ndx = self.solvent_option.findText(value, Qt.MatchExactly)
        if ndx >= 0:
            self.solvent_option.setCurrentIndex(ndx)
    
    def getSolvent(self, update_settings):
        """returns ImplicitSolvent for the current solvent settings"""
        model = self.solvent_option.currentText()
        if model == "None":
            if update_settings:
                self.job_settings.previous_solvent_model = "None"
            return None

        solvent = self.solvent_name.text()

        if update_settings:
            self.job_settings.previous_solvent_model = model
            self.job_settings.previous_solvent_name = solvent

        return ImplicitSolvent(model, solvent)

    def setSolvent(self, solvent):
        """sets solvent to match the given ImplicitSolvent"""
        if isinstance(solvent, ImplicitSolvent):
            ndx = self.solvent_option.findText(solvent.solvent_model)
            if ndx >= 0:
                self.solvent_option.setCurrentIndex(ndx)
    
            self.solvent_name.setText(solvent.solvent)
        else:
            self.solvent_option.setCurrentIndex(0)

    def something_changed(self, *args, **kw):
        """called whenever a setting has changed to notify the main tool"""
        self.jobTypeChanged.emit()

    def setProcessors(self, value):
        self.nprocs.setValue(value)
    
    def setMemory(self, value):
        self.mem.setValue(value)

    def getCharge(self, update_settings=True):
        """returns charge"""
        charge = self.charge.value()
        if update_settings:
            self.job_settings.previous_charge = charge

        return charge

    def setCharge(self, charge):
        self.charge.setValue(charge)
    
    def setMultiplicity(self, mult):
        self.multiplicity.setValue(mult)

    def getMultiplicity(self, update_settings=True):
        """returns multiplicity"""
        mult = self.multiplicity.value()
        if update_settings:
            self.job_settings.previous_mult = mult

        return mult

    def getNProc(self, update_settings=False):
        """returns number of processors"""
        if update_settings:
            self.job_settings.last_nproc = self.nprocs.value()

        if self.nprocs.value() > 0:
            return self.nprocs.value()
        else:
            return None

    def getMem(self, update_settings=False):
        """returns memory"""
        if update_settings:
            self.job_settings.last_mem = self.mem.value()

        if self.mem.value() != 0:
            return self.mem.value()
        else:
            return None

    def getKWDict(self, update_settings=False):
        """returns dictiory specifying misc options for writing an input file"""
        if update_settings:
            self.job_settings.last_nproc = self.nprocs.value()
            self.job_settings.last_mem = self.mem.value()

        return self.form.get_job_kw_dict(
            False,
            False,
            False,
            False,
            False,
            False,
        )

