from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow

from Qt.QtCore import Qt
from Qt.QtGui import QIcon
from Qt.QtWidgets import (
    QPushButton,
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
)

from AaronTools.atoms import Atom
from AaronTools.component import Component

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.libraries import LigandTable
from SEQCROW.managers.filereader_manager import apply_seqcrow_preset
from SEQCROW.tools.structure_editing import _PTable
from SEQCROW.widgets.periodic_table import ElementButton

def create_coord_items(tool, layout, allow_minimization=True, default_ele="Ca"):
    """
    add widgets to the layout and set appropriate attributes for tool
    this is used by this tool and the AaronJr input builder
    """
    tool.element = ElementButton(default_ele, single_state=True)
    tool.element.clicked.connect(lambda *args, t=tool: open_ptable(t))
    layout.addRow("element:", tool.element)

    tool.vsepr = QComboBox()
    tool.vsepr.addItems([
        "trigonal pyramidal",             # 1
        "tetrahedral",                    # 2
        "seesaw",                         # 3
        "square planar",                  # 4
        
        "trigonal bipyramidal",           # 5
        "square pyramidal",               # 6
        "pentagonal",                     # 7
        
        "octahedral",                     # 8
        "hexagonal",                      # 9
        "trigonal prismatic",             #10
        "pentagonal pyramidal",           #11
        
        "capped octahedral",              #12
        "capped trigonal prismatic",      #13
        "heptagonal",                     #14
        "hexagonal pyramidal",            #15
        "pentagonal bipyramidal",         #16
    ])
    
    tool.vsepr.setCurrentIndex(7)
    
    tool.vsepr.insertSeparator(11)
    tool.vsepr.insertSeparator(7)
    tool.vsepr.insertSeparator(4)
    layout.addRow("geometry:", tool.vsepr)
    
    if allow_minimization:
        tool.minimize = QCheckBox()
        tool.minimize.setCheckState(Qt.Checked)
        tool.minimize.setToolTip("rotate substituents on ligands to mitigate steric clashing")
        layout.addRow("relax ligands:", tool.minimize)
    
    ligand_box = QGroupBox("ligands")
    ligand_layout = QFormLayout(ligand_box)
    layout.addRow(ligand_box)
    
    tool.ligand_table = QTableWidget()
    tool.ligand_table.setColumnCount(3)
    tool.ligand_table.setHorizontalHeaderLabels(["name", "C\u2082-symmetric", "remove"])
    tool.ligand_table.cellClicked.connect(
        lambda row, column, t=tool:ligand_table_clicked(t, row, column)
    )
    tool.ligand_table.setEditTriggers(QTableWidget.NoEditTriggers)
    add_ligand(tool)
    tool.ligand_table.resizeColumnToContents(0)
    tool.ligand_table.resizeColumnToContents(1)
    tool.ligand_table.resizeColumnToContents(2)
    tool.ligand_table.horizontalHeader().setStretchLastSection(False)
    tool.ligand_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    tool.ligand_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
    tool.ligand_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
    ligand_layout.addRow(tool.ligand_table)

def ligand_table_clicked(tool, row, column):
    if row == tool.ligand_table.rowCount() - 1 or tool.ligand_table.rowCount() == 1:
        add_ligand(tool)
    elif column == 2:
        tool.ligand_table.removeRow(row)
    elif column == 0:
        tool.tool_window.create_child_window(
            "select ligand",
            window_class=LigandSelection,
            nameWidget=tool.ligand_table.item(row, 0),
            symmetryWidget=tool.ligand_table.cellWidget(row, 1).layout().itemAt(0).widget(),
        )
    
def open_ptable(tool):
    tool.tool_window.create_child_window(
        "select element", window_class=_PTable, button=tool.element
    )
    
def add_ligand(tool):
    rows = tool.ligand_table.rowCount()
    if rows != 0:
        rows -= 1
        ligand_name = QTableWidgetItem()
        name = "<click to choose>"
        is_c2 = Qt.Unchecked
        enabled = True
        if rows > 0:
            name = tool.ligand_table.item(rows - 1, 0).text()
            is_c2 = tool.ligand_table.cellWidget(rows - 1, 1).layout().itemAt(0).widget().checkState()
            enabled = tool.ligand_table.cellWidget(rows - 1, 1).layout().itemAt(0).widget().isEnabled()

        ligand_name.setData(Qt.DisplayRole, name)
        tool.ligand_table.setItem(rows, 0, ligand_name)
        
        widget_that_lets_me_horizontally_align_a_checkbox = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_a_checkbox)
        c2 = QCheckBox()
        c2.setEnabled(enabled)
        c2.setCheckState(is_c2)
        widget_layout.addWidget(c2, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        tool.ligand_table.setCellWidget(
            rows, 1, widget_that_lets_me_horizontally_align_a_checkbox
        )
        
        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        section_remove = QLabel()
        dim = int(1.5 * section_remove.fontMetrics().boundingRect("Q").height())
        section_remove.setPixmap(
            QIcon(section_remove.style().standardIcon(
                QStyle.SP_DialogDiscardButton)
            ).pixmap(dim, dim)
        )
        widget_layout.addWidget(section_remove, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        tool.ligand_table.setCellWidget(
            rows, 2, widget_that_lets_me_horizontally_align_an_icon
        )
        rows += 1

    tool.ligand_table.insertRow(rows)

    widget_that_lets_me_horizontally_align_an_icon = QWidget()
    widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
    ligand_add = QLabel("add ligand")
    widget_layout.addWidget(ligand_add, 0, Qt.AlignHCenter)
    widget_layout.setContentsMargins(0, 0, 0, 0)
    tool.ligand_table.setCellWidget(rows, 1, widget_that_lets_me_horizontally_align_an_icon)



class CoordinationComplexVomit(ToolInstance):
    
    help = "https://github.com/QChASM/SEQCROW/wiki/Coordination-Complex-Generator-Tool"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QFormLayout()

        create_coord_items(self, layout)
        
        do_it = QPushButton("create coordination complexes")
        do_it.clicked.connect(self.create_complexes)
        layout.addRow(do_it)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def create_complexes(self):
        c2_symmetric = []
        ligands = []
        minimize = self.minimize.checkState() == Qt.Checked
        for i in range(0, self.ligand_table.rowCount() - 1):
            ligand_name = self.ligand_table.item(i, 0).text()
            if ligand_name == "<click to choose>":
                continue
            ligands.append(ligand_name)
            
            checkbox = self.ligand_table.cellWidget(i, 1).layout().itemAt(0).widget()
            c2 = checkbox.checkState() == Qt.Checked
            c2_symmetric.append(c2)

        denticity = 0
        for lig in ligands:
            comp = Component(lig)
            denticity += len(comp.key_atoms)

        vsepr = self.vsepr.currentText()
        expected_denticity = len(Atom.get_shape(vsepr)) - 1
        if expected_denticity != denticity:
            self.session.logger.error(
                "the sum of the denticity of you ligands is %i, but " % denticity +
                "a %s coordination geometry has %i sites\n" % (vsepr, expected_denticity) +
                "add or remove ligands so that the total ligand denticity is %i, " % expected_denticity +
                "or choose a different coordination geometry"
            )
            return

        rescols, formula = ResidueCollection.get_coordination_complexes(
            self.element.text(),
            ligands,
            vsepr,
            c2_symmetric=c2_symmetric,
            minimize=minimize,
            session=self.session,
        )
        
        self.session.logger.info("generic formula is %s" % formula)
        models = [rescol.get_chimera(self.session) for rescol in rescols]

        self.session.models.add(models)
        for model in models:
            apply_seqcrow_preset(model, fallback="Ball-Stick-Endcap")


class LigandSelection(ChildToolWindow):
    def __init__(
            self,
            tool_instance,
            title,
            nameWidget=None,
            symmetryWidget=None,
            **kwargs
    ):
        super().__init__(tool_instance, title, **kwargs)
        
        self.nameWidget = nameWidget
        self.symmetryWidget = symmetryWidget
        
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout()
        
        self.lig_table = LigandTable(
            singleSelect=True, maxDenticity=2, include_substituents=True
        )
        self.lig_table.table.itemSelectionChanged.connect(self.refresh_selection)
        layout.addRow(self.lig_table)
        
        done = QPushButton("done selecting ligand")
        done.clicked.connect(self.destroy)
        layout.addRow(done)
        
        self.ui_area.setLayout(layout)
        
        self.manage(None)

    def refresh_selection(self):
        lig_names = []
        for row in self.lig_table.table.selectionModel().selectedRows():
            if self.lig_table.table.isRowHidden(row.row()):
                continue
            
            lig_names.append(row.data())
        
        if not lig_names:
            return
        
        self.nameWidget.setData(Qt.DisplayRole, ",".join(lig_names))
        comp = Component(lig_names[0])
        if len(comp.key_atoms) == 2:
            self.symmetryWidget.setEnabled(True)
            c2_symmetric = comp.c2_symmetric()
            if c2_symmetric:
                self.symmetryWidget.setCheckState(Qt.Checked)
            else:
                self.symmetryWidget.setCheckState(Qt.Unchecked)
        else:
            self.symmetryWidget.setEnabled(False)
