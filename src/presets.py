import numpy as np

def apply_seqcrow_bse_lighting(session):
    view = session.main_view
    # view.set_background_color([1., 1., 1., 0])
    view.silhouette.enabled = True
    
    lighting_profile = view.lighting
    
    lighting_profile.key_light_intensity = 1.
    lighting_profile.depth_cue = True
    lighting_profile.shadows = False
    lighting_profile.multishadow = 0
    lighting_profile.fill_light_intensity = 0.5
    lighting_profile.ambient_light_intensity = 0.4
    lighting_profile.key_light_color = [1., 1., 1., 0]
    lighting_profile.fill_light_color = [1., 1., 1., 0]
    lighting_profile.ambient_light_color = [1., 1., 1., 0]
    lighting_profile.depth_cue_color = [1., 1., 1.]
    
    view.update_lighting = True
    view.redraw_needed = True

def seqcrow_bse(session, models=None, atoms=None):
    """non-H atoms are displayed with B&S
    H atoms are displayed with S
    atoms colored by Jmol colors"""

    from AaronTools.const import RADII
    from chimerax.atomic import AtomicStructure, Atom, Bond
    from chimerax.atomic.colors import element_color

    if models is None or atoms is None:
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
    
    if models is None or atoms is None:
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
    view.silhouette.enabled = True

    lighting_profile = view.lighting
    
    lighting_profile.key_light_intensity = 1.
    lighting_profile.depth_cue = True
    lighting_profile.shadows = True
    lighting_profile.multishadow = 64
    lighting_profile.multishadow_map_size = 1024
    lighting_profile.multishadow_depth_bias = 0.01
    lighting_profile.fill_light_intensity = 0.5
    lighting_profile.ambient_light_intensity = 0.4
    lighting_profile.key_light_color = [1., 1., 1., 0]
    lighting_profile.fill_light_color = [1., 1., 1., 0]
    lighting_profile.ambient_light_color = [1., 1., 1., 0]
    lighting_profile.depth_cue_color = [1., 1., 1.]

    view.update_lighting = True
    view.redraw_needed = True
    
def seqcrow_s(session, models=None, atoms=None):
    """atoms are represented with sticks
    atoms colored by Jmol colors"""

    from AaronTools.const import RADII, VDW_RADII, TMETAL
    from chimerax.atomic import AtomicStructure, Atom, Bond
    from chimerax.atomic.colors import element_color

    if models is None or atoms is None:
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
                for bonded_atom in atom.neighbors:
                    if any(x == bonded_atom.element.name for x in ["N", "O", "F", "Cl", "Br"] + list(TMETAL.keys())):
                        display = True
                        break
                
                atom.display = display

def indexLabel(session, models=None):
    from chimerax.core.objects import Objects
    from chimerax.atomic import AtomicStructure, Atoms
    from chimerax.label.label3d import label
    
    if models is None:
        models = session.models.list(type=AtomicStructure)
    elif isinstance(models, AtomicStructure):
        models = [models]
    
    for m in models:
        for i, atom in enumerate(m.atoms):
            l = str(i+1)
            label(session, objects=Objects(atoms=Atoms([atom])), object_type='atoms', \
                text=l, offset=(-0.11*len(l),-0.2,-0.2), height=0.4, on_top=True)

