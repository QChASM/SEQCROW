from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegularExpression
from PyQt5.QtWidgets import QWidget, QTableWidget, QGridLayout, QLineEdit, QComboBox, QLabel

from glob import glob


class _PseudoGeometry:
    """it would take a long ling to create the library dialogs if we actually had to read
    the entire file for all of the ligands, figure out their key atoms, then read all of the substituents,
    figure out their conformer info, then read all of the ring fragments...
    PseudoGeometry speeds up this process by only reading the relevant info from the file and 
    storing the method we should use to create the AaronTools Geometry (i.e. Component, Substituent, Ring)"""
    def __init__(self, filename, method):
        """filename - path to file containing a structure
        method - Substituent, Component, or Ring classes from AaronTools"""
        import os
        import re

        from linecache import getline, clearcache
        from AaronTools.substituent import Substituent
        from AaronTools.ring import Ring
        from AaronTools.component import Component
        
        self.name = os.path.split(filename)[-1].replace('.xyz', '')
        self.filename = filename
        self.method = method
        
        #TODO: use AaronTools to parse comment lines
        
        if method == Component:
            self.key_atoms = []
            self.key_elements = []
            line1 = getline(filename, 2)
            #figure out which atoms are key atoms
            key_info = re.search("K:([0-9,;]+)", line1)
            if key_info is not None:
                key_info = key_info.group(1).split(';')
                for m in key_info:
                    if m == "":
                        continue
                    
                    m = m.split(',')
                    for i in m:
                        if i == "":
                            continue
                        self.key_atoms.append(int(i.strip(';')))   
                
            #read only the lines with key atoms and grab the element of each key atom
            for atom in self.key_atoms:
                atom_info = getline(filename, atom+2)
                self.key_elements.append(atom_info.split()[0])
                
            clearcache()
                
        if method == Substituent:
            line1 = getline(filename, 2)
            #read conformer info
            conf_info = re.search("CF:(\d+),(\d+)", line1)
            if conf_info is not None:
                self.conf_num = int(conf_info.group(1))
                self.conf_angle = int(conf_info.group(2))
            else:
                self.conf_num = -1
                self.conf_angle = -1
            
            clearcache()


class LigandTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QGridLayout(self)
        
        self.table = QTableWidget()
        
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['name', 'denticity', 'coordinating elements'])
        
        self.add_ligands()
        
        for i in range(0, 3):
            self.table.resizeColumnToContents(i)
        
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
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

    def add_ligands(self):
        from AaronTools.component import Component

        lig_list = [_PseudoGeometry(lig, Component) for lig in glob(Component.AARON_LIBS) + glob(Component.BUILTIN)]
        
        for lig in lig_list:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(lig.name))
            
            #this is an integer, so I need to initialize it then set the data
            denticity = QTableWidgetItem()
            denticity.setData(Qt.DisplayRole, len(lig.key_elements))
            self.table.setItem(row, 1, denticity)
            
            self.table.setItem(row, 2, QTableWidgetItem(", ".join(sorted(lig.key_elements))))
    
        self.ligand_list = lig_list

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
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QGridLayout(self)
        
        self.table = QTableWidget()
        
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['name', 'conformers', 'conf. angle'])

        self.add_subs()

        for i in range(0, 3):
            self.table.resizeColumnToContents(i)
        
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
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

        sub_list = [_PseudoGeometry(sub, Substituent) for sub in glob(Substituent.AARON_LIBS) + glob(Substituent.BUILTIN)]
        
        for sub in sub_list:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(sub.name))
            
            #the next two items are integers - need to initialize then setData so they sort and display correctly
            conf_num = QTableWidgetItem()
            conf_num.setData(Qt.DisplayRole, sub.conf_num)
            self.table.setItem(row, 1, conf_num)
            
            conf_angle = QTableWidgetItem()
            conf_angle.setData(Qt.DisplayRole, sub.conf_angle)
            self.table.setItem(row, 2, conf_angle)

        self.substituent_list = sub_list


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
        
        rings = [_PseudoGeometry(ring, Ring) for ring in glob(Ring.AARON_LIBS) + glob(Ring.BUILTIN)]
        
        for ring in rings:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(ring.name))
            
        self.ring_list = rings
        