import Tkinter
import ChimAARON
import os

from ChimAARON.prefs import ENVIRONMENT
from CGLtk.Table import SortableTable
from chimera import openModels, Molecule, preferences, replyobj, MaterialColor
from chimera.baseDialog import ModelessDialog
from chimera.tkoptions import StringOption, IntOption, ColorOption
from ttk import Notebook

class LibraryDialog(ModelessDialog):
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
                addSub(real_geom, color=self.subColor.get(), showAttach=self.showAttach.get())
            
            elif geom.method == Component:             
                addLig(real_geom, color=self.keyColor.get(), showKey=self.showKey.get())
                
            elif geom.method == RingFragment:
                addRing(real_geom, color=self.walkColor.get(), showWalk=self.showWalk.get())
            
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
        
        targetFrame = Tkinter.Frame(parent)
        self.target = StringOption(targetFrame, 0, "Substituent atoms", "", None, balloon="OSL atom specification for substituent atoms")
        targetFrame.grid(row=row, column=0, columnspan=2, sticky='se')
        
        self.targetCurrentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.targetSetCurrent)
        self.targetCurrentSelectionButton.grid(row=row, column=2, sticky='sw')
        
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
        self.overwriteCheck.grid(row=row, column=1, sticky='nw')
        
        self.overwriteLabel = Tkinter.Label(parent, text="Overwrite existing")
        self.overwriteLabel.grid(row=row, column=0, sticky='ne')
        
        row += 1

        self.libAddButton = Tkinter.Button(parent, pady=0, text="Add to library", command=self.libaddSub)
        self.libAddButton.grid(row=row, column=0, columnspan=2, sticky='new')
        
        row += 1

        parent.pack()
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

    def targetSetCurrent(self):
        from chimera.selection import currentAtoms
        self.target.set(" ".join([atom.oslIdent() for atom in currentAtoms()]))

    def libaddSub(self):
        import numpy as np
        
        from chimera.selection import OSLSelection
        from ChimAARON import ChimeraMolecule2AaronGeometry
        
        name = self.subName.get()

        chim_targets = OSLSelection(self.target.get()).atoms()
        mol = chim_targets[0].molecule
        for atom in chim_targets:
            if atom.molecule != mol:
                raise RuntimeError("atoms must all be on the same molecule")
        
        geom = ChimeraMolecule2AaronGeometry(mol)
        
        targets = [geom.atoms[mol.atoms.index(chim_target)] for chim_target in chim_targets]
        
        avoid = None
        target = None
        for atom in geom.atoms:
            if atom not in targets and any([atom in atom2.connected for atom2 in targets]):
                if avoid is None:
                    avoid = atom
                    for atom2 in targets:
                        if atom in atom2.connected:
                            if target is None:
                                target = atom2
                            else:
                                raise RuntimeError("selected substituent has multiple connections to the molecule")
                else:
                    raise RuntimeError("selected substituent has multiple conenctions to the molecule")
        
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

        addSub(sub, name=name, overwrite=overwrite)
            
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
        self.overwriteCheck.grid(row=row, column=1, sticky='nw')
        
        self.overwriteLabel = Tkinter.Label(parent, text="Overwrite existing")
        self.overwriteLabel.grid(row=row, column=0, sticky='ne')
        
        row += 1

        self.libAddButton = Tkinter.Button(parent, state="disabled", pady=0, text="Add to library", command=self.libaddLig)
        self.libAddButton.grid(row=row, column=0, columnspan=2, sticky='new')
        
        row += 1
        
        parent.pack()
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        
    def libaddLig(self):
        from AaronTools.catalyst import Catalyst 
        from AaronTools.component import Component
        from ChimAARON import ChimeraMolecule2AaronGeometry
        
        name = self.ligName.get()
        
        mol = self.modelSelection.selected()[0]
        cat = Catalyst(ChimeraMolecule2AaronGeometry(mol))
        
        if cat.center is not None:
            cat.coord_shift(-cat.COM(targets=cat.center))
            
        ligands = cat.components['ligand']
        lig_index = 0
        
        if len(ligands) > 1:
            replyobj.status("multiple ligands found")
            
        new_ligand = ligands[lig_index]
        new_ligand.comment = "K:" + ",".join([str(new_ligand.atoms.index(key) + 1) for key in new_ligand.key_atoms]) + ";"
        
        overwrite = self.overwrite.get()

        addLig(new_ligand, name=name, overwrite=overwrite)
        
    def selectOne(self, models):
        state = "normal"
        print(models)
        if len(models) != 1:
            state = "disabled"
            
        self.libAddButton.config(state=state)

class LibAddRingGUI:
    def __init__(self, parent):
        row = 0 
        
        walkFrame = Tkinter.Frame(parent)
        self.walk = StringOption(walkFrame, row, "Walk atoms", "", None, balloon="OSL atom specification to define the direction to go around the ring")
        walkFrame.grid(row=row, column=0, columnspan=2, sticky='se')
        
        self.currentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.setCurrent)
        self.currentSelectionButton.grid(row=row, column=2, sticky='sw')  

        row += 1

        self.ringName = StringOption(parent, row, "Ring name", "", None, balloon="name of ring\nleave blank to see the ring before adding it to the library")
        
        row += 1

        self.overwrite = Tkinter.BooleanVar()
        self.overwrite.set(False)
        self.overwriteCheck = Tkinter.Checkbutton(parent, indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.overwrite)
        self.overwriteCheck.grid(row=row, column=1, sticky='nw')
        
        self.overwriteLabel = Tkinter.Label(parent, text="Overwrite existing")
        self.overwriteLabel.grid(row=row, column=0, sticky='ne')
        
        row += 1

        self.libAddButton = Tkinter.Button(parent, pady=0, text="Add to library", command=self.libaddRing)
        self.libAddButton.grid(row=row, column=0, columnspan=2, sticky='new')
        
        row += 1
        
        parent.pack()
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        
    def setCurrent(self):
        from chimera.selection import currentAtoms
        self.walk.set(" ".join([atom.oslIdent() for atom in currentAtoms()]))
        
    def libaddRing(self):
        from AaronTools.ringfragment import RingFragment
        from chimera.selection import OSLSelection
        from ChimAARON import ChimeraMolecule2AaronGeometry

        name = self.ringName.get()
        
        chim_walk = OSLSelection(self.walk.get()).atoms()
        mol = chim_walk[0].molecule
        
        for atom in chim_walk:
            if atom.molecule != mol:
                raise RuntimeError("walk atoms must be on the same molecule")

        ring = RingFragment(ChimeraMolecule2AaronGeometry(mol))

        walk = ",".join([str(mol.atoms.index(atom) + 1) for atom in chim_walk])
        walk_atoms = walk.split(',')
        
        ring.find_end(len(walk_atoms), walk_atoms)
        
        ring.comment = "E:%s" % walk
        
        overwrite = self.overwrite.get()

        addRing(ring, name=name, overwrite=overwrite)
        
def doLibaddLig(cmdName, arg_str):
    """libaddLigand but in chimera
    libaddligand [name <name>] [overwrite <FALSE|true>] model selection"""
    from ChimAARON import ArgumentParser, ChimeraMolecule2AaronGeometry
    from chimera.selection import OSLSelection, currentMolecules
    from AaronTools.component import Component
    from AaronTools.catalyst import Catalyst
    
    parser = ArgumentParser()
    
    parser.addArg('name', 1, kind=str, default=False)
    parser.addArg('overwrite', 1, kind=bool, default=False)
    
    args = parser.parse_args(arg_str)
    
    name = args['name']
    overwrite = args['overwrite']
    sel = " ".join(args['other'])
    
    if sel != 'sel':
        mol = OSLSelection(sel).molecules()
    else:
        mol = currentMolecules()
        
    if len(mol) != 1:
        raise RuntimeError("one molecule must be selected")
    else:
        mol = mol[0]
        
    cat = Catalyst(ChimeraMolecule2AaronGeometry(mol))
    
    if cat.center is not None:
        cat.coord_shift(-cat.COM(targets=cat.center))
        
    ligands = cat.components['ligand']
    lig_index = 0
    
    if len(ligands) > 1:
        replyobj.status("multiple ligands found")
        
    new_ligand = ligands[lig_index]
    new_ligand.comment = "K:" + ",".join([str(new_ligand.atoms.index(key) + 1) for key in new_ligand.key_atoms]) + ";"
    
    addLig(new_ligand, name=name, overwrite=overwrite)

def doLibaddSub(cmdName, arg_str):
    import numpy as np

    from ChimAARON import ArgumentParser, ChimeraMolecule2AaronGeometry
    from chimera.selection import OSLSelection, currentAtoms
    from AaronTools.substituent import Substituent
    
    parser = ArgumentParser()
    
    parser.addArg('name', 1, kind=str, default=False)
    parser.addArg('overwrite', 1, kind=bool, default=False)
    parser.addArg('target', 1, kind='selec', default=None)
    parser.addArg('avoid', 1, kind='selec', default=None)
    parser.addArg('conformers', 1, kind=int, default=0)
    parser.addArg('angle', 1, kind=int, default=0)
    
    args = parser.parse_args(arg_str)
    
    name = args['name']
    overwrite = args['overwrite']
    chim_target = args['target']
    chim_avoid = args['avoid']
    conformers = args['conformers']
    angle = args['angle']
    
    if chim_target is None or chim_avoid is None:
        sel = " ".join(args['other'])
        
        if sel != 'sel':
            chim_targets = OSLSelection(sel).atoms()
        else:
            chim_targets = currentAtoms()
        
        if len(chim_targets) == 0:
            raise RuntimeError("no atoms selected")
        
        mol = chim_targets[0].molecule
        for atom in chim_targets:
            if atom.molecule != mol:
                raise RuntimeError("atoms must all be on the same molecule")
            
        geom = ChimeraMolecule2AaronGeometry(mol)
        
        targets = [geom.atoms[mol.atoms.index(chim_target)] for chim_target in chim_targets]
        
        avoid = None
        target = None
        for atom in geom.atoms:
            if atom not in targets and any([atom in atom2.connected for atom2 in targets]):
                if avoid is None:
                    avoid = atom
                    for atom2 in targets:
                        if atom in atom2.connected:
                            if target is None:
                                target = atom2
                            else:
                                raise RuntimeError("selected substituent has multiple connections to the molecule")
                else:
                    raise RuntimeError("selected substituent has multiple conenctions to the molecule")
    else:
        chim_target = OSLSelection(chim_target).atoms()
        if len(chim_target) != 1:
            raise RuntimeError("target must be one atom (%i selected)" % len(chim_target))
        else:
            chim_target = chim_target[0]
            
        chim_avoid = OSLSelection(chim_avoid).atoms()
        if len(chim_avoid) != 1:
            raise RuntimeError("avoid must be one atom (%i selected)" % len(chim_avoid))
        else:
            chim_avoid = chim_avoid[0]
        
        if chim_target.molecule != chim_avoid.molecule:
            raise RuntimeError("selected atoms must be on the same molecule")
        
        mol = chim_target.molecule
        
        geom = ChimeraMolecule2AaronGeometry(mol)

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
    
    sub.comment = "CF:%i,%i" % (conformers, angle)

    addSub(sub, name=name, overwrite=overwrite)

def doLibaddRing(cmdName, arg_str):
    from ChimAARON import ArgumentParser, ChimeraMolecule2AaronGeometry
    from AaronTools.ringfragment import RingFragment
    from chimera.selection import OSLSelection, currentAtoms

    parser = ArgumentParser()
    
    parser.addArg('name', 1, kind=str, default=False)
    parser.addArg('walk', 1, kind='selec', default="")
    parser.addArg('overwrite', 1, kind=bool, default=False)
    
    args = parser.parse_args(arg_str)
    
    name = args['name']
    walk = args['walk']
    overwrite = args['overwrite']
    
    if walk != 'sel':
        chim_walk = OSLSelection(walk).atoms()
    else:
        chim_walk = currentAtoms()
    
    if len(chim_walk) == 0:
        raise RuntimeError("must specify walk atoms")
    
    mol = chim_walk[0].molecule
    for atom in chim_walk:
        if atom.molecule != mol:
            raise RuntimeError("walk atoms must be on the same molecule")
    
    ring = RingFragment(ChimeraMolecule2AaronGeometry(mol))

    walk = ",".join([str(mol.atoms.index(atom) + 1) for atom in chim_walk])
    walk_atoms = walk.split(',')
    
    ring.find_end(len(walk_atoms), walk_atoms)
    
    ring.comment = "E:%s" % walk
    
    addRing(ring, name=name, overwrite=overwrite)

def addRing(ring, name=False, overwrite=False, color=None, showWalk=True):
    """ring   - AaronTools RingFragment
    name      - if name is false, load ring into chimera
              - if name is not false, add the ring to the AaronTools library
    overwrite - overwrite lig with same name if it already is in the library
    color     - chimera.MaterialColor: color of walk arrows
    showWalk  - whether or not to draw walk arrows"""
    
    import os
    
    from AaronTools.ringfragment import RingFragment
    from Bld2VRML import openBildString
    from chimera import openModels, MaterialColor, replyobj, Bond
    from ChimAARON import AaronGeometry2ChimeraMolecule
    
    if name:
        ring_file = os.path.join(os.path.dirname(RingFragment.AARON_LIBS), name + '.xyz')
        if os.path.exists(ring_file) and not overwrite:
            replyobj.error("%s already exists" % ring_file)
        else:
            ring.write(outfile=ring_file)
            replyobj.status("%s added to ring fragment library" % name)

    else:
        ring_mol = AaronGeometry2ChimeraMolecule(ring)
        openModels.add([ring_mol])
        if showWalk:
            if color is None:
                color = MaterialColor(0.9, 0.4, 0.3, 0.9)
            #radius for arrows
            r_bd = ring_mol.bonds[0].radius*ring_mol.stickScale
            #radius for spheres (used when there's only one end atom)
            r_sp = 1.1*ring_mol.ballScale
        
            s = ''
            if len(ring.end) == 1:
                chim_atom = ring_mol.atoms[ring.atoms.index(ring.end[0])]
                info = tuple(ring.end[0].coords) + (r_sp*chim_atom.radius,)
                s += ".sphere %f %f %f   %f\n" % info
            else:
                for atom1, atom2 in zip(ring.end[:-1], ring.end[1:]):
                    chim_atom1 = ring_mol.atoms[ring.atoms.index(atom1)]
                    chim_atom2 = ring_mol.atoms[ring.atoms.index(atom2)]
                    for bond in chim_atom1.bonds:
                        if chim_atom1 in bond.atoms and chim_atom2 in bond.atoms:
                            bond.display = Bond.Never
                    
                    v = atom1.bond(atom2)
                    info = tuple(atom1.coords) + tuple(atom2.coords - r_sp*v) + (r_bd, 1.5*r_bd,)
                    s += ".arrow %f %f %f   %f %f %f   %f %f 0.7\n" % info
                    
            mdls = openBildString(s)
            for mdl in mdls:
                mdl.color = color
                
            openModels.add(mdls, sameAs=ring_mol)

def addLig(lig, name=False, overwrite=False, color=None, showKey=True):
    """lig    - AaronTools Component
    name      - if name is false, load lig into chimera
              - if name is not false, add the lig to the AaronTools library
    overwrite - overwrite lig with same name if it already is in the library
    color     - chimera.MaterialColor: color of key atoms
    showKey   - whether or not to highlight key atoms"""
    
    import os
    
    from AaronTools.component import Component
    from Bld2VRML import openBildString
    from chimera import openModels, MaterialColor, replyobj
    from ChimAARON import AaronGeometry2ChimeraMolecule
    
    if name:
        lig_file = os.path.join(os.path.dirname(Component.AARON_LIBS), name + '.xyz')
        if os.path.exists(lig_file) and not overwrite:
            replyobj.error("%s already exists" % lig_file)
        else:
            lig.write(outfile=lig_file)
            replyobj.status("%s added to ligand library" % name)
    else:
        lig_mol = AaronGeometry2ChimeraMolecule(lig)
        openModels.add([lig_mol])
        if showKey:
            if color is None:
                color = MaterialColor(0.2, 0.5, 0.8, 0.5)

            r = 1.1*lig_mol.ballScale

            s = ''

            for atom in lig.key_atoms:
                #scale sphere radius to be slightly larger than the ball radius for b&s representation
                chim_atom = lig_mol.atoms[lig.atoms.index(atom)] 
                info = tuple(atom.coords) + (r*chim_atom.radius,)
                s += ".sphere %f %f %f   %f\n" % info

            mdls = openBildString(s)
            for mdl in mdls:
                mdl.color = color
                
            openModels.add(mdls, sameAs=lig_mol)

def addSub(sub, name=False, overwrite=False, color=None, showAttach=True):
    """sub    - AaronTools Substituent
    name      - if name is false, load sub into chimera
              - if name is not false, add the sub to the AaronTools library
    overwrite - overwrite sub with same name if it already is in the library
    color     - chimera.MaterialColor: color of key atoms
    showKey   - whether or not to highlight key atoms"""
    
    import os
    
    from AaronTools.substituent import Substituent
    from Bld2VRML import openBildString
    from chimera import openModels, MaterialColor, replyobj
    from ChimAARON import AaronGeometry2ChimeraMolecule
    
    if name:
        sub_file = os.path.join(os.path.dirname(Substituent.AARON_LIBS), name + '.xyz')
        if os.path.exists(sub_file) and not overwrite:
            replyobj.error("%s already exists" % sub_file)
        else:
            sub.write(outfile=sub_file)
            replyobj.status("%s added to substituent library" % name)
    else:
        sub_mol = AaronGeometry2ChimeraMolecule(sub)
        openModels.add([sub_mol])
        if showAttach:
            if color is None:
                color = MaterialColor(0.60784, 0.145098, 0.70196, 0.5)
            
            if len(sub_mol.bonds) > 0:
                r = sub_mol.bonds[0].radius*sub_mol.stickScale
            else:
                r = 0.2
                    
            s = ".sphere 0 0 0  %f\n" % r
            s += ".cylinder 0 0 0   %f 0 0   %f open\n" % (sub.atoms[0].coords[0], r)
            
            mdls = openBildString(s)
            for mdl in mdls:
                mdl.color = color
            
            openModels.add(mdls, sameAs=sub_mol)

