from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import FloatArg, BoolArg

from PyQt5.Qt import QClipboard
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QLabel, QGridLayout, QComboBox, QSplitter, QFrame, QLineEdit, QDoubleSpinBox, QMenuBar, QFileDialog, QAction, QApplication

from ChimAARON.managers.filereader_manager import FILEREADER_CHANGE 

from AaronTools.comp_output import CompOutput

class _ComputeThermoSettings(Settings):

    AUTO_SAVE = {
        'w0': Value(100.0, FloatArg, str),
        'include_header': Value(True, BoolArg, str),
    }


class Thermochem(ToolInstance):
    #XML_TAG ChimeraX :: Tool :: Process Thermochemistry :: AaronTools :: Compute the free energy of a molecule with frequency data
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.display_name = "Thermochemistry"
        
        self.tool_window = MainToolWindow(self)        

        self.settings = _ComputeThermoSettings(self.session, name)

        self._build_ui()

        self.refresh_models()
        
        self._refresh_handler = self.session.filereader_manager.triggers.add_handler(FILEREADER_CHANGE, self.refresh_models)

    def _build_ui(self):
        layout = QGridLayout()

        #box for sp
        sp_area_widget = QFrame()
        self.sp_layout = QGridLayout(sp_area_widget)

        sp_label = QLabel("Single-point energy:")
        self.sp_layout.addWidget(sp_label, 0, 0, 1, 1, Qt.AlignTop)

        self.sp_selector = QComboBox()
        self.sp_selector.currentIndexChanged.connect(self.set_sp)
        self.sp_layout.addWidget(self.sp_selector, 0, 1, 1, 2, Qt.AlignTop)
        
        nrg_label = QLabel("E =")
        self.sp_layout.addWidget(nrg_label, 1, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.sp_nrg_line = QLineEdit()
        self.sp_nrg_line.setReadOnly(True)
        self.sp_nrg_line.setToolTip("electronic energy")
        self.sp_layout.addWidget(self.sp_nrg_line, 1, 1, 1, 1, Qt.AlignTop)
        
        self.sp_layout.addWidget(QLabel("E<sub>h</sub>"), 1, 2, 1, 1, Qt.AlignTop)
        
        self.sp_layout.setColumnStretch(0, 0)
        self.sp_layout.setColumnStretch(1, 1)
        self.sp_layout.setRowStretch(0, 0)
        self.sp_layout.setRowStretch(1, 1)
        sp_area_widget.setFrameStyle(QFrame.StyledPanel)
        

        row = 0
        #box for thermo
        therm_area_widget = QFrame()
        self.thermo_layout = QGridLayout(therm_area_widget)
        
        therm_label = QLabel("Thermal corrections:")
        self.thermo_layout.addWidget(therm_label, row, 0, 1, 1, Qt.AlignTop)
        
        self.thermo_selector = QComboBox()
        self.thermo_selector.currentIndexChanged.connect(self.set_thermo_mdl)
        self.thermo_layout.addWidget(self.thermo_selector, row, 1, 1, 2, Qt.AlignTop)

        row += 1

        self.thermo_layout.addWidget(QLabel("T ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.temperature_line = QDoubleSpinBox()
        self.temperature_line.setMaximum(2**31 - 1)
        self.temperature_line.setValue(298.15)
        self.temperature_line.setSingleStep(10)
        self.temperature_line.setSuffix(" K")
        self.temperature_line.setMinimum(0)
        self.temperature_line.valueChanged.connect(self.set_thermo)
        self.thermo_layout.addWidget(self.temperature_line, row, 1, 1, 2, Qt.AlignTop)
        
        row += 1
        
        self.thermo_layout.addWidget(QLabel("𝜔<sub>0</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.v0_edit = QDoubleSpinBox()
        self.v0_edit.setMaximum(2**31 - 1)
        self.v0_edit.setValue(self.settings.w0)
        self.v0_edit.setSingleStep(25)
        self.v0_edit.setSuffix(" cm\u207b\u00b9")
        self.v0_edit.valueChanged.connect(self.set_thermo)
        self.v0_edit.setMinimum(0)
        self.v0_edit.setToolTip("frequency paramter for quasi treatments of entropy")
        self.thermo_layout.addWidget(self.v0_edit, row, 1, 1, 2, Qt.AlignTop)
        
        row += 1
    
        self.thermo_layout.addWidget(QLabel("𝛿ZPE ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)

        self.zpe_line = QLineEdit()
        self.zpe_line.setReadOnly(True)
        self.zpe_line.setToolTip("zero-point energy correction")
        self.thermo_layout.addWidget(self.zpe_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)  
        
        row += 1

        self.thermo_layout.addWidget(QLabel("𝛿H<sub>RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)

        self.enthalpy_line = QLineEdit()
        self.enthalpy_line.setReadOnly(True)
        self.enthalpy_line.setToolTip("RRHO enthalpy correction")
        self.thermo_layout.addWidget(self.enthalpy_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)        

        row += 1

        self.thermo_layout.addWidget(QLabel("𝛿G<sub>RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)

        self.rrho_g_line = QLineEdit()
        self.rrho_g_line.setReadOnly(True)
        self.rrho_g_line.setToolTip("""RRHO free energy correction""")
        self.thermo_layout.addWidget(self.rrho_g_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)        
        
        row += 1
        
        self.thermo_layout.addWidget(QLabel("𝛿G<sub>Quasi-RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.qrrho_g_line = QLineEdit()
        self.qrrho_g_line.setReadOnly(True)
        self.qrrho_g_line.setToolTip("Quasi-RRHO free energy correction\n" + \
        "Vibrational entropy of each mode is weighted and complemented with rotational entropy\n" + \
        "The weighting is much lower for modes with frequencies less than 𝜔\u2080")        
        self.thermo_layout.addWidget(self.qrrho_g_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)        
        
        row += 1
        
        self.thermo_layout.addWidget(QLabel("𝛿G<sub>Quasi-Harmonic</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.qharm_g_line = QLineEdit()
        self.qharm_g_line.setReadOnly(True)
        self.qharm_g_line.setToolTip("Quasi-hamonic free energy correction\n" + \
        "For entropy, real vibrational modes lower than 𝜔\u2080 are treated as 𝜔\u2080")
        self.thermo_layout.addWidget(self.qharm_g_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)

        self.thermo_layout.setColumnStretch(0, 0)
        self.thermo_layout.setColumnStretch(1, 1)
        for i in range(0, row - 1):
            self.thermo_layout.setRowStretch(i, 0)
        
        self.thermo_layout.setRowStretch(row, 1)
        therm_area_widget.setFrameStyle(QFrame.StyledPanel)
        
        
        row = 0
        # for for total
        sum_area_widget = QFrame()
        self.sum_layout = QGridLayout(sum_area_widget)
        sum_area_widget.setFrameStyle(QFrame.StyledPanel)
        
        total_label = QLabel("Thermochemistry")
        self.sum_layout.addWidget(total_label, row, 0, 1, 3, Qt.AlignHCenter | Qt.AlignTop)
        
        row += 1
        
        self.sum_layout.addWidget(QLabel("ZPE ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.zpe_sum_line = QLineEdit()
        self.zpe_sum_line.setReadOnly(True)
        self.zpe_sum_line.setToolTip("sum of electronic energy and ZPE correction")
        self.sum_layout.addWidget(self.zpe_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)      
        
        row += 1
                
        self.sum_layout.addWidget(QLabel("H<sub>RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.h_sum_line = QLineEdit()
        self.h_sum_line.setReadOnly(True)
        self.h_sum_line.setToolTip("sum of electronic energy and RRHO enthalpy correction")
        self.sum_layout.addWidget(self.h_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)      
        
        row += 1
        
        self.sum_layout.addWidget(QLabel("G<sub>RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.rrho_g_sum_line = QLineEdit()
        self.rrho_g_sum_line.setReadOnly(True)
        self.rrho_g_sum_line.setToolTip("sum of electronic energy and RRHO free energy correction")
        self.sum_layout.addWidget(self.rrho_g_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)        
        
        row += 1
        
        self.sum_layout.addWidget(QLabel("G<sub>Quasi-RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.qrrho_g_sum_line = QLineEdit()
        self.qrrho_g_sum_line.setReadOnly(True)
        self.qrrho_g_sum_line.setToolTip("Sum of electronic energy and quasi-RRHO free energy correction\n" + \
        "Vibrational entropy of each mode is weighted and complemented with rotational entropy\n" + \
        "The weighting is much lower for modes with frequencies less than 𝜔\u2080")
        self.sum_layout.addWidget(self.qrrho_g_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)  
        
        row += 1
        
        self.sum_layout.addWidget(QLabel("G<sub>Quasi-Harmonic</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.qharm_g_sum_line = QLineEdit()
        self.qharm_g_sum_line.setReadOnly(True)
        self.qharm_g_sum_line.setToolTip("Sum of electronic energy and quasi-harmonic free energy correction\n" + \
        "For entropy, real vibrational modes lower than 𝜔\u2080 are treated as 𝜔\u2080")
        self.sum_layout.addWidget(self.qharm_g_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)
        
        self.sum_layout.setColumnStretch(0, 0)
        for i in range(0, row-1):
            self.sum_layout.setRowStretch(i, 0)

        self.sum_layout.setRowStretch(row, 1)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(sp_area_widget)
        splitter.addWidget(therm_area_widget)
        splitter.addWidget(sum_area_widget)
        
        layout.addWidget(splitter)

        #menu stuff
        menu = QMenuBar()
        
        export = menu.addMenu("&Export")
        copy = QAction("&Copy CSV to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_csv)
        shortcut = QKeySequence(Qt.CTRL + Qt.Key_C)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        
        add_header = QAction("&Include CSV header", self.tool_window.ui_area, checkable=True)
        add_header.setChecked(self.settings.include_header)
        add_header.triggered.connect(self.header_check)
        export.addAction(add_header)
        
        save = QAction("&Save CSV...", self.tool_window.ui_area)
        save.triggered.connect(self.save_csv)
        #this shortcut interferes with main window's save shortcut
        #shortcut = QKeySequence(Qt.CTRL + Qt.Key_S)
        #save.setShortcut(shortcut)
        #save.setShortcutContext(Qt.WidgetShortcut)
        export.addAction(save)
        
        menu.setNativeMenuBar(False)
        layout.setMenuBar(menu)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
        
    def save_csv(self):
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
        if filename:
            s = self.get_csv()
   
            with open(filename, 'w') as f:
                f.write(s.strip())
                
            print("saved to %s" % filename)

    def copy_csv(self):
        app = QApplication.instance()
        clipboard = app.clipboard()
        csv = self.get_csv()
        clipboard.setText(csv)
        print("copied to clipboard")

    def get_csv(self):
        if self.settings.include_header:
            s = "E,ZPE,H(RRHO),G(RRHO),G(Quasi-RRHO),G(Quasi-harmonic),dZPE,dH(RRHO),dG(RRHO),dG(Quasi-RRHO),dG(Quasi-harmonic),SP File,Thermo File\n"
        else:
            s = ""
        
        fmt = 11*"%.12f," + "%s,%s" + "\n"
        
        E    = float(self.sp_nrg_line.text())
        
        dZPE = float(self.zpe_line.text())
        dH       = float(self.enthalpy_line.text())
        rrho_dG  = float(self.rrho_g_line.text())
        qrrho_dG = float(self.qrrho_g_line.text())
        qharm_dG = float(self.qharm_g_line.text())            
        
        ZPE = float(self.zpe_sum_line.text())
        H       = float(self.h_sum_line.text())
        rrho_G  = float(self.rrho_g_sum_line.text())
        qrrho_G = float(self.qrrho_g_sum_line.text())
        qharm_G = float(self.qharm_g_sum_line.text())
        
        sp_mdl = self.sp_selector.currentData()
        sp_name = sp_mdl.aarontools_filereader.name
                    
        therm_mdl = self.thermo_selector.currentData()
        therm_name = therm_mdl.aarontools_filereader.name
        
        s += fmt % (E, ZPE, H, rrho_G, qrrho_G, qharm_G, dZPE, dH, rrho_dG, qrrho_dG, qharm_dG, sp_name, therm_name)
        
        return s
    
    def header_check(self, state):
        if state:
            self.settings.include_header = True
        else:
            self.settings.include_header = False
    
    def refresh_models(self, *args, **kwargs):
        models = self.session.filereader_manager.models
        
        comp_outs = [CompOutput(mdl.aarontools_filereader) for mdl in models]
        self.nrg_cos = {mdl:co for mdl, co in zip(models, comp_outs) if co.energy is not None}
        self.thermo_cos = {mdl:co for mdl, co in zip(models, comp_outs) if co.grimme_g is not None}
        
        self.nrg_models = list(self.nrg_cos.keys())
        self.thermo_models = list(self.thermo_cos.keys())
        
        for i in range(0, self.sp_selector.count()):
            if self.sp_selector.itemData(i) not in self.nrg_models:
                self.sp_selector.removeItem(i)
                
        for model in self.nrg_models:
            if self.sp_selector.findData(model) == -1:
                self.sp_selector.addItem("%s (%s)" % (model.name, model.atomspec), model)
        
        for i in range(0, self.thermo_selector.count()):
            if self.thermo_selector.itemData(i) not in self.thermo_models:
                self.thermo_selector.removeItem(i)
                
        for model in self.thermo_models:
            if self.thermo_selector.findData(model) == -1:
                self.thermo_selector.addItem("%s (%s)" % (model.name, model.atomspec), model)

    def set_sp(self):
        if self.sp_selector.currentIndex() >= 0:
            mdl = self.nrg_models[self.sp_selector.currentIndex()]
            co = self.nrg_cos[mdl]
                
            self.sp_nrg_line.setText(repr(co.energy))
        else:
            self.sp_nrg_line.setText("")
            
        self.update_sum()
        
    def set_thermo_mdl(self):
        if self.thermo_selector.currentIndex() >= 0:
            mdl = self.thermo_models[self.thermo_selector.currentIndex()]
            co = self.thermo_cos[mdl]
            
            if co.temperature is not None:
                self.temperature_line.setValue(co.temperature)

        self.set_thermo()
                
    def set_thermo(self):      
        if self.thermo_selector.currentIndex() >= 0:
            mdl = self.thermo_models[self.thermo_selector.currentIndex()]
            co = self.thermo_cos[mdl]
            
            v0 = self.v0_edit.value()

            if v0 != self.settings.w0:
                self.settings.w0 = v0
            
            T = self.temperature_line.value()
            if not T:
                return
            
            dZPE = co.ZPVE
            dE, dH, s = co.therm_corr(temperature=T)
            rrho_dg = co.calc_G_corr(v0=0, temperature=T)
            qrrho_dg = co.calc_G_corr(v0=v0, temperature=T, quasi_harmonic=False)
            qharm_dg = co.calc_G_corr(v0=v0, temperature=T, quasi_harmonic=True)
            
            self.zpe_line.setText(repr(dZPE))
            self.enthalpy_line.setText(repr(dH))
            self.rrho_g_line.setText(repr(rrho_dg))
            self.qrrho_g_line.setText(repr(qrrho_dg))
            self.qharm_g_line.setText(repr(qharm_dg))
        else:
            self.zpe_line.setText("")
            self.enthalpy_line.setText("")
            self.rrho_g_line.setText("")
            self.qrrho_g_line.setText("")
            self.qharm_g_line.setText("")
        
        self.update_sum()
        
    def update_sum(self):
        dZPE = self.zpe_line.text()
        dH = self.enthalpy_line.text()
        dG = self.rrho_g_line.text()
        dG_qrrho = self.qrrho_g_line.text()
        dG_qharm = self.qharm_g_line.text()
        
        nrg = self.sp_nrg_line.text()
        
        if len(dH) == 0 or len(nrg) == 0:
            self.zpe_sum_line.setText("")
            self.h_sum_line.setText("")
            self.rrho_g_sum_line.setText("")
            self.qrrho_g_sum_line.setText("")
            self.qharm_g_sum_line.setText("")
            return
        else:
            dZPE = float(dZPE)
            dH = float(dH)
            dG = float(dG)
            dG_qrrho = float(dG_qrrho)
            dG_qharm = float(dG_qharm)
            
            nrg = float(nrg)
            
            zpe = nrg + dZPE
            enthalpy = nrg + dH
            rrho_g = nrg + dG
            qrrho_g = nrg + dG_qrrho
            qharm_g = nrg + dG_qharm
            
            self.zpe_sum_line.setText(repr(zpe))
            self.h_sum_line.setText(repr(enthalpy))
            self.rrho_g_sum_line.setText(repr(rrho_g))
            self.qrrho_g_sum_line.setText(repr(qrrho_g))
            self.qharm_g_sum_line.setText(repr(qharm_g))
        
    def delete(self):
        """overload delete"""
        self.session.filereader_manager.triggers.remove_handler(self._refresh_handler)
        super().delete()           