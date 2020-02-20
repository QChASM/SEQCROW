import numpy as np

from AaronTools.substituent import Substituent
from AaronTools.component import Component
from AaronTools.catalyst import Catalyst
from AaronTools.ring import Ring

from chimerax.atomic import selected_atoms, selected_residues
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow

from io import BytesIO

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QTabWidget, QComboBox, QTableWidget, QTableView, QWidget, QVBoxLayout, QTableWidgetItem, QFormLayout, QCheckBox

from ChimAARON.residue_collection import ResidueCollection
from ChimAARON.libraries import SubstituentTable, LigandTable, RingTable

class EditStructure(ToolInstance):
    #XML_TAG ChimeraX :: Tool :: Structure Modification :: AaronTools :: Modify substituents, swap ligands, and close rings, all for the one-time fee of an arm and a leg!
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    display_name = "The Alchemist"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)        

        self.close_previous_bool = True

        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()
        
        self.alchemy_tabs = QTabWidget()
        
        #substitute
        self.substitute_tab = QWidget()
        self.substitute_layout = QGridLayout(self.substitute_tab) 
                
        sublabel = QLabel("substituent name:")
        self.substitute_layout.addWidget(sublabel, 0, 0)
        
        self.subname = QLineEdit()
        self.subname.setToolTip("name of substituent in AaronTools library")
        self.substitute_layout.addWidget(self.subname, 0, 1)
        
        open_sub_lib = QPushButton("from library...")
        open_sub_lib.clicked.connect(self.open_sub_selector)
        self.substitute_layout.addWidget(open_sub_lib, 0, 2)        
        
        self.close_previous_sub = QCheckBox("modify selected structure")
        self.close_previous_sub.setToolTip("checked: selected structure will be modified\nunchecked: new model will be created for the modified structure")
        self.close_previous_sub.toggle()
        self.close_previous_sub.stateChanged.connect(self.close_previous_change)
        self.substitute_layout.addWidget(self.close_previous_sub, 1, 0, 1, 3)
        
        substitute_button = QPushButton("substitute current selection")
        substitute_button.clicked.connect(self.do_substitute)
        self.substitute_layout.addWidget(substitute_button, 2, 0, 1, 3)
        
        #map ligand
        self.maplig_tab = QWidget()
        self.maplig_layout = QGridLayout(self.maplig_tab)
        
        liglabel = QLabel("ligand name:")
        self.maplig_layout.addWidget(liglabel, 0, 0)
        
        self.ligname = QLineEdit()
        self.ligname.setToolTip("name of ligand in AaronTools library")
        self.maplig_layout.addWidget(self.ligname, 0, 1)
        
        open_lig_lib = QPushButton("from library...")
        open_lig_lib.clicked.connect(self.open_lig_selector)
        self.maplig_layout.addWidget(open_lig_lib, 0, 2)        
        
        self.close_previous_lig = QCheckBox("modify selected structure")
        self.close_previous_lig.setToolTip("checked: selected structure will be modified\nunchecked: new model will be created for the modified structure")
        self.close_previous_lig.toggle()
        self.close_previous_lig.stateChanged.connect(self.close_previous_change)
        self.maplig_layout.addWidget(self.close_previous_lig, 1, 0, 1, 3)
        
        maplig_button = QPushButton("swap ligand of current selection")
        maplig_button.clicked.connect(self.do_maplig)
        self.maplig_layout.addWidget(maplig_button, 2, 0, 1, 3)
        
        #close ring
        self.closering_tab = QWidget()
        self.closering_layout = QGridLayout(self.closering_tab)
        
        ringlabel = QLabel("ring name:")
        self.closering_layout.addWidget(ringlabel, 0, 0)
        
        self.ringname = QLineEdit()
        self.ringname.setToolTip("name of ring in AaronTools library")
        self.closering_layout.addWidget(self.ringname, 0, 1)
        
        open_ring_lib = QPushButton("from library...")
        open_ring_lib.clicked.connect(self.open_ring_selector)
        self.closering_layout.addWidget(open_ring_lib, 0, 2)        
        
        self.close_previous_ring = QCheckBox("modify selected structure")
        self.close_previous_ring.setToolTip("checked: selected structure will be modified\nunchecked: new model will be created for the modified structure")
        self.close_previous_ring.toggle()
        self.close_previous_ring.stateChanged.connect(self.close_previous_change)
        self.closering_layout.addWidget(self.close_previous_ring, 1, 0, 1, 3)
        
        closering_button = QPushButton("put a ring on current selection")
        closering_button.clicked.connect(self.do_closering)
        self.closering_layout.addWidget(closering_button, 2, 0, 1, 3)
        
        self.alchemy_tabs.addTab(self.substitute_tab, "substitute")
        self.alchemy_tabs.addTab(self.maplig_tab, "swap ligand")
        self.alchemy_tabs.addTab(self.closering_tab, "close ring")

        layout.addWidget(self.alchemy_tabs)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage('side')
    
    def close_previous_change(self, state):
        if state == Qt.Checked:
            for checkbox in [self.close_previous_lig, self.close_previous_sub, self.close_previous_ring]:
                checkbox.setChecked(True)
            self.close_previous_bool = True
        else:
            for checkbox in [self.close_previous_lig, self.close_previous_sub, self.close_previous_ring]:
                checkbox.setChecked(False)
            self.close_previous_bool = False
    
    def do_substitute(self):
        subnames = self.subname.text()
        selection = selected_atoms(self.session)
        
        if len(selection) < 1:
            raise RuntimeWarning("nothing selected")
        
        models = {}
        for atom in selection:
            if atom.structure not in models:
                models[atom.structure] = [str(atom.atomspec)]
            else:
                models[atom.structure].append(str(atom.atomspec))
                
        first_pass = True
        new_structures = []
        for subname in subnames.split(','):
            subname = subname.strip()
            sub = Substituent(subname)
            for model in models:
                if self.close_previous_bool and first_pass:
                    rescol = ResidueCollection(model)
                    for target in models[model]:
                        rescol.substitute(sub.copy(), target)
                    
                    rescol.update_chix(model)
                    
                elif self.close_previous_bool and not first_pass:
                    raise RuntimeError("only the first model can be replaced")
                else:
                    model_copy = model.copy()
                    rescol = ResidueCollection(model_copy)
                    for i, atom in enumerate(model.atoms):
                        rescol.atoms[i].atomspec = atom.atomspec
                        rescol.atoms[i].add_tag(atom.atomspec)
                        
                    for target in models[model]:
                        rescol.substitute(sub.copy(), target)
                                
                    struc = rescol.get_chimera(self.session)
                    new_structures.append(struc)
            
            first_pass = False
        
        if not self.close_previous_bool:
            self.session.models.add(new_structures)
        
    def open_sub_selector(self):
        self.tool_window.create_child_window("select substituents", window_class=SubstituentSelection, textBox=self.subname)

    def do_maplig(self):
        lignames = self.ligname.text()
        selection = self.session.chimaaron_ordered_selection_manager.selection
        
        if len(selection) < 1:
            raise RuntimeWarning("nothing selected")
        
        models = {}
        for atom in selection:
            if atom.structure not in models:
                models[atom.structure] = [str(atom.atomspec)]
            else:
                models[atom.structure].append(str(atom.atomspec))        
        
        first_pass = True
        new_structures = []
        for ligname in lignames.split(','):
            ligname = ligname.strip()
            lig = Component(ligname)
            for model in models:
                if self.close_previous_bool and first_pass:
                    rescol = ResidueCollection(model)
                elif self.close_previous_bool and not first_pass:
                    raise RuntimeError("only the first model can be replaced")
                else:
                    model_copy = model.copy()
                    rescol = ResidueCollection(model_copy)
                    for i, atom in enumerate(model.atoms):
                        rescol.atoms[i].atomspec = atom.atomspec
                        rescol.atoms[i].add_tag(atom.atomspec)
                        rescol.atoms[i].chix_atom = atom
                        
                try:
                    cat = Catalyst(structure=rescol)                   
                except IOError:
                    cat = Catalyst(structure=rescol, comment=model.comment)                     
                except KeyError:
                    cat = Catalyst(structure=rescol, comment=model.comment) 
                
                target = cat.find(models[model])
                if len(target) % len(lig.key_atoms) == 0:
                    k = 0
                    ligands = []
                    while k != len(target):
                        res_lig = ResidueCollection(lig.copy(), comment=lig.comment)
                        res_lig.parse_comment()
                        res_lig = Component(res_lig, key_atoms = ",".join([str(k + 1) for k in res_lig.other["key_atoms"]]))
                        ligands.append(res_lig)
                        k += len(lig.key_atoms)
                else:
                    raise RuntimeError("number of key atoms no not match: %i now, new ligand has %i" % (len(target), len(lig.key_atoms)))
                
                cat.map_ligand(ligands, target)
                
                if self.close_previous_bool:    
                    new_rescol = ResidueCollection(cat)
                    new_rescol.update_chix(model)
                else:
                    new_rescol = ResidueCollection(cat)
                                
                    struc = new_rescol.get_chimera(self.session)
                    new_structures.append(struc)
            
            first_pass = False
        
        if not self.close_previous_bool:
            self.session.models.add(new_structures)
                    
    def open_lig_selector(self):
        self.tool_window.create_child_window("select ligands", window_class=LigandSelection, textBox=self.ligname)
    
    def do_closering(self):
        ringnames = self.ringname.text()
        selection = self.session.chimaaron_ordered_selection_manager.selection
        
        if len(selection) < 2:
            raise RuntimeWarning("two atoms must be selected per molecule")
        
        models = {}
        for atom in selection:
            if atom.structure not in models:
                models[atom.structure] = [atom.atomspec]
            else:
                models[atom.structure].append(atom.atomspec)
        
            if len(models[atom.structure]) > 2:
                raise RuntimeError("only two atoms can be selected on any model")
        
        first_pass = True
        new_structures = []
        for ringname in ringnames.split(','):
            ringname = ringname.strip()
            
            for model in models:
                if self.close_previous_bool and first_pass:
                    rescol = ResidueCollection(model)
                elif self.close_previous_bool and not first_pass:
                    raise RuntimeError("only the first model can be replaced")
                else:
                    model_copy = model.copy()
                    rescol = ResidueCollection(model_copy)
                    for i, atom in enumerate(model.atoms):
                        rescol.atoms[i].atomspec = atom.atomspec
                        rescol.atoms[i].add_tag(atom.atomspec)
                
                target = rescol.find(models[model])
                                
                rescol.ring_substitute(target, ringname)
                
                if self.close_previous_bool:                    
                    rescol.update_chix(model)
                else:
                    struc = rescol.get_chimera(self.session)
                    new_structures.append(struc)
            
            first_pass = False
        
        if not self.close_previous_bool:
            self.session.models.add(new_structures)
                    
    def open_ring_selector(self):
        self.tool_window.create_child_window("select rings", window_class=RingSelection, textBox=self.ringname)
    
    
class SubstituentSelection(ChildToolWindow):
    def __init__(self, tool_instance, title, textBox=None, **kwargs):
        super().__init__(tool_instance, title, **kwargs)
        
        self.textBox = textBox
        
        self._build_ui()
        
    def _build_ui(self):
        layout = QGridLayout()
        
        self.sub_table = SubstituentTable()
        self.sub_table.itemSelectionChanged.connect(self.refresh_selection)
        layout.addWidget(self.sub_table)
        
        self.ui_area.setLayout(layout)
        
        self.manage(None)
        
    def refresh_selection(self):
        sub_names = []
        for row in self.sub_table.selectionModel().selectedRows():
            sub_names.append(row.data())
            
        self.textBox.setText(",".join(sub_names))  

        
class LigandSelection(ChildToolWindow):
    def __init__(self, tool_instance, title, textBox=None, **kwargs):
        super().__init__(tool_instance, title, **kwargs)
        
        self.textBox = textBox
        
        self._build_ui()
        
    def _build_ui(self):
        layout = QGridLayout()
        
        self.lig_table = LigandTable()
        self.lig_table.itemSelectionChanged.connect(self.refresh_selection)
        layout.addWidget(self.lig_table)
        
        self.ui_area.setLayout(layout)
        
        self.manage(None)
        
    def refresh_selection(self):
        lig_names = []
        for row in self.lig_table.table.selectionModel().selectedRows():
            if self.lig_table.table.isRowHidden(row.row()):
                continue
            
            lig_names.append(row.data())
            
        self.textBox.setText(",".join(lig_names))   

        
class RingSelection(ChildToolWindow):
    def __init__(self, tool_instance, title, textBox=None, **kwargs):
        super().__init__(tool_instance, title, **kwargs)
        
        self.textBox = textBox
        
        self._build_ui()
        
    def _build_ui(self):
        layout = QGridLayout()
        
        self.ring_table = RingTable()
        self.ring_table.itemSelectionChanged.connect(self.refresh_selection)
        layout.addWidget(self.ring_table)
        
        self.ui_area.setLayout(layout)
        
        self.manage(None)
        
    def refresh_selection(self):
        ring_names = []
        for row in self.ring_table.selectionModel().selectedRows():
            ring_names.append(row.data())
            
        self.textBox.setText(",".join(ring_names))
        