import re
import os

from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegularExpression
from PyQt5.QtWidgets import QWidget, QTableWidget, QGridLayout, QLineEdit, QComboBox, QLabel, QHeaderView

from AaronTools.geometry import Geometry
from AaronTools.fileIO import read_types


class LigandTable(QWidget):
    def __init__(self, parent=None, singleSelect=False, maxDenticity=None):
        super().__init__(parent)
        
        layout = QGridLayout(self)
        
        self.table = QTableWidget()
        
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['name', 'denticity', 'coordinating elements'])
        
        self.add_ligands(maxDenticity)
        
        for i in range(0, 3):
            self.table.resizeColumnToContents(i)
            
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        if singleSelect:
            self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.filterEdit = QLineEdit()
        self.filterEdit.textChanged.connect(self.apply_filter)
        self.filterEdit.setClearButtonEnabled(True)
        
        self.filter_columns = QComboBox()
        self.filter_columns.addItem("name")
        self.filter_columns.addItem("denticity")
        self.filter_columns.addItem("coordinating elements")
        self.filter_columns.currentTextChanged.connect(self.change_filter_method)

        self.name_regex_option = QComboBox()
        self.name_regex_option.addItem("case-insensitive")
        self.name_regex_option.addItem("case-sensitive")
        self.name_regex_option.currentTextChanged.connect(self.apply_filter)
        self.name_regex_option.setVisible(self.filter_columns.currentText() == "name")

        self.coordinating_elements_method = QComboBox()
        self.coordinating_elements_method.addItem("exactly")
        self.coordinating_elements_method.addItem("at least")
        self.coordinating_elements_method.currentTextChanged.connect(self.apply_filter)
        self.coordinating_elements_method.setVisible(self.filter_columns.currentText() == "coordinating elements")

        layout.addWidget(self.table, 0, 0, 1, 4)
        layout.addWidget(QLabel("filter based on"), 1, 0)
        layout.addWidget(self.filter_columns, 1, 1)
        layout.addWidget(self.coordinating_elements_method, 1, 2)
        layout.addWidget(self.name_regex_option, 1, 2)
        layout.addWidget(self.filterEdit, 1, 3)

        self.change_filter_method("name")

    def add_ligands(self, maxDenticity=None):
        from AaronTools.component import Component

        names = []
        
        for lib in [Component.AARON_LIBS, Component.BUILTIN]:
            if not os.path.exists(lib):
                continue
            for lig in os.listdir(lib):
                name, ext = os.path.splitext(lig)
                if not any(".%s" % x == ext for x in read_types):
                    continue
                
                if name in names:
                    continue
                
                names.append(name)
            
                geom = Geometry(
                    os.path.join(lib, lig),
                    refresh_connected=False,
                    refresh_ranks=False,
                )
            
                key_atoms = [geom.atoms[i] for i in geom.other["key_atoms"]]
            
                if maxDenticity and len(key_atoms) > maxDenticity:
                    continue
            
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(name))
                
                #this is an integer, so I need to initialize it then set the data
                denticity = QTableWidgetItem()
                denticity.setData(Qt.DisplayRole, len(key_atoms))
                self.table.setItem(row, 1, denticity)
                
                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        ", ".join(
                            sorted([atom.element for atom in key_atoms])
                        )
                    )
                )
    
        self.ligand_list = names

    def change_filter_method(self, text):
        if text == "coordinating elements":
            self.filterEdit.setToolTip("comma and/or space delimited elements")
            self.coordinating_elements_method.setVisible(True)
            self.name_regex_option.setVisible(False)
        elif text == "name":
            self.filterEdit.setToolTip("name regex")
            self.coordinating_elements_method.setVisible(False)
            self.name_regex_option.setVisible(True)
        elif text == "denticity":
            self.filterEdit.setToolTip("number of key atoms")
            self.coordinating_elements_method.setVisible(False)
            self.name_regex_option.setVisible(False)
            
        self.apply_filter()

    def apply_filter(self, *args):
        text = self.filterEdit.text()
        if text:
            if self.filter_columns.currentText() == "name":
                m = QRegularExpression(text)
                if m.isValid():
                    if self.name_regex_option.currentText() == "case-insensitive":
                        m.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
                        
                    m.optimize()
                    filter = lambda row_num: m.match(self.table.item(row_num, 0).text()).hasMatch()
                else:
                    return
                
            elif self.filter_columns.currentText() == "denticity":
                if text.isdigit():
                    filter = lambda row_num: int(self.table.item(row_num, 1).text()) == int(text)
                else:
                    filter = lambda row: True
            
            elif self.filter_columns.currentText() == "coordinating elements":
                method = self.coordinating_elements_method.currentText()
                def filter(row_num):
                    row_key_atoms = [item.strip() for item in self.table.item(row_num, 2).text().split(',')]
                    search_atoms = []
                    for item in text.split():
                        for ele in item.split(','):
                            if ele.strip() != "":
                                search_atoms.append(ele)
                    
                    if method == "exactly":
                        if all([row_key_atoms.count(element) == search_atoms.count(element) for element in set(search_atoms)]) and \
                            all([row_key_atoms.count(element) == search_atoms.count(element) for element in set(row_key_atoms)]):
                            return True
                        else:
                            return False                    
                    
                    elif method == "at least":
                        if all([row_key_atoms.count(element) >= search_atoms.count(element) for element in set(search_atoms)]):
                            return True
                        else:
                            return False
                        
        else:
            filter = lambda row: True
            
        for i in range(0, self.table.rowCount()):
            self.table.setRowHidden(i, not filter(i))
 

class SubstituentTable(QWidget):
    def __init__(self, parent=None, singleSelect=False):
        super().__init__(parent)
        
        layout = QGridLayout(self)
        
        self.table = QTableWidget()
        
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['name', 'conformers', 'conf. angle'])

        self.add_subs()

        for i in range(0, 3):
            self.table.resizeColumnToContents(i)
        
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        if singleSelect:
            self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.filterEdit = QLineEdit()
        self.filterEdit.textChanged.connect(self.apply_filter)
        self.filterEdit.setClearButtonEnabled(True)
        
        self.filter_columns = QComboBox()
        self.filter_columns.addItem("name")
        self.filter_columns.addItem("conformers")
        self.filter_columns.addItem("conf. angle")
        self.filter_columns.currentTextChanged.connect(self.change_filter_method)

        self.name_regex_option = QComboBox()
        self.name_regex_option.addItem("case-insensitive")
        self.name_regex_option.addItem("case-sensitive")
        self.name_regex_option.currentTextChanged.connect(self.apply_filter)
        self.name_regex_option.setVisible(self.filter_columns.currentText() == "name")

        layout.addWidget(self.table, 0, 0, 1, 4)
        layout.addWidget(QLabel("filter based on"), 1, 0)
        layout.addWidget(self.filter_columns, 1, 1)
        layout.addWidget(self.name_regex_option, 1, 2)
        layout.addWidget(self.filterEdit, 1, 3)
    
        self.change_filter_method("name")
    
    def change_filter_method(self, text):
        if text == "name":
            self.filterEdit.setToolTip("name regex")
            self.name_regex_option.setVisible(True)
        elif text == "conformers":
            self.filterEdit.setToolTip("number of conformers")
            self.name_regex_option.setVisible(False)        
        elif text == "conf. angle":
            self.filterEdit.setToolTip("angle between conformers")
            self.name_regex_option.setVisible(False)
            
        self.apply_filter()

    def apply_filter(self, *args):
        text = self.filterEdit.text()
        if text:
            if self.filter_columns.currentText() == "name":
                m = QRegularExpression(text)
                if m.isValid():
                    if self.name_regex_option.currentText() == "case-insensitive":
                        m.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
                        
                    m.optimize()
                    filter = lambda row_num: m.match(self.table.item(row_num, 0).text()).hasMatch()
                else:
                    return
 
            elif self.filter_columns.currentText() == "conformers":
                if text.isdigit():
                    filter = lambda row_num: int(self.table.item(row_num, 1).text()) == int(text)
                else:
                    filter = lambda row: True
            
            elif self.filter_columns.currentText() == "conf. angle":
                if text.isdigit():
                    filter = lambda row_num: int(self.table.item(row_num, 2).text()) == int(text)
                else:
                    filter = lambda row: True
                    
        else:
            filter = lambda row: True
            
        for i in range(0, self.table.rowCount()):
            self.table.setRowHidden(i, not filter(i))

    def add_subs(self):
        from AaronTools.substituent import Substituent
        
        names = []
        
        for lib in [Substituent.AARON_LIBS, Substituent.BUILTIN]:
            if not os.path.exists(lib):
                continue
            for ring in os.listdir(lib):
                name, ext = os.path.splitext(ring)
                if not any(".%s" % x == ext for x in read_types):
                    continue
                
                if name in names:
                    continue
                
                names.append(name)
            
                geom = Geometry(
                    os.path.join(lib, ring),
                    refresh_connected=False,
                    refresh_ranks=False,
                )
            
                conf_info = re.search(r"CF:(\d+),(\d+)", geom.comment)
            
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(name))
                
                #the next two items are integers - need to initialize then setData so they sort and display correctly
                conf_num = QTableWidgetItem()
                conf_num.setData(Qt.DisplayRole, conf_info.group(1))
                self.table.setItem(row, 1, conf_num)
                
                conf_angle = QTableWidgetItem()
                conf_angle.setData(Qt.DisplayRole, conf_info.group(2))
                self.table.setItem(row, 2, conf_angle)

        self.substituent_list = names


class RingTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QGridLayout(self)
        
        self.table = QTableWidget()
        
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(['name'])

        self.add_rings()

        for i in range(0, 1):
            self.table.resizeColumnToContents(i)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.filterEdit = QLineEdit()
        self.filterEdit.textChanged.connect(self.apply_filter)
        self.filterEdit.setClearButtonEnabled(True)

        self.filter_columns = QComboBox()
        self.filter_columns.addItem("name")
        self.filter_columns.currentTextChanged.connect(self.change_filter_method)

        self.name_regex_option = QComboBox()
        self.name_regex_option.addItem("case-insensitive")
        self.name_regex_option.addItem("case-sensitive")
        self.name_regex_option.currentTextChanged.connect(self.apply_filter)
        self.name_regex_option.setVisible(self.filter_columns.currentText() == "name")

        layout.addWidget(self.table, 0, 0, 1, 4)
        layout.addWidget(QLabel("filter based on"), 1, 0)
        layout.addWidget(self.filter_columns, 1, 1)
        layout.addWidget(self.name_regex_option, 1, 2)
        layout.addWidget(self.filterEdit, 1, 3)
    
        self.change_filter_method("name")        

    def change_filter_method(self, text):
        if text == "name":
            self.filterEdit.setToolTip("name regex")
            self.name_regex_option.setVisible(True)
            
        self.apply_filter()

    def apply_filter(self, *args):
        text = self.filterEdit.text()
        if text:
            if self.filter_columns.currentText() == "name":
                m = QRegularExpression(text)
                if m.isValid():
                    if self.name_regex_option.currentText() == "case-insensitive":
                        m.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
                        
                    m.optimize()
                    filter = lambda row_num: m.match(self.table.item(row_num, 0).text()).hasMatch()
                else:
                    return
                     
        else:
            filter = lambda row: True
            
        for i in range(0, self.table.rowCount()):
            self.table.setRowHidden(i, not filter(i))

    def add_rings(self):
        from AaronTools.ring import Ring
        
        names = []
        for lib in [Ring.AARON_LIBS, Ring.BUILTIN]:
            if not os.path.exists(lib):
                continue
            for ring in os.listdir(lib):
                name, ext = os.path.splitext(ring)
                if not any(".%s" % x == ext for x in read_types):
                    continue
                
                if name in names:
                    continue
                
                names.append(name)

                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(name))
                
        self.ring_list = names
