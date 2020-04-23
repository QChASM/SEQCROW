from chimerax.atomic import AtomicStructure, selected_atoms, selected_bonds
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import StringArg, BoolArg, ListOf, IntArg
from chimerax.core.models import ADD_MODELS, REMOVE_MODELS

from json import dumps, loads

from PyQt5.Qt import QClipboard, QStyle, QIcon
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QKeySequence, QFontMetrics
from PyQt5.QtWidgets import QCheckBox, QLabel, QGridLayout, QComboBox, QSplitter, QFrame, QLineEdit, \
                            QSpinBox, QMenuBar, QFileDialog, QAction, QApplication, QPushButton, \
                            QTabWidget, QWidget, QGroupBox, QListWidget, QTableWidget, QTableWidgetItem, \
                            QHBoxLayout, QFormLayout, QDoubleSpinBox
from SEQCROW.residue_collection import ResidueCollection
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
        'last_number_basis': Value(1, IntArg), 
        'last_ecp': Value([], ListOf(StringArg), tuple2str), 
        'last_custom_ecp_kw': Value([], ListOf(StringArg), tuple2str), 
        'last_custom_ecp_builtin': Value([], ListOf(StringArg), tuple2str), 
        'last_ecp_elements': Value([], ListOf(StringArg), tuple2str),
        'last_ecp_path': Value("", StringArg),
        'last_number_ecp': Value(0, IntArg), 
        'previous_functional': Value("", StringArg),
        'previous_custom_func': Value("", StringArg), 
        'previous_functional_names': Value([], ListOf(StringArg), tuple2str),
        'previous_functional_needs_basis': Value([], ListOf(BoolArg), tuple2str),
        'previous_dispersion': Value("None", StringArg),
        'previous_grid': Value("Default", StringArg),
        'previous_charge': Value(0, IntArg), 
        'previous_mult': Value(1, IntArg), 
        'previous_gaussian_solvent_model': Value("None", StringArg), 
        'previous_gaussian_solvent_name': Value("", StringArg), 
        #shh these are just jsons
        'previous_gaussian_options': Value(dumps({Method.GAUSSIAN_ROUTE:{'opt':['NoEigenTest', 'Tight', 'VeryTight'], 'DensityFit':[], 'pop':['NBO', 'NBO7']}}), StringArg),
        'last_gaussian_options': Value(dumps({Method.GAUSSIAN_ROUTE:{}}), StringArg),
    }


def combine_dicts(d1, d2):
    #TODO
    #accept any number of input dicts
    out = {}
    for key in set(list(d1.keys()) + list(d2.keys())):
        if key in d1 and not key in d2:
            out[key] = d1[key]
            
        elif key in d2 and key not in d1:
            out[key] = d2[key]
            
        else:
            if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                out[key] = combine_dicts(d1[key], d2[key])

            else:
                out[key] = d1[key] + d2[key]
                
    return out


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
        self.job_widget = JobTypeOption(self.settings, self.session, init_form=self.file_type.currentText())
        
        #functional stuff
        self.functional_widget = FunctionalOption(self.settings, init_form=self.file_type.currentText())

        #basis set stuff
        self.basis_widget = BasisWidget(self.settings)
        
        #other keywords
        self.other_keywords_widget = KeywordWidget(self.settings, init_form=self.file_type.currentText())
        
        tabs = QTabWidget()
        tabs.addTab(self.job_widget, "job details")
        tabs.addTab(self.functional_widget, "functional")
        tabs.addTab(self.basis_widget, "basis functions")
        tabs.addTab(self.other_keywords_widget, "other options")
        
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
        save.triggered.connect(self.save_input)
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

        func = self.functional_widget.getFunctional()        
        basis = self.get_basis_set()
        dispersion = self.functional_widget.getDispersion()
        grid = self.functional_widget.getGrid()      
        charge = self.job_widget.getCharge()
        mult = self.job_widget.getMultiplicity()

        self.settings.save()

        constraints = self.job_widget.getConstraints()
        
        self.theory = Method(structure=model, charge=charge, multiplicity=mult, \
                             functional=func, basis=basis, empirical_dispersion=dispersion, \
                             grid=grid, constraints=constraints)

    def change_job_type(self):
        #implement later
        pass
    
    def change_model(self, index):
        if index == -1:
            self.basis_widget.setElements([])
            return
            
        mdl = self.model_selector.currentData()
        elements = set(mdl.atoms.elements.names)
        self.basis_widget.setElements(elements)
        self.job_widget.setStructure(mdl)
        
        if mdl in self.session.filereader_manager.filereader_dict:
            fr = self.session.filereader_manager.filereader_dict[mdl]
            if 'charge' in fr.other:
                self.job_widget.setCharge(fr.other['charge'])
           
            if 'multiplicity' in fr.other:
                self.job_widget.setMultiplicity(fr.other['multiplicity'])
                
            if 'temperature' in fr.other:
                self.job_widget.setTemperature(fr.other['temperature'])
    
    def get_basis_set(self):
        basis, ecp = self.basis_widget.get_basis()
        
        return BasisSet(basis, ecp)

    def copy_input(self):
        self.update_theory()
        
        kw_dict = self.job_widget.getKWDict()
        other_kw_dict = self.other_keywords_widget.getKWDict()
        self.settings.save()
        
        combined_dict = combine_dicts(kw_dict, other_kw_dict)
        
        output, warnings = self.theory.write_gaussian_input(combined_dict)
        
        for warning in warnings:
            self.session.logger.warning(warning)

        app = QApplication.instance()
        clipboard = app.clipboard()
        clipboard.setText(output)
    
        print("copied to clipboard")
    
    def save_input(self):
        self.update_theory()
        
        kw_dict = self.job_widget.getKWDict()
        other_kw_dict = self.other_keywords_widget.getKWDict()
        self.settings.save()
        
        combined_dict = combine_dicts(kw_dict, other_kw_dict)

        output, warnings = self.theory.write_gaussian_input(combined_dict)
        
        for warning in warnings:
            self.session.logger.warning(warning)

        filename, _ = QFileDialog.getSaveFileName(filter="Gaussian input files (*.com)")
        if filename:
            with open(filename, 'w') as f:
                f.write(output)
                
            print("saved to %s" % filename)
    
    def delete(self):
        #overload delete ro de-register handler
        self.session.triggers.remove_handler(self._add_handler)
        self.session.triggers.remove_handler(self._remove_handler)
        super().delete()  

    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
    

class JobTypeOption(QWidget):
    def __init__(self, settings, session, init_form, parent=None):
        super().__init__(parent)
        
        self.settings = settings
        self.session = session
        self.form = init_form
        self.structure = None
        self.constrained_atoms = []
        self.constrained_bonds = []
        
        self.layout = QGridLayout(self)
        
        job_form = QWidget()
        job_type_layout = QFormLayout(job_form)
        
        self.charge = QSpinBox()
        self.charge.setRange(-5, 5)
        self.charge.setSingleStep(1)
        self.charge.setValue(self.settings.previous_charge)
        
        job_type_layout.addRow("charge:", self.charge)
                
        self.multiplicity = QSpinBox()
        self.multiplicity.setRange(1, 3)
        self.multiplicity.setSingleStep(1)
        self.multiplicity.setValue(self.settings.previous_mult)
        
        job_type_layout.addRow("multiplicity:", self.multiplicity)
        
        self.do_geom_opt = QCheckBox()
        self.do_geom_opt.stateChanged.connect(self.change_job_type)
        job_type_layout.addRow("geometry optimization:", self.do_geom_opt)
        
        self.do_freq = QCheckBox()
        self.do_freq.stateChanged.connect(self.change_job_type)
        job_type_layout.addRow("frequency calculation:", self.do_freq)
        
        self.layout.addWidget(job_form, 0, 0, Qt.AlignTop)
        
        self.job_type_opts = QTabWidget()
        
        self.geom_opt = QWidget()
        geom_opt_layout = QGridLayout(self.geom_opt)
        geom_opt_form_widget = QWidget()
        geom_opt_form = QFormLayout(geom_opt_form_widget)
        
        self.ts_opt = QCheckBox()
        geom_opt_form.addRow("transition state structure:", self.ts_opt)
        
        self.use_contraints = QCheckBox()
        self.use_contraints.stateChanged.connect(self.show_contraints)
        geom_opt_form.addRow("constrained:", self.use_contraints)
        
        self.constraints_widget = QWidget()
        constraints_layout = QGridLayout(self.constraints_widget)
        
        geom_opt_layout.addWidget(geom_opt_form_widget, 0, 0, Qt.AlignTop)
        
        freeze_atoms = QPushButton("constrain selected atoms")
        freeze_atoms.clicked.connect(self.constrain_atoms)
        constraints_layout.addWidget(freeze_atoms, 0, 0, Qt.AlignTop)
        
        freeze_bonds = QPushButton("constrain selected bonds")
        freeze_bonds.clicked.connect(self.constrain_bonds)
        constraints_layout.addWidget(freeze_bonds, 0, 1, Qt.AlignTop)
        
        constraints_viewer = QTabWidget()
                
        self.constrained_atom_table = QTableWidget()
        self.constrained_atom_table.setColumnCount(1)
        self.constrained_atom_table.setHorizontalHeaderLabels(["atom"])
        self.constrained_bond_table = QTableWidget()
        self.constrained_bond_table.setColumnCount(2)
        self.constrained_bond_table.setHorizontalHeaderLabels(["atom 1", "atom 2"])
        
        constraints_viewer.addTab(self.constrained_atom_table, "atoms")
        constraints_viewer.addTab(self.constrained_bond_table, "bonds")
        
        constraints_layout.addWidget(constraints_viewer, 1, 0, 1, 2, Qt.AlignTop)

        constraints_layout.setRowStretch(0, 0)
        constraints_layout.setRowStretch(1, 1)
        
        self.constraints_widget.setVisible(self.use_contraints.checkState() == Qt.Checked)

        geom_opt_layout.addWidget(self.constraints_widget, 1, 0, Qt.AlignTop)
        
        self.job_type_opts.addTab(self.geom_opt, "optimization settings")
        
        self.freq_opt = QWidget()
        freq_opt_form = QFormLayout(self.freq_opt)
        
        self.temp = QDoubleSpinBox()
        self.temp.setRange(0, 10000)
        self.temp.setValue(298.15)
        self.temp.setSuffix(" K")
        self.temp.setSingleStep(10)
        
        freq_opt_form.addRow("temperature:", self.temp)
        
        self.hpmodes = QCheckBox()
        self.hpmodes.setCheckState(Qt.Checked)
        self.hpmodes.setToolTip("ask Gaussian to print extra precision on frequencies")
        freq_opt_form.addRow("high-precision modes:", self.hpmodes)

        self.raman = QCheckBox()
        self.raman.setCheckState(Qt.Unchecked)
        self.raman.setToolTip("ask Gaussian to compute Raman scattering intensities")
        freq_opt_form.addRow("Raman intensities:", self.raman)

        self.job_type_opts.addTab(self.freq_opt, "frequency settings")
        
        solvent_widget = QWidget()
        solvent_layout = QGridLayout(solvent_widget)
        
        solvent_form = QWidget()
        solvent_form_layout = QFormLayout(solvent_form)
        
        self.solvent_option = QComboBox()
        self.solvent_option.addItems(["None", "PCM", "SMD", "CPCM", "Dipole", "IPCM", "SCIPCM"])
        #TODO: move to setOptions
        ndx = self.solvent_option.findText(self.settings.previous_gaussian_solvent_model)
        if ndx >= 0:
            self.solvent_option.setCurrentIndex(ndx)
        self.solvent_option.currentTextChanged.connect(self.change_solvent_model)
        solvent_form_layout.addRow("implicit solvent model:", self.solvent_option)
        
        self.solvent_name_label = QLabel("solvent:")
        self.solvent_name = QLineEdit()
        #TODO: move to setOptions
        self.solvent_name.setText(self.settings.previous_gaussian_solvent_name)
        self.solvent_name.textChanged.connect(self.filter_solvents)
        self.solvent_name.setClearButtonEnabled(True)
        solvent_form_layout.addRow(self.solvent_name_label, self.solvent_name)
        self.solvent_name_label.setVisible(self.solvent_option.currentText() != "None")
        self.solvent_name.setVisible(self.solvent_option.currentText() != "None")
        
        solvent_layout.addWidget(solvent_form, 0, 0, Qt.AlignTop)
        
        self.solvent_names = QListWidget()
        self.solvent_names.setSelectionMode(self.solvent_names.SingleSelection)
        self.solvent_names.itemSelectionChanged.connect(self.change_selected_solvent)
        #TODO: move to setOptions
        self.solvent_names.addItems(ImplicitSolvent.KNOWN_GAUSSIAN_SOLVENTS)
        self.solvent_names.sortItems()
        self.solvent_names.setVisible(self.solvent_option.currentText() != "None")
        
        solvent_layout.addWidget(self.solvent_names)
        
        self.job_type_opts.addTab(solvent_widget, "solvent options")
        
        self.layout.addWidget(self.job_type_opts, 1, 0, Qt.AlignTop)

        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)

        self.setOptions(self.form)
        
        self.change_job_type()
        
    def setOptions(self, program):
        #do this when other programs are supported
        pass
    
    def change_selected_solvent(self):
        item = self.solvent_names.selectedItems()
        if len(item) == 1:
            name = item[0].text()
            self.solvent_name.setText(name)
    
    def filter_solvents(self, text):
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
        if self.solvent_option.currentText() != "None":
            self.solvent_name_label.setVisible(True)
            self.solvent_name.setVisible(True)
            self.solvent_names.setVisible(True)
        else:
            self.solvent_name_label.setVisible(False)
            self.solvent_name.setVisible(False)
            self.solvent_names.setVisible(False)            
    
    def change_job_type(self, *args):
        self.job_type_opts.setTabEnabled(0, self.do_geom_opt.checkState() == Qt.Checked)
        self.job_type_opts.setTabEnabled(1, self.do_freq.checkState() == Qt.Checked)
          
    def show_contraints(self, value):
        self.constraints_widget.setVisible(bool(value))
        
    def getCharge(self):
        charge = self.charge.value()
        self.settings.previous_charge = charge
        return charge

    def setCharge(self, value):
        self.charge.setValue(value)
        
    def getMultiplicity(self):
        mult = self.multiplicity.value()
        self.settings.previous_mult = mult
        return mult

    def setMultiplicity(self, value):
        self.multiplicity.setValue(value)
        
    def setTemperature(self, value):
        self.temp.setValue(value)

    def setStructure(self, structure):
        self.structure = structure
        self.constrained_atoms = []
        self.constrained_bonds = []
                
    def constrain_atoms(self):
        self.constrained_atom_table.setRowCount(0)
        self.constrained_atoms = [atom for atom in selected_atoms(self.session) if atom.structure is self.structure]
        for atom in self.constrained_atoms:
            row = self.constrained_atom_table.rowCount()
            self.constrained_atom_table.insertRow(row)
            item = QTableWidgetItem()
            item.setData(Qt.DisplayRole, atom.atomspec)
            self.constrained_atom_table.setItem(row, 0, item)

    def constrain_bonds(self):
        self.constrained_bond_table.setRowCount(0)
        self.constrained_bonds = [bond for bond in selected_bonds(self.session) if bond.structure is self.structure]
        for bond in self.constrained_bonds:
            row = self.constrained_bond_table.rowCount()
            self.constrained_bond_table.insertRow(row)
            atom1, atom2 = bond.atoms
            
            item1 = QTableWidgetItem()
            item1.setData(Qt.DisplayRole, atom1.atomspec)
            self.constrained_bond_table.setItem(row, 0, item1)
            
            item2 = QTableWidgetItem()
            item2.setData(Qt.DisplayRole, atom2.atomspec)
            self.constrained_bond_table.setItem(row, 1, item2)

    def getConstraints(self):
        if self.do_geom_opt.checkState() != Qt.Checked:
            return None
            
        elif self.use_contraints.checkState() == Qt.Unchecked:
            return None
            
        else:
            return {'atoms':self.constrained_atoms, 'bonds':self.constrained_bonds, 'angles':[], 'torsions':[]}
            
    def getKWDict(self):
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
                
                if self.raman.checkState() == Qt.Unchecked:
                    route['freq'].append("NoRaman")
                else:
                    route['freq'].append("Raman")
                    
                if self.hpmodes.checkState() == Qt.Checked:
                    route['freq'].append('HPModes')
                    
            if self.solvent_option.currentText() != "None":
                solvent_scrf = self.solvent_option.currentText()
                self.settings.previous_gaussian_solvent_model = solvent_scrf
                route['scrf'] = [solvent_scrf]
                
                solvent_name = self.solvent_name.text()
                self.settings.previous_gaussian_solvent_name = solvent_name
                route['scrf'].append("solvent=%s" % solvent_name)
                
            else:
                self.settings.previous_gaussian_solvent_model = "None"
                    
            return {Method.GAUSSIAN_ROUTE:route}
                

class FunctionalOption(QWidget):
    #TODO: make checking the "is_semiemperical" box disable the basis functions tab of the parent tab widget
    GAUSSIAN_FUNCTIONALS = ["B3LYP", "M06", "M06-L", "M06-2X", "ωB97X-D", "B3PW91", "B97-D", "BP86", "PBE0", "PM6", "AM1"]
    GAUSSIAN_DISPERSION = ["Grimme D2", "Grimme D3", "Becke-Johnson damped Grimme D3", "Petersson-Frisch"]
    GAUSSIAN_GRIDS = ["Default", "SuperFineGrid", "UltraFine", "FineGrid"]
    
    def __init__(self, settings, init_form, parent=None):
        super().__init__(parent)

        self.settings = settings
        self.form = init_form
        
        self.layout = QGridLayout(self)
        
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

        self.layout.addWidget(functional_form, 0, 0, Qt.AlignTop)

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

        self.layout.addWidget(self.previously_used_table, 1, 0, Qt.AlignTop)

        dft_form = QWidget()
        disp_form_layout = QFormLayout(dft_form)

        self.dispersion = QComboBox()

        disp_form_layout.addRow("empirical dispersion:", self.dispersion)
        
        self.grid = QComboBox()
        self.grid.setToolTip("integration grid for methods without analytical exchange")
        
        disp_form_layout.addRow("integration grid:", self.grid)
        
        self.layout.addWidget(dft_form, 2, 0, Qt.AlignTop)
        
        self.other_options = [keyword_label, self.functional_kw, semi_empirical_label, self.is_semiemperical, self.previously_used_table]
        
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 0)
        self.layout.setRowStretch(2, 1)
        
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
        
        #TODO: figure out how to make the previous functionals table grow
        #self.layout.setRowStretch(1, int(text == "other"))
        #self.layout.setRowStretch(2, int(text != "other"))

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
        self.grid.clear()
        self.form = program
        if program == "Gaussian":
            self.functional_option.addItems(self.GAUSSIAN_FUNCTIONALS)
            self.functional_option.addItem("other")
            
            self.dispersion.addItem("None")
            self.dispersion.addItems(self.GAUSSIAN_DISPERSION)
            
            self.grid.addItems(self.GAUSSIAN_GRIDS)

    def setPreviousStuff(self):
        func = self.settings.previous_functional
        disp = self.settings.previous_dispersion
        grid = self.settings.previous_grid
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
                
            if grid in self.GAUSSIAN_GRIDS:
                ndx = self.grid.findText(grid, Qt.MatchExactly)
                self.grid.setCurrentIndex(ndx)
                
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
                self.settings.previous_functional = "Gaussian's B3LYP"
                return Functional("Gaussian's B3LYP", False)
            
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

    def getGrid(self):
        grid = self.grid.currentText()
        self.settings.previous_grid = grid
        if grid == "Default":
            return None
        else:
            return IntegrationGrid(grid)
                    
    
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
        self.previously_used_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.previously_used_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.previously_used_table.setSelectionMode(QTableWidget.SingleSelection)
        self.previously_used_table.verticalHeader().setVisible(False)
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
        
        for i in range(0, self.settings.last_number_basis):
            self.new_basis(use_saved=i)        
        
        for i in range(0, self.settings.last_number_ecp):
            self.new_ecp(use_saved=i)

    def close_ecp_tab(self, index):
        self.remove_basis(self.ecp_options[index])
    
    def close_basis_tab(self, index):
        self.remove_basis(self.basis_options[index])

    def new_ecp(self, checked=None, use_saved=None):
        """add an ECPOption"""
        new_basis = ECPOption(self, self.settings)
        new_basis.setToolBox(self.ecp_toolbox)
        new_basis.setElements(self.elements)
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
                        
    def new_basis(self, checked=None, use_saved=None):
        """add a BasisOption"""
        new_basis = BasisOption(self, self.settings)
        new_basis.setToolBox(self.basis_toolbox)
        new_basis.setElements(self.elements)
        if use_saved is None:
            use_saved = len(self.basis_options)
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
                
        #self.settings.last_basis = self.settings.last_basis[:len(self.basis_options)]
        #self.settings.last_custom_basis_kw = self.settings.last_custom_basis_kw[:len(self.basis_options)]
        #self.settings.last_custom_basis_builtin = self.settings.last_custom_basis_builtin[:len(self.basis_options)]
        #self.settings.last_basis_elements = self.settings.last_basis_elements[:len(self.basis_options)]
        
        self.settings.last_number_basis = len(self.basis_options)
        
        if len(basis_set) == 0:
            basis_set = None
                
        for i, basis in enumerate(self.ecp_options):
            basis_name, gen_path = basis.currentBasis(True, index=i)
            ecp.append(ECP(basis_name, elements=basis.currentElements(), user_defined=gen_path))
        
        #self.settings.last_ecp = self.settings.last_ecp[:len(self.ecp_options)]
        #self.settings.last_custom_ecp_kw = self.settings.last_custom_ecp_kw[:len(self.ecp_options)]
        #self.settings.last_custom_ecp_builtin = self.settings.last_custom_ecp_builtin[:len(self.ecp_options)]
        #self.settings.last_ecp_elements = self.settings.last_ecp_elements[:len(self.ecp_options)]

        if len(ecp) == 0:
            ecp = None

        self.settings.last_number_ecp = len(self.ecp_options)
        
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
        

class KeywordWidget(QWidget):
    class GaussianKeywordOptions(QWidget):
        def __init__(self, settings, parent=None):
            super().__init__(parent)
            self.settings = settings
            
            self.previous_dict = {}
            previous_dict = loads(self.settings.previous_gaussian_options)
            for key in previous_dict.keys():
                self.previous_dict[int(key)] = previous_dict[key]
            
            self.last_dict = {}
            last_dict = loads(self.settings.last_gaussian_options)
            for key in last_dict.keys():
                self.last_dict[int(key)] = last_dict[key]
                        
            self.layout = QGridLayout(self)
            
            position_widget = QWidget()
            position_widget_layout = QFormLayout(position_widget)
            position_selector = QComboBox()
            position_selector.addItems(['route'])
            position_widget_layout.addRow("position:", position_selector)
            
            self.layout.addWidget(position_widget, 0, 0)
            
            self.link0_area = QWidget()
            link0_layout = QGridLayout(self.link0_area)
            self.layout.addWidget(self.link0_area, 1, 0)
            
            self.route_keyword_area = QWidget()
            route_layout = QGridLayout(self.route_keyword_area)
            self.layout.addWidget(self.route_keyword_area, 1, 0)
            
            
            self.keyword_groupbox = QGroupBox("keyword")
            self.keyword_layout = QGridLayout(self.keyword_groupbox)
            route_layout.addWidget(self.keyword_groupbox, 0, 0)
            
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
            self.current_kw_table.setHorizontalHeaderLabels(['current', 'trash'])
            self.current_kw_table.setSelectionMode(QTableWidget.SingleSelection)
            self.current_kw_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.current_kw_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.current_kw_table.verticalHeader().setVisible(False)
            self.current_kw_table.cellActivated.connect(self.clicked_current_route_keyword)
            self.keyword_layout.addWidget(self.current_kw_table, 0, 1)

            new_kw_widget = QWidget()
            new_kw_widgets_layout = QGridLayout(new_kw_widget)
            self.new_kw = QLineEdit()
            add_kw_button = QPushButton("add")
            add_kw_button.clicked.connect(self.add_kw)
            new_kw_widgets_layout.addWidget(QLabel("new:"), 0, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
            new_kw_widgets_layout.addWidget(self.new_kw, 0, 1)
            new_kw_widgets_layout.addWidget(add_kw_button, 0, 2)
            self.keyword_layout.addWidget(new_kw_widget, 1, 0, 1, 2)
            

            self.option_groupbox = QGroupBox("options")
            option_layout = QGridLayout(self.option_groupbox)
            route_layout.addWidget(self.option_groupbox, 0, 1)
            
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
            self.current_opt_table.setHorizontalHeaderLabels(['current', 'trash'])
            self.current_opt_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.current_opt_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.current_opt_table.cellActivated.connect(self.clicked_current_keyword_option)
            self.current_opt_table.verticalHeader().setVisible(False)
            option_layout.addWidget(self.current_opt_table, 0, 1)

            new_opt_widget = QWidget()
            new_opt_widgets_layout = QGridLayout(new_opt_widget)
            self.new_opt = QLineEdit()
            add_opt_button = QPushButton("add")
            add_opt_button.clicked.connect(self.add_opt)
            new_opt_widgets_layout.addWidget(QLabel("new:"), 0, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
            new_opt_widgets_layout.addWidget(self.new_opt, 0, 1)
            new_opt_widgets_layout.addWidget(add_opt_button, 0, 2)
            option_layout.addWidget(new_opt_widget, 1, 0, 1, 2)

            self.current_kw_table.itemSelectionChanged.connect(self.update_route_opts)

            for kw in self.previous_dict[Method.GAUSSIAN_ROUTE].keys():
                self.add_item_to_previous_kw_table(kw)
                    
            for kw in self.last_dict[Method.GAUSSIAN_ROUTE].keys():
                self.add_item_to_current_kw_table(kw)
                
            position_selector.currentTextChanged.connect(self.change_widget)            
            self.change_widget(position_selector.currentText())
            
            self.previous_kw_table.resizeColumnToContents(0)
            self.previous_kw_table.resizeColumnToContents(1)
            self.current_kw_table.resizeColumnToContents(0)
            self.current_kw_table.resizeColumnToContents(1)
            self.previous_opt_table.resizeColumnToContents(0)
            self.previous_opt_table.resizeColumnToContents(1)
            self.current_opt_table.resizeColumnToContents(0)
            self.current_opt_table.resizeColumnToContents(1)
            
            self.selected_kw = None

        def add_item_to_previous_kw_table(self, kw):
            row = self.previous_kw_table.rowCount()
            self.previous_kw_table.insertRow(row)
            item = QTableWidgetItem(kw)
            item.setToolTip("double click to use %s" % kw)
            self.previous_kw_table.setItem(row, 0, item)
        
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            trash_button = QLabel()
            trash_button.setMaximumSize(16, 16)
            trash_button.setScaledContents(False)
            trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(16, 16))
            trash_button.setToolTip("double click to remove from stored keywords")
            widget_layout.addWidget(trash_button)
            self.previous_kw_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)
        
            self.previous_kw_table.resizeRowToContents(row)

        def remove_previous_kw_row(self, row):
            item = self.previous_kw_table.item(row, 0)
            kw = item.text()
            del self.previous_dict[Method.GAUSSIAN_ROUTE][kw]
            
            self.settings.previous_gaussian_options = dumps(self.previous_dict)
            self.settings.save()
            
            self.previous_kw_table.removeRow(row)
        
        def add_item_to_current_kw_table(self, kw):
            row = self.current_kw_table.rowCount()
            self.current_kw_table.insertRow(row)
            item = QTableWidgetItem(kw)
            self.current_kw_table.setItem(row, 0, item)
        
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            trash_button = QLabel()
            trash_button.setMaximumSize(16, 16)
            trash_button.setScaledContents(False)
            trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(16, 16))
            trash_button.setToolTip("double click to not use this keyword")
            widget_layout.addWidget(trash_button)
            self.current_kw_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)
        
            self.current_kw_table.resizeRowToContents(row)
            self.current_kw_table.resizeColumnToContents(0)
            self.current_kw_table.resizeColumnToContents(1)
            
        def add_item_to_previous_opt_table(self, opt):
            row = self.previous_opt_table.rowCount()
            self.previous_opt_table.insertRow(row)
            item = QTableWidgetItem(opt)
            item.setToolTip("double click to use %s=(%s)" % (self.selected_kw, opt))
            self.previous_opt_table.setItem(row, 0, item)
            
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            trash_button = QLabel()
            trash_button.setMaximumSize(16, 16)
            trash_button.setScaledContents(False)
            trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(16, 16))
            trash_button.setToolTip("double click to remove from stored option")
            widget_layout.addWidget(trash_button)
            self.previous_opt_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)
        
            self.previous_opt_table.resizeRowToContents(row)
        
        def remove_previous_opt_row(self, row):
            item = self.previous_opt_table.item(row, 0)
            opt = item.text()
            self.previous_dict[Method.GAUSSIAN_ROUTE][self.selected_kw].remove(opt)
            
            self.settings.previous_gaussian_options = dumps(self.previous_dict)
            self.settings.save()
            
            self.previous_opt_table.removeRow(row)
        
        def add_item_to_current_opt_table(self, opt):
            row = self.current_opt_table.rowCount()
            self.current_opt_table.insertRow(row)
            item = QTableWidgetItem(opt)
            self.current_opt_table.setItem(row, 0, item)
            
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            trash_button = QLabel()
            trash_button.setMaximumSize(16, 16)
            trash_button.setScaledContents(False)
            trash_button.setPixmap(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(16, 16))
            trash_button.setToolTip("double click to not use this option")
            widget_layout.addWidget(trash_button)
            self.current_opt_table.setCellWidget(row, 1, widget_that_lets_me_horizontally_align_an_icon)
        
            self.current_opt_table.resizeRowToContents(row)
            self.current_opt_table.resizeColumnToContents(0)
            self.current_opt_table.resizeColumnToContents(1)
            
        def add_kw(self):
            kw = self.new_kw.text()
            if kw not in self.last_dict[Method.GAUSSIAN_ROUTE]:
                self.last_dict[Method.GAUSSIAN_ROUTE][kw] = []
            
            self.add_item_to_current_kw_table(kw)

        def add_opt(self):
            opt = self.new_opt.text()

            kw = self.selected_kw
            if opt not in self.last_dict[Method.GAUSSIAN_ROUTE][kw]:
                self.last_dict[Method.GAUSSIAN_ROUTE][kw].append(opt)

                self.add_item_to_current_opt_table(opt)

        def change_widget(self, name):
            if name == "link 0 commands":
                self.link0_area.setVisible(True)
                self.route_keyword_area.setVisible(False)
                
            elif name == "route":
                self.link0_area.setVisible(False)
                self.route_keyword_area.setVisible(True)
                
        def update_route_opts(self):
            for i in range(self.previous_opt_table.rowCount(), -1, -1):
                self.previous_opt_table.removeRow(i)    
                
            for i in range(self.current_opt_table.rowCount(), -1, -1):
                self.current_opt_table.removeRow(i)
            
            selected_items = self.current_kw_table.selectedItems()
            if len(selected_items) != 1:
                self.option_groupbox.setTitle("options")
                return
            
            keyword = selected_items[0].text()              
            self.selected_kw = keyword
            
            self.option_groupbox.setTitle("'%s' options" % keyword)

            if keyword in self.previous_dict[Method.GAUSSIAN_ROUTE]:
                for opt in self.previous_dict[Method.GAUSSIAN_ROUTE][keyword]:
                    self.add_item_to_previous_opt_table(opt)
                
            if keyword in self.last_dict[Method.GAUSSIAN_ROUTE]:
                for opt in self.last_dict[Method.GAUSSIAN_ROUTE][keyword]:
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
                if any(keyword == kw for kw in self.last_dict[Method.GAUSSIAN_ROUTE].keys()):
                    return
                
                self.last_dict[Method.GAUSSIAN_ROUTE][keyword] = []
                
                self.add_item_to_current_kw_table(keyword)
    
        def clicked_current_route_keyword(self, row, column):
            if column == 1:
                item = self.current_kw_table.item(row, 0)
                kw = item.text()
                del self.last_dict[Method.GAUSSIAN_ROUTE][kw]
                
                self.settings.last_gaussian_options = dumps(self.last_dict)  
                
                self.current_kw_table.removeRow(row)
                
                if kw == self.selected_kw:
                    self.update_route_opts()
                
        def clicked_keyword_option(self, row, column):
            if column == 1:
                self.remove_previous_opt_row(row)
            elif column == 0:
                item = self.previous_opt_table.item(row, column)
                option = item.text()
    
                keyword = self.selected_kw
                
                if option in self.last_dict[Method.GAUSSIAN_ROUTE][keyword]:
                    return
                
                self.last_dict[Method.GAUSSIAN_ROUTE][keyword].append(option)
                
                self.add_item_to_current_opt_table(option)
      
        def clicked_current_keyword_option(self, row, column):
            if column == 1:
                item = self.current_opt_table.item(row, 0)
                opt = item.text()
                self.last_dict[Method.GAUSSIAN_ROUTE][self.selected_kw].remove(opt)
                
                self.settings.last_gaussian_options = dumps(self.last_dict)
                
                self.current_opt_table.removeRow(row)


    def __init__(self, settings, init_form, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.form = init_form
        
        self.layout = QGridLayout(self)
        
        self.gaussian_widget = self.GaussianKeywordOptions(self.settings)
        self.layout.addWidget(self.gaussian_widget)
        
        if init_form == "Gaussian":
            self.gaussian_widget.setVisible(True)
                        
    def getKWDict(self):
        if self.form == "Gaussian":
            for key in self.gaussian_widget.last_dict.keys():
                if key == Method.GAUSSIAN_ROUTE:
                    for kw in self.gaussian_widget.last_dict[key].keys():
                        if kw not in self.gaussian_widget.previous_dict[key].keys():
                            self.gaussian_widget.previous_dict[key][kw] = []
                            
                        for opt in self.gaussian_widget.last_dict[key][kw]:
                            if opt not in self.gaussian_widget.previous_dict[key][kw]:
                                self.gaussian_widget.previous_dict[key][kw].append(opt)
                                
            self.settings.previous_gaussian_options = dumps(self.gaussian_widget.previous_dict)
            self.settings.last_gaussian_options = dumps(self.gaussian_widget.last_dict)
                        
            return self.gaussian_widget.last_dict
        
        