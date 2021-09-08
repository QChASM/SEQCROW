import os.path
import pathlib
import re
import ssl

from AaronTools.config import Config
from AaronTools.fileIO import FileReader
from AaronTools.geometry import CACTUS_HOST

from chimerax.ui import HtmlToolInstance

from SEQCROW.managers.filereader_manager import apply_seqcrow_preset
from SEQCROW.residue_collection import ResidueCollection

DEFAULT_CONFIG = Config(quiet=True)

#TODO: turn this into a setting on the menu instead of 
# AaronTools config
if not DEFAULT_CONFIG["DEFAULT"].getboolean("local_only"):
    import urllib.parse
    from urllib.error import HTTPError
    from urllib.request import urlopen

"""
class MolGraphicsScene(QGraphicsScene):
    def __init__(self, *args, tools=None, element=None, **kwargs):
        self._tools = tools
        self._element = element
        
        self._atoms = []
        self._coordinates = np.zeros((0, 2))
        self._bonds = []
        self._click_tol = 13
        self._start_drag = None
        self._click_tol2 = self._click_tol ** 2
        self._speculative_bond = None
        self._bond_length = 32
        self._bond_width = 2
        self._down = False
        self._highlighted_item = None
        
        super().__init__(*args, **kwargs)
    
    def mousePressEvent(self, event):
        self._down = True
        point = event.scenePos()
        item = self.get_clicked_item(point)
        if item and not self._start_drag and any(atom[1] is item[1] for atom in self._atoms):
            self._start_drag = item[1]
        tool_id = self._tools.downId()
        if tool_id == 1:
            self.draw_new_bond(self._start_drag, point, speculative=True)
        print("click")
    
    def mouseMoveEvent(self, event):
        point = event.scenePos()
        
        if self._highlighted_item:
            self.removeItem(self._highlighted_item)
            self._highlighted_item = None
        
        tool_id = self._tools.downId()
        if tool_id != 1:
            return
            
        item = self.get_clicked_item(point)
        if item and any(atom[1] is item[1] for atom in self._atoms):
            self.highlight_atom(item[1])
        elif item and any(bond[2] is item[1] for bond in self._bonds):
            self.highlight_bond(item[1])

        if not self._start_drag:
            return
        if self._down and item and not self._start_drag and any(atom[1] is item[1] for atom in self._atoms):
            self._start_drag = item[1]
        self.draw_new_bond(self._start_drag, point, speculative=True)
    
    def mouseReleaseEvent(self, event):
        
        if self._highlighted_item:
            self.removeItem(self._highlighted_item)
            self._highlighted_item = None
        
        self._down = False
        point = event.scenePos()
        tool_id = self._tools.downId()
        if tool_id == 0:
            if len(self._coordinates) == 0:
                self.add_atom(self._element.text(), point)
            else:
                item = self.get_clicked_item(point)
                print("clicked item", item)
                if item and not any(atom[1] is item[1] for atom in self._atoms):
                    return
                if item:
                    self.change_element(item[1], self._element.text())
            print("atom")
        if tool_id == 1:
            print("bond")
            item = self.get_clicked_item(point)
            print("clicked item", item)
            if item and any(atom[1] is item[1] for atom in self._atoms):
                self.draw_new_bond(item[1], point)
            elif item:
                self.increase_bond_order(item[2])
            else:
                self.draw_new_bond_to_nowhere(point)
            
        elif tool_id == 2:
            print("eraser")
            item = self.get_clicked_item(point)
            print("clicked item", item)
            if item and any(atom[1] is item[1] for atom in self._atoms):
                self.erase_atom(item[1])
            elif item:
                self.erase_bond(item[2])

        if self._speculative_bond:
            self.removeItem(self._speculative_bond)
            self._speculative_bond = None
        self._start_drag = None

        print("unclick")

    def highlight_atom(self, atom):
        ndx = 0
        for i, a in enumerate(self._atoms):
            if a[1] is atom:
                ndx = i
                break
        if self._coordinates.ndim == 1:
            x, y = self._coordinates
        else:
            x, y = self._coordinates[ndx]
        
        self._highlighted_item = self.addEllipse(
                x - self._click_tol / 2,
                y - self._click_tol / 2,
                self._click_tol,
                self._click_tol,
                brush=QBrush(Qt.green),
            )

    def highlight_bond(self, bond):
        ndx = 0
        for i, b in enumerate(self._bonds):
            if b[2] is bond:
                ndx = i
                break

        v1 = self._coordinates[self._bonds[ndx][0]]
        v2 = self._coordinates[self._bonds[ndx][1]]
        
        pen = QPen(QBrush(Qt.green), self._click_tol)
        self._highlighted_item = self.addLine(
                v1[0], v1[1], v2[0], v2[1], pen=pen,
            )

    def increase_bond_order(self, bond):
        pass

    def get_clicked_item(self, point):
        if len(self._coordinates) < 1:
            return None
        click_coords = np.array([point.x(), point.y()])
        
        clicked_atom = self.get_clicked_atom(click_coords)
        clicked_bond = self.get_clicked_bond(click_coords)
        if not clicked_atom and not clicked_bond:
            return None
        if clicked_atom and not clicked_bond:
            return clicked_atom[1]
        if clicked_bond and not clicked_atom:
            return clicked_bond[1]
        return sorted([clicked_atom, clicked_bond], key=lambda x: x[0])[0][1]

    def get_clicked_atom(self, click_coords):
        diff = self._coordinates - click_coords
        dist2 = np.sum(diff * diff, axis=1)
        min_d = None
        # there is one atom
        if isinstance(dist2, float):
            if dist2 < self._click_tol2:
                return (dist2, self._atoms[0])
            return None
        
        # there is more than one atom
        for atom, d in zip(self._atoms, dist2):
            if d > self._click_tol:
                continue
            if not min_d or d < min_d[0]:
                min_d = (d, atom)
        
        return min_d
    
    def get_clicked_bond(self, click_coords):
        if len(self._bonds) < 1:
            return None
        
        bond_coords = np.zeros((len(self._bonds), 2))
        for i, bond in enumerate(self._bonds):
            bond_coords[i] = (
                self._coordinates[bond[0][0]] + self._coordinates[bond[0][1]]
            ) / 2
        
        diff = bond_coords - click_coords
        dist2 = np.sum(diff * diff, axis=1)
        min_d = None
        # there is one bond
        if isinstance(dist2, float):
            if dist2 < self._click_tol2:
                return (dist2, self._bonds[0])
            return None
        
        for bond, d in zip(self._bonds, dist2):
            if d > self._click_tol:
                continue
            if not min_d or d < min_d[0]:
                min_d = (d, bond)
        
        return min_d

    def add_atom(self, element, point):
        if isinstance(point, np.ndarray):
            x, y = point
        else:
            x = point.x()
            y = point.y()
        if element != "C":
            text = element
            if element in SATURATION:
                if element == "H":
                    text = "H<sub>%i</sub>" % 2
                elif any(element == x for x in ["O", "F", "Cl", "Br", "I"]):
                    text = "hydrogen"
                    text += element
                else:
                    text += "hydrogen"
                
                if SATURATION[element] > 1:
                    text = text.replace("hydrogen", "H<sub>%i</sub>" % SATURATION[element])
                elif SATURATION[element] == 1:
                    text = text.replace("hydrogen", "H")
                else:
                    text = text.replace("hydrogen", "")
            
            atom = self.addText(text)
            atom.setHtml(text)
            rect = atom.boundingRect()
            ax = x - rect.width() / 2
            ay = y - rect.height() / 2
            atom.setPos(ax, ay)
        
        else:
            atom = self.addEllipse(
                x - self._bond_width / 2,
                y - self._bond_width / 2,
                self._bond_width,
                self._bond_width,
                brush=QBrush(Qt.black),
            )
        self._atoms.append((element, atom))
        self._coordinates = np.append(
            self._coordinates,
            np.array([[x, y]]),
            axis=0,
        )
        print(self._coordinates)

    def change_element(self, atom, element):
        ndx = 0
        for i, a in enumerate(self._atoms):
            if a[1] is atom:
                ndx = i
                break
        if self._coordinates.ndim == 1:
            x, y = self._coordinates
        else:
            x, y = self._coordinates[ndx]
        if atom:
            self.removeItem(atom)
        
        new_atom = None
        if element != "C":
            text = element
            if element in SATURATION:
                n_bonds = 0
                for bond in self._bonds:
                    if ndx in bond[0]:
                        n_bonds += bond[1]
                n_bonds = int(ceil(n_bonds))
                if element == "H":
                    if SATURATION[element] - n_bonds > 0:
                        text = "H<sub>%i</sub>" % (SATURATION[element] - n_bonds + 1)
                    else:
                        text = element
                elif any(element == x for x in ["O", "F", "Cl", "Br", "I"]):
                    text = "hydrogen"
                    text += element
                else:
                    text += "hydrogen"
                
                if SATURATION[element] - n_bonds > 1:
                    text = text.replace("hydrogen", "H<sub>%i</sub>" % (SATURATION[element] - n_bonds))
                elif SATURATION[element] - n_bonds == 1:
                    text = text.replace("hydrogen", "H")
                else:
                    text = text.replace("hydrogen", "")
            
            new_atom = self.addText(text)
            new_atom.setHtml(text)
            rect = new_atom.boundingRect()
            ax = x - rect.width() / 2
            ay = y - rect.height() / 2
            new_atom.setPos(ax, ay)
        
        else:
            for bond in self._bonds:
                if ndx in bond[0]:
                    break
            else:
                new_atom = self.addEllipse(
                    x - self._bond_width / 2,
                    y - self._bond_width / 2,
                    self._bond_width,
                    self._bond_width,
                    brush=QBrush(Qt.black),
                )
        self._atoms[ndx] = (element, new_atom)

    def draw_new_bond(self, atom, point, order=1, speculative=False):
        if self._speculative_bond:
            self.removeItem(self._speculative_bond)
        self._speculative_bond = None
        
        if not speculative and not self._start_drag and len(self._atoms) == 0:
            self.add_atom("C", point)
            return
        elif not self._start_drag:
            return

        ndx1 = None
        ndx2 = None
        for i, a in enumerate(self._atoms):
            if a[1] is self._start_drag:
                ndx1 = i
            if a[1] is atom:
                ndx2 = i

        if ndx1 == ndx2 or ndx2 is None:
            self.draw_new_bond_to_nowhere(point, order=order, speculative=speculative)
            return

        # don't draw duplicate bonds
        for bond in self._bonds:
            if ndx1 in bond[0] and ndx2 in bond[0]:
                return

        v1 = self._coordinates[ndx1]
        v2 = self._coordinates[ndx2]
        
        for bond in self._bonds:
            if ndx1 in bond[0] and ndx2 in bond[0]:
                self._bonds.remove(bond)
                break
        
        if speculative:
            brush = QBrush(Qt.lightGray)
        else:
            brush = QBrush(Qt.black)
        pen = QPen(brush, self._bond_width)
        
        new_bond = self.addLine(v1[0], v1[1], v2[0], v2[1], pen=pen)
        if speculative:
            self._speculative_bond = new_bond
            return
        
        self._bonds.append([[ndx1, ndx2], order, new_bond])
    
    def draw_new_bond_to_nowhere(self, point, order=1, speculative=False):
        if not self._start_drag:
            return
        if self._speculative_bond:
            self.removeItem(self._speculative_bond)
        self._speculative_bond = None
        
        x = point.x()
        y = point.y()
        ndx = None
        for i, a in enumerate(self._atoms):
            print(a, self._start_drag)
            if a[1] is self._start_drag:
                ndx = i
                break
        print("ndx", ndx, self._start_drag)

        v1 = np.array([x, y])
        print("dim", self._coordinates.ndim)
        print(self._coordinates)
        if self._coordinates.ndim == 1:
            v2 = self._coordinates
        else:
            v2 = self._coordinates[ndx]
        d = np.linalg.norm(v1 - v2)

        neighbors = []
        for bond in self._bonds:
            if bond[0][0] == ndx:
                neighbors.append(bond[0][1])
            elif bond[0][1] == ndx:
                neighbors.append(bond[0][0])

        p1 = v2
        if d < self._click_tol and len(neighbors) == 0:
            p2 = np.array([
                self._bond_length * np.cos(np.pi / 6),
                self._bond_length * np.sin(np.pi / 6),
            ])
            p2 += p1
        elif d < self._click_tol and len(neighbors) == 1:
            v12 = v2 - self._coordinates[neighbors[0]]
            v12 /= np.linalg.norm(v12)
            v12 *= self._bond_length
            angle = np.pi / 3
            rot = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)],
            ])
            p2 = np.dot(rot, v12)
            p2 += p1
        elif d > self._click_tol:
            v2 = np.array([x, y])
            print("finding space point", v2, p1)
            v2 -= p1
            v2 /= np.linalg.norm(v2)
            p2 = self._bond_length * v2
            p2 += p1
        else:
            print("draw bond based on neighbors")
            return
        
        test_atom = self.get_clicked_atom(p2)
        if test_atom and test_atom[1][1] is not self._start_drag:
            print("recursive", test_atom[1][1], self._start_drag)
            self.draw_new_bond(test_atom[1][1], point, order=order, speculative=speculative)
            return
        
        if speculative:
            brush = QBrush(Qt.green)
        else:
            brush = QBrush(Qt.black)
        pen = QPen(brush, self._bond_width)
        
        new_bond = self.addLine(p1[0], p1[1], p2[0], p2[1], pen=pen)
        if speculative:
            self._speculative_bond = new_bond
            return
        
        self._bonds.append([[ndx, len(self._atoms)], order, new_bond])
        self.add_atom("C", p2)
    
    def erase_atom(self, atom):
        ndx = 0
        for i, a in enumerate(self._atoms):
            if a[1] is atom:
                ndx = i
                break
        # remove atom drawing
        self.removeItem(atom)
        # remove bonds
        for bond in self._bonds[::-1]:
            if ndx in bond[0]:
                self.removeItem(bond[2])
                self._bonds.remove(bond)
                print("deleting bond", bond)
                continue
            if bond[0][0] > ndx:
                bond[0][0] -= 1
            if bond[0][1] > ndx:
                bond[0][1] -= 1
        self._atoms.pop(ndx)
        self._coordinates = np.delete(self._coordinates, ndx, axis=0)
    
    def erase_bond(self, bond):
        print(bond)
        for bond2 in self._bonds[::-1]:
            if bond is bond2[2]:
                self._bonds.remove(bond2)
                break
        self.removeItem(bond)
        

class ToolButtonGroup:
    def __init__(self, *buttons, **kwargs):
        self.buttons = buttons
        for button in self.buttons:
            button.clicked.connect(lambda *args, b=button: self.toggle_buttons(b))
    
        self.buttons[0].setDown(True)
        if not isinstance(self.buttons[0], ElementButton):
            self.buttons[0].setCheckable(True)
            self.buttons[0].setChecked(True)
        else:
            self.buttons[0].setState(ElementButton.Checked)
        
        for button in self.buttons[1:]:
            button.setDown(False)
            if not isinstance(button, ElementButton):
                button.setCheckable(True)
                button.setChecked(False)
            else:
                button.setState(ElementButton.Unchecked)
    
    def toggle_buttons(self, button):
        button.setDown(True)
        if isinstance(button, ElementButton):
            button.setState(ElementButton.Checked)
        else:
            button.setChecked(True)
        
        for button2 in self.buttons:
            if button2 is button:
                continue
            if isinstance(button2, ElementButton):
                button2.setState(ElementButton.Unchecked)
            else:
                button2.setChecked(False)
            button2.setDown(False)
    
    def downId(self):
        res = 0
        for i, button in enumerate(self.buttons):
            if button.isChecked() or (isinstance(button, ElementButton) and button.state == ElementButton.Checked):
                print(i)
                res = i
        return res
""" 
    
class MolBuilder(HtmlToolInstance):

    help = "TODO"
    CUSTOM_SCHEME = "editor"
    SESSION_ENDURING = False
    SESSION_SAVE = False
    PLACEMENT = None
    
    def __init__(self, session, name):       
        super().__init__(session, name, size_hint=(450, 450))

        self.display_name = "Tutorial — HTML-based"

        self._build_ui()

    def _build_ui(self):
        html_file = os.path.join(os.path.dirname(__file__), "../ChemDoodleWebComponents/editor.html")
        self.html_view.setUrl(pathlib.Path(html_file).as_uri())

    def handle_scheme(self, url):
        
        query = urllib.parse.parse_qs(url.query())
        
        molfile = query["molfile"][0].replace("sPaCe", " ").replace("\\n", "\n")
        url = "https://cactus.nci.nih.gov/cgi-bin/translate.tcl?smiles=&format=sdf&astyle=kekule&dim=3D&file=%s" % urllib.parse.quote_plus(molfile)
        s_sd_get = urlopen(url, context=ssl.SSLContext())
        msg, status = s_sd_get.msg, s_sd_get.status
        if msg != "OK":
            self.session.logger.error(
                "Issue contacting %s for SMILES lookup (status: %s)",
                CACTUS_HOST,
                status,
            )
            raise IOError
        s_sd_get = s_sd_get.read().decode("utf8")
        try:
            tmp_url = re.search(
                'User-defined exchange format file: <a href="(.*)"',
                s_sd_get,
            ).group(1)
        except AttributeError as err:
            if re.search("You entered an invalid MOL file", s_sd_get):
                self.session.logger.error(
                    "Invalid format encountered: %s (consult %s for syntax help)",
                    molfile,
                    "https://cactus.nci.nih.gov/translate/smiles.html",
                )
            raise IOError(err)
        new_url = "{}{}".format(CACTUS_HOST, tmp_url)
        s_sd = (
            urlopen(new_url, context=ssl.SSLContext())
            .read()
            .decode("utf8")
        )
        fr = FileReader(("new", "sd", s_sd))
        rescol = ResidueCollection(fr)
        struc = rescol.get_chimera(self.session, filereader=fr)
        self.session.models.add([struc])
        apply_seqcrow_preset(
            struc, fallback="Ball-Stick-Endcap",
        )
    # def _build_ui(self):
    #     layout = QGridLayout()
    # 
    #     self.element_button = ElementButton("C")
    #     self.element_button.setState(ElementButton.Checked)
    #     self.element_button.clicked.disconnect(self.element_button._changeState)
    #     self.element_button.clicked.connect(self.open_ptable)
    #     layout.addWidget(self.element_button, 1, 0, 1, 1, Qt.AlignLeft)
    # 
    #     bond_button = QPushButton("bond")
    #     layout.addWidget(bond_button, 1, 1, 1, 1, Qt.AlignLeft)
    # 
    #     eraser = QPushButton("eraser")
    #     layout.addWidget(eraser, 1, 2, 1, 1, Qt.AlignLeft)
    # 
    #     self.tool_box = ToolButtonGroup(
    #         self.element_button,
    #         bond_button,
    #         eraser,
    #     )
    # 
    #     self.mol_scene = MolGraphicsScene(
    #         0, 0, 400, 350, tools=self.tool_box, element=self.element_button
    #     )
    #     mol_view = QGraphicsView(self.mol_scene)
    #     layout.addWidget(mol_view, 0, 0, 1, 6)
    # 
    #     self.tool_window.ui_area.setLayout(layout)
    # 
    #     self.tool_window.manage(None)
    # 
    # def open_ptable(self):
    #     if self.tool_box.downId() != 0:
    #         return
    #     self.tool_window.create_child_window(
    #         "select element",
    #         window_class=_PTable,
    #         button=self.element_button,
    #     )
    #     self.element_button.setState(ElementButton.Checked)
