import Tkinter
import Pmw
import ChimAARON

from chimera.preferences import preferences
from chimera.baseDialog import ModelessDialog
from chimera.tkoptions import InputFileOption

class FreqFileLoader(ModelessDialog):

    title = "Load Frequency File"
    buttons = ['OK', 'Cancel']
    help = ("tutorials/normalModes.html", ChimAARON)
    
    def __init__(self, freqFile=None):
        self.freqFile = freqFile
        
        ModelessDialog.__init__(self)
        
    def fillInUI(self, parent):
        from ChimAARON.prefs import INPUT_FILES
        inputPref = preferences.get('ChimAARON', INPUT_FILES)

        if 'Frequency' in inputPref:
            defaultIn = inputPref['Frequency']
        else:
            defaultIn = None

        self.frame = InputFileOption(parent, 0,
        "Frequency File", defaultIn,
        None, title="Choose Frequency File",
        historyID="Frequency File")
                    
    def Apply(self):
        from chimera import replyobj
        from AaronTools.fileIO import FileReader
        from ChimAARON.prefs import prefs, INPUT_FILES
        from copy import deepcopy
                
        inputPrefs = deepcopy(prefs[INPUT_FILES])
        
        self.freqFile = self.frame.get()

        if True:
#        try:
            NormalModeDialog(FileReader(self.freqFile, just_geom=False))
            inputPrefs['Frequency'] = self.freqFile
            prefs[INPUT_FILES] = inputPrefs
            self.destroy()
#        except Exception, msg:
#            self.enter()
#            replyobj.error(str(msg) + '\n')

class NormalModeDialog(ModelessDialog):
    """interface for an opened frequency job"""
    oneshot = True
    provideStatus = True
    buttons = ("Close",)
    title = "Normal Modes"
    help = ("tutorials/normalModes.html", ChimAARON)
    
    def __init__(self, fileReader):
        if 'frequency' not in fileReader.other:
            raise RuntimeError("FileReader %s has no frequencies" % fileReader.name)
        
        self.fileReader = fileReader
        self.data = fileReader.other['frequency'].data
        
        ModelessDialog.__init__(self)
        
    def fillInUI(self, parent):
        from CGLtk.Table import SortableTable
        from ttk import Notebook
        
        modes = [i for i in range(0, len(self.fileReader.other['frequency'].data))]
        
        self.table = SortableTable(parent)
        freqCol = self.table.addColumn("Frequency (cm^-1)", \
                             "frequency", \
                             format="%.2f")
        
        if all([hasattr(self.fileReader.other['frequency'].data[i], "intensity") for i in modes]):
            intenCol = self.table.addColumn("I.R. Intensity", \
                                 "intensity", \
                                 format="%.2f")
                    
        self.table.setData(self.data)
		
        self.table.launch(browseCmd=self.showableModes)
        self.table.grid(row=0, sticky="nsew")
        self.table.columnconfigure(0, weight=1)
        self.table.rowconfigure(0, weight=1)
        
        self.modeOptions = ["Vectors", "Animate"]
        
        self.animOrVec = Notebook(parent)
                
        self.frames = {}
        self.modeGUIs = {}
        
        self.frames["Vectors"] = Tkinter.Frame(self.animOrVec)
        self.modeGUIs["Vectors"] = vectorGUI(self.frames["Vectors"], self.fileReader, self.data, self.table)
        
        self.frames["Animate"] = Tkinter.Frame(self.animOrVec)
        self.modeGUIs["Animate"] = animateGUI(self.frames["Animate"], self.fileReader, self.data, self.table)
        
        self.animOrVec.add(self.frames["Vectors"], text="Vectors")
        self.animOrVec.add(self.frames["Animate"], text="Animate")
        
        self.animOrVec.grid(row=1, column=0, sticky='nsew')
        
        parent.pack(fill='both')

    def showableModes(self, modes):
        state = "normal"
        if len(modes) != 1:
            state = "disabled"
        
        for key in self.modeGUIs:
            self.modeGUIs[key].loadModeButton.config(state=state)

class animateGUI:
    def __init__(self, parent, fileReader, data, table):
        from chimera.tkoptions import FloatOption, IntOption
        from AaronTools.geometry import Geometry
        
        self.fileReader = fileReader
        self.data = data
        self.table = table

        self.geom = Geometry(self.fileReader)

        row = 0
    
        self.scaleOption = FloatOption(parent, row, "Max. displacement", 0.2, None, width=6)
        row += 1
        
        self.nFrameOption = IntOption(parent, row, "Number of frames", 101, None, width=6)
        row += 1
        
        self.loadModeButton = Tkinter.Button(parent, state="disabled", pady=0, \
                                    text="Animated selected mode", \
                                    command=self._animated_selected_modes)
        
        self.loadModeButton.grid(row=row, column=0, columnspan=2, sticky='ew')
        row += 1
        
    def _animated_selected_modes(self):
        from ChimAARON import Freq2Pathway, Pathway2Ensemble
        from AaronTools.geometry import Geometry
        from Movie.gui import MovieDialog

        mode_data = self.table.selected()
        scales = [[self.scaleOption.get()]]
        nFrames = self.nFrameOption.get()
                
        modes = [[self.data.index(mode) for mode in mode_data]]
        
        pathway = Freq2Pathway(self.geom, self.data, modes, scales)
        ensemble = Pathway2Ensemble(pathway, nFrames)
        ensemble.name = "%f cm^-1" % mode_data[0].frequency
        
        MovieDialog(ensemble)
           
class vectorGUI:
    def __init__(self, parent, fileReader, data, table):
        from chimera.tkoptions import FloatOption, BooleanOption, ColorOption
        from AaronTools.geometry import Geometry
        from ChimAARON import AaronGeometry2ChimeraMolecule
        
        self.fileReader = fileReader
        self.data = data
        self.table = table

        self.geom = Geometry(self.fileReader)
        self.mol = AaronGeometry2ChimeraMolecule(self.geom)
        
        row = 0
        
        self.scaleOption = FloatOption(parent, row, "Vector scaling", 1.5, None, width=6)
        row += 1
        
        self.massWeightOption = BooleanOption(parent, row, "Use mass-weighted", 0, None)
        row += 1
        
        self.colorSelect = ColorOption(parent, row, "Vector color", tuple((0, 1, 0)), None)
        row += 1
        
        self.loadModeButton = Tkinter.Button(parent, state="disabled", pady=0, \
                                    text="Display mode vectors", \
                                    command=self._display_mode_vectors)
        
        
        self.loadModeButton.grid(row=row, column=0, columnspan=2, sticky='ew')
        row += 1
                
    def _display_mode_vectors(self):
        from ChimAARON import Freq2Bild, AaronGeometry2ChimeraMolecule
        from AaronTools.geometry import Geometry
        from chimera import openModels
        
        mode_data = self.table.selected()
        scales = [[self.scaleOption.get()]]
        massweight = self.massWeightOption.get()
        color = self.colorSelect.get()
        
        print(color)
        if hasattr(color, "__dict__"):
            print(color.__dict__)
        
        modes = [[self.data.index(mode) for mode in mode_data]]
        
        mdl = Freq2Bild(self.geom, self.data, modes, scales, massweight, color)
        mol = AaronGeometry2ChimeraMolecule(self.geom)
        
        openModels.add([mol])
        openModels.add(mdl, sameAs=mol)
        