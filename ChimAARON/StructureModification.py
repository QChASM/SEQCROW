import Tkinter
import ChimAARON

from ttk import Notebook
from chimera import openModels
from chimera.baseDialog import ModelessDialog
from chimera.tkoptions import StringOption

class StructureModificationDialog(ModelessDialog):
    title = "Structure Modification"
    oneshot = True
    buttons = ("Close",)
    
    def __init__(self, notebookTab=None):
        ModelessDialog.__init__(self)
        
    def fillInUI(self, parent):
        self.frames = {}
        self.modGUIs = {}
    
        self.modOptions = Notebook(parent)
        
        
        self.frames['Map Ligand'] = Tkinter.Frame(self.modOptions)
        self.replaceLigandFrame = Tkinter.Frame(self.frames['Map Ligand'])
        self.replaceLig = Tkinter.BooleanVar()
        self.replaceLig.set(True)
        self.replaceLigCheck = Tkinter.Checkbutton(self.replaceLigandFrame, text="Replace previous structure", indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.replaceLig)
        self.replaceLigCheck.grid(row=0, column=0, sticky='w')
        self.modGUIs['Map Ligand'] = MapLigandGUI(self.frames['Map Ligand'], self, self.replaceLigandFrame)
        
        self.frames['Substitute'] = Tkinter.Frame(self.modOptions)
        self.replaceSubFrame = Tkinter.Frame(self.frames['Substitute'])
        self.replaceSub = Tkinter.BooleanVar()
        self.replaceSub.set(True)
        self.replaceSubCheck = Tkinter.Checkbutton(self.replaceSubFrame, text="Replace previous structure", indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.replaceSub)
        self.replaceSubCheck.grid(row=0, column=0, sticky='w')
        self.modGUIs['Substitute'] = SubstituteGUI(self.frames['Substitute'], self, self.replaceSubFrame)
        
        self.frames['Close Ring'] = Tkinter.Frame(self.modOptions)
        self.replaceRingFrame = Tkinter.Frame(self.frames['Close Ring'])
        self.replaceRing = Tkinter.BooleanVar()
        self.replaceRing.set(True)
        self.replaceRingCheck = Tkinter.Checkbutton(self.replaceRingFrame, text="Replace previous structure", indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.replaceRing)
        self.replaceRingCheck.grid(row=0, column=0, sticky='w')
        self.modGUIs['Close Ring'] = CloseRingGUI(self.frames['Close Ring'], self, self.replaceRingFrame)
        
        for k in self.frames:
            self.modOptions.add(self.frames[k], text=k)
            
        self.modOptions.pack(fill='both')
    
    def mapLigand(self, ligand_names, key_atoms):
        """called by MapLigandGUI"""                        
        from chimera.selection import OSLSelection
        
        atoms = OSLSelection(key_atoms).atoms()
        
        open_mols = []
        for ligand in ligand_names:
            new_mols, oldMols = ChimAARON.mapLigand(ligand, atoms)
            
            open_mols.extend(new_mols)
        
        replace = self.replaceLig.get()
        
        if replace:
            openModels.close(oldMols)
     
        for mol in open_mols:
            openModels.add([mol])
     
    def substitute(self, substituent_names, positions):
        """called by SubstituteGUI"""
        from chimera.selection import OSLSelection
        
        atoms = OSLSelection(positions).atoms()
        
        open_mols = []
        for sub in substituent_names:
            new_mols, old_mols = ChimAARON.substitute(sub, atoms)
            open_mols.extend(new_mols)
        
        replace = self.replaceSub.get()
        
        if replace:
            openModels.close(old_mols)

        for mol in open_mols:
            openModels.add([mol])
        
    def closeRing(self, ring_names, positions):
        """called by CloseRingGUI"""
        from chimera.selection import OSLSelection
        
        atoms = OSLSelection(positions).atoms()
        
        replace = self.replaceRing.get()
        
        open_mols = []
        for ring in ring_names:
            new_mols, old_mols = ChimAARON.closeRing(ring, atoms)
            open_mols.extend(new_mols)
            
        if replace:
            openModels.close(old_mols)

        for mol in open_mols:
            openModels.add([mol])

class MapLigandGUI:
    class LigandSelectorGUI(ModelessDialog):
        buttons = ("OK", "Close",)
        title = "Select Ligands"
        
        def __init__(self, origin):
            self.origin = origin
            ModelessDialog.__init__(self)
        
        def fillInUI(self, parent):
            from LibraryDialog import ligandGUI
            
            self.table, nCol = ligandGUI.getLigandTable(parent)
            self.table.launch()
            self.table.grid(row=0, column=0, columnspan=nCol, sticky='nsew')
            
            parent.rowconfigure(0, weight=1)
            parent.columnconfigure(0, weight=1)

        def Apply(self):
            geoms = self.table.selected()
            if geoms:
                self.origin.ligandName.set(",".join([geom.name for geom in geoms]))
        
    def __init__(self, parent, origin, extra_frame=None):
        self.origin = origin
        
        row = 0
        self.ligandName = StringOption(parent, row, "Ligand", "", None, balloon="name of ligands in AaronTools Ligand Library")

        self.selectLigandButton = Tkinter.Button(parent, text="From library...", command=self.openLigandSelectorGUI)
        self.selectLigandButton.grid(row=row, column=2, sticky='ew')
    
        row += 1

        self.atomSelection = StringOption(parent, row, "Key atoms", "", None, balloon="Chimera OSL atom or model specifiers (space-delimited)")
        
        self.currentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.setCurrent)
        self.currentSelectionButton.grid(row=row, column=2, sticky='ew')
        
        row += 1

        if extra_frame is not None:
            extra_frame.grid(row=row, column=0, sticky='ew', columnspan=3)
            row += 1
        
        self.doMapButton = Tkinter.Button(parent, text="map ligand", command=self.doMapLigand)
        self.doMapButton.grid(row=row, column=0, columnspan=3, sticky='ew')

    def openLigandSelectorGUI(self):
        self.LigandSelectorGUI(self)
        
    def setCurrent(self):
        from chimera.selection import currentAtoms
        self.atomSelection.set(" ".join([atom.oslIdent() for atom in currentAtoms()]))
        
    def doMapLigand(self):
        ligands = self.ligandName.get().split(',')
        
        positions = self.atomSelection.get()
        
        if not ligands:
            raise RuntimeError("No ligand")
            
        if not positions:
            raise RuntimeError("No key atoms")
                
        self.origin.mapLigand(ligands, positions)

class SubstituteGUI:
    class SubstituentSelectorGUI(ModelessDialog):
        buttons = ("OK", "Close",)
        title = "Select Substituents"
        
        def __init__(self, origin):
            self.origin = origin
            ModelessDialog.__init__(self)
        
        def fillInUI(self, parent):
            from LibraryDialog import substituentGUI
            
            self.table, nCol = substituentGUI.getSubstituentTable(parent)
            self.table.launch()
            self.table.grid(row=0, column=0, columnspan=nCol, sticky='nsew')
            
            parent.rowconfigure(0, weight=1)
            parent.columnconfigure(0, weight=1)
            
        def Apply(self):
            geoms = self.table.selected()
            if geoms:
                self.origin.substituentName.set(",".join([geom.name for geom in geoms]))
        
    def __init__(self, parent, origin, extra_frame=None):
        self.origin = origin
        
        row = 0
        self.substituentName = StringOption(parent, row, "Substituent", "", None, balloon="name of substituents from the AaronTools Substituent Library")

        self.selectSubstituentButton = Tkinter.Button(parent, text="From library...", command=self.openSubstituentSelectorGUI)
        self.selectSubstituentButton.grid(row=row, column=2, sticky='ew')
    
        row += 1

        self.atomSelection = StringOption(parent, row, "Atom selection", "", None, balloon="Chimera OSL atom specifiers (space-delimited)")
        
        self.currentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.setCurrent)
        self.currentSelectionButton.grid(row=row, column=2, sticky='ew')

        row += 1

        if extra_frame is not None:
            extra_frame.grid(row=row, column=0, sticky='ew', columnspan=3)
            row += 1
            
        self.doSubButton = Tkinter.Button(parent, text="substitute", command=self.doSubstitute)
        self.doSubButton.grid(row=row, column=0, columnspan=3, sticky='ew')

    def openSubstituentSelectorGUI(self):
        self.SubstituentSelectorGUI(self)
        
    def setCurrent(self):
        from chimera.selection import currentAtoms
        self.atomSelection.set(" ".join([atom.oslIdent() for atom in currentAtoms()]))
        
    def doSubstitute(self):
        substituents = self.substituentName.get().split(',')
        
        positions = self.atomSelection.get()
        
        if not substituents:
            raise RuntimeError("No substituents")
            
        if not positions:
            raise RuntimeError("Atom selection empty")
                
        self.origin.substitute(substituents, positions)

class CloseRingGUI:
    class RingSelectorGUI(ModelessDialog):
        buttons = ("OK", "Close",)
        title = "Select Ring Fragments"
        
        def __init__(self, origin):
            self.origin = origin
            ModelessDialog.__init__(self)
        
        def fillInUI(self, parent):
            from LibraryDialog import ringFragGUI
            
            self.table, nCol = ringFragGUI.getRingTable(parent)
            self.table.launch()
            self.table.grid(row=0, column=0, columnspan=nCol, sticky='nsew')

            parent.rowconfigure(0, weight=1)
            parent.columnconfigure(0, weight=1)

        def Apply(self):
            geoms = self.table.selected()
            if geoms:
                self.origin.ringName.set(",".join([geom.name for geom in geoms]))
        
    def __init__(self, parent, origin, extra_frame=None):
        self.origin = origin
        
        row = 0
        self.ringName = StringOption(parent, row, "Ring fragment", "", None, balloon="name of ring fragments from the AaronTools Ring Fragment Library")

        self.selectRingButton = Tkinter.Button(parent, text="From library...", command=self.openRingFragGUI)
        self.selectRingButton.grid(row=row, column=2, sticky='ew')
    
        row += 1

        self.atomSelection = StringOption(parent, row, "Atom selection", "", None, balloon="Chimera OSL atom specifiers (space-delimited)")
        
        self.currentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.setCurrent)
        self.currentSelectionButton.grid(row=row, column=2, sticky='ew')
        
        row += 1

        if extra_frame is not None:
            extra_frame.grid(row=row, column=0, sticky='ew', columnspan=3)
            row += 1
            
        self.doCloseRingButton = Tkinter.Button(parent, text="close ring", command=self.doCloseRing)
        self.doCloseRingButton.grid(row=row, column=0, columnspan=3, sticky='ew')

    def openRingFragGUI(self):
        self.RingSelectorGUI(self)
        
    def setCurrent(self):
        from chimera.selection import currentAtoms
        self.atomSelection.set(" ".join([atom.oslIdent() for atom in currentAtoms()]))
        
    def doCloseRing(self):
        ringFrags = self.ringName.get().split(',')
        
        positions = self.atomSelection.get()
        
        if not ringFrags:
            raise RuntimeError("No ring fragments")
            
        if not positions:
            raise RuntimeError("Atom selection empty")
                
        self.origin.closeRing(ringFrags, positions)

        