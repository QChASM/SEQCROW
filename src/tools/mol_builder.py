import os.path
import pathlib
import re
import ssl
from random import uniform
from time import perf_counter

import numpy as np
from scipy.spatial.distance import pdist

from AaronTools.atoms import Atom, BondOrder
from AaronTools.config import Config
from AaronTools.fileIO import FileReader
from AaronTools.geometry import CACTUS_HOST
from AaronTools.theory import Theory, OptimizationJob
from AaronTools.const import SATURATION, CONNECTIVITY, RADII, UNIT, EIJ, RIJ
from AaronTools.internal_coordinates import InternalCoordinateSet, Torsion
from AaronTools.utils.utils import shortest_path, fibonacci_sphere

from chimerax.core.commands import run
from chimerax.ui import HtmlToolInstance

from SEQCROW.jobs import SQMJob
from SEQCROW.managers.filereader_manager import apply_seqcrow_preset
from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.selectors import prune_branches

DEFAULT_CONFIG = Config(quiet=True)

#TODO: turn this into a setting on the menu instead of 
# AaronTools config
if not DEFAULT_CONFIG["DEFAULT"].getboolean("local_only"):
    import urllib.parse
    from urllib.request import urlopen
    from urllib.error import HTTPError

"""
I was hoping for a python 2D builder, but all the ones I found were based on RDKit
the RDKit that is available on pypi doesn't work with the Qt that comes with ChimeraX
it relies on SVG, which our Qt doesn't have a module for
I think it also wasn't available for windows (or maybe the editor that uses rdkit
isn't available for windows)
so I tried to make my own, but that wasn't going well
lines were jagged, you can't draw double bonds yet, hydrogens don't move
like they need to
but this is it, in case I need it again
possibly just a reference for putting drawings on an interactable graphics scene
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

    help = "https://github.com/QChASM/SEQCROW/wiki/2D-Builder"
    CUSTOM_SCHEME = ["editor", "cxcmd"]
    SESSION_ENDURING = False
    SESSION_SAVE = False
    PLACEMENT = None
    
    def __init__(self, session, name):       
        super().__init__(session, name, size_hint=(475, 450))

        self.display_name = "2D Builder"
        if DEFAULT_CONFIG["DEFAULT"].getboolean("local_only"):
            self.session.logger.error(
                "this tool will not work while 'local_only' is enabled in your AaronTools config\n"
                "please disable 'local_only' in your AaronTools config and restart ChimeraX"
            )

        self._build_ui()

    def _build_ui(self):
        html_file = os.path.join(os.path.dirname(__file__), "../ChemDoodleWebComponents/editor.html")
        self.html_view.setUrl(pathlib.Path(html_file).as_uri())

    def handle_scheme(self, url):
        query = urllib.parse.parse_qs(url.query())

        # tool has URL's to acknowledge how we get the structure
        # clicking those opens these links
        if "link" in query:
            link = query["link"][0]
            if link == "AmberTools":
                run(self.session, "open \"https://ambermd.org/AmberTools.php\"")
            elif link == "NCI/CADD":
                run(self.session, "open \"https://cactus.nci.nih.gov/\"")
            return

        # this is the 2D mol file that we will convert to a 3D structure
        # as some point in the HTML file, spaces are turned into sPaCe so they don't get nuked
        molfile = query["molfile"][0].replace("sPaCe", " ").replace("\\n", "\n")
        mol3file = query["mol3file"][0].replace("sPaCe", " ").replace("\\n", "\n")
        center_x = float(query["x"][0])
        center_y = float(query["y"][0])
        center_z = float(query["z"][0])
        target_destination = np.array([center_x, center_y, center_z])
        # copy-paste from AaronTools.from_string
        # instead of smiles, we have a file
        url = "https://cactus.nci.nih.gov/cgi-bin/translate.tcl?smiles=&format=sdf&astyle=kekule&dim=3D&file=%s" % urllib.parse.quote_plus(molfile)
        try:
            print("getting structure")
            s_sd_get = urlopen(url, context=ssl.SSLContext())
            msg, status = s_sd_get.msg, s_sd_get.status
            if msg != "OK":
                self.session.logger.error(
                    "Issue contacting %s for MOL lookup (status: %s)",
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
            name = query["name"][0]
            try:
                fr = FileReader((name, "sd", s_sd))
            except Exception:
                self.session.logger.error(
                    "failed to open structure: %s\n\n%s" % (
                        molfile, s_sd
                    )
                )
                return

            rescol = ResidueCollection(fr)

        except (AttributeError, HTTPError):
            for line in mol3file.splitlines():
                if re.search("COUNTS", line):
                    n_atoms = int(line.split()[3])
                    if n_atoms > 99:
                        self.session.logger.info("structure in V3000 format:")
                        self.session.logger.info("<pre>" + mol3file + "</pre>", is_html=True)
                        self.session.logger.info("structure in V2000 format:")
                        self.session.logger.info("<pre>" + molfile + "</pre>", is_html=True)
                        self.session.logger.error(
                            "structure may be too large to fetch using the CACTUS web API. "
                            "try uploading the V2000 mol file printed in the log to https://cactus.nci.nih.gov/translate/\n"
                            "select 'MOL' or 'SDF' as the output, and also select '3D' to generate 3D coordinates\n"
                            "alternatively, trim parts of your 2D structure and then add the parts you trimmed in ChimeraX using other structure editing tools"
                        )
            self.session.logger.error(
                "Structure could not be generated by the NCI CACTUS web API. "
                "Check your structure for errors"
            )

            return


        if fr is None:
            self.session.logger.warning("structure was not generated using CACTUS - it might suck!")

        rescol.coords += target_destination - rescol.COM(mass_weight=False)
        # if not optimization was requested, open the new molecule
        if query["method"][0] == "no":
            struc = rescol.get_chimera(self.session, filereader=fr)
            self.session.models.add([struc])
            apply_seqcrow_preset(
                struc, fallback="Ball-Stick-Endcap",
            )
            return
        
        # if optimization was requested, run the SQM job with auto_open=True
        theory = Theory(
            method=query["method"][0],
            charge=fr.other["charge"],
            job_type=OptimizationJob(),
        )
        
        job = SQMJob(
            name, self.session, theory, rescol, auto_open=True,
        )
        self.session.logger.info(
            "structure will appear when optimization completes"
        )
        self.session.logger.status(
            "structure will appear when optimization completes"
        )
        self.session.seqcrow_job_manager.add_job(job)

    def gen_structure(self, mol3file):
        # this generates kind of bad structures and takes a long time
        # hence, it isn't used
        atoms = []
        bond_orders = []
        reading_atoms = False
        reading_bonds = False
        # read structure
        code_to_order = {
            "4": "1.5",
        }
        for line in mol3file.splitlines():
            if "END BOND" in line:
                reading_bonds = False
            if "END ATOM" in line:
                reading_atoms = False
                
            if reading_atoms:
                info = line.split()
                atoms.append(Atom(
                    element=info[3],
                    coords=info[4:7]
                ))
                if charge := re.search("CHG=(-?\d+)", line):
                    atoms[-1].charge = int(charge.group(1))
                else:
                    atoms[-1].charge = 0
            
            if reading_bonds:
                info = line.split()
                ndx1 = int(info[4]) - 1
                ndx2 = int(info[5]) - 1
                atoms[ndx1].connected.add(atoms[ndx2])
                atoms[ndx2].connected.add(atoms[ndx1])
                try:
                    order = code_to_order[info[3]]
                except KeyError:
                    order = info[3]
                bond_orders.append((ndx1, ndx2, order))
                
            if cfg := re.search("CFG=(\d)", line):
                if cfg.group(1) == "1":
                    atoms[ndx2].coords[2] += 0.75
                elif cfg.group(1) == "2":
                    atoms[ndx2].coords[2] -= 0.75

            if "BEGIN BOND" in line:
                reading_bonds = True
            if "BEGIN ATOM" in line:
                reading_atoms = True

        # add Hs to atoms that need them
        # they'll be in the wrong spot
        added_atoms = []
        for i, atom in enumerate(atoms):
            expected_bonds = len(atom.connected)
            try:
                expected_bonds = SATURATION[atom.element]
            except KeyError:
                pass
            
            # TODO: lone pairs?
            add_Hs = expected_bonds - abs(atom.charge)
            for bond in bond_orders:
                if i == bond[0] or i == bond[1]:
                    add_Hs -= float(bond[2])
            add_Hs = int(add_Hs)
            for _ in range(0, add_Hs):
                coords = np.array([uniform(-1, 1), uniform(-1, 1), uniform(-0.1, 0.1)])
                coords /= np.linalg.norm(coords)
                coords += atom.coords
                bond_orders.append((i, len(atoms) + len(added_atoms), "1"))
                added_atoms.append(Atom(
                    element="H", coords=coords
                ))
                atoms[i].connected.add(added_atoms[-1])
                added_atoms[-1].connected.add(atoms[i])
        
        atoms.extend(added_atoms)
        geom = ResidueCollection(atoms, refresh_connected=False, refresh_ranks=False)
        geom.coords *= 1.4
        # crappy force field
        start = perf_counter()
        top = Topology(geom, bond_orders)
        stop = perf_counter()
        print("generating topology took", stop - start)
        
        atoms_that_matter = geom.find(NotAny(added_atoms))
        min_e = top.calculate_energy()
        start = perf_counter()
        # kind of fix where the Hs are
        for i in range(0, 4):
            for atom in added_atoms:
                anchor = next(iter(atom.connected))
                if i > 0 and [a.element for a in anchor.connected].count("H") < i:
                    continue
                
                best_coords = atom.coords
                for bond in top.bonds:
                    if geom.atoms[bond[0].atom1] is atom or geom.atoms[bond[0].atom2] is atom:
                        r0 = bond[1]
                
                pts = fibonacci_sphere(
                    radius=r0,
                    center=anchor.coords,
                    num=20,
                )
                d = cdist(geom.coordinates(atoms_that_matter), pts, "sqeuclidean")
                pt_filter = np.argmin(d, axis=0) == geom.atoms.index(anchor)
                pts = pts[pt_filter]
                coords_that_matter = geom.coordinates(NotAny(atom))
                for pt in pts:
                    atom.coords = pt
                    r = np.linalg.norm(coords_that_matter - atom.coords, axis=1)
                    if np.any(r < 1e-1):
                        continue
                    nrg = top.calculate_energy()
                    if np.isnan(nrg):
                        continue
                    if min_e is None or nrg < min_e:
                        min_e = nrg
                        best_coords = pt
                
                if min_e is not None:
                    atom.coords = best_coords
    
        stop = perf_counter()
        print("placing Hs took", stop - start)

        max_step = 0.2
        prev_step = np.zeros((geom.num_atoms, 3))
        momentum_ratio = 0.35
        prev_coords = geom.coords
        for i in range(0, 350):
            force = top.calculate_forces()
            norms = np.linalg.norm(force, axis=1)
            if max(norms) > max_step:
                force *= max_step / max(norms)
            
            dx = (1 - momentum_ratio) * force + momentum_ratio * prev_step
            prev_step = dx
            
            geom.coords += dx
        
        geom.coords -= geom.COM()
    
        stop = perf_counter()
        print("optimization took", stop - start)
        
        return geom


class Topology:
    def __init__(self, geom, bond_orders):
        self.geom = geom
        self.bonds = []
        self.angles = []
        self.torsions = []
        self.oops = []
        self.non_bonded = {}
        self.fudge_factors = {}
        ndx = {a: i for i, a in enumerate(geom.atoms)}
        
        bond_order_mat = np.zeros((geom.num_atoms, geom.num_atoms))
        for bond in bond_orders:
            bond_order_mat[bond[0]][bond[1]] = float(bond[2])
            bond_order_mat[bond[1]][bond[0]] = float(bond[2])

        # find rings and see if they are aromatic
        # the structure is probably kekulized and 
        # we want to change it to 1.5 order bonds
        graph = [
            [ndx[j] for j in i.connected] for i in geom.atoms
        ]
        
        prune_branches(graph)
        
        ring_atoms = set()
        for a in range(0, len(graph)):
            if not graph[a]:
                continue
            
            if a in ring_atoms:
                continue
            
            found_ring = False
            for a2 in graph[a]:
                if found_ring and a2 in ring_atoms:
                    continue
                graph[a].remove(a2)
                path = shortest_path(graph, a, a2)
                if path is not None:
                    ring_atoms.update(path)
                    found_ring = True
                    graph[a].append(a2)
                    ring_bonds = []
                    ring_lps = []
                    prev_atom = a2
                    for x in path:
                        ring_bonds.append(bond_order_mat[prev_atom, x])
                        ring_lps.append(
                            CONNECTIVITY[geom.atoms[x].element] - np.sum(bond_order_mat[x])
                        )
                        prev_atom = x
                    print("====== found a ring ======")
                    print(ring_bonds, ring_lps)
                    prev = None
                    for lp, bo in zip(ring_lps, ring_bonds):
                        x = lp + bo
                        print(x)
                        if prev is None:
                            prev = x
                            continue
                        if prev == x or bo > 2 or bo < 1:
                            print("not aromatic", x, prev)
                            break
                        prev = x
                    else:
                        prev_atom = a2
                        for x in path:
                            bond_order_mat[prev_atom, x] = 1.5
                            bond_order_mat[x, prev_atom] = 1.5
                            prev_atom = x
                else:
                    graph[a2].remove(a)

            if not found_ring:
                for a2 in graph[a]:
                    graph[a2].remove(a)
                graph[a] = []
                prune_branches(graph)

        print("====== atoms in rings:", ring_atoms)
        print(bond_order_mat)
        
        bo = BondOrder()

        visited = dict()
        nb_14 = dict()

        self.ric = InternalCoordinateSet(geom, torsion_type="all", oop_type="yes")
        
        bond_k = 40000
        angle_k = 80000
        torsion_k = 1500
        oop_k = 50000
        
        for bond in self.ric.coordinates["bonds"]:
            key = bo.key(geom.atoms[bond.atom1].element, geom.atoms[bond.atom2].element)
            r0 = RADII[geom.atoms[bond.atom1].element] + RADII[geom.atoms[bond.atom2].element]
            bo.bonds[key]["%.1f" % bond_order_mat[bond.atom1][bond.atom2]]
            try:
                r0 = bo.bonds[key]["%.1f" % bond_order_mat[bond.atom1][bond.atom2]]
                print("found bond order data", key, r0)
            except KeyError:
                print("guessing")
                pass
            self.bonds.append([bond, r0, bond_k])
            
            visited.setdefault(bond.atom1, set([]))
            visited[bond.atom1].add(bond.atom2)
            visited.setdefault(bond.atom2, set([]))
            visited[bond.atom2].add(bond.atom1)

        for angle in self.ric.coordinates["angles"]:
            p_contribution = 3
            for a in geom.atoms[angle.atom2].connected:
                p_contribution -= (bond_order_mat[angle.atom2][ndx[a]] - 1)
    
            ideal_angle = 109.5
            if p_contribution < 1.5:
                ideal_angle = 180.0
            if p_contribution >= 1.5 and p_contribution < 3:
                ideal_angle = 120.0
            print(p_contribution, ideal_angle)
    
            self.angles.append((angle, np.deg2rad(ideal_angle), angle_k))
            
            visited.setdefault(angle.atom1, set([]))
            visited[angle.atom1].add(angle.atom2)
            visited[angle.atom1].add(angle.atom3)
            visited.setdefault(angle.atom2, set([]))
            visited[angle.atom2].add(angle.atom1)
            visited[angle.atom2].add(angle.atom3)
            visited.setdefault(angle.atom3, set([]))
            visited[angle.atom3].add(angle.atom1)
            visited[angle.atom3].add(angle.atom2)

        graph = [
            [ndx[j] for j in i.connected] for i in geom.atoms
        ]
        
        for torsion in self.ric.coordinates["torsions"]:
            if geom.atoms[torsion.group1[0]] == "H" and geom.atoms[torsion.group2[0]] == "H":
                continue
            p1_contribution = 3
            for a in geom.atoms[torsion.atom1].connected:
                p1_contribution -= (bond_order_mat[torsion.atom1][ndx[a]] - 1)
            p2_contribution = 3
            for a in geom.atoms[torsion.atom2].connected:
                p2_contribution -= (bond_order_mat[torsion.atom2][ndx[a]] - 1)

            ideal_angle = 0
            periodicity = 1
            path = shortest_path(graph, torsion.atom1, torsion.atom2)
            if p1_contribution == p2_contribution and p1_contribution == 2:
                # allene crap
                if len(path) % 2 == 0:
                    ideal_angle = 180
                else:
                    ideal_angle = 90
                periodicity = 2
            elif p1_contribution == 3 or p2_contribution == 3:
                ideal_angle = 60
                periodicity = 3
            
            self.torsions.append([torsion, np.deg2rad(ideal_angle), periodicity, torsion_k])
            
            if len(path) == 2:
                for a1 in torsion.group1:
                    visited.setdefault(a1, set([]))
                    nb_14.setdefault(a1, set([]))
                    for a2 in torsion.group2:
                        visited[a1].add(a2)
                        nb_14[a1].add(a2)
                for a1 in torsion.group2:
                    visited.setdefault(a1, set([]))
                    nb_14.setdefault(a1, set([]))
                    for a2 in torsion.group1:
                        visited[a1].add(a2)
                        nb_14[a1].add(a2)
            else:
                for a1 in torsion.group1:
                    fudge_atoms = geom.find(BondsFrom(geom.atoms[a1], 3))
                    visited.setdefault(a1, set([]))
                    nb_14.setdefault(a1, set([]))
                    visited[a1] = visited[a1] | set(fudge_atoms)
                    nb_14[a1] = nb_14[a1] | set(fudge_atoms)

        for atom in self.geom.atoms:
            if len(atom.connected) != 3:
                continue
            p_contribution = 3
            for a in atom.connected:
                p_contribution -= (bond_order_mat[ndx[atom]][ndx[a]] - 1)
            
            if p_contribution != 2:
                continue
            
            a1, a2, a3 = atom.connected
            oop = Torsion([ndx[a1]], ndx[a2], ndx[a3], [ndx[atom]], improper=True)
            self.oops.append([oop, 0, oop_k])
            if not any(oop == ric_oop for ric_oop in self.ric.coordinates["out of plane bends"]):
                self.ric.coordinates["out of plane bends"].append(oop)
    
        non_bonded = dict()
        for i in range(0, geom.num_atoms):
            non_bonded.setdefault(i, set([]))
            for j in range(0, i):
                if j in visited:
                    continue
                non_bonded[i].add(j)

        self.non_bonded = non_bonded
        self.nb_14 = nb_14

    def calculate_forces(self):
        grad = np.zeros(3 * self.geom.num_atoms)
        coords = self.geom.coords
        for bond in self.bonds:
            grad += (
                bond[0].s_vector(coords) * (
                    bond[1] - bond[0].value(coords)
                ) * bond[2]
            )

        for angle in self.angles:
            grad += (
                angle[0].s_vector(coords) * (
                    angle[1] - angle[0].value(coords)
                ) * angle[2]
            )

        for torsion in self.torsions:
            grad += (
                torsion[0].s_vector(coords) * (
                    -torsion[2] * np.sin(torsion[2] * (torsion[0].value(coords) - torsion[1]))
                )
            )

        for oop in self.oops:
            val = oop[0].value(coords)
            if val > np.pi / 2:
                val = np.pi - val
            grad -= oop[0].s_vector(coords) * (
                oop[2] * val
            )

        grad = np.reshape(grad, (self.geom.num_atoms, 3))
        
        r = pdist(coords)
        for i in self.non_bonded:
            for j in self.non_bonded[i]:
                a, b = sorted([i, j])
                r_ij = r[self.geom.num_atoms * i + j - ((i + 2) * (i + 1)) // 2]
                try:
                    eps_ij = EIJ[self.geom.atoms[i].element + self.geom.atoms[j].element]
                    eps_ij /= UNIT.HART_TO_KCAL
                    sig_ij = RIJ[self.geom.atoms[i].element + self.geom.atoms[j].element]
                except:
                    continue
                
                e_r2 = (sig_ij / r_ij) ** 2
                e_r6 = e_r2 ** 3
                
                f = 12 * eps_ij * e_r6 * (e_r6 - 0.5) / r_ij
                e_ij = (coords[j] - coords[i]) / r_ij
                grad += f * e_ij 
        
        for i in self.nb_14:
            for j in self.nb_14[i]:
                a, b = sorted([i, j])
                r_ij = r[self.geom.num_atoms * i + j - ((i + 2) * (i + 1)) // 2]
                try:
                    eps_ij = EIJ[self.geom.atoms[i].element + self.geom.atoms[j].element]
                    eps_ij /= UNIT.HART_TO_KCAL
                    sig_ij = RIJ[self.geom.atoms[i].element + self.geom.atoms[j].element]
                except:
                    continue
                
                e_r2 = (sig_ij / r_ij) ** 2
                e_r6 = e_r2 ** 3
                
                f = 6 * eps_ij * e_r6 * (e_r6 - 0.5) / r_ij
                e_ij = (coords[j] - coords[i]) / r_ij
                grad += f * e_ij 
        
        return grad
    
    def calculate_energy(self, ignore=None):
        nrg = 0
        coords = self.geom.coords
        for bond in self.bonds:
            nrg += 0.5 * (
                bond[1] - bond[0].value(coords)
            ) ** 2 * bond[2]

        # print("bonds done", nrg)

        for angle in self.angles:
            nrg += 0.5 * (
                angle[1] - angle[0].value(coords)
            ) ** 2 * angle[2]
        
        # print("angles done", nrg)

        for torsion in self.torsions:
            nrg += (
                np.cos(torsion[2] * (torsion[0].value(coords) - torsion[1]))
            )
        
        # print("torsions done", nrg)

        for oop in self.oops:
            val = oop[0].value(coords)
            if val > np.pi / 2:
                val = np.pi - val
            nrg += 0.5 * oop[2] * val ** 2
        
        # print("oops done", nrg)

        r = pdist(coords)
        for i in self.non_bonded:
            for j in self.non_bonded[i]:
                a, b = sorted([i, j])
                r_ij = r[self.geom.num_atoms * i + j - ((i + 2) * (i + 1)) // 2]
                try:
                    eps_ij = EIJ[self.geom.atoms[i].element + self.geom.atoms[j].element]
                    eps_ij /= UNIT.HART_TO_KCAL
                    sig_ij = RIJ[self.geom.atoms[i].element + self.geom.atoms[j].element]
                except:
                    continue
                
                e_r2 = (sig_ij / r_ij) ** 2
                e_r6 = e_r2 ** 3
                e_r12 = e_r6 ** 2
                
                e = eps_ij * e_r6 * (e_r6 - 1)
                nrg += e
        
        # print("nb done", nrg)

        for i in self.nb_14:
            for j in self.nb_14[i]:
                a, b = sorted([i, j])
                r_ij = r[self.geom.num_atoms * i + j - ((i + 2) * (i + 1)) // 2]
                try:
                    eps_ij = EIJ[self.geom.atoms[i].element + self.geom.atoms[j].element]
                    eps_ij /= UNIT.HART_TO_KCAL
                    sig_ij = RIJ[self.geom.atoms[i].element + self.geom.atoms[j].element]
                except:
                    continue
                
                e_r2 = (sig_ij / r_ij) ** 2
                e_r6 = e_r2 ** 3
                e_r12 = e_r6 ** 2
                
                e = 0.5 * eps_ij * e_r6 * (e_r6 - 1)
                nrg += e
        
        # print("nb14 done", nrg)

        return nrg


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
