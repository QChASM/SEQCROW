from chimerax.core.tools import ToolInstance
from chimerax.ui.widgets import ColorButton
from chimerax.bild.bild import read_bild
from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import FloatArg, TupleOf

from io import BytesIO

from Qt import QtCore
from Qt.QtWidgets import QGridLayout, QPushButton, QCheckBox, QTabWidget, QWidget, QVBoxLayout

from AaronTools.component import Component
from AaronTools.ring import Ring
from AaronTools.substituent import Substituent

from SEQCROW.libraries import LigandTable, SubstituentTable, RingTable
from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.utils import iter2str
from SEQCROW.managers.filereader_manager import apply_seqcrow_preset

# TODO: change decorations to use ChimeraX atom/bond defaults
class _BrowseLibSettings(Settings):
    AUTO_SAVE = {
        'key_atom_color': Value((0.2, 0.5, 0.8, 0.5), TupleOf(FloatArg, 4), iter2str),
        'ghost_connection_color': Value((0.60784, 0.145098, 0.70196, 0.5), TupleOf(FloatArg, 4), iter2str),
        'ring_walk_color': Value((0.9, 0.4, 0.3, 0.9), TupleOf(FloatArg, 4), iter2str),
    }
    
    
#TODO:
#make double clicking things in the library tables open them

#TODO:
#make the AaronTools 'database' be discoverable (so open Me AaronTools works or whatever)
    
class AaronTools_Library(ToolInstance):

    help = "https://github.com/QChASM/SEQCROW/wiki/Browse-AaronTools-Libraries-Tool"
    SESSION_ENDURING = False
    SESSION_SAVE = False
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        
        self.settings = _BrowseLibSettings(self.session, name)
        
        self.showLigKeyBool = True
        self.showSubGhostBool = True
        self.showRingWalkBool = True
        
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()

        self.library_tabs = QTabWidget()

        #add a tab for ligands
        self.ligand_tab = QWidget()
        self.ligand_layout = QVBoxLayout(self.ligand_tab)
        self.lig_table = LigandTable()
        self.ligand_layout.addWidget(self.lig_table)

        showKeyAtomsCheck = QCheckBox('show key atoms')
        showKeyAtomsCheck.setToolTip("ligand's coordinating atoms will be highlighted")
        showKeyAtomsCheck.toggle()
        showKeyAtomsCheck.stateChanged.connect(self.showKeyAtoms)
        self.ligand_layout.addWidget(showKeyAtomsCheck)
        
        self.lig_color = ColorButton('key atom color', has_alpha_channel=True)
        self.lig_color.setToolTip("highlight color for ligand's key atoms")
        self.lig_color.set_color(self.settings.key_atom_color)
        self.ligand_layout.addWidget(self.lig_color)

        openLigButton = QPushButton("open selected ligands")
        openLigButton.setToolTip("ligands selected in the table will be loaded into ChimeraX")
        openLigButton.clicked.connect(self.open_ligands)
        self.ligand_layout.addWidget(openLigButton)
        self.openLigButton = openLigButton

        #add a tab for substituents
        self.substituent_tab = QWidget()
        self.substituent_layout = QVBoxLayout(self.substituent_tab)
        self.sub_table = SubstituentTable()
        self.substituent_layout.addWidget(self.sub_table)
        
        showGhostConnectionCheck = QCheckBox('show ghost connection')
        showGhostConnectionCheck.setToolTip("ligand's coordinating atoms will be highlighted")
        showGhostConnectionCheck.toggle()
        showGhostConnectionCheck.stateChanged.connect(self.showGhostConnection)
        self.substituent_layout.addWidget(showGhostConnectionCheck)
        
        self.sub_color = ColorButton('ghost connection color', has_alpha_channel=True)
        self.sub_color.setToolTip("color of ghost connection")
        self.sub_color.set_color(self.settings.ghost_connection_color)
        self.substituent_layout.addWidget(self.sub_color)

        openSubButton = QPushButton("open selected substituents")
        openSubButton.setToolTip("substituents selected in the table will be loaded into ChimeraX")
        openSubButton.clicked.connect(self.open_substituents)
        self.substituent_layout.addWidget(openSubButton)
        self.openSubButton = openSubButton
        
        #add a tab for rings
        self.ring_tab = QWidget()
        self.ring_layout = QVBoxLayout(self.ring_tab)
        self.ring_table = RingTable()
        self.ring_layout.addWidget(self.ring_table)
        
        showRingWalkCheck = QCheckBox('show ring walk')
        showRingWalkCheck.setToolTip("arrows will show the way AaronTools traverses the ring")
        showRingWalkCheck.toggle()
        showRingWalkCheck.stateChanged.connect(self.showRingWalk)
        self.ring_layout.addWidget(showRingWalkCheck)
        
        self.ring_color = ColorButton('walk arrow color', has_alpha_channel=True)
        self.ring_color.setToolTip("color of walk arrows")
        self.ring_color.set_color(self.settings.ring_walk_color)
        self.ring_layout.addWidget(self.ring_color)

        openRingButton = QPushButton("open selected rings")
        openRingButton.setToolTip("rings selected in the table will be loaded into ChimeraX")
        openRingButton.clicked.connect(self.open_rings)
        self.ring_layout.addWidget(openRingButton)
        self.openRingButton = openRingButton
        
        self.library_tabs.resize(300, 200)
        
        self.library_tabs.addTab(self.ligand_tab, "ligands")
        self.library_tabs.addTab(self.substituent_tab, "substituents")
        self.library_tabs.addTab(self.ring_tab, "rings")

        layout.addWidget(self.library_tabs)
        
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def showKeyAtoms(self, state):
        if Qt.CheckState(state) == QtCore.Qt.Checked:
            self.showLigKeyBool = True
        else:
            self.showLigKeyBool = False

    def open_ligands(self):
        for row in self.lig_table.table.selectionModel().selectedRows():
            if self.lig_table.table.isRowHidden(row.row()):
                continue
                
            lig_name = row.data()
            ligand = Component(lig_name)
            chimera_ligand = ResidueCollection(ligand, name=lig_name).get_chimera(self.session)

            self.session.models.add([chimera_ligand])
            apply_seqcrow_preset(chimera_ligand, fallback="Ball-Stick-Endcap")

            if self.showLigKeyBool:
                color = self.lig_color.get_color()
                
                color = [c/255. for c in color]
                
                self.settings.key_atom_color = tuple(color)
                
                bild_obj = key_atom_highlight(ligand, color, self.session)
            
                self.session.models.add(bild_obj, parent=chimera_ligand)

    def showGhostConnection(self, state):
        if Qt.CheckState(state) == QtCore.Qt.Checked:
            self.showSubGhostBool = True
        else:
            self.showSubGhostBool = False

    def open_substituents(self):
        for row in self.sub_table.table.selectionModel().selectedRows():
            if self.sub_table.table.isRowHidden(row.row()):
                continue
            
            sub_name = row.data()
            substituent = Substituent(sub_name, name=sub_name)
            chimera_substituent = ResidueCollection(substituent).get_chimera(self.session)

            self.session.models.add([chimera_substituent])
            apply_seqcrow_preset(chimera_substituent, fallback="Ball-Stick-Endcap")

            if self.showSubGhostBool:
                color = self.sub_color.get_color()
                
                color = [c/255. for c in color]
                
                self.settings.ghost_connection_color = tuple(color)
                
                bild_obj = ghost_connection_highlight(substituent, color, self.session)
            
                self.session.models.add(bild_obj, parent=chimera_substituent)

    def showRingWalk(self, state):
        if Qt.CheckState(state) == QtCore.Qt.Checked:
            self.showRingWalkBool = True
        else:
            self.showRingWalkBool = False

    def open_rings(self):
        for row in self.ring_table.table.selectionModel().selectedRows():
            if self.ring_table.table.isRowHidden(row.row()):
                continue

            ring_name = row.data()
            ring = Ring(ring_name, name=ring_name)
            chimera_ring = ResidueCollection(ring.copy()).get_chimera(self.session)

            self.session.models.add([chimera_ring])
            apply_seqcrow_preset(chimera_ring, fallback="Ball-Stick-Endcap")

            if self.showRingWalkBool:
                color = self.ring_color.get_color()
                
                color = [c/255. for c in color]
                
                self.ring_walk_color = tuple(color)
                
                bild_obj = show_walk_highlight(ring, chimera_ring, color, self.session)
            
                self.session.models.add(bild_obj, parent=chimera_ring)
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
    
def key_atom_highlight(ligand, color, session):
    """returns a bild object with spheres on top on ligand's key atoms"""
    s = ".note coordinating atoms\n"
    s += ".color %f %f %f\n" % tuple(color[:-1])
    s += ".transparency %f\n" % (1. - color[-1])
    for atom in ligand.key_atoms:
        if hasattr(atom, "_radii"):
            
            r = 0.6*atom._radii
        else:
            r = 0.5
            
        if atom.element == 'H':
            r *= 1.5
        
        s += ".sphere %f %f %f   %f\n" % (*atom.coords, r)
        
    stream = BytesIO(bytes(s, 'utf-8'))
    bild_obj, status = read_bild(session, stream, "highlighting key atoms")
        
    return bild_obj
    
def ghost_connection_highlight(substituent, color, session):            
    """returns a bild object with a cylinder pointing along the 
    x axis towards the substituent and a sphere at the origin"""
    s = ".note connection to molecule\n"
    s += ".color %f %f %f\n" % tuple(color[:-1])
    s += ".transparency %f\n" % (1. - color[-1])
    s += ".sphere 0 0 0  %f\n" % 0.15
    s += ".cylinder 0 0 0   %f 0 0   %f open\n" % (substituent.atoms[0].coords[0], 0.15)
        
    stream = BytesIO(bytes(s, 'utf-8'))
    bild_obj, status = read_bild(session, stream, "ghost connection")
    
    return bild_obj
    
def show_walk_highlight(ring, chimera_ring, color, session):            
    """returns a bild sphere on the walk atom if there is only one walk atom
    returns a set of bild arrows showing the walk direction if there are multiple walk atoms
        will also hide any bonds on chimera_ring that are under/over the arrows"""
    s = ".note direction to walk around ring\n"
    s += ".color %f %f %f\n" % tuple(color[:-1])
    s += ".transparency %f\n" % (1. - color[-1])
    if len(ring.end) == 1:
        if hasattr(ring.end[0], "_radii"):
            r = 0.6*ring.end[0]._radii
        else:
            r = 1
        
        info = tuple(ring.end[0].coords) + (r,)
        s += ".sphere %f %f %f   %f\n" % info
    else:
        r_bd = 0.16
        for atom1, atom2 in zip(ring.end[:-1], ring.end[1:]):                       
            v = atom1.bond(atom2)
            
            if hasattr(atom2, "_radii"):
                r_sp = 0.4*atom2._radii
            else:
                r_sp = 0.4
            
            info = tuple(atom1.coords) + tuple(atom2.coords - r_sp*v) + (r_bd, 1.5*r_bd,)
            s += ".arrow %f %f %f   %f %f %f   %f %f 0.7\n" % info
        
            for bond in chimera_ring.bonds:
                bond_atoms = [chimera_ring.atoms.index(atom) for atom in bond.atoms]
                if ring.atoms.index(atom1) in bond_atoms and ring.atoms.index(atom2) in bond_atoms:
                    bond.display  = False
                    break
                        
    stream = BytesIO(bytes(s, 'utf-8'))
    bild_obj, status = read_bild(session, stream, "walk direction")
    
    return bild_obj
