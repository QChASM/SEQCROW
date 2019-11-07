import Tkinter
import Pmw
import ChimAARON

from chimera.baseDialog import ModelessDialog
from chimera.tkoptions import StringOption, EnumOption, BooleanOption, IntOption, FloatOption

class InputGenerator_templateSelector(ModelessDialog):
    """dialog prompting the user to select a ts template or resume and input recording"""
    title = "Select AARON Template"
    buttons = ("Apply", "Close",)
    
    def __init__(self):
        #currently displayed input recording format (from TS template, from loaded strux, resume)
        self.curFormat = None
        self.template_options = ["TS Template", "Custom"]
        
        if len(ChimAARON.arn_input_manager.records) > 0:
            self.template_options.append("Previous from Session")

        ModelessDialog.__init__(self)
        
    def fillInUI(self, parent):
        #select recording type
        self.template = Pmw.OptionMenu(parent, initialitem=self.template_options[-1], \
                            command=self.showTemplateFormat, items=self.template_options, \
                            labelpos='w', label_text="Template source:")
                            
        self.template.grid(row=0, column=0, sticky='new')
        self.template.rowconfigure(0, weight=1)
        
        self.curFormat = None
        self.frames = {}
        self.templateGUIs = {}
        
        self.frames["TS Template"] = Tkinter.Frame(parent)
        self.templateGUIs["TS Template"] = TsTemplateGUI(self.frames["TS Template"])
        
        self.frames["Custom"] = Tkinter.Frame(parent)
        self.templateGUIs["Custom"] = TsCustomGUI(self.frames["Custom"])

        self.frames["Previous from Session"] = Tkinter.Frame(parent)
        self.templateGUIs["Previous from Session"] = TsRestartGUI(self.frames["Previous from Session"])
        
        self.showTemplateFormat(self.template_options[-1])
        
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
                
    def showTemplateFormat(self, format):
        """change from one format to another"""
        if format not in self.template_options:
            return
        
        if self.curFormat:
            self.frames[self.curFormat].grid_forget()
            
        self.frames[format].grid(row=1, column=0, sticky='nsew')
        self.frames[format].rowconfigure(1, weight=1)
        self.frames[format].columnconfigure(0, weight=1)
        
        self.curFormat = format

        if self.curFormat == "Previous from Session":
            self.templateGUIs[self.curFormat].recordOption.remakeMenu()

    def Apply(self):
        """create a dialog for the selected format when the OK button is pressed"""
        from chimera import replyobj
        
        if self.curFormat == "Custom":
            template = self.templateGUIs[self.curFormat].template_option.get()
            rxn_type = self.templateGUIs[self.curFormat].rxn_type_option.get()
            name = self.templateGUIs[self.curFormat].recordNameOption.get()
            models = self.templateGUIs[self.curFormat].modelSelection.selected()
            if len(models) < 1:
                raise RuntimeWarning("No models selected in the table.")
                return
       
            modelids = " ".join([mol.oslIdent() for mol in models])

            InputGenerator_structureChanges(template=template, \
                                            reaction_type=rxn_type, \
                                            model_ids=modelids, \
                                            record_name=name, \
                                            overwrite=True)
            self.destroy()
        
        elif self.curFormat == "Previous from Session":
            record_name = self.templateGUIs[self.curFormat].recordOption.get()
            InputGenerator_structureChanges(record_name=record_name, overwrite=False)
            self.destroy()
        

class TsTemplateGUI:
    """frame for selecting a TS template"""
    def __init__(self, parent):
        self.placeholder = Tkinter.Label(parent, text="placeholder")
        
        self.placeholder.grid(row=0, column=0)
        
        self.recordNameOption = StringOption(parent, 1, "Record Name", "new record", None, balloon = "name of AARON Input Recorder session")

class TsRestartGUI:
    """frame for restarting from an existing record"""
    def __init__(self, parent):
        from ChimAARON import arn_input_manager
        recordNames = sorted(arn_input_manager.records.keys())
        
        if not recordNames:
            recordNames = [None]
        
        self.recordOption = EnumOption(parent, 0, "Record name", recordNames[0], None, balloon = "name of AARON Input Recorder session")
        self.recordOption.values = recordNames
        
        self.warn_about_kw = Tkinter.Label(parent, text="Note: keywords are not saved with input recordings")
        self.warn_about_kw.grid(row=1, column=0, columnspan=2)
                
class TsCustomGUI:
    """class for create a new record from scratch"""
    def __init__(self, parent):
        from CGLtk.Table import SortableTable
        from chimera import openModels, Molecule
        row = 0
        
        self.rxn_type_option = StringOption(parent, row, "Reaction type", "", None)
        row += 1 
        
        self.template_option = StringOption(parent, row, "Template", "", None)
        row += 1
        
        self.modelSelection = SortableTable(parent)
        open_mols = openModels.list(modelTypes=[Molecule])

        idCol = self.modelSelection.addColumn("ID", "lambda m: m.oslIdent()", format="%s")
        nameCol = self.modelSelection.addColumn("Name", "name", format="%s")
        
        self.modelSelection.setData(open_mols)
        self.modelSelection.launch()
        self.modelSelection.grid(row=row, column=0, columnspan=2, sticky='nsew')
        self.modelSelection.columnconfigure(0, weight=1)
        self.modelSelection.rowconfigure(row, weight=1)

        row += 1
        
        self.recordNameOption = StringOption(parent, row, "Record Name", "new record", None, balloon = "name of AARON Input Recorder session")
        row += 1
        
class InputGenerator_structureChanges(ModelessDialog):
    """dialog for recording substitutions, ligand mappings, input keywords"""
    oneshot = True
    provideStatus = True
    buttons = ("Close",)
    title = "AARON Input Recorder"
    
    def __init__(self, model_ids=None, \
                 perl=False, \
                 record_name="new record", \
                 overwrite=True, \
                 **kwargs):
        """model ids - OSLSelection identifiers for all involved models
        perl - bool/true when making Perl AARON input
        record_name - name of record for arn_input_manager
        overwrite - true to overwrite value in AARON Input Manager dictionary of records
        kwargs - AARON Input file keywords
        """
        from ChimAARON import arn_input_manager
        
        basis_kw, str_kw, float_kw, int_kw, bool_kw = arn_input_manager.AARONKeyWords()

        all_kw = basis_kw + str_kw + float_kw + int_kw + bool_kw
        
        #TODO:
        #store keyword values in preferences
        self.kw_dict = {}
        
        for kw in all_kw:
            if kw in kwargs:
                self.kw_dict[kw] = kwargs[kw]
            else:
                self.kw_dict[kw] = None
        
        self.perl = perl
        self.record_name = record_name
        
        if overwrite:
            arn_input_manager.newRecord(self.record_name, model_ids)
        
        ModelessDialog.__init__(self)
        self.refresh_text()

    def fillInUI(self, parent):        
        row = 0

        #mapligand cell
        self.mapLigandFrame = Tkinter.LabelFrame(parent, text='Map Ligand')
        self.mapLigandGUI = MapLigandGUI(self.mapLigandFrame, self)
        self.mapLigandFrame.grid(row=row, column=0, sticky='sew')
        row += 1

        #substitute cell
        self.substituteFrame = Tkinter.LabelFrame(parent, text='Substitute')
        self.substituteGUI = SubstituteGUI(self.substituteFrame, self)
        self.substituteFrame.grid(row=row, column=0, sticky='new')
        row += 1
        
        #AARON input keywords
        self.keyWordFrame = Tkinter.LabelFrame(parent, text='Set Input Options')
        self.keyWordGUI = keyWordGUI(self.keyWordFrame, self)
        self.keyWordFrame.grid(row=row, column=0, sticky='new')
        row += 1
        
        #AARON version option
        if self.perl:
            initialItem = "Perl"
        else:
            initialItem = "Python"
        self.versionOption = Pmw.OptionMenu(parent, initialitem=initialItem, \
                            command=self.setVersion, items=["Perl", "Python"], \
                            labelpos='w', label_text="AARON version:")
        self.versionOption.grid(row=row, column=0, sticky='nsew')
        row += 1
        
        #display input file
        #all other buttons and fields should be before this to make setting the rowspan easier
        self.inputDisplayArea = Tkinter.LabelFrame(parent, text="Input")
        self.inputDisplayArea.grid(row=0, column=1, sticky='nsew', rowspan=row+1)
        self.inputDisplayArea.rowconfigure(0, weight=1)
        self.inputDisplayArea.columnconfigure(1, weight=1)
        
        self.inputDisplay = Tkinter.Text(self.inputDisplayArea)
        self.inputDisplay.grid(row=0, column=0, sticky='nsew')
        self.inputScroll = Tkinter.Scrollbar(self.inputDisplayArea, command=self.inputDisplay.yview)
        self.inputScroll.grid(row=0, column=1, sticky='nsew')
        self.inputDisplay.rowconfigure(0, weight=1)
        self.inputDisplay.columnconfigure(0, weight=1)
        self.inputDisplay['yscrollcommand'] = self.inputScroll.set    

        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

    def mapLigand(self, ligand_names, positions):
        """map ligands going through the AARON Input Manager
        ligand_names: list of ligand names from the library
        positions: string with OSL identifiers"""
        from chimera.selection import OSLSelection
        
        atoms = OSLSelection(positions).atoms()
                
        for ligand in ligand_names:
            ChimAARON.arn_input_manager.mapLigand(self.record_name, atoms, ligand)
    
        self.refresh_text()
    
    def substitute(self, substituents, positions):
        """substitute going through the AARON Input Manager
        substituents: list of substituent names from the library
        positions: string with OSL identifiers"""
        from chimera.selection import OSLSelection
        
        atoms = OSLSelection(positions).atoms()
                
        for sub in substituents:
            ChimAARON.arn_input_manager.subSomething(self.record_name, atoms, sub)
  
        self.refresh_text()
    
    def setVersion(self, version):
        """set the input file to display in Perl format or Python format"""
        if version == "Python":
            self.perl = False
        
        if version == "Perl":
            self.perl = True
            
        self.refresh_text()
    
    def refresh_text(self):
        """update the input file text - should be called after every event that would change the input file"""
        input = ChimAARON.arn_input_manager.get_input(self.record_name, perl=self.perl, **self.kw_dict)
        
        self.inputDisplay.delete("1.0", Tkinter.END)
        self.inputDisplay.insert(Tkinter.END, input)

class keyWordGUI:
    """selector for AARON input keywords"""                        
    def __init__(self, parent, origin):
        """ origin should be the InputGenerator_structureChanges that created this"""
        self.origin = origin
        
        row = 0
        
        basis_kw, str_kw, float_kw, int_kw, bool_kw = ChimAARON.arnmngr.InputManager.AARONKeyWords()
        self.all_kw = sorted(basis_kw + str_kw + float_kw + int_kw + bool_kw)
        
        #keyword selector dropdown menu
        self.kwSelector = Pmw.OptionMenu(parent, initialitem=self.all_kw[0], \
                                command=self.showOptionGUI, items=self.all_kw, \
                                labelpos='w', label_text="Keyword:")
        
        self.kwSelector.grid(row=row, column=0, sticky='ew')
        self.kwSelector.rowconfigure(row, weight=1)
        self.kwSelector.columnconfigure(0, weight=0)
        
        row += 1
        
        #create a frame to display when an input keyword is selected
        self.optionFrame = {}
        self.optionGUI = {}
        for kw in basis_kw + str_kw:
            self.optionFrame[kw] = Tkinter.Frame(parent)
            self.optionGUI[kw] = StringOption(self.optionFrame[kw], 0, kw, "", None, balloon=self.getBallon(kw))
            
        for kw in float_kw:
            self.optionFrame[kw] = Tkinter.Frame(parent)
            self.optionGUI[kw] = FloatOption(self.optionFrame[kw], 0, kw, 0, None, balloon=self.getBallon(kw))
            
        for kw in int_kw:
            self.optionFrame[kw] = Tkinter.Frame(parent)
            self.optionGUI[kw] = IntOption(self.optionFrame[kw], 0, kw, 0, None, balloon=self.getBallon(kw))
            
        for kw in bool_kw:
            self.optionFrame[kw] = Tkinter.Frame(parent)
            self.optionGUI[kw] = BooleanOption(self.optionFrame[kw], 0, kw, 0, None, balloon=self.getBallon(kw))
        
        self.curFormat = None
        self.showOptionGUI(self.all_kw[0])
        
        row += 1
        
        #set and unset buttons to add or remove a keyword from the input file
        self.optionSet = Tkinter.Button(parent, text="set", command=self.setOptionValue)
        self.optionSet.grid(row=row, column=0, sticky='ew')
        self.optionUnset = Tkinter.Button(parent, text="unset", command=self.unsetOptionValue)
        self.optionUnset.grid(row=row, column=1, sticky='ew')
 
        row += 1

    def showOptionGUI(self, format):
        """change the keyword that is displayed"""
        if format not in self.all_kw:
            return
        
        if self.curFormat:
            self.optionFrame[self.curFormat].grid_forget()
            
        self.optionFrame[format].grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.optionFrame[format].rowconfigure(1, weight=1)
        self.optionFrame[format].columnconfigure(0, weight=1)
        
        self.curFormat = format

    def setOptionValue(self):
        value = self.optionGUI[self.curFormat].get()
        self.origin.kw_dict[self.curFormat] = value

        self.origin.refresh_text()    
        
    def unsetOptionValue(self):
        self.origin.kw_dict[self.curFormat] = None

        self.origin.refresh_text()

    def getBallon(self, kw):        
        if kw == "method":
            return "DFT functional used for steps 2-4 (structure optimization and thermal corrections)"
            
        elif kw == "basis":
            return "basis set used for steps 2-4 (structure optimization and thermal corrections)\n" + \
                    "you can specify elements that the basis set applies to if using multiple basis sets\n" + \
                    "e.g. C N H O 6-31G\n" + \
                    "tm is a synonym for any transistion metal"
            
        elif kw == "ecp":
            return "effective core potential used for steps 2-4 (structure optimization and thermal corrections)\n" + \
                    "you can specify elements that the ECP applies\n" + \
                    "e.g. Ir SDD\n" + \
                    "tm is a synonym for any transistion metal"
                    
        elif kw == "high_method":
            return "DFT functional used for step 5 (single point energy)"
            
        elif kw == "high_basis":
            return "basis set used for steps 5 (single point energy)\n" + \
                    "you can specify elements that the basis set applies to if using multiple basis sets\n" + \
                    "e.g. C N H O 6-31G\n" + \
                    "tm is a synonym for any transistion metal"

        elif kw == "high_ecp":
            return "effective core potential used for steps 5 (single point energy)\n" + \
                    "you can specify elements that the ECP applies\n" + \
                    "e.g. Ir SDD\n" + \
                    "tm is a synonym for any transistion metal"

        elif kw == "high_solvent":
            return "solvent used for step 5 (single point energy)"
            
        elif kw == "high_solvent_model":
            return "implicit solvent model used for step 5 (single point energy)"
            
        elif kw == "low_method":
            return "DFT functional or semi-empirical method used for step 1 (coarse optimization of new ligands/substituents)"
            
        elif kw == "low_basis":
            return "basis set used when using DFT for step 1 (coarse optimization of new ligands/substituents)"
            
        elif kw == "temperature":
            return "temperature in K for thermal corrections"
            
        elif kw == "denfit":
            return "whether or not density fitting is used"
            
        elif kw == "charge":
            return "total charge of the system"
            
        elif kw == "mult":
            return "spin multiplicity"
            
        elif kw == "solvent_model":
            return "implicit solvent model used for steps 2-4 (geometry optimization and thermal corrections)"
            
        elif kw == "solvent":
            return "solvent used for steps 2-4 (geometry optimization and thermal corrections)"
            
        elif kw == "grid":
            return "integration grid keyword"
            
        elif kw == "gen":
            return "name of gen basis set"
        
        elif kw == "emp_dispersion":
            return "empirical dispersion keyword (e.g. GD3)"
            
        elif kw == "custom":
            return "alias for custom defaults from your AARON rc file"
            
        elif kw == "n_procs":
            return "number of processors to use for steps 2-5"
            
        elif kw == "wall":
            return "walltime in hours for steps 2-5"
            
        elif kw == "short_procs":
            return "number of processors to use for step 1"
            
        elif kw == "short_wall":
            return "walltime in hours for step 1"
            
        elif kw == "submission_template":
            return "path to a job template file to use instead of $QCHASM/AaronTools/template.job"
            
        elif kw == "reaction_type":
            return "name of a TS library"
            
        elif kw == "template":
            return "name of the template for the specified TS library (reaction_type)"
            
        elif kw == "input_conformers":
            return "whether or not to do a conformer search\n" + \
                    "default: true"
            
        elif kw == "full_conformers":
            return "whether or not to do a heirarchical conformer search\n" + \
                    "default: true"
            
        elif kw == "multistep":
            return "whether or not the reaction is multistep\n" + \
                    "default: false"
            
        elif kw == "rmsd_cutoff":
            return "RMSD cutoff for deciding if a conformer is a duplicate\n" + \
                    "default: 0.15"
            
        elif kw == "d_cutoff":
            return "amount a constrained bond is allowed to change in step 3 (unconstrained optimization)\n" + \
                    "before reverting to a previous step\n" + \
                    "default: 0.35"
                    
        else:
            return "tell Tony he forgot about the balloon for %s" % kw

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
        
    def __init__(self, parent, origin):
        self.origin = origin
        
        row = 0
        self.ligandName = StringOption(parent, row, "Ligand", "", None, balloon="name of ligands in AaronTools Ligand Library")

        self.selectLigandButton = Tkinter.Button(parent, text="From library...", command=self.openLigandSelectorGUI)
        self.selectLigandButton.grid(row=row, column=2, sticky='ew')
    
        row += 1

        self.atomSelection = StringOption(parent, row, "Key atoms", "", None, balloon="Chimera OSL atom specifiers (space-delimited)")
        
        self.currentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.setCurrent)
        self.currentSelectionButton.grid(row=row, column=2, sticky='ew')
        
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
        
    def __init__(self, parent, origin):
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

        
        
        
        
        