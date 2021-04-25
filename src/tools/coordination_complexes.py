from chimerax.atomic.colors import element_color
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.settings import Settings

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

from AaronTools.const import ELEMENTS
from AaronTools.geometry import Geometry

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.libraries import LigandTable
from SEQCROW.widgets import PeriodicTable
from SEQCROW.managers.filereader_manager import apply_seqcrow_preset
from SEQCROW.tools.structure_editing import _PTable

class CoordinationComplexVomit(ToolInstance):
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QFormLayout()

        self.element = QPushButton("Ca")
        self.element.setMinimumWidth(int(1.3*self.element.fontMetrics().boundingRect("QQ").width()))
        self.element.setMaximumWidth(int(1.3*self.element.fontMetrics().boundingRect("QQ").width()))
        self.element.setMinimumHeight(int(1.5*self.element.fontMetrics().boundingRect("QQ").height()))
        self.element.setMaximumHeight(int(1.5*self.element.fontMetrics().boundingRect("QQ").height()))
        ele_color = tuple(list(element_color(ELEMENTS.index("Ca")))[:-1])
        self.element.setStyleSheet(
            "QPushButton { background: rgb(%i, %i, %i); color: %s; font-weight: bold; }" % (
                *ele_color,
                'white' if sum(
                    int(x < 130) - int(x > 225) for x in ele_color
                ) - int(ele_color[1] > 225) +
                int(ele_color[2] > 200) >= 2 else 'black'
            )
        )
        self.element.clicked.connect(self.open_ptable)
        layout.addRow("element:", self.element)

        self.vsepr = QComboBox()
        self.vsepr.addItems([
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
        
        self.vsepr.setCurrentIndex(7)
        
        self.vsepr.insertSeparator(12)
        self.vsepr.insertSeparator(8)
        self.vsepr.insertSeparator(5)
        layout.addRow("geometry:", self.vsepr)
        
        ligand_box = QGroupBox("ligands")
        ligand_layout = QFormLayout(ligand_box)
        layout.addRow(ligand_box)
        
        self.ligand_table = QTableWidget()
        self.ligand_table.setColumnCount(3)
        self.ligand_table.setHorizontalHeaderLabels(["name", "C\u2082-symmetric", "remove"])
        self.ligand_table.cellClicked.connect(self.ligand_table_clicked)
        self.ligand_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.add_ligand()
        self.ligand_table.resizeColumnToContents(0)
        self.ligand_table.resizeColumnToContents(1)
        self.ligand_table.resizeColumnToContents(2)
        self.ligand_table.horizontalHeader().setStretchLastSection(False)
        self.ligand_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ligand_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.ligand_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        ligand_layout.addRow(self.ligand_table)
        
        do_it = QPushButton("create coordination complexes")
        do_it.clicked.connect(self.create_complexes)
        layout.addRow(do_it)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
    
    def open_ptable(self):
        self.tool_window.create_child_window("select element", window_class=_PTable, button=self.element)
    
    def ligand_table_clicked(self, row, column):
        if row == self.ligand_table.rowCount() - 1 or self.ligand_table.rowCount() == 1:
            self.add_ligand()
        elif column == 2:
            self.ligand_table.removeRow(row)
        elif column == 0:
            self.tool_window.create_child_window(
                "select ligand",
                window_class=LigandSelection,
                tableWidget=self.ligand_table.item(row, column),
            )
    
    def add_ligand(self):
        rows = self.ligand_table.rowCount()
        if rows != 0:
            rows -= 1
            ligand_name = QTableWidgetItem()
            name = "<click to choose>"
            is_c2 = Qt.Unchecked
            if rows > 0:
                name = self.ligand_table.item(rows - 1, 0).text()
                is_c2 = self.ligand_table.cellWidget(rows - 1, 1).layout().itemAt(0).widget().checkState()

            ligand_name.setData(Qt.DisplayRole, name)
            self.ligand_table.setItem(rows, 0, ligand_name)
            
            widget_that_lets_me_horizontally_align_a_checkbox = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_a_checkbox)
            c2 = QCheckBox()
            c2.setCheckState(is_c2)
            widget_layout.addWidget(c2, 0, Qt.AlignHCenter)
            widget_layout.setContentsMargins(0, 0, 0, 0)
            self.ligand_table.setCellWidget(rows, 1, widget_that_lets_me_horizontally_align_a_checkbox)
            
            widget_that_lets_me_horizontally_align_an_icon = QWidget()
            widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
            section_remove = QLabel()
            dim = int(1.5 * section_remove.fontMetrics().boundingRect("Q").height())
            section_remove.setPixmap(QIcon(section_remove.style().standardIcon(QStyle.SP_DialogDiscardButton)).pixmap(dim, dim))
            widget_layout.addWidget(section_remove, 0, Qt.AlignHCenter)
            widget_layout.setContentsMargins(0, 0, 0, 0)
            self.ligand_table.setCellWidget(rows, 2, widget_that_lets_me_horizontally_align_an_icon)
            rows += 1

        self.ligand_table.insertRow(rows)

        widget_that_lets_me_horizontally_align_an_icon = QWidget()
        widget_layout = QHBoxLayout(widget_that_lets_me_horizontally_align_an_icon)
        ligand_add = QLabel("add ligand")
        widget_layout.addWidget(ligand_add, 0, Qt.AlignHCenter)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        self.ligand_table.setCellWidget(rows, 1, widget_that_lets_me_horizontally_align_an_icon)

    def create_complexes(self):
        c2_symmetric = []
        ligands = []
        for i in range(0, self.ligand_table.rowCount() - 1):
            ligand_name = self.ligand_table.item(i, 0).text()
            ligands.append(ligand_name)
            
            checkbox = self.ligand_table.cellWidget(i, 1).layout().itemAt(0).widget()
            c2 = checkbox.checkState() == Qt.Checked
            c2_symmetric.append(c2)
        
        rescols, formula = ResidueCollection.get_coordination_complexes(
            self.element.text(),
            ligands,
            self.vsepr.currentText(),
            c2_symmetric=c2_symmetric,
            minimize=True,
            session=self.session,
        )
        
        self.session.logger.info("generic formula is %s" % formula)
        models = [rescol.get_chimera(self.session) for rescol in rescols]

        self.session.models.add(models)
        for model in models:
            apply_seqcrow_preset(model, fallback="Ball-Stick-Endcap")


class LigandSelection(ChildToolWindow):
    def __init__(self, tool_instance, title, tableWidget=None, **kwargs):
        super().__init__(tool_instance, title, **kwargs)
        
        self.tableWidget = tableWidget
        
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout()
        
        self.lig_table = LigandTable(singleSelect=True, maxDenticity=2)
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
            
        self.tableWidget.setData(Qt.DisplayRole, ",".join(lig_names))
