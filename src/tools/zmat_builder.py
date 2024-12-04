from AaronTools.utils.utils import angle_between_vectors, perp_vector, rotation_matrix
from AaronTools.substituent import Substituent

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
    QTabWidget,
)

from SEQCROW.widgets import ElementButton
from SEQCROW.tools.bond_editor import ORDER_BOND_ORDER, BondOrderSpinBox, PTable2
from SEQCROW.tools.structure_editing import _PTable, SubstituentSelection
from SEQCROW.managers.filereader_manager import apply_seqcrow_preset
from SEQCROW.residue_collection import ResidueCollection

from AaronTools.internal_coordinates import *

import numpy as np


# convenient q transformation for RIC
class CustomizableRIC(InternalCoordinateSet):
    def __init__(self):
        self.coordinates = {
            "cartesian": [],
            "bonds": [],
            "angles": [],
            "linear angles": [],
            "torsions": [],
        }

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
        tool_layout = QFormLayout()
        
        self.tabs = QTabWidget()
        tool_layout.addRow(self.tabs)
    
        build_tab = QWidget()
        layout = QFormLayout(build_tab)
        
        layout.addRow(QLabel("select up to 3 atoms to define coordinates"))

        layout.addRow(QLabel("if no atoms are selected, a new structure will be created"))
        
        self.substituent_button = QPushButton("Me")
        self.substituent_button.clicked.connect(self.open_substituent_selector)
        
        self.element_button = ElementButton("C", single_state=True)
        self.element_button.clicked.connect(self.open_ptable)

        self.type_selector = QComboBox()
        self.type_selector.addItems(["element:", "substituent:"])
        self.type_selector.currentTextChanged.connect(self.select_shown_button)

        element_or_substituent = QWidget()
        element_or_substituent_layout = QGridLayout()
        element_or_substituent_layout.addWidget(self.element_button, 0, 0)
        element_or_substituent_layout.addWidget(self.substituent_button, 0, 1)
        self.select_shown_button("element:")

        layout.addRow(self.type_selector, element_or_substituent_layout)
        
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
        
        add_atom = QPushButton("add atom/substituent")
        add_atom.clicked.connect(self.place_new_atom)
        layout.addRow(add_atom)
        
        draw_bond = QPushButton("bond selected atoms")
        draw_bond.clicked.connect(self.draw_new_bond)
        layout.addRow(draw_bond)
        
        delete_atoms = QPushButton("delete selected atoms")
        delete_atoms.clicked.connect(self.delete_selected_atoms)
        layout.addRow(delete_atoms)
        
        self.tabs.addTab(build_tab, "build")
        
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
        
        tool_layout.addRow(bond_lookup)
        
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
        
        tool_layout.addRow(quick_angles)
        
        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        tool_layout.addRow(self.status)

        self.tool_window.ui_area.setLayout(tool_layout)

        self.tool_window.manage(None)
    
    def select_shown_button(self, text):
        if text == "element:":
            self.element_button.setVisible(True)
            self.substituent_button.setVisible(False)
        else:
            self.element_button.setVisible(False)
            self.substituent_button.setVisible(True)

    def open_substituent_selector(self, *args):
        self.tool_window.create_child_window(
            "select a substituent",
            window_class=SubstituentSelection,
            textBox=self.substituent_button,
            singleSelect=True,
        )

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
        b2 = coord3[0, :] - coord2
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
            coord3 = np.dot(R, coord3.T).T
            coord3 += coord2
            b1 = coord1 - coord2
            b2 = coord3[0, :] - coord2
            current_angle = angle_between_vectors(b1, b2)
        return abs(current_angle - target_angle) < 1e-5, coord3
    
    def set_torsion(self, coord1, coord2, coord3, coord4, target_angle):
        b1 = coord4[0, :] - coord3
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
            coord4 = np.dot(R, coord4.T).T
            coord4 += coord3
            b1 = coord4[0, :] - coord3
            b2 = coord3 - coord2
            b3 = coord2 - coord1
            v1 = np.cross(b1, b2)
            v2 = np.cross(b2, b3)
            current_angle = -np.arctan2(
                np.dot(b2, np.cross(v1, v2)),
                np.linalg.norm(b2) * np.dot(v1, v2)
            )
        return abs(current_angle - target_angle) < 1e-5, coord4
    
    def add_new_sub_atoms(self, sub, atom):
            new_atoms = []
            for a in sub.atoms:
                name = self.get_atom_name(a.element, atom.residue)
                chix_atom = atom.structure.new_atom(name, a.element)
                chix_atom.coord = a.coords
                atom.residue.add_atom(chix_atom)
                new_atoms.append(chix_atom)
            
            run(self.session, "bond %s %s reasonable true" % (new_atoms[0].atomspec, atom.atomspec))
            apply_seqcrow_preset(
                atom.structure,
                atoms=new_atoms,
            )
    
    def place_new_atom(self):
        sel = selected_atoms(self.session)
        element = self.element_button.text()
        substituent = self.substituent_button.text()
        placing_substituent = self.type_selector.currentText() == "substituent:"
        if placing_substituent:
            sub = Substituent(substituent)
        
        if len(sel) == 0:
            # create a new structure
            if placing_substituent:
                rescol = ResidueCollection(sub)
                mdl = rescol.get_chimera(
                    self.session,
                    apply_preset=False,
                )
                self.session.models.add([mdl])
                apply_seqcrow_preset(
                    mdl,
                )
            else:
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
        if placing_substituent:
            coords = sub.coords
            coords -= sub.atoms[0].coords
        else:
            atom = atom1.structure.new_atom(name, element)
            res.add_atom(atom)
            coords = np.array(atom1.coord, ndmin=2)
        dist = self.distance.value()
        coords[:, 2] += dist
        if placing_substituent:
            sub.coords = coords
        else:
            atom.coord = coords[0]
            run(self.session, "bond %s %s reasonable true" % (atom.atomspec, atom1.atomspec))
            apply_seqcrow_preset(
                atom1.structure,
                atoms=[atom],
            )

        if len(sel) < 2:
            if self.placing_substituent:
                self.add_new_sub_atoms(sub, atom1)
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
        if placing_substituent:
            sub.coords = coords
        else:
            atom.coord = coords[0]
        
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
        
        ric = CustomizableRIC()
        ric.coordinates["bonds"] = [
            Bond(0, 1),
        ]
        valence_angle = self.valence_angle.value()
        ric.coordinates["angles"] = [
            Angle(0, 1, 2),
        ]
        ric.coordinates["torsions"] = [
            Torsion([0], 1, 2, [3]),
        ]
        ric.coordinates["cartesian"] = [
            CartesianCoordinate(1),
            CartesianCoordinate(2),
            CartesianCoordinate(3),
        ]
        if placing_substituent:
            sub_ric = InternalCoordinateSet(sub, torsion_type="all", oop_type="improper")
            for coord_type, coords in sub_ric.coordinates.items():
                ric.coordinates.setdefault(coord_type, [])
                for coord in coords:
                    if hasattr(coord, "atom1") and coord.atom1 != 0:
                        coord.atom1 += 3
                    if hasattr(coord, "atom2") and coord.atom2 != 0:
                        coord.atom2 += 3
                    if hasattr(coord, "atom3") and coord.atom3 != 0:
                        coord.atom3 += 3
                    if hasattr(coord, "atom") and coord.atom != 0:
                        coord.atom += 3
                    if hasattr(coord, "group1"):
                        coord.group1 = [i + 3 if i != 0 else i for i in coord.group1]
                    if hasattr(coord, "group2"):
                        coord.group2 = [i + 3 if i != 0 else i for i in coord.group2]
                    ric.coordinates[coord_type].append(coord)
        print(ric.coordinates)
        
        if placing_substituent:
            current_cartesians = np.array([
                sub.atoms[0].coords,
                atom1.coord,
                atom2.coord,
                atom3.coord,
                *sub.coords[1:],
            ])
        else:
            current_cartesians = np.array([
                atom.coord,
                atom1.coord,
                atom2.coord,
                atom3.coord,
            ])
        print("current cartesian")
        print(current_cartesians)
        current_q = ric.values(current_cartesians)
        desired_q = current_q.copy()
        i = 0
        for coord_type in ric.coordinates:
            if coord_type == "bonds":
                desired_q[i] = dist
            if coord_type == "angles":
                desired_q[i] = np.deg2rad(valence_angle)
            if coord_type == "torsions":
                desired_q[i] = np.deg2rad(angle)
            for coord in ric.coordinates[coord_type]:
                i += coord.n_values
                print(i, coord, coord.value(current_cartesians))

        dq = ric.adjust_phase(desired_q - current_q)
        print("current", current_q)
        print("desired", desired_q)
        print("desired change", dq)
        new_coords, err = ric.apply_change(current_cartesians, dq)
        print("new cartesian")
        print(new_coords)
        print("dq -> x error")
        print(err)
        new_q = ric.values(new_coords)
        print("new", new_q)
        final_dq = new_q - current_q
        print("actual change", final_dq)
        print("difference from desired", final_dq - dq)

        if placing_substituent:
            for i, a in enumerate(sub.atoms):
                if i != 0:
                    i += 3
                a.coords = new_coords[i]
            self.add_new_sub_atoms(sub, atom1)
        else:
            atom.coord = new_coords[0]

