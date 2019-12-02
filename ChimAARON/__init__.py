import arnmngr
arn_input_manager = arnmngr.InputManager()

def AaronGeometry2ChimeraMolecule(mol, tagList=False):
    """convert AaronTools Geometry to Chimera Molecule"""
    from chimera import Coord, Molecule, Element, connectMolecule
    from re import search
    
    #create new molecule and residue
    m = Molecule()
    r = m.newResidue("UNK", " ", 1, " ")
    #chimera uses the comment line to name molecules
    if mol.name:
        m.name = mol.comment
    else:
        m.name = "molecule"
    
    #convert each atom. assign it a serial number
    atomElements = {}
    for i, atom in enumerate(mol.atoms):
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
    #delete all bonds - we'll be using the mol's bonds
#    for bond in m.bonds:
#        m.deleteBond(bond)
    
#    for i, atom1 in enumerate(mol.atoms):
#        for j, atom2 in enumerate(mol.atoms[:]):
#            if atom2 in atom1.connected:
#                if not any([bond.contains(m.atoms[i]) and bond.contains(m.atoms[j]) for bond in m.bonds]):
#                    m.newBond(m.atoms[i], m.atoms[j])
            
#    mol.chimera = m
    
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

def doSubstitute(cmdName, arg_str):
    """substitute a substituent for a different substituent"""
    from chimera import replyobj, openModels, selection
    from AaronTools.geometry import Geometry
    from AaronTools.substituent import Substituent
    from AaronTools.fileIO import FileWriter
    from Midas import _selectedAtoms
    from Midas.midas_text import getSpecs
    
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

def doCloseRing(cmdName, arg_str):
    from chimera import replyobj, openModels
    from AaronTools.geometry import Geometry
    from AaronTools.ringfragment import RingFragment
    from AaronTools.fileIO import FileWriter
    from Midas import _selectedAtoms
    from Midas.midas_text import getSpecs
    
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

def doFollow(cmdName, arg_str):
    """make an animation for the normal modes in the specified file"""
    from chimera import replyobj
    from AaronTools.fileIO import FileReader
    from AaronTools.geometry import Geometry
    from Movie.gui import MovieDialog

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
    
def doMapLigand(cmdName, arg_str):
    """substitute one ligand for another"""
    from chimera import replyobj, selection
    from AaronTools.catalyst import Catalyst
    from AaronTools.component import Component
    from Midas import _selectedAtoms
    from Midas.midas_text import getSpecs
    
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
    
def substitute(sub_name, atoms, form='from_library'):
    """substitute one substituent for another"""
    from AaronTools.substituent import Substituent
    
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

def doArnRecord(cmdName, arg_str):
    from chimera import openModels, replyobj
    from chimera.selection import OSLSelection, currentAtoms
    from AaronTools.catalyst import Catalyst
    from arnmngr import Record
    
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
        
def getAARONkw(cmdName, arg_str, perl=True):
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