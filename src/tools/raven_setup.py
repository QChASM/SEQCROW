from jinja2 import Template

from json import loads

from chimerax.atomic import get_triggers
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.commands import run
from chimerax.core.settings import Settings

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
from SEQCROW.widgets.periodic_table import PeriodicTable, ElementButton
from SEQCROW.widgets.comboboxes import ModelComboBox
from SEQCROW.finders import AtomSpec


from AaronTools.const import ELEMENTS
from AaronTools.theory import *
from AaronTools.theory.method import KNOWN_SEMI_EMPIRICAL
from AaronTools.utils.utils import combine_dicts
from AaronTools.json_extension import ATDecoder, ATEncoder


def ele_order(name):
    if name == "C":
        return 0
    try:
        return ELEMENTS.index(name)
    except KeyError:
        return len(ELEMENTS)


class _RavenSettings(Settings):
    AUTO_SAVE = {
        "grow_max_disp_tol": 2e-2,
        "grow_rms_disp_tol": 1.34e-2,
        "done_max_disp_tol": 2e-2,
        "done_rms_disp_tol": 1.34e-2,
        "nodes": 11,
        "kernel": "RBF",
        "stddev_cutoff": 1.5e-2,
        "length_param": 10,
    }


class BuildRaven(BuildQM, ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False

    def __init__(self, session, name):
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

        self.presets = dict()
        cached = loads(self.settings.presets, cls=ATDecoder)
        for file_format in session.seqcrow_qm_input_manager.formats:
            info = session.seqcrow_qm_input_manager.get_info(file_format)
            if not info.allow_raven:
                continue
            if file_format not in self.presets:
                self.presets[file_format] = info.initial_presets
            else:
                self.presets[file_format] = cached[file_format]

        if self.settings.settings_version == 2:
            self.migrate_settings_from_v2()
            self.session.logger.warning("settings migrated from version 2")
            self.settings.settings_version = self.settings.settings_version + 1

        self.refresh_presets()

        global_triggers = get_triggers()

        self.changed = False
        self._changes = global_triggers.add_handler("changes", self.check_changes)
        self._changes_done = global_triggers.add_handler(
            "changes done", self.struc_mod_update_preview
        )

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
        for item in self.session.seqcrow_qm_input_manager.formats:
            info = self.session.seqcrow_qm_input_manager.get_info(
                item
            )
            if not info.allow_raven:
                continue
            self.file_type.addItem(item)

        ndx = self.file_type.findText(init_form.name, Qt.MatchExactly)
        if ndx >= 0:
            self.file_type.setCurrentIndex(ndx)
        self.file_type.currentIndexChanged.connect(self.change_file_type)

        form_layout.addRow("file type:", self.file_type)

        self.reactant_selector = ModelComboBox(self.session)
        form_layout.addRow("reactant:", self.reactant_selector)

        self.product_selector = ModelComboBox(self.session)
        form_layout.addRow("product:", self.product_selector)

        layout.addWidget(basics_form, 0, 0)

        self.job_widget = GSMWidget(
            self.raven_settings, self.settings, self.session, init_form
        )

        #method stuff
        self.method_widget = MethodOption(self.settings, self.session, init_form=init_form)
        self.method_widget.methodChanged.connect(self.update_preview)

        #basis set stuff
        self.basis_widget = BasisWidget(self.settings, init_form=init_form)
        self.basis_widget.basisChanged.connect(self.update_preview)

        #solvent
        self.solvent_widget = SolventWidget(self.settings, init_form=init_form)
        self.solvent_widget.solventChanged.connect(self.update_preview)

        #other keywords
        self.other_keywords_widget = KeywordWidget(self.session, self.settings, init_form=init_form)
        self.other_keywords_widget.additionalOptionsChanged.connect(self.update_preview)

        tabs = QTabWidget()
        tabs.addTab(self.job_widget, "TS search options")
        tabs.addTab(self.method_widget, "method")
        tabs.addTab(self.basis_widget, "basis functions")
        tabs.addTab(self.solvent_widget, "implicit solvent")
        tabs.addTab(self.other_keywords_widget, "additional options")

        self.reactant_selector.currentIndexChanged.connect(self.change_reactant)
        self.product_selector.currentIndexChanged.connect(self.change_product)

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

        self.presets_menu = menu.addMenu("Presets")

        run_jobs = menu.addMenu("&Run")
        locally = QAction("&On this computer...", self.tool_window.ui_area)
        #remotely = QAction("R&emotely - coming eventually", self.tool_window.ui_area)
        locally.triggered.connect(self.show_local_job_prep)
        run_jobs.addAction(locally)
        #run_jobs.addAction(remotely)

        clusterly = QAction("&Submit to local cluster...", self.tool_window.ui_area)
        #remotely = QAction("R&emotely - coming eventually", self.tool_window.ui_area)
        clusterly.triggered.connect(self.show_cluster_job_prep)
        run_jobs.addAction(clusterly)
        #run_jobs.addAction(remotely)

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
        self.solvent_widget.blockSignals(True)
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
        self.solvent_widget.setOptions(file_info)
        self.other_keywords_widget.setOptions(file_info)

        self.file_type.blockSignals(False)
        self.method_widget.blockSignals(False)
        self.solvent_widget.blockSignals(False)
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

        if product in self.session.filereader_manager.filereader_dict:
            for fr in self.session.filereader_manager.filereader_dict[product]:
                if 'charge' in fr.other:
                    self.job_widget.setCharge(fr.other['charge'])

                if 'multiplicity' in fr.other:
                    self.job_widget.setMultiplicity(fr.other['multiplicity'])

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

    def update_preview(self):
        model = self.product_selector.currentData()
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
            self.solvent_widget.setSolvent(theory.solvent)

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

        solvent = self.solvent_widget.getSolvent(update_settings)
        
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
            job_type="force",
            solvent=solvent,
            geometry=rescol,
            **combined_dict
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

        raven_kwargs = dict()
        raven_kwargs["n_nodes"] = self.job_widget.n_nodes.value()
        self.raven_settings.nodes = raven_kwargs["n_nodes"]
        raven_kwargs["kernel"] = self.job_widget.kernel.currentData(Qt.UserRole)
        self.raven_settings.kernel = raven_kwargs["kernel"]
        raven_kwargs["grow_rms_disp_tol"] = self.job_widget.grow_rms_disp_tol.value()
        self.raven_settings.grow_rms_disp_tol = raven_kwargs["grow_rms_disp_tol"]
        raven_kwargs["grow_max_disp_tol"] = self.job_widget.grow_max_disp_tol.value()
        self.raven_settings.grow_max_disp_tol = raven_kwargs["grow_max_disp_tol"]
        raven_kwargs["done_rms_disp_tol"] = self.job_widget.done_rms_disp_tol.value()
        self.raven_settings.done_rms_disp_tol = raven_kwargs["done_rms_disp_tol"]
        raven_kwargs["done_max_disp_tol"] = self.job_widget.done_max_disp_tol.value()
        self.raven_settings.done_max_disp_tol = raven_kwargs["done_max_disp_tol"]
        raven_kwargs["length_param"] = self.job_widget.length_param.value()
        self.raven_settings.length_param = raven_kwargs["length_param"]
        raven_kwargs["stddev_cutoff"] = self.job_widget.stddev_cutoff.value()
        self.raven_settings.stddev_cutoff = raven_kwargs["stddev_cutoff"]

        self.raven_settings.save()

        program = self.file_type.currentText()
        queue_type = self.session.seqcrow_settings.settings.QUEUE_TYPE
        cluster_type = self.session.seqcrow_cluster_scheduling_software_manager.get_queue_manager(queue_type).get_template(program)()
        template = self.templates[queue_type][program][template_name]
 
        reactant = ResidueCollection(self.reactant_selector.currentData())
        product = ResidueCollection(self.product_selector.currentData())

        program = self.file_type.currentText()
        if program in self.session.seqcrow_job_manager.formats:
            job_cls = self.session.seqcrow_job_manager.formats["ParallelRaven"].run_provider(
                self.session,
                "ParallelRaven",
                self.session.seqcrow_job_manager,
            )
            job = job_cls(
                name,
                self.session,
                self.theory,
                reactant,
                product,
                program,
                cluster_type,
                template=Template(template),
                template_kwargs=template_kwargs,
                processors=self.job_widget.getNProc(),
                memory=memory,
                auto_update=auto_update,
                auto_open=auto_open,
                **raven_kwargs,
            )
    
            self.session.logger.status("adding %s to queue" % name)
    
            self.session.seqcrow_job_manager.add_job(job)
        else:
            raise NotImplementedError("no provider for running local %s jobs" % program)

        self.update_preview()
    
    def run_local_job(
        self,
        *args,
        name="local_job",
        auto_update=False,
        auto_open=False,
    ):
        """run job"""
        self.update_theory(update_settings=True)

        self.settings.last_program = self.file_type.currentText()

        raven_kwargs = dict()
        raven_kwargs["n_nodes"] = self.job_widget.n_nodes.value()
        self.raven_settings.nodes = raven_kwargs["n_nodes"]
        raven_kwargs["kernel"] = self.job_widget.kernel.currentData(Qt.UserRole)
        self.raven_settings.kernel = raven_kwargs["kernel"]
        raven_kwargs["grow_rms_disp_tol"] = self.job_widget.grow_rms_disp_tol.value()
        self.raven_settings.grow_rms_disp_tol = raven_kwargs["grow_rms_disp_tol"]
        raven_kwargs["grow_max_disp_tol"] = self.job_widget.grow_max_disp_tol.value()
        self.raven_settings.grow_max_disp_tol = raven_kwargs["grow_max_disp_tol"]
        raven_kwargs["done_rms_disp_tol"] = self.job_widget.done_rms_disp_tol.value()
        self.raven_settings.done_rms_disp_tol = raven_kwargs["done_rms_disp_tol"]
        raven_kwargs["done_max_disp_tol"] = self.job_widget.done_max_disp_tol.value()
        self.raven_settings.done_max_disp_tol = raven_kwargs["done_max_disp_tol"]
        raven_kwargs["length_param"] = self.job_widget.length_param.value()
        self.raven_settings.length_param = raven_kwargs["length_param"]
        raven_kwargs["stddev_cutoff"] = self.job_widget.stddev_cutoff.value()
        self.raven_settings.stddev_cutoff = raven_kwargs["stddev_cutoff"]

        self.raven_settings.save()

        reactant = ResidueCollection(self.reactant_selector.currentData())
        product = ResidueCollection(self.product_selector.currentData())

        program = self.file_type.currentText()
        if program in self.session.seqcrow_job_manager.formats:
            job_cls = self.session.seqcrow_job_manager.formats["Raven"].run_provider(
                self.session,
                "Raven",
                self.session.seqcrow_job_manager,
            )
            job = job_cls(
                name,
                self.session,
                self.theory,
                reactant,
                product,
                program,
                auto_update=auto_update,
                auto_open=auto_open,
                **raven_kwargs,
            )
    
            self.session.logger.status("adding %s to queue" % name)
    
            self.session.seqcrow_job_manager.add_job(job)
        else:
            raise NotImplementedError("no provider for running local %s jobs" % program)

        self.update_preview()


class GSMWidget(QWidget):
    jobTypeChanged = Signal()

    def __init__(
        self,
        settings,
        job_settings,
        session,
        init_form,
        parent=None,
    ):
        super().__init__(parent)
        self.structure = None
        self.settings = settings
        self.job_settings = job_settings
        self.form = init_form
        
        self.layout = QGridLayout(self)
        tabs = QTabWidget()
        self.layout.addWidget(tabs, 0, 0)
        
        job_form = QWidget()
        job_type_layout = QFormLayout(job_form)


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

        tabs.addTab(job_form, "job details")


        string_options_widget = QWidget()
        string_options_layout = QFormLayout(string_options_widget)
        
        self.n_nodes = QSpinBox()
        self.n_nodes.setMaximum(101)
        self.n_nodes.setMinimum(6)
        self.n_nodes.setValue(self.settings.nodes)
        string_options_layout.addRow("number of nodes:", self.n_nodes)
        
        self.grow_max_disp_tol = QDoubleSpinBox()
        self.grow_max_disp_tol.setDecimals(4)
        self.grow_max_disp_tol.setMinimum(1e-4)
        self.grow_max_disp_tol.setMaximum(5e-2)
        self.grow_max_disp_tol.setSingleStep(1e-3)
        self.grow_max_disp_tol.setValue(self.settings.grow_max_disp_tol)
        self.grow_max_disp_tol.setToolTip(
            """maximum displacement tolerance for determining
        whether or not to add a node to the string"""
        )
        string_options_layout.addRow(
            "grow max. displacement tolerance:", self.grow_max_disp_tol,
        )

        self.grow_rms_disp_tol = QDoubleSpinBox()
        self.grow_rms_disp_tol.setDecimals(4)
        self.grow_rms_disp_tol.setMinimum(1e-4)
        self.grow_rms_disp_tol.setMaximum(5e-2)
        self.grow_rms_disp_tol.setSingleStep(1e-3)
        self.grow_rms_disp_tol.setValue(self.settings.grow_rms_disp_tol)
        self.grow_rms_disp_tol.setToolTip(
            """root mean squared displacement tolerance for
        determining whether or not to add a node to the string"""
        )
        string_options_layout.addRow(
            "grow RMS displacement tolerance:", self.grow_rms_disp_tol,
        )

        self.done_max_disp_tol = QDoubleSpinBox()
        self.done_max_disp_tol.setDecimals(4)
        self.done_max_disp_tol.setMinimum(1e-4)
        self.done_max_disp_tol.setMaximum(5e-2)
        self.done_max_disp_tol.setSingleStep(1e-3)
        self.done_max_disp_tol.setValue(self.settings.done_max_disp_tol)
        self.done_max_disp_tol.setToolTip(
            """maximum displacement tolerance for determining
        whether or not to finish optimizing the reaction path"""
        )
        string_options_layout.addRow(
            "done max. displacement tolerance:", self.done_max_disp_tol,
        )

        self.done_rms_disp_tol = QDoubleSpinBox()
        self.done_rms_disp_tol.setDecimals(4)
        self.done_rms_disp_tol.setMinimum(1e-4)
        self.done_rms_disp_tol.setMaximum(5e-2)
        self.done_rms_disp_tol.setSingleStep(1e-3)
        self.done_rms_disp_tol.setValue(self.settings.done_rms_disp_tol)
        self.done_rms_disp_tol.setToolTip(
            """root mean squared displacement tolerance for determining
        whether or not to finish optimizing the reaction path"""
        )
        string_options_layout.addRow(
            "done RMS displacement tolerance:", self.done_rms_disp_tol,
        )
        
        tabs.addTab(string_options_widget, "growing string options")
    
    
        gpr_options_widget = QWidget()
        gpr_options_layout = QFormLayout(gpr_options_widget)
        
        self.kernel = QComboBox()
        self.kernel.addItems([
            "radial basis function",
            "Matérn (ν=3/2)",
            "Matérn (ν=5/2)",
        ])
        self.kernel.setItemData(0, "RBF")
        self.kernel.setItemData(1, "Matern1.5")
        self.kernel.setItemData(2, "Matern2.5")
        ndx = self.kernel.findData(self.settings.kernel)
        if ndx >= 0:
            self.kernel.setCurrentIndex(ndx)
        gpr_options_layout.addRow("kernel:", self.kernel)
        
        self.length_param = QDoubleSpinBox()
        self.length_param.setMaximum(100)
        self.length_param.setMinimum(1)
        self.length_param.setSingleStep(0.5)
        self.length_param.setValue(self.settings.length_param)
        gpr_options_layout.addRow(
            "similarity falloff parameter:", self.length_param
        )
        
        self.stddev_cutoff = QDoubleSpinBox()
        self.stddev_cutoff.setMaximum(1)
        self.stddev_cutoff.setMinimum(0)
        self.stddev_cutoff.setDecimals(3)
        self.stddev_cutoff.setSingleStep(1e-3)
        self.stddev_cutoff.setValue(self.settings.stddev_cutoff)
        gpr_options_layout.addRow(
            "prediction certainty threshold:", self.stddev_cutoff
        )
        
        tabs.addTab(gpr_options_widget, "GPR options")
    
    def setStructure(self, mdl):
        self.structure = mdl
    
    def setOptions(self, file_info):
        pass
    
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


class SolventWidget(QWidget):
    solventChanged = Signal()

    def __init__(self, settings, init_form, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.form = init_form
        
        self.layout = QFormLayout(self)
        
        self.solvent_option = QComboBox()
        self.solvent_option.currentTextChanged.connect(self.change_solvent_model)
        self.layout.addRow("implicit solvent model:", self.solvent_option)

        self.solvent_name_label = QLabel("solvent:")
        self.solvent_name = QLineEdit()
        self.solvent_name.setText(self.settings.previous_solvent_name)
        self.solvent_name.textChanged.connect(self.filter_solvents)
        self.solvent_name.setClearButtonEnabled(True)
        self.layout.addRow(self.solvent_name_label, self.solvent_name)

        self.solvent_names = QListWidget()
        self.solvent_names.setSelectionMode(self.solvent_names.SingleSelection)
        self.solvent_names.itemSelectionChanged.connect(self.change_selected_solvent)
        self.solvent_names.itemDoubleClicked.connect(self.change_selected_solvent)

        self.layout.addRow(self.solvent_names)

        self.setOptions(self.form)

    def setOptions(self, file_info):
        self.form = file_info
        self.solvent_option.clear()
        self.solvent_names.clear()
        self.solvent_option.addItems(["None"])
        
        if file_info.solvent_models is not None:
            self.solvent_option.addItems(file_info.solvent_models)
        if file_info.solvents:
            ndx = self.solvent_option.findText(self.settings.previous_solvent_model)
            if ndx >= 0:
                self.solvent_option.setCurrentIndex(ndx)
            if isinstance(file_info.solvents, dict) and self.solvent_option.currentText() in file_info.solvents:
                self.solvent_names.addItems(file_info.solvents[self.solvent_option.currentText()])
            else:
                self.solvent_names.addItems(file_info.solvents)
            self.solvent_name.setText(self.settings.previous_solvent_name)

        self.solvent_names.sortItems()

    def change_selected_solvent(self):
        """when a solvent is selected in the list, the solvent is set to that"""
        item = self.solvent_names.selectedItems()
        if len(item) == 1:
            name = item[0].text()
            self.solvent_name.setText(name)

        self.solventChanged.emit()

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

        self.solventChanged.emit()

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
            ndx = self.solvent_option.findText(solvent.solvent_model)
            if ndx >= 0:
                self.solvent_option.setCurrentIndex(ndx)
    
            self.solvent_name.setText(solvent.solvent)
        else:
            self.solvent_option.setCurrentIndex(0)