from os import cpu_count

from psutil import virtual_memory

from chimerax.core.commands import run
from chimerax.core.tools import ToolInstance
from chimerax.map.volume import Volume, RenderingOptions
from chimerax.map_data import MatrixValueStatistics
from chimerax.map_data.griddata import GridData
from chimerax.ui.gui import MainToolWindow, ChildToolWindow

import numpy as np

from Qt.QtCore import Qt
from Qt.QtWidgets import (
    QPushButton,
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QFormLayout,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QWidget,
    QLabel,
    QStyle,
    QHeaderView,
    QTableWidgetSelectionRange,
)

from AaronTools.const import UNIT

from SEQCROW.widgets import FilereaderComboBox


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
            ijk_origin[2]:ijk_size[2]:ijk_step[2],
            ijk_origin[1]:ijk_size[1]:ijk_step[1],
            ijk_origin[0]:ijk_size[0]:ijk_step[0]
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
            ijk_origin[2]:ijk_size[2]:ijk_step[2],
            ijk_origin[1]:ijk_size[1]:ijk_step[1],
            ijk_origin[0]:ijk_size[0]:ijk_step[0]
        ]


class OrbitalTableItem(QTableWidgetItem):
    def __lt__(self, other):
        return self.data(Qt.UserRole) < other.data(Qt.UserRole)


class OrbitalViewer(ToolInstance):
    
    # help = "https://github.com/QChASM/SEQCROW/wiki/Coordination-Complex-Generator-Tool"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)
        
        self._build_ui()
    
        self.fill_orbits(0)
        self.estimate_memory()

    def _build_ui(self):
        layout = QFormLayout()

        self.model_selector = FilereaderComboBox(self.session, otherItems=['orbitals'])
        self.model_selector.currentIndexChanged.connect(self.fill_orbits)
        layout.addRow(self.model_selector)

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
        layout.addRow(self.mo_table)

        draw_orbits = QPushButton("view selected orbital")
        draw_orbits.clicked.connect(self.show_orbit)
        layout.addRow(draw_orbits)

        self.padding = QDoubleSpinBox()
        self.padding.setRange(1., 10.)
        self.padding.setDecimals(2)
        self.padding.setValue(3.)
        self.padding.setSingleStep(0.25)
        self.padding.setSuffix(" \u212B")
        layout.addRow("padding:", self.padding)

        self.spacing = QDoubleSpinBox()
        self.spacing.setRange(0.05, 0.75)
        self.spacing.setDecimals(2)
        self.spacing.setValue(0.2)
        self.spacing.setSingleStep(0.05)
        self.spacing.setSuffix(" \u212B")
        layout.addRow("resolution:", self.spacing)

        self.threads = QSpinBox()
        self.threads.setRange(1, cpu_count())
        self.threads.setValue(int(cpu_count() // 2))
        layout.addRow("multithread calculation:", self.threads)

        # show estimated memory usage
        # this can deter from trying to make a massive grid that
        # could freeze the computer
        self.estimated_memory = QLabel("estimated peak memory used: x GB")
        layout.addRow(self.estimated_memory)

        self.padding.valueChanged.connect(self.estimate_memory)
        self.spacing.valueChanged.connect(self.estimate_memory)
        self.threads.valueChanged.connect(self.estimate_memory)
        self.model_selector.currentIndexChanged.connect(self.estimate_memory)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def fill_orbits(self, ndx):
        self.mo_table.setRowCount(0)
        
        if ndx == -1:
            return
        
        fr = self.model_selector.currentData()
        if fr is None:
            return
        
        orbits = fr.other["orbitals"]
        
        homo_item = None
        
        if not orbits.beta_nrgs:
            self.mo_table.setColumnCount(3)
            self.mo_table.setHorizontalHeaderLabels(
                ["#", "Ground State Occ.", "Energy (E\u2095)"]
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
                if i >= (orbits.n_mos - orbits.n_alpha):
                    occ += "\u21bf"
                if i >= (orbits.n_mos - orbits.n_beta):
                    occ += "\u21c2"

                occupancy = OrbitalTableItem()
                occupancy.setData(Qt.DisplayRole, occ)
                occupancy.setData(Qt.UserRole, len(occ))
                occupancy.setTextAlignment(Qt.AlignCenter)
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
        
        homo_ndx = orbits.n_mos - max(orbits.n_alpha, orbits.n_beta)
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

    def estimate_memory(self):
        fr = self.model_selector.currentData()
        if fr is None:
            return

        table_items = self.mo_table.selectedItems()
        if len(table_items) == 0:
            return
        for item in table_items:
            if item.column() == 0:
                mo = item.data(Qt.UserRole)

        orbits = fr.other["orbitals"]

        padding = self.padding.value()
        spacing = self.spacing.value()
        threads = self.threads.value()

        model = self.session.filereader_manager.get_model(fr)
        geom_coords = np.array([atom.coords for atom in fr.atoms])

        def get_standard_axis():
            """returns info to set up a grid along the x, y, and z axes"""

            # get range of geom's coordinates
            x_min = np.min(geom_coords[:,0])
            x_max = np.max(geom_coords[:,0])
            y_min = np.min(geom_coords[:,1])
            y_max = np.max(geom_coords[:,1])
            z_min = np.min(geom_coords[:,2])
            z_max = np.max(geom_coords[:,2])

            # add padding, figure out vectors
            r1 = 2 * padding + x_max - x_min
            n_pts1 = int(r1 // spacing) + 1
            d1 = r1 / (n_pts1 - 1)
            v1 = np.array((d1, 0., 0.))
            r2 = 2 * padding + y_max - y_min
            n_pts2 = int(r2 // spacing) + 1
            d2 = r2 / (n_pts2 - 1)
            v2 = np.array((0., d2, 0.))
            r3 = 2 * padding + z_max - z_min
            n_pts3 = int(r3 // spacing) + 1
            d3 = r3 / (n_pts3 - 1)
            v3 = np.array((0., 0., d3))
            com = np.array([x_min, y_min, z_min]) - padding
            return n_pts1, n_pts2, n_pts3, v1, v2, v3, com

        test_coords = geom_coords - np.mean(geom_coords, axis=0)
        covar = np.dot(test_coords.T, test_coords)
        try:
            # use SVD on the coordinate covariance matrix
            # this decreases the volume of the box we're making
            # that means less work for higher resolution
            # for many structures, this only decreases the volume
            # by like 5%
            u, s, vh = np.linalg.svd(covar)
            v1 = u[:,0]
            v2 = u[:,1]
            v3 = u[:,2]
            # change basis of coordinates to the singular vectors
            # this is how we determine the range + padding
            new_coords = np.dot(test_coords, u)
            x1 = np.dot(test_coords, v1)
            x2 = np.dot(test_coords, v2)
            x3 = np.dot(test_coords, v3)
            xr_max = np.max(new_coords[:,0])
            xr_min = np.min(new_coords[:,0])
            yr_max = np.max(new_coords[:,1])
            yr_min = np.min(new_coords[:,1])
            zr_max = np.max(new_coords[:,2])
            zr_min = np.min(new_coords[:,2])
            com = np.array([xr_min, yr_min, zr_min]) - padding
            # move the COM back to the xyz space of the original molecule
            com = np.dot(u, com)
            com += np.mean(geom_coords, axis=0)
            r1 = 2 * padding + np.linalg.norm(xr_max - xr_min)
            r2 = 2 * padding + np.linalg.norm(yr_max - yr_min)
            r3 = 2 * padding + np.linalg.norm(zr_max - zr_min)
            n_pts1 = int(r1 // spacing) + 1
            n_pts2 = int(r2 // spacing) + 1
            n_pts3 = int(r3 // spacing) + 1
            v1 = v1 * r1 / (n_pts1 - 1)
            v2 = v2 * r2 / (n_pts2 - 1)
            v3 = v3 * r3 / (n_pts3 - 1)
        except np.linalg.LinAlgError:
            n_pts1, n_pts2, n_pts3, v1, v2, v3, com = get_standard_axis()
        
        n_val = n_pts1 * n_pts2 * n_pts3
        n_val *= 32 * 4 * threads
        gb = n_val * (10 ** -9)
        
        if n_val > (0.75 * virtual_memory().free):
            self.estimated_memory.setStyleSheet("color: red")
        else:
            self.estimated_memory.setStyleSheet("")

        
        self.estimated_memory.setText("estimated peak memory used: %.1f GB" % gb)

    def show_orbit(self):
        fr = self.model_selector.currentData()
        if fr is None:
            return

        table_items = self.mo_table.selectedItems()
        if len(table_items) == 0:
            return
        for item in table_items:
            if item.column() == 0:
                mo = item.data(Qt.UserRole)

        orbits = fr.other["orbitals"]

        padding = self.padding.value()
        spacing = self.spacing.value()
        threads = self.threads.value()

        model = self.session.filereader_manager.get_model(fr)
        geom_coords = np.array([atom.coords for atom in fr.atoms])

        def get_standard_axis():
            """returns info to set up a grid along the x, y, and z axes"""

            # get range of geom's coordinates
            x_min = np.min(geom_coords[:,0])
            x_max = np.max(geom_coords[:,0])
            y_min = np.min(geom_coords[:,1])
            y_max = np.max(geom_coords[:,1])
            z_min = np.min(geom_coords[:,2])
            z_max = np.max(geom_coords[:,2])

            # add padding, figure out vectors
            r1 = 2 * padding + x_max - x_min
            n_pts1 = int(r1 // spacing) + 1
            d1 = r1 / (n_pts1 - 1)
            v1 = np.array((d1, 0., 0.))
            r2 = 2 * padding + y_max - y_min
            n_pts2 = int(r2 // spacing) + 1
            d2 = r2 / (n_pts2 - 1)
            v2 = np.array((0., d2, 0.))
            r3 = 2 * padding + z_max - z_min
            n_pts3 = int(r3 // spacing) + 1
            d3 = r3 / (n_pts3 - 1)
            v3 = np.array((0., 0., d3))
            com = np.array([x_min, y_min, z_min]) - padding
            return n_pts1, n_pts2, n_pts3, v1, v2, v3, com

        test_coords = geom_coords - np.mean(geom_coords, axis=0)
        covar = np.dot(test_coords.T, test_coords)
        try:
            # use SVD on the coordinate covariance matrix
            # this decreases the volume of the box we're making
            # that means less work for higher resolution
            # for many structures, this only decreases the volume
            # by like 5%
            u, s, vh = np.linalg.svd(covar)
            v1 = u[:,0]
            v2 = u[:,1]
            v3 = u[:,2]
            # change basis of coordinates to the singular vectors
            # this is how we determine the range + padding
            new_coords = np.dot(test_coords, u)
            x1 = np.dot(test_coords, v1)
            x2 = np.dot(test_coords, v2)
            x3 = np.dot(test_coords, v3)
            xr_max = np.max(new_coords[:,0])
            xr_min = np.min(new_coords[:,0])
            yr_max = np.max(new_coords[:,1])
            yr_min = np.min(new_coords[:,1])
            zr_max = np.max(new_coords[:,2])
            zr_min = np.min(new_coords[:,2])
            com = np.array([xr_min, yr_min, zr_min]) - padding
            # move the COM back to the xyz space of the original molecule
            com = np.dot(u, com)
            com += np.mean(geom_coords, axis=0)
            r1 = 2 * padding + np.linalg.norm(xr_max - xr_min)
            r2 = 2 * padding + np.linalg.norm(yr_max - yr_min)
            r3 = 2 * padding + np.linalg.norm(zr_max - zr_min)
            n_pts1 = int(r1 // spacing) + 1
            n_pts2 = int(r2 // spacing) + 1
            n_pts3 = int(r3 // spacing) + 1
            v1 = v1 * r1 / (n_pts1 - 1)
            v2 = v2 * r2 / (n_pts2 - 1)
            v3 = v3 * r3 / (n_pts3 - 1)
        except np.linalg.LinAlgError:
            n_pts1, n_pts2, n_pts3, v1, v2, v3, com = get_standard_axis()
            u = np.eye(3)

        ndx = np.vstack(
            np.mgrid[0:n_pts1, 0:n_pts2, 0:n_pts3]
        ).reshape(3, np.prod([n_pts1, n_pts2, n_pts3])).T
        coords = np.matmul(ndx, [v1, v2, v3])
        coords += com
        val = orbits.mo_value(mo, coords, n_jobs=threads)
        val = np.reshape(val, (n_pts1, n_pts2, n_pts3))

        grid = OrbitalGrid(
            (n_pts1, n_pts2, n_pts3),
            name="MO %i" % (mo + 1),
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
            surface_levels=[-0.022, 0.022],
            surface_colors=[(1., 0., 0., 0.5), (0., 0., 1., 0.5)],
        )
        vol.matrix_value_statistics(read_matrix=True)
        vol.update_drawings()
        for child in model.child_models():
            if isinstance(child, Volume) and child.name.startswith("MO"):
                run(self.session, "close %s" % child.atomspec)
        self.session.models.add([vol], parent=model)
