from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QGridLayout, QComboBox, QSplitter, QFrame, QLineEdit, QDoubleSpinBox

from ChimAARON.managers.filereader_manager import FILEREADER_CHANGE 

from AaronTools.comp_output import CompOutput

class Thermochem(ToolInstance):
    #XML_TAG ChimeraX :: Tool :: Process Thermochemistry :: AaronTools :: Compute the free energy of a molecule with frequency data
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.display_name = "Thermochemistry"
        
        self.tool_window = MainToolWindow(self)        

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
        self.v0_edit.setValue(100)
        self.v0_edit.setSingleStep(25)
        self.v0_edit.setSuffix(" cm\u207b\u00b9")
        self.v0_edit.valueChanged.connect(self.set_thermo)
        self.v0_edit.setMinimum(0)
        self.thermo_layout.addWidget(self.v0_edit, row, 1, 1, 2, Qt.AlignTop)
        
        row += 1

        self.thermo_layout.addWidget(QLabel("𝛿H ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)

        self.enthalpy_line = QLineEdit()
        self.enthalpy_line.setReadOnly(True)
        self.thermo_layout.addWidget(self.enthalpy_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)        

        row += 1

        self.thermo_layout.addWidget(QLabel("𝛿G<sub>RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)

        self.rrho_g_line = QLineEdit()
        self.rrho_g_line.setReadOnly(True)
        self.thermo_layout.addWidget(self.rrho_g_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)        
        
        row += 1
        
        self.thermo_layout.addWidget(QLabel("𝛿G<sub>Quasi-RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.qrrho_g_line = QLineEdit()
        self.qrrho_g_line.setReadOnly(True)
        self.thermo_layout.addWidget(self.qrrho_g_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.thermo_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)        
        
        row += 1
        
        self.thermo_layout.addWidget(QLabel("𝛿G<sub>Quasi-Harmonic</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.qharm_g_line = QLineEdit()
        self.qharm_g_line.setReadOnly(True)
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
        
        self.sum_layout.addWidget(QLabel("H ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.h_sum_line = QLineEdit()
        self.h_sum_line.setReadOnly(True)
        self.sum_layout.addWidget(self.h_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)      
        
        row += 1
        
        self.sum_layout.addWidget(QLabel("G<sub>RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.rrho_g_sum_line = QLineEdit()
        self.rrho_g_sum_line.setReadOnly(True)
        self.sum_layout.addWidget(self.rrho_g_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)        
        
        row += 1
        
        self.sum_layout.addWidget(QLabel("G<sub>Quasi-RRHO</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.qrrho_g_sum_line = QLineEdit()
        self.qrrho_g_sum_line.setReadOnly(True)
        self.sum_layout.addWidget(self.qrrho_g_sum_line, row, 1, 1, 1, Qt.AlignTop)
        
        self.sum_layout.addWidget(QLabel("E<sub>h</sub>"), row, 2, 1, 1, Qt.AlignTop)  
        
        row += 1
        
        self.sum_layout.addWidget(QLabel("G<sub>Quasi-Harmonic</sub> ="), row, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        
        self.qharm_g_sum_line = QLineEdit()
        self.qharm_g_sum_line.setReadOnly(True)
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

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
        
    def refresh_models(self, *args, **kwargs):
        models = self.session.filereader_manager.models
        
        comp_outs = [CompOutput(mdl.aarontools_filereader) for mdl in models]
        self.nrg_cos = {mdl:co for mdl, co in zip(models, comp_outs) if co.energy is not None}
        self.thermo_cos = {mdl:co for mdl, co in zip(models, comp_outs) if co.free_energy is not None}
        
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

            T = self.temperature_line.value()
            if not T:
                return
            
            dE, dH, s = co.therm_corr(temperature=T)
            rrho_dg = co.calc_G_corr(v0=0, temperature=T)
            qrrho_dg = co.calc_G_corr(v0=v0, temperature=T, quasi_harmonic=False)
            qharm_dg = co.calc_G_corr(v0=v0, temperature=T, quasi_harmonic=True)
            
            self.enthalpy_line.setText(repr(dH))
            self.rrho_g_line.setText(repr(rrho_dg))
            self.qrrho_g_line.setText(repr(qrrho_dg))
            self.qharm_g_line.setText(repr(qharm_dg))
        else:
            self.enthalpy_line.setText("")
            self.rrho_g_line.setText("")
            self.qrrho_g_line.setText("")
            self.qharm_g_line.setText("")
        
        self.update_sum()
        
    def update_sum(self):
        dH = self.enthalpy_line.text()
        dG = self.rrho_g_line.text()
        dG_qrrho = self.qrrho_g_line.text()
        dG_qharm = self.qharm_g_line.text()
        
        nrg = self.sp_nrg_line.text()
        
        if len(dH) == 0 or len(nrg) == 0:
            self.h_sum_line.setText("")
            self.rrho_g_sum_line.setText("")
            self.qrrho_g_sum_line.setText("")
            self.qharm_g_sum_line.setText("")
            return
        else:
            dH = float(dH)
            dG = float(dG)
            dG_qrrho = float(dG_qrrho)
            dG_qharm = float(dG_qharm)
            
            nrg = float(nrg)
            
            enthalpy = nrg + dH
            rrho_g = nrg + dG
            qrrho_g = nrg + dG_qrrho
            qharm_g = nrg + dG_qharm
            
            self.h_sum_line.setText(repr(enthalpy))
            self.rrho_g_sum_line.setText(repr(rrho_g))
            self.qrrho_g_sum_line.setText(repr(qrrho_g))
            self.qharm_g_sum_line.setText(repr(qharm_g))
        
    def delete(self):
        """overload delete"""
        self.session.filereader_manager.triggers.remove_handler(self._refresh_handler)
        super().delete()           