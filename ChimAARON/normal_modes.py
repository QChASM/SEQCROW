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
        from ChimAARON import Pathway2Ensemble
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
        from ChimAARON import AaronGeometry2ChimeraMolecule
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

def parse_mode_str(s, t):
    """split mode string into modes and mode combos
    e.g.
    t=int, 1,2+3,4 -> [[0], [1,2], [3]]
    t=float 0.1,0.05+0.03,0.07 -> [[0.1], [0.05, 0.03], [0.07]]"""

    #the way this is being used is if t is int, we are changing 1-indexed things to 0-index
    #if t is float, were going to use the result to scale a normal mode (don't subtract 1)

    if t is not int and t is not float:
        raise TypeError("can only parse mode string into ints or floats, not %s" % repr(t))

    modes = s.split(',')
    out_modes = []
    for mode in modes:
        out_modes.append([])
        for combo in mode.split('+'):
            if t is int:
                out_modes[-1].append(int(combo)-1)
            elif t is float:
                out_modes[-1].append(float(combo))

    return out_modes

def Freq2Pathway(geom, data, modes, scale, roundtrip=True):
    """create an animation of modes"""
    from chimera import replyobj
    from AaronTools.trajectory import Pathway
    from numpy.linalg import norm
    from numpy import zeros
    
    #figure out how much to move for each moe based on scale
    for i, mode in enumerate(modes):
        dX = zeros((len(geom.atoms), 3))
        for j, combo in enumerate(mode):
            max_norm = 0
            for k, v in enumerate(data[combo].vector):
                n = norm(v)
                if n > max_norm:
                    max_norm = n
                    
            x_factor = scale[i][j]/max_norm
                        
            dX += x_factor*data[combo].vector
    
    #set up pathway
    replyobj.status("preparing to load animation...")
    Gf=geom.copy()
    Gf.update_geometry(geom.coords() + dX)
    Gr = geom.copy()
    Gr.update_geometry(geom.coords() - dX)
    
    if roundtrip:
        S = Pathway([Gf, geom, Gr, geom, Gf])
    else:
        S = Pathway([Gf, geom, Gr])
        
    return S

def Freq2Bild(geom, data, modes, scale, massweight, color):
    from Bld2VRML import openBildString
    from numpy.linalg import norm
    from numpy import zeros
    
    #figure out how long each vector should be
    for i, mode in enumerate(modes):
        dX = zeros((len(geom.atoms), 3))
        for j, combo in enumerate(mode):
            max_norm = 0
            for k, v in enumerate(data[combo].vector):
                n = norm(v)
                
                if massweight:
                    n *= geom.atoms[k].mass()
                    
                if n > max_norm:
                    max_norm = n
                    
            x_factor = scale[i][j]/max_norm
            
            dX += x_factor*data[combo].vector
    
    #start creating a bild string
    if isinstance(color, basestring):
        output = ".color %s\n" % color
    else:
        output = ""
    
    #add vectors to bild string
    for n in range(0, len(geom.atoms)):
        if massweight:
            dX[n] *= geom.atoms[n].mass()
            
        v_len = norm(dX[n])
    
        info = tuple(t for s in [ \
            [x for x in geom.atoms[n].coords], \
            [x for x in geom.atoms[n].coords+dX[n]], \
            [v_len/(v_len+0.75)], \
            [geom.atoms[n].element]]\
            for t in s)
    
        if v_len > 0.1:
            output += ".arrow %10.6f %10.6f %10.6f   %10.6f %10.6f %10.6f   0.02 0.05 %5.3f #%s\n" % info
    
    #convert bild string to model
    mdl = openBildString(output)
    
    if not isinstance(color, basestring):
        for m in mdl:
            m.color = color
    
    return mdl

def doFollow(cmdName, arg_str):
    """make an animation for the normal modes in the specified file"""
    from chimera import replyobj
    from AaronTools.fileIO import FileReader
    from AaronTools.geometry import Geometry
    from Movie.gui import MovieDialog
    from ChimAARON import ArgumentParser, Pathway2Ensemble

    parser = ArgumentParser()
    parser.addArg('nFrames', nargs=1, default=61, kind=int)
    parser.addArg('roundTrip', nargs=1, default=True, kind=bool)
    parser.addArg('maxDisplacement', nargs=1, default=None, kind=float)
    parser.addArg('mode', nargs=1, default="1", kind=str)

    replyobj.status("parsing input...")
    args = parser.parse_args(arg_str)    

    filename = args['other'][0]

    modes = parse_mode_str(args['mode'], int)
    roundtrip = args['roundTrip']
    nFrames = args['nFrames']
        
    if args['maxDisplacement'] is None:
        scale = [[0.2]*len(mode) for mode in modes]
    else:
        scale = parse_mode_str(args['maxDisplacement'], float)
    
    replyobj.status("loading Geometry...")
    G_AAron_file = FileReader(filename, just_geom=False)
    geom = Geometry(G_AAron_file)

    S = Freq2Pathway(geom, G_AAron_file.other['frequency'].data, modes, scale, roundtrip)
    
    ensemble = Pathway2Ensemble(S, nFrames)    
    ensemble.name = "mode %s from %s scaled by %s" % (str(modes), geom.name, str(scale))

    replyobj.status("creating interface...")
    MovieDialog(ensemble)

def doFreqBild(cmdName, arg_str):
    """display vectors for the normal modes in the specified file"""
    import os

    from chimera import replyobj, openModels, MaterialColor
    from AaronTools.fileIO import FileReader
    from AaronTools.geometry import Geometry
    from ChimAARON import ArgumentParser, AaronGeometry2ChimeraMolecule

    parser = ArgumentParser()

    parser.addArg('color', 1, default="green", kind="color")
    parser.addArg('scale', 1, default=None, kind=str)
    parser.addArg('mode', 1, default="1", kind=str)
    parser.addArg('massWeight', 1, default=True, kind=bool)
    
    replyobj.status("parsing input...")
    args = parser.parse_args(arg_str)
        
    filename = args['other'][0]
    
    replyobj.status("loading Geometry...")
    G_AAron_file = FileReader(filename, just_geom=False)
    geom = Geometry(G_AAron_file)
    
    modes = parse_mode_str(args['mode'], int)
        
    color = args['color']
    if not isinstance(color, basestring):
        color = MaterialColor(*color)
        
    if args['scale'] is None:
        scale = [[1.5]*len(mode) for mode in modes]
    else:
        scale = parse_mode_str(args['scale'], float)

    massweight = args['massWeight']

    mdl = Freq2Bild(geom, G_AAron_file.other['frequency'].data, modes, scale, massweight, color)   
    
    mol = AaronGeometry2ChimeraMolecule(geom)
    openModels.add([mol])
    openModels.add(mdl, sameAs=mol)
    
        