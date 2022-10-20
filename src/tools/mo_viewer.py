from os import cpu_count

from chimerax.atomic import Atoms
from chimerax.core.commands import run
from chimerax.core.commands.cli import TupleOf, FloatArg
from chimerax.core.configfile import Value
from chimerax.core.objects import Objects
from chimerax.core.tools import ToolInstance
from chimerax.label.label3d import label
from chimerax.map.volume import Volume, RenderingOptions
from chimerax.map_data.griddata import GridData
from chimerax.core.settings import Settings
from chimerax.ui.gui import MainToolWindow
from chimerax.ui.widgets import ColorButton

import numpy as np

from Qt.QtCore import Qt
from Qt.QtWidgets import (
    QPushButton,
    QDoubleSpinBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QFormLayout,
    QCheckBox,
    QHBoxLayout,
    QWidget,
    QHeaderView,
    QTableWidgetSelectionRange,
    QMessageBox,
    QSizePolicy,
    QTabWidget,
    QGroupBox,
    QLabel,
    QComboBox,
)

from AaronTools.fileIO import Orbitals
from AaronTools.utils.utils import available_memory

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.widgets import FilereaderComboBox
from SEQCROW.utils import iter2str


class OrbitalGrid(GridData):
    polar_values = True
    
    def read_matrix(self,
        ijk_origin=(0,0,0),
        ijk_size=None,
        ijk_step=(1,1,1),
        progress=None,
    ):
        if ijk_size is None:
            ijk_size = self.data.shape
        return self._data[
            ijk_origin[2]:ijk_size[2] + ijk_origin[2]:ijk_step[2],
            ijk_origin[1]:ijk_size[1] + ijk_origin[1]:ijk_step[1],
            ijk_origin[0]:ijk_size[0] + ijk_origin[0]:ijk_step[0]
        ]
    
    def matrix(
        self,
        ijk_origin=(0,0,0),
        ijk_size=None,
        ijk_step=(1,1,1),
        progress=None,
        from_cache_only=False
    ):
        if ijk_size is None:
            ijk_size = self.data.shape
        return self._data[
            ijk_origin[2]:ijk_size[2] + ijk_origin[2]:ijk_step[2],
            ijk_origin[1]:ijk_size[1] + ijk_origin[1]:ijk_step[1],
            ijk_origin[0]:ijk_size[0] + ijk_origin[0]:ijk_step[0]
        ]


class _OrbitalSettings(Settings):
    AUTO_SAVE = {
        "color1": Value((0.0, 1.0, 0.0, 0.5), TupleOf(FloatArg, 4), iter2str),
        "color2": Value((0.0, 0.0, 1.0, 0.5), TupleOf(FloatArg, 4), iter2str),
        "keep_open": True,
        "padding": 3.0,
        "spacing": 0.20,
        "iso_val": 0.025,
        "threads": int(cpu_count() // 2),
        "ed_color": Value((1.0, 1.0, 1.0, 0.5), TupleOf(FloatArg, 4), iter2str),
        "ed_iso_val": 0.001,
        "ed_low_mem": False,
        "fd_color": Value((1.0, 0.0, 0.0, 0.5), TupleOf(FloatArg, 4), iter2str),
        "fa_color": Value((1.0, 1.0, 0.0, 0.5), TupleOf(FloatArg, 4), iter2str),
        "fd_iso_val": 0.01,
        "fukui_delta": 0.1,
        "fa_low_mem": False,
        "n_radial": "20",
        "n_angular": "194",
        "vdw_radii": "UMN",
    }


class OrbitalTableItem(QTableWidgetItem):
    def __lt__(self, other):
        if isinstance(self.data(Qt.UserRole), tuple):
            return self.data(Qt.UserRole)[0] < other.data(Qt.UserRole)[0]
        return self.data(Qt.UserRole) < other.data(Qt.UserRole)


class OrbitalViewer(ToolInstance):
    
    help = "https://github.com/QChASM/SEQCROW/wiki/Orbital-Tool"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)
       
        self.settings = _OrbitalSettings(session, name)

        self.alpha_occ = None
        self.beta_occ = None

        self._build_ui()
    
        self.fill_orbits(0)

    def _build_ui(self):
        layout = QFormLayout()

        self.model_selector = FilereaderComboBox(self.session, otherItems=['orbitals'])
        self.model_selector.currentIndexChanged.connect(self.fill_orbits)
        layout.addRow(self.model_selector)

        tabs = QTabWidget()

        orbit_tab = QWidget()
        orbit_layout = QFormLayout(orbit_tab)

        self.mo_table = QTableWidget()
        self.mo_table.setColumnCount(3)
        self.mo_table.setHorizontalHeaderLabels(
            ["#", "Ground State Occ.", "Energy (E\u2095)"]
        )
        self.mo_table.horizontalHeader().setStretchLastSection(False)
        self.mo_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.mo_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.mo_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.mo_table.setSortingEnabled(True)
        self.mo_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.mo_table.setSelectionMode(QTableWidget.SingleSelection)
        self.mo_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.mo_table.verticalHeader().setVisible(False)
        self.mo_table.resizeColumnToContents(0)
        self.mo_table.resizeColumnToContents(1)
        self.mo_table.resizeColumnToContents(2)
        orbit_layout.addRow(self.mo_table)

        draw_orbits = QPushButton("view selected orbital")
        draw_orbits.clicked.connect(self.show_orbit)
        orbit_layout.addRow(draw_orbits)
        
        tabs.addTab(orbit_tab, "orbitals")


        options_tab = QWidget()
        options_layout = QFormLayout(options_tab)

        self.padding = QDoubleSpinBox()
        self.padding.setRange(0.25, 10.)
        self.padding.setDecimals(2)
        self.padding.setValue(self.settings.padding)
        self.padding.setSingleStep(0.25)
        self.padding.setSuffix(" \u212B")
        options_layout.addRow("padding:", self.padding)

        self.spacing = QDoubleSpinBox()
        self.spacing.setRange(0.05, 0.75)
        self.spacing.setDecimals(2)
        self.spacing.setValue(self.settings.spacing)
        self.spacing.setSingleStep(0.05)
        self.spacing.setSuffix(" \u212B")
        options_layout.addRow("resolution:", self.spacing)

        color_options = QWidget()
        color_layout = QHBoxLayout(color_options)
        color_layout.setContentsMargins(5, 0, 5, 0)
        
        self.pos_color = ColorButton(has_alpha_channel=True, max_size=(16, 16))
        self.pos_color.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.pos_color.set_color(self.settings.color1)
        color_layout.insertWidget(0, self.pos_color, 0, Qt.AlignLeft | Qt.AlignVCenter)
        
        self.neg_color = ColorButton(has_alpha_channel=True, max_size=(16, 16))
        self.neg_color.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.neg_color.set_color(self.settings.color2)
        color_layout.insertWidget(1, self.neg_color, 0, Qt.AlignLeft | Qt.AlignVCenter)
        
        # widget for alignment
        color_layout.insertWidget(2, QWidget(), 1)
        
        options_layout.addRow("colors:", color_options)
        
        self.iso_value = QDoubleSpinBox()
        self.iso_value.setDecimals(4)
        self.iso_value.setRange(1e-4, 1)
        self.iso_value.setSingleStep(0.001)
        self.iso_value.setValue(self.settings.iso_val)
        options_layout.addRow("isosurface:", self.iso_value)

        self.threads = QSpinBox()
        self.threads.setRange(1, cpu_count())
        self.threads.setValue(self.settings.threads)
        options_layout.addRow("multithread calculation:", self.threads)

        self.keep_open = QCheckBox()
        self.keep_open.setCheckState(Qt.Checked if self.settings.keep_open else Qt.Unchecked)
        options_layout.addRow("cache previous surfaces:", self.keep_open)

        self.low_mem_mode = QCheckBox()
        self.low_mem_mode.setCheckState(
            Qt.Checked if self.settings.ed_low_mem else Qt.Unchecked
        )
        self.low_mem_mode.setToolTip(
            "use less memory at the cost of performance\n"
            "when calculating electron density\n"
            "expect calculation to take the time to calculate\n"
            "an orbital multiplied by the number of electrons\n"
            "divide by 2 if closed shell\n"
            "memory usage is the same as orbital calculation\n"
            "Note: this will not impact orbitals, only electron density"
        )
        options_layout.addRow("low memory denisities:", self.low_mem_mode)
        

        tabs.addTab(options_tab, "orbital settings")


        other_surface_tab = QWidget()
        other_surface_layout = QFormLayout(other_surface_tab)
        
        self.e_density_group = QGroupBox("electron density")
        e_density_layout = QFormLayout(self.e_density_group)
        other_surface_layout.addRow(self.e_density_group)
        
        self.ed_color = ColorButton(has_alpha_channel=True, max_size=(16, 16))
        self.ed_color.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.ed_color.set_color(self.settings.ed_color)
        e_density_layout.addRow("color:", self.ed_color)
        
        self.ed_iso_value = QDoubleSpinBox()
        self.ed_iso_value.setDecimals(4)
        self.ed_iso_value.setRange(1e-4, 5)
        self.ed_iso_value.setSingleStep(1e-3)
        self.ed_iso_value.setValue(self.settings.ed_iso_val)
        e_density_layout.addRow("isosurface:", self.ed_iso_value)

        show_e_density = QPushButton("calculate SCF electron density")
        show_e_density.clicked.connect(self.show_e_density)
        e_density_layout.addRow(show_e_density)
        

        self.fukui_group = QGroupBox("Fukui functions")
        fukui_layout = QFormLayout(self.fukui_group)
        other_surface_layout.addRow(self.fukui_group)
        
        
        self.fukui_type = QComboBox()
        self.fukui_type.addItems(["volume", "condensed"])
        self.fukui_type.currentTextChanged.connect(self.show_fukui_options)
        fukui_layout.addRow("display type:", self.fukui_type)

        self.fukui_volume_widget = QWidget()
        fukui_volume_layout = QFormLayout(self.fukui_volume_widget)
        fukui_volume_layout.setContentsMargins(0, 0, 0, 0)


        fukui_color_options = QWidget()
        color_layout = QHBoxLayout(fukui_color_options)
        color_layout.setContentsMargins(5, 0, 5, 0)

        f_plus = QLabel("")
        f_plus.setText("<a href=\"test\" style=\"text-decoration: none;\"><i>f</i><sub>w</sub><sup>-</sup>:</a>")
        f_plus.setTextFormat(Qt.RichText)
        f_plus.setTextInteractionFlags(Qt.TextBrowserInteraction)
        f_plus.linkActivated.connect(
            lambda *args, doi="doi:10.1002/jcc.24699": self.open_link(doi)
        )
        color_layout.insertWidget(0, f_plus, 0, Qt.AlignRight | Qt.AlignVCenter)

        self.fd_color = ColorButton(has_alpha_channel=True, max_size=(16, 16))
        self.fd_color.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.fd_color.set_color(self.settings.fd_color)
        color_layout.insertWidget(1, self.fd_color, 0, Qt.AlignLeft | Qt.AlignVCenter)
        
        f_minus = QLabel("")
        f_minus.setText("<a href=\"test\" style=\"text-decoration: none;\"><i>f</i><sub>w</sub><sup>+</sup>:</a>")
        f_minus.setTextFormat(Qt.RichText)
        f_minus.setTextInteractionFlags(Qt.TextBrowserInteraction)
        f_minus.linkActivated.connect(
            lambda *args, doi="10.1021/acs.jpca.9b07516": self.open_link(doi)
        )
        color_layout.insertWidget(2, f_minus, 0, Qt.AlignRight | Qt.AlignVCenter)

        self.fa_color = ColorButton(has_alpha_channel=True, max_size=(16, 16))
        self.fa_color.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.fa_color.set_color(self.settings.fa_color)
        color_layout.insertWidget(3, self.fa_color, 0, Qt.AlignLeft | Qt.AlignVCenter)
        
        # widget for alignment
        color_layout.insertWidget(4, QWidget(), 1, Qt.AlignLeft)
        
        fukui_volume_layout.addRow("colors:", fukui_color_options)

        self.fd_iso_value = QDoubleSpinBox()
        self.fd_iso_value.setDecimals(4)
        self.fd_iso_value.setRange(1e-4, 5)
        self.fd_iso_value.setSingleStep(1e-3)
        self.fd_iso_value.setValue(self.settings.fd_iso_val)
        fukui_volume_layout.addRow("isosurface:", self.fd_iso_value)

        
        self.fukui_condensed_widget = QWidget()
        fukui_condensed_layout = QFormLayout(self.fukui_condensed_widget)
        fukui_condensed_layout.setContentsMargins(0, 0, 0, 0)
        
        self.vdw_radii = QComboBox()
        self.vdw_radii.addItems(["UMN", "Bondi"])
        ndx = self.vdw_radii.findText(self.settings.vdw_radii, Qt.MatchExactly)
        if ndx >= 0:
            self.vdw_radii.setCurrentIndex(ndx)
        fukui_condensed_layout.addRow("radii:", self.vdw_radii)
        
        
        n_radial = [20, 32, 64, 75, 99, 127]
        n_angular = [110, 194, 302, 590, 974, 1454, 2030, 2702, 5810]
        
        self.radial = QComboBox()
        self.angular = QComboBox()
        for widget, data in zip([self.radial, self.angular], [n_radial, n_angular]):
            for i, n in enumerate(data):
                widget.addItem(str(n))
                widget.setItemData(i, n)
        ndx = self.radial.findText(self.settings.n_radial, Qt.MatchExactly)
        if ndx >= 0:
            self.radial.setCurrentIndex(ndx)
        ndx = self.angular.findText(self.settings.n_angular, Qt.MatchExactly)
        if ndx >= 0:
            self.angular.setCurrentIndex(ndx)

        fukui_condensed_layout.addRow("radial points:", self.radial)
        fukui_condensed_layout.addRow("angular points:", self.angular)

        
        fukui_layout.addRow(self.fukui_volume_widget)
        fukui_layout.addRow(self.fukui_condensed_widget)
        self.fukui_condensed_widget.setVisible(False)
        

        self.fukui_delta = QDoubleSpinBox()
        self.fukui_delta.setDecimals(2)
        self.fukui_delta.setRange(1e-2, 5)
        self.fukui_delta.setSingleStep(1e-2)
        self.fukui_delta.setValue(self.settings.fukui_delta)
        self.fukui_delta.setSuffix(" E\u2095")
        self.fukui_delta.setToolTip(
            "width of gaussian function for weighting orbitals"
        )
        fukui_layout.addRow("Δ parameter:", self.fukui_delta)

        show_fukui_donor = QPushButton("calculate Fukui donor")
        show_fukui_donor.clicked.connect(self.show_fukui_donor)
        fukui_layout.addRow(show_fukui_donor)

        show_fukui_acceptor = QPushButton("calculate Fukui acceptor")
        show_fukui_acceptor.clicked.connect(self.show_fukui_acceptor)
        fukui_layout.addRow(show_fukui_acceptor)

        show_fukui_dual = QPushButton("calculate Fukui dual")
        show_fukui_dual.clicked.connect(self.show_fukui_dual)
        fukui_layout.addRow(show_fukui_dual)
        
        
        tabs.addTab(other_surface_tab, "other surfaces")

        layout.addRow(tabs)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def show_fukui_options(self, text):
        if text == "volume":
            self.fukui_volume_widget.setVisible(True)
            self.fukui_condensed_widget.setVisible(False)
        else:
            self.fukui_volume_widget.setVisible(False)
            self.fukui_condensed_widget.setVisible(True)

    def fill_orbits(self, ndx):
        self.mo_table.setRowCount(0)
        
        self.alpha_occ = None
        self.beta_occ = None

        if ndx == -1:
            return
        
        fr = self.model_selector.currentData()
        if fr is None:
            return
        
        orbits = fr.other["orbitals"]

        self.fukui_group.setEnabled(True)
        self.e_density_group.setEnabled(True)

        homo_ndx = 0
        if orbits.alpha_occupancies and not orbits.beta_occupancies:
            if not all(np.isclose(occ, 1) or np.isclose(occ, 0) for occ in orbits.alpha_occupancies):
                self.fukui_group.setEnabled(False)
            if "orbit_kinds" not in fr.other:
                self.mo_table.setColumnCount(3)
                self.mo_table.setHorizontalHeaderLabels(
                    ["#", "alpha + beta occ.", "Energy (E\u2095)"]
                )
            else:
                self.mo_table.setColumnCount(2)
                self.mo_table.setHorizontalHeaderLabels(
                    ["#", "Type"]
                )
            for i, nrg in enumerate(orbits.alpha_nrgs[::-1]):
                row = self.mo_table.rowCount()
                self.mo_table.insertRow(row)
                
                ndx = OrbitalTableItem()
                ndx_str = str(orbits.n_mos - i)
                ndx.setData(Qt.DisplayRole, ndx_str)
                ndx.setData(Qt.UserRole, orbits.n_mos - i - 1)
                ndx.setTextAlignment(Qt.AlignCenter)
                self.mo_table.setItem(row, 0, ndx)
                
                occ = 2 * orbits.alpha_occupancies[orbits.n_mos - i - 1]

                occupancy = OrbitalTableItem()
                occupancy.setData(Qt.DisplayRole, "%.5f" % occ)
                occupancy.setData(Qt.UserRole, occ)
                occupancy.setTextAlignment(Qt.AlignCenter)
                self.mo_table.setItem(row, 1, occupancy)
                
                nrg_str = "%.5f" % nrg
                orbit_nrg = OrbitalTableItem()
                orbit_nrg.setData(Qt.DisplayRole, nrg_str)
                orbit_nrg.setData(Qt.UserRole, nrg)
                orbit_nrg.setTextAlignment(Qt.AlignCenter)
                self.mo_table.setItem(row, 2, orbit_nrg)
            if not homo_ndx:
                homo_ndx = orbits.n_mos - max(orbits.n_alpha, orbits.n_beta)
        elif orbits.alpha_occupancies and orbits.beta_occupancies:
            self.fukui_group.setEnabled(False)
            if "orbit_kinds" not in fr.other:
                self.mo_table.setColumnCount(3)
                self.mo_table.setHorizontalHeaderLabels(
                    ["#", "alpha occ.", "beta occ.", "Energy (E\u2095)"]
                )
            else:
                self.mo_table.setColumnCount(2)
                self.mo_table.setHorizontalHeaderLabels(
                    ["#", "Type"]
                )
            for i, nrg in enumerate(orbits.alpha_nrgs[::-1]):
                row = self.mo_table.rowCount()
                self.mo_table.insertRow(row)
                
                ndx = OrbitalTableItem()
                ndx_str = str(orbits.n_mos - i)
                ndx.setData(Qt.DisplayRole, ndx_str)
                ndx.setData(Qt.UserRole, orbits.n_mos - i - 1)
                ndx.setTextAlignment(Qt.AlignCenter)
                self.mo_table.setItem(row, 0, ndx)
                
                alpha_occ = orbits.alpha_occupancies[orbits.n_mos - i - 1]
                beta_occ = orbits.beta_occupancies[orbits.n_mos - i - 1]

                a_occupancy = OrbitalTableItem()
                a_occupancy.setData(Qt.DisplayRole, "%.5f" % alpha_occ)
                a_occupancy.setData(Qt.UserRole, alpha_occ)
                a_occupancy.setTextAlignment(Qt.AlignCenter)
                self.mo_table.setItem(row, 1, a_occupancy)
                
                b_occupancy = OrbitalTableItem()
                b_occupancy.setData(Qt.DisplayRole, "%.5f" % beta_occ)
                b_occupancy.setData(Qt.UserRole, beta_occ)
                b_occupancy.setTextAlignment(Qt.AlignCenter)
                self.mo_table.setItem(row, 1, b_occupancy)
                
                nrg_str = "%.5f" % nrg
                orbit_nrg = OrbitalTableItem()
                orbit_nrg.setData(Qt.DisplayRole, nrg_str)
                orbit_nrg.setData(Qt.UserRole, nrg)
                orbit_nrg.setTextAlignment(Qt.AlignCenter)
                self.mo_table.setItem(row, 3, orbit_nrg)
            if not homo_ndx:
                homo_ndx = orbits.n_mos - max(orbits.n_alpha, orbits.n_beta)
        elif orbits.beta_nrgs is None or len(orbits.beta_nrgs) == 0:
            if "orbit_kinds" not in fr.other:
                self.mo_table.setColumnCount(3)
                self.mo_table.setHorizontalHeaderLabels(
                    ["#", "Ground State Occ.", "Energy (E\u2095)"]
                )
            else:
                self.fukui_group.setEnabled(False)
                self.e_density_group.setEnabled(False)
                self.mo_table.setColumnCount(2)
                self.mo_table.setHorizontalHeaderLabels(
                    ["#", "Type"]
                )
            for i, nrg in enumerate(orbits.alpha_nrgs[::-1]):
                row = self.mo_table.rowCount()
                self.mo_table.insertRow(row)
                
                ndx = OrbitalTableItem()
                ndx_str = str(orbits.n_mos - i)
                ndx.setData(Qt.DisplayRole, ndx_str)
                ndx.setData(Qt.UserRole, orbits.n_mos - i - 1)
                ndx.setTextAlignment(Qt.AlignCenter)
                self.mo_table.setItem(row, 0, ndx)
                
                occ = ""
                change_font = True
                if i >= (orbits.n_mos - orbits.n_alpha):
                    occ += "\u21bf"
                if i >= (orbits.n_mos - orbits.n_beta):
                    occ += "\u21c2"

                if "orbit_kinds" in fr.other:
                    change_font = False
                    occ = fr.other["orbit_kinds"][-i - 1]
                    if not homo_ndx and "ry" not in occ and "*" not in occ:
                        homo_ndx = i

                occupancy = OrbitalTableItem()
                occupancy.setData(Qt.DisplayRole, occ)
                occupancy.setData(Qt.UserRole, len(occ))
                occupancy.setTextAlignment(Qt.AlignCenter)
                if change_font:
                    occupancy_font = occupancy.font()
                    # the arrows are really small by default
                    # up it to 2.5x
                    occupancy_font.setPointSize(int(2.5 * occupancy_font.pointSize()))
                    occupancy.setFont(occupancy_font)
                self.mo_table.setItem(row, 1, occupancy)
                
                nrg_str = "%.5f" % nrg
                orbit_nrg = OrbitalTableItem()
                orbit_nrg.setData(Qt.DisplayRole, nrg_str)
                orbit_nrg.setData(Qt.UserRole, nrg)
                orbit_nrg.setTextAlignment(Qt.AlignCenter)
                self.mo_table.setItem(row, 2, orbit_nrg)
            if not homo_ndx:
                homo_ndx = orbits.n_mos - max(orbits.n_alpha, orbits.n_beta)
        else:
            self.mo_table.setColumnCount(3)
            self.mo_table.setHorizontalHeaderLabels(
                ["#", "Ground State Occ.", "Energy (E\u2095)"]
            )
            alpha_ndx = beta_ndx = len(orbits.alpha_nrgs) - 1
            while alpha_ndx >= 0 or beta_ndx >= 0:
                use_alpha = True
                if alpha_ndx >= 0 and beta_ndx >= 0:
                    if orbits.alpha_nrgs[alpha_ndx] < orbits.beta_nrgs[beta_ndx]:
                        use_alpha = False
                elif alpha_ndx < 0:
                    use_alpha = False
                
                row = self.mo_table.rowCount()
                self.mo_table.insertRow(row)
                
                ndx = OrbitalTableItem()
                ndx_str = alpha_ndx + beta_ndx + 2
                ndx.setData(Qt.DisplayRole, ndx_str)
                ndx.setData(
                    Qt.UserRole,
                    (alpha_ndx, "alpha") if use_alpha else (beta_ndx, "beta")
                )
                ndx.setTextAlignment(Qt.AlignCenter)
                self.mo_table.setItem(row, 0, ndx)
                
                occ = "_ " if use_alpha else " _"
                if use_alpha and alpha_ndx < orbits.n_alpha:
                    occ = "\u21bf "
                elif beta_ndx < orbits.n_beta:
                    occ = " \u21c2"
                occupancy = OrbitalTableItem()
                occupancy.setData(Qt.DisplayRole, occ)
                occupancy.setData(Qt.UserRole, alpha_ndx if use_alpha else beta_ndx)
                occupancy.setTextAlignment(Qt.AlignCenter)
                occupancy_font = occupancy.font()
                # the arrows are really small by default
                # up it to 2.5x
                occupancy_font.setPointSize(int(2.5 * occupancy_font.pointSize()))
                occupancy.setFont(occupancy_font)
                self.mo_table.setItem(row, 1, occupancy)
                
                if use_alpha:
                    nrg = orbits.alpha_nrgs[alpha_ndx]
                    alpha_ndx -= 1
                else:
                    nrg = orbits.beta_nrgs[beta_ndx]
                    beta_ndx -= 1
                nrg_str = "%.5f" % nrg
                orbit_nrg = OrbitalTableItem()
                orbit_nrg.setData(Qt.DisplayRole, nrg_str)
                orbit_nrg.setData(Qt.UserRole, nrg)
                orbit_nrg.setTextAlignment(Qt.AlignCenter)
                self.mo_table.setItem(row, 2, orbit_nrg)
            homo_ndx = 2 * orbits.n_mos - orbits.n_alpha - orbits.n_beta

        self.mo_table.setRangeSelected(
            QTableWidgetSelectionRange(homo_ndx, 0, homo_ndx, 2), True
        )
        # calling scrollToItem doesn't work the first time
        # IDK ¯\_(ツ)_/¯
        self.mo_table.scrollToItem(
            self.mo_table.item(homo_ndx, 0), QTableWidget.PositionAtCenter
        )
        self.mo_table.scrollToItem(
            self.mo_table.item(homo_ndx, 0), QTableWidget.PositionAtCenter
        )

    def open_link(self, doi):
        run(self.session, "open https://doi.org/%s" % doi)

    def get_coords(self):
        fr = self.model_selector.currentData()
        if fr is None:
            return
        spacing = self.spacing.value()
        padding = self.padding.value()

        return Orbitals.get_cube_array(
            ResidueCollection(fr, refresh_connected=False, refresh_ranks=False),
            padding=padding,
            spacing=spacing,
        )

    def show_orbit(self):
        fr = self.model_selector.currentData()
        if fr is None:
            return
        model = self.session.filereader_manager.get_model(fr)

        table_items = self.mo_table.selectedItems()
        if len(table_items) == 0:
            return
        for item in table_items:
            if item.column() == 0:
                mo = item.data(Qt.UserRole)

        alpha = True
        if isinstance(mo, tuple):
            mo, alpha_or_beta = mo
            alpha = alpha_or_beta == "alpha"

        orbits = fr.other["orbitals"]

        padding = self.padding.value()
        self.settings.padding = padding
        spacing = self.spacing.value()
        self.settings.spacing = spacing
        threads = self.threads.value()
        self.settings.threads = threads
        iso_val = self.iso_value.value()
        self.settings.iso_val = iso_val
        color1 = tuple(x / 255. for x in self.pos_color.get_color())
        self.settings.color1 = color1
        color2 = tuple(x / 255. for x in self.neg_color.get_color())
        self.settings.color2 = color2
        keep_open = self.keep_open.checkState() == Qt.Checked
        self.settings.keep_open = keep_open
        
        cube = self.get_coords()
        if cube is False:
            return
        n_pts1, n_pts2, n_pts3, v1, v2, v3, com, u = cube

        if keep_open:
            found = False
            hide_vols = []
            for child in model.child_models():
                if (
                    isinstance(child, Volume) and 
                    child.name == "MO %s %i" % ("alpha" if alpha else "beta", mo + 1)
                ):
                    if (
                        all(x == y for x, y in zip(com, child.data.origin)) and
                        child.data._data.shape == (n_pts3, n_pts2, n_pts1)
                    ):
                        found = True
                        run(self.session, "show %s" % child.atomspec)
                        hex1 = hex2 = "#"
                        for v1, v2 in zip(color1, color2):
                            ch1 = str(hex(int(255 * v1)))[2:]
                            ch2 = str(hex(int(255 * v2)))[2:]
                            if len(ch1) == 1:
                                ch1 = "0" + ch1
                            if len(ch2) == 1:
                                ch2 = "0" + ch2
                            hex1 += ch1
                            hex2 += ch2
                        run(
                            self.session,
                            "volume %s level -%.3f level %.3f color %s color %s" % (
                                child.atomspec,
                                iso_val, iso_val,
                                hex2, hex1,
                            )
                        )
                    elif child.name.startswith("MO") and child.visible:
                        hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("MO") and child.visible:
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("electron density") and child.visible:
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui donor") and child.visible:
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui acceptor") and child.visible:
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui dual") and child.visible:
                    hide_vols.append(child)

            for child in hide_vols:
                run(self.session, "hide %s" % child.atomspec)
                
            if found:
                return

        n_val = n_pts1 * n_pts2 * n_pts3
        mem = orbits.memory_estimate(
            "mo_value",
            n_points=n_val,
            n_atoms=len(fr.atoms),
            n_jobs=threads,
        )
        if mem * 1e9 > (0.9 * available_memory()):
            are_you_sure = QMessageBox.warning(
                self.mo_table,
                "Memory Limit Warning",
                "Estimated peak memory usage (%.1fGB) is above or close to\n" % mem +
                "the available memory (%.1fGB).\n" % (available_memory() * 1e-9) +
                "Exceeding available memory might affect the stability of your\n"
                "computer. You may attempt to continue, but it is recommended\n" +
                "that you lower your resolution, decrease padding, or use\n" +
                "fewer threads.\n\n" +
                "Press \"Ok\" to continue or \"Abort\" to cancel.",
                QMessageBox.Abort | QMessageBox.Ok,
                defaultButton=QMessageBox.Abort,
            )
            if are_you_sure != QMessageBox.Ok:
                return False
        
        coords, _ = orbits.get_cube_points(
            n_pts1, n_pts2, n_pts3, v1, v2, v3, com, sort=False
        )
        
        val = orbits.mo_value(mo, coords, alpha=alpha, n_jobs=threads)
        val = np.reshape(val, (n_pts1, n_pts2, n_pts3))

        grid = OrbitalGrid(
            (n_pts1, n_pts2, n_pts3),
            name="MO %s %i" % ("alpha" if alpha else "beta", mo + 1),
            origin=com,
            rotation=u,
            step=[np.linalg.norm(v) for v in [v1, v2, v3]],
        )
        grid._data = np.swapaxes(val, 0, 2)
        
        opt = RenderingOptions()
        opt.flip_normals = True
        opt.bt_correction = True
        opt.cap_faces = False
        opt.square_mesh = False
        opt.smooth_lines = True
        opt.tilted_slab_axis = v3 / np.linalg.norm(v3)

        vol = Volume(self.session, grid, rendering_options=opt)
        vol.set_parameters(
            surface_levels=[-iso_val, iso_val],
            surface_colors=[color2, color1],
        )
        vol.matrix_value_statistics(read_matrix=True)
        vol.update_drawings()
        if not keep_open:
            for child in model.child_models():
                if isinstance(child, Volume) and child.name.startswith("MO"):
                    if keep_open:
                        run(self.session, "close %s" % child.atomspec)
        self.session.models.add([vol], parent=model)

    def show_e_density(self):
        fr = self.model_selector.currentData()
        if fr is None:
            return
        model = self.session.filereader_manager.get_model(fr)
        orbits = fr.other["orbitals"]

        padding = self.padding.value()
        self.settings.padding = padding
        spacing = self.spacing.value()
        self.settings.spacing = spacing
        threads = self.threads.value()
        self.settings.threads = threads
        iso_val = self.ed_iso_value.value()
        self.settings.ed_iso_val = iso_val
        ed_color = tuple(x / 255. for x in self.ed_color.get_color())
        self.settings.ed_color = ed_color
        keep_open = self.keep_open.checkState() == Qt.Checked
        self.settings.keep_open = keep_open
        low_mem_mode = self.low_mem_mode.checkState() == Qt.Checked
        
        cube = self.get_coords()
        if cube is False:
            return
        n_pts1, n_pts2, n_pts3, v1, v2, v3, com, u = cube

        if keep_open:
            found = False
            hide_vols = []
            for child in model.child_models():
                if (
                    isinstance(child, Volume) and 
                    child.name.startswith("electron density")
                ):
                    if (
                        all(x == y for x, y in zip(com, child.data.origin)) and
                        child.data._data.shape == (n_pts3, n_pts2, n_pts1)
                    ):
                        found = True
                        run(self.session, "show %s" % child.atomspec)
                        hex_color = "#"
                        for v in ed_color:
                            ch1 = str(hex(int(255 * v)))[2:]
                            if len(ch1) == 1:
                                ch1 = "0" + ch1
                            hex_color += ch1
                        run(
                            self.session,
                            "volume %s level %.4f color %s" % (
                                child.atomspec,
                                iso_val,
                                hex_color,
                            )
                        )
                    elif child.shown():
                        hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("MO") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("electron density") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui donor") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui acceptor") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui dual") and child.shown():
                    hide_vols.append(child)

            for child in hide_vols:
                run(self.session, "hide %s" % child.atomspec)
                
            if found:
                return

        n_val = n_pts1 * n_pts2 * n_pts3
        mem = orbits.memory_estimate(
            "density_value",
            n_points=n_val,
            n_atoms=len(fr.atoms),
            n_jobs=threads,
        )
        if mem * 1e9 > (0.9 * available_memory()):
            are_you_sure = QMessageBox.warning(
                self.mo_table,
                "Memory Limit Warning",
                "Estimated peak memory usage (%.1fGB) is above or close to\n" % mem +
                "the available memory (%.1fGB).\n" % (available_memory() * 1e-9) +
                "Exceeding available memory might affect the stability of your\n"
                "computer. You may attempt to continue, but it is recommended\n" +
                "that you lower your resolution, decrease padding, or use\n" +
                "fewer threads.\n\n" +
                "Press \"Ok\" to continue or \"Abort\" to cancel.",
                QMessageBox.Abort | QMessageBox.Ok,
                defaultButton=QMessageBox.Abort,
            )
            if are_you_sure != QMessageBox.Ok:
                return False
        
        coords, _ = orbits.get_cube_points(
            n_pts1, n_pts2, n_pts3, v1, v2, v3, com, sort=False
        )
        
        val = orbits.density_value(
            coords, n_jobs=threads, low_mem=low_mem_mode
        )
        val = np.reshape(val, (n_pts1, n_pts2, n_pts3))

        grid = OrbitalGrid(
            (n_pts1, n_pts2, n_pts3),
            name="electron density",
            origin=com,
            rotation=u,
            step=[np.linalg.norm(v) for v in [v1, v2, v3]],
        )
        grid._data = np.swapaxes(val, 0, 2)
        
        opt = RenderingOptions()
        opt.flip_normals = True
        opt.bt_correction = True
        opt.cap_faces = False
        opt.square_mesh = False
        opt.smooth_lines = True
        opt.tilted_slab_axis = v3 / np.linalg.norm(v3)

        vol = Volume(self.session, grid, rendering_options=opt)
        vol.set_parameters(
            surface_levels=[iso_val],
            surface_colors=[ed_color],
        )
        vol.matrix_value_statistics(read_matrix=True)
        vol.update_drawings()
        if not keep_open:
            for child in model.child_models():
                if isinstance(child, Volume) and child.name.startswith("electron density"):
                    run(self.session, "close %s" % child.atomspec)
        self.session.models.add([vol], parent=model)

    def show_fukui_donor(self):
        fr = self.model_selector.currentData()
        if fr is None:
            return
        model = self.session.filereader_manager.get_model(fr)
        orbits = fr.other["orbitals"]
 
        padding = self.padding.value()
        self.settings.padding = padding
        spacing = self.spacing.value()
        self.settings.spacing = spacing
        threads = self.threads.value()
        self.settings.threads = threads
        iso_val = self.fd_iso_value.value()
        self.settings.fd_iso_val = iso_val
        fd_color = tuple(x / 255. for x in self.fd_color.get_color())
        self.settings.fd_color = fd_color
        keep_open = self.keep_open.checkState() == Qt.Checked
        self.settings.keep_open = keep_open
        low_mem_mode = self.low_mem_mode.checkState() == Qt.Checked
        delta = self.fukui_delta.value()
        if delta != self.settings.fukui_delta:
            keep_open = False
        self.settings.fukui_delta = delta

        if self.fukui_type.currentText() == "condensed":
            self.settings.n_radial = self.radial.currentText()
            self.settings.n_angular = self.angular.currentText()
            self.settings.vdw_radii = self.vdw_radii.currentText()
            
            rescol = ResidueCollection(model)
            values = orbits.condensed_fukui_donor_values(
                rescol,
                n_jobs=threads,
                apoints=self.angular.currentData(),
                rpoints=self.radial.currentData(),
                radii=self.vdw_radii.currentText(),
                delta=delta,
                low_mem=low_mem_mode,
            )
            for val, atom in zip(values, model.atoms):
                l = "%6.3f" % val
                label(
                    self.session,
                    objects=Objects(atoms=Atoms([atom])),
                    object_type="atoms",
                    text=l,
                    offset=(-0.11*len(l),-0.2,-0.2),
                    height=0.4,
                    on_top=True,
                )
            return

        cube = self.get_coords()
        if cube is False:
            return
        n_pts1, n_pts2, n_pts3, v1, v2, v3, com, u = cube

        if keep_open:
            found = False
            hide_vols = []
            for child in model.child_models():
                if (
                    isinstance(child, Volume) and 
                    child.name.startswith("fukui donor")
                ):
                    if (
                        all(x == y for x, y in zip(com, child.data.origin)) and
                        child.data._data.shape == (n_pts3, n_pts2, n_pts1)
                    ):
                        found = True
                        run(self.session, "show %s" % child.atomspec)
                        hex_color = "#"
                        for v in fd_color:
                            ch1 = str(hex(int(255 * v)))[2:]
                            if len(ch1) == 1:
                                ch1 = "0" + ch1
                            hex_color += ch1
                        run(
                            self.session,
                            "volume %s level %.4f color %s" % (
                                child.atomspec,
                                iso_val,
                                hex_color,
                            )
                        )
                    elif child.shown():
                        hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("MO") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("electron density") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui donor") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui acceptor") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui dual") and child.shown():
                    hide_vols.append(child)

            for child in hide_vols:
                run(self.session, "hide %s" % child.atomspec)
                
            if found:
                return

        n_val = n_pts1 * n_pts2 * n_pts3
        mem = orbits.memory_estimate(
            "fukui_donor_value",
            n_points=n_val,
            n_atoms=len(fr.atoms),
            n_jobs=threads,
        )
        if mem * 1e9 > (0.9 * available_memory()):
            are_you_sure = QMessageBox.warning(
                self.mo_table,
                "Memory Limit Warning",
                "Estimated peak memory usage (%.1fGB) is above or close to\n" % mem +
                "the available memory (%.1fGB).\n" % (available_memory() * 1e-9) +
                "Exceeding available memory might affect the stability of your\n"
                "computer. You may attempt to continue, but it is recommended\n" +
                "that you lower your resolution, decrease padding, or use\n" +
                "fewer threads.\n\n" +
                "Press \"Ok\" to continue or \"Abort\" to cancel.",
                QMessageBox.Abort | QMessageBox.Ok,
                defaultButton=QMessageBox.Abort,
            )
            if are_you_sure != QMessageBox.Ok:
                return False
        
        coords, _ = orbits.get_cube_points(
            n_pts1, n_pts2, n_pts3, v1, v2, v3, com, sort=False
        )
        
        val = orbits.fukui_donor_value(
            coords, n_jobs=threads, low_mem=low_mem_mode, delta=delta,
        )
        val = np.reshape(val, (n_pts1, n_pts2, n_pts3))

        grid = OrbitalGrid(
            (n_pts1, n_pts2, n_pts3),
            name="fukui donor",
            origin=com,
            rotation=u,
            step=[np.linalg.norm(v) for v in [v1, v2, v3]],
        )
        grid._data = np.swapaxes(val, 0, 2)
        
        opt = RenderingOptions()
        opt.flip_normals = True
        opt.bt_correction = True
        opt.cap_faces = False
        opt.square_mesh = False
        opt.smooth_lines = True
        opt.tilted_slab_axis = v3 / np.linalg.norm(v3)

        vol = Volume(self.session, grid, rendering_options=opt)
        vol.set_parameters(
            surface_levels=[iso_val],
            surface_colors=[fd_color],
        )
        vol.matrix_value_statistics(read_matrix=True)
        vol.update_drawings()
        if not keep_open:
            for child in model.child_models():
                if isinstance(child, Volume) and child.name.startswith("fukui donor"):
                    run(self.session, "close %s" % child.atomspec)
        self.session.models.add([vol], parent=model)

    def show_fukui_acceptor(self):
        fr = self.model_selector.currentData()
        if fr is None:
            return
        model = self.session.filereader_manager.get_model(fr)
        orbits = fr.other["orbitals"]

        padding = self.padding.value()
        self.settings.padding = padding
        spacing = self.spacing.value()
        self.settings.spacing = spacing
        threads = self.threads.value()
        self.settings.threads = threads
        iso_val = self.fd_iso_value.value()
        self.settings.fd_iso_val = iso_val
        fa_color = tuple(x / 255. for x in self.fa_color.get_color())
        self.settings.fa_color = fa_color
        keep_open = self.keep_open.checkState() == Qt.Checked
        self.settings.keep_open = keep_open
        low_mem_mode = self.low_mem_mode.checkState() == Qt.Checked
        delta = self.fukui_delta.value()
        if delta != self.settings.fukui_delta:
            keep_open = False
        self.settings.fukui_delta = delta

        if self.fukui_type.currentText() == "condensed":
            self.settings.n_radial = self.radial.currentText()
            self.settings.n_angular = self.angular.currentText()
            self.settings.vdw_radii = self.vdw_radii.currentText()

            rescol = ResidueCollection(model)
            values = orbits.condensed_fukui_acceptor_values(
                rescol,
                n_jobs=threads,
                apoints=self.angular.currentData(),
                rpoints=self.radial.currentData(),
                radii=self.vdw_radii.currentText(),
                delta=delta,
                low_mem=low_mem_mode,
            )
            for val, atom in zip(values, model.atoms):
                l = "%6.3f" % val
                label(
                    self.session,
                    objects=Objects(atoms=Atoms([atom])),
                    object_type="atoms",
                    text=l,
                    offset=(-0.11*len(l),-0.2,-0.2),
                    height=0.4,
                    on_top=True,
                )
            return

        cube = self.get_coords()
        if cube is False:
            return
        n_pts1, n_pts2, n_pts3, v1, v2, v3, com, u = cube
        
        if keep_open:
            found = False
            hide_vols = []
            for child in model.child_models():
                if (
                    isinstance(child, Volume) and 
                    child.name.startswith("fukui acceptor")
                ):
                    if (
                        all(x == y for x, y in zip(com, child.data.origin)) and
                        child.data._data.shape == (n_pts3, n_pts2, n_pts1)
                    ):
                        found = True
                        run(self.session, "show %s" % child.atomspec)
                        hex_color = "#"
                        for v in fa_color:
                            ch1 = str(hex(int(255 * v)))[2:]
                            if len(ch1) == 1:
                                ch1 = "0" + ch1
                            hex_color += ch1
                        run(
                            self.session,
                            "volume %s level %.4f color %s" % (
                                child.atomspec,
                                iso_val,
                                hex_color,
                            )
                        )
                    elif child.shown():
                        hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("MO") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("electron density") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui donor") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui acceptor") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui dual") and child.shown():
                    hide_vols.append(child)

            for child in hide_vols:
                run(self.session, "hide %s" % child.atomspec)
                
            if found:
                return

        n_val = n_pts1 * n_pts2 * n_pts3
        mem = orbits.memory_estimate(
            "fukui_acceptor_value",
            n_points=n_val,
            n_atoms=len(fr.atoms),
            n_jobs=threads,
        )
        if mem * 1e9 > (0.9 * available_memory()):
            are_you_sure = QMessageBox.warning(
                self.mo_table,
                "Memory Limit Warning",
                "Estimated peak memory usage (%.1fGB) is above or close to\n" % mem +
                "the available memory (%.1fGB).\n" % (available_memory() * 1e-9) +
                "Exceeding available memory might affect the stability of your\n"
                "computer. You may attempt to continue, but it is recommended\n" +
                "that you lower your resolution, decrease padding, or use\n" +
                "fewer threads.\n\n" +
                "Press \"Ok\" to continue or \"Abort\" to cancel.",
                QMessageBox.Abort | QMessageBox.Ok,
                defaultButton=QMessageBox.Abort,
            )
            if are_you_sure != QMessageBox.Ok:
                return False
        
        coords, _ = orbits.get_cube_points(
            n_pts1, n_pts2, n_pts3, v1, v2, v3, com, sort=False
        )
        
        val = orbits.fukui_acceptor_value(
            coords, n_jobs=threads, low_mem=low_mem_mode, delta=delta,
        )
        val = np.reshape(val, (n_pts1, n_pts2, n_pts3))

        grid = OrbitalGrid(
            (n_pts1, n_pts2, n_pts3),
            name="fukui acceptor",
            origin=com,
            rotation=u,
            step=[np.linalg.norm(v) for v in [v1, v2, v3]],
        )
        grid._data = np.swapaxes(val, 0, 2)
        
        opt = RenderingOptions()
        opt.flip_normals = True
        opt.bt_correction = True
        opt.cap_faces = False
        opt.square_mesh = False
        opt.smooth_lines = True
        opt.tilted_slab_axis = v3 / np.linalg.norm(v3)

        vol = Volume(self.session, grid, rendering_options=opt)
        vol.set_parameters(
            surface_levels=[iso_val],
            surface_colors=[fa_color],
        )
        vol.matrix_value_statistics(read_matrix=True)
        vol.update_drawings()
        if not keep_open:
            for child in model.child_models():
                if isinstance(child, Volume) and child.name.startswith("fukui acceptor"):
                    run(self.session, "close %s" % child.atomspec)
        self.session.models.add([vol], parent=model)

    def show_fukui_dual(self):
        fr = self.model_selector.currentData()
        if fr is None:
            return
        model = self.session.filereader_manager.get_model(fr)
        orbits = fr.other["orbitals"]

        padding = self.padding.value()
        self.settings.padding = padding
        spacing = self.spacing.value()
        self.settings.spacing = spacing
        threads = self.threads.value()
        self.settings.threads = threads
        iso_val = self.fd_iso_value.value()
        self.settings.fd_iso_val = iso_val
        fa_color = tuple(x / 255. for x in self.fa_color.get_color())
        self.settings.fa_color = fa_color
        fd_color = tuple(x / 255. for x in self.fd_color.get_color())
        self.settings.fd_color = fd_color
        keep_open = self.keep_open.checkState() == Qt.Checked
        self.settings.keep_open = keep_open
        low_mem_mode = self.low_mem_mode.checkState() == Qt.Checked
        delta = self.fukui_delta.value()
        if delta != self.settings.fukui_delta:
            keep_open = False
        self.settings.fukui_delta = delta

        if self.fukui_type.currentText() == "condensed":
            self.settings.n_radial = self.radial.currentText()
            self.settings.n_angular = self.angular.currentText()
            self.settings.vdw_radii = self.vdw_radii.currentText()

            rescol = ResidueCollection(model)
            values = orbits.condensed_fukui_dual_values(
                rescol,
                n_jobs=threads,
                apoints=self.angular.currentData(),
                rpoints=self.radial.currentData(),
                radii=self.vdw_radii.currentText(),
                delta=delta,
                low_mem=low_mem_mode,
            )
            for val, atom in zip(values, model.atoms):
                l = "%6.3f" % val
                label(
                    self.session,
                    objects=Objects(atoms=Atoms([atom])),
                    object_type="atoms",
                    text=l,
                    offset=(-0.11*len(l),-0.2,-0.2),
                    height=0.4,
                    on_top=True,
                )
            return

        cube = self.get_coords()
        if cube is False:
            return
        n_pts1, n_pts2, n_pts3, v1, v2, v3, com, u = cube

        if keep_open:
            found = False
            hide_vols = []
            for child in model.child_models():
                if (
                    isinstance(child, Volume) and 
                    child.name.startswith("fukui dual")
                ):
                    if (
                        all(x == y for x, y in zip(com, child.data.origin)) and
                        child.data._data.shape == (n_pts3, n_pts2, n_pts1)
                    ):
                        found = True
                        run(self.session, "show %s" % child.atomspec)
                        hex_color1 = hex_color2 = "#"
                        for v1, v2 in zip(fa_color, fd_color):
                            ch1 = str(hex(int(255 * v1)))[2:]
                            if len(ch1) == 1:
                                ch1 = "0" + ch1
                            hex_color1 += ch1
                            ch2 = str(hex(int(255 * v2)))[2:]
                            if len(ch2) == 1:
                                ch2 = "0" + ch2
                            hex_color2 += ch2
                        run(
                            self.session,
                            "volume %s level -%.4f level %.4f color %s color %s" % (
                                child.atomspec,
                                iso_val,
                                iso_val,
                                hex_color2,
                                hex_color1,
                            )
                        )
                    elif child.shown():
                        hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("MO") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("electron density") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui donor") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui acceptor") and child.shown():
                    hide_vols.append(child)
                elif isinstance(child, Volume) and child.name.startswith("fukui dual") and child.shown():
                    hide_vols.append(child)

            for child in hide_vols:
                run(self.session, "hide %s" % child.atomspec)
                
            if found:
                return

        n_val = n_pts1 * n_pts2 * n_pts3
        mem = orbits.memory_estimate(
            "fukui_dual_value",
            n_points=n_val,
            n_atoms=len(fr.atoms),
            n_jobs=threads,
        )
        if mem * 1e9 > (0.9 * available_memory()):
            are_you_sure = QMessageBox.warning(
                self.mo_table,
                "Memory Limit Warning",
                "Estimated peak memory usage (%.1fGB) is above or close to\n" % mem +
                "the available memory (%.1fGB).\n" % (available_memory() * 1e-9) +
                "Exceeding available memory might affect the stability of your\n"
                "computer. You may attempt to continue, but it is recommended\n" +
                "that you lower your resolution, decrease padding, or use\n" +
                "fewer threads.\n\n" +
                "Press \"Ok\" to continue or \"Abort\" to cancel.",
                QMessageBox.Abort | QMessageBox.Ok,
                defaultButton=QMessageBox.Abort,
            )
            if are_you_sure != QMessageBox.Ok:
                return False
        
        coords, _ = orbits.get_cube_points(
            n_pts1, n_pts2, n_pts3, v1, v2, v3, com, sort=False
        )
        
        val = orbits.fukui_dual_value(
            coords, n_jobs=threads, low_mem=low_mem_mode, delta=delta,
        )
        val = np.reshape(val, (n_pts1, n_pts2, n_pts3))

        grid = OrbitalGrid(
            (n_pts1, n_pts2, n_pts3),
            name="fukui dual",
            origin=com,
            rotation=u,
            step=[np.linalg.norm(v) for v in [v1, v2, v3]],
        )
        grid._data = np.swapaxes(val, 0, 2)
        
        opt = RenderingOptions()
        opt.flip_normals = True
        opt.bt_correction = True
        opt.cap_faces = False
        opt.square_mesh = False
        opt.smooth_lines = True
        opt.tilted_slab_axis = v3 / np.linalg.norm(v3)

        vol = Volume(self.session, grid, rendering_options=opt)
        vol.set_parameters(
            surface_levels=[-iso_val, iso_val],
            surface_colors=[fd_color, fa_color],
        )
        vol.matrix_value_statistics(read_matrix=True)
        vol.update_drawings()
        if not keep_open:
            for child in model.child_models():
                if isinstance(child, Volume) and child.name.startswith("fukui dual"):
                    run(self.session, "close %s" % child.atomspec)
        self.session.models.add([vol], parent=model)

    def delete(self):
        self.model_selector.deleteLater()

        return super().delete()
    
    def close(self):
        self.model_selector.deleteLater()
    
    def cleanup(self):
        self.model_selector.deleteLater()

        return super().cleanup()


# class OccupancyEditor(ChildToolWindow):
#     def __init__(self, tool_instance, title, **kwargs):
#         super().__init__(tool_instance, title, statusbar=False, **kwargs)
#         
#         self._build_ui()
#     
#     def _build_ui(self):
#         layout = QFormLayout()
# 
#         self.ui_area.setLayout(layout)
#         self.manage(None)

