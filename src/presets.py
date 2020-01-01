def preset1(session):
    """non-H atoms are displayed with B&S
    H atoms are displayed with S
    atoms colored by Jmol colors"""
    #TODO: set depth fog, unset silhouettes, whatever else is in my chimera preset
    from AaronTools.const import RADII
    from chimerax.atomic import AtomicStructure, Atom, Bond
    from chimerax.atomic.colors import element_color
    
    geoms = session.models.list(type=AtomicStructure)
    
    for geom in geoms:
        for bond in geom.bonds:
            bond.halfbond = True
            bond.radius = 0.2
            bond.hide = False
            
        for atom in geom.atoms:
            ele = atom.element.name
            color = element_color(atom.element.number)
            atom.color = color
            
            if ele in RADII:
                #AaronTools has bonding radii, maybe I should use vdw?
                atom.radius = 1.7*RADII[ele]
            
            if ele != 'H':
                atom.draw_mode = Atom.BALL_STYLE
            else:
                atom.draw_mode = Atom.STICK_STYLE
            