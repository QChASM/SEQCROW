import Tkinter
import Pmw
import ChimAARON
import ttk

from ChimAARON import arn_input_manager
from chimera.baseDialog import ModelessDialog
from chimera.tkoptions import StringOption, EnumOption, BooleanOption, IntOption, FloatOption
from tkFileDialog import asksaveasfilename

class InputGenerator_templateSelector(ModelessDialog):
    """dialog prompting the user to select a ts template or resume and input recording"""
    title = "Select AARON Template"
    buttons = ("Apply", "Close",)

    help = ("tutorials/aaronInput.html", ChimAARON)

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

        self.recordNameOption = StringOption(parent, 1, "Record Name", "new record", None, balloon="name of AARON Input Recorder session")

class TsRestartGUI:
    """frame for restarting from an existing record"""
    def __init__(self, parent):
        from ChimAARON import arn_input_manager
        recordNames = sorted(arn_input_manager.records.keys())

        if not recordNames:
            recordNames = [None]

        self.recordOption = EnumOption(parent, 0, "Record name", recordNames[0], None, balloon="name of AARON Input Recorder session")
        self.recordOption.values = recordNames

        self.warn_about_kw = Tkinter.Label(parent, text="Note: keywords are not saved with input recordings")
        self.warn_about_kw.grid(row=1, column=0, columnspan=2)

class TsCustomGUI:
    """class for create a new record from scratch"""
    def __init__(self, parent):
        from CGLtk.Table import SortableTable
        from chimera import openModels, Molecule
        row = 0

        self.rxn_type_option = StringOption(parent, row, "Reaction type", "", None, balloon=keyWordGUI.getBallon('reaction_type'))
        row += 1

        self.template_option = StringOption(parent, row, "Template", "", None, balloon=keyWordGUI.getBallon('template'))
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

        self.recordNameOption = StringOption(parent, row, "Record Name", "new record", None, balloon="name of AARON Input Recorder session")
        row += 1

class InputGenerator_structureChanges(ModelessDialog):
    """dialog for recording substitutions, ligand mappings, input keywords"""
    oneshot = True
    provideStatus = True
    buttons = ("Save", "Close",)
    title = "AARON Input Recorder"

    help = ("tutorials/aaronInput.html", ChimAARON)
    
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

        from ChimAARON.structure_modification import MapLigandGUI, SubstituteGUI
        row = 0

        self.libraryMenu = ttk.Notebook(parent)

        #mapligand cell
        self.mapLigandFrame = Tkinter.Frame(parent)

        self.replaceLigandFrame = Tkinter.Frame(self.mapLigandFrame)
        self.hiddenLigandEntry = Tkinter.BooleanVar()
        self.hiddenLigandEntry.set(False)
        self.hiddenLigCheck = Tkinter.Checkbutton(self.replaceLigandFrame, text="Hide entry", indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.hiddenLigandEntry)
        self.hiddenLigCheck.grid(row=0, column=0, sticky='w')

        self.replaceLigand = Tkinter.BooleanVar()
        self.replaceLigand.set(False)
        self.replaceLigCheck = Tkinter.Checkbutton(self.replaceLigandFrame, text="Replace previous structure", indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.replaceLigand)
        self.replaceLigCheck.grid(row=1, column=0, sticky='w')

        self.mapLigandGUI = MapLigandGUI(self.mapLigandFrame, self, self.replaceLigandFrame)

        #mapping ligands with this tool only uses model selections
        self.mapLigandGUI.atomSelection._label.config(text="Model selection:")

        self.mapLigandFrame.grid(row=row, column=0, sticky='sew')

        self.libraryMenu.add(self.mapLigandFrame, text="Map Ligand")

        #substitute cell
        self.substituteFrame = Tkinter.Frame(parent)

        self.replaceSubFrame = Tkinter.Frame(self.substituteFrame)
        self.hiddenSubstituentEntry = Tkinter.BooleanVar()
        self.hiddenSubstituentEntry.set(False)
        self.hiddenSubCheck = Tkinter.Checkbutton(self.replaceSubFrame, text="Hide entry", indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.hiddenSubstituentEntry)
        self.hiddenSubCheck.grid(row=0, column=0, sticky='w')

        self.replaceSubstituent = Tkinter.BooleanVar()
        self.replaceSubstituent.set(False)
        self.replaceSubCheck = Tkinter.Checkbutton(self.replaceSubFrame, text="Replace previous structure", indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.replaceSubstituent)
        self.replaceSubCheck.grid(row=1, column=0, sticky='w')

        self.substituteGUI = SubstituteGUI(self.substituteFrame, self, self.replaceSubFrame)

        self.libraryMenu.add(self.substituteFrame, text="Substitute")

        #AARON input keywords
        self.keyWordFrame = Tkinter.Frame(parent)
        self.keyWordGUI = keyWordGUI(self.keyWordFrame, self)
        
        self.keyWordFrame.columnconfigure(0, weight=1)
        self.keyWordFrame.rowconfigure(1, weight=0)  
        
        self.substituteFrame.columnconfigure(0, weight=1)
        self.substituteFrame.rowconfigure(1, weight=0)  
        
        self.replaceLigandFrame.columnconfigure(0, weight=1)
        self.replaceLigandFrame.rowconfigure(1, weight=0)

        self.libraryMenu.add(self.keyWordFrame, text="Input Options")

        #AARON version option
        if self.perl:
            initialItem = "Perl"
        else:
            initialItem = "Python"
        self.versionOption = Pmw.OptionMenu(parent, initialitem=initialItem, \
                            command=self.setVersion, items=["Perl", "Python"], \
                            labelpos='w', label_text="AARON version:")
        self.versionOption.grid(row=row, column=0, sticky='sew')
        self.versionOption.rowconfigure(0, weight=0)

        row += 1

        self.libraryMenu.grid(row=row, column=0, sticky='new')
        self.libraryMenu.rowconfigure(1, weight=1)
        self.libraryMenu.columnconfigure(0, weight=0)

        row += 1

        #display input file
        #all other buttons and fields should be before this to make setting the rowspan easier
        self.inputDisplayArea = Tkinter.LabelFrame(parent, text="Input")
        self.inputDisplayArea.grid(row=0, column=1, sticky='nsew', rowspan=row+1)
        self.inputDisplayArea.columnconfigure(0, weight=1)
        self.inputDisplayArea.rowconfigure(0, weight=1)

        self.inputDisplay = Tkinter.Text(self.inputDisplayArea)
        self.inputDisplay.grid(row=0, column=0, sticky='nsew')
        self.inputScroll = Tkinter.Scrollbar(self.inputDisplayArea, command=self.inputDisplay.yview)
        self.inputScroll.grid(row=0, column=1, sticky='nsew')
        self.inputDisplay['yscrollcommand'] = self.inputScroll.set      

        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)

    def mapLigand(self, ligand_names, positions):
        """map ligands going through the AARON Input Manager
        ligand_names: list of ligand names from the library
        positions: string with OSL identifiers"""
        from chimera.selection import OSLSelection

        selec = OSLSelection(positions).molecules()

        hiddenEntry = self.hiddenLigandEntry.get()
        replaceModel = self.replaceLigand.get()

        for ligand in ligand_names:
            ChimAARON.arn_input_manager.mapLigand(self.record_name, selec, ligand, hiddenEntry, replaceModel)

        self.refresh_text()

    def substitute(self, substituents, positions):
        """substitute going through the AARON Input Manager
        substituents: list of substituent names from the library
        positions: string with OSL identifiers"""
        from chimera.selection import OSLSelection

        atoms = OSLSelection(positions).atoms()

        replaceModel = self.replaceSubstituent.get()
        hiddenEntry = self.hiddenSubstituentEntry.get()

        for sub in substituents:
            ChimAARON.arn_input_manager.subSomething(self.record_name, atoms, sub, hiddenEntry, replaceModel)

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

    def Save(self):
        SaveAARONInputGUI(self)

class keyWordGUI:
    """selector for AARON input keywords"""
    class SaveCustomDialog(ModelessDialog):
        buttons = ("Save", "Close")
        title = "Save AARON keywords"
        help = "https://github.com/QChASM/Aaron/wiki/More-on-AARON-Input-Files#custom-defaults"
        
        def __init__(self, origin):
            self.origin = origin
            ModelessDialog.__init__(self)
            
        def fillInUI(self, parent):
            self.customName = StringOption(parent, 0, "Name of custom", "NewCustom", None, balloon="name to refer to the AARON keyword preset")

        def Save(self):
            import os
            
            from AaronTools.const import HOME
            
            aaronrc_file = os.path.join(HOME, ".aaronrc")
            
            customName = self.customName.get()
            
            header = arn_input_manager.get_header(**self.origin.origin.kw_dict)
        
            options = [line for line in header.split('\n') if line]

            customs = read_custom_kw()
            if customName in customs:
                del customs[customName]
                
            customs[customName] = {}
            for opt in options:
                kw = opt.split('=')[0]
                val = opt.split('=')[1]
                if kw not in customs[customName]:
                    customs[customName][kw] = [val]
                else:
                    customs[customName][kw].append(val)
                        
            s = ''
            for key in customs:
                s += "%s\n" % key
                for kw in customs[key]:
                    s += "    %s=%s\n" % (kw, " ".join([str(val) for val in customs[key][kw]]))
                
                s += "\n"

            with open(aaronrc_file, 'w') as f:
                f.write(s.strip())
            
            self.origin.customDropdown.setitems([custom for custom in customs if '=' not in custom])
            
            self.Close()
    
    def __init__(self, parent, origin):
        """ origin should be the InputGenerator_structureChanges that created this"""
        self.origin = origin

        row = 0

        basis_kw, str_kw, float_kw, int_kw, bool_kw = ChimAARON.managers.InputManager.AARONKeyWords()
        self.all_kw = sorted(basis_kw + str_kw + float_kw + int_kw + bool_kw)

        #keyword selector dropdown menu
        self.kwSelector = Pmw.OptionMenu(parent, initialitem='custom', \
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

        # special dropdown menu for custom keyword
        customs = [key for key in read_custom_kw().keys() if '=' not in key]
        self.customDropdown = Pmw.OptionMenu(self.optionFrame['custom'], initialitem=customs[0], \
                                items=customs, \
                                command=self.optionGUI['custom'].set, \
                                labelpos='w')
        
        self.expandCustom = Tkinter.Button(self.optionFrame['custom'], text="Expand custom", pady=0, command=self.expandCustom)
        self.expandCustom.grid(row=1, column=0, sticky='ew', columnspan=3)
        
        self.customDropdown.grid(row=0, column=2, sticky='ew')
                
        self.curFormat = None
        self.showOptionGUI('custom')

        row += 1

        #set and unset buttons to add or remove a keyword from the input file
        self.optionSet = Tkinter.Button(parent, text="set", command=self.setOptionValue, pady=0)
        self.optionSet.grid(row=row, column=0, sticky='ew')
        self.optionSet.columnconfigure(0, weight=1)
        
        self.optionUnset = Tkinter.Button(parent, text="unset", command=self.unsetOptionValue, pady=0)
        self.optionUnset.grid(row=row, column=1, sticky='ew')
        self.optionUnset.columnconfigure(0, weight=1)
        
        row += 1
        
        self.saveKeywords = Tkinter.Button(parent, text="Save to .aaronrc", pady=0, command=lambda: self.SaveCustomDialog(self))
        self.saveKeywords.grid(row=row, column=0, sticky='ew', columnspan=2)
        
        row += 1
        
        self.unsetAllButton = Tkinter.Button(parent, text="Unset all keywords", pady=0, command=self.unsetAll)
        self.unsetAllButton.grid(row=row, column=0, sticky='ew', columnspan=2)
        
        row += 1

    def expandCustom(self):
        """expand the custom keyword to whatever is set in the .aaronrc file"""
        import os

        from AaronTools.const import HOME

        basis_kw, str_kw, float_kw, int_kw, bool_kw = ChimAARON.managers.InputManager.AARONKeyWords()

        custom_name = self.origin.kw_dict['custom']

        if custom_name is not None:
            customs = read_custom_kw()
            my_custom = customs[custom_name]
            for key in my_custom:
                if self.origin.kw_dict[key] is None:
                    if key in basis_kw:
                        self.origin.kw_dict[key] = my_custom[key]
                    else:
                        if key in float_kw:
                            self.origin.kw_dict[key] = float(my_custom[key][0])
                        
                        elif key in int_kw:
                            self.origin.kw_dict[key] = int(my_custom[key][0])
                        
                        elif key in bool_kw:
                            if my_custom[key][0].lower() in ['true', '1']:
                                self.origin.kw_dict[key] = True                            
                            elif my_custom[key][0].lower() in ['false', '0']:
                                self.origin.kw_dict[key] = False
                            else:
                                raise RuntimeError("expected one of %s for %s, got %s" % (", ".join(['true', '1', 'false', '0']), key, my_custom[key][0]))
                        
                        else:
                            self.origin.kw_dict[key] = my_custom[key][0]

            self.origin.kw_dict['custom'] = None
            self.origin.refresh_text()
        else:
            raise RuntimeWarning("'custom' keyword is not set")

    def showOptionGUI(self, format):
        """change the keyword that is displayed"""
        if format not in self.all_kw:
            return

        if self.curFormat:
            self.optionFrame[self.curFormat].grid_forget()

        self.optionFrame[format].grid(row=1, column=0, columnspan=2, sticky='ew')
        self.optionFrame[format].rowconfigure(1, weight=1)
        self.optionFrame[format].columnconfigure(0, weight=1)

        self.curFormat = format

    def setOptionValue(self):
        basis_kw, str_kw, float_kw, int_kw, bool_kw = ChimAARON.managers.InputManager.AARONKeyWords()
        value = self.optionGUI[self.curFormat].get()
        # basis keywords can have multiple values because different elements can use different basis sets
        if self.curFormat in basis_kw:
            if self.origin.kw_dict[self.curFormat] is None:
                self.origin.kw_dict[self.curFormat] = [value]
            else:
                element_and_basis = value.split()
                if len(element_and_basis) > 1:
                    basis = element_and_basis[-1]
                    elements = element_and_basis[:-1]
                    for i, val in enumerate(self.origin.kw_dict[self.curFormat]):
                        previous_ele_and_basis = val.split()
                        if len(previous_ele_and_basis) > 1:
                            prev_basis = previous_ele_and_basis[-1]
                            prev_ele = previous_ele_and_basis[:-1]
                            for element in elements:
                                if any([element == ele for ele in prev_ele]):
                                    prev_ele.remove(element)
 
                            if len(prev_ele) == 0:
                                del self.origin.kw_dict[self.curFormat][i]
                            elif prev_basis == basis:
                                del self.origin.kw_dict[self.curFormat][i]
                                value = "%s %s" % (" ".join(prev_ele), value)
                            else:
                                self.origin.kw_dict[self.curFormat][i] = "%s %s" % (" ".join(prev_ele), prev_basis)

                else:
                    for i, val in enumerate(self.origin.kw_dict[self.curFormat]):
                        if val.split()[-1] == value:
                            del self.origin.kw_dict[self.curFormat][i]
                        
                        elif len(val.split()) == 1:
                            del self.origin.kw_dict[self.curFormat][i]

                self.origin.kw_dict[self.curFormat].append(value)

        else:
            self.origin.kw_dict[self.curFormat] = value

        self.origin.refresh_text()

    def unsetOptionValue(self):
        basis_kw, str_kw, float_kw, int_kw, bool_kw = ChimAARON.managers.InputManager.AARONKeyWords()
        
        #basis kw get unset differently - can unset elements or basis set
        if self.curFormat in basis_kw:
            value = self.optionGUI[self.curFormat].get()
            if value:
                vals = value.split()
                for i, basis in enumerate(self.origin.kw_dict[self.curFormat]):
                    ele_and_basis = basis.split()
                    if len(ele_and_basis) > 1:
                        prev_basis = ele_and_basis[-1]
                        prev_ele = ele_and_basis[:-1]

                        #just a basis is being unset - delete any entries with that basis set
                        if len(vals) == 1 and prev_basis in vals:
                            del self.origin.kw_dict[self.curFormat][i]
                            continue

                        #check to see if any elements are being unset
                        for val in vals:
                            if any([val == ele for ele in prev_ele]):
                                prev_ele.remove(val)
                        
                        #if all elements have been removed for one basis set, delete that entry
                        if len(prev_ele) == 0:
                            del self.origin.kw_dict[self.curFormat][i]
                        #if any elements have been removed, remake that entry
                        else:
                            self.origin.kw_dict[self.curFormat][i] = "%s %s" % (" ".join(prev_ele), prev_basis)

                    else:
                        print(basis, vals)
                        if basis.endswith(value):
                            del self.origin.kw_dict[self.curFormat][i]
            
            else:
                self.origin.kw_dict[self.curFormat] = None
        else:        
            self.origin.kw_dict[self.curFormat] = None

        self.origin.refresh_text()

    def unsetAll(self):
        for kw in self.origin.kw_dict:
            self.origin.kw_dict[kw] = None

        self.origin.refresh_text()

    @classmethod
    def getBallon(cls, kw):

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

class SaveAARONInputGUI(ModelessDialog):
    title = "Save AARON Input File"
    buttons = ('Save', 'Close')
    help = ("tutorials/aaronInput.html", ChimAARON)

    
    def __init__(self, origin):
        self.origin = origin
        
        ModelessDialog.__init__(self)
        
    def fillInUI(self, parent):
        import os
        self.fileNameOption = StringOption(parent, 0, "AARON input location", os.path.join(os.getcwd(), self.origin.record_name + ".in"), None, balloon="name of AARON Input file")
        
        self.browseButton = Tkinter.Button(parent, text="Browse", pady=0, command=self.openFileBrowser)
        self.browseButton.grid(row=0, column=2)
    
    def openFileBrowser(self):
        import os
        outfile = asksaveasfilename(initialdir=os.getcwd(), initialfile=self.origin.record_name + ".in")
        
        if outfile:
            self.fileNameOption.set(outfile)
    
    def Save(self):        
        filename = self.fileNameOption.get()
        
        if filename:
            s = self.origin.inputDisplay.get("1.0", Tkinter.END)
            
            with open(filename, 'w') as f:
                f.write(s.strip())
                
        self.Close()

def doArnRecord(cmdName, arg_str):
    from chimera import openModels, replyobj
    from chimera.selection import OSLSelection, currentAtoms
    from AaronTools.catalyst import Catalyst
    from ChimAARON import ArgumentParser

    parser = ArgumentParser()

    parser.addArg("record", 0)
    parser.addArg("write", 0)
    #this will get all values that come after 'mapligand' and before another keyword
    parser.addArg("mapligand", 1, kind="selec")
    parser.addArg("substitute", 1, kind="selec")
    parser.addArg("models", 1, kind="selec")
    parser.addArg("ligPrefix", 1, default=None)
    parser.addArg("subPrefix", 1, default=None)
    parser.addArg("prefix", 1)
    parser.addArg("perl", 0)

    args = parser.parse_args(arg_str)

    name = args['other'][0]
    ligPrefix = args['ligPrefix']
    subPrefix = args['subPrefix']

    perl = args['perl']

    if args['write']:
        aaron_kw = getAARONkw(cmdName, " ".join(args['other'][1:]))
        inp = arn_input_manager.get_input(name, header=aaron_kw, perl=perl)
        print(inp)
        replyobj.status("printed to reply log")

    elif args['record']:
        replyobj.status("setting up record %s..." % name)
        model_ids = args['models']

        if model_ids is None:
            raise RuntimeError("no models specified for new record")

        arn_input_manager.newRecord(name, model_ids, ligPrefix=ligPrefix, subPrefix=subPrefix, perl=perl)

        replyobj.status("record named %s created" % name)

    elif bool(args['mapligand'] is not None) ^ (args['substitute'] is not None):

        if name not in arn_input_manager.records:
            raise RuntimeError("unrecognized record name: %s" % name)

        if args['mapligand'] is not None:
            command_arg_str = args['mapligand']
        else:
            command_arg_str = args['substitute']

        command_parser = ArgumentParser()

        command_parser.addArg("replaceOld", 1, default=False, kind=bool)
        command_parser.addArg("hiddenEntry", 1, default=False, kind=bool)

        command_args = command_parser.parse_args(command_arg_str)

        hidden = command_args['hiddenEntry']
        replace = command_args['replaceOld']

        if len(command_args['other']) > 1:
            osl_str = " ".join(command_args['other'][1:])
            if osl_str.startswith('sel'):
                sel = currentAtoms()
            else:
                sel = OSLSelection(" ".join(command_args['other'][1:])).atoms()
        else:
            sel = currentAtoms()

        if len(sel) == 0:
            raise RuntimeError("must specify selection")

        if args['mapligand'] is not None:
            ligand_name = command_args['other'][0]

            arn_input_manager.mapLigand(name, [sel[0].molecule], ligand_name, hidden, replace, ligPrefix)

        else:
            sub_name = command_args['other'][0]

            arn_input_manager.subSomething(name, sel, sub_name, hidden, replace, ligPrefix=ligPrefix, subPrefix=subPrefix)

    else:
        raise RuntimeWarning("must use 'record', 'mapligand', or 'substitute'")

def getAARONkw(cmdName, arg_str, perl=False):
    """cmdName - name of command that called this subroutine (value has no effect on output)
    arg_str - string of keyword arguments and values, like 'method B3LYP'
    perl - bool true if we are making a header for a perl AARON input file (python/false is not implemented)
    """
    basis_kw, str_kw, float_kw, int_kw, bool_kw = arn_input_manager.AARONKeyWords()

    parser = ArgumentParser()

    #Gaussian options
    for kw in basis_kw:
        parser.addArg(kw, 1, kind="selec")

    for kw in str_kw:
        parser.addArg(kw, 1)

    for kw in float_kw:
        parser.addArg(kw, 1, kind=float)

    for kw in int_kw:
        parser.addArg(kw, 1, kind=int)

    for kw in bool_kw:
        parser.addArg(kw, 0)

    args = parser.parse_args(arg_str)

    if len(args['other']) > 0:
        raise RuntimeWarning("the following keywords/values are not recognized:\n%s" % " ".join(args['other']))

    header = ""
    for kw in basis_kw:
        if args[kw] is not None:
            header += "%s=%s\n" % (kw, args[kw])

    for kw in str_kw:
        if args[kw] is not None:
            header += "%s=%s\n" % (kw, args[kw])

    for kw in float_kw:
        if args[kw] is not None:
            header+= "%s=%.2f\n" % (kw, args[kw])

    for kw in int_kw:
        if args[kw] is not None:
            header += "%s=%i\n" % (kw, args[kw])

    for kw in bool_kw:
        if args[kw] is not None:
            if args[kw]:
                header += "%s=true\n" % (kw)
            else:
                header += "%s=false\n" % (kw)

    return header

def read_custom_kw():
    """reads .aaronrc and returns a dictionary with all of the custom names
    replace with whatever the python AARON version is"""
    import os
    from AaronTools.const import HOME
    
    aaronrc_file = os.path.join(HOME, ".aaronrc")
    
    with open(aaronrc_file, 'r') as f:
        lines = f.readlines()
        
    lines = [line.rstrip() for line in lines]
    
    customs = {}

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip() == line and line.strip() != '':
            customs[line] = {}
            for opt in lines[i+1:]:
                i += 1
                if opt.lstrip() != opt and opt.strip() != '' and '=' in opt:
                    kw = opt.strip().split('=')[0].lower()
                    val = opt.strip().split('=')[1]
                    if kw not in customs[line]:
                        customs[line][kw] = [val]
                    else:
                        customs[line][kw].append(val)
                else:
                    break
        else:
            i += 1
    
    for custom in customs:
        print('custom', custom)
    
    return customs