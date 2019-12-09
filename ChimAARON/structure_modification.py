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
            new_mols, oldMols = mapLigand(ligand, atoms)

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
            new_mols, old_mols = substitute(sub, atoms)
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
            new_mols, old_mols = closeRing(ring, atoms)
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
            from ChimAARON.library import ligandGUI

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

        self.selectLigandButton = Tkinter.Button(parent, text="from library...", command=self.openLigandSelectorGUI, pady=0)
        self.selectLigandButton.grid(row=row, column=2, sticky='ew')

        row += 1

        self.atomSelection = StringOption(parent, row, "Key atoms", "", None, balloon="Chimera OSL atom or model specifiers (space-delimited)")

        self.currentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.setCurrent, pady=0)
        self.currentSelectionButton.grid(row=row, column=2, sticky='ew')

        row += 1

        if extra_frame is not None:
            extra_frame.grid(row=row, column=0, sticky='ew', columnspan=3)
            row += 1

        self.doMapButton = Tkinter.Button(parent, text="map ligand", command=self.doMapLigand, pady=0)
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
            from ChimAARON.library import substituentGUI

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

        self.selectSubstituentButton = Tkinter.Button(parent, text="from library...", command=self.openSubstituentSelectorGUI, pady=0)
        self.selectSubstituentButton.grid(row=row, column=2, sticky='ew')

        row += 1

        self.atomSelection = StringOption(parent, row, "Atom selection", "", None, balloon="Chimera OSL atom specifiers (space-delimited)")

        self.currentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.setCurrent, pady=0)
        self.currentSelectionButton.grid(row=row, column=2, sticky='ew')

        row += 1

        if extra_frame is not None:
            extra_frame.grid(row=row, column=0, sticky='ew', columnspan=3)
            row += 1

        self.doSubButton = Tkinter.Button(parent, text="substitute", command=self.doSubstitute, pady=0)
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
            from ChimAARON.library import ringFragGUI

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

        self.selectRingButton = Tkinter.Button(parent, text="from library...", command=self.openRingFragGUI, pady=0)
        self.selectRingButton.grid(row=row, column=2, sticky='ew')

        row += 1

        self.atomSelection = StringOption(parent, row, "Atom selection", "", None, balloon="Chimera OSL atom specifiers (space-delimited)")

        self.currentSelectionButton = Tkinter.Button(parent, text="current selection", command=self.setCurrent, pady=0)
        self.currentSelectionButton.grid(row=row, column=2, sticky='ew')

        row += 1

        if extra_frame is not None:
            extra_frame.grid(row=row, column=0, sticky='ew', columnspan=3)
            row += 1

        self.doCloseRingButton = Tkinter.Button(parent, text="close ring", command=self.doCloseRing, pady=0)
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

def doSubstitute(cmdName, arg_str):
    """substitute a substituent for a different substituent"""
    from chimera import replyobj, openModels, selection
    from AaronTools.geometry import Geometry
    from AaronTools.substituent import Substituent
    from AaronTools.fileIO import FileWriter
    from Midas import _selectedAtoms
    from Midas.midas_text import getSpecs
    from ChimAARON import ArgumentParser

    parser = ArgumentParser()
    parser.addArg('form', 1, kind=str, default='from_library')
    parser.addArg('selec', 1, kind='selec', default='sel')
    parser.addArg('replace', 1, kind=bool, default=True)

    args = parser.parse_args(arg_str)

    substituent = args['other'][0]

    sel = args['selec']
    sub_form = args['form']

    atoms = _selectedAtoms(getSpecs(sel))

    new_mols, old_mols = substitute(substituent, atoms, form=sub_form)

    if not args['replace']:
        return new_mols, []
    else:
        return new_mols, old_mols

def substitute(sub_name, atoms, form='from_library'):
    """substitute one substituent for another"""
    from AaronTools.substituent import Substituent
    from ChimAARON import ChimeraMolecule2AaronGeometry, AaronGeometry2ChimeraMolecule

    known_mols = {}
    for atom in atoms:
        if atom.molecule not in known_mols:
            geom = ChimeraMolecule2AaronGeometry(atom.molecule)
            known_mols[atom.molecule] = {'geom':geom, 'targets':geom.find(str(atom.serialNumber))}
            geom = known_mols[atom.molecule]
        else:
            geom = known_mols[atom.molecule]['geom']
            known_mols[atom.molecule]['targets'].append(geom.find(str(atom.serialNumber))[0])

    new_mols = []
    for mol in known_mols:
        geom = known_mols[mol]['geom']
        targets = known_mols[mol]['targets']
        for target in targets:
            if form == 'from_library':
                sub = Substituent(sub_name)
            else:
                sub = Substituent.from_string(sub_name, form=form)

            geom.substitute(sub, target)
            geom.refresh_connected()

        new_mol = AaronGeometry2ChimeraMolecule(geom)
        new_mols.append(new_mol)

    return new_mols, known_mols.keys()

def doCloseRing(cmdName, arg_str):
    from AaronTools.ringfragment import RingFragment
    from Midas import _selectedAtoms
    from Midas.midas_text import getSpecs
    from ChimAARON import ArgumentParser

    parser = ArgumentParser()
    parser.addArg('form', 1, kind=str, default='from_library')
    parser.addArg('selec', 1, kind='selec', default='sel')
    parser.addArg('replace', 1, kind=bool, default=True)

    args = parser.parse_args(arg_str)

    ring_name = args['other'][0]

    atoms = _selectedAtoms(getSpecs('sel'))

    new_mols, old_mols = closeRing(ring_name, atoms, form=args['form'])

    if not args['replace']:
        return new_mols, []
    else:
        return new_mols, old_mols

def closeRing(ring_name, atoms, form='from_library'):
    from chimera import replyobj
    from AaronTools.ringfragment import RingFragment
    from ChimAARON import ChimeraMolecule2AaronGeometry, AaronGeometry2ChimeraMolecule

    known_mols = {}
    for atom in atoms:
        if atom.molecule not in known_mols:
            geom = ChimeraMolecule2AaronGeometry(atom.molecule)
            targets = geom.find(str(atom.serialNumber))
            known_mols[atom.molecule] = {'geom':geom, 'targets':targets}
        else:
            geom = known_mols[atom.molecule]['geom']
            targets = known_mols[atom.molecule]['targets']
            targets.extend(geom.find(str(atom.serialNumber)))

    new_mols = []
    for mol in known_mols:

        replyobj.status("loading ring %s..." % ring_name)
        if form == 'from_library':
            ring = RingFragment(ring_name)
        else:
            ring = RingFragment.from_string(ring_name, form=form)

        geom = known_mols[mol]['geom']
        targets = known_mols[mol]['targets']
        geom.ring_substitute(targets, ring)

        new_mol = AaronGeometry2ChimeraMolecule(geom)

        new_mols.append(new_mol)

    return new_mols, known_mols.keys()

def doMapLigand(cmdName, arg_str):
    """substitute one ligand for another"""
    from chimera import replyobj, selection
    from AaronTools.catalyst import Catalyst
    from AaronTools.component import Component
    from Midas import _selectedAtoms
    from Midas.midas_text import getSpecs
    from ChimAARON import ArgumentParser

    parser = ArgumentParser()
    parser.addArg('selec', 1, kind='selec', default='sel')
    parser.addArg('replace', 1, kind=bool, default=True)

    args = parser.parse_args(arg_str)

    ligand_name = args['other'][0]
    sel = args['selec']

    atoms = _selectedAtoms(getSpecs(sel))
    new_mols, old_mols = mapLigand(ligand_name, atoms)

    if not args['replace']:
        return new_mols, []
    else:
        return new_mols, old_mols

def mapLigand(ligand_name, atoms, form='from_library'):
    """substitute one ligand for another"""
    from chimera import replyobj
    from AaronTools.catalyst import Catalyst
    from AaronTools.component import Component
    from ChimAARON import ChimeraMolecule2AaronGeometry, AaronGeometry2ChimeraMolecule

    known_mols = {}
    for atom in atoms:
        if atom.molecule not in known_mols:
            cat = Catalyst(ChimeraMolecule2AaronGeometry(atom.molecule))
            targets = cat.find(str(atom.serialNumber))
            known_mols[atom.molecule] = {'cat':cat, 'key_atoms':targets}
        else:
            cat = known_mols[atom.molecule]['cat']
            targets = known_mols[atom.molecule]['key_atoms']
            targets.extend(cat.find(str(atom.serialNumber)))

    replyobj.status("loading ligand %s..." % ligand_name)
    if form == 'from_library':
        lig = Component(ligand_name)
    else:
        raise NotImplementedError("ligands must be loaded from the ligand library")

    replyobj.status("substituting the ligands...")

    new_mols = []
    for mol in known_mols:
        lig_copy = lig.copy()
        cat = known_mols[mol]['cat']
        targets = known_mols[mol]['key_atoms']
        cat.map_ligand(lig_copy, targets)

        new_mol = AaronGeometry2ChimeraMolecule(cat)

        new_mols.append(new_mol)

    return new_mols, known_mols.keys()
