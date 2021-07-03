import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands import run
from chimerax.core.commands.cli import FloatArg, BoolArg, StringArg, IntArg

from numpy import isclose

from Qt.QtCore import Qt, Signal, QRegularExpression
from Qt.QtGui import QKeySequence, QIcon
from Qt.QtWidgets import (
    QLabel,
    QGridLayout,
    QSplitter,
    QLineEdit,
    QDoubleSpinBox,
    QMenuBar,
    QFileDialog,
    QAction,
    QApplication,
    QWidget,
    QGroupBox,
    QStatusBar,
    QTabWidget,
    QTreeWidget,
    QSizePolicy,
    QPushButton,
    QTreeWidgetItem,
    QStyle,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
)

from SEQCROW.widgets import FilereaderComboBox

from AaronTools.comp_output import CompOutput
from AaronTools.geometry import Geometry
from AaronTools.const import PHYSICAL, UNIT

class _ComputeThermoSettings(Settings):

    AUTO_SAVE = {
        'w0': Value(100.0, FloatArg, str),
        'include_header': Value(True, BoolArg, str),
        'delimiter': Value('comma', StringArg), 
        'rel_temp': Value(298.15, FloatArg, str), 
        'ref_col_1': Value(150, IntArg), 
        'ref_col_2': Value(150, IntArg), 
        'other_col_1': Value(150, IntArg), 
        'other_col_2': Value(150, IntArg), 
    }


class ReadOnlyTableItem(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)


class SmallLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if args:
            text = args[0]
            self.setMinimumWidth(int(1.5*self.fontMetrics().boundingRect(text).width()))
            self.setMaximumWidth(int(1.5*self.fontMetrics().boundingRect(text).width()))
        self.setAlignment(Qt.AlignCenter)


class Thermochem(ToolInstance):
    """tool for calculating free energy corrections based on frequencies and energies 
    associated with FileReaders
    there are two tabs: absolute and relative
    
    the absolute tab can be used to combine the thermo corrections from one
    FileReader with the energy of another
    
    the relative tab can do the same, but it prints the energies relative to
    those of another FileReader
    multiple molecule groups can be added (i.e. for reactions with multiple
    reactants and products)
    each molecule group can have multiple conformers
    the energies of these conformers are boltzmann weighted, and the boltzmann-weighted
    energy is used to calculate the energy of either the reference group or the 'other' group"""
    
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    help = "https://github.com/QChASM/SEQCROW/wiki/Process-Thermochemistry-Tool"

    theory_helper = {"Grimme's Quasi-RRHO":"https://doi.org/10.1002/chem.201200497",
                     "Truhlar's Quasi-Harmonic":"https://doi.org/10.1021/jp205508z"}
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.display_name = "Thermochemistry"
        
        self.tool_window = MainToolWindow(self)        

        self.settings = _ComputeThermoSettings(self.session, name)

        self.nrg_fr = {}
        self.thermo_fr = {}
        self.thermo_co = {}
        self._headers = []
        self._data = []

        self._build_ui()
        
        self.set_sp()
        self.set_thermo_mdl()
        
        self.calc_relative_thermo()

    def _build_ui(self):
        #each group has an empty widget at the bottom so they resize the way I want while also having the
        #labels where I want them
        layout = QGridLayout()

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        #layout for absolute thermo stuff
        absolute_widget = QWidget()
        absolute_layout = QGridLayout(absolute_widget)


        #box for sp
        sp_area_widget = QGroupBox("Single-point")
        sp_layout = QFormLayout(sp_area_widget)

        self.sp_selector = FilereaderComboBox(self.session, otherItems=['energy'])
        self.sp_selector.currentIndexChanged.connect(self.set_sp)
        sp_layout.addRow(self.sp_selector)
        
        self.sp_table = QTableWidget()
        self.sp_table.setColumnCount(3)
        self.sp_table.setShowGrid(False)
        self.sp_table.horizontalHeader().hide()
        self.sp_table.verticalHeader().hide()
        self.sp_table.setFrameShape(QTableWidget.NoFrame)
        self.sp_table.setSelectionMode(QTableWidget.NoSelection)
        self.sp_table.insertRow(0)
        sp_layout.addRow(self.sp_table)


        #box for thermo
        therm_area_widget = QGroupBox("Thermal corrections")
        thermo_layout = QFormLayout(therm_area_widget)

        self.thermo_selector = FilereaderComboBox(self.session, otherItems=['frequency'])
        self.thermo_selector.currentIndexChanged.connect(self.set_thermo_mdl)
        thermo_layout.addRow(self.thermo_selector)
        
        self.temperature_line = QDoubleSpinBox()
        self.temperature_line.setMaximum(2**31 - 1)
        self.temperature_line.setValue(298.15)
        self.temperature_line.setSingleStep(10)
        self.temperature_line.setSuffix(" K")
        self.temperature_line.setMinimum(0)
        self.temperature_line.valueChanged.connect(self.set_thermo)
        thermo_layout.addRow("T =", self.temperature_line)

        self.v0_edit = QDoubleSpinBox()
        self.v0_edit.setMaximum(4000)
        self.v0_edit.setValue(self.settings.w0)
        self.v0_edit.setSingleStep(25)
        self.v0_edit.setSuffix(" cm\u207b\u00b9")
        self.v0_edit.valueChanged.connect(self.set_thermo)
        self.v0_edit.setMinimum(0)
        self.v0_edit.setToolTip("frequency parameter for quasi treatments of entropy")
        thermo_layout.addRow("𝜔<sub>0</sub> =", self.v0_edit)

        self.thermo_table = QTableWidget()
        self.thermo_table.setColumnCount(3)
        self.thermo_table.setShowGrid(False)
        self.thermo_table.horizontalHeader().hide()
        self.thermo_table.verticalHeader().hide()
        self.thermo_table.setFrameShape(QTableWidget.NoFrame)
        self.thermo_table.setSelectionMode(QTableWidget.NoSelection)
        thermo_layout.addRow(self.thermo_table)


        # for for total
        sum_area_widget = QGroupBox("Thermochemistry")
        sum_layout = QFormLayout(sum_area_widget)

        self.sum_table = QTableWidget()
        self.sum_table.setColumnCount(3)
        self.sum_table.setShowGrid(False)
        self.sum_table.horizontalHeader().hide()
        self.sum_table.verticalHeader().hide()
        self.sum_table.setFrameShape(QTableWidget.NoFrame)
        self.sum_table.setSelectionMode(QTableWidget.NoSelection)
        sum_layout.addRow(self.sum_table)

        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(sp_area_widget)
        splitter.addWidget(therm_area_widget)
        splitter.addWidget(sum_area_widget)
        
        
        
        absolute_layout.addWidget(splitter)

        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        self.status.setStyleSheet("color: red")
        absolute_layout.addWidget(self.status, 1, 0, 1, 1, Qt.AlignTop)

        self.tab_widget.addTab(absolute_widget, "absolute")


        relative_widget = QWidget()
        relative_layout = QGridLayout(relative_widget)

        size = [self.settings.ref_col_1, self.settings.ref_col_2]
        self.ref_group = ThermoGroup("reference group", self.session, self.nrg_fr, self.thermo_co, size)
        self.ref_group.changes.connect(self.calc_relative_thermo)
        relative_layout.addWidget(self.ref_group, 0, 0, 1, 3, Qt.AlignTop)
        
        size = [self.settings.other_col_1, self.settings.other_col_2]
        self.other_group = ThermoGroup("other group", self.session, self.nrg_fr, self.thermo_co, size)
        self.other_group.changes.connect(self.calc_relative_thermo)
        relative_layout.addWidget(self.other_group, 0, 3, 1, 3, Qt.AlignTop)
        
        self.relative_temperature = QDoubleSpinBox()
        self.relative_temperature.setMaximum(2**31 - 1)
        self.relative_temperature.setValue(self.settings.rel_temp)
        self.relative_temperature.setSingleStep(10)
        self.relative_temperature.setSuffix(" K")
        self.relative_temperature.setMinimum(0)
        self.relative_temperature.valueChanged.connect(self.calc_relative_thermo)
        relative_layout.addWidget(QLabel("T ="), 1, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        relative_layout.addWidget(self.relative_temperature, 1, 1, 1, 5, Qt.AlignLeft | Qt.AlignVCenter)

        self.relative_v0 = QDoubleSpinBox()
        self.relative_v0.setMaximum(2**31 - 1)
        self.relative_v0.setValue(self.settings.w0)
        self.relative_v0.setSingleStep(25)
        self.relative_v0.setSuffix(" cm\u207b\u00b9")
        self.relative_v0.setMinimum(0)
        self.relative_v0.setToolTip("frequency parameter for quasi treatments of entropy")
        self.relative_v0.valueChanged.connect(self.calc_relative_thermo)
        relative_layout.addWidget(QLabel("𝜔<sub>0</sub> ="), 2, 0, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        relative_layout.addWidget(self.relative_v0, 2, 1, 1, 5, Qt.AlignLeft | Qt.AlignVCenter)

        relative_layout.addWidget(QLabel("Boltzmann-weighted relative energies in kcal/mol:"), 3, 0, 1, 6, Qt.AlignVCenter | Qt.AlignLeft)
        
        self.relative_table = QTextBrowser()
        self.relative_table.setMaximumHeight(
            4 * self.relative_table.fontMetrics().boundingRect("Q").height()
        )
        relative_layout.addWidget(self.relative_table, 4, 0, 1, 6, Qt.AlignTop)
        
        relative_layout.setRowStretch(0, 1)
        relative_layout.setRowStretch(1, 0)
        relative_layout.setRowStretch(2, 0)
        relative_layout.setRowStretch(3, 0)
        relative_layout.setRowStretch(4, 0)
        
        self.tab_widget.addTab(relative_widget, "relative")
        
        #menu stuff
        menu = QMenuBar()
        
        export = menu.addMenu("&Export")
        copy = QAction("&Copy CSV to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_csv)
        shortcut = QKeySequence(Qt.CTRL + Qt.Key_C)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        self.copy = copy
        
        save = QAction("&Save CSV...", self.tool_window.ui_area)
        save.triggered.connect(self.save_csv)
        #this shortcut interferes with main window's save shortcut
        #I've tried different shortcut contexts to no avail
        #thanks Qt...
        #shortcut = QKeySequence(Qt.CTRL + Qt.Key_S)
        #save.setShortcut(shortcut)
        #save.setShortcutContext(Qt.WidgetShortcut)
        export.addAction(save)

        delimiter = export.addMenu("Delimiter")
        
        comma = QAction("comma", self.tool_window.ui_area, checkable=True)
        comma.setChecked(self.settings.delimiter == "comma")
        comma.triggered.connect(lambda *args, delim="comma": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(comma)
        
        tab = QAction("tab", self.tool_window.ui_area, checkable=True)
        tab.setChecked(self.settings.delimiter == "tab")
        tab.triggered.connect(lambda *args, delim="tab": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(tab)
        
        space = QAction("space", self.tool_window.ui_area, checkable=True)
        space.setChecked(self.settings.delimiter == "space")
        space.triggered.connect(lambda *args, delim="space": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(space)
        
        semicolon = QAction("semicolon", self.tool_window.ui_area, checkable=True)
        semicolon.setChecked(self.settings.delimiter == "semicolon")
        semicolon.triggered.connect(lambda *args, delim="semicolon": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(semicolon)
        
        add_header = QAction("&Include CSV header", self.tool_window.ui_area, checkable=True)
        add_header.setChecked(self.settings.include_header)
        add_header.triggered.connect(self.header_check)
        export.addAction(add_header)
        
        comma.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        comma.triggered.connect(lambda *args, action=space: action.setChecked(False))
        comma.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        tab.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        tab.triggered.connect(lambda *args, action=space: action.setChecked(False))
        tab.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        space.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        space.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        space.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        semicolon.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        semicolon.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        semicolon.triggered.connect(lambda *args, action=space: action.setChecked(False))

        menu.setNativeMenuBar(False)
        self._menu = menu
        layout.setMenuBar(menu)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def calc_relative_thermo(self, *args):
        """changes the values on the 'relative' tab
        called when the tool is opened and whenever something changes on the relative tab"""
        def calc_free_energies(nrg_list, co_list, T, w0):
            """returns lists for ZPVE, H, RRHO G, QRRHO G, and QHARM G
            for the items in nrg_list and co_list at temperature T
            and frequency parameter w0"""
            ZPVEs = []
            if all(co.frequency.anharm_data for co_group in co_list for co in co_group):
                anharm_ZVPEs = []
            else:
                anharm_ZVPEs = None
            Hs = []
            Gs = []
            RRHOG = []
            QHARMG = []
            for i in range(0, len(nrg_list)):
                ZPVEs.append([])
                if anharm_ZVPEs is not None:
                    anharm_ZVPEs.append([])
                Hs.append([])
                Gs.append([])
                RRHOG.append([])
                QHARMG.append([])
                for nrg, co in zip(nrg_list[i], co_list[i]):
                    ZPVE = co.ZPVE
                    ZPVEs[-1].append(nrg + ZPVE)
                    
                    if anharm_ZVPEs is not None:
                        zpve_anharm = co.calc_zpe(anharmonic=True)
                        anharm_ZVPEs[-1].append(nrg + zpve_anharm)
                    
                    dH = co.therm_corr(T, w0, CompOutput.RRHO)[1]
                    Hs[-1].append(nrg + dH)
                    
                    dG = co.calc_G_corr(temperature=T, v0=w0, method=CompOutput.RRHO)
                    Gs[-1].append(nrg + dG)            
                    
                    dQRRHOG = co.calc_G_corr(temperature=T, v0=w0, method=CompOutput.QUASI_RRHO)
                    RRHOG[-1].append(nrg + dQRRHOG)
                    
                    dQHARMG = co.calc_G_corr(temperature=T, v0=w0, method=CompOutput.QUASI_HARMONIC)
                    QHARMG[-1].append(nrg + dQHARMG)
            
            return ZPVEs, anharm_ZVPEs, Hs, Gs, RRHOG, QHARMG
        
        def boltzmann_weight(energies1, energies2, T):
            """
            energies - list of lists
                       list axis 0 - molecule groups
                            axis 1 - energies of conformers
            boltzmann weight energies for conformers 
            combine energies for molecule groups 
            return the difference"""
            totals1 = []
            totals2 = []

            beta = UNIT.HART_TO_JOULE/(PHYSICAL.KB * T)
            
            for energy_group in energies1:
                if len(energy_group) == 0:
                    continue
                    
                rezero = min(energy_group)
                rel_nrgs = [(x - rezero) for x in energy_group]
                weights = [np.exp(-beta*nrg) for nrg in rel_nrgs]

                totals1.append(-PHYSICAL.BOLTZMANN * T * np.log(sum(weights)) + rezero * UNIT.HART_TO_KCAL)

            for energy_group in energies2:
                if len(energy_group) == 0:
                    continue
                    
                rezero = min(energy_group)
                rel_nrgs = [(x - rezero) for x in energy_group]
                weights = [np.exp(-beta*nrg) for nrg in rel_nrgs]

                totals2.append(-PHYSICAL.BOLTZMANN * T * np.log(sum(weights)) + rezero * UNIT.HART_TO_KCAL)

            return sum(totals2) - sum(totals1)

        ref_Es = self.ref_group.energies()
        ref_cos = self.ref_group.compOutputs()

        other_Es = self.other_group.energies()
        other_cos = self.other_group.compOutputs()

        if any(len(x) == 0  or all(len(y) == 0 for y in x) for x in [ref_Es, other_Es]):
            self.relative_table.setText("not enough data")
            return

        T = self.relative_temperature.value()
        self.settings.rel_temp = T
        w0 = self.relative_v0.value()

        if w0 != self.settings.w0:
            self.settings.w0 = w0

        rel_E = boltzmann_weight(ref_Es, other_Es, T)
        headers = ["ΔE"]
        data = [rel_E]

        empty_groups = []
        for i, group in enumerate(ref_cos):
            if len(group) == 0:
                empty_groups.append(i)
        for ndx in empty_groups[::-1]:
            ref_Es.pop(ndx)
            ref_cos.pop(ndx)

        empty_groups = []
        for i, group in enumerate(other_cos):
            if len(group) == 0:
                empty_groups.append(i)

        for ndx in empty_groups[::-1]:
            other_Es.pop(ndx)
            other_cos.pop(ndx)

        if not any(len(x) == 0  or all(len(y) == 0 for y in x) for x in [ref_cos, other_cos]):
            rel_E = boltzmann_weight(ref_Es, other_Es, T)
            data = [rel_E]

            ref_ZPVEs, ref_anharm_zpve, ref_Hs, ref_Gs, ref_QRRHOGs, ref_QHARMGs = calc_free_energies(
                ref_Es, ref_cos, T, w0
            )
            other_ZPVEs, other_anharm_zpve, other_Hs, other_Gs, other_QRRHOGs, other_QHARMGs = calc_free_energies(
                other_Es, other_cos, T, w0
            )

            rel_ZPVE = boltzmann_weight(ref_ZPVEs, other_ZPVEs, T)
            rel_H = boltzmann_weight(ref_Hs, other_Hs, T)
            rel_G = boltzmann_weight(ref_Gs, other_Gs, T)
            rel_QRRHOG = boltzmann_weight(ref_QRRHOGs, other_QRRHOGs, T)
            rel_QHARMG = boltzmann_weight(ref_QHARMGs, other_QHARMGs, T)
    
            if ref_anharm_zpve and other_anharm_zpve:
                rel_anharm_ZPVE = boltzmann_weight(ref_anharm_zpve, other_anharm_zpve, T)
                headers.extend([
                    "ΔZPE", "ΔZPE<sub>anh</sub>", "ΔH<sub>RRHO</sub>", "ΔG<sub>RRHO</sub>",
                    "ΔG<sub>Quasi-RRHO</sub>", "ΔG<sub>Quasi-Harmonic</sub>",
                ])
                data.extend([
                    rel_ZPVE,
                    rel_anharm_ZPVE,
                    rel_H,
                    rel_G,
                    rel_QRRHOG,
                    rel_QHARMG,
                ])
            else:
                headers.extend([
                    "ΔZPE", "ΔH<sub>RRHO</sub>", "ΔG<sub>RRHO</sub>",
                    "ΔG<sub>Quasi-RRHO</sub>", "ΔG<sub>Quasi-Harmonic</sub>",
                ])
                data.extend([
                    rel_ZPVE,
                    rel_H,
                    rel_G,
                    rel_QRRHOG,
                    rel_QHARMG,
                ])

        self._headers = headers
        self._data = data

        s = "<table style=\"border: 1px solid ghostwhite;\">\n"
        s += "\t<tr>\n"
        for header in headers:
            s += "\t\t<th style=\"text-align: center; border: 1px solid ghostwhite; padding-left: 5px;  padding-right: 5px\">%s</th>\n" % header
        s += "\t</tr>\n"
        s += "\t<tr>\n"
        for val in data:
            s += "\t\t<td style=\"text-align: center; border: 1px solid ghostwhite; padding-left: 5px;  padding-right: 5px\">%.1f</td>\n" % val
        s += "\t</tr>\n"
        s += "</table>"
        
        self.relative_table.setText(s)

    def open_link(self, theory):
        """open the oft-cited QRRHO or QHARM reference"""
        link = self.theory_helper[theory]
        run(self.session, "open %s" % link)

    def save_csv(self):
        """save data on current tab to CSV file"""
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
        if filename:
            s = self.get_csv()
   
            with open(filename, 'w') as f:
                f.write(s.strip())
                
            self.session.logger.status("saved to %s" % filename)

    def copy_csv(self):
        """put CSV data for current tab on the clipboard"""
        app = QApplication.instance()
        clipboard = app.clipboard()
        csv = self.get_csv()
        clipboard.setText(csv)
        self.session.logger.status("copied to clipboard")

    def get_csv(self):
        """get CSV data for the current tab"""
        if self.settings.delimiter == "comma":
            delim = ","
        elif self.settings.delimiter == "space":
            delim = " "
        elif self.settings.delimiter == "tab":
            delim = "\t"
        elif self.settings.delimiter == "semicolon":
            delim = ";"

        if self.tab_widget.currentIndex() == 0:
            s = ""
            if self.settings.include_header:
                link_re = QRegularExpression("<a[\d\D]*>(𝛿?Δ?[\d\D]*)</a>")
                # get header labels from the tables
                for table in [self.sp_table, self.thermo_table, self.sum_table]:
                    for row in range(0, table.rowCount()):
                        item = table.cellWidget(row, 0)
                        text = item.text()
                        text = text.replace(" =", "")
                        text = text.replace("<sub>", "(")
                        text = text.replace("</sub>", ")")
                        # if there's a link like for QRRHO G, remove the link
                        if "href=" in text:
                            match = link_re.match(text)
                            text = match.captured(1)
                        text = text.replace("𝛿", "d")
                        s += "%s%s" % (text, delim)

                s += "SP_File%sThermo_File\n" % delim

            # get values from tables
            for table in [self.sp_table, self.thermo_table, self.sum_table]:
                for row in range(0, table.rowCount()):
                    item = table.cellWidget(row, 1)
                    s += "%s%s" % (item.text(), delim)

            sp_mdl = self.sp_selector.currentData()
            sp_name = sp_mdl.name
            therm_mdl = self.thermo_selector.currentData()

            s += "%s" % sp_name
            if therm_mdl:
                therm_name = therm_mdl.name
                s += "%s%s" % (delim, therm_name)
            s += "\n"

        elif self.tab_widget.currentIndex() == 1:
            s = ""
            if self.settings.include_header:
                link_re = QRegularExpression("<a[\d\D]*>(𝛿?Δ?[\d\D]*)</a>")
                # get header labels from the tables
                for text in self._headers:
                    text = text.replace(" =", "")
                    text = text.replace("<sub>", "(")
                    text = text.replace("</sub>", ")")
                    # if there's a link like for QRRHO G, remove the link
                    if "href=" in text:
                        match = link_re.match(text)
                        text = match.captured(1)
                    text = text.replace("𝛿", "d")
                    s += "%s%s" % (text, delim)

            s = s.rstrip(delim)
            s += "\n"
            s += delim.join(["%.1f" % val for val in self._data])
        
        return s
    
    def header_check(self, state):
        """user has [un]checked the 'include header' option on the menu"""
        if state:
            self.settings.include_header = True
        else:
            self.settings.include_header = False
    
    def set_sp(self):
        """set energy entry for when sp model changes"""
        self.sp_table.setRowCount(0)
        if self.sp_selector.currentIndex() >= 0:
            fr = self.sp_selector.currentData()

            self.check_geometry_rmsd("SP")

            self.sp_table.insertRow(0)
            
            nrg_label = QLabel("E =")
            nrg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.sp_table.setCellWidget(0, 0, nrg_label)
            
            unit_label = ReadOnlyTableItem()
            unit_label.setData(Qt.DisplayRole, "E\u2095")
            unit_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.sp_table.setItem(0, 2, unit_label)

            sp_nrg = SmallLineEdit("%.6f" % fr.other['energy'])
            sp_nrg.setReadOnly(True)
            sp_nrg.setFrame(False)
            self.sp_table.setCellWidget(0, 1, sp_nrg)
            
            self.sp_table.resizeRowToContents(0)
            self.sp_table.resizeColumnToContents(0)
            self.sp_table.resizeColumnToContents(1)
            self.sp_table.resizeColumnToContents(2)

        self.update_sum()

    def set_thermo_mdl(self):
        """
        frequencies filereader has changed on the absolute tab
        also changes the temperature option (on the absolute tab only)
        """
        if self.thermo_selector.currentIndex() >= 0:
            fr = self.thermo_selector.currentData()
            
            self.check_geometry_rmsd("THERM")

            if 'temperature' in fr.other:
                self.temperature_line.setValue(fr.other['temperature'])

        self.set_thermo()

    def check_geometry_rmsd(self, *args):
        """check RMSD between energy and frequency filereader on the absolute tab
        if the RMSD is > 10^-5 or the number of atoms is different, put a warning in the
        status bar"""
        if self.thermo_selector.currentIndex() >= 0 and self.sp_selector.currentIndex() >= 0:
            fr = self.sp_selector.currentData()
            fr2 = self.thermo_selector.currentData()

            if len(fr.atoms) != len(fr2.atoms):
                self.status.showMessage("structures are not the same: different number of atoms")
                return

            geom = Geometry(fr)
            geom2 = Geometry(fr2)
            rmsd = geom.RMSD(geom2)
            if not isclose(rmsd, 0, atol=10**-5):
                rmsd = geom.RMSD(geom2, sort=True)
            
            if not isclose(rmsd, 0, atol=10**-5):
                self.status.showMessage("structures might not be the same - RMSD = %.4f" % rmsd)
            else:
                self.status.showMessage("")

    def set_thermo(self):
        """computes thermo corrections and sets thermo entries for when thermo model changes"""
        #index of combobox is -1 when combobox has no entries
        self.thermo_table.setRowCount(0)
        if self.thermo_selector.currentIndex() >= 0:
            fr = self.thermo_selector.currentData()
            if fr not in self.thermo_co:
                self.thermo_co[fr] = CompOutput(fr)
            co = self.thermo_co[fr]

            v0 = self.v0_edit.value()

            if v0 != self.settings.w0:
                self.settings.w0 = v0

            T = self.temperature_line.value()
            if not T:
                return

            dZPE = co.ZPVE
            #compute enthalpy and entropy at this temperature
            #AaronTools uses Grimme's Quasi-RRHO, but this is the same as RRHO when w0=0
            dE, dH, s = co.therm_corr(temperature=T, v0=0, method="RRHO")
            rrho_dg = dH - T * s
            #compute G with quasi entropy treatments
            qrrho_dg = co.calc_G_corr(v0=v0, temperature=T, method="QRRHO")
            qharm_dg = co.calc_G_corr(v0=v0, temperature=T, method="QHARM")
            
            items = [(
                "𝛿ZPE =",
                dZPE,
                None,
                "lowest energy the molecule can have\n"
                "no rotational or vibrational modes populated\n"
                "equal to enthalpy at 0 K",
            )]

            if fr.other["frequency"].anharm_data:
                dZPE_anh = co.calc_zpe(anharmonic=True)
                items.append((
                    "𝛿ZPE<sub>anh</sub> =",
                    dZPE_anh,
                    None,
                    "lowest energy the molecule can have\n"
                    "no rotational or vibrational modes populated\n"
                    "includes corrections for anharmonic vibrations",
                ))
            
            items.extend([
                (
                    "𝛿H<sub>RRHO</sub> =",
                    dH,
                    None,
                    "enthalpy of formation",
                ), (
                    "𝛿G<sub>RRHO</sub> =",
                    rrho_dg,
                    None,
                    "energy after taking into account the average\n"
                    "population of vibrational, rotational, and translational\n"
                    "degrees of freedom",
                ), (
                    "𝛿G<sub>Quasi-RRHO</sub> =",
                    qrrho_dg,
                    "Grimme's Quasi-RRHO",
                    "vibrational entropy of each real mode is damped and complemented\n"
                    "with rotational entropy, with the damping function being stronger for\n"
                    "frequencies < 𝜔\u2080\n"
                    "can mitigate error from inaccuracies in the harmonic oscillator\n"
                    "approximation for low-frequency vibrations",
                ), (
                    "𝛿G<sub>Quasi-Harmonic</sub> =",
                    qharm_dg,
                    "Truhlar's Quasi-Harmonic",
                    "real vibrational frequencies below 𝜔\u2080 are treated as 𝜔\u2080\n"
                    "can mitigate error from inaccuracies in the harmonic oscillator\n"
                    "approximation for low-frequency vibrations",
                ),
            ])
            
            for i, (label_text, val, link, tooltip) in enumerate(items):
                self.thermo_table.insertRow(i)
                
                label = QLabel(label_text)
                if link:
                    label = QLabel()
                    label.setText("<a href=\"%s\" style=\"text-decoration: none;\">%s</a>" % (link, label_text))
                    label.setTextFormat(Qt.RichText)
                    label.setTextInteractionFlags(Qt.TextBrowserInteraction)
                    label.linkActivated.connect(self.open_link)

                label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                label.setToolTip(tooltip)

                self.thermo_table.setCellWidget(i, 0, label)

                unit_label = ReadOnlyTableItem()
                unit_label.setData(Qt.DisplayRole, "E\u2095")
                unit_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                unit_label.setToolTip(tooltip)
                self.thermo_table.setItem(i, 2, unit_label)

                d_nrg = SmallLineEdit("%.6f" % val)
                d_nrg.setReadOnly(True)
                d_nrg.setFrame(False)
                d_nrg.setToolTip(tooltip)
                self.thermo_table.setCellWidget(i, 1, d_nrg)

                self.thermo_table.resizeRowToContents(i)
            
            self.thermo_table.resizeColumnToContents(0)
            self.thermo_table.resizeColumnToContents(1)
            self.thermo_table.resizeColumnToContents(2)

        self.update_sum()

    def update_sum(self):
        """updates the sum of energy and thermo corrections"""
        self.sum_table.setRowCount(0)

        if not self.sp_table.rowCount():
            return

        sp_nrg = float(self.sp_table.cellWidget(0, 1).text())

        for row in range(0, self.thermo_table.rowCount()):
            self.sum_table.insertRow(row)

            label = self.thermo_table.cellWidget(row, 0)
            tooltip = label.toolTip()
            text = label.text().replace("𝛿", "")
            sum_label = QLabel(text)
            if "href=" in text:
                sum_label = QLabel()
                sum_label.setText(text)
                sum_label.setTextFormat(Qt.RichText)
                sum_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
                sum_label.linkActivated.connect(self.open_link)

            sum_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            sum_label.setToolTip(tooltip)

            self.sum_table.setCellWidget(row, 0, sum_label)

            thermo = float(self.thermo_table.cellWidget(row, 1).text())

            total = sp_nrg + thermo
            total_nrg = SmallLineEdit("%.6f" % total)
            total_nrg.setFrame(False)
            total_nrg.setReadOnly(True)
            total_nrg.setToolTip(tooltip)
            self.sum_table.setCellWidget(row, 1, total_nrg)

            unit_label = ReadOnlyTableItem()
            unit_label.setData(Qt.DisplayRole, "E\u2095")
            unit_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            unit_label.setToolTip(tooltip)
            self.sum_table.setItem(row, 2, unit_label)

            self.sum_table.resizeRowToContents(row)
        
        self.sum_table.resizeColumnToContents(0)
        self.sum_table.resizeColumnToContents(1)
        self.sum_table.resizeColumnToContents(2)
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")

    def delete(self):
        #overload because closing a tool window doesn't destroy any widgets on it
        self.settings.ref_col_1 = self.ref_group.tree.columnWidth(0)
        self.settings.ref_col_2 = self.ref_group.tree.columnWidth(1)
        
        self.settings.other_col_1 = self.other_group.tree.columnWidth(0)
        self.settings.other_col_2 = self.other_group.tree.columnWidth(1)
        
        self.sp_selector.deleteLater()
        self.thermo_selector.deleteLater()
        self.ref_group.deleteLater()
        self.other_group.deleteLater()
        
        return super().delete()           

    def close(self):
        #overload because closing a tool window doesn't destroy any widgets on it
        self.settings.ref_col_1 = self.ref_group.tree.columnWidth(0)
        self.settings.ref_col_2 = self.ref_group.tree.columnWidth(1)
        
        self.settings.other_col_1 = self.other_group.tree.columnWidth(0)
        self.settings.other_col_2 = self.other_group.tree.columnWidth(1)
        
        self.sp_selector.deleteLater()
        self.thermo_selector.deleteLater()
        self.ref_group.deleteLater()
        self.other_group.deleteLater()
        
        return super().close()           


class ThermoGroup(QWidget):
    """widget used for the 'other' and 'reference' frames on the relative tab"""
    changes = Signal()
    
    def __init__(self, name, session, nrg_fr, thermo_co, size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.session = session
        self.nrg_fr = nrg_fr
        self.thermo_co = thermo_co
        
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setRowStretch(0, 1)
        
        frame = QGroupBox(name)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        frame_layout = QGridLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setRowStretch(0, 1)
        
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["energy", "frequencies", "remove"])
        self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tree.setColumnWidth(0, size[0])
        self.tree.setColumnWidth(1, size[1])
        self.tree.resizeColumnToContents(2)
        
        root_item = self.tree.invisibleRootItem()
        plus = QTreeWidgetItem(root_item)
        plus_button = QPushButton("add molecule")
        plus_button.setFlat(True)
        plus_button.clicked.connect(self.add_mol_group)        
        plus_button2 = QPushButton("")
        plus_button2.setFlat(True)
        plus_button2.clicked.connect(self.add_mol_group)
        self.tree.setItemWidget(plus, 0, plus_button)
        self.tree.setItemWidget(plus, 1, plus_button2)
        self.tree.insertTopLevelItem(1, plus)
        
        self.add_mol_group()
        
        frame_layout.addWidget(self.tree)

        layout.addWidget(frame)
    
    def add_mol_group(self, *args):
        row = self.tree.topLevelItemCount()
        
        root_item = self.tree.invisibleRootItem()
        
        mol_group = QTreeWidgetItem(root_item)
        self.tree.insertTopLevelItem(row, mol_group)
        trash_button = QPushButton()
        trash_button.setFlat(True)
        
        trash_button.clicked.connect(lambda *args, parent=mol_group: self.remove_mol_group(parent))
        trash_button.setIcon(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)))
        
        add_conf_button = QPushButton("add conformer")
        add_conf_button.setFlat(True)
        add_conf_button.clicked.connect(lambda *args, conf_group_widget=mol_group: self.add_conf_group(conf_group_widget))
        
        add_conf_button2 = QPushButton("")
        add_conf_button2.setFlat(True)
        add_conf_button2.clicked.connect(lambda *args, conf_group_widget=mol_group: self.add_conf_group(conf_group_widget))
        
        add_conf_child = QTreeWidgetItem(mol_group)
        self.tree.setItemWidget(add_conf_child, 0, add_conf_button)
        self.tree.setItemWidget(add_conf_child, 1, add_conf_button2)
        self.tree.setItemWidget(mol_group, 2, trash_button)
        
        mol_group.setText(0, "group %i" % row)
        
        mol_group.addChild(add_conf_child)
        self.add_conf_group(mol_group)

        self.tree.expandItem(mol_group)

        self.changes.emit()

    def add_conf_group(self, conf_group_widget):
        row = conf_group_widget.childCount()
        
        conformer_item = QTreeWidgetItem(conf_group_widget)
        conf_group_widget.insertChild(row, conformer_item)
        
        nrg_combobox = FilereaderComboBox(self.session, otherItems=['energy'])
        nrg_combobox.currentIndexChanged.connect(lambda *args: self.changes.emit())
        freq_combobox = FilereaderComboBox(self.session, otherItems=['frequency'])
        freq_combobox.currentIndexChanged.connect(lambda *args: self.changes.emit())
        
        trash_button = QPushButton()
        trash_button.setFlat(True)
        trash_button.clicked.connect(lambda *args, combobox=nrg_combobox: combobox.deleteLater())
        trash_button.clicked.connect(lambda *args, combobox=freq_combobox: combobox.deleteLater())
        trash_button.clicked.connect(lambda *args, child=conformer_item: conf_group_widget.removeChild(child))
        trash_button.clicked.connect(lambda *args: self.changes.emit())
        trash_button.setIcon(QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton)))
        
        self.tree.setItemWidget(conformer_item, 0, nrg_combobox)
        self.tree.setItemWidget(conformer_item, 1, freq_combobox)
        self.tree.setItemWidget(conformer_item, 2, trash_button)
        
        self.changes.emit()

    def compOutputs(self):
        out = []
        for mol_index in range(1, self.tree.topLevelItemCount()):
            out.append([])
            mol = self.tree.topLevelItem(mol_index)
            for conf_ndx in range(1, mol.childCount()):
                conf = mol.child(conf_ndx)
                fr = self.tree.itemWidget(conf, 1).currentData()
                if fr is None:
                    continue
                
                if fr not in self.thermo_co:
                    self.thermo_co[fr] = CompOutput(fr)
                out[-1].append(self.thermo_co[fr])
        
        return out
    
    def energies(self):
        out = []
        for mol_index in range(1, self.tree.topLevelItemCount()):
            out.append([])
            mol = self.tree.topLevelItem(mol_index)
            for conf_ndx in range(1, mol.childCount()):
                conf = mol.child(conf_ndx)
                fr = self.tree.itemWidget(conf, 0).currentData()
                if fr is None:
                    continue

                out[-1].append(fr.other['energy'])
        
        return out
    
    def remove_mol_group(self, parent):
        for conf_ndx in range(1, parent.childCount()):
            conf = parent.child(conf_ndx)
            self.tree.itemWidget(conf, 0).destroy()
            self.tree.itemWidget(conf, 1).destroy()
        
        ndx = self.tree.indexOfTopLevelItem(parent)
        self.tree.takeTopLevelItem(ndx)
        
        self.changes.emit()

    def deleteLater(self):
        for mol_index in range(1, self.tree.topLevelItemCount()):
            mol = self.tree.topLevelItem(mol_index)
            for conf_ndx in range(1, mol.childCount()):
                conf = mol.child(conf_ndx)
                self.tree.itemWidget(conf, 0).deleteLater()
                self.tree.itemWidget(conf, 1).deleteLater()
        
        super().deleteLater()

