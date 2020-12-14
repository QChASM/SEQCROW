from AaronTools.substituent import Substituent
from AaronTools.component import Component
from AaronTools.ring import Ring

from chimerax.atomic import selected_atoms, selected_residues, PseudobondGroup
from chimerax.atomic.colors import element_color
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands import BoolArg, run

from io import BytesIO

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QTabWidget, QComboBox, \
                            QTableWidget, QTableView, QWidget, QVBoxLayout, QTableWidgetItem, \
                            QFormLayout, QCheckBox, QCompleter

from AaronTools.const import ELEMENTS
from AaronTools.atoms import Atom

from SEQCROW.residue_collection import ResidueCollection, Residue
from SEQCROW.libraries import SubstituentTable, LigandTable, RingTable
from SEQCROW.commands.substitute import guessAttachmentTargets
from SEQCROW.finders import AtomSpec
from SEQCROW.widgets import PeriodicTable, ModelComboBox
from SEQCROW.managers.filereader_manager import apply_seqcrow_preset


class _EditStructureSettings(Settings):
    AUTO_SAVE = {'modify': Value(True, BoolArg), 
                 'guess': Value(True, BoolArg),
                 'minimize': Value(False, BoolArg), 
                 'change_bonds': Value(True, BoolArg), 
                }


class EditStructure(ToolInstance):

    help = "https://github.com/QChASM/SEQCROW/wiki/Structure-Modification-Tool"
    SESSION_ENDURING = True
    SESSION_SAVE = True

    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.settings = _EditStructureSettings(session, "Structure Modification")
        
        self.tool_window = MainToolWindow(self)        

        self.close_previous_bool = self.settings.modify

        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()
        
        self.alchemy_tabs = QTabWidget()
        
        #substitute
        substitute_tab = QWidget()
        substitute_layout = QGridLayout(substitute_tab) 

        sublabel = QLabel("substituent name:")
        substitute_layout.addWidget(sublabel, 0, 0, Qt.AlignVCenter)
        
        self.subname = QLineEdit()
        sub_completer = NameCompleter(Substituent.list(), self.subname)
        self.subname.setCompleter(sub_completer)
        self.subname.setToolTip("name of substituent in the AaronTools library or your personal library\nseparate names with commas and uncheck 'modify selected structure' to create several structures")
        substitute_layout.addWidget(self.subname, 0, 1, Qt.AlignVCenter)
        
        open_sub_lib = QPushButton("from library...")
        open_sub_lib.clicked.connect(self.open_sub_selector)
        substitute_layout.addWidget(open_sub_lib, 0, 2, Qt.AlignTop)        
        
        substitute_layout.addWidget(QLabel("modify selected structure:"), 1, 0, 1, 1, Qt.AlignVCenter)
        
        self.close_previous_sub = QCheckBox()
        self.close_previous_sub.setToolTip("checked: selected structure will be modified\nunchecked: new model will be created for the modified structure")
        self.close_previous_sub.setChecked(self.settings.modify)
        self.close_previous_sub.stateChanged.connect(self.close_previous_change)
        substitute_layout.addWidget(self.close_previous_sub, 1, 1, 1, 2, Qt.AlignTop)    
        
        substitute_layout.addWidget(QLabel("relax substituent:"), 2, 0, 1, 1, Qt.AlignVCenter)
        
        self.minimize = QCheckBox()
        self.minimize.setToolTip("spin the added substituents to try to minimize the LJ potential energy")
        self.minimize.setChecked(self.settings.minimize)
        substitute_layout.addWidget(self.minimize, 2, 1, 1, 1, Qt.AlignTop)
        
        substitute_layout.addWidget(QLabel("guess previous substituent:"), 3, 0, 1, 1, Qt.AlignVCenter)
        
        self.guess_old = QCheckBox()
        self.guess_old.setToolTip("checked: leave the longest connected fragment in the residue\nunchecked: previous substituent must be selected")
        self.guess_old.setChecked(self.settings.guess)
        self.guess_old.stateChanged.connect(lambda state, settings=self.settings: settings.__setattr__("guess", True if state == Qt.Checked else False))
        substitute_layout.addWidget(self.guess_old, 3, 1, 1, 2, Qt.AlignTop)
        
        substitute_layout.addWidget(QLabel("new residue name:"), 4, 0, 1, 1, Qt.AlignVCenter)
        
        self.new_sub_name = QLineEdit()
        self.new_sub_name.setToolTip("change name of modified residues")
        self.new_sub_name.setPlaceholderText("leave blank to keep current")
        substitute_layout.addWidget(self.new_sub_name, 4, 1, 1, 2, Qt.AlignTop)
        
        substitute_button = QPushButton("substitute current selection")
        substitute_button.clicked.connect(self.do_substitute)
        substitute_layout.addWidget(substitute_button, 5, 0, 1, 3, Qt.AlignTop)
        
        substitute_layout.setRowStretch(0, 0)
        substitute_layout.setRowStretch(1, 0)
        substitute_layout.setRowStretch(2, 0)
        substitute_layout.setRowStretch(3, 0)
        substitute_layout.setRowStretch(4, 0)
        substitute_layout.setRowStretch(5, 1)
        
        
        #map ligand
        maplig_tab = QWidget()
        maplig_layout = QGridLayout(maplig_tab)
        
        liglabel = QLabel("ligand name:")
        maplig_layout.addWidget(liglabel, 0, 0, Qt.AlignVCenter)
        
        self.ligname = QLineEdit()
        lig_completer = NameCompleter(Component.list(), self.ligname)
        self.ligname.setCompleter(lig_completer)
        self.ligname.setToolTip("name of ligand in the AaronTools library or your personal library\nseparate names with commas and uncheck 'modify selected structure' to create several structures")
        maplig_layout.addWidget(self.ligname, 0, 1, Qt.AlignVCenter)
        
        open_lig_lib = QPushButton("from library...")
        open_lig_lib.clicked.connect(self.open_lig_selector)
        maplig_layout.addWidget(open_lig_lib, 0, 2, Qt.AlignTop)        
        
        maplig_layout.addWidget(QLabel("modify selected structure:"), 1, 0, 1, 1, Qt.AlignVCenter)
        
        self.close_previous_lig = QCheckBox()
        self.close_previous_lig.setToolTip("checked: selected structure will be modified\nunchecked: new model will be created for the modified structure")
        self.close_previous_lig.setChecked(self.settings.modify)
        self.close_previous_lig.stateChanged.connect(self.close_previous_change)
        maplig_layout.addWidget(self.close_previous_lig, 1, 1, 1, 2, Qt.AlignTop)

        maplig_button = QPushButton("swap ligand with selected coordinating atoms")
        maplig_button.clicked.connect(self.do_maplig)
        maplig_layout.addWidget(maplig_button, 2, 0, 1, 3, Qt.AlignTop)

        start_structure_button = QPushButton("place in:")
        self.lig_model_selector = ModelComboBox(self.session, addNew=True)
        start_structure_button.clicked.connect(self.do_new_lig)
        maplig_layout.addWidget(start_structure_button, 3, 0, 1, 1, Qt.AlignTop)
        maplig_layout.addWidget(self.lig_model_selector, 3, 1, 1, 2, Qt.AlignTop)

        maplig_layout.setRowStretch(0, 0)
        maplig_layout.setRowStretch(1, 0)
        maplig_layout.setRowStretch(2, 0)
        maplig_layout.setRowStretch(3, 1)
        
        
        #close ring
        closering_tab = QWidget()
        closering_layout = QGridLayout(closering_tab)
        
        ringlabel = QLabel("ring name:")
        closering_layout.addWidget(ringlabel, 0, 0, Qt.AlignVCenter)
        
        self.ringname = QLineEdit()
        ring_completer = NameCompleter(Ring.list(), self.ringname)
        self.ringname.setCompleter(ring_completer)
        self.ringname.setToolTip("name of ring in the AaronTools library or your personal library\nseparate names with commas and uncheck 'modify selected structure' to create several structures")
        closering_layout.addWidget(self.ringname, 0, 1, Qt.AlignVCenter)
        
        open_ring_lib = QPushButton("from library...")
        open_ring_lib.clicked.connect(self.open_ring_selector)
        closering_layout.addWidget(open_ring_lib, 0, 2, Qt.AlignTop)        
        
        closering_layout.addWidget(QLabel("modify selected structure:"), 1, 0, 1, 1, Qt.AlignVCenter) 
        
        self.close_previous_ring = QCheckBox()
        self.close_previous_ring.setToolTip("checked: selected structure will be modified\nunchecked: new model will be created for the modified structure")
        self.close_previous_ring.setChecked(self.settings.modify)
        self.close_previous_ring.stateChanged.connect(self.close_previous_change)
        closering_layout.addWidget(self.close_previous_ring, 1, 1, 1, 2, Qt.AlignTop)

        closering_layout.addWidget(QLabel("new residue name:"), 2, 0, 1, 1, Qt.AlignVCenter)
        
        self.new_ring_name = QLineEdit()
        self.new_ring_name.setToolTip("change name of modified residues")
        self.new_ring_name.setPlaceholderText("leave blank to keep current")
        closering_layout.addWidget(self.new_ring_name, 2, 1, 1, 2, Qt.AlignTop)

        closering_button = QPushButton("put a ring on current selection")
        closering_button.clicked.connect(self.do_fusering)
        closering_layout.addWidget(closering_button, 3, 0, 1, 3, Qt.AlignTop)

        start_structure_button = QPushButton("place in:")
        self.ring_model_selector = ModelComboBox(self.session, addNew=True)
        start_structure_button.clicked.connect(self.do_new_ring)
        closering_layout.addWidget(start_structure_button, 4, 0, 1, 1, Qt.AlignTop)
        closering_layout.addWidget(self.ring_model_selector, 4, 1, 1, 2, Qt.AlignTop)

        closering_layout.setRowStretch(0, 0)
        closering_layout.setRowStretch(1, 0)
        closering_layout.setRowStretch(2, 0)
        closering_layout.setRowStretch(3, 0)
        closering_layout.setRowStretch(4, 1)


        #change element
        changeelement_tab = QWidget()
        changeelement_layout = QFormLayout(changeelement_tab)
        
        self.element = QPushButton("C")
        self.element.setMinimumWidth(int(1.3*self.element.fontMetrics().boundingRect("QQ").width()))
        self.element.setMaximumWidth(int(1.3*self.element.fontMetrics().boundingRect("QQ").width()))
        self.element.setMinimumHeight(int(1.5*self.element.fontMetrics().boundingRect("QQ").height()))
        self.element.setMaximumHeight(int(1.5*self.element.fontMetrics().boundingRect("QQ").height()))
        ele_color = tuple(list(element_color(ELEMENTS.index("C")))[:-1])
        self.element.setStyleSheet("QPushButton { background: rgb(%i, %i, %i); color: %s; font-weight: bold; }" % (*ele_color, 'white' if sum(int(x < 150) - int(x > 250) for x in ele_color) - int(ele_color[1] > 200) + int(ele_color[2] > 200) >= 2 else 'black'))
        self.element.clicked.connect(self.open_ptable)
        changeelement_layout.addRow("element:", self.element)
        
        self.vsepr = QComboBox()
        self.vsepr.addItems(["do not change",               # 0
                             "linear (1 bond)",             # 1
                             "linear (2 bonds)",            # 2 
                             "trigonal planar (2 bonds)",   # 3
                             "tetrahedral (2 bonds)",       # 4 
                             "trigonal planar",             # 5
                             "tetrahedral (3 bonds)",       # 6
                             "T-shaped",                    # 7
                             "tetrahedral",                 # 8
                             "sawhorse",                    # 9
                             "square planar",               #10
                             "trigonal bipyramidal",        #11
                             "square pyramidal",            #12
                             "octahedral",                  #13
                            ]
        )
        
        self.vsepr.setCurrentIndex(8)
        
        self.vsepr.insertSeparator(13)
        self.vsepr.insertSeparator(11)
        self.vsepr.insertSeparator(8)
        self.vsepr.insertSeparator(5)
        self.vsepr.insertSeparator(2)
        self.vsepr.insertSeparator(1)
        self.vsepr.insertSeparator(0)
        changeelement_layout.addRow("VSEPR:", self.vsepr)
        
        self.change_bonds = QCheckBox()
        self.change_bonds.setChecked(self.settings.change_bonds)
        changeelement_layout.addRow("adjust bond lengths:", self.change_bonds)
        
        change_element_button = QPushButton("change selected elements")
        change_element_button.clicked.connect(self.do_change_element)
        changeelement_layout.addRow(change_element_button)

        start_structure_button = QPushButton("place in:")
        self.model_selector = ModelComboBox(self.session, addNew=True)
        start_structure_button.clicked.connect(self.do_new_atom)
        changeelement_layout.addRow(start_structure_button, self.model_selector)
        
        delete_atoms_button = QPushButton("delete selected atoms")
        delete_atoms_button.clicked.connect(self.delete_atoms)
        changeelement_layout.addRow(delete_atoms_button)

        self.alchemy_tabs.addTab(substitute_tab, "substitute")
        self.alchemy_tabs.addTab(maplig_tab, "swap ligand")
        self.alchemy_tabs.addTab(closering_tab, "fuse ring")
        self.alchemy_tabs.addTab(changeelement_tab, "change element")

        layout.addWidget(self.alchemy_tabs)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
    
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
        
        new_name = self.new_sub_name.text()

        use_attached = not self.guess_old.isChecked()
        
        minimize = self.minimize.isChecked()
        
        self.settings.minimize = minimize

        if len(new_name.strip()) > 0:
            run(self.session, "substitute sel substituents %s newName %s guessAttachment %s modify %s minimize %s" %
                              (subnames, \
                               new_name, \
                               not use_attached, \
                               self.close_previous_bool, \
                               minimize)
                )

        else:
            run(self.session, "substitute sel substituents %s guessAttachment %s modify %s minimize %s" %
                              (subnames, \
                               not use_attached, \
                               self.close_previous_bool, \
                               minimize)
                )

    def open_sub_selector(self):
        self.tool_window.create_child_window("select substituents", window_class=SubstituentSelection, textBox=self.subname)

    def do_maplig(self):
        lignames = self.ligname.text()
        selection = self.session.seqcrow_ordered_selection_manager.selection
        sel = selected_atoms(self.session)
        if len(sel) != len(selection) or not all(a in selection for a in sel) or not all(a in sel for a in selection):
            selection = sel
        
        if len(selection) < 1:
            raise RuntimeWarning("nothing selected")
        
        models = {}
        for atom in selection:
            if atom.structure not in models:
                models[atom.structure] = [AtomSpec(atom.atomspec)]
            else:
                models[atom.structure].append(AtomSpec(atom.atomspec))        
        
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

                target = rescol.find(models[model])
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
                
                rescol.map_ligand(ligands, target)

                for center_atom in rescol.center:
                    center_atom.connected = set([])
                    for atom in rescol.atoms:
                        if atom not in rescol.center:
                            if center_atom.is_connected(atom):
                                atom.connected.add(center_atom)
                                center_atom.connected.add(atom)
                
                if self.close_previous_bool:    
                    rescol.update_chix(model)
                else:
                    struc = rescol.get_chimera(self.session)
                    new_structures.append(struc)
            
            first_pass = False
        
        if not self.close_previous_bool:
            self.session.models.add(new_structures)

    def open_lig_selector(self):
        self.tool_window.create_child_window("select ligands", window_class=LigandSelection, textBox=self.ligname)
    
    def do_fusering(self):
        ring_names = self.ringname.text()
        
        new_name = self.new_ring_name.text()

        if len(new_name.strip()) > 0:
            run(self.session, "fuseRing sel rings %s newName %s modify %s" %
                              (ring_names, \
                               new_name, \
                               self.close_previous_bool)
                )

        else:
            run(self.session, "fuseRing sel rings %s modify %s" %
                              (ring_names, \
                               self.close_previous_bool)
                )

    def open_ring_selector(self):
        self.tool_window.create_child_window("select rings", window_class=RingSelection, textBox=self.ringname)

    def open_ptable(self):
        self.tool_window.create_child_window("select element", window_class=PTable, button=self.element)
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
    
    def do_change_element(self):
        element = self.element.text()
        adjust_bonds = self.change_bonds.isChecked()
        self.settings.change_bonds = adjust_bonds
        vsepr = self.vsepr.currentText()
        
        if vsepr == "do not change":
            vsepr = False
        elif vsepr == "linear (1 bond)":
            vsepr = "linear 1"
            goal = 1
        elif vsepr == "linear (2 bonds)":
            vsepr = "linear 2"
            goal = 2
        elif vsepr == "trigonal planar (2 bonds)":
            vsepr = "bent 2 planar"
            goal = 2
        elif vsepr == "tetrahedral (2 bonds)":
            vsepr = "bent 2 tetrahedral"
            goal = 2
        elif vsepr == "trigonal planar":
            goal = 3
        elif vsepr == "tetrahedral (3 bonds)":
            vsepr = "bent 3 tetrahedral"
            goal = 3
        elif vsepr == "T-shaped":
            vsepr = "t shaped"
            goal = 3
        elif vsepr == "tetrahedral":
            goal = 4
        elif vsepr == "sawhorse":
            goal = 4
        elif vsepr == "square planar":
            goal = 4
        elif vsepr == "trigonal bipyramidal":
            goal = 5
        elif vsepr == "square pyramidal":
            goal = 5
        elif vsepr == "octahedral":
            goal = 6
        
        sel = selected_atoms(self.session)
        models, _ = guessAttachmentTargets(sel, self.session, allow_adjacent=False)
        for model in models:
            conv_res = list(models[model].keys())
            for res in models[model]:
                for target in models[model][res]:
                    for neighbor in target.neighbors:
                        if neighbor.residue not in conv_res:
                            conv_res.append(neighbor.residue)
            
                    for pbg in self.session.models.list(type=PseudobondGroup):
                        for pbond in pbg.pseudobonds:
                            if target in pbond.atoms and all(atom.structure is model for atom in pbond.atoms):
                                other_atom = pbond.other_atom(target)
                                if other_atom.residue not in conv_res:
                                    conv_res.append(other_atom.residue)
                    
            
            rescol = ResidueCollection(model, convert_residues=conv_res)
            for res in models[model]:
                residue = [resi for resi in rescol.residues if resi.chix_residue is res][0]
                
                for target in models[model][res]:
                    targ = rescol.find_exact(AtomSpec(target.atomspec))[0]
                    adjust_hydrogens = vsepr
                    if vsepr is not False:
                        cur_bonds = len(targ.connected)
                        change_Hs = goal - cur_bonds
                        adjust_hydrogens = (change_Hs, vsepr)

                    residue.change_element(targ, 
                                           element, 
                                           adjust_bonds=adjust_bonds, 
                                           adjust_hydrogens=adjust_hydrogens,
                    )
                
                residue.update_chix(res)    
    
    def do_new_ring(self):
        rings = self.ringname.text()
        
        for ring in rings.split(","):
            ring = ring.strip()
            
            rescol = ResidueCollection(Ring(ring))
        
            model = self.ring_model_selector.currentData()
            if model is None:
                chix = rescol.get_chimera(self.session)
                self.session.models.add([chix])
                apply_seqcrow_preset(chix, fallback="Ball-Stick-Endcap")
                self.ring_model_selector.setCurrentIndex(self.ring_model_selector.count()-1)
    
            else:
                res = model.new_residue("new", "a", len(model.residues)+1)
                rescol.residues[0].update_chix(res)
                run(self.session, "select add %s" % " ".join([atom.atomspec for atom in res.atoms]))
    
    def do_new_lig(self):
        ligands = self.ligname.text()
        
        for lig in ligands.split(","):
            lig = lig.strip()
            
            rescol = ResidueCollection(Component(lig))
        
            model = self.lig_model_selector.currentData()
            if model is None:
                chix = rescol.get_chimera(self.session)
                self.session.models.add([chix])
                apply_seqcrow_preset(chix, fallback="Ball-Stick-Endcap")
                self.lig_model_selector.setCurrentIndex(self.lig_model_selector.count()-1)
    
            else:
                res = model.new_residue("new", "a", len(model.residues)+1)
                rescol.residues[0].update_chix(res)
                run(self.session, "select add %s" % " ".join([atom.atomspec for atom in res.atoms]))

    def do_new_atom(self):
        element = self.element.text()
        adjust_bonds = self.change_bonds.isChecked()
        self.settings.change_bonds = adjust_bonds
        vsepr = self.vsepr.currentText()
        
        if vsepr == "do not change":
            vsepr = False
        elif vsepr == "linear (1 bond)":
            vsepr = "linear 1"
            goal = 1
        elif vsepr == "linear (2 bonds)":
            vsepr = "linear 2"
            goal = 2
        elif vsepr == "trigonal planar (2 bonds)":
            vsepr = "bent 2 planar"
            goal = 2
        elif vsepr == "tetrahedral (2 bonds)":
            vsepr = "bent 2 tetrahedral"
            goal = 2
        elif vsepr == "trigonal planar":
            goal = 3
        elif vsepr == "tetrahedral (3 bonds)":
            vsepr = "bent 3 tetrahedral"
            goal = 3
        elif vsepr == "T-shaped":
            vsepr = "t shaped"
            goal = 3
        elif vsepr == "tetrahedral":
            goal = 4
        elif vsepr == "sawhorse":
            goal = 4
        elif vsepr == "square planar":
            goal = 4
        elif vsepr == "trigonal bipyramidal":
            goal = 5
        elif vsepr == "square pyramidal":
            goal = 5
        elif vsepr == "octahedral":
            goal = 6
        
        atom = Atom(element=element, coords=[0., 0., 0.])
        rescol = ResidueCollection([atom], name="new")
        
        adjust_hydrogens = vsepr
        if vsepr is not False:
            change_Hs = goal
            adjust_hydrogens = (change_Hs, vsepr)
        
        rescol.change_element(atom, 
                              element, 
                              adjust_bonds=adjust_bonds, 
                              adjust_hydrogens=adjust_hydrogens,
        )
        
        model = self.model_selector.currentData()
        if model is None:
            chix = rescol.get_chimera(self.session)
            self.session.models.add([chix])
            apply_seqcrow_preset(chix, fallback="Ball-Stick-Endcap")
            self.model_selector.setCurrentIndex(self.model_selector.count()-1)

        else:
            res = model.new_residue("new", "a", len(model.residues)+1)
            rescol.residues[0].update_chix(res)
            run(self.session, "select add %s" % " ".join([atom.atomspec for atom in res.atoms]))
    
    def delete_atoms(self, *args):
        atoms = selected_atoms(self.session)
        for atom in atoms:
            atom.delete()
    
    def delete(self):
        self.ring_model_selector.deleteLater()
        self.lig_model_selector.deleteLater()
        self.model_selector.deleteLater()

        return super().delete()    
    
    def close(self):
        self.ring_model_selector.deleteLater()
        self.lig_model_selector.deleteLater()
        self.model_selector.deleteLater()

        return super().close()
    
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


class PTable(ChildToolWindow):
    def __init__(self, tool_instance, title, button, **kwargs):
        super().__init__(tool_instance, title, **kwargs)
        
        self.button = button
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QGridLayout()
        
        self.ptable = PeriodicTable(initial_elements=[self.button.text()], select_multiple=False)
        self.ptable.elementSelectionChanged.connect(self.element_changed)
        layout.addWidget(self.ptable)
        
        self.ui_area.setLayout(layout)
        
        self.manage(None)
    
    def element_changed(self, *args):
        elements = self.ptable.selectedElements()
        
        if len(elements) == 1:
            element = elements[0]
            self.button.setText(element)
            ele_color = tuple(list(element_color(ELEMENTS.index(element)))[:-1])
            self.button.setStyleSheet("QPushButton { background: rgb(%i, %i, %i); color: %s; font-weight: bold; }" % (*ele_color, 'white' if sum(int(x < 150) - int(x > 250) for x in ele_color) - int(ele_color[1] > 200) + int(ele_color[2] > 200) >= 2 else 'black'))


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