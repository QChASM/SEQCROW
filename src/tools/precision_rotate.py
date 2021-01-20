import numpy as np

from chimerax.atomic import selected_atoms, selected_bonds, get_triggers
from chimerax.bild.bild import read_bild
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.settings import Settings
from chimerax.core.generic3d import Generic3DModel 
from chimerax.core.selection import SELECTION_CHANGED

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QFormLayout, QCheckBox, QPushButton, \
                            QDoubleSpinBox, QWidget, QLabel, QStatusBar, QComboBox, \
                            QHBoxLayout

from io import BytesIO


class _PrecisionRotateSettings(Settings):
    AUTO_SAVE = {
    }

class PrecisionRotate(ToolInstance):

    help = "https://github.com/QChASM/SEQCROW/wiki/Rotate-Tool"
    SESSION_ENDURING = True
    SESSION_SAVE = True
    
    def __init__(self, session, name):
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)
        
        self.settings = _PrecisionRotateSettings(session, name)
        
        self.bonds = {}
        self.bond_centers = {}
        self.groups = {}
        self.perpendiculars = {}
        self.perp_centers = {}
        self.manual_center = {}
        
        self._build_ui()

        self._show_rot_vec = self.session.triggers.add_handler(SELECTION_CHANGED, self.show_rot_vec)
        global_triggers = get_triggers()
        self._changes = global_triggers.add_handler("changes done", self.show_rot_vec)
        
        self.show_rot_vec()
    
    def _build_ui(self):
        layout = QGridLayout()
        
        layout.addWidget(QLabel("center of rotation:"), 0, 0, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)
        
        self.cor_button = QComboBox()
        self.cor_button.addItems(["automatic", "select atoms", "view's center of rotation"])
        layout.addWidget(self.cor_button, 0, 1, 1, 1, Qt.AlignTop)
        
        self.set_cor_selection = QPushButton("set selection")
        self.cor_button.currentTextChanged.connect(lambda t, widget=self.set_cor_selection: widget.setEnabled(t == "select atoms"))
        self.set_cor_selection.clicked.connect(self.manual_cor)
        layout.addWidget(self.set_cor_selection, 0, 2, 1, 1, Qt.AlignTop)
        self.set_cor_selection.setEnabled(False)
        
        layout.addWidget(QLabel("rotation vector:"), 1, 0, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)
        
        self.vector_option = QComboBox()
        self.vector_option.addItems(["axis", "view axis", "bond", "perpendicular to plane", "centroid of atoms", "custom"])
        layout.addWidget(self.vector_option, 1, 1, 1, 1, Qt.AlignVCenter)
        
        vector = QWidget()
        vector.setToolTip("vector will be normalized before rotating")
        vector_layout = QHBoxLayout(vector)
        vector_layout.setContentsMargins(0, 0, 0, 0)
        self.vector_x = QDoubleSpinBox()
        self.vector_y = QDoubleSpinBox()
        self.vector_z = QDoubleSpinBox()
        self.vector_z.setValue(1.0)
        for c, t in zip([self.vector_x, self.vector_y, self.vector_z], [" x", " y", " z"]):
            c.setSingleStep(0.01)
            c.setRange(-100, 100)
            # c.setSuffix(t)
            c.valueChanged.connect(self.show_rot_vec)
            vector_layout.addWidget(c)
        
        layout.addWidget(vector, 1, 2, 1, 1, Qt.AlignTop)
        vector.setVisible(self.vector_option.currentText() == "custom")
        self.vector_option.currentTextChanged.connect(lambda text, widget=vector: widget.setVisible(text == "custom"))
        
        self.view_axis = QComboBox()
        self.view_axis.addItems(["z", "y", "x"])
        layout.addWidget(self.view_axis, 1, 2, 1, 1, Qt.AlignTop)
        self.view_axis.setVisible(self.vector_option.currentText() == "view axis")
        self.vector_option.currentTextChanged.connect(lambda text, widget=self.view_axis: widget.setVisible(text == "view axis"))
        
        self.axis = QComboBox()
        self.axis.addItems(["z", "y", "x"])
        layout.addWidget(self.axis, 1, 2, 1, 1, Qt.AlignTop)
        self.axis.setVisible(self.vector_option.currentText() == "axis")
        self.vector_option.currentTextChanged.connect(lambda text, widget=self.axis: widget.setVisible(text == "axis"))

        self.bond_button = QPushButton("set selected bond")
        self.bond_button.clicked.connect(self.set_bonds)
        layout.addWidget(self.bond_button, 1, 2, 1, 1, Qt.AlignTop)
        self.bond_button.setVisible(self.vector_option.currentText() == "bond")
        self.vector_option.currentTextChanged.connect(lambda text, widget=self.bond_button: widget.setVisible(text == "bond"))

        self.perp_button = QPushButton("set selected atoms")
        self.perp_button.clicked.connect(self.set_perpendicular)
        layout.addWidget(self.perp_button, 1, 2, 1, 1, Qt.AlignTop)
        self.perp_button.setVisible(self.vector_option.currentText() == "perpendicular to plane")
        self.vector_option.currentTextChanged.connect(lambda text, widget=self.perp_button: widget.setVisible(text == "perpendicular to plane"))

        self.group_button = QPushButton("set selected atoms")
        self.group_button.clicked.connect(self.set_group)
        layout.addWidget(self.group_button, 1, 2, 1, 1, Qt.AlignTop)
        self.group_button.setVisible(self.vector_option.currentText() == "centroid of atoms")
        self.vector_option.currentTextChanged.connect(lambda text, widget=self.group_button: widget.setVisible(text == "centroid of atoms"))

        layout.addWidget(QLabel("angle:"), 2, 0, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)

        self.angle = QDoubleSpinBox()
        self.angle.setRange(-360, 360)
        self.angle.setSingleStep(5)
        self.angle.setSuffix("°")
        layout.addWidget(self.angle, 2, 1, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)
        
        layout.addWidget(QLabel("preview rotation axis:"), 3, 0, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)
        self.display_rot_vec = QCheckBox()
        self.display_rot_vec.setCheckState(Qt.Checked)
        self.display_rot_vec.stateChanged.connect(self.show_rot_vec)
        layout.addWidget(self.display_rot_vec, 3, 1, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)
        
        rotate_button = QPushButton("rotate selected atoms")
        rotate_button.clicked.connect(self.do_rotate)
        layout.addWidget(rotate_button, 4, 0, 1, 3, Qt.AlignTop)
        self.rotate_button = rotate_button

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar, 5, 0, 1, 3, Qt.AlignTop)
        
        self.vector_option.currentTextChanged.connect(self.show_auto_status)
        self.cor_button.currentIndexChanged.connect(lambda *args: self.show_auto_status("select atoms"))
        
        self.cor_button.currentIndexChanged.connect(self.show_rot_vec)
        self.set_cor_selection.clicked.connect(self.show_rot_vec)
        self.vector_option.currentIndexChanged.connect(self.show_rot_vec)
        self.axis.currentIndexChanged.connect(self.show_rot_vec)
        self.view_axis.currentIndexChanged.connect(self.show_rot_vec)
        self.bond_button.clicked.connect(self.show_rot_vec)
        self.perp_button.clicked.connect(self.show_rot_vec)
        self.group_button.clicked.connect(self.show_rot_vec)
        
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 0)
        layout.setRowStretch(2, 0)
        layout.setRowStretch(3, 0)
        layout.setRowStretch(4, 0)
        layout.setRowStretch(5, 1)
        
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        self.tool_window.ui_area.setLayout(layout)
        
        self.tool_window.manage(None)

    def manual_cor(self, *args):
        selection = selected_atoms(self.session)
        
        models = {}
        for atom in selection:
            if atom.structure not in models:
                models[atom.structure] = [atom]
            else:
                models[atom.structure].append(atom)
        
        self.manual_center = {}
        for model in models:
            atoms = models[model]
            coords = np.array([atom.coord for atom in atoms])
            self.manual_center[model] = np.mean(coords, axis=0)

    def show_auto_status(self, text):
        if self.cor_button.currentText() == "automatic":
            if text == "bond":
                self.status_bar.showMessage("center set to one of the bonded atoms")
            elif text == "perpendicular to plane":
                self.status_bar.showMessage("center set to centroid of atoms")
            else:
                self.status_bar.showMessage("center set to centroid of rotating atoms")

        elif self.cor_button.currentText() == "select atoms":
            self.status_bar.showMessage("center set to centroid of specified atoms")
        
        else:
            self.status_bar.showMessage("center set to view's center of rotation")

    def set_bonds(self, *args):
        bonds = selected_bonds(self.session)
        if len(bonds) == 0:
            self.session.logger.error("no bonds selected")
            return
            
        models = [bond.structure for bond in bonds]
        if any(models.count(m) > 1 for m in models):
            self.session.logger.error("multiple bonds selected on the same structure")
            return
        
        self.bonds = {model:(bond.atoms[0].coord - bond.atoms[1].coord) for model, bond in zip(models, bonds)}
        self.bond_centers = {model:bond.atoms[1].coord for model, bond in zip(models, bonds)}

    def set_perpendicular(self, *args):
        atoms = selected_atoms(self.session)
        if len(atoms) == 0:
            self.session.logger.error("no atoms selected")
            return
        
        self.perpendiculars = {}
        self.perp_centers = {}
        
        models = set(atom.structure for atom in atoms)
        for model in models:
            atom_coords = []
            for atom in atoms:
                if atom.structure is model:
                    atom_coords.append(atom.coord)
            
            if len(atom_coords) < 3:
                self.session.logger.error("fewer than 3 atoms selected on %s" % model.atomspec)
                continue
            
            xyz = np.array(atom_coords)
            xyz -= np.mean(atom_coords, axis=0)
            R = np.dot(xyz.T, xyz)
            u, s, vh = np.linalg.svd(R, compute_uv=True)
            vector = u[:,-1]
            
            self.perpendiculars[model] = vector
            self.perp_centers[model] = np.mean(atom_coords, axis=0)

    def set_group(self, *args):
        atoms = selected_atoms(self.session)
        if len(atoms) == 0:
            self.session.logger.error("no atoms selected")
            return
        
        self.groups = {}
        
        models = set(atom.structure for atom in atoms)
        for model in models:
            atom_coords = []
            for atom in atoms:
                if atom.structure is model:
                    atom_coords.append(atom.coord)
        
            self.groups[model] = np.mean(atom_coords, axis=0)

    def do_rotate(self, *args):
        selection = selected_atoms(self.session)

        models = {}
        for atom in selection:
            if atom.structure not in models:
                models[atom.structure] = [atom]
            else:
                models[atom.structure].append(atom)
        
        if len(models.keys()) == 0:
            return
    
        if self.vector_option.currentText() == "axis":
            if self.axis.currentText() == "z":
                vector = np.array([0., 0., 1.])
            elif self.axis.currentText() == "y":
                vector = np.array([0., 1., 0.])            
            elif self.axis.currentText() == "x":
                vector = np.array([1., 0., 0.])
        
        elif self.vector_option.currentText() == "view axis":
            if self.view_axis.currentText() == "z":
                vector = self.session.view.camera.get_position().axes()[2]
            elif self.view_axis.currentText() == "y":
                vector = self.session.view.camera.get_position().axes()[1]       
            elif self.view_axis.currentText() == "x":
                vector = self.session.view.camera.get_position().axes()[0]
        
        elif self.vector_option.currentText() == "bond":
            vector = self.bonds
        
        elif self.vector_option.currentText() == "perpendicular to plane":
            vector = self.perpendiculars
        
        elif self.vector_option.currentText() == "centroid of atoms":
            vector = self.groups
        
        elif self.vector_option.currentText() == "custom":
            x = self.vector_x.value()
            y = self.vector_y.value()
            z = self.vector_z.value()
            vector = np.array([x, y, z])
        
        angle = np.deg2rad(self.angle.value())
        
        center = {}
        for model in models:
            atoms = models[model]
            coords = np.array([atom.coord for atom in atoms])
            center[model] = np.mean(coords, axis=0)
        
        if self.cor_button.currentText() == "automatic":
            if self.vector_option.currentText() == "perpendicular to plane":
                center = self.perp_centers
            
            elif self.vector_option.currentText() == "bond":
                center = self.bond_centers
        
        elif self.cor_button.currentText() == "select atoms":
            center = self.manual_center
        
        else:
            center = self.session.main_view.center_of_rotation

        for model in models:
            if isinstance(vector, dict):
                if model not in vector.keys():
                    continue
                else:
                    v = vector[model]
            
            else:
                v = vector
            
            if isinstance(center, dict):
                if model not in center.keys():
                    continue
                else:
                    c = center[model]
            
            else:
                c = center
            
            if self.vector_option.currentText() == "centroid of atoms" and self.cor_button.currentText() != "automatic":
                v = v - c

            v = v / np.linalg.norm(v)
            q = np.hstack(([np.cos(angle / 2)], v * np.sin(angle / 2)))
            
            q /= np.linalg.norm(q)
            qs = q[0]
            qv = q[1:]
        
            xyz = np.array([a.coord for a in models[model]])
            xyz -= c
            xprod = np.cross(qv, xyz)
            qs_xprod = 2 * qs * xprod
            qv_xprod = 2 * np.cross(qv, xprod)
    
            xyz += qs_xprod + qv_xprod + c
            for t, coord in zip(models[model], xyz):
                t.coord = coord

    def show_rot_vec(self, *args):
        for model in self.session.models.list(type=Generic3DModel):
            if model.name == "rotation vector":
                model.delete()
    
        if self.display_rot_vec.checkState() == Qt.Unchecked:
            return
        
        selection = selected_atoms(self.session)

        if len(selection) == 0:
            return

        models = {}
        for atom in selection:
            if atom.structure not in models:
                models[atom.structure] = [atom]
            else:
                models[atom.structure].append(atom)
        
        if len(models.keys()) == 0:
            return
    
        if self.vector_option.currentText() == "axis":
            if self.axis.currentText() == "z":
                vector = np.array([0., 0., 1.])
            elif self.axis.currentText() == "y":
                vector = np.array([0., 1., 0.])            
            elif self.axis.currentText() == "x":
                vector = np.array([1., 0., 0.])
        
        elif self.vector_option.currentText() == "view axis":
            if self.view_axis.currentText() == "z":
                vector = self.session.view.camera.get_position().axes()[2]
            elif self.view_axis.currentText() == "y":
                vector = self.session.view.camera.get_position().axes()[1]       
            elif self.view_axis.currentText() == "x":
                vector = self.session.view.camera.get_position().axes()[0]

        elif self.vector_option.currentText() == "bond":
            vector = self.bonds
        
        elif self.vector_option.currentText() == "perpendicular to plane":
            vector = self.perpendiculars
        
        elif self.vector_option.currentText() == "centroid of atoms":
            vector = self.groups
        
        elif self.vector_option.currentText() == "custom":
            x = self.vector_x.value()
            y = self.vector_y.value()
            z = self.vector_z.value()
            vector = np.array([x, y, z])
        
        angle = np.deg2rad(self.angle.value())
        
        center = {}
        for model in models:
            atoms = models[model]
            coords = np.array([atom.coord for atom in atoms])
            center[model] = np.mean(coords, axis=0)
        
        if self.cor_button.currentText() == "automatic":
            if self.vector_option.currentText() == "perpendicular to plane":
                center = self.perp_centers
            
            elif self.vector_option.currentText() == "bond":
                center = self.bond_centers
        
        elif self.cor_button.currentText() == "select atoms":
            center = self.manual_center
        
        else:
            center = self.session.main_view.center_of_rotation

        for model in models:
            if isinstance(vector, dict):
                if model not in vector.keys():
                    continue
                else:
                    v = vector[model]
            
            else:
                v = vector
            
            if isinstance(center, dict):
                if model not in center.keys():
                    continue
                else:
                    c = center[model]
            
            else:
                c = center
            
            if self.vector_option.currentText() == "centroid of atoms" and self.cor_button.currentText() != "automatic":
                v = v - c

            if np.linalg.norm(v) == 0:
                continue

            residues = []
            for atom in models[model]:
                if atom.residue not in residues:
                    residues.append(atom.residue)
            
            v_c = c + v
            
            s = ".color red\n"
            s += ".arrow %10.6f %10.6f %10.6f   %10.6f %10.6f %10.6f   0.2 0.4 0.7\n" % (*c, *v_c)
            
            stream = BytesIO(bytes(s, 'utf-8'))
            bild_obj, status = read_bild(self.session, stream, "rotation vector")

            self.session.models.add(bild_obj, parent=model)

    def delete(self):
        self.session.triggers.remove_handler(self._show_rot_vec)
        global_triggers = get_triggers()
        global_triggers.remove_handler(self._changes)
        
        for model in self.session.models.list(type=Generic3DModel):
            if model.name == "rotation vector":
                model.delete()
        
        return super().delete()

    def close(self):
        self.session.triggers.remove_handler(self._show_rot_vec)
        global_triggers = get_triggers()
        global_triggers.remove_handler(self._changes)
        
        for model in self.session.models.list(type=Generic3DModel):
            if model.name == "rotation vector":
                model.delete()
        
        return super().close()
