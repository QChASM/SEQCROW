from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import QtWidgets
from glob import glob

class _PseudoGeometry:
    """it would take a long ling to create the library dialogs if we actually had to read
    the entire file for all of the ligands, figure out their key atoms, then read all of the substituents,
    figure out their conformer info, then read all of the ring fragments...
    PseudoGeometry speeds up this process by only reading the relevant info from the file and 
    storing the method we should use to create the AaronTools Geometry (i.e. Component, Substituent, RingFragment)"""
    def __init__(self, filename, method):
        """filename - path to file containing a structure
        method - Substituent, Component, or RingFragment classes from AaronTools"""
        import os
        import re

        from linecache import getline, clearcache
        from AaronTools.substituent import Substituent
        from AaronTools.ringfragment import RingFragment
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

class LigandTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(['name', 'denticity', 'coordinating elements'])
        
        self.add_ligands()
        
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

    def add_ligands(self):
        from AaronTools.component import Component

        lig_list = [_PseudoGeometry(lig, Component) for lig in glob(Component.AARON_LIBS) + glob(Component.BUILTIN)]
        
        for lig in lig_list:
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(lig.name))
            self.setItem(row, 1, QTableWidgetItem(str(len(lig.key_elements))))
            self.setItem(row, 2, QTableWidgetItem(", ".join(sorted(lig.key_elements))))
    
        self.ligand_list = lig_list
 
 
class SubstituentTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(['name', 'conformers', 'conf. angle'])
        
        self.add_subs()
        
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        
    def add_subs(self):
        from AaronTools.substituent import Substituent

        sub_list = [_PseudoGeometry(sub, Substituent) for sub in glob(Substituent.AARON_LIBS) + glob(Substituent.BUILTIN)]
        
        for sub in sub_list:
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(sub.name))
            self.setItem(row, 1, QTableWidgetItem(str(sub.conf_num)))
            self.setItem(row, 2, QTableWidgetItem(str(sub.conf_angle)))

        self.substituent_list = sub_list


class RingTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(['name'])
        
        self.add_rings()
        
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        
    def add_rings(self):
        from AaronTools.ringfragment import RingFragment
        
        rings = [_PseudoGeometry(ring, RingFragment) for ring in glob(RingFragment.AARON_LIBS) + glob(RingFragment.BUILTIN)]
        
        for ring in rings:
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(ring.name))
            
        self.ring_list = rings
        