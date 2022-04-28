from chimerax.core.commands import run


def apply_seqcrow_bse_lighting(session):
    view = session.main_view
    # view.set_background_color([1., 1., 1., 0])
    
    lighting_profile = view.lighting
    
    lighting_profile.key_light_intensity = 1.
    lighting_profile.multishadow = 0
    lighting_profile.fill_light_intensity = 0.5
    lighting_profile.ambient_light_intensity = 0.4
    lighting_profile.key_light_color = [1., 1., 1., 0]
    lighting_profile.fill_light_color = [1., 1., 1., 0]
    lighting_profile.ambient_light_color = [1., 1., 1., 0]
    lighting_profile.depth_cue_color = [1., 1., 1.]
    
    run(session, "graphics silhouettes true", log=False)
    run(session, "lighting depthCue true", log=False)
    run(session, "lighting shadows false", log=False)

def seqcrow_bse(session, models=None, atoms=None):
    """non-H atoms are displayed with B&S
    H atoms are displayed with S
    atoms colored by Jmol colors"""

    from AaronTools.const import RADII
    from chimerax.atomic import AtomicStructure, Atom
    from chimerax.atomic.colors import element_color

    apply_seqcrow_bse_lighting(session)

    if models is None:
        if atoms is None:
            models = session.models.list(type=AtomicStructure)
        else:
            models = list(set([atom.structure for atom in atoms]))
    elif isinstance(models, AtomicStructure):
        models = [models]
    
    for m in models:
        m.ball_scale = 0.4
        
        if atoms is None:
            atom_list = m.atoms
        else:
            atom_list = [atom for atom in atoms if (atom.structure is m or atom.residue is m)]
        
        for bond in m.bonds:
            if any(a in atom_list for a in bond.atoms):
                bond.halfbond = True
                bond.radius = 0.16
                bond.hide = False
        
        for atom in atom_list:
            ele = atom.element.name
            color = element_color(atom.element.number)

            atom.color = color
            atom.display = True

            if ele in RADII:
                #AaronTools has bonding radii, maybe I should use vdw?
                #check to see how necessary this is
                atom.radius = RADII[ele]

            if ele != 'H':
                atom.draw_mode = Atom.BALL_STYLE
            elif len(atom.neighbors) > 1:
                atom.radius = 0.625
                atom.draw_mode = Atom.BALL_STYLE
            else:
                atom.draw_mode = Atom.STICK_STYLE

def seqcrow_bse_cartoon(session, models=None, atoms=None):
    """non-H atoms are displayed with B&S
    H atoms are displayed with S
    atoms colored by Jmol colors"""

    from AaronTools.const import RADII
    from chimerax.atomic import AtomicStructure, Atom
    from chimerax.atomic.colors import element_color

    apply_seqcrow_bse_lighting(session)

    if models is None:
        if atoms is None:
            models = session.models.list(type=AtomicStructure)
        else:
            models = list(set([atom.structure for atom in atoms]))
    elif isinstance(models, AtomicStructure):
        models = [models]
    
    for m in models:
        if atoms is None:
            m.ball_scale = 0.4
        
        if atoms is None:
            atom_list = m.atoms
        else:
            atom_list = [atom for atom in atoms if (atom.structure is m or atom.residue is m)]
        
        for bond in m.bonds:
            if any(a in atom_list for a in bond.atoms):
                bond.halfbond = True
                bond.radius = 0.16
                bond.hide = False
        
        for atom in atom_list:
            if not atom.display:
                if (
                    atom.element.name == "H" and
                    len(atom.neighbors) > 0 and
                    not atom.neighbors[0].display
                ):
                    continue
                elif atom.element.name != "H":
                    continue
            
            ele = atom.element.name
            color = element_color(atom.element.number)

            atom.color = color
            atom.display = True

            if ele in RADII:
                #AaronTools has bonding radii, maybe I should use vdw?
                #check to see how necessary this is
                atom.radius = RADII[ele]

            if ele != 'H':
                atom.draw_mode = Atom.BALL_STYLE
            elif len(atom.neighbors) > 1:
                atom.radius = 0.625
                atom.draw_mode = Atom.BALL_STYLE
            else:
                atom.draw_mode = Atom.STICK_STYLE


def seqcrow_vdw(session, models=None, atoms=None):
    """atoms are displayed as B
    atoms colored by Jmol colors"""

    from AaronTools.const import VDW_RADII
    from chimerax.atomic import AtomicStructure, Atom
    from chimerax.atomic.colors import element_color
    
    apply_seqcrow_bse_lighting(session)

    if models is None:
        if atoms is None:
            models = session.models.list(type=AtomicStructure)
        else:
            models = list(set([atom.structure for atom in atoms]))
    elif isinstance(models, AtomicStructure):
        models = [models]
    
    for m in models:
        if atoms is None:
            m.ball_scale = 1.0

        if atoms is None:
            atom_list = m.atoms
        else:
            atom_list = [atom for atom in atoms if atom.structure is m]
        
        for bond in m.bonds:
            if any(a in atom_list for a in bond.atoms):
                bond.halfbond = True
                bond.radius = 0.16
                bond.hide = False
                
        for atom in atom_list:
            ele = atom.element.name
            color = element_color(atom.element.number)

            atom.color = color
            atom.display = True
            
            if ele in VDW_RADII:
                atom.radius = VDW_RADII[ele]
            
            atom.draw_mode = Atom.BALL_STYLE

def apply_seqcrow_s_lighting(session):
    view = session.main_view
    # view.set_background_color([1., 1., 1., 0])

    lighting_profile = view.lighting
    
    lighting_profile.key_light_intensity = 1.
    lighting_profile.multishadow = 64
    lighting_profile.multishadow_map_size = 1024
    lighting_profile.multishadow_depth_bias = 0.01
    lighting_profile.fill_light_intensity = 0.5
    lighting_profile.ambient_light_intensity = 0.4
    lighting_profile.key_light_color = [1., 1., 1., 0]
    lighting_profile.fill_light_color = [1., 1., 1., 0]
    lighting_profile.ambient_light_color = [1., 1., 1., 0]
    lighting_profile.depth_cue_color = [1., 1., 1.]
   
    run(session, "graphics silhouettes true", log=False)
    run(session, "lighting depthCue true", log=False)
    run(session, "lighting shadows true", log=False)

def seqcrow_s(session, models=None, atoms=None):
    """atoms are represented with sticks
    atoms colored by Jmol colors"""

    from AaronTools.const import RADII
    from chimerax.atomic import AtomicStructure, Atom
    from chimerax.atomic.colors import element_color
    from SEQCROW.selectors import get_fragment

    apply_seqcrow_s_lighting(session)

    if models is None:
        if atoms is None:
            models = session.models.list(type=AtomicStructure)
        else:
            models = list(set([atom.structure for atom in atoms]))
    elif isinstance(models, AtomicStructure):
        models = [models]

    for m in models:
        if atoms is None:
            m.ball_scale = 0.625

        if atoms is None:
            atom_list = m.atoms
        else:
            atom_list = [atom for atom in atoms if atom.structure is m]

        for bond in m.bonds:
            if any(a in atom_list for a in bond.atoms):
                bond.halfbond = True
                bond.radius = 0.25
                bond.hide = False

        tm_bonds = m.pseudobond_group(m.PBG_METAL_COORDINATION, create_type=None)
        ts_bonds = m.pseudobond_group("TS bonds", create_type=None)
        h_bonds = m.pseudobond_group("hydrogen bonds", create_type=None)

        for atom in atom_list:
            ele = atom.element.name
            color = element_color(atom.element.number)

            atom.color = color
            
            if not atom.neighbors:
                atom.draw_mode = Atom.BALL_STYLE
                if ele in RADII:
                    atom.radius = RADII[ele]
            
            else:
                atom.draw_mode = Atom.STICK_STYLE
            
            if atom.element.name == "H":
                display = len(atom.neighbors) != 1
                if tm_bonds:
                    if any(atom in bond.atoms for bond in tm_bonds.pseudobonds):
                        display = True
                
                if h_bonds:
                    if any(atom in bond.atoms for bond in h_bonds.pseudobonds):
                        display = True
                
                if ts_bonds:
                    if any(atom in bond.atoms for bond in ts_bonds.pseudobonds):
                        display = True

                if not display:
                    for bonded_atom in atom.neighbors:
                        if "C" != bonded_atom.element.name or (
                            (
                                bonded_atom.element.name == "C" and (
                                    # show H's on terminal carbons that aren't RCH3's
                                    sum(len(a.neighbors) == 1 for a in bonded_atom.neighbors) >= bonded_atom.num_bonds - 1
                                    and not (
                                        sum(int(a.element.name == "H") for a in bonded_atom.neighbors) == 3
                                        and len(bonded_atom.neighbors) == 4
                                    )
                                    # show H's in TS bonds or on atoms that are coordinated to a metal
                                    or (ts_bonds and any(bonded_atom in bond.atoms for bond in ts_bonds.pseudobonds))
                                    or (tm_bonds and any(bonded_atom in bond.atoms for bond in tm_bonds.pseudobonds))
                                )
                            )
                            # show H's that are on chiral carbons
                            # this is a really lazy check and doesn't get everything
                            or (
                                sum(a.element.name == "H" for a in bonded_atom.neighbors) == 1 and (
                                    len(set(sum(
                                        get_fragment(a, bonded_atom).elements.masses) for a in bonded_atom.neighbors
                                    )) == 4 # or any(a.element.name not in "CH" for a in bonded_atom.neighbors)
                                ) and bonded_atom.num_bonds == 4
                            )
                        ): 
                            display = True
                            break
                        
                        # show H's on trigonal carbons adjacent to terminal trigonal carbons
                        if "C" == bonded_atom.element.name and bonded_atom.num_bonds < 4:
                            for bonded_atom2 in bonded_atom.neighbors:
                                if bonded_atom2.element.name == "C" and (
                                    sum(len(a.neighbors) == 1 for a in bonded_atom2.neighbors) >= bonded_atom2.num_bonds - 1
                                    and not (
                                        sum(int(a.element.name == "H") for a in bonded_atom2.neighbors) == 3
                                        and len(bonded_atom2.neighbors) == 4
                                    )
                                ):
                                    display = True
                                    break
                
                atom.display = display


def seqcrow_s_cartoon(session, models=None, atoms=None):
    """atoms are represented with sticks
    atoms colored by Jmol colors"""

    from AaronTools.const import RADII
    from chimerax.atomic import AtomicStructure, Atom
    from chimerax.atomic.colors import element_color
    from SEQCROW.selectors import get_fragment

    apply_seqcrow_bse_lighting(session)

    if models is None:
        if atoms is None:
            models = session.models.list(type=AtomicStructure)
        else:
            models = list(set([atom.structure for atom in atoms]))
    elif isinstance(models, AtomicStructure):
        models = [models]

    for m in models:
        if atoms is None:
            m.ball_scale = 0.625

        if atoms is None:
            atom_list = m.atoms
        else:
            atom_list = [atom for atom in atoms if atom.structure is m]

        for bond in m.bonds:
            if any(a in atom_list for a in bond.atoms):
                bond.halfbond = True
                bond.radius = 0.25
                bond.hide = False

        tm_bonds = m.pseudobond_group(m.PBG_METAL_COORDINATION, create_type=None)
        ts_bonds = m.pseudobond_group("TS bonds", create_type=None)
        h_bonds = m.pseudobond_group("hydrogen bonds", create_type=None)

        for atom in atom_list:
            if not atom.display:
                continue
            ele = atom.element.name
            color = element_color(atom.element.number)

            atom.color = color
            
            if not atom.neighbors:
                atom.draw_mode = Atom.BALL_STYLE
                if ele in RADII:
                    atom.radius = RADII[ele]
            
            else:
                atom.draw_mode = Atom.STICK_STYLE
            
            if atom.element.name == "H":
                display = len(atom.neighbors) != 1
                if tm_bonds:
                    if any(atom in bond.atoms for bond in tm_bonds.pseudobonds):
                        display = True
                
                if h_bonds:
                    if any(atom in bond.atoms for bond in h_bonds.pseudobonds):
                        display = True
                
                if ts_bonds:
                    if any(atom in bond.atoms for bond in ts_bonds.pseudobonds):
                        display = True

                if not display:
                    for bonded_atom in atom.neighbors:
                        if "C" != bonded_atom.element.name or (
                            (
                                bonded_atom.element.name == "C" and (
                                    # show H's on terminal carbons that aren't RCH3's
                                    sum(len(a.neighbors) == 1 for a in bonded_atom.neighbors) >= bonded_atom.num_bonds - 1
                                    and not (
                                        sum(int(a.element.name == "H") for a in bonded_atom.neighbors) == 3
                                        and len(bonded_atom.neighbors) == 4
                                    )
                                    # show H's in TS bonds or on atoms that are coordinated to a metal
                                    or (ts_bonds and any(bonded_atom in bond.atoms for bond in ts_bonds.pseudobonds))
                                    or (tm_bonds and any(bonded_atom in bond.atoms for bond in tm_bonds.pseudobonds))
                                )
                            )
                            # show H's that are on chiral carbons
                            # this is a really lazy check and doesn't get everything
                            or (
                                sum(a.element.name == "H" for a in bonded_atom.neighbors) == 1 and (
                                    len(set(sum(
                                        get_fragment(a, bonded_atom).elements.masses) for a in bonded_atom.neighbors
                                    )) == 4 # or any(a.element.name not in "CH" for a in bonded_atom.neighbors)
                                ) and bonded_atom.num_bonds == 4
                            )
                        ): 
                            display = True
                            break
                        
                        # show H's on trigonal carbons adjacent to terminal trigonal carbons
                        if "C" == bonded_atom.element.name and bonded_atom.num_bonds < 4:
                            for bonded_atom2 in bonded_atom.neighbors:
                                if bonded_atom2.element.name == "C" and (
                                    sum(len(a.neighbors) == 1 for a in bonded_atom2.neighbors) >= bonded_atom2.num_bonds - 1
                                    and not (
                                        sum(int(a.element.name == "H") for a in bonded_atom2.neighbors) == 3
                                        and len(bonded_atom2.neighbors) == 4
                                    )
                                ):
                                    display = True
                                    break
                
                atom.display = display


def indexLabel(session, models=None):
    from chimerax.core.objects import Objects
    from chimerax.atomic import AtomicStructure, Atoms
    from chimerax.label.label3d import label
    from SEQCROW.utils import contrast_bw
    
    if models is None:
        models = session.models.list(type=AtomicStructure)
    elif isinstance(models, AtomicStructure):
        models = [models]
    
    for m in models:
        for i, atom in enumerate(m.atoms):
            l = str(i+1)
            ele_color = atom.color[:-1]
            if contrast_bw(ele_color) == "black":
                label_color = (0, 0, 0, 255)
            else:
                label_color = (255, 255, 255, 255)
            label(
                session,
                objects=Objects(atoms=Atoms([atom])),
                object_type='atoms',
                text=l,
                offset=(-0.11*len(l),-0.2,-0.2),
                height=0.4,
                on_top=True,
                color=label_color,
            )

