import numpy as np

from chimerax.core.commands import BoolArg, StringArg, CmdDesc, EnumOf, FloatArg, IntArg, ModelsArg, Or, TupleOf, run
from chimerax.atomic import AtomsArg, AtomicStructure
from chimerax.core.models import Surface

from AaronTools.const import VDW_RADII, BONDI_RADII
from AaronTools.utils.utils import rotation_matrix, fibonacci_sphere

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec

from scipy.spatial import distance_matrix, ConvexHull


vbur_description = CmdDesc(
    required=[("selection", ModelsArg)], \
    keyword=[
        (
            "radii",
            EnumOf(["UMN", "Bondi"], case_sensitive=False),
        ),
        ("radius", FloatArg), 
        ("scale", FloatArg), 
        (
            "method", 
            EnumOf(["leb", "mc"], ["Lebedev", "Monte-Carlo"], case_sensitive=False),
        ),
        ("radialPoints", EnumOf(["20", "32", "64", "75", "99", "127"])),                                        
        ("angularPoints", EnumOf(["110", "194", "302", "590", "974", "1454", "2030", "2702", "5810"])),                                        
        ("minimumIterations", IntArg), 
        ("scale", FloatArg), 
        ("onlyAtoms", AtomsArg), 
        ("center", Or(AtomsArg, TupleOf(FloatArg, 3))), 
        ("useCentroid", BoolArg), 
        ("displaySphere", EnumOf(["free", "buried"])), 
        ("pointSpacing", FloatArg), 
        ("intersectionScale", FloatArg), 
        ("palette", StringArg), 
    ],
    synopsis="calculate volume buried by ligands around a center",
    url="https://github.com/QChASM/SEQCROW/wiki/Commands#percentVolumeBuried",
)

def percent_vbur(
        session, 
        selection, 
        radii="UMN", 
        radius=3.5, 
        scale=1.17, 
        method="Lebedev", 
        radialPoints=20, 
        angularPoints=1454, 
        minimumIterations=25,
        onlyAtoms=None,
        center=None,
        useCentroid=True,
        displaySphere=None,
        pointSpacing=0.1,
        intersectionScale=6,
        palette="rainbow",
        return_values=False,
        steric_map=False,
        use_scene=False,
        num_pts=100,
        shape="circle",
):
    
    out = []
    
    models = {
        model:[atom for atom in model.atoms if onlyAtoms is not None and atom in onlyAtoms]
        for model in selection if isinstance(model, AtomicStructure)
    }
    
    s = "<pre>model\tcenter\t%Vbur\n"
    
    for model in models:
        if len(models[model]) == 0:
            targets = None
        else:
            targets = [AtomSpec(atom.atomspec) for atom in models[model]]
        
        if center is not None:
            if isinstance(center, tuple):
                mdl_center = np.array(center)
            else:
                mdl_center = [AtomSpec(atom.atomspec) for atom in model.atoms if atom in center]

        else:
            mdl_center = []
        
        rescol = ResidueCollection(model)
        
        if use_scene:
            oop_vector = session.view.camera.get_position().axes()[2]
            ip_vector = session.view.camera.get_position().axes()[1]
        
        else:
            oop_vector = None
            ip_vector = None
        
        if len(mdl_center) == 0:
            rescol.detect_components()
            mdl_center = rescol.center
        elif not isinstance(center, np.ndarray):
            mdl_center = rescol.find([AtomSpec(c.atomspec) for c in center])
        
        if not useCentroid and not isinstance(center, np.ndarray):
            for c in mdl_center:
                if steric_map:
                    if targets is not None:
                        key_atoms = []
                        targets = rescol.find(targets)
                        for atom in targets:
                            if c in atom.connected or atom in c.connected:
                                key_atoms.append(atom)
                    else:
                        key_atoms = None

                    x, y, z, min_alt, max_alt, basis, targets = rescol.steric_map(
                        center=c,
                        key_atoms=key_atoms,
                        radii=radii,
                        oop_vector=oop_vector,
                        ip_vector=ip_vector,
                        radius=radius,
                        return_basis=True,
                        num_pts=num_pts,
                        shape=shape,
                    )
                    
                    vbur = rescol.percent_buried_volume(
                        targets=targets,
                        basis=basis,
                        center=c,
                        radius=radius,
                        radii=radii,
                        scale=scale,
                        method=method,
                        rpoints=int(radialPoints),
                        apoints=int(angularPoints),
                        min_iter=minimumIterations,
                    )
                    
                    out.append((model.name, c.atomspec, vbur, (x, y, z, min_alt, max_alt)))
                
                else:
                    vbur = rescol.percent_buried_volume(
                        targets=targets,
                        center=c,
                        radius=radius,
                        radii=radii,
                        scale=scale,
                        method=method,
                        rpoints=int(radialPoints),
                        apoints=int(angularPoints),
                        min_iter=minimumIterations,
                    )
                        
                    s += "%s\t%s\t%4.1f%%\n" % (model.name, c.atomspec, vbur)
                
                    out.append((model.name, c.atomspec, vbur))
        
                if displaySphere is not None:
                    mdl = vbur_vis(
                            session,
                            rescol,
                            targets,
                            radii,
                            scale,
                            radius,
                            c,
                            pointSpacing,
                            intersectionScale,
                            displaySphere,
                    )
                    model.add([mdl])
                    atomspec = mdl.atomspec
                    center_coords = rescol.COM(c)
                    #XXX: the center will be wrong if the models are tiled
                    args = [
                        "color", "radial", atomspec,
                        "center", ",".join(["%.4f" % x for x in center_coords]),
                        "palette", palette,
                        ";",
                        "transparency", atomspec, "30", 
                    ]
                    
                    run(session, " ".join(args))
        else:
            if steric_map:
                if targets is not None:
                    key_atoms = []
                    targets = rescol.find(targets)
                    for atom in targets:
                        if any(c in atom.connected for c in mdl_center):
                            key_atoms.append(atom)
                else:
                    key_atoms = None
                        
                x, y, z, min_alt, max_alt, basis, targets = rescol.steric_map(
                    center=mdl_center,
                    key_atoms=key_atoms,
                    radius=radius,
                    radii=radii,
                    oop_vector=oop_vector,
                    ip_vector=ip_vector,
                    return_basis=True,
                    num_pts=num_pts,
                    shape=shape,
                )
                
                vbur = rescol.percent_buried_volume(
                    targets=targets,
                    basis=basis,
                    center=mdl_center,
                    radius=radius,
                    radii=radii,
                    scale=scale,
                    method=method,
                    rpoints=int(radialPoints),
                    apoints=int(angularPoints),
                    min_iter=minimumIterations,
                )
                
                if not isinstance(mdl_center, np.ndarray):
                    out.append((model.name, ",".join([c.atomspec for c in mdl_center]), vbur, (x, y, z, min_alt, max_alt)))
                else:
                    out.append((model.name, ",".join(["%.3f" % c for c in mdl_center]), vbur, (x, y, z, min_alt, max_alt)))

            else:
                vbur = rescol.percent_buried_volume(
                    targets=targets,
                    center=mdl_center,
                    radius=radius,
                    radii=radii,
                    scale=scale,
                    method=method,
                    rpoints=int(radialPoints),
                    apoints=int(angularPoints),
                    min_iter=minimumIterations,
                )
                
                if not isinstance(mdl_center, np.ndarray):
                    s += "%s\t%s\t%4.1f%%\n" % (model.name, ", ".join([c.atomspec for c in mdl_center]), vbur)
                    out.append((model.name, ", ".join([c.atomspec for c in mdl_center]), vbur))
                else:
                    s += "%s\t%s\t%4.1f%%\n" % (model.name, ",".join(["%.3f" % c for c in mdl_center]), vbur)
                    out.append((model.name, ",".join(["%.3f" % c for c in mdl_center]), vbur))

            if displaySphere is not None:
                mdl = vbur_vis(
                        session,
                        rescol,
                        targets,
                        radii,
                        scale,
                        radius,
                        mdl_center,
                        pointSpacing,
                        intersectionScale,
                        displaySphere,
                )
                model.add([mdl])
                atomspec = mdl.atomspec
                if not isinstance(mdl_center, np.ndarray):
                    center_coords = rescol.COM(mdl_center)
                else:
                    center_coords = mdl_center
                #XXX: the center will be wrong if the models are tiled
                args = [
                    "color", "radial", atomspec,
                    "center", ",".join(["%.4f" % x for x in center_coords]),
                    "palette", palette,
                    ";",
                    "transparency", atomspec, "30", 
                ]
                
                run(session, " ".join(args))
    
    s = s.strip()
    s += "</pre>"
    
    if not return_values:
        session.logger.info(s, is_html=True)
    else:
        return out


def vbur_vis(
        session,
        geom,
        targets,
        radii,
        scale,
        radius, 
        center, 
        point_spacing, 
        intersection_scale,
        volume_type,
):
    # from cProfile import Profile
    # 
    # profile = Profile()
    # profile.enable()

    # number of points is based on surface area
    n_grid = int(4 * np.pi * radius**2 / point_spacing)
    if volume_type == "buried":
        model = Surface("%%Vbur for %s" % geom.name, session)
    else:
        model = Surface("%%Vfree for %s" % geom.name, session)
    # verts, norms, and triangles for the drawing
    vertices = []
    normals = []
    triangles = []
    
    if isinstance(center, np.ndarray):
        center_coords = center
    else:
        center_coords = geom.COM(center)

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
    
    if not hasattr(center, "__iter__"):
        center = [center]
    
    if targets is None:
        if len(center) == 1:
            atoms = [atom for atom in geom.atoms if atom not in center]
        else:
            atoms = geom.atoms
    else:
        atoms = geom.find(targets)
    
    atoms_within_radius = []
    for atom in atoms:
        # determine which atom's radii extend within the sphere
        # reduces the number of distances we need to calculate
        d = np.linalg.norm(center_coords - atom.coords)
        inner_edge = d - scale*radii_dict[atom.element]
        if inner_edge < radius:
            atoms_within_radius.append(atom)
    
    # sort atoms based on their distance to the center
    # this makes is so we usually break out of looping over the atoms faster
    atoms_within_radius.sort(key=lambda a, c=center_coords: np.linalg.norm(a.coords - c))
    
    radius_list = []
    for atom in atoms_within_radius:
        radius_list.append(scale * radii_dict[atom.element])
        
    coords = geom.coordinates(atoms_within_radius)
    
    atom_dist = distance_matrix(coords, coords)
    
    sphere = fibonacci_sphere(num=n_grid, radius=radius)
    
    # add points right where spheres intersect
    # this makes the intersections look less pokey
    d_ac = distance_matrix(coords, [center_coords])
    center_added_points = []
    atom_added_points = [[] for atom in atoms_within_radius]
    for i in range(0, len(coords)):
        r1 = radius_list[i]    
        v_n = coords[i] - center_coords
        v_n /= np.linalg.norm(v_n)
        d = d_ac[i,0]
        # intersection with big sphere
        if d + r1 > radius:
            theta = np.arccos((r1**2 - radius**2 - d**2) / (-2 * d * radius))
            h = radius * np.sin(theta)
            b = radius * np.cos(theta)
            p = b * v_n
            
            circ = 2 * np.pi * h
            n_added = int(np.ceil(intersection_scale * circ / point_spacing))
            r_t = np.zeros(3)
            for j in range(0, 3):
                if v_n[j] != 0:
                    if j == 0:
                        r_t[1] = v_n[j]
                        r_t[0] = v_n[1]
                    else:
                        r_t[0] = v_n[j]
                        r_t[1] = v_n[0]
                    break
            
            r0 = np.cross(r_t, v_n)
            r0 *= h / np.linalg.norm(r0)
            
            rot_angle = 2*np.pi / n_added
            R = rotation_matrix(rot_angle, v_n)
            prev_r = r0
            prev_r_list = []
            for x in np.linspace(0, 2*np.pi, num=n_added):
                prev_r = np.dot(R, prev_r)
                prev_r_list.append(prev_r)
            prev_r_list = np.array(prev_r_list)
            d_ep = distance_matrix(prev_r_list + p + center_coords, coords)
            # if the point is obscured by another atom, don't bother adding it
            # this saves time on triangulation
            diff_mat = d_ep - radius_list
            diff_mat[:,i] = 1
            mask = np.invert(np.any(diff_mat < 0, axis=1))
            center_added_points.extend(prev_r_list[mask] + p)
            atom_added_points[i].extend(prev_r_list[mask] + p + center_coords)

        for j in range(0, i):
            d = atom_dist[i,j]
            r2 = radius_list[j]
            if d < r1 + r2 and d > abs(r1 - r2):
                v_n = coords[j] - coords[i]
                v_n /= np.linalg.norm(v_n)
                theta = np.arccos((r2**2 - r1**2 - d**2) / (-2 * r1 * d))
                h = r1 * np.sin(theta)
                b = r1 * np.cos(theta)
                p = b * v_n
                
                circ = 2 * np.pi * h
                n_added = int(np.ceil(intersection_scale * circ / point_spacing))
                r_t = np.zeros(3)
                for k in range(0, 3):
                    if v_n[k] != 0:
                        if k == 0:
                            r_t[1] = v_n[k]
                            r_t[0] = v_n[1]
                        else:
                            r_t[0] = v_n[k]
                            r_t[1] = v_n[0]
                        break
                
                r0 = np.cross(r_t, v_n)
                r0 *= h / np.linalg.norm(r0)
    
                rot_angle = 2*np.pi / n_added
                R = rotation_matrix(rot_angle, v_n)
                prev_r = r0
                prev_r_list = []
                for x in np.linspace(0, 2*np.pi, num=n_added):
                    prev_r = np.dot(R, prev_r)
                    prev_r_list.append(prev_r)
                prev_r_list = np.array(prev_r_list)
                norm_mask = np.linalg.norm(center_coords - (prev_r_list + p + coords[i]), axis=1) < radius
                prev_r_list = prev_r_list[norm_mask]
                
                if not len(prev_r_list):
                    continue
                d_ep = distance_matrix(prev_r_list + p + coords[i], coords)
                diff_mat = d_ep - radius_list
                diff_mat[:,i] = 1
                diff_mat[:,j] = 1
                mask = np.invert(np.any(diff_mat < 0, axis=1))
                if any(mask):
                    atom_added_points[i].extend(prev_r_list[mask] + p + coords[i])
                    atom_added_points[j].extend(prev_r_list[mask] + p + coords[i])

    tol = 0.3 * point_spacing
    for i in range(0, len(coords)):
        # get a grid of points around each atom
        # remove any points that are close to an intersection
        # this makes it less likely for the triangulation to choose
        # one of these points instead of one that we already added
        # then, if we have to remove a triangle involving one of these points later,
        # it won't leave a gap
        n_atom_grid = int(radius_list[i]**2 * n_grid / radius**2)
        atom_sphere = fibonacci_sphere(radius=radius_list[i], num=n_atom_grid)
        mask = np.ones(len(atom_sphere), dtype=bool)
        n_atom_grid = len(atom_sphere)
        if len(atom_added_points[i]) > 0:
            remove_ndx = []
            dist_mat = distance_matrix(atom_sphere, np.array(atom_added_points[i]) - coords[i])
            mask *= np.any((dist_mat - tol) < 0)

            atom_sphere = atom_sphere[mask]

            atom_sphere = np.array(atom_sphere)
            n_atom_grid = len(atom_sphere)
            atom_sphere = np.concatenate((atom_sphere, np.array(atom_added_points[i]) - coords[i]))

        if len(atom_sphere) < 4:
            continue
        atom_hull = ConvexHull(atom_sphere / radius_list[i])
        tri = atom_hull.simplices

        atom_sphere += coords[i]
        
        remove_v = []
        new_ndx = np.zeros(len(atom_sphere), dtype=int)

        # remove any points that are covered by another atom
        # only loop over n_atom_grid points so we don't remove
        # any points right on the intersection b/c of 
        # numerical issues
        del_count = 0
        atom_grid_dist = distance_matrix(atom_sphere, coords)
        center_atom_grid_dist = distance_matrix(atom_sphere, [center_coords])[:,0]
        for j in range(0, n_atom_grid):
            if center_atom_grid_dist[j] > radius:
                remove_v.append(j)
                del_count += 1
                continue
            for k in range(0, len(coords)):
                if i == k:
                    continue
                if atom_grid_dist[j,k] < radius_list[k]:
                    remove_v.append(j)
                    del_count += 1
                    break
            
            new_ndx[j] = j - del_count
        
        for j in range(n_atom_grid, len(atom_sphere)):
            new_ndx[j] = j - del_count
    
        if len(remove_v) == len(atom_sphere):
            continue
    
        atom_sphere = atom_sphere.tolist()
        for vi in remove_v[::-1]:
            atom_sphere.pop(vi)
            tri = tri[np.all(tri != vi, axis=1)]
        
        for j, ti in enumerate(tri):
            for k, v in enumerate(ti):
                tri[j][k] = new_ndx[v]
  
        atom_sphere = np.array(atom_sphere)
        norms = -(atom_sphere - coords[i]) / radius_list[i]
        
        triangles.extend(tri + len(vertices))
        vertices.extend(atom_sphere)
        normals.extend(norms)
    

    remove_ndx = []
    if len(center_added_points) > 0:
        dist_mat = distance_matrix(sphere, center_added_points)
        for i in range(0, len(sphere)):
            for j in range(0, len(center_added_points)):
                if dist_mat[i,j] < tol:
                    remove_ndx.append(i)
                    break
        
        sphere = sphere.tolist()
        for ndx in remove_ndx[::-1]:
            sphere.pop(ndx)
        
        sphere = np.array(sphere)
    
    n_sphere = len(sphere)
    if center_added_points:
        sphere = np.concatenate((sphere, np.array(center_added_points)))

    center_hull = ConvexHull(sphere / radius)
    sphere += center_coords
    tri = center_hull.simplices
    
    remove_v = []
    new_ndx = np.zeros(len(sphere), dtype=int)
    del_count = 0
    center_grid_dist = distance_matrix(sphere, coords)
    for i in range(0, n_sphere):
        if volume_type == "free":
            for j in range(0, len(coords)):
                if center_grid_dist[i,j] < radius_list[j]:
                    remove_v.append(i)
                    del_count += 1
                    break
            
        elif volume_type == "buried":
            if all(center_grid_dist[i,j] > radius_list[j] for j in range(0, len(coords))):
                remove_v.append(i)
                del_count += 1

        new_ndx[i] = i - del_count
        
    for i in range(n_sphere, len(sphere)):
        new_ndx[i] = i - del_count
        
    sphere = sphere.tolist()
    mask = np.ones(len(tri), dtype=bool)
    for vi in remove_v[::-1]:
        sphere.pop(vi)
        mask *= np.invert(np.any(tri == vi, axis=1))
    tri = tri[mask]

    new_t = tri
    if volume_type == "buried":
        mask = np.invert(np.all(new_t >= n_sphere, axis=1))
        new_t = new_t[mask]

    new_t = np.array(new_t)

    for i, ti in enumerate(new_t):
        new_t[i] = new_ndx[ti]

    norms = []
    if sphere:
        sphere = np.array(sphere)
        norms = (sphere - center_coords) / radius
    
    triangles.extend(new_t + len(vertices))
    vertices.extend(sphere)
    normals.extend(norms)
    
    # the triangles need to be reordered so the points are 
    # clockwise (or counterclockwise? i don't remember)
    vertices = np.array(vertices)
    normals = np.array(normals)
    triangles = np.array(triangles)
    v1 = vertices[triangles[:,1]] - vertices[triangles[:,0]]
    v2 = vertices[triangles[:,2]] - vertices[triangles[:,0]]
    c = np.cross(v1, v2)
    mask = np.sum(c * normals[triangles[:,0]], axis=1) < 0
    triangles[mask] = triangles[mask, ::-1]

    model.set_geometry(vertices, normals, triangles)
    
    # profile.disable()
    # from TestManager.stream_holder import StreamHolder
    # import pstats
    # stream = StreamHolder(session)
    # pstats.Stats(profile, stream=stream).strip_dirs().sort_stats(-1).print_stats()
    # stream.flush()

    
    return model