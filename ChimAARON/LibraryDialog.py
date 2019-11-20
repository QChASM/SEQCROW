import Pmw
import Tkinter
import ChimAARON
import ttk

from chimera.tkoptions import ColorOption
from chimera.baseDialog import ModelessDialog

class LibraryDialogMenu(ModelessDialog):
    oneshot = True
    provideStatus = True
    buttons = ("Close", )
    title = "AaronTools Libraries"
    help = ("tutorials/libraries.html", ChimAARON)

    
    def __init__(self):
        self.curFormat = None

        ModelessDialog.__init__(self)
        
    def fillInUI(self, parent):
        self.libOptions = ['Ligands', 'Substituents', 'Ring Fragments']
        
        self.libraryMenu = ttk.Notebook(parent)
                                
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
            mol = AaronGeometry2ChimeraMolecule(real_geom)
            openModels.add([mol])
            if geom.method == Substituent and self.showAttach.get():
                self.ghostAttach(real_geom, mol)
            
            elif geom.method == Component:
                #if self.showBackbone.get():
                #    self.highlightBackbone(real_geom, mol)
                
                if self.showKey.get():
                    self.highlightKey(real_geom, mol)
                
            elif geom.method == RingFragment and self.showWalk.get():
                mdl = self.ringWalk(real_geom, mol)
            
    def ghostAttach(self, sub, mol):
        """show ghost atom and bond where sub attaches to the rest of the molecule"""
        from Bld2VRML import openBildString
        from chimera import openModels
    
        color = self.subColor.get()
        
        if len(mol.bonds) > 0:
            r = mol.bonds[0].radius*mol.stickScale
        else:
            r = 0.2
                
        s = ".sphere 0 0 0  %f\n" % r
        s += ".cylinder 0 0 0   %f 0 0   %f open\n" % (sub.atoms[0].coords[0], r)
        
        mdls = openBildString(s)
        for mdl in mdls:
            mdl.color = color
        
        openModels.add(mdls, sameAs=mol)
                
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
        
    def highlightKey(self, lig, mol):
        """highlight the ligand backbone"""
        from Bld2VRML import openBildString
        from chimera import openModels

        color = self.keyColor.get()
        
        r = 1.1*mol.ballScale
        
        s = ''
        
        for atom in lig.key_atoms:
            #scale sphere radius to be slightly larger than the ball radius for b&s representation
            chim_atom = mol.atoms[lig.atoms.index(atom)] 
            info = tuple(atom.coords) + (r*chim_atom.radius,)
            s += ".sphere %f %f %f   %f\n" % info
                
        mdls = openBildString(s)
        for mdl in mdls:
            mdl.color = color
            
        openModels.add(mdls, sameAs=mol)        
        
    def ringWalk(self, ring, mol):
        """put arrows on the path that we'll walk around the ring"""
        from Bld2VRML import openBildString
        from chimera import openModels, Bond, MaterialColor     

        color = self.walkColor.get()

        #radius for arrows
        r_bd = mol.bonds[0].radius*mol.stickScale
        #radius for spheres (used when there's only one end atom)
        r_sp = 1.1*mol.ballScale

        s = ''
        if len(ring.end) == 1:
            chim_atom = mol.atoms[ring.atoms.index(ring.end[0])]
            info = tuple(ring.end[0].coords) + (r_sp*chim_atom.radius,)
            s += ".sphere %f %f %f   %f\n" % info
        else:
            for atom1, atom2 in zip(ring.end[:-1], ring.end[1:]):
                chim_atom1 = mol.atoms[ring.atoms.index(atom1)]
                chim_atom2 = mol.atoms[ring.atoms.index(atom2)]
                for bond in chim_atom1.bonds:
                    if chim_atom1 in bond.atoms and chim_atom2 in bond.atoms:
                        bond.display = Bond.Never
                
                v = atom1.bond(atom2)
                info = tuple(atom1.coords) + tuple(atom2.coords - r_sp*v) + (r_bd, 1.5*r_bd,)
                s += ".arrow %f %f %f   %f %f %f   %f %f 0.7\n" % info
                
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

        #turns out, the backbone is everything?
        #self.showBackbone = Tkinter.BooleanVar()
        #self.showBackbone.set(False)
        #self.showBackboneButton = Tkinter.Checkbutton(parent, text="Show backbone", indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.showBackbone)
        #self.showBackboneButton.grid(row=1, column=2, sticky='sew')
        
        #self.ligColor = ColorOption(parent, 1, "Backbone color", tuple((0.1, 0.1, 0.7, 0.5)), None)

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
        
        from AaronTools.ringfragment import RingFragment
        from CGLtk.Table import SortableTable
        from glob import glob
        
        self.nRow = 2
        self.nCol = 1
        
        #create table of ring fragments
        #TODO: make table creation a classmethod like ligands
        ring_list = glob(RingFragment.AARON_LIBS) + glob(RingFragment.BUILTIN)
        
        self.table = SortableTable(parent)
        nameCol = self.table.addColumn("Name", "name", format="%s")
        
        self.table.setData([PseudoGeometry(ring, RingFragment) for ring in ring_list]) 
        
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
        