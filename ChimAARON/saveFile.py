import ChimAARON
import Tkinter

from chimera.baseDialog import ModelessDialog
from chimera.tkoptions import StringOption

class SaveXYZ_Dialog(ModelessDialog):
    title = "Save XYZ File"
    buttons = ("Save", "Close")
    
    def fillInUI(self, parent):
        from Pmw import OptionMenu
        from CGLtk.Table import SortableTable
        from chimera import openModels, Molecule
        
        self.parent = parent
        
        row = 0
        
        self.fileNameOption = StringOption(parent, row, "XYZ file location", "", None, balloon="location of XYZ file", width=20)
        
        self.browseButton = Tkinter.Button(parent, text="Browse", pady=0, command=self.openFileBrowser)
        self.browseButton.grid(row=0, column=2)
    
        row += 1
    
        self.addXYZ = Tkinter.BooleanVar()
        self.addXYZ.set(True)
        self.addXYZCheck = Tkinter.Checkbutton(parent, text="Add .xyz if it is not given", indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.addXYZ)
        self.addXYZCheck.grid(row=row, column=0, sticky='ew', columnspan=2)
    
        row += 1        
        
        self.displayedOnly = Tkinter.BooleanVar()
        self.displayedOnly.set(False)
        self.displayedOnlyCheck = Tkinter.Checkbutton(parent, text="Save displayed atoms only", indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.displayedOnly)
        self.displayedOnlyCheck.grid(row=row, column=0, sticky='ew', columnspan=2)
    
        row += 1
        
        self.commentOption = StringOption(parent, row, "comment", "", None, balloon="comment line of XYZ file", width=20)

        row += 1
        
        self.saveOpions = ['models', 'current selection']
    
        self.saveSelection = OptionMenu(parent, initialitem=self.saveOpions[0], command=self.setSaveOption, items=self.saveOpions, labelpos='w', label_text="Save atoms in")
        self.saveSelection.grid(row=row, column=0, stick='sew')
        
        row += 1
                
        self.modelSelection = SortableTable(parent)
        open_mols = openModels.list(modelTypes=[Molecule])

        idCol = self.modelSelection.addColumn("ID", "lambda m: m.oslIdent()", format="%s")
        nameCol = self.modelSelection.addColumn("Name", "name", format="%s")

        self.modelSelection.setData(open_mols)
        self.modelSelection.launch()

        self.setSaveOption(self.saveOpions[0])

        
    def setSaveOption(self, value):     
        self.saveSel = value
        if value == "models":
            row = self.parent.grid_size()[0]+1
            self.modelSelection.grid(row=row, column=0, columnspan=3, sticky='nsew')
            self.modelSelection.columnconfigure(0, weight=1)
            self.modelSelection.rowconfigure(row, weight=1)
        else:
            self.modelSelection.grid_forget()
    
    def openFileBrowser(self):
        import os
        from tkFileDialog import asksaveasfilename

        outfile = asksaveasfilename(initialdir=os.getcwd())
        
        if outfile:
            if not outfile.endswith('.xyz') and self.addXYZ.get():
                outfile += '.xyz'
            self.fileNameOption.set(outfile)
            
    def Save(self):
        from AaronTools.atoms import Atom
        from AaronTools.geometry import Geometry
        from ChimAARON import ChimeraAtom2AaronAtom
        from chimera.selection import currentAtoms
        
        outfile = self.fileNameOption.get()
        if outfile.strip() == "":
            raise RuntimeError("empty file name")
        
        if not outfile.endswith('.xyz') and self.addXYZ.get():
            outfile += '.xyz'
        
        if self.saveSel == 'current selection':
            atoms = currentAtoms()
        else:
            mols = self.modelSelection.selected()
            atoms = []
            for mol in mols:
                atoms.extend(mol.atoms)
                
        if len(atoms) == 0:
            raise RuntimeError("no atoms to write")
            
        aaron_atoms = []
        for atom in atoms:
            if not atom.__destroyed__ and atom.name != "ghost":
                if (self.displayedOnly.get() and atom.display) or not self.displayedOnly.get():
                    aaron_atoms.append(ChimeraAtom2AaronAtom(atom))
        
        geom = Geometry(aaron_atoms, comment=self.commentOption.get())
        
        geom.write(outfile=outfile)
        
        self.Close()
        