import os
import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.atomic import selected_atoms
from chimerax.bild.bild import read_bild
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import BoolArg
from chimerax.core.settings import Settings

from io import BytesIO

from PyQt5.Qt import QClipboard
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QPushButton, QFormLayout, QComboBox, QLineEdit, QLabel, QCheckBox, QMenuBar, QAction, \
                            QFileDialog, QApplication

from AaronTools.const import VDW_RADII, BONDI_RADII
from AaronTools.substituent import Substituent

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec


class _SterimolSettings(Settings):

    AUTO_SAVE = {
        "radii": "UMN",
        "display_radii": Value(True, BoolArg),
        "display_vectors": Value(True, BoolArg),
        "include_header": Value(True, BoolArg),
        "include_header": Value(True, BoolArg),
        "delimiter": "comma",
    }

class Sterimol(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    help = "https://github.com/QChASM/SEQCROW/wiki/Sterimol-Tool"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        
        self.settings = _SterimolSettings(self.session, name)
        
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout()

        self.radii_option = QComboBox()
        self.radii_option.addItems(["Bondi", "UMN"])
        ndx = self.radii_option.findText(self.settings.radii, Qt.MatchExactly)
        self.radii_option.setCurrentIndex(ndx)
        layout.addRow("radii:", self.radii_option)
        
        self.display_vectors = QCheckBox()
        self.display_vectors.setChecked(self.settings.display_vectors)
        layout.addRow("show vectors:", self.display_vectors)
        
        self.display_radii = QCheckBox()
        self.display_radii.setChecked(self.settings.display_radii)
        layout.addRow("show radii:", self.display_radii)
        
        calc_sterimol_button = QPushButton("calculate parameters")
        calc_sterimol_button.clicked.connect(self.calc_sterimol)
        layout.addRow(calc_sterimol_button)
        
        self.l_box = QLineEdit()
        layout.addRow(QLabel("L"), self.l_box) 
        
        self.b1_box = QLineEdit()
        layout.addRow(QLabel("B<sub>1</sub>"), self.b1_box)
        
        self.b5_box = QLineEdit()
        layout.addRow(QLabel("B<sub>5</sub>"), self.b5_box)
        
        menu = QMenuBar()
        
        export = menu.addMenu("&Export")
        copy = QAction("&Copy CSV to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_csv)
        shortcut = QKeySequence(Qt.CTRL + Qt.Key_C)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        
        save = QAction("&Save CSV...", self.tool_window.ui_area)
        save.triggered.connect(self.save_csv)
        #this shortcut interferes with main window's save shortcut
        #I've tried different shortcut contexts to no avail
        #thanks Qt...
        #shortcut = QKeySequence(Qt.CTRL + Qt.Key_S)
        #save.setShortcut(shortcut)
        #save.setShortcutContext(Qt.WidgetShortcut)
        export.addAction(save)

        delimiter = export.addMenu("Delimiter")
        
        comma = QAction("comma", self.tool_window.ui_area, checkable=True)
        comma.setChecked(self.settings.delimiter == "comma")
        comma.triggered.connect(lambda *args, delim="comma": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(comma)
        
        tab = QAction("tab", self.tool_window.ui_area, checkable=True)
        tab.setChecked(self.settings.delimiter == "tab")
        tab.triggered.connect(lambda *args, delim="tab": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(tab)
        
        space = QAction("space", self.tool_window.ui_area, checkable=True)
        space.setChecked(self.settings.delimiter == "space")
        space.triggered.connect(lambda *args, delim="space": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(space)
        
        semicolon = QAction("semicolon", self.tool_window.ui_area, checkable=True)
        semicolon.setChecked(self.settings.delimiter == "semicolon")
        semicolon.triggered.connect(lambda *args, delim="semicolon": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(semicolon)
        
        add_header = QAction("&Include CSV header", self.tool_window.ui_area, checkable=True)
        add_header.setChecked(self.settings.include_header)
        add_header.triggered.connect(self.header_check)
        export.addAction(add_header)
        
        comma.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        comma.triggered.connect(lambda *args, action=space: action.setChecked(False))
        comma.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        tab.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        tab.triggered.connect(lambda *args, action=space: action.setChecked(False))
        tab.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        space.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        space.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        space.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        semicolon.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        semicolon.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        semicolon.triggered.connect(lambda *args, action=space: action.setChecked(False))

        menu.setNativeMenuBar(False)
        layout.setMenuBar(menu)
        
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def calc_sterimol(self, *args):
        selection = selected_atoms(self.session)
        if len(selection) == 0:
            self.session.logger.warning("nothing selected")
            return
        
        model = selection[0].structure
        
        end = None

        for atom in selection:
            for bond in atom.bonds:
                atom2 = bond.other_atom(atom)
                if atom2 not in selection:
                    if end is not None:
                        self.session.logger.error("substituent can only have one bond to the rest of the molecule")
                        return
                    end = atom2


        if end is None:
            self.session.logger.error("atom the substituent is attached to must not be selected")

        self.settings.radii = self.radii_option.currentText()
        self.settings.display_radii = self.display_radii.checkState() == Qt.Checked
        self.settings.display_vectors = self.display_vectors.checkState() == Qt.Checked

        convert_residues = set(atom.residue for atom in selection)
        rescol = ResidueCollection(model, convert_residues=convert_residues)
        substituent_atoms = rescol.find([AtomSpec(atom.atomspec) for atom in selection])
        end_atom = rescol.find_exact(AtomSpec(end.atomspec))[0]
        sub = Substituent(substituent_atoms, end=end_atom, detect=False)
        
        radii = self.radii_option.currentText().lower()
        
        l_start, l_end = sub.sterimol("L", return_vector=True, radii=radii)
        l = np.linalg.norm(l_end - l_start)

        b1_start, b1_end = sub.sterimol("B1", return_vector=True, radii=radii)
        b1 = np.linalg.norm(b1_end - b1_start)
        
        b5_start, b5_end = sub.sterimol("B5", return_vector=True, radii=radii)
        b5 = np.linalg.norm(b5_end - b5_start)
        
        s = ""
        if self.display_vectors.checkState() == Qt.Checked:
            s += ".color black\n"
            s += ".note Sterimol B1\n"
            s += ".arrow %6.3f %6.3f %6.3f   %6.3f %6.3f %6.3f   0.1 0.25 %f\n" % (*b1_start, *b1_end, b1/(b1 + 0.75))
            s += ".color red\n"
            s += ".note Sterimol B5\n"
            s += ".arrow %6.3f %6.3f %6.3f   %6.3f %6.3f %6.3f   0.1 0.25 %f\n" % (*b5_start, *b5_end, b5/(b5 + 0.75))
            s += ".color blue\n"
            s += ".note Sterimol L\n"
            s += ".arrow %6.3f %6.3f %6.3f   %6.3f %6.3f %6.3f   0.1 0.25 %f\n" % (*l_start, *l_end, l/(l + 0.75))
        
        if self.display_radii.checkState() == Qt.Checked:
            s += ".transparency 75\n"
            color = None
            for atom in selection:
                if radii == "umn":
                    r = VDW_RADII[atom.element.name]
                elif radii == "bondi":
                    r = BONDI_RADII[atom.element.name]
                
                if color is None or atom.color != color:
                    color = atom.color
                    rgb = [x/255. for x in atom.color]
                    rgb.pop(-1)
                    
                    s += ".color %f %f %f\n" % tuple(rgb)
                
                s += ".sphere %f %f %f %f\n" % (*atom.coord, r)
        
        if self.display_radii.checkState() == Qt.Checked or self.display_vectors.checkState() == Qt.Checked:
            stream = BytesIO(bytes(s, "utf-8"))
            bild_obj, status = read_bild(self.session, stream, "Sterimol")
            
            self.session.models.add(bild_obj, parent=model)
        
        self.l_box.setText("%.2f" % l)
        self.b1_box.setText("%.2f" % b1)
        self.b5_box.setText("%.2f" % b5)
    
    def header_check(self, state):
        """user has [un]checked the 'include header' option on the menu"""
        if state:
            self.settings.include_header = True
        else:
            self.settings.include_header = False

    def get_csv(self):
        if self.settings.delimiter == "comma":
            delim = ","
        elif self.settings.delimiter == "space":
            delim = " "
        elif self.settings.delimiter == "tab":
            delim = "\t"
        elif self.settings.delimiter == "semicolon":
            delim = ";"
            
        if self.settings.include_header:
            s = delim.join(["L", "B1", "B5"])
            s += "\n"
        else:
            s = ""
        
        s += delim.join([x.text() for x in [self.l_box, self.b1_box, self.b5_box]])
        s += "\n"
        
        return s
    
    def copy_csv(self):
        app = QApplication.instance()
        clipboard = app.clipboard()
        csv = self.get_csv()
        clipboard.setText(csv)
        self.session.logger.status("copied to clipboard")

    def save_csv(self):
        """save data on current tab to CSV file"""
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
        if filename:
            s = self.get_csv()
   
            with open(filename, 'w') as f:
                f.write(s.strip())
                
            self.session.logger.status("saved to %s" % filename)
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
