from chimerax.atomic import AtomicStructure
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import StringArg, BoolArg, ListOf
from chimerax.core.models import ADD_MODELS, REMOVE_MODELS

from PyQt5.Qt import QClipboard, QStyle, QIcon
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QKeySequence, QFontMetrics
from PyQt5.QtWidgets import QCheckBox, QLabel, QGridLayout, QComboBox, QSplitter, QFrame, QLineEdit, QSpinBox, QMenuBar, QFileDialog, QAction, QApplication, QPushButton, QTabWidget, QWidget, QGroupBox, QListWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QToolBox, QFormLayout

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.tools.theory_literature import LiteratureBrowser
from SEQCROW.theory import *
#TODO: rename tuple2str to iter2str
from SEQCROW.settings import tuple2str

class _InputGeneratorSettings(Settings):
    EXPLICIT_SAVE = {
        'previous_basis_names': Value([], ListOf(StringArg), tuple2str),
        'previous_basis_paths': Value([], ListOf(StringArg), tuple2str),        
        'previous_ecp_names': Value([], ListOf(StringArg), tuple2str),
        'previous_ecp_paths': Value([], ListOf(StringArg), tuple2str),
        'last_basis': Value(["def2-SVP"], ListOf(StringArg), tuple2str),
        'last_custom_basis_kw': Value([""], ListOf(StringArg), tuple2str), 
        'last_custom_basis_builtin': Value([""], ListOf(StringArg), tuple2str),  
        'last_basis_elements': Value([""], ListOf(StringArg), tuple2str),
        'last_basis_path': Value("", StringArg), 
        'last_ecp': Value([], ListOf(StringArg), tuple2str), 
        'last_custom_ecp_kw': Value([], ListOf(StringArg), tuple2str), 
        'last_custom_ecp_builtin': Value([], ListOf(StringArg), tuple2str), 
        'last_ecp_elements': Value([], ListOf(StringArg), tuple2str),
        'last_ecp_path': Value("", StringArg),
        'previous_functional': Value("", StringArg),
        'previous_custom_func': Value("", StringArg), 
        'previous_functional_names': Value([], ListOf(StringArg), tuple2str),
        'previous_functional_needs_basis': Value([], ListOf(StringArg), tuple2str),
        'previous_dispersion': Value("None", StringArg),
    }


class BuildQM(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         

    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.settings = _InputGeneratorSettings(session, name)
        
        self.display_name = "QM Input Generator"
        
        self.tool_window = MainToolWindow(self)        

        self._build_ui()

        self.models = []
        self.other_kw_dict = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}
        
        self.refresh_models()
        self.update_theory

        self._add_handler = self.session.triggers.add_handler(ADD_MODELS, self.refresh_models)
        self._remove_handler = self.session.triggers.add_handler(REMOVE_MODELS, self.refresh_models)

    def _build_ui(self):
        #build an interface with a dropdown menu to select software package
        #change from one software widget to another when the dropdown menu changes
        #TODO: move everything to do with the tabwidget into a different widget
        #TODO: add a presets tab to save/load presets to aaronrc or to seqcrow 
        #      so it can easily be used in other tools (like one that runs QM software)
        layout = QGridLayout()
        
        basics_form = QWidget()
        form_layout = QFormLayout(basics_form)
                
        self.file_type = QComboBox()
        self.file_type.addItems(['Gaussian'])
        #self.file_type.currentIndexChanged.connect(self.change_file_type)
        form_layout.addRow("file type:", self.file_type)
        
        self.model_selector = QComboBox()
        form_layout.addRow("structure:", self.model_selector)
        
        layout.addWidget(basics_form, 0, 0)
        
        #job type stuff
        job_type_area = QWidget()
        job_type_layout = QGridLayout(job_type_area)
        job_type_layout.addWidget(QLabel("job type:"), 0, 0)
        self.job_type = QComboBox()
        self.job_type.addItems(KNOWN_GAUSSIAN_JOB_TYPES)
        self.job_type.currentIndexChanged.connect(self.change_job_type)
        job_type_layout.addWidget(self.job_type, 0, 1)
        
        job_type_layout.setRowStretch(0, 1)
        
        #functional stuff
        self.functional_widget = FunctionalOption(self.settings, init_form=self.file_type.currentText())

        #basis set stuff
        self.basis_widget = BasisWidget(self.settings)
        
        tabs = QTabWidget()
        tabs.addTab(job_type_area, "job type")
        tabs.addTab(self.functional_widget, "functional")
        tabs.addTab(self.basis_widget, "basis functions")
        
        self.model_selector.currentIndexChanged.connect(self.change_model)

        layout.addWidget(tabs, 1, 0)
      
        #menu stuff
        menu = QMenuBar()
        
        export = menu.addMenu("&Export")
        copy = QAction("&Copy input to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_input)
        shortcut = QKeySequence(Qt.CTRL + Qt.Key_C)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        
        save = QAction("&Save Input", self.tool_window.ui_area)
        #save.triggered.connect(self.save_csv)
        #this shortcut interferes with main window's save shortcut
        #I've tried different shortcut contexts to no avail
        #thanks Qt...
        #shortcut = QKeySequence(Qt.CTRL + Qt.Key_S)
        #save.setShortcut(shortcut)
        #save.setShortcutContext(Qt.WidgetShortcut)
        export.addAction(save)
        
        menu.setNativeMenuBar(False)
        layout.setMenuBar(menu)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def refresh_models(self, *args, **kwargs):
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

    def update_theory(self):
        if self.model_selector.currentIndex() >= 0:
            model = self.models[self.model_selector.currentIndex()]
        else:
            model = None
 
        basis = self.get_basis_set()
        func = self.functional_widget.getFunctional()
        dispersion = self.functional_widget.getDispersion()

        self.settings.save()
        
        self.theory = Method(structure=model, charge=0, multiplicity=1, \
                             functional=func, basis=basis, empirical_dispersion=dispersion)

    def change_job_type(self):
        if self.file_type.currentText() == "Gaussian":
            if self.job_type.currentText() in KNOWN_GAUSSIAN_JOB_TYPES:
                self.other_kw_dict[Method.GAUSSIAN_ROUTE].append(GAUSSIAN_JOB_TYPE_KW[self.job_type.currentText()])
                self.other_kw_dict[Method.GAUSSIAN_ROUTE] = [option for option in self.other_kw_dict[Method.GAUSSIAN_ROUTE] \
                                                                    if option not in GAUSSIAN_JOB_TYPE_KW.items() or \
                                                                    option == GAUSSIAN_JOB_TYPE_KW[self.job_type.currentText()]]
                    
            else:  
                self.other_kw_dict[Method.GAUSSIAN_ROUTE].append(GAUSSIAN_JOB_TYPE_KW['single-point energy'])
                self.other_kw_dict[Method.GAUSSIAN_ROUTE] = [option for option in self.other_kw_dict[Method.GAUSSIAN_ROUTE] \
                                                                    if option not in GAUSSIAN_JOB_TYPE_KW.items() or \
                                                                    option == GAUSSIAN_JOB_TYPE_KW['single-point energy']]
    
    def change_model(self, index):
        if index == -1:
            self.basis_widget.setElements([])
            return
            
        mdl = self.model_selector.currentData()
        elements = set(mdl.atoms.elements.names)
        self.basis_widget.setElements(elements)
    
    def get_basis_set(self):
        basis, ecp = self.basis_widget.get_basis()
        
        return BasisSet(basis, ecp)

    def copy_input(self):
        self.update_theory()
        output, warnings = self.theory.write_gaussian_input({})
        print(output)
        
        print("warnings:")
        for warning in warnings:
            print(warning)

        app = QApplication.instance()
        clipboard = app.clipboard()
        clipboard.setText(output)
    
    def delete(self):
        #overload delete ro de-register handler
        self.session.triggers.remove_handler(self._add_handler)
        self.session.triggers.remove_handler(self._remove_handler)
        super().delete()  


class FunctionalOption(QWidget):
    #TODO: make checking the "is_semiemperical" box disable the basis functions tab of the parent tab widget
    GAUSSIAN_FUNCTIONALS = ["B3LYP", "M06", "M06-L", "M06-2X", "ωB97X-D", "B3PW91", "B97-D", "BP86", "PBE0", "PM6", "AM1"]
    GAUSSIAN_DISPERSION = ["Grimme D2", "Grimme D3", "Becke-Johnson damped Grimme D3", "Petersson-Frisch"]
    
    def __init__(self, settings, init_form, parent=None):
        super().__init__(parent)

        self.settings = settings
        self.form = init_form
        
        layout = QGridLayout(self)
        
        functional_form = QWidget()
        func_form_layout = QFormLayout(functional_form)
        
        self.functional_option = QComboBox()
        func_form_layout.addRow("functional:", self.functional_option)
        
        keyword_label = QLabel("keyword:")
        
        self.functional_kw = QLineEdit()
        self.functional_kw.setClearButtonEnabled(True)
        
        func_form_layout.addRow(keyword_label, self.functional_kw)
        
        semi_empirical_label = QLabel("basis set is integral:")
        semi_empirical_label.setToolTip("check if basis set is integral to the functional (e.g. semi-empirical methods)")
        
        self.is_semiemperical = QCheckBox()
        self.is_semiemperical.setToolTip("check if basis set is integral to the functional (e.g. semi-empirical methods)")

        func_form_layout.addRow(semi_empirical_label, self.is_semiemperical)

        layout.addWidget(functional_form, 0, 0, Qt.AlignTop)

        self.previously_used_table = QTableWidget()
        self.previously_used_table.setColumnCount(3)
        self.previously_used_table.setHorizontalHeaderLabels(["name", "needs basis set", "trash"])
        self.previously_used_table.setSelectionBehavior(self.previously_used_table.SelectRows)
        self.previously_used_table.setEditTriggers(self.previously_used_table.NoEditTriggers)
        self.previously_used_table.setSelectionMode(self.previously_used_table.SingleSelection)
        for i, (name, basis_required) in enumerate(zip(self.settings.previous_functional_names, self.settings.previous_functional_needs_basis)):
            row = self.previously_used_table.rowCount()
            self.add_previously_used(row, name, basis_required)

        self.previously_used_table.cellActivated.connect(lambda *args, s=self: FunctionalOption.remove_saved_func(s, *args))

        layout.addWidget(self.previously_used_table, 1, 0, Qt.AlignTop)

        dispersion_form = QWidget()
        disp_form_layout = QFormLayout(dispersion_form)

        self.dispersion = QComboBox()

        disp_form_layout.addRow("empirical dispersion:", self.dispersion)
        
        layout.addWidget(dispersion_form, 2, 0, Qt.AlignTop)
        
        self.other_options = [keyword_label, self.functional_kw, semi_empirical_label, self.is_semiemperical, self.previously_used_table]
        
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 0)
        layout.setRowStretch(2, 0)
        
        self.functional_option.currentTextChanged.connect(self.functional_changed)
        self.setOptions(self.form)
        self.setPreviousStuff()
        self.functional_kw.textChanged.connect(self.apply_filter)
        
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
        self.previously_used_table.setItem(row, 1, needs_basis)
        
        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        trash_button = QLabel()
        trash_button.setMaximumSize(16, 16)
        trash_button.setScaledContents(False)
        trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(16, 16))
        trash_button.setToolTip("double click to remove from stored functionals")
        widget_layout.addWidget(trash_button)
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
        for option in self.other_options:
            option.setVisible(text == "other")

    def apply_filter(self, text):
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
        self.functional_option.clear()
        self.dispersion.clear()
        self.form = program
        if program == "Gaussian":
            self.functional_option.addItems(self.GAUSSIAN_FUNCTIONALS)
            self.functional_option.addItem("other")
            
            self.dispersion.addItem("None")
            self.dispersion.addItems(self.GAUSSIAN_DISPERSION)

    def setPreviousStuff(self):
        func = self.settings.previous_functional
        disp = self.settings.previous_dispersion
        if self.form == "Gaussian":
            #update functional
            if func == "Gaussian's B3LYP":
                ndx = self.functional_option.findText("B3LYP", Qt.MatchExactly)
                self.functional_option.setCurrentIndex(ndx)
                
            elif func == "other":
                ndx = self.functional_option.findText("other", Qt.MatchExactly)
                self.functional_option.setCurrentIndex(ndx)
                self.functional_kw.setText(self.settings.previous_custom_func)
                
            elif func in self.GAUSSIAN_FUNCTIONALS:
                    ndx = self.functional_option.findText(func, Qt.MatchExactly)
                    self.functional_option.setCurrentIndex(ndx)
                    self.is_semiemperical.setCheckState(func in KNOWN_SEMI_EMPIRICAL)
            
            #omegas don't get decoded right
            elif func == "wB97X-D":
                ndx = self.functional_option.findText("ωB97X-D", Qt.MatchExactly)
                self.functional_option.setCurrentIndex(ndx)
    
            #update_dispersion
            if disp in self.GAUSSIAN_DISPERSION:
                ndx = self.dispersion.findText(disp, Qt.MatchExactly)
                self.dispersion.setCurrentIndex(ndx)
                
    def use_previous_from_table(self, row):
        """grabs the functional info from the table of previously used options and 
        sets the current functional name to that"""
        if row >= 0:
            name = self.previously_used_table.item(row, 0).text()
            self.functional_kw.setText(name)
            
            needs_basis = self.previously_used_table.item(row, 1).text()
            if needs_basis == "yes":
                self.is_semiemperical.setCheckState(Qt.Unchecked)
            else:
                self.is_semiemperical.setCheckState(Qt.Checked)            
                               
    def getFunctional(self):
        if self.form == "Gaussian":
            if self.functional_option.currentText() == "B3LYP":
                self.settings.previous_functional = "Gaussians's B3LYP"
                return Functional("Gaussians's B3LYP", False)
            
        if self.functional_option.currentText() != "other":
            functional = self.functional_option.currentText()
            #omega doesn't get decoded right
            self.settings.previous_functional = functional.replace('ω', 'w')
            
            if functional in KNOWN_SEMI_EMPIRICAL:
                is_semiemperical = True
            else:
                is_semiemperical = False
                
            return Functional(functional, is_semiemperical)
            
        else:
            self.settings.previous_functional = "other"
            functional = self.functional_kw.text()
            self.settings.previous_custom_func = functional
            
            is_semiemperical = self.is_semiemperical.checkState() == Qt.Checked
            
            if len(functional) > 0:
                found_func = False
                for i in range(0, len(self.settings.previous_functional_names)):
                    if self.settings.previous_functional_names[i] == functional and \
                        self.settings.previous_functional_needs_basis[i] != is_semiemperical:
                        found_func = True
                
                if not found_func:
                    #append doesn't seem to call __setattr__, so the setting doesn't get updated
                    self.settings.previous_functional_names = self.settings.previous_functional_names + [functional]
                    self.settings.previous_functional_needs_basis = self.settings.previous_functional_needs_basis + [not is_semiemperical]
                    row = self.previously_used_table.rowCount()
                    self.add_previously_used(row, functional, not is_semiemperical)

            return Functional(functional, is_semiemperical)

    def getDispersion(self):
        disp = self.dispersion.currentText()
        self.settings.previous_dispersion = disp
        if disp == 'None':
            dispersion = None
        else:
            dispersion = EmpiricalDispersion(disp)
            
        return dispersion   


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
    

    options = ["def2-SVP", "def2-TZVP", "aug-cc-pVDZ", "aug-cc-pVTZ", "6-311+G**", "SDD", "LANL2DZ", "other"]
    name_setting = "previous_basis_names"
    path_setting = "previous_basis_paths"
    last_used = "last_basis"
    last_custom = "last_custom_basis_kw"
    last_custom_builtin = "last_custom_basis_builtin"
    last_custom_path = "last_basis_path"
    last_elements = "last_basis_elements"
        
    toolbox_name = "basis_toolbox"
        
    def __init__(self, parent, settings):
        self.parent = parent
        self.settings = settings
        super().__init__(parent)

        self.layout = QGridLayout(self)
        
        self.basis_names = QWidget()
        self.basis_name_options = QFormLayout(self.basis_names)
        
        self.basis_option = QComboBox()
        self.basis_option.addItems(self.options)
        self.basis_option.currentIndexChanged.connect(self.basis_changed)
        self.basis_name_options.addRow(self.basis_option)

        self.elements = QListWidget()
        #make element list roughly as wide as two characters + a scroll bar
        #this keeps the widget as narrow as possible so it doesn't take up the entire screen
        scroll_width = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        self.elements.setMinimumWidth(scroll_width + int(1.5*self.fontMetrics().boundingRect("QQ").width()))
        self.elements.setMaximumHeight(int(6*self.fontMetrics().boundingRect("QQ").height()))
        self.elements.setSelectionMode(QListWidget.MultiSelection)
        self.elements.itemSelectionChanged.connect(lambda *args, s=self: self.parent.check_elements(s))
        self.layout.addWidget(self.elements, 0, 2, 2, 1, Qt.AlignTop)
        
        self.custom_basis_kw = QLineEdit()
        self.custom_basis_kw.textChanged.connect(self.apply_filter)
        self.custom_basis_kw.textChanged.connect(self.update_tooltab)
        self.custom_basis_kw.setClearButtonEnabled(True)
        
        keyword_label = QLabel("keyword:")
        self.basis_name_options.addRow(keyword_label, self.custom_basis_kw)

        self.is_builtin = QCheckBox()
            
        self.is_builtin.stateChanged.connect(self.show_gen_path)
        self.layout.addWidget(self.is_builtin, 1, 3, 1, 1, Qt.AlignTop)
    
        gen_path_label = QLabel("path to basis set file:")
        self.layout.addWidget(gen_path_label, 3, 0, 1, 1)
        
        is_builtin_label = QLabel("built-in:")
        self.basis_name_options.addRow(is_builtin_label, self.is_builtin)

        self.layout.addWidget(self.basis_names, 0, 0, 3, 2)
                
        self.path_to_basis_file = QLineEdit()
        self.layout.addWidget(self.path_to_basis_file, 3, 1, 1, 1, Qt.AlignTop)
        
        browse_button = QPushButton("browse...")
        browse_button.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(browse_button, 3, 2, 1, 1, Qt.AlignTop)
        
        #previously_used_label = QLabel("previously used:")
        #self.layout.addWidget(previously_used_label, 3, 0, 1, 1, Qt.AlignTop)
        
        self.previously_used_table = QTableWidget()
        self.previously_used_table.setColumnCount(3)
        self.previously_used_table.setHorizontalHeaderLabels(["name", "basis file", "trash"])
        self.previously_used_table.setSelectionBehavior(self.previously_used_table.SelectRows)
        self.previously_used_table.setEditTriggers(self.previously_used_table.NoEditTriggers)
        self.previously_used_table.setSelectionMode(self.previously_used_table.SingleSelection)
        self.custom_basis_rows = []
        for i, (name, path) in enumerate(zip(self.settings.__getattr__(self.name_setting), self.settings.__getattr__(self.path_setting))):
            row = self.previously_used_table.rowCount()
            self.add_previously_used(row, name, path, False)
        
        self.previously_used_table.resizeColumnToContents(0)
        self.previously_used_table.resizeColumnToContents(2)
        
        self.previously_used_table.cellActivated.connect(lambda *args, s=self: BasisOption.remove_saved_basis(s, *args))
        self.layout.addWidget(self.previously_used_table, 4, 0, 1, 3, Qt.AlignTop)
        
        self.custom_basis_options = [keyword_label, self.custom_basis_kw, is_builtin_label, self.is_builtin, self.previously_used_table]
        self.gen_options = [gen_path_label, self.path_to_basis_file, browse_button]
        
    def open_file_dialog(self):
        """ask user to locate external basis file on their computer"""
        filename, _ = QFileDialog.getOpenFileName(filter="Basis Set Files (*.gbs)")
        if filename:
            self.path_to_basis_file.setText(filename)

    def apply_filter(self, text):
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
    
    def setToolBox(self, toolbox):
        self.parent_toolbox = toolbox
    
    def update_tooltab(self):
        basis_name, _ = self.currentBasis()
        ndx = self.parent_toolbox.indexOf(self)
        if len(self.parent.basis_options) != 1 or len(self.parent.ecp_options) != 0:
            elements = "(%s)" % ", ".join(self.currentElements())
        else:
            elements = ""
                
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

        if basis != "other":
            return basis, False
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

            return basis, gen_path

    def add_previously_used(self, row, name, path, add_to_others=True):
        """add a basis set to the table of previously used options
        name            - name of basis set
        path            - path to external basis set file
        add_to_others   - also add the option to siblings (should be False when a new 
                            BasisOption is created in the BasisWidget to avoid duplicates)"""
        if add_to_others:
            self.parent.add_to_all_but(self, row, name, path)
        
        self.custom_basis_rows.append((name, path))
        self.previously_used_table.insertRow(row)
        
        basis = QTableWidgetItem()
        basis.setData(Qt.DisplayRole, name)
        basis.setToolTip("double click to use")
        self.previously_used_table.setItem(row, 0, basis)
        
        gbs_file = QTableWidgetItem()
        gbs_file.setData(Qt.DisplayRole, path)
        gbs_file.setToolTip("double click to use")
        self.previously_used_table.setItem(row, 1, gbs_file)
        
        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        trash_button = QLabel()
        trash_button.setMaximumSize(16, 16)
        trash_button.setScaledContents(False)
        trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(16, 16))
        trash_button.setToolTip("double click to remove from stored basis sets")
        widget_layout.addWidget(trash_button)
        self.previously_used_table.setCellWidget(row, 2, widget_that_lets_me_horizontally_align_an_icon)
        
        self.previously_used_table.resizeRowToContents(row)
        
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

    def setBasis(self, name, custom_kw="", builtin=""):
        ndx = self.basis_option.findData(name, Qt.MatchExactly)
        self.basis_option.setCurrentIndex(ndx)
        self.custom_basis_kw.setText(custom_kw)
        if len(builtin) > 0:
            self.is_builtin.setCheckState(Qt.Unchecked)
            self.path_to_basis_file.setText(builtin)
        else:
            self.is_builtin.setCheckState(Qt.Checked)
            self.path_to_basis_file.setText(self.settings.__getattr__(self.last_custom_path))

class ECPOption(BasisOption):
    options = ["SDD", "LANL2DZ", "other"]
    label_text = "ECP:"
    name_setting = "previous_ecp_names"
    path_setting = "previous_ecp_paths"
    last_used = "last_ecp"
    last_custom = "last_custom_ecp_kw"
    last_custom_builtin = "last_custom_ecp_builtin"
    last_custom_path = "last_ecp_path"
    last_elements = "last_ecp_elements"
    
    def __init__(self, parent, settings):
        super().__init__(parent, settings)

    def update_tooltab(self):
        basis_name, _ = self.currentBasis()
        elements = "(%s)" % ", ".join(self.currentElements())
        ndx = self.parent_toolbox.indexOf(self)
        
        self.parent_toolbox.setTabText(ndx, "%s %s" % (basis_name, elements))
  
  
class BasisWidget(QWidget):
    """widget to store and manage BasisOptions and ECPOptions"""
    def __init__(self, settings, parent=None):
        super().__init__(parent)
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
        valence_layout.addWidget(self.basis_toolbox, 0, 0)
        self.basis_warning = QLabel()
        self.basis_warning.setStyleSheet("QLabel { color : red; }")
        valence_layout.addWidget(self.basis_warning, 1, 0)
        
        ecp_side = QWidget()
        ecp_side_layout = QGridLayout(ecp_side)
        ecp_basis_area = QGroupBox("effective core potential")        
        ecp_layout = QGridLayout(ecp_basis_area)
        self.ecp_toolbox = QTabWidget()
        self.ecp_toolbox.setTabsClosable(True)
        self.ecp_toolbox.tabCloseRequested.connect(self.close_ecp_tab)
        ecp_layout.addWidget(self.ecp_toolbox, 0, 0)

        valence_side_layout.addWidget(valence_basis_area, 0, 0)
        ecp_side_layout.addWidget(ecp_basis_area, 0, 0)
        
        self.new_basis_button = QPushButton("new basis...")
        self.new_basis_button.clicked.connect(self.new_basis)
        valence_side_layout.addWidget(self.new_basis_button, 1, 0)
                
        self.new_ecp_button = QPushButton("new ECP...")
        self.new_ecp_button.clicked.connect(self.new_ecp)
        ecp_side_layout.addWidget(self.new_ecp_button, 1, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(True)
        splitter.addWidget(valence_side)
        splitter.addWidget(ecp_side)
        
        self.layout.addWidget(splitter)
        
        for i, basis in enumerate(self.settings.last_basis):
            self.new_basis(use_saved=i)        
        
        for i, basis in enumerate(self.settings.last_ecp):
            self.new_ecp(use_saved=i)

    def close_ecp_tab(self, index):
        self.remove_basis(self.ecp_options[index])
    
    def close_basis_tab(self, index):
        self.remove_basis(self.basis_options[index])

    def new_ecp(self, use_saved=0):
        """add an ECPOption"""
        new_basis = ECPOption(self, self.settings)
        new_basis.setToolBox(self.ecp_toolbox)
        new_basis.setElements(self.elements)
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
                        
    def new_basis(self, use_saved=0):
        """add a BasisOption"""
        new_basis = BasisOption(self, self.settings)
        new_basis.setToolBox(self.basis_toolbox)
        new_basis.setElements(self.elements)
        if use_saved < len(self.settings.last_basis):
            name = self.settings.last_basis[use_saved]
            custom = self.settings.last_custom_basis_kw[use_saved]
            builtin = self.settings.last_custom_basis_builtin[use_saved]
            new_basis.setBasis(name, custom, builtin)
            #new_basis.setSelectedElements(self.settings.last_basis_elements[use_saved].split(','))
            
        new_basis.basis_changed()

        elements_without_basis = []
        for element in self.elements:
            if not any([element in basis.currentElements() for basis in self.basis_options]):
                elements_without_basis.append(element)
        
        new_basis.setSelectedElements(elements_without_basis)

        self.basis_options.append(new_basis)
        
        if len(self.basis_options) == 1 and len(self.ecp_options) == 0:
            self.basis_options[0].setSelectedElements(self.elements)
            self.basis_warning.setVisible(False)

        self.check_elements()

        self.basis_toolbox.addTab(new_basis, "")
        self.basis_toolbox.setCurrentWidget(new_basis)

        self.refresh_basis()
    
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

        elements_without_basis = []
        for element in self.elements:
            if not any([element in basis.currentElements() for basis in self.basis_options]):
                elements_without_basis.append(element)
        
        for basis in self.basis_options + self.ecp_options:
            basis.update_tooltab()
        
        if len(elements_without_basis) != 0:
            self.basis_warning.setText("elements with no basis: %s" % ", ".join(elements_without_basis))
            self.basis_warning.setVisible(True)
        else:
            self.basis_warning.setText("elements with no basis: None")
            self.basis_warning.setVisible(False)

    def refresh_ecp(self):
        """repositions ecp options
        may be called after one option is removed"""
        for i, basis in enumerate(self.ecp_options):
            basis.update_tooltab()
            
            basis.show_elements(not (len(self.basis_options) == 1 and len(self.ecp_options) == 0))
        
    def get_basis(self):
        """returns ([Basis], [ECP]) corresponding to the current settings"""
        basis_set = []
        ecp = []
        for i, basis in enumerate(self.basis_options):
            basis_name, gen_path = basis.currentBasis(True, index=i)
            basis_set.append(Basis(basis_name, elements=basis.currentElements(), user_defined=gen_path))
                
        self.settings.last_basis = self.settings.last_basis[:len(self.basis_options)]
        self.settings.last_custom_basis_kw = self.settings.last_custom_basis_kw[:len(self.basis_options)]
        self.settings.last_custom_basis_builtin = self.settings.last_custom_basis_builtin[:len(self.basis_options)]
        self.settings.last_basis_elements = self.settings.last_basis_elements[:len(self.basis_options)]
                
        if len(basis_set) == 0:
            basis_set = None
                
        for i, basis in enumerate(self.ecp_options):
            basis_name, gen_path = basis.currentBasis(True, index=i)
            ecp.append(ECP(basis_name, elements=basis.currentElements(), user_defined=gen_path))
        
        self.settings.last_ecp = self.settings.last_ecp[:len(self.ecp_options)]
        self.settings.last_custom_ecp_kw = self.settings.last_custom_ecp_kw[:len(self.ecp_options)]
        self.settings.last_custom_ecp_builtin = self.settings.last_custom_ecp_builtin[:len(self.ecp_options)]
        self.settings.last_ecp_elements = self.settings.last_ecp_elements[:len(self.ecp_options)]

        if len(ecp) == 0:
            ecp = None
        
        return basis_set, ecp

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
            for option in self.basis_options:
                if option is not exclude_option:
                    for i in range(0, option.elements.count()):
                        if option.elements.item(i).text() in element_list:
                            option.elements.item(i).setSelected(False)

    def setElements(self, element_list):
        """sets the available elements in all child BasisOptions
        if an element is already available, it will not be removed"""
        previous_elements = self.elements
        self.elements = element_list
        
        new_elements = [element for element in element_list if element not in previous_elements]
        del_elements = [element for element in previous_elements if element not in element_list]
        
        for j, basis in enumerate(self.basis_options):
            for i in range(basis.elements.count()-1, -1, -1):
                if basis.elements.item(i).text() in del_elements:
                    basis.elements.takeItem(i)
                    
            basis.elements.addItems(new_elements)
            basis.elements.sortItems()
            basis.setSelectedElements(self.settings.last_basis_elements[j].split(","))

        for j, basis in enumerate(self.ecp_options):
            for i in range(basis.elements.count()-1, -1, -1):
                if basis.elements.item(i).text() in del_elements:
                    basis.elements.takeItem(i)
                    
            basis.elements.addItems(new_elements)
            basis.elements.sortItems()
            basis.setSelectedElements(self.settings.last_ecp_elements[j].split(","))

        if len(self.basis_options) == 1 and len(self.ecp_options) == 0:
            self.basis_options[0].setSelectedElements(self.elements)
                
        self.check_elements()