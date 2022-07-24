import numpy as np

from chimerax.core.commands import (
    run,
    BoolArg,
    CmdDesc,
    EnumOf,
    FloatArg,
    IntArg,
    ModelsArg,
    Or,
    TupleOf,
)
from chimerax.atomic import AtomsArg
from chimerax.core.models import Surface
from chimerax.geometry.sphere import sphere_triangulation
from chimerax.graphics.drawing import Drawing

from AaronTools.const import VDW_RADII, BONDI_RADII
from AaronTools.component import Component
from AaronTools.utils.utils import rotation_matrix, fibonacci_sphere, perp_vector

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec

from scipy.spatial import distance_matrix, ConvexHull


solid_angle_description = CmdDesc(
    required=[("selection", ModelsArg)], \
    keyword=[
        (
            "radii",
            EnumOf(["UMN", "Bondi"], case_sensitive=False),
        ),
        ("radius", FloatArg),
        ("points", IntArg),                                        
        ("center", Or(AtomsArg, TupleOf(FloatArg, 3))), 
        ("useCentroid", BoolArg), 
        ("display", BoolArg), 
        ("pointSpacing", FloatArg), 
        ("intersectionScale", FloatArg), 
    ],
    synopsis="calculate ligand solid angles",
)

def solid_angle(
        session, 
        selection, 
        radii="UMN", 
        radius=0, 
        points=5810, 
        center=None,
        useCentroid=False,
        display=False,
        pointSpacing=0.2,
        intersectionScale=200,
        color="#44fc39",
):
    out = []
    
    models = dict()
    for atom in selection:
        try:
            models[atom.structure].append(atom)
        except KeyError:
            models[atom.structure] = [atom]
    
    s = "<pre>model\tcenter\tangle (steradians)\n"
    
    for model in models:        
        rescol = ResidueCollection(model)
        try:
            targets = rescol.find([AtomSpec(atom.atomspec) for atom in models[model]])
        except LookupError:
            session.logger.warning("no targets on %s" % model.atomspec)
            continue
        
        if center is not None:
            if isinstance(center, tuple):
                mdl_center = np.array(center)
            else:
                mdl_center = [AtomSpec(atom.atomspec) for atom in model.atoms if atom in center]
                if not mdl_center:
                    session.logger.warning("no atoms were specified on the same structure as a center: %s" % center.atomspec)

        else:
            session.logger.warning("no atoms were specified on the same structure as a center: %s" % center.atomspec)
            mdl_center = []

        if len(mdl_center) == 0:
            rescol.detect_components()
            mdl_center = rescol.center
        elif not isinstance(center, np.ndarray):
            mdl_center = rescol.find([AtomSpec(c.atomspec) for c in center])

        if not useCentroid and not isinstance(center, np.ndarray):
            for c in mdl_center:
                ligand = Component(
                    targets,
                    key_atoms=[targets[0]],
                    detect_backbone=False,
                    refresh_ranks=False,
                )
                
                angle = ligand.solid_angle(
                    center=c,
                    radii=radii,
                    grid=int(points),
                )
                
                if display:
                    vis = solid_angle_vis(
                        session,
                        rescol,
                        targets,
                        c,
                        radius,
                        radii,
                        pointSpacing,
                        intersectionScale,
                    )
                    model.add([vis])
                    # I don't like how this looks
                    # cmd = " ".join([
                    #     "color",
                    #     "radial",
                    #     vis.child_models()[0].atomspec,
                    #     "palette",
                    #     "#00000000:#00000099:#000000ff",
                    #     "center",
                    #     ",".join([str(x) for x in c.coords]),
                    #     "coordinateSystem",
                    #     model.atomspec,
                    # ])
                    # run(session, cmd)
                
                out.append((model, c, angle))
                s += "%s\t%s\t%.3f\n" % (
                    model.atomspec,
                    c.atomspec,
                    angle,
                )
               
        else:
            ligand = Component(
                targets,
                key_atoms=[targets[0]],
                detect_backbone=False,
                refresh_ranks=False,
            )
            
            angle = ligand.solid_angle(
                center=mdl_center,
                radii=radii,
                grid=int(points),
            )
            
            if display:
                vis = solid_angle_vis(
                    session,
                    rescol,
                    targets,
                    mdl_center,
                    radius,
                    radii,
                    pointSpacing,
                    intersectionScale,
                )
                model.add([vis])
                # center_coords = mdl_center
                # if not isinstance(mdl_center, np.ndarray):
                #     center_coords = rescol.coordinates(mdl_center)
                # cmd = " ".join([
                #     "color",
                #     "radial",
                #     vis.child_models()[0].atomspec,
                #     "palette",
                #     "#00000000:#00000099:#000000ff",
                #     "center",
                #     ",".join([str(x) for x in center_coords]),
                #     "coordinateSystem",
                #     model.atomspec,
                # ])
                # run(session, cmd)

            out.append((model, mdl_center, angle))
            s += "%s\t%s\t%.3f\n" % (
                model.atomspec,
                str(c) if isinstance(c, np.ndarray) else c.atomspec,
                angle,
            )
        
    s += "</pre>"
    session.logger.info(s, is_html=True)
    return out


def solid_angle_vis(
    session,
    geom,
    targets,
    center,
    radius,
    radii,
    point_spacing,
    intersection_scale,
):
    model = Surface("Solid angle", session)
    side = Surface("shadows", session)
    atom_radii = Surface("atoms", session)
    
    
    if isinstance(center, np.ndarray):
        center_coords = center
    else:
        center_coords = geom.coordinates(center)
    
    if center_coords.ndim > 1:
        center_coords = center_coords.flatten()

    if isinstance(radii, dict):
        radii_dict = radii
    elif radii.lower() == "umn":
        radii_dict = VDW_RADII
    elif radii.lower() == "bondi":
        radii_dict = BONDI_RADII
    else:
        raise RuntimeError(
            "received %s for radii, must be umn or bondi" % radii
        )
    
    coords = geom.coordinates(targets)

    radius_list = np.array([radii_dict[a.element] for a in targets])
    shifted_coords = coords - center_coords
    dx2 = np.sum(shifted_coords * shifted_coords, axis=1)
    dist = np.sqrt(dx2)


    coord_norms = shifted_coords / np.linalg.norm(shifted_coords, axis=1)[:, np.newaxis]
    X = np.divide(np.sqrt(dx2 - radius_list ** 2), dx2)
    if np.any(np.isnan(X)):
        atoms = [atom for i, atom in enumerate(targets) if np.isnan(X[i])]
        session.logger.warning("one or more atoms overlaps with the center, so everything is in a shadow: %s" % (
            ", ".join([atom.atomspec for atom in atoms])
        ))
        return model
    adjusted_coords = X[:, np.newaxis] * shifted_coords
    H = radius_list / dist
    
    if radius == 0:
        radius = max(dist + radius_list) + 0.1
    else:
        H[dist - radius_list > radius] = 0
        
    n_grid = int(4 * np.pi * radius ** 2 / point_spacing)
    
    sphere = fibonacci_sphere(num=n_grid)

    atom_added_points = []
    side_points = []
    side_norms = []
    side_tris = []
    base_v, base_t = sphere_triangulation(500)
    for i, atom in enumerate(targets):
        atom_v = radius_list[i] * base_v + coords[i]
        drawing = Drawing(atom.atomspec)
        drawing.set_geometry(atom_v, base_v, base_t)
        drawing.set_color((*atom.chix_atom.color[:-1], 255))
        atom_radii.add_drawing(drawing)
        
        if H[i] == 0:
            continue
        n_added = int(np.ceil(radius * intersection_scale * H[i] / point_spacing))

        dv = coord_norms[i] - [0, 0, 1]
        c2 = np.dot(dv, dv)
        theta = np.arccos(-c2 / 2. + 1)
        rv = np.cross(coord_norms[i], [0, 0, 1])
        rv /= np.linalg.norm(rv)
        R = rotation_matrix(theta, rv)
        angles = np.linspace(0, 2 * np.pi, num=n_added)
        circle = np.stack((np.cos(angles), np.sin(angles), np.zeros(n_added)), axis=-1)
        added_coords = H[i] * np.dot(circle, R) + adjusted_coords[i]
        added_top_sides = added_coords
        added_bottom_sides = dx2[i]  * X[i] * (H[i] * np.dot(circle, R) + adjusted_coords[i]) / radius

        d_ep = distance_matrix(added_coords, adjusted_coords)
        diff_mat = d_ep - H[np.newaxis, :]
        diff_mat[:, i] = 1
        mask = np.invert(np.any(diff_mat <= 0, axis=1))
        if not np.any(mask):
            continue
        
        added_top_sides[np.invert(mask)] = 0.99 * added_top_sides[np.invert(mask)]
        atom_added_points.extend(added_coords[mask])

        new_tris_1 = np.stack(
            (
                np.arange(0, n_added, dtype=int),
                np.arange(n_added, 2 * n_added, dtype=int),
                np.arange(1, n_added + 1, dtype=int),
            ),
            axis=-1
        )
        new_tris_1[-1] -= [0, n_added, n_added]
        new_tris_2 = np.stack(
            (
                np.arange(1, n_added + 1, dtype=int),
                np.arange(n_added, 2 * n_added, dtype=int),
                np.arange(n_added + 1, 2 * n_added + 1, dtype=int),
            ),
            axis=-1
        )
        new_tris_2[-1] -= [n_added, 0, n_added]

        side_tris.extend(new_tris_1 + len(side_points))
        side_tris.extend(new_tris_2 + len(side_points))

        side_points.extend(added_top_sides)
        side_norms.extend(added_top_sides - adjusted_coords[i])
        side_norms.extend(added_top_sides - adjusted_coords[i])
        side_points.extend(added_bottom_sides)

    dist = distance_matrix(sphere, adjusted_coords)
    mask = np.any(dist - H <= 0, axis=1)
    keep_pts = np.concatenate((mask, np.ones(len(atom_added_points), dtype=bool)))
    
    if atom_added_points:
        sphere = np.concatenate((sphere, atom_added_points))
    hull = ConvexHull((sphere - center_coords))
    tri = hull.simplices
    
    shift_ndx = dict()
    keep_verts = []
    for j in range(0, len(sphere)):
        if j > n_grid:
            shift_ndx[j] = len(shift_ndx)
            continue
        if keep_pts[j]:
            keep_verts.append(j)
            shift_ndx[j] = len(shift_ndx)
    keep_verts.extend(np.arange(n_grid, n_grid + len(atom_added_points), dtype=int))
    
    mask = np.invert(np.all(tri > n_grid, axis=1))
    mask[mask] = np.min(np.isin(tri[mask], keep_verts), axis=1)
    keep_tri = tri[mask]
    keep_tri = np.vectorize(shift_ndx.get)(keep_tri)
    sphere = radius * sphere[keep_pts]
    sphere += center_coords
    norms = sphere - center_coords
    norms /= np.linalg.norm(norms, axis=1)[:, np.newaxis]
    
    v1 = sphere[keep_tri[:, 1]] - sphere[keep_tri[:, 0]]
    v2 = sphere[keep_tri[:, 2]] - sphere[keep_tri[:, 0]]
    c = np.cross(v1, v2)
    mask = np.sum(c * norms[keep_tri[:, 0]], axis=1) < 0
    keep_tri[mask] = keep_tri[mask, ::-1]

    model.set_geometry(sphere, norms, keep_tri)
    model.set_color((0, 0, 0, 255))
    
    side_points = radius * np.array(side_points) + center_coords
    side_norms = np.array(side_norms)
    side_norms /= np.linalg.norm(side_norms, axis=1)[:, np.newaxis]
    side.set_geometry(side_points, side_norms, np.array(side_tris))
    side.set_color((0, 0, 0, 50))
    model.add([side, atom_radii])
    
    return model