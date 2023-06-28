from AaronTools.utils.utils import angle_between_vectors, perp_vector, rotation_matrix

from chimerax.atomic import selected_atoms, AtomicStructure
from chimerax.ui.gui import MainToolWindow
from chimerax.core.tools import ToolInstance
from chimerax.core.commands import run
from chimerax.core.selection import SELECTION_CHANGED

from Qt.QtCore import Qt
from Qt.QtWidgets import (
    QLabel,
    QPushButton,
    QComboBox,
    QWidget,
    QFormLayout,
    QCheckBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QStatusBar,
)

from SEQCROW.widgets import ElementButton
from SEQCROW.tools.bond_editor import ORDER_BOND_ORDER, BondOrderSpinBox, PTable2
from SEQCROW.tools.structure_editing import _PTable
from SEQCROW.managers.filereader_manager import apply_seqcrow_preset

import numpy as np


class ZMatrixBuilder(ToolInstance):
    def __init__(self, session, name):
        super().__init__(session, name)

        self.tool_window = MainToolWindow(self)        

        self._build_ui()
        
        self._update_atom_labels = self.session.triggers.add_handler(
            SELECTION_CHANGED,
            self.update_atom_labels,
        )

    def _build_ui(self):
        layout = QFormLayout()
        
        layout.addRow(QLabel("select up to 3 atoms to define coordinates"))

        layout.addRow(QLabel("if no atoms are selected, a new structure will be created"))
        
        self.element_button = ElementButton("C", single_state=True)
        self.element_button.clicked.connect(self.open_ptable)
        layout.addRow("element:", self.element_button)
        
        self.atom1_label = QLabel("atom 1 <i>d</i>:")
        self.distance = QDoubleSpinBox()
        self.distance.setDecimals(4)
        self.distance.setMinimum(0)
        self.distance.setMaximum(30)
        self.distance.setValue(1.51)
        self.distance.setSingleStep(0.05)
        self.distance.setSuffix(" Å")
        layout.addRow(self.atom1_label, self.distance)
        
        self.atom2_label = QLabel("atom 2 <i>θ</i>:")
        self.valence_angle = QDoubleSpinBox()
        self.valence_angle.setDecimals(4)
        self.valence_angle.setMinimum(0)
        self.valence_angle.setMaximum(180)
        self.valence_angle.setValue(120)
        self.valence_angle.setSingleStep(0.5)
        self.valence_angle.setSuffix("°")
        layout.addRow(self.atom2_label, self.valence_angle)
        
        self.atom3_label = QLabel("atom 3 <i>φ</i>:")
        self.torsion_angle = QDoubleSpinBox()
        self.torsion_angle.setDecimals(4)
        self.torsion_angle.setMinimum(-180)
        self.torsion_angle.setMaximum(180)
        self.torsion_angle.setSingleStep(0.5)
        self.torsion_angle.setSuffix("°")
        layout.addRow(self.atom3_label, self.torsion_angle)
        
        add_atom = QPushButton("add atom")
        add_atom.clicked.connect(self.place_new_atom)
        layout.addRow(add_atom)
        
        draw_bond = QPushButton("bond selected atoms")
        draw_bond.clicked.connect(self.draw_new_bond)
        layout.addRow(draw_bond)
        
        delete_atoms = QPushButton("delete selected atoms")
        delete_atoms.clicked.connect(self.delete_selected_atoms)
        layout.addRow(delete_atoms)
        
        bond_lookup = QGroupBox("bond length lookup")
        bond_lookup_layout = QGridLayout(bond_lookup)
        
        bond_lookup_layout.addWidget(
            QLabel("elements:"),
            0, 0,
        )
        
        self.ele1 = ElementButton("C", single_state=True)
        self.ele1.clicked.connect(lambda *args, button=self.ele1: self.open_bo_ptable(button))
        bond_lookup_layout.addWidget(self.ele1, 0, 1, Qt.AlignRight | Qt.AlignTop)
        
        bond_lookup_layout.addWidget(QLabel("-"), 0, 2, Qt.AlignHCenter | Qt.AlignVCenter)
        
        self.ele2 = ElementButton("C", single_state=True)
        self.ele2.clicked.connect(lambda *args, button=self.ele2: self.open_bo_ptable(button))
        bond_lookup_layout.addWidget(self.ele2, 0, 3, Qt.AlignLeft | Qt.AlignTop)
        
        bond_lookup_layout.addWidget(QLabel("bond order:"), 1, 0)
        
        self.bond_order = BondOrderSpinBox()
        self.bond_order.setRange(1., 3.)
        self.bond_order.setValue(1)
        self.bond_order.setSingleStep(0.5)
        self.bond_order.setDecimals(1)
        self.bond_order.valueChanged.connect(self.check_bond_lengths)
        bond_lookup_layout.addWidget(self.bond_order, 1, 1, 1, 3)
        
        bond_lookup_layout.setColumnStretch(0, 0)
        bond_lookup_layout.setColumnStretch(1, 0)
        bond_lookup_layout.setColumnStretch(2, 0)
        bond_lookup_layout.setColumnStretch(3, 1)
        
        layout.addRow(bond_lookup)
        
        quick_angles = QGroupBox("quick angles")
        quick_angles_layout = QGridLayout(quick_angles)
        
        quick_angles_layout.addWidget(QLabel("<i>θ</i>:"), 0, 0, 1, 1)
        quick_angles_layout.addWidget(QLabel("<i>φ</i>:"), 1, 0, 1, 1)
        
        for i, angle in enumerate([90, 109.4712206, 120, 180]):
            button = QPushButton("%.1f" % angle)
            button.clicked.connect(
                lambda *args, a=angle: self.set_angle_value(a)
            )
            button.setMaximumWidth(int(3.2 * button.fontMetrics().boundingRect("0000").width()))
            quick_angles_layout.addWidget(button, 0, 2 * i + 1, 1, 2, alignment=Qt.AlignHCenter | Qt.AlignTop)
        
        for i, angle in enumerate([-120, -90, -60, 0, 60, 90, 120, 180]):
            button = QPushButton("%i" % angle)
            button.clicked.connect(
                lambda *args, a=angle: self.set_torsion_value(a)
            )
            button.setMaximumWidth(int(1.6 * button.fontMetrics().boundingRect("0000").width()))
            quick_angles_layout.addWidget(button, 1, i + 1, 1, 1, alignment=Qt.AlignHCenter | Qt.AlignTop)
        
        layout.addRow(quick_angles)
        
        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        layout.addRow(self.status)
        
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
    
    def set_angle_value(self, angle):
        self.valence_angle.setValue(angle)
    
    def set_torsion_value(self, angle):
        self.torsion_angle.setValue(angle)
    
    def draw_new_bond(self):
        run(self.session, "bond sel reasonable false")

    def update_atom_labels(self, *args, **kwargs):
        self.atom1_label.setText("atom 1 <i>d</i>:")
        self.atom2_label.setText("atom 2 <i>θ</i>:")
        self.atom3_label.setText("atom 3 <i>φ</i>:")
        sel = selected_atoms(self.session)
        if len(sel) == 0 or len(sel) > 3:
            return
        if not all(a.structure is sel[0].structure for a in sel[1:]):
            return
        
        labels = [self.atom1_label, self.atom2_label, self.atom3_label]
        for a, label in zip(sel[::-1], labels):
            label.setText("%s %s" % (label.text(), a.atomspec))

    def delete(self):
        self.session.triggers.remove_handler(self._update_atom_labels)

        return super().delete()

    def delete_selected_atoms(self):
        run(self.session, "del sel")
    
    def open_ptable(self, *args):
        self.tool_window.create_child_window(
            "select element",
            window_class=_PTable,
            button=self.element_button,
            show_dummy=True,
        )

    def open_bo_ptable(self, button):
        self.tool_window.create_child_window(
            "select element",
            window_class=PTable2,
            button=button,
            callback=self.check_bond_lengths,
        )
    
    def check_bond_lengths(self, *args):
        ele1 = self.ele1.text()
        ele2 = self.ele2.text()
        key = ORDER_BOND_ORDER.key(ele1, ele2)
        
        order = "%.1f" % self.bond_order.value()
        if key in ORDER_BOND_ORDER.bonds and order in ORDER_BOND_ORDER.bonds[key]:
            self.distance.setValue(ORDER_BOND_ORDER.bonds[key][order])
            self.status.showMessage("")
        else:
            self.status.showMessage("no bond data for %s-%s %sx bonds" % (ele1, ele2, order))

    def get_atom_name(self, element, residue):
        i = 1
        name_found = False
        while not name_found:
            for atom in residue.atoms:
                if atom.element.name != element:
                    continue
                if atom.element.name == element and atom.name == "%s%i" % (element, i):
                    i += 1
                    break
            else:
                name_found = True
            
        return "%s%i" % (element, i)
    
    def set_angle(self, coord1, coord2, coord3, target_angle):
        b1 = coord1 - coord2
        b2 = coord3 - coord2
        current_angle = angle_between_vectors(b1, b2)
        d_theta = target_angle - current_angle
        if abs(d_theta) > 1e-5:
            coords = np.array([
                b1,
                [0, 0, 0],
                b2,
            ])
            v = perp_vector(coords)
            R = rotation_matrix(d_theta, v)
            coord3 -= coord2
            coord3 = np.dot(R, coord3)
            coord3 += coord2
            b1 = coord1 - coord2
            b2 = coord3 - coord2
            current_angle = angle_between_vectors(b1, b2)
        return abs(current_angle - target_angle) < 1e-5, coord3
    
    def set_torsion(self, coord1, coord2, coord3, coord4, target_angle):
        b1 = coord4 - coord3
        b2 = coord3 - coord2
        b3 = coord2 - coord1
        v1 = np.cross(b1, b2)
        v2 = np.cross(b2, b3)
        current_angle = -np.arctan2(
            np.dot(b2, np.cross(v1, v2)),
            np.linalg.norm(b2) * np.dot(v1, v2)
        )
        da = target_angle - current_angle
        if abs(da) > 1e-5:
            R = rotation_matrix(-da, coord2 - coord3)
            coord4 -= coord3
            coord4 = np.dot(R, coord4)
            coord4 += coord3
            b1 = coord4 - coord3
            b2 = coord3 - coord2
            b3 = coord2 - coord1
            v1 = np.cross(b1, b2)
            v2 = np.cross(b2, b3)
            current_angle = -np.arctan2(
                np.dot(b2, np.cross(v1, v2)),
                np.linalg.norm(b2) * np.dot(v1, v2)
            )
        return abs(current_angle - target_angle) < 1e-5, coord4
    
    def place_new_atom(self):
        sel = selected_atoms(self.session)
        element = self.element_button.text()
        if len(sel) == 0:
            # create a new structure
            mdl = AtomicStructure(self.session, name="new")
            res = mdl.new_residue("new", "a", 1)
            name = self.get_atom_name(element, res)
            atom = mdl.new_atom(name, element)
            atom.coord = np.zeros(3)
            res.add_atom(atom)
            self.session.models.add([mdl])
            apply_seqcrow_preset(
                mdl,
                atoms=[atom],
            )
            return
        
        if not all(a.structure is sel[0].structure for a in sel[1:]):
            self.session.logger.error("selected atoms must be in the same structure")
            return
        
        if len(sel) > 3:
            self.session.logger.error("cannot select more than three atoms (%i selected)" % len(sel))
            return
        
        atom1 = sel[-1]
        res = atom1.residue
        name = self.get_atom_name(element, res)
        atom = atom1.structure.new_atom(name, element)
        res.add_atom(atom)
        coords = np.array(atom1.coord)
        dist = self.distance.value()
        coords[2] += dist
        atom.coord = coords
        run(self.session, "bond %s %s reasonable true" % (atom.atomspec, atom1.atomspec))
        apply_seqcrow_preset(
            atom1.structure,
            atoms=[atom],
        )

        if len(sel) < 2:
            return
        
        angle = np.deg2rad(self.valence_angle.value())
        atom2 = sel[-2]
        angle_set = False
        i = 0
        while not angle_set and i < 10:
            angle_set, coords = self.set_angle(
                atom2.coord, atom1.coord, coords, angle,
            )
            i += 1
        atom.coord = coords
        
        if len(sel) < 3:
            return
        
        atom3 = sel[-3]
        angle = np.deg2rad(self.torsion_angle.value())
        angle_set = False
        i = 0
        while not angle_set and i < 10:
            angle_set, coords = self.set_torsion(
                atom3.coord,
                atom2.coord,
                atom1.coord,
                coords,
                angle,
            )
            i += 1
        atom.coord = coords

