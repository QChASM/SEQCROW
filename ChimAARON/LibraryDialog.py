import Tkinter
import ChimAARON
import os

from ChimAARON.prefs import ENVIRONMENT
from CGLtk.Table import SortableTable
from chimera import openModels, Molecule, preferences, replyobj, MaterialColor
from chimera.baseDialog import ModelessDialog
from chimera.tkoptions import StringOption, IntOption, ColorOption
from ttk import Notebook

class LibraryDialogMenu(ModelessDialog):
    buttons = ("Close", )
    title = "AaronTools Libraries"
    help = ("tutorials/libraries.html", ChimAARON)

    
    def __init__(self):
        self.curFormat = None

        ModelessDialog.__init__(self)
        
    def fillInUI(self, parent):
        self.libOptions = ['Ligands', 'Substituents', 'Ring Fragments']
        
        self.libraryMenu = Notebook(parent)
                                
        self.frames = {}
        self.paramGUIs = {}
        
        #switch between ligand, substituent, and ring fragment frames with the OptionMenu
        self.frames['Ligands'] = Tkinter.Frame(self.libraryMenu)
        self.paramGUIs['Ligands'] = ligandGUI(self.frames['Ligands'])
        
        self.frames['Substituents'] = Tkinter.Frame(self.libraryMenu)
        self.paramGUIs['Substituents'] = substituentGUI(self.frames['Substituents'])
        
        self.frames['Ring Fragments'] = Tkinter.Frame(self.libraryMenu)
        self.paramGUIs['Ring Fragments'] = ringFragGUI(self.frames['Ring Fragments'])
        
        self.libraryMenu.add(self.frames['Ligands'], text="Ligands")
        self.libraryMenu.add(self.frames['Substituents'], text="Substituents")
        self.libraryMenu.add(self.frames['Ring Fragments'], text="Ring Fragments")

        self.libraryMenu.pack(fill='both')
       
class GeomLoadGUI:
    def _open_geom(self):
        """opens structures and adds decorations on key atoms, substituents, or ring fragment (if requested by child gui)"""
        from ChimAARON import AaronGeometry2ChimeraMolecule
        from chimera import openModels
        from AaronTools.geometry import Geometry
        from AaronTools.substituent import Substituent
        from AaronTools.ringfragment import RingFragment
        from AaronTools.component import Component
        
        geoms = self.table.selected()
        
        for geom in geoms:
            real_geom = geom.method(str(geom.name))

            if geom.method == Substituent:
                ChimAARON.addSub(real_geom, color=self.subColor.get(), showAttach=self.showAttach.get())
            
            elif geom.method == Component:             
                ChimAARON.addLig(real_geom, color=self.keyColor.get(), showKey=self.showKey.get())
                
            elif geom.method == RingFragment:
                ChimAARON.addRing(real_geom, color=self.walkColor.get(), showWalk=self.showWalk.get())
            
    def highlightBackbone(self, lig, mol):
        """highlight the ligand backbone"""
        from Bld2VRML import openBildString
        from chimera import openModels

        color = self.ligColor.get()
        
        r = 1.1*mol.bonds[0].radius*mol.stickScale
        
        s = ''
        
        for i, atom1 in enumerate(lig.backbone):
            for atom2 in lig.backbone[i+1:]:
                if atom2 in atom1.connected:
                    info_cyl = tuple(atom1.coords) + tuple(atom2.coords) + (r,)
                    info_sp1 = tuple(atom1.coords) + (r,)
                    info_sp2 = tuple(atom2.coords) + (r,)
                    s += ".cylinder %f %f %f   %f %f %f   %f open\n" % info_cyl
                    s += ".sphere %f %f %f   %f\n" % info_sp1
                    s += ".sphere %f %f %f   %f\n" % info_sp2
                
        mdls = openBildString(s)
        for mdl in mdls:
            mdl.color = color
            
        openModels.add(mdls, sameAs=mol)            
        
    def canOpen(self, selected):
        state = "normal"
        if len(selected) < 1:
            state = "disabled"
            
        self.loadButton.config(state=state)
      
class ligandGUI(GeomLoadGUI):
    def __init__(self, parent):
        """ligand library frame"""
        
        self.nRow = 2

        #get a table with all the ligands and ligand info in it
        self.table, self.nCol = self.getLigandTable(parent)
        
        self.table.launch(browseCmd=self.canOpen)
        self.table.grid(row=0, column=0, columnspan=self.nCol, sticky='nsew')
        self.table.rowconfigure(0, weight=1)
        self.table.columnconfigure(0, weight=1)

        #options for highlighting key atoms
        self.showKey = Tkinter.BooleanVar()
        self.showKey.set(True)
        self.showKeyButton = Tkinter.Checkbutton(parent, indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.showKey)
        self.showKeyButton.grid(row=1, column=self.nCol-1, sticky='e')
        
        self.showKeyLabel = Tkinter.Label(parent, text="Highlight key atoms")
        self.showKeyLabel.grid(row=1, column=self.nCol-2, sticky='e')
        
        self.keyColor = ColorOption(parent, 2, "Key atom highlight color", tuple((0.2, 0.5, 0.8, 0.5)), None, startCol=self.nCol-2)
        self.keyColor.stretch = True

        #open ligand button
        self.loadButton = Tkinter.Button(parent, state="disabled", pady=0, \
                                    text="Open selected ligands", \
                                    command=self._open_geom, anchor='s')
        
        self.loadButton.grid(row=3, columnspan=1+self.nCol, sticky='sew')
        
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
    
    @classmethod
    def getLigandTable(cls, parent):
        """returns a table with ligand info - name, denticity, and coordinating elements"""
        from glob import glob
        
        from AaronTools.component import Component
        from CGLtk.Table import SortableTable
        
        lig_list = glob(Component.AARON_LIBS) + glob(Component.BUILTIN)
                
        table = SortableTable(parent)
        nameCol = table.addColumn("Name", "name", format="%s")
        atomsCol = table.addColumn("Denticity", "lambda l: len(l.key_atoms)", format="%s")
        keyCol = table.addColumn("Coordinating Elements", "lambda l: ', '.join(sorted(l.key_elements))", format="%s")
        
        table.setData([PseudoGeometry(lig, Component) for lig in lig_list if lig])
        
        return (table, 3)
        
class substituentGUI(GeomLoadGUI):
    def __init__(self, parent):
        """substituent library frame"""
                
        self.nRow = 2
        
        #add the substituent table
        self.table, self.nCol = self.getSubstituentTable(parent)
        
        self.table.launch(browseCmd=self.canOpen)
        self.table.grid(row=0, column=0, columnspan=self.nCol, sticky='nsew')
        self.table.rowconfigure(0, weight=1)
        self.table.columnconfigure(0, weight=1)
        
        #options for showing where the substituent attaches
        self.showAttach = Tkinter.BooleanVar()
        self.showAttach.set(True)
        self.showAttachButton = Tkinter.Checkbutton(parent, indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.showAttach)
        self.showAttachButton.grid(row=1, column=self.nCol-1, sticky='e')
        
        self.showAttachLabel = Tkinter.Label(parent, text="Ghost attachement")
        self.showAttachLabel.grid(row=1, column=self.nCol-2)
        
        self.subColor = ColorOption(parent, 2, "Attachment color", tuple((0.60784, 0.145098, 0.70196, 0.5)), None, startCol=self.nCol-2)
        
        #button to open
        self.loadButton = Tkinter.Button(parent, state="disabled", pady=0, \
                                    text="Open selected substituents", \
                                    command=self._open_geom, anchor='s')
        
        self.loadButton.grid(row=3, columnspan=1+self.nCol, sticky='sew')        

        parent.pack()
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        
    @classmethod
    def getSubstituentTable(cls, parent):
        """returns table with substituent info - name, number of conformers, angle between conformers"""
        from glob import glob
        
        from AaronTools.substituent import Substituent
        from CGLtk.Table import SortableTable
        
        sub_list = glob(Substituent.AARON_LIBS) + glob(Substituent.BUILTIN)

        table = SortableTable(parent)
        nameCol = table.addColumn("Name", "name", format="%s")
        confCol = table.addColumn("Conformers", "conf_num", format="%i")
        anglCol = table.addColumn("Conformer Angle", "conf_angle", format="%i")

        table.setData([PseudoGeometry(sub, Substituent) for sub in sub_list if sub])         

        return (table, 3)

class ringFragGUI(GeomLoadGUI):
    def __init__(self, parent):
        """ring fragment library frame"""

        
        self.nRow = 2
        
        self.table, self.nCol = self.getRingTable(parent)

        self.table.launch(browseCmd=self.canOpen)
        self.table.grid(row=0, column=0, columnspan=3, sticky='nsew')
        self.table.rowconfigure(0, weight=1)
        self.table.columnconfigure(0, weight=1)

        #options for arrows showing the path around the ring
        self.showWalk = Tkinter.BooleanVar()
        self.showWalk.set(True)
        self.showWalkButton = Tkinter.Checkbutton(parent, indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.showWalk)
        self.showWalkButton.grid(row=1, column=1, sticky='e')
        
        self.showWalkLabel = Tkinter.Label(parent, text='Show walk direction')
        self.showWalkLabel.grid(row=1, column=0, sticky='e')
        
        self.walkColor = ColorOption(parent, 2, "Walk arrow color", tuple((0.9, 0.4, 0.3, 0.9)), None, startCol=0)
        
        self.loadButton = Tkinter.Button(parent, state="disabled", pady=0, \
                                    text="Open selected ring fragments", \
                                    command=self._open_geom, anchor='s')
        
        self.loadButton.grid(row=3, columnspan=1+self.nCol, sticky='ew')
        
        parent.pack()
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        
    @classmethod
    def getRingTable(cls, parent):
        from AaronTools.ringfragment import RingFragment
        from CGLtk.Table import SortableTable
        from glob import glob        
        
        ring_list = glob(RingFragment.AARON_LIBS) + glob(RingFragment.BUILTIN)
        
        table = SortableTable(parent)
        nameCol = table.addColumn("Name", "name", format="%s")
        
        table.setData([PseudoGeometry(ring, RingFragment) for ring in ring_list]) 
        
        return table, 1
        
class PseudoGeometry:
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

class LibAddDialog(ModelessDialog):
    title = "Add to Personal Library"
    buttons = ("Close",)
    
    def __init__(self, notebookTab=None):
        ModelessDialog.__init__(self)
        envPrefs = preferences.preferences.get('ChimAARON', ENVIRONMENT)
        if 'AARONLIB' not in envPrefs:
            raise RuntimeWarning("AARONLIB location is not set. You must set AARONLIB in the \"Set up AaronTools\" menu before adding anything to your personal library.")
        
    def fillInUI(self, parent):
        self.frames = {}
        self.libGUIs = {}
        
        self.libOptions = Notebook(parent)
        
        self.frames['Ligand'] = Tkinter.Frame(self.libOptions)
        self.libGUIs['Ligand'] = LibAddLigGUI(self.frames['Ligand'])
        
        self.frames['Substituent'] = Tkinter.Frame(self.libOptions)
        self.libGUIs['Substituent'] = LibAddSubGUI(self.frames['Substituent'])
        
        self.frames['Ring Fragment'] = Tkinter.Frame(self.libOptions)        
        self.libGUIs['Ring Fragment'] = LibAddRingGUI(self.frames['Ring Fragment'])
        
        for k in sorted(self.frames.keys()):
            self.libOptions.add(self.frames[k], text=k)
        
        self.libOptions.pack(fill='both')
        
class LibAddSubGUI:
    def __init__(self, parent):
        row = 0 
        
        self.target = StringOption(parent, row, "Target atom", "", None, balloon="OSL atom specification for substituent atom that is connected to the rest of the molecule")
        self.targetCurrentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.targetSetCurrent)
        self.targetCurrentSelectionButton.grid(row=row, column=2, sticky='ew')
        
        row += 1    
        
        self.avoid = StringOption(parent, row, "Avoid atom", "", None, balloon="OSL atom specification for molecule atom that is connected to the substituent")
        self.avoidCurrentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.avoidSetCurrent)
        self.avoidCurrentSelectionButton.grid(row=row, column=2, sticky='ew')
        
        row += 1
        
        self.nconf = IntOption(parent, row, "Number of conformers", 0, None, balloon="number of confomers to generate during conformer searches")
        
        row += 1
        
        self.confAngle = IntOption(parent, row, "Conformer angle", 0, None, balloon="rotation angle (degrees) used to generate each conformer")
        
        row += 1

        self.subName = StringOption(parent, row, "Substituent name", "", None, balloon="name of substituent\nleave blank to see the substituent before adding it to the library")

        row += 1

        self.overwrite = Tkinter.BooleanVar()
        self.overwrite.set(False)
        self.overwriteCheck = Tkinter.Checkbutton(parent, indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.overwrite)
        self.overwriteCheck.grid(row=row, column=1, sticky='w')
        
        self.overwriteLabel = Tkinter.Label(parent, text="Overwrite existing")
        self.overwriteLabel.grid(row=row, column=0, sticky='e')
        
        row += 1

        self.libAddButton = Tkinter.Button(parent, pady=0, text="Add to library", command=self.libaddSub)
        self.libAddButton.grid(row=row, column=0, columnspan=2, sticky='ew')
        
        row += 1

    def targetSetCurrent(self):
        from chimera.selection import currentAtoms
        self.target.set(currentAtoms()[0].oslIdent())

    def avoidSetCurrent(self):
        from chimera.selection import currentAtoms
        self.avoid.set(currentAtoms()[0].oslIdent())

    def libaddSub(self):
        import numpy as np
        
        from AaronTools.substituent import Substituent
        from chimera.selection import OSLSelection
        
        name = self.subName.get()

        chim_target = OSLSelection(self.target.get()).atoms()[0]
        chim_avoid = OSLSelection(self.avoid.get()).atoms()[0]
        mol = chim_target.molecule
        
        geom = ChimAARON.ChimeraMolecule2AaronGeometry(mol)
        
        target = geom.atoms[mol.atoms.index(chim_target)]
        avoid = geom.atoms[mol.atoms.index(chim_avoid)]
        
        geom.coord_shift(-avoid.coords)
        
        sub = geom.get_fragment(target, avoid, as_object=True)
        
        x_axis = np.array([1., 0., 0.])
        n = np.linalg.norm(target.coords)
        vb = target.coords/n
        d = np.linalg.norm(vb - x_axis)
        
        theta = np.arccos((d**2 - 2) / -2)
        
        vx = np.cross(vb, x_axis)
        
        sub.rotate(vx, theta)
        
        sub.comment = "CF:%i,%i" % (self.nconf.get(), self.confAngle.get())

        overwrite = self.overwrite.get()

        ChimAARON.addSub(sub, name=name, overwrite=overwrite)
            
class LibAddLigGUI:
    def __init__(self, parent):
        row = 0 
        
        self.modelSelection = SortableTable(parent)
        open_mols = openModels.list(modelTypes=[Molecule])

        idCol = self.modelSelection.addColumn("ID", "lambda m: m.oslIdent()", format="%s")
        nameCol = self.modelSelection.addColumn("Name", "name", format="%s")
        
        self.modelSelection.setData(open_mols)
        self.modelSelection.launch(browseCmd=self.selectOne)
        self.modelSelection.grid(row=row, column=0, columnspan=2, sticky='nsew')
        self.modelSelection.columnconfigure(0, weight=1)
        self.modelSelection.rowconfigure(row, weight=1)

        row += 1

        self.ligName = StringOption(parent, row, "Ligand name", "", None, balloon="name of ligand\nleave blank to see the ligand before adding it to the library")
        
        row += 1

        self.overwrite = Tkinter.BooleanVar()
        self.overwrite.set(False)
        self.overwriteCheck = Tkinter.Checkbutton(parent, indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.overwrite)
        self.overwriteCheck.grid(row=row, column=1, sticky='w')
        
        self.overwriteLabel = Tkinter.Label(parent, text="Overwrite existing")
        self.overwriteLabel.grid(row=row, column=0, sticky='e')
        
        row += 1

        self.libAddButton = Tkinter.Button(parent, state="disabled", pady=0, text="Add to library", command=self.libaddLig)
        self.libAddButton.grid(row=row, column=0, columnspan=2, sticky='ew')
        
        row += 1

    def libaddLig(self):
        from AaronTools.catalyst import Catalyst 
        from AaronTools.component import Component
        
        name = self.ligName.get()
        
        mol = self.modelSelection.selected()[0]
        cat = Catalyst(ChimAARON.ChimeraMolecule2AaronGeometry(mol))
        
        if cat.center is not None:
            cat.coord_shift(-cat.COM(targets=cat.center))
            
        ligands = cat.components['ligand']
        lig_index = 0
        
        if len(ligands) > 1:
            replyobj.status("multiple ligands found")
            
        new_ligand = ligands[lig_index]
        new_ligand.comment = "K:" + ",".join([str(new_ligand.atoms.index(key) + 1) for key in new_ligand.key_atoms]) + ";"
        
        overwrite = self.overwrite.get()

        ChimAARON.addLig(new_ligand, name=name, overwrite=overwrite)
        
    def selectOne(self, models):
        state = "normal"
        print(models)
        if len(models) != 1:
            state = "disabled"
            
        self.libAddButton.config(state=state)

class LibAddRingGUI:
    def __init__(self, parent):
        row = 0 
        
        self.walk = StringOption(parent, row, "Walk atoms", "", None, balloon="OSL atom specification to define the direction to go around the ring")
        self.currentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.setCurrent)
        self.currentSelectionButton.grid(row=row, column=2, sticky='ew')  

        row += 1

        self.ringName = StringOption(parent, row, "Ring name", "", None, balloon="name of ring\nleave blank to see the ring before adding it to the library")
        
        row += 1

        self.overwrite = Tkinter.BooleanVar()
        self.overwrite.set(False)
        self.overwriteCheck = Tkinter.Checkbutton(parent, indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.overwrite)
        self.overwriteCheck.grid(row=row, column=1, sticky='w')
        
        self.overwriteLabel = Tkinter.Label(parent, text="Overwrite existing")
        self.overwriteLabel.grid(row=row, column=0, sticky='e')
        
        row += 1

        self.libAddButton = Tkinter.Button(parent, pady=0, text="Add to library", command=self.libaddRing)
        self.libAddButton.grid(row=row, column=0, columnspan=2, sticky='ew')
        
        row += 1
        
    def setCurrent(self):
        from chimera.selection import currentAtoms
        self.walk.set(" ".join([atom.oslIdent() for atom in currentAtoms()]))
        
    def libaddRing(self):
        from AaronTools.ringfragment import RingFragment
        from chimera.selection import OSLSelection

        name = self.ringName.get()
        
        chim_walk = OSLSelection(self.walk.get()).atoms()
        mol = chim_walk[0].molecule
        
        for atom in chim_walk:
            if atom.molecule != mol:
                raise RuntimeError("walk atoms must be on the same molecule")

        ring = RingFragment(ChimAARON.ChimeraMolecule2AaronGeometry(mol))

        walk = ",".join([str(mol.atoms.index(atom) + 1) for atom in chim_walk])
        walk_atoms = walk.split(',')
        
        ring.find_end(len(walk_atoms), walk_atoms)
        
        ring.comment = "E:%s" % walk
        
        overwrite = self.overwrite.get()

        ChimAARON.addRing(ring, name=name, overwrite=overwrite)
        