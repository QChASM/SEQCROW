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
    QHBoxLayout,
)

from SEQCROW.widgets import ElementButton
from SEQCROW.tools.bond_editor import ORDER_BOND_ORDER, BondOrderSpinBox, PTable2
from SEQCROW.tools.structure_editing import _PTable, SubstituentSelection
from SEQCROW.managers.filereader_manager import apply_seqcrow_preset
from SEQCROW.residue_collection import ResidueCollection

from AaronTools.internal_coordinates import *
from AaronTools.utils.utils import fibonacci_sphere

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
        self.build_layout = QFormLayout()
        
        self.build_layout.addRow(QLabel("select up to 3 atoms to define coordinates"))

        self.build_layout.addRow(QLabel("if no atoms are selected, a new structure will be created"))
        
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

        self.build_layout.addRow(self.type_selector, element_or_substituent_layout)
        
        self.atom1_label = QLabel("atom 1 <i>d</i>:")
        self.atom1_label.setToolTip("1-new distance")
        self.distance = QDoubleSpinBox()
        self.distance.setToolTip("1-new distance")
        self.distance.setDecimals(5)
        self.distance.setMinimum(0)
        self.distance.setMaximum(30)
        self.distance.setValue(1.51)
        self.distance.setSingleStep(0.05)
        self.distance.setSuffix(" Å")
        self.build_layout.addRow(self.atom1_label, self.distance)
        
        self.atom2_label = QLabel("atom 2 <i>θ</i>:")
        self.atom2_label.setToolTip("valence 2-1-new angle")
        self.valence_angle = QDoubleSpinBox()
        self.valence_angle.setToolTip("valence 2-1-new angle")
        self.valence_angle.setDecimals(5)
        self.valence_angle.setMinimum(0)
        self.valence_angle.setMaximum(180)
        self.valence_angle.setValue(120)
        self.valence_angle.setSingleStep(0.5)
        self.valence_angle.setSuffix("°")
        self.build_layout.addRow(self.atom2_label, self.valence_angle)
        
        coord3_widget = QWidget()
        coord3_widget.setToolTip("φ: 3-2-1-new torsional angle\n" + \
        "θ₂: valence 3-1-new angle")
        coord3_layout = QHBoxLayout(coord3_widget)
        coord3_layout.setContentsMargins(0, 0, 0, 0)
        self.coord3 = QComboBox()
        self.coord3.addItem("φ", "torsion")
        self.coord3.addItem("θ₂", "valence angle")
        self.atom3_label = QLabel(":")
        coord3_layout.addWidget(QLabel("atom 3"))
        coord3_layout.addWidget(self.coord3)
        coord3_layout.addWidget(self.atom3_label)
        self.torsion_angle = QDoubleSpinBox()
        self.torsion_angle.setToolTip("φ: 3-2-1-new torsional angle\n" + \
        "θ₂: valence 3-1-new angle")
        self.torsion_angle.setDecimals(5)
        self.torsion_angle.setMinimum(-180)
        self.torsion_angle.setMaximum(180)
        self.torsion_angle.setSingleStep(0.5)
        self.torsion_angle.setSuffix("°")
        self.build_layout.addRow(coord3_widget, self.torsion_angle)
        
        self.atom4_label = QLabel("atom 4 <i>θ<sub>3</sub></i>:")
        self.atom4_label.setToolTip("valence 4-1-new angle")
        self.valence_angle2 = QDoubleSpinBox()
        self.valence_angle2.setToolTip("valence 4-1-new angle")
        self.valence_angle2.setDecimals(5)
        self.valence_angle2.setMinimum(0)
        self.valence_angle2.setMaximum(180)
        self.valence_angle2.setValue(120)
        self.valence_angle2.setSingleStep(0.5)
        self.valence_angle2.setSuffix("°")
        self.build_layout.addRow(self.atom4_label, self.valence_angle2)
        self.valence_angle2_row = self.build_layout.rowCount() - 1
        self.build_layout.setRowVisible(self.valence_angle2_row, False)
        self.coord3.currentIndexChanged.connect(self.show_valence_angle2)
        
        add_atom = QPushButton("add atom/substituent")
        add_atom.clicked.connect(self.place_new_atom)
        self.build_layout.addRow(add_atom)
        
        draw_bond = QPushButton("bond selected atoms")
        draw_bond.clicked.connect(self.draw_new_bond)
        
        delete_atoms = QPushButton("delete selected atoms")
        delete_atoms.clicked.connect(self.delete_selected_atoms)
        self.build_layout.addRow(draw_bond, delete_atoms)

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
        
        self.build_layout.addRow(bond_lookup)
        
        quick_angles = QGroupBox("quick angles")
        quick_angles_layout = QFormLayout(quick_angles)

        quick_angle1_widget = QWidget()
        quick_angle1_layout = QHBoxLayout(quick_angle1_widget)
        quick_angle1_layout.setContentsMargins(0, 0, 0, 0)
        quick_angle2_widget = QWidget()
        quick_angle2_layout = QHBoxLayout(quick_angle2_widget)
        quick_angle2_layout.setContentsMargins(0, 0, 0, 0)
        quick_angle3_widget = QWidget()
        quick_angle3_layout = QHBoxLayout(quick_angle3_widget)
        quick_angle3_layout.setContentsMargins(0, 0, 0, 0)
        for i, angle in enumerate([90, np.rad2deg(np.arccos(-1./3)), 120, 180]):
            button = QPushButton("%.1f" % angle)
            button.clicked.connect(
                lambda *args, a=angle: self.set_angle_value(a)
            )
            button.setMaximumWidth(int(3.2 * button.fontMetrics().boundingRect("0000").width()))
            quick_angle1_layout.addWidget(button)
            
            button = QPushButton("%.1f" % angle)
            button.clicked.connect(
                lambda *args, a=angle: self.set_angle2_value(a)
            )
            button.setMaximumWidth(int(3.2 * button.fontMetrics().boundingRect("0000").width()))
            quick_angle2_layout.addWidget(button)
            
            button = QPushButton("%.1f" % angle)
            button.clicked.connect(
                lambda *args, a=angle: self.set_angle3_value(a)
            )
            button.setMaximumWidth(int(3.2 * button.fontMetrics().boundingRect("0000").width()))
            quick_angle3_layout.addWidget(button)
        quick_angles_layout.addRow(QLabel("<i>θ</i>:"), quick_angle1_widget)
        quick_angles_layout.addRow(QLabel("<i>θ</i><sub>2</sub>:"), quick_angle2_widget)
        quick_angles_layout.addRow(QLabel("<i>θ</i><sub>3</sub>:"), quick_angle3_widget)
        quick_angles_layout.setRowVisible(1, False)
        quick_angles_layout.setRowVisible(2, False)
        
        torsion_widget = QWidget()
        torsion_layout = QHBoxLayout(torsion_widget)
        torsion_layout.setContentsMargins(0, 0, 0, 0)
        for i, angle in enumerate([-120, -90, -60, 0, 60, 90, 120, 180]):
            button = QPushButton("%i" % angle)
            button.clicked.connect(
                lambda *args, a=angle: self.set_torsion_value(a)
            )
            button.setMaximumWidth(int(1.6 * button.fontMetrics().boundingRect("0000").width()))
            torsion_layout.addWidget(button)
        
        quick_angles_layout.addRow(QLabel("<i>φ</i>:"), torsion_widget)
        
        # index 0 = torsion, hide the valence 2 and 3 options and show the torsion
        # index 1 = valence angle, do the opposite
        self.coord3.currentIndexChanged.connect(
            lambda x: quick_angles_layout.setRowVisible(1, bool(x))
        )
        self.coord3.currentIndexChanged.connect(
            lambda x: quick_angles_layout.setRowVisible(2, bool(x))
        )
        self.coord3.currentIndexChanged.connect(
            lambda x: quick_angles_layout.setRowVisible(3, not bool(x))
        )
        
        self.build_layout.addRow(quick_angles)
        
        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        self.build_layout.addRow(self.status)

        self.tool_window.ui_area.setLayout(self.build_layout)

        self.tool_window.manage(None)
    
    def show_valence_angle2(self, ndx):
        if ndx == 0:
            self.build_layout.setRowVisible(self.valence_angle2_row, False)
        else:
            self.build_layout.setRowVisible(self.valence_angle2_row, True)

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
    
    def set_angle2_value(self, angle):
        self.torsion_angle.setValue(angle)
    
    def set_angle3_value(self, angle):
        self.valence_angle2.setValue(angle)
    
    def set_torsion_value(self, angle):
        self.torsion_angle.setValue(angle)
    
    def draw_new_bond(self):
        run(self.session, "bond sel reasonable false")

    def update_atom_labels(self, *args, **kwargs):
        self.atom1_label.setText("atom 1 <i>d</i>:")
        self.atom2_label.setText("atom 2 <i>θ</i>:")
        self.atom3_label.setText(":")
        self.atom4_label.setText("atom 4 <i>θ</i><sub>3</sub>:")
        sel = selected_atoms(self.session)
        if len(sel) == 0 or len(sel) > 4 or (
            len(sel) > 3 and self.coord3.currentData() == "torsion"
        ):
            return
        if not all(a.structure is sel[0].structure for a in sel[1:]):
            return
        
        labels = [self.atom1_label, self.atom2_label, self.atom3_label, self.atom4_label]
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
            coord3 = np.dot(coord3, R.T)
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
            coord4 = np.dot(coord4, R.T)
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
    
    def place_substituent(self, atom, other_atom, sub_name):
        sub = Substituent(sub_name)
        ndx = {a: i for i, a in enumerate(sub.atoms)}
        v1 = atom.coord - other_atom.coord
        sub.align_to_bond(v1)
        sub.coords -= sub.atoms[0].coords
        sub.coords += atom.coord
        ele = atom.element.get_element(sub.atoms[0].element)
        atom.element = ele

        new_atoms = [atom]
        for a in sub.atoms[1:]:
            name = self.get_atom_name(a.element, atom.residue)
            chix_atom = atom.structure.new_atom(name, a.element)
            chix_atom.coord = a.coords
            atom.residue.add_atom(chix_atom)
            new_atoms.append(chix_atom)
        
        for a1 in sub.atoms:
            chix_a1 = new_atoms[ndx[a1]]
            if a1 is sub.atoms[0]:
                chix_a1 = atom
            for a2 in a1.connected:
                if ndx[a2] < ndx[a1]:
                    continue
                chix_a2 = new_atoms[ndx[a2]]
                bond = atom.structure.new_bond(chix_a1, chix_a2)
        
        apply_seqcrow_preset(
            atom.structure,
            atoms=new_atoms,
        )
    
    def place_new_atom(self):
        sel = selected_atoms(self.session)
        element = self.element_button.text()
        substituent = self.substituent_button.text()
        placing_substituent = self.type_selector.currentText() == "substituent:"

        if len(sel) == 0:
            # create a new structure
            if placing_substituent:
                sub = Substituent(substituent)
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
        
        if len(sel) > 3 and self.coord3.currentData() == "torsion":
            self.session.logger.error("cannot select more than three atoms (%i selected)" % len(sel))
            return
        
        if len(sel) > 4:
            self.session.logger.error("cannot select more than four atoms (%i selected)" % len(sel))
            return
        
        # place the new atom the right distance away from atom1
        # this is done by adjusting the z component of the coordinate
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

        # only one atom is selected, so we can't use angles or anything
        # to further refine the coordinates
        if len(sel) < 2:
            if placing_substituent:
                self.place_substituent(atom, sel[-1], substituent)
            return
        
        valence_angle = np.deg2rad(self.valence_angle.value())
        atom2 = sel[-2]
        angle_set = False
        i = 0
        while not angle_set and i < 10:
            angle_set, coords = self.set_angle(
                atom2.coord, atom1.coord, coords, valence_angle,
            )
            i += 1
        atom.coord = coords
        
        # if there's only two atoms or if it's a linear angle
        # we won't try to set the torsion
        if len(sel) < 3 or (
            np.isclose(valence_angle - np.pi, 0) and self.coord3.currentData() == "torsion"
        ):
            if placing_substituent:
                self.place_substituent(atom, sel[-1], substituent)
            return
        
        # we do initially try to set the position
        # this will technically work for torsions
        # with two valence angles, it might not have a unique
        # solution or any solution at all
        # with three valence angles, it might have a unique
        # solution but it might also have no solution
        # only rotating one to match one angle at a time
        # will probably not find a suitable solution, or
        # we would have to iterate all angles multiple times
        # instead we set up some internal coordinates
        # and fit to those
        atom3 = sel[-3]
        torsion_angle = np.deg2rad(self.torsion_angle.value())
        angle_set = False
        i = 0
        # try the initial rotation to match the angle/torsion
        if self.coord3.currentData() == "torsion":
            while not angle_set and i < 10:
                angle_set, coords = self.set_torsion(
                    atom3.coord,
                    atom2.coord,
                    atom1.coord,
                    coords,
                    torsion_angle,
                )
                i += 1
        else:
            while not angle_set and i < 10:
                angle_set, coords = self.set_angle(
                    atom3.coord,
                    atom1.coord,
                    coords,
                    torsion_angle,
                )
                i += 1
        
        atom.coord = coords
        
        valence_angle2 = np.deg2rad(self.valence_angle2.value())
        
        # set up the internal coordinates
        # numbers correspond to indices in current_cartesians
        # which is set up later
        ric = CustomizableRIC()
        bond = Bond(0, 1)
        ric.coordinates["bonds"] = [bond]
        angle1 = Angle(0, 1, 2)
        ric.coordinates["angles"] = [angle1]
        if self.coord3.currentData() == "torsion":
            angle2 = Torsion([0], 1, 2, [3])
            ric.coordinates["torsions"] = [angle2]
        else:
            angle2 = Angle(0, 1, 3)
            ric.coordinates["angles"].append(angle2)

        # include the cartesian coordinates of the selected atoms
        # this will definitely prevent things from rotating/translating
        # when the internal coordinates are fit
        ric.coordinates["cartesian"] = [
            CartesianCoordinate(1),
            CartesianCoordinate(2),
            CartesianCoordinate(3),
        ]
        angle3 = None
        if len(sel) == 4:
            angle3 = Angle(0, 1, 4)
            ric.coordinates["angles"].append(angle3)
            ric.coordinates["cartesian"].append(CartesianCoordinate(4))
        
        atom_coords = [a.coord for a in sel[::-1]]
        current_cartesians = np.array([
            atom.coord,
            *atom_coords,
        ])
        # determine the current coordinates and what we
        # want them to be
        current_q = ric.values(current_cartesians)
        desired_q = current_q.copy()
        i = 0
        for coord_type in ric.coordinates:
            for coord in ric.coordinates[coord_type]:
                if coord is bond:
                    desired_q[i] = dist
                if coord is angle1:
                    desired_q[i] = valence_angle
                if coord is angle2:
                    desired_q[i] = torsion_angle
                if coord is angle3:
                    desired_q[i] = valence_angle2
                i += coord.n_values
    
        # try numerous points around atom1 to see which point best matches
        # the requested coordinates
        # without this, if there are 3 valence angles given we could
        # end up with a poor solution for the final coordinates
        # this grid usually gets a point pretty close to the final (<0.05 error)
        best_pt = atom.coord
        lowest_diff = None
        test_coords = current_cartesians.copy()
        for pt in fibonacci_sphere(radius=dist, center=atom1.coord):
            test_coords[0] = pt
            test_q = ric.values(test_coords)
            diff = np.linalg.norm(ric.adjust_phase(test_q - desired_q))
            if lowest_diff is None or diff < lowest_diff:
                lowest_diff = diff
                best_pt = pt
                current_q = test_q
        
        current_cartesians[0] = best_pt
        
        # adjust the cartesian coordinates to match the desired
        # change in internal coordinates
        dq = desired_q - current_q
        
        new_coords, err = ric.apply_change(
            current_cartesians, dq,
            use_delocalized=False,
            debug=False,
        )
        if err > 1e-5:
            self.session.logger.warning(
                "could not converge structure to match specified internal coordinates\n" + \
                "these internal coordinates might not correspond to a point in 3D space"
            )

        current_cartesians[0] = new_coords[0]

        atom.coord = new_coords[0]
        if placing_substituent:
            self.place_substituent(atom, sel[-1], substituent)

