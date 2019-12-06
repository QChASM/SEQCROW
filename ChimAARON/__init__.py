import managers
arn_input_manager = managers.InputManager()

def AaronGeometry2ChimeraMolecule(geom, tagList=False):
    """convert AaronTools Geometry to Chimera Molecule"""
    from chimera import Coord, Molecule, Element, connectMolecule
    from re import search

    #create new molecule and residue
    m = Molecule()
    r = m.newResidue("UNK", " ", 1, " ")
    #chimera uses the comment line to name molecules
    if geom.comment:
        m.name = geom.comment
    else:
        m.name = "molecule"

    #convert each atom. assign it a serial number
    atomElements = {}
    for i, atom in enumerate(geom.atoms):
        if atom.element not in atomElements:
            atomElements[atom.element] = 1
        else:
            atomElements[atom.element] += 1

        element = Element(atom.element)
        a = m.newAtom("%s%i" % (atom.element, atomElements[atom.element]), element)
        r.addAtom(a)
        a.setCoord(Coord(*atom.coords))
        a.serialNumber = i + 1
        if tagList:
            a.tag = tagList[i]

    #connect the graphs and draw bonds
    connectMolecule(m)

    return m

def ChimeraMolecule2AaronGeometry(mol):
    """convert chimera Molecule to AaronTools Geometry"""
    from AaronTools.geometry import Geometry
    from AaronTools.atoms import Atom

    #create a list of AaronTools atoms from the Molecule atoms

    atoms = []
    for atom in mol.atoms:
        if not atom.__destroyed__ and atom.name != "ghost":
            atoms.append(ChimeraAtom2AaronAtom(atom))

    #make Geometry
    geom = Geometry(atoms, mol.name, mol.name)

#    for chimatom, arn_atom in zip(mol.atoms, geom.atoms):
#        connected = []
#        for bonds in chimatom.bonds:
#            for bonded_atom in bonds.atoms:
#                if bonded_atom != chimatom:
#                    connected.append(geom.atoms[bonded_atom.serialNumber-1])
#

#        arn_atom.connected = set(connected)

    return geom

def ChimeraAtom2AaronAtom(atom):
    """convert chimer Atom to AaronTools atom"""
    from AaronTools.atoms import Atom

    aaron_atom = Atom(str(atom.element), [x for x in atom.xformCoord()], name = str(atom.serialNumber))
    return aaron_atom

def parse_Aaron_comment(mol):
    """parse mol's comment line and return a dictionary with the atom numbers that are
    in the ligand, catalyst center, and substrate"""
    from AaronTools.const import TMETAL

    out = {}
    #chimera stores the comment of xyz files as the name of the Molecule
    s = mol.name
    #try to parse the comment
    try:
        for part in s.split():
            if part.startswith('C'):
                out['C'] = [int(atom) for atom in part[2:].rstrip(';').split(',')]
                out['S'] = [atom for atom in range(1, min(out['C']))]

            elif part.startswith('L'):
                r = [int(atom) for atom in part[2:].rstrip(';').split('-')]
                out['L'] = [atom for atom in range(r[0], r[1]+1)]
    except:
        pass

    #if we didn't find a catalyst center, try to treat this as a trasition metal-catalyzed system
    if 'C' not in out:
        for atom in mol.atoms:
            if str(atom.element) in TMETAL:
                out['C'] = [atom.serialNumber]
                out['S'] = [atom for atom in range(1, out['C'][0])]
                out['L'] = [atom for atom in range(out['C'][0] + 1, len(mol.atoms) + 1)]
                break

    return out

def Pathway2Ensemble(path, nFrames):
    """make a movie with nFrames out of AaronTools Pathway"""
    from numpy import linspace

    geometries = [path.Geom_func(t) for t in linspace(0, 1, nFrames)]

    ensemble = GeomList2Ensemble(geometries)

    return ensemble

def GeomList2Ensemble(geom_list):
    """takes a list of geometries and returns an ensemble"""
    import chimera

    chimera.replyobj.status("creating ensemble...")
    mol = AaronGeometry2ChimeraMolecule(geom_list[0])
    for atom in mol.atoms:
        # I don't know what altLoc is supposed to be, but if it's false, we

        # can't draw pseudobonds to metals very easily
        atom.altLoc = "1"

    crdSet1 = mol.activeCoordSet

    for i, geom in enumerate(geom_list[1:]):

        setID = crdSet1.id + i + 1
        crdSet = mol.newCoordSet(setID)
        for a1, a2 in zip(mol.atoms, geom.atoms):
            x2 = chimera.Point(*a2.coords)
            a1.setCoord(x2, crdSet)

    class GeomTraj:
        def __len__(self):
            return len(self.molecule.coordSets)

    ensemble = GeomTraj()
    ensemble.startFrame = 1
    ensemble.endFrame = len(geom_list)
    ensemble.molecule = mol
    ensemble.name = mol.name

    return ensemble

def doAARON_SCL(cmdName, arg_str):
    """label atoms according to AARON relative numbering for substrate/ligand"""
    import chimera

    mols = chimera.openModels.list(modelTypes=[chimera.Molecule])

    #try using AaronTools parse_comment at some point...
    for mol in mols:
        components = parse_Aaron_comment(mol)

        if not all([key in components for key in ['C', 'S', 'L']]):
            return

        for atom in mol.atoms:
            if atom.serialNumber in components['S']:
                atom.label = "%s%i" % ('S', atom.serialNumber)
            elif atom.serialNumber in components['C']:
                atom.label = "%s%i" % ('C', atom.serialNumber - components['C'][0] + 1)
            elif atom.serialNumber in components['L']:
                atom.label = "%s%i" % ('L', atom.serialNumber - components['C'][-1])

def doPrintXYZ(cmdName, sel):
    """print selected atoms to reply log"""
    from chimera import replyobj
    from AaronTools.geometry import Geometry
    from AaronTools.fileIO import FileWriter
    from Midas import _selectedAtoms
    from Midas.midas_text import getSpecs

    #get a list of selected atoms - sel = "" will use all loaded atoms
    atoms = _selectedAtoms(getSpecs(sel), asDict=False)
    replyobj.status("converting to AaronTools Atoms...")
    aaron_atoms = [ChimeraAtom2AaronAtom(atom) for atom in atoms]
    #make AaronTools Geometry - note: atoms become disordered when we use _selectedAtoms
    geom = Geometry([ChimeraAtom2AaronAtom(atom) for atom in sorted(atoms, key=lambda atom: atom.serialNumber)], "current selection")

    print(FileWriter.write_xyz(geom, append=False, outfile=False))
    replyobj.status("printed to reply log")

def doRmsdAlign(cmdName, arg_str):
    from chimera import Coord, replyobj, specifier

    parser = ArgumentParser()

    parser.addArg('sort', 0, default=False)
    parser.addArg('longsort', 0, default=False)

    args = parser.parse_args(arg_str)

    sel = " ".join(args['other'])

    if sel.strip() == "":
        sel = 'sel'

    atoms = specifier.evalSpec(sel).atoms()
    known_mols = {}
    first_mol = None

    for atom in atoms:
        mol = atom.molecule
        if first_mol is None:
            first_mol = atom.molecule

        if mol not in known_mols:
            geom = ChimeraMolecule2AaronGeometry(mol)
            known_mols[mol] = {'geom':geom, 'targets':[geom.find(str(atom.serialNumber))[0]]}
        else:
            known_mols[mol]['targets'].append(known_mols[mol]['geom'].find(str(atom.serialNumber))[0])

    for mol in known_mols:
        known_mols[mol]['geom'].RMSD(known_mols[first_mol]['geom'], align=True, \
                targets=known_mols[mol]['targets'], ref_targets=known_mols[first_mol]['targets'], sort=args['sort'], longsort=args['longsort'])

        for i in range(0, len(mol.atoms)):
            mol.atoms[i].setCoord(Coord(*known_mols[mol]['geom'].atoms[i].coords))

def doTSBond(cmdName, arg_str):
    from chimera import MaterialColor, specifier, Bond, replyobj, Element
    from chimera.colorTable import colors

    parser = ArgumentParser()

    parser.addArg('selec', 1, default='sel', kind="selec")
    parser.addArg('color', 1, default='byatom', kind="color")
    parser.addArg('transparency', 1, default=50, kind=float)

    replyobj.status("parsing arguments...")
    args = parser.parse_args(arg_str)

    transparency = args['transparency']

    #get color
    if isinstance(args['color'], str) and not args['color'] == 'byatom':
        replyobj.warning("color is not 'byatom' - consider selecting the bonds and using the command\n" \
                "`color %s,b sel; trans %i,b sel`\n" % (args['color'], transparency) + \
                "as it would result in the same appearance, but does not destroy the bond")

        #color is named color - get from color table
        #color table values are 0-255
        color = colors[args['color']]
        #add in transparency
        color = tuple(c/255. for c in color) + (1 - transparency/100.,)
        color = MaterialColor(*color)
    elif args['color'] == 'byatom':
        #color byatom - use the connected atoms' colors sort of like halfbond mode
        color = 'byatom'
    else:
            #rgb[a] tuple was given
        color = args['color']
        if len(color) == 4:
            replyobj.warning("color is not 'byatom' - consider selecting the bonds and using the command\n" \
                    "`color %s,b sel`\n" % (",".join(str(c) for c in args['color'])) + \
                    "as it would result in the same appearance, but does not destroy the bond")

            transparency = 100 - list(color)[-1]*100
        else:
            color += (1 - transparency/100.,)
            replyobj.warning("color is not 'byatom' - consider selecting the bonds and using the command\n" \
                    "`color %s,b sel; trans %i,b sel`\n" % (",".join(str(c) for c in args['color']), transparency) + \
                    "as it would result in the same appearance, but does not destroy the bond")

        color = MaterialColor(*color)

    transparency = 100 - transparency

    transparency /= 100.

    sel = args['selec']

    atoms = [specifier.evalSpec(sel).atoms()]
    if len(atoms[0]) != 2 and len(atoms[0]) != 0:
        raise ValueError("must select either 2 atoms or any number of bonds; %i atoms selected" % len(atoms))
    elif len(atoms[0]) == 0:
        bonds = specifier.evalSpec(sel).bonds()
        atoms = [bond.atoms for bond in bonds]
    elif len(atoms[0]) == 2:
        m = atoms[0][0].molecule
        if not any([mbond.contains(atoms[0][0]) and mbond.contains(atoms[0][1]) for mbond in m.bonds]):
            #create a new bond b/c we need to know what the bond radius is
            bonds = [m.newBond(*atoms[0])]
            for bond in bonds:
                bond.drawMode = Bond.Stick
        else:
            bonds = [mbond for mbond in m.bonds if mbond.contains(atoms[0][0]) and mbond.contains(atoms[0][1])]

    replyobj.status("creating partial bonds...")
    for ts_bond in bonds:
        m = ts_bond.molecule
        atom_pair = ts_bond.atoms
        r = atom_pair[0].residue

        if ts_bond.drawMode >= 1:
            radius = ts_bond.radius*ts_bond.molecule.stickScale

        if color == 'byatom':
            color1 = atom_pair[0].color
            if color1 is None:
                color1 = m.color

            color1_rgba = list(color1.rgba())
            color1_rgba[-1] = transparency
            color1 = MaterialColor(*color1_rgba)

            color2 = atom_pair[1].color
            if color2 is None:
                color2 = m.color

            color2_rgba = list(color2.rgba())
            color2_rgba[-1] = transparency
            color2 = MaterialColor(*color2_rgba)

        else:
            color1 = color
            color2 = color

        ghostElement1 = Element(atom_pair[0].element)
        ghostElement2 = Element(atom_pair[1].element)

        ghostAtom1 = m.newAtom(atom_pair[0].name, ghostElement1)
        ghostAtom2 = m.newAtom(atom_pair[1].name, ghostElement2)
        r.addAtom(ghostAtom1)
        r.addAtom(ghostAtom2)
        for coordset in m.coordSets:
            ghostAtom1.setCoord(m.coordSets[coordset].coords()[atom_pair[0].coordIndex], m.coordSets[coordset])
            ghostAtom2.setCoord(m.coordSets[coordset].coords()[atom_pair[1].coordIndex], m.coordSets[coordset])
        ghostAtom1.color = color1
        ghostAtom2.color = color2
        ghostAtom1.radius = atom_pair[0].radius
        ghostAtom2.radius = atom_pair[1].radius
        ghostAtom1.name = "ghost"
        ghostAtom2.name = "ghost"

        new_bond = m.newBond(ghostAtom1, ghostAtom2)
        new_bond.display = Bond.Always
        new_bond.drawMode = ts_bond.drawMode

        ghostAtom1.display = False
        ghostAtom2.display = False

        ts_bond.molecule.deleteBond(ts_bond)

def doAllGeom(cmdName, arg_str):
    """read all geometries and make a movie"""
    from chimera import replyobj
    from AaronTools.fileIO import FileReader, read_types
    from AaronTools.geometry import Geometry
    from Movie.gui import MovieDialog, ScriptDialog
    from Movie.prefs import prefs, SCRIPT_PYTHON, DICT_NAME

    parser = ArgumentParser()
    parser.addArg('roundTrip', nargs=1, default=False, kind=bool)
    parser.addArg('dynamicBonds', nargs=1, default=True, kind=bool)

    replyobj.status("parsing arguments...")

    args = parser.parse_args(arg_str)

    files = [f for f in args['other'] if any([f.endswith(ext) for ext in read_types])]

    for filename in files:
        replyobj.status("reading %s..." % filename)
        f = FileReader(filename, get_all=True)
        geoms = [Geometry(geom) if not isinstance(geom, tuple) else Geometry(geom[-1]) for geom in f.all_geom]

        if args['roundTrip']:
            geoms += geoms[-2:0:-1]

        ensemble = GeomList2Ensemble(geoms)

        movie = MovieDialog(ensemble)
        replyobj.status("loaded trajectory")
        if args['dynamicBonds']:
            script = getDynamicBondScript(cmdName, arg_str)
            movie.scriptDialog = ScriptDialog(movie)
            movie.scriptDialog._setFrameSubst(SCRIPT_PYTHON)
            movie.scriptDialog.scriptText.insert('insert', script)
            movie.scriptDialog.scriptType.setvalue(SCRIPT_PYTHON)
            movie.scriptDialog.Cancel()

            movie.setScript(script, SCRIPT_PYTHON, frameSubst=prefs[DICT_NAME])

            replyobj.status("Movie script set to dynamically break and form bonds")

def getDynamicBondScript(cmdName, arg_str):
    """return a script for a movie that will make bonds dynamic"""
    from Movie.prefs import prefs, DICT_NAME

    parser = ArgumentParser()
    parser.addArg('drawMode', nargs=1, default="Stick", kind=str)

    args = parser.parse_args(arg_str)

    script = """from chimera import connectMolecule, Bond, OpenModels, makePseudoBondsToMetals
from chimera.misc import getPseudoBondGroup

mol = %s['mol']

for bond in mol.bonds:
    mol.deleteBond(bond)

if mol.id == OpenModels.Default:
    cat = "coordination complexes of %%s " %% (mol.name,)
else:
    cat = "coordination complexes of %%s (%%s)" %% (mol.name, mol)

coordination_pb = getPseudoBondGroup(cat, associateWith=[mol])
coordination_pb.deleteAll()

connectMolecule(mol)
""" % prefs[DICT_NAME]
    script += """
for bond in mol.bonds:
    bond.drawMode = Bond.%s

makePseudoBondsToMetals([mol])
""" % args['drawMode']

    return script

class ArgumentParser:
    def __init__(self):
        self.keywords = {}

    def addArg(self, keyword, nargs, default=None, kind=str):
        if nargs == 0:
            self.keywords[keyword] = {'value':False, 'n':0, "type":str}
        else:
            self.keywords[keyword] = {'value':default, 'n':nargs, 'type':kind}

    def parse_args(self, arg_str):
        """parse arguments in self.keywords"""
        from chimera.colorTable import colors

        out = {key:self.keywords[key]['value'] for key in self.keywords}
        out['other'] = []

        args = arg_str.split()
        i = 0
        while i < len(args):
            arg = args[i]
            if any([key.startswith(arg) for key in self.keywords]):
                keys = [key for key in self.keywords if key.startswith(arg)]
                if len(keys) > 1:
                    #multiple keywords could correspond to this abbreviated argument
                    raise ValueError("%s is ambiguous in %s" % (s, arg_str))
                else:
                    i += 1
                    key = keys[0]

                if self.keywords[key]["type"] == 'color':
                    #color argument is treated differently
                    #if it's and r,g,b[,a] tuple, return a tuple of those values
                    #otherwise, try to find a color with that name
                    joined_colors = {''.join(c.split()):c for c in colors if c.count(' ') > 0}

                    try_color = args[i]
                    i += 1
                    if try_color.count(',') in [2,3]:
                        out[key] = tuple([float(x) for x in try_color.split(',')])
                    else:
                        while i < len(args) and \
                          try_color not in colors and try_color not in joined_colors and \
                          len(try_color) > 1:
                            try_color += " %s" % args[i]
                            i += 1

                        if try_color not in colors and try_color not in joined_colors and len(try_color) > 1:
                            raise ValueError("color name not recognized: %s" % try_color)
                        else:
                            if try_color in joined_colors:
                                out[key] = joined_colors[try_color]
                            else:
                                out[key] = try_color

                elif self.keywords[key]["type"] == 'selec':
                    #for atom selections, keep grabbing arguments until we find another keyword
                    out[key] = ""
                    while i < len(args) and not any([outkey.startswith(args[i]) for outkey in out]):
                        out[key] += "%s " % str(args[i])
                        i += 1

                    out[key] = out[key].strip()
                    if len(out[key]) == 0:
                        out[key] = self.keywords[key]['value']

                else:
                    #for everything else, there's mastercard
                    #jk, grab as many arguments are we're asked to
                    #check to see if it's the right type and convert it to that type
                    if self.keywords[key]['n'] == 0:
                        out[key] = True
                    else:
                        out[key] = " ".join(args[i:i + self.keywords[key]['n']])
                        if self.keywords[key]['type'] is not None:
                            try:
                                self.keywords[key]['type'](out[key])
                            except:
                                raise ValueError("argument for keyword %s was expected to be %s; got %s" % \
                                    (key, self.keywords[key]['type'], out[key]))

                            if self.keywords[key]['type'] is bool:
                                #if it's a bool, check to see if it's true-ish or false-ish
                                #bool(str) will always return True unless str is empty
                                if out[key].lower() in ["1", "true", "t", "yes", "y"]:
                                    out[key] = True
                                elif out[key].lower() in ["0", "false", "f", "no", "n"]:
                                    out[key] = False
                                else:
                                    raise ValueError("argument for Boolean keyword %s must be true or false; got %s" % \
                                        (key, out[key]))

                            else:
                                out[key] = self.keywords[key]['type'](out[key])

                        i += self.keywords[key]['n']
            else:
                #don't recognize the argument, pass it back to the command in the 'other' list
                #let the command decide if we should die
                out['other'].append(arg)

                while (args[i].endswith('\\') and not args[i].endswith('\\\\')) and i < len(args):
                    i += 1
                    out['other'][-1] = out['other'][-1][:-1] + " " + args[i]

                i += 1

        return out
