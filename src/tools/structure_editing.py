import numpy as np

from AaronTools.substituent import Substituent
from AaronTools.component import Component
from AaronTools.catalyst import Catalyst
from AaronTools.ring import Ring

from chimerax.atomic import selected_atoms, selected_residues
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import BoolArg

from io import BytesIO

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QTabWidget, QComboBox, \
                            QTableWidget, QTableView, QWidget, QVBoxLayout, QTableWidgetItem, \
                            QFormLayout, QCheckBox, QCompleter

from SEQCROW.residue_collection import ResidueCollection, Residue
from SEQCROW.libraries import SubstituentTable, LigandTable, RingTable

def minimal_ring_convert(atomic_structure, atom1, atom2):
    residues = [atom1.residue]
    if atom2.residue not in residues:
        residues.append(atom2.residue)
        
    max_iter = len(atomic_structure.atoms)
    start = atom1
    i = 0
    while start != atom2:
        if start.residue not in residues:
            residues.append(residue)
            
        i += 1
        if i > max_iter:
            return atomic_structure.residues
            
        v1 = atom2.coord - start.coord
        max_overlap = None
        for atom in start.neighbors:
            v2 = atom.coord - start.coord
            overlap = np.dot(v1, v2)
            if max_overlap is None or overlap > max_overlap:
                new_start = atom
                max_overlap = overlap
                
        start = new_start
        
    return residues


class _EditStructureSettings(Settings):
    AUTO_SAVE = {'modify': Value(True, BoolArg), 
                 'guess': Value(True, BoolArg),
                }


class EditStructure(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    help = "https://github.com/QChASM/SEQCROW/wiki/Structure-Modification-Tool"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.settings = _EditStructureSettings(session, name)
        
        self.tool_window = MainToolWindow(self)        

        self.close_previous_bool = self.settings.modify

        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()
        
        self.alchemy_tabs = QTabWidget()
        
        #substitute
        self.substitute_tab = QWidget()
        self.substitute_layout = QGridLayout(self.substitute_tab) 

        sublabel = QLabel("substituent name:")
        self.substitute_layout.addWidget(sublabel, 0, 0, Qt.AlignVCenter)
        
        self.subname = QLineEdit()
        sub_completer = NameCompleter(Substituent.list(), self.subname)
        self.subname.setCompleter(sub_completer)
        self.subname.setToolTip("name of substituent in the AaronTools library or your personal library\nseparate names with commas and uncheck 'modify selected structure' to create several structures")
        self.substitute_layout.addWidget(self.subname, 0, 1, Qt.AlignVCenter)
        
        open_sub_lib = QPushButton("from library...")
        open_sub_lib.clicked.connect(self.open_sub_selector)
        self.substitute_layout.addWidget(open_sub_lib, 0, 2, Qt.AlignTop)        
        
        self.substitute_layout.addWidget(QLabel("modify selected structure:"), 1, 0, 1, 1, Qt.AlignTop)
        
        self.close_previous_sub = QCheckBox()
        self.close_previous_sub.setToolTip("checked: selected structure will be modified\nunchecked: new model will be created for the modified structure")
        self.close_previous_sub.setChecked(self.settings.modify)
        self.close_previous_sub.stateChanged.connect(self.close_previous_change)
        self.substitute_layout.addWidget(self.close_previous_sub, 1, 1, 1, 2, Qt.AlignTop)    
        
        self.substitute_layout.addWidget(QLabel("guess previous substituent:"), 2, 0, 1, 1, Qt.AlignTop)
        
        self.guess_old = QCheckBox()
        self.guess_old.setToolTip("checked: AaronTools will use the shortest connected fragment in the residue\nunchecked: previous substituent must be selected")
        self.guess_old.setChecked(self.settings.guess)
        self.guess_old.stateChanged.connect(lambda state, settings=self.settings: settings.__setattr__("guess", True if state == Qt.Checked else False))
        self.substitute_layout.addWidget(self.guess_old, 2, 1, 1, 2, Qt.AlignTop)
        
        self.substitute_layout.addWidget(QLabel("new residue name:"), 3, 0, 1, 1, Qt.AlignTop)
        
        self.new_sub_name = QLineEdit()
        self.new_sub_name.setToolTip("change name of modified residues")
        self.new_sub_name.setPlaceholderText("leave blank to keep current")
        self.substitute_layout.addWidget(self.new_sub_name, 3, 1, 1, 2, Qt.AlignTop)
        
        substitute_button = QPushButton("substitute current selection")
        substitute_button.clicked.connect(self.do_substitute)
        self.substitute_layout.addWidget(substitute_button, 4, 0, 1, 3, Qt.AlignTop)
        
        self.substitute_layout.setRowStretch(0, 0)
        self.substitute_layout.setRowStretch(1, 0)
        self.substitute_layout.setRowStretch(2, 0)
        self.substitute_layout.setRowStretch(3, 0)
        self.substitute_layout.setRowStretch(4, 1)
        
        
        #map ligand
        self.maplig_tab = QWidget()
        self.maplig_layout = QGridLayout(self.maplig_tab)
        
        liglabel = QLabel("ligand name:")
        self.maplig_layout.addWidget(liglabel, 0, 0, Qt.AlignVCenter)
        
        self.ligname = QLineEdit()
        lig_completer = NameCompleter(Component.list(), self.ligname)
        self.ligname.setCompleter(lig_completer)
        self.ligname.setToolTip("name of ligand in the AaronTools library or your personal library\nseparate names with commas and uncheck 'modify selected structure' to create several structures")
        self.maplig_layout.addWidget(self.ligname, 0, 1, Qt.AlignVCenter)
        
        open_lig_lib = QPushButton("from library...")
        open_lig_lib.clicked.connect(self.open_lig_selector)
        self.maplig_layout.addWidget(open_lig_lib, 0, 2, Qt.AlignTop)        
        
        self.maplig_layout.addWidget(QLabel("modify selected structure:"), 1, 0, 1, 1, Qt.AlignTop)
        
        self.close_previous_lig = QCheckBox()
        self.close_previous_lig.setToolTip("checked: selected structure will be modified\nunchecked: new model will be created for the modified structure")
        self.close_previous_lig.setChecked(self.settings.modify)
        self.close_previous_lig.stateChanged.connect(self.close_previous_change)
        self.maplig_layout.addWidget(self.close_previous_lig, 1, 1, 1, 2, Qt.AlignTop)

        maplig_button = QPushButton("swap ligand of current selection")
        maplig_button.clicked.connect(self.do_maplig)
        self.maplig_layout.addWidget(maplig_button, 2, 0, 1, 3, Qt.AlignTop)
        
        self.maplig_layout.setRowStretch(0, 0)
        self.maplig_layout.setRowStretch(1, 0)
        self.maplig_layout.setRowStretch(2, 1)
        
        
        #close ring
        self.closering_tab = QWidget()
        self.closering_layout = QGridLayout(self.closering_tab)
        
        ringlabel = QLabel("ring name:")
        self.closering_layout.addWidget(ringlabel, 0, 0, Qt.AlignVCenter)
        
        self.ringname = QLineEdit()
        ring_completer = NameCompleter(Ring.list(), self.ringname)
        self.ringname.setCompleter(ring_completer)
        self.ringname.setToolTip("name of ring in the AaronTools library or your personal library\nseparate names with commas and uncheck 'modify selected structure' to create several structures")
        self.closering_layout.addWidget(self.ringname, 0, 1, Qt.AlignVCenter)
        
        open_ring_lib = QPushButton("from library...")
        open_ring_lib.clicked.connect(self.open_ring_selector)
        self.closering_layout.addWidget(open_ring_lib, 0, 2, Qt.AlignTop)        
        
        self.closering_layout.addWidget(QLabel("modify selected structure:"), 1, 0, 1, 1, Qt.AlignTop) 
        
        self.close_previous_ring = QCheckBox()
        self.close_previous_ring.setToolTip("checked: selected structure will be modified\nunchecked: new model will be created for the modified structure")
        self.close_previous_ring.setChecked(self.settings.modify)
        self.close_previous_ring.stateChanged.connect(self.close_previous_change)
        self.closering_layout.addWidget(self.close_previous_ring, 1, 1, 1, 2, Qt.AlignTop)

        self.closering_layout.addWidget(QLabel("new residue name:"), 2, 0, 1, 1, Qt.AlignTop)
        
        self.new_ring_name = QLineEdit()
        self.new_ring_name.setToolTip("change name of modified residues")
        self.new_ring_name.setPlaceholderText("leave blank to keep current")
        self.closering_layout.addWidget(self.new_ring_name, 2, 1, 1, 2, Qt.AlignTop)

        closering_button = QPushButton("put a ring on current selection")
        closering_button.clicked.connect(self.do_closering)
        self.closering_layout.addWidget(closering_button, 3, 0, 1, 3, Qt.AlignTop)

        self.closering_layout.setRowStretch(0, 0)
        self.closering_layout.setRowStretch(1, 0)
        self.closering_layout.setRowStretch(2, 0)
        self.closering_layout.setRowStretch(3, 1)


        self.alchemy_tabs.addTab(self.substitute_tab, "substitute")
        self.alchemy_tabs.addTab(self.maplig_tab, "swap ligand")
        self.alchemy_tabs.addTab(self.closering_tab, "close ring")

        layout.addWidget(self.alchemy_tabs)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage('side')
    
    def close_previous_change(self, state):
        if state == Qt.Checked:
            self.settings.modify = True
            for checkbox in [self.close_previous_lig, self.close_previous_sub, self.close_previous_ring]:
                checkbox.setChecked(True)
            self.close_previous_bool = True
        else:
            self.settings.modify = False
            for checkbox in [self.close_previous_lig, self.close_previous_sub, self.close_previous_ring]:
                checkbox.setChecked(False)
            self.close_previous_bool = False
    
    def do_substitute(self):
        subnames = self.subname.text()
        selection = selected_atoms(self.session)
        
        new_name = self.new_sub_name.text()
        if len(new_name.strip()) == 0:
            new_name = None
        elif any(len(name.strip()) > 4 for name in new_name.split(',')):
            raise RuntimeError("residue names must be 4 characters or less")
        elif any(x in new_name for x in "!@#$%^&*()\\/.<><;':\"[]{}|-=_+"):
            raise RuntimeError("invalid residue name: %s" % new_name)
        elif len(subnames.split(',')) != len(new_name.split(',')):
            raise RuntimeError("number of substituents is not the same as the number of new names")
        else:
            new_name = [x.strip() for x in new_name.split(',')]
        
        if len(selection) < 1:
            raise RuntimeWarning("nothing selected")
        
        use_attached = not self.guess_old.isChecked()
        
        models = {}
        attached = {}
        for atom in selection:
            if use_attached:
                for bond in atom.bonds:
                    atom2 = bond.other_atom(atom)
                    if atom2 not in selection:
                        if atom in attached:
                            raise RuntimeError("cannot determine previous substituent; multiple fragments unselected")
                        
                        attached[atom] = atom2
           
                        if atom.structure not in models:
                            models[atom.structure] = {atom.residue:[atom]}
            
                        else:
                            if atom.residue not in models[atom.structure]:
                                models[atom.structure][atom.residue] = [atom]
                            else:
                                models[atom.structure][atom.residue].append(atom)
            
            else:
                if atom.structure not in models:
                    models[atom.structure] = {atom.residue:[atom]}
    
                else:
                    if atom.residue not in models[atom.structure]:
                        models[atom.structure][atom.residue] = [atom]
                    else:
                        models[atom.structure][atom.residue].append(atom)

        first_pass = True
        new_structures = []
        for ndx, subname in enumerate(subnames.split(',')):
            subname = subname.strip()
            sub = Substituent(subname)
            for model in models:
                if self.close_previous_bool and first_pass:
                    for res in models[model]:
                        residue = Residue(res)
                        if new_name is not None:
                            residue.name = new_name[ndx]
                            
                        for target in models[model][res]:
                            if use_attached:
                                end = attached[target].atomspec
                            else:
                                end = None 
                            
                            residue.substitute(sub.copy(), target.atomspec, attached_to=end)
                    
                        residue.update_chix(res)

                    
                elif self.close_previous_bool and not first_pass:
                    raise RuntimeError("only the first model can be replaced")
                else:
                    model_copy = model.copy()
                    
                    residues = [model_copy.residues[i] for i in [model.residues.index(res) for res in models[model]]]
                    
                    rescol = ResidueCollection(model_copy, convert_residues=residues)
                    for res_copy, res in zip(residues, models[model]):                        
                        residue = Residue(res_copy)
                        if new_name is not None:
                            residue.name = new_name[ndx]
                        
                        for target in models[model][res]:
                            if use_attached:
                                end = attached[target].atomspec
                            else:
                                end = None
                                
                            for atom, chix_atom in zip(rescol.atoms, model.atoms):
                                atom.atomspec = chix_atom.atomspec
                                atom.add_tag(chix_atom.atomspec)

                            residue.substitute(sub.copy(), model_copy.atoms[model.atoms.index(target)].atomspec, attached_to=end)
                            
                        residue.update_chix(res_copy)

                    new_structures.append(model_copy)
            
            first_pass = False
        
        if not self.close_previous_bool:
            self.session.models.add(new_structures)

    def open_sub_selector(self):
        self.tool_window.create_child_window("select substituents", window_class=SubstituentSelection, textBox=self.subname)

    def do_maplig(self):
        lignames = self.ligname.text()
        selection = self.session.seqcrow_ordered_selection_manager.selection
        
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
                cat.fix_comment()

                for center_atom in cat.center:
                    center_atom.connected = set([])
                    for atom in cat.atoms:
                        if atom not in cat.center:
                            if center_atom.is_connected(atom):
                                atom.connected.add(center_atom)
                                center_atom.connected.add(atom)
                
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
        selection = self.session.seqcrow_ordered_selection_manager.selection
        new_name = self.new_ring_name.text()
        
        if len(new_name.strip()) == 0:
            new_name = None
        elif any(len(name.strip()) > 4 for name in new_name.split(',')):
            raise RuntimeError("residue names must be 4 characters or less")
        elif any(x in new_name for x in "!@#$%^&*()\\/.<><;':\"[]{}|-=_+"):
            raise RuntimeError("invalid residue name: %s" % new_name)
        elif len(ringnames.split(',')) != len(new_name.split(',')):
            raise RuntimeError("number of substituents is not the same as the number of new names")
        else:
            new_name = [x.strip() for x in new_name.split(',')]
        
        if len(selection) < 2:
            raise RuntimeWarning("two atoms must be selected per molecule")
        
        models = {}
        for atom in selection:
            if atom.structure not in models:
                models[atom.structure] = [atom]
            else:
                models[atom.structure].append(atom)
        
            if len(models[atom.structure]) > 2:
                raise RuntimeError("only two atoms can be selected on any model")
        
        first_pass = True
        new_structures = []
        for i, ringname in enumerate(ringnames.split(',')):
            ringname = ringname.strip()
            
            for model in models:
                atom1 = models[model][0]
                atom2 = models[model][1]
                if self.close_previous_bool and first_pass:
                    convert = minimal_ring_convert(model, *models[model])
                    if new_name is not None:
                        for res in convert:
                            res.name = new_name[i]
                    rescol = ResidueCollection(model, convert_residues=convert)

                elif self.close_previous_bool and not first_pass:
                    raise RuntimeError("only the first model can be replaced")
                else:
                    model_copy = model.copy()
                    a1 = model_copy.atoms[model.atoms.index(models[model][0])]
                    a2 = model_copy.atoms[model.atoms.index(models[model][1])]
                    convert = minimal_ring_convert(model_copy, a1, a2)
                    if new_name is not None:
                        for res in convert:
                            res.name = new_name[i]

                    rescol = ResidueCollection(model_copy, convert_residues=convert)
                                
                    for atom in rescol.atoms:
                        atom.atomspec = model.atoms[model_copy.atoms.index(atom.chix_atom)].atomspec

                target = rescol.find([atom1.atomspec, atom2.atomspec])
                                
                rescol.ring_substitute(target, ringname)
                
                if self.close_previous_bool:                    
                    rescol.update_chix(model)
                else:
                    rescol.update_chix(model_copy)
                    new_structures.append(model_copy)
            
            first_pass = False
        
        if not self.close_previous_bool:
            self.session.models.add(new_structures)

    def open_ring_selector(self):
        self.tool_window.create_child_window("select rings", window_class=RingSelection, textBox=self.ringname)
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
    
    
class SubstituentSelection(ChildToolWindow):
    def __init__(self, tool_instance, title, textBox=None, **kwargs):
        super().__init__(tool_instance, title, **kwargs)
        
        self.textBox = textBox
        
        self._build_ui()
        
    def _build_ui(self):
        layout = QGridLayout()
        
        self.sub_table = SubstituentTable()
        self.sub_table.table.itemSelectionChanged.connect(self.refresh_selection)
        layout.addWidget(self.sub_table)
        
        self.ui_area.setLayout(layout)
        
        self.manage(None)
        
    def refresh_selection(self):
        sub_names = []
        for row in self.sub_table.table.selectionModel().selectedRows():
            if self.sub_table.table.isRowHidden(row.row()):
                continue
            
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
        self.lig_table.table.itemSelectionChanged.connect(self.refresh_selection)
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
        self.ring_table.table.itemSelectionChanged.connect(self.refresh_selection)
        layout.addWidget(self.ring_table)
        
        self.ui_area.setLayout(layout)
        
        self.manage(None)
        
    def refresh_selection(self):
        ring_names = []
        for row in self.ring_table.table.selectionModel().selectedRows():
            if self.ring_table.table.isRowHidden(row.row()):
                continue

            ring_names.append(row.data())
            
        self.textBox.setText(",".join(ring_names))
        


class NameCompleter(QCompleter):
    def __init__(self, name_list, parent=None):
        super().__init__(name_list, parent=parent)
        
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(self.PopupCompletion)
        self.setFilterMode(Qt.MatchContains)
        self.setWrapAround(False)
        
    def pathFromIndex(self, ndx):
        name = super().pathFromIndex(ndx)
        
        names = self.widget().text().split(',')
        
        if len(names) > 1:
            name = "%s, %s" % (", ".join(names[:-1]), name)
            
        return name
        
    def splitPath(self, path):
        path = path.split(',')[-1].strip()
        return [path]