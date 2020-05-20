import os
import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.atomic import selected_atoms

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QPushButton, QTabWidget, QWidget, QVBoxLayout, QLineEdit, QLabel, QSpinBox, QFormLayout, QMessageBox

from AaronTools.component import Component
from AaronTools.ring import Ring
from AaronTools.substituent import Substituent
from AaronTools.const import AARONLIB

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.tools import key_atom_highlight, ghost_connection_highlight, show_walk_highlight

from warnings import warn

# TODO: change decorations to use ChimeraX atom/bond defaults

class LibAdd(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    help = "https://github.com/QChASM/ChimAARON/wiki/Add-to-Personal-Library-Tool"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        
        self.key_atomspec = []
                
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()

        library_tabs = QTabWidget()
        
        
        #ligand tab
        ligand_tab = QWidget()
        ligand_layout = QGridLayout(ligand_tab)
        
        ligand_name_label = QLabel("ligand name:")
        ligand_layout.addWidget(ligand_name_label, 0, 0)
        self.ligand_name = QLineEdit()
        self.ligand_name.setText("")
        self.ligand_name.setToolTip("name of ligand you are adding to your ligand library\nleave blank to open a new model with just the ligand")
        ligand_layout.addWidget(self.ligand_name, 0, 1)
        
        ligand_key_atoms = QPushButton("set key atoms to current selection")
        ligand_key_atoms.clicked.connect(self.update_key_atoms)
        ligand_key_atoms.setToolTip("the current selection will be the key atoms for the ligand\nleave blank to automatically determine key atoms")
        ligand_layout.addWidget(ligand_key_atoms, 1, 0, 1, 2)
        
        libadd_ligand = QPushButton("add current selection to library")
        libadd_ligand.clicked.connect(self.libadd_ligand)
        ligand_layout.addWidget(libadd_ligand, 2, 0, 1, 2)  

        
        #substituent tab
        sub_tab = QWidget()
        sub_layout = QGridLayout(sub_tab)

        sub_info_form = QWidget()
        sub_info = QFormLayout(sub_info_form)
        
        self.sub_name = QLineEdit()
        self.sub_name.setText("")
        self.sub_name.setToolTip("name of substituent you are adding to your substituent library\nleave blank to open a new model with just the substituent")
        sub_info.addRow("substituent name:", self.sub_name)
        
        self.sub_confs = QSpinBox()
        self.sub_confs.setMinimum(1)
        sub_info.addRow("number of conformers:", self.sub_confs)
        
        self.sub_angle = QSpinBox()
        self.sub_angle.setRange(0, 180)
        self.sub_angle.setSingleStep(30)
        sub_info.addRow("angle between conformers:", self.sub_angle)
        
        sub_layout.addWidget(sub_info_form)
        
        libadd_sub = QPushButton("add current selection to library")
        libadd_sub.clicked.connect(self.libadd_substituent)
        sub_layout.addWidget(libadd_sub)

        #ring tab
        ring_tab = QWidget()
        ring_layout = QGridLayout(ring_tab)
        
        ring_name_label = QLabel("ring name:")
        ring_layout.addWidget(ring_name_label, 0, 0)
        self.ring_name = QLineEdit()
        self.ring_name.setText("")
        self.ring_name.setToolTip("name of ring you are adding to your ring library\nleave blank to open a new model with just the ring")
        ring_layout.addWidget(self.ring_name, 0, 1)
        
        libadd_ring = QPushButton("add ring with selected walk to library")
        libadd_ring.clicked.connect(self.libadd_ring)
        ring_layout.addWidget(libadd_ring, 1, 0, 1, 2)
        
        
        library_tabs.addTab(sub_tab, "substituent")
        library_tabs.addTab(ring_tab, "ring")
        library_tabs.addTab(ligand_tab, "ligand")
        

        layout.addWidget(library_tabs)
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage('side')

    def update_key_atoms(self):
        selection = selected_atoms(self.session)
        if not selection.single_structure:
            raise RuntimeError("selected atoms must be on the same model")
                
        else:
            self.key_atomspec = selection
        
        self.tool_window.status("key atoms set to %s" % " ".join(atom.atomspec for atom in selection))
        
    def libadd_ligand(self):
        """add ligand to library or open it in a new model"""
        selection = selected_atoms(self.session)
        
        if not selection.single_structure:
            raise RuntimeError("selected atoms must be on the same model")
          
        rescol = ResidueCollection(selection[0].structure)
        ligand_atoms = [atom for atom in rescol.atoms if atom.chix_atom in selection]

        key_chix_atoms = [atom for atom in self.key_atomspec if not atom.deleted]
        if len(key_chix_atoms) < 1:
            key_atoms = set([])
            for atom in ligand_atoms:
                for atom2 in atom.connected:
                    if atom2 not in ligand_atoms:
                        key_atoms.add(atom)
                        
        else:
            key_atoms = rescol.find(",".join([atom.atomspec for atom in key_chix_atoms]))
                        
        if len(key_atoms) < 1:
            raise RuntimeError("no key atoms could be determined")
        
        lig_name = self.ligand_name.text()
        ligand = Component(ligand_atoms, name=lig_name, key_atoms=key_atoms)
        ligand.comment = "K:%s" % ",".join([str(ligand.atoms.index(atom) + 1) for atom in key_atoms])
        
        if len(lig_name) == 0:
            chimerax_ligand = ResidueCollection(ligand).get_chimera(self.session)
            chimerax_ligand.name = "ligand preview"
            self.session.models.add([chimerax_ligand])
            bild_obj = key_atom_highlight(ligand, [0.2, 0.5, 0.8, 0.5], self.session)
            self.session.models.add(bild_obj, parent=chimerax_ligand)
            
        else:
            check_aaronlib_dir()
            filename = os.path.join(AARONLIB, "Ligands", lig_name + ".xyz")
            if os.path.exists(filename):
                exists_warning = QMessageBox()
                exists_warning.setIcon(QMessageBox.Warning)
                exists_warning.setText("%s already exists.\nWould you like to overwrite?" % filename)
                exists_warning.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                
                rv = exists_warning.exec_()
                if rv == QMessageBox.Yes:
                    ligand.write(outfile=filename)
                    self.tool_window.status("%s added to ligand library" % lig_name)
                
                else:
                    self.tool_window.status("%s has not been added to ligand library" % lig_name)

            else:
                ligand.write(outfile=filename)
                self.tool_window.status("%s added to ligand library" % lig_name)        
        
    def libadd_ring(self):
        """add ring to library or open it in a new model"""
        selection = self.session.seqcrow_ordered_selection_manager.selection
        
        if not selection.single_structure:
            raise RuntimeError("selected atoms must be on the same model")
          
        rescol = ResidueCollection(selection[0].structure)
        walk_atoms = rescol.find(",".join([atom.atomspec for atom in selection]))
                        
        if len(walk_atoms) < 1:
            raise RuntimeError("no walk direction could be determined")
        
        ring_name = self.ring_name.text()
        ring = Ring(rescol, name=ring_name, end=walk_atoms)
        ring.comment = "E:%s" % ",".join([str(rescol.atoms.index(atom) + 1) for atom in walk_atoms])
        
        if len(ring_name) == 0:
            chimerax_ring = ResidueCollection(ring).get_chimera(self.session)
            chimerax_ring.name = "ring preview"
            self.session.models.add([chimerax_ring])
            bild_obj = show_walk_highlight(ring, chimerax_ring, [0.9, 0.4, 0.3, 0.9], self.session)
            self.session.models.add(bild_obj, parent=chimerax_ring)
            
        else:
            check_aaronlib_dir()
            filename = os.path.join(AARONLIB, "Rings", ring_name + ".xyz")
            if os.path.exists(filename):
                exists_warning = QMessageBox()
                exists_warning.setIcon(QMessageBox.Warning)
                exists_warning.setText("%s already exists.\nWould you like to overwrite?" % filename)
                exists_warning.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                
                rv = exists_warning.exec_()
                if rv == QMessageBox.Yes:
                    ring.write(outfile=filename)
                    self.tool_window.status("%s added to ring library" % ring_name)
                
                else:
                    self.tool_window.status("%s has not been added to ring library" % ring_name)

            else:
                ring.write(outfile=filename)
                self.tool_window.status("%s added to ring library" % ring_name)        
    
    def libadd_substituent(self):
        """add ligand to library or open it in a new model"""
        selection = selected_atoms(self.session)
        
        if not selection.single_structure:
            raise RuntimeError("selected atoms must be on the same model")
          
        rescol = ResidueCollection(selection[0].structure)
            
        substituent_atoms = [atom for atom in rescol.atoms if atom.chix_atom in selection]
        
        start = None
        avoid = None
        for atom in substituent_atoms:
            for atom2 in atom.connected:
                if atom2 not in substituent_atoms:
                    if start is None:
                        start = atom
                        avoid = atom2
                    else:
                        raise RuntimeError("substituent must only have one connection to the molecule")
                        
        if start is None:
            raise RuntimeError("substituent is not connected to a larger molecule")
            
        substituent_atoms.remove(start)
        substituent_atoms.insert(0, start)
        
        sub_name = self.sub_name.text()
        confs = self.sub_confs.value()
        angle = self.sub_angle.value()
        
        comment = "CF:%i,%i" % (confs, angle)
        if len(sub_name) == 0:
            sub = Substituent(substituent_atoms, name="test", conf_num=confs, conf_angle=angle)
        else:
            sub = Substituent(substituent_atoms, name=sub_name, conf_num=confs, conf_angle=angle)
        
        sub.comment = comment
        
        #align substituent bond to x axis
        sub.coord_shift(-avoid.coords)
        x_axis = np.array([1., 0., 0.])
        n = np.linalg.norm(start.coords)
        vb = start.coords/n
        d = np.linalg.norm(vb - x_axis)
        theta = np.arccos((d**2 - 2) / -2)
        vx = np.cross(vb, x_axis)
        sub.rotate(vx, theta)
        
        if len(sub_name) == 0:
            chimerax_sub = ResidueCollection(sub).get_chimera(self.session)
            chimerax_sub.name = "substituent preview"
            self.session.models.add([chimerax_sub])
            bild_obj = ghost_connection_highlight(sub, [0.60784, 0.145098, 0.70196, 0.5], self.session)
            self.session.models.add(bild_obj, parent=chimerax_sub)
            
        else:
            check_aaronlib_dir()
            filename = os.path.join(AARONLIB, "Subs", sub_name + ".xyz")
            if os.path.exists(filename):
                exists_warning = QMessageBox()
                exists_warning.setIcon(QMessageBox.Warning)
                exists_warning.setText("%s already exists.\nWould you like to overwrite?" % filename)
                exists_warning.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                
                rv = exists_warning.exec_()
                if rv == QMessageBox.Yes:
                    sub.write(outfile=filename)
                    self.tool_window.status("%s added to substituent library" % sub_name)
                
                else:
                    self.tool_window.status("%s has not been added to substituent library" % sub_name)

            else:
                sub.write(outfile=filename)
                self.tool_window.status("%s added to substituent library" % sub_name)
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
    
def check_aaronlib_dir():
    aaronlib = os.getenv("AARONLIB", False)
    if not aaronlib:
        aaronlib = AARONLIB
        warn("AARONLIB environment variable not set, using %s" % aaronlib)
        
    libs = ["Subs", "Ligands", "Rings"]
    for d in libs:
        library_dir = os.path.join(aaronlib, d)
        if not os.path.isdir(library_dir):
            os.makedirs(library_dir)
