import Pmw
import Tkinter
import ChimAARON

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
        
        self.libraryMenu = Pmw.OptionMenu(parent, initialitem=self.libOptions[0],
                                command=self.showFormat, items=self.libOptions, labelpos='w',
                                label_text='Browse library:')
                                
        self.libraryMenu.grid(row=0, column=0, sticky='new')
        self.libraryMenu.rowconfigure(0, weight=0)
        self.frames = {}
        self.paramGUIs = {}
        
        self.frames['Ligands'] = Tkinter.Frame(parent)
        self.paramGUIs['Ligands'] = ligandGUI(self.frames['Ligands'])
        
        self.frames['Substituents'] = Tkinter.Frame(parent)
        self.paramGUIs['Substituents'] = substituentGUI(self.frames['Substituents'])
        
        self.frames['Ring Fragments'] = Tkinter.Frame(parent)
        self.paramGUIs['Ring Fragments'] = ringFragGUI(self.frames['Ring Fragments'])
         
        self.showFormat(self.libOptions[0])
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
         
    def showFormat(self, format):
        if format not in self.libOptions:
            return
        
        if self.curFormat:
            self.frames[self.curFormat].grid_forget()
            
        self.frames[format].grid(row=1, column=0, sticky='nsew', \
                            columnspan=self.paramGUIs[format].nCol)

        self.frames[format].rowconfigure(1, weight=1)
        self.frames[format].columnconfigure(0, weight=1)
        
        self.curFormat = format
       
class GeomLoadGUI:
    def _open_geom(self):
        from ChimAARON import AaronGeometry2ChimeraMolecule
        from chimera import openModels
        from AaronTools.geometry import Geometry
        
        geoms = self.table.selected()
        
        for geom in geoms:
            mol = AaronGeometry2ChimeraMolecule(geom.method(str(geom.name)))
            openModels.add([mol])

    def canOpen(self, selected):
        state = "normal"
        if len(selected) < 1:
            state = "disabled"
            
        self.loadButton.config(state=state)
      
class ligandGUI(GeomLoadGUI):
    def __init__(self, parent):
        import os        
        
        self.nRow = 2
        self.nCol = 3

        self.table, nCol = self.getLigandTable(parent)
        
        self.table.launch(browseCmd=self.canOpen)
        self.table.grid(row=0, column=0, columnspan=nCol, sticky='nsew')
        self.table.rowconfigure(0, weight=1)
        self.table.columnconfigure(0, weight=1)

        self.loadButton = Tkinter.Button(parent, state="disabled", pady=0, \
                                    text="Open selected ligands", \
                                    command=self._open_geom, anchor='s')
        
        self.loadButton.grid(row=1, sticky='sew')
    
    @classmethod
    def getLigandTable(cls, parent):
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
        import os
                
        self.nRow = 2
        self.nCol = 3
        
        self.table, nCol = self.getSubstituentTable(parent)
        
        self.table.launch(browseCmd=self.canOpen)
        self.table.grid(row=0, column=0, columnspan=nCol, sticky='nsew')
        self.table.rowconfigure(0, weight=1)
        self.table.columnconfigure(0, weight=1)
        
        self.loadButton = Tkinter.Button(parent, state="disabled", pady=0, \
                                    text="Open selected substituents", \
                                    command=self._open_geom, anchor='s')
        
        self.loadButton.grid(row=1, sticky='sew')        

    @classmethod
    def getSubstituentTable(cls, parent):
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
        import os
        
        from AaronTools.ringfragment import RingFragment
        from CGLtk.Table import SortableTable
        from glob import glob
        
        self.nRow = 2
        self.nCol = 1
        
        ring_list = glob(RingFragment.AARON_LIBS) + glob(RingFragment.BUILTIN)
        
        self.table = SortableTable(parent)
        nameCol = self.table.addColumn("Name", "name", format="%s")
        
        self.table.setData([PseudoGeometry(ring, RingFragment) for ring in ring_list]) 
        
        self.table.launch(browseCmd=self.canOpen)
        self.table.grid(row=0, column=0, columnspan=self.nCol, sticky='nsew')
        self.table.columnconfigure(0, weight=1)
        self.table.rowconfigure(0, weight=1)
        
        self.loadButton = Tkinter.Button(parent, state="disabled", pady=0, \
                                    text="Open selected ring fragments", \
                                    command=self._open_geom, anchor='s')
        
        self.loadButton.grid(row=1, sticky='ew')
        
class PseudoGeometry:
    def __init__(self, filename, method):
        import os
        import re

        from linecache import getline, clearcache
        from AaronTools.substituent import Substituent
        from AaronTools.ringfragment import RingFragment
        from AaronTools.component import Component
        
        self.name = os.path.split(filename)[-1].replace('.xyz', '')
        self.filename = filename
        self.method = method
        
        if method == Component:
            self.key_atoms = []
            self.key_elements = []
            line1 = getline(filename, 2)
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
                
            for atom in self.key_atoms:
                atom_info = getline(filename, atom+2)
                self.key_elements.append(atom_info.split()[0])
                
            clearcache()
                
        if method == Substituent:
            line1 = getline(filename, 2)
                            
            conf_info = re.search("CF:(\d+),(\d+)", line1)
            if conf_info is not None:
                self.conf_num = int(conf_info.group(1))
                self.conf_angle = int(conf_info.group(2))
            else:
                self.conf_num = -1
                self.conf_angle = -1
            
            clearcache()
        