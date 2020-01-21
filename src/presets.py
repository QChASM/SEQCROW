import numpy as np

def chimaaron_bse(session):
    """non-H atoms are displayed with B&S
    H atoms are displayed with S
    atoms colored by Jmol colors"""

    from AaronTools.const import RADII
    from chimerax.atomic import AtomicStructure, Atom, Bond
    from chimerax.atomic.colors import element_color
    
    view = session.main_view
    view.set_background_color([1., 1., 1., 0])
    view.silhouette.enabled = True
    
    lighting_profile = view.lighting
    
    lighting_profile.shadows = False
    lighting_profile.key_light_intensity = 1.
    lighting_profile.depth_cue = True
    lighting_profile.shadows = False
    lighting_profile.key_light_color = [1., 1., 1., 0]   
    lighting_profile.fill_light_color = [1., 1., 1., 0]
    lighting_profile.ambient_light_color = [1., 1., 1., 0]
    
    view.update_lighting = True
    view.redraw_needed = True

    geoms = session.models.list(type=AtomicStructure)
    
    for geom in geoms:
        for bond in geom.bonds:
            bond.halfbond = True
            bond.radius = 0.16
            bond.hide = False
            
        for atom in geom.atoms:
            ele = atom.element.name
            color = element_color(atom.element.number)
            if hasattr(atom, "ghost"):
                color = tuple(*color, atom.color[-1])
                
            atom.color = color
            
            if ele in RADII:
                #AaronTools has bonding radii, maybe I should use vdw?
                atom.radius = 1.6*RADII[ele]
            
            if ele != 'H':
                atom.draw_mode = Atom.BALL_STYLE
            else:
                atom.draw_mode = Atom.STICK_STYLE

def chimaaron_s(session):
    """atoms are represented with sticks
    atoms colored by Jmol colors"""

    from AaronTools.const import RADII
    from chimerax.atomic import AtomicStructure, Atom, Bond
    from chimerax.atomic.colors import element_color
    
    view = session.main_view
    view.set_background_color([1., 1., 1., 0])
    view.silhouette.enabled = True

    lighting_profile = view.lighting
    
    lighting_profile.shadows = False
    lighting_profile.key_light_intensity = 1.
    lighting_profile.depth_cue = True
    lighting_profile.shadows = False

    view.update_lighting = True
    view.redraw_needed = True
    
    geoms = session.models.list(type=AtomicStructure)
    
    for geom in geoms:
        for bond in geom.bonds:
            bond.halfbond = True
            bond.radius = 0.25
            bond.hide = False
            
        for atom in geom.atoms:
            ele = atom.element.name
            color = element_color(atom.element.number)
            if hasattr(atom, "ghost"):
                color = tuple(*color, atom.color[-1])
             
            atom.color = color
            
            if ele in RADII:
                #AaronTools has bonding radii, maybe I should use vdw?
                atom.radius = 1.6*RADII[ele]
            
            atom.draw_mode = Atom.STICK_STYLE

def indexLabel(session):
    from chimerax.core.objects import Objects
    from chimerax.atomic import AtomicStructure, Atoms
    from chimerax.label.label3d import label
    
    for m in session.models.list(type=AtomicStructure):
        for i, atom in enumerate(m.atoms):
            l = str(i+1)
            label(session, objects=Objects(atoms=Atoms([atom])), object_type='atoms', \
                text=l, offset=(-0.2,-0.2,-0.2), height=0.4, on_top=True)

def blue_filter1(session):
    import numpy as np
    filter = np.array([252./255, 236./255, 217./255, 1.])
    
    apply_filter(filter, session)

def blue_filter2(session):
    filter = np.array([252./255., 217./255., 179./255., 1.])
    
    apply_filter(filter, session)

def protanopia(session):
    filter = np.array([[0.567, 0.433, 0.000, 0.0], \
                        [0.558, 0.442, 0.000, 0.0], \
                        [0.000, 0.242, 0.758, 0.0], \
                        [0.000, 0.000, 0.000, 1.0]])
                        
    apply_filter(filter, session, to_models=True)
    
def protanomaly(session):
    filter = np.array([[0.817, 0.183, 0.000, 0.0], \
                        [0.333, 0.667, 0.000, 0.0], \
                        [0.000, 0.125, 0.875, 0.0],
                        [0.000, 0.000, 0.000, 1.0]])

    apply_filter(filter, session, to_models=True)
    
def deuteranopia(session):
    filter = np.array([[0.625, 0.375, 0.000, 0.0], \
                        [0.700, 0.300, 0.000, 0.0], \
                        [0.000, 0.300, 0.700, 0.0], \
                        [0.000, 0.000, 0.000, 1.0]])

    apply_filter(filter, session, to_models=True)
    
def deuteranomaly(session):
    filter = np.array([[0.800, 0.200, 0.000, 0.0], \
                        [0.258, 0.742, 0.000, 0.0], \
                        [0.000, 0.142 ,0.858, 0.0], \
                        [0.000, 0.000, 0.000, 1.0]])

    apply_filter(filter, session, to_models=True)
    
def tritanopia(session):
    filter = np.array([[0.950, 0.050, 0.000, 0.0], \
                        [0.000, 0.433, 0.567, 0.0], \
                        [0.000, 0.475 ,0.525, 0.0], \
                        [0.000, 0.000, 0.000, 1.0]])

    apply_filter(filter, session, to_models=True)
    
def tritanomaly(session):
    filter = np.array([[0.967, 0.033, 0.000, 0.0], \
                        [0.000, 0.733, 0.267, 0.0], \
                        [0.000, 0.183, 0.817, 0.0], \
                        [0.000, 0.000, 0.000, 1.0]])

    apply_filter(filter, session, to_models=True)
    
def achromatopsia(session):
    filter = np.array([[0.299, 0.587, 0.114, 0.0], \
                        [0.299, 0.587, 0.114, 0.0], \
                        [0.299, 0.587 ,0.114, 0.0], \
                        [0.000, 0.000, 0.000, 1.0]])

    apply_filter(filter, session, to_models=True)
    
def achromatomaly(session):
    filter = np.array([[0.618, 0.320, 0.062, 0.0], \
                        [0.163, 0.775, 0.062, 0.0], \
                        [0.163, 0.320 ,0.516, 0.0], \
                        [0.000, 0.000, 0.000, 1.0]])

    apply_filter(filter, session, to_models=True)

def get_new_color(color, filter, kind=int):   
    old_color = np.array(color)
    if old_color.shape == (3,):
        old_color = np.append(old_color, [1.])
        
    if filter.shape == (4,): 
        new_color = tuple([kind(x) for x in np.multiply(filter, old_color)])
    elif filter.shape == (4,4,):
        new_color = tuple([kind(x) for x in np.dot(filter, old_color)])
    else:
        raise RuntimeError("color filter should be of shape (4,) or (4,4)")
    
    return new_color
                
def apply_filter(filter, session, to_models=False):
    view = session.main_view
    new_color = get_new_color(view.get_background_color(), filter, kind=float)
    view.set_background_color(new_color)
    
    if not to_models:
        lighting_profile = view.lighting
        
        new_color = get_new_color(lighting_profile.key_light_color, filter, kind=float)
        lighting_profile.key_light_color = new_color   
        
        new_color = get_new_color(lighting_profile.fill_light_color, filter, kind=float)
        lighting_profile.fill_light_color = new_color
        
        new_color = get_new_color(lighting_profile.ambient_light_color, filter, kind=float)
        lighting_profile.ambient_light_color = new_color
        
        view.update_lighting = True
        view.redraw_needed = True
    else:
        for m in session.models.list():
            if hasattr(m, "color"):
                if m.color is not None:
                    new_color = get_new_color(m.color, filter)
                    m.color = new_color
                    
            if hasattr(m, 'atoms'):
                for atom in m.atoms:
                    if hasattr(atom, "color"):
                        if atom.color is not None:
                            new_color = get_new_color(atom.color, filter)
                            atom.color = new_color