import concurrent.futures
from cProfile import Profile
import os

import numpy as np

from chimerax.core.commands import (
    BoolArg,
    StringArg,
    CmdDesc,
    EnumOf,
    FloatArg,
    IntArg,
    ModelsArg,
    Or,
    TupleOf,
    run,
)
from chimerax.atomic import AtomsArg, AtomicStructure, Atoms
from chimerax.label.label3d import ObjectLabel, ObjectLabels
from chimerax.core.models import Surface

from AaronTools.const import VDW_RADII, BONDI_RADII
from AaronTools.finders import AnyTransitionMetal
from AaronTools.utils.utils import rotation_matrix, fibonacci_sphere, perp_vector

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec

from scipy.spatial import distance_matrix, ConvexHull


class VoidLabel(ObjectLabel):
    def __init__(self, text, location, view):
        self._location = location
        super().__init__(None, view, text=text)
    
    def location(self, scene_position=None):
        return self._location


class VoidLabels(ObjectLabels):
    def add_labels(self, labels):
        self._labels.extend(labels)
        self._count_pixel_sized_labels()
        self.update_labels()
    
    def labels(self, objects=None):
        if objects is None:
            return self._labels
        ol = self._object_label
        return [ol[o] for o in objects if o in ol]


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
        ("labels", EnumOf(["none", "quadrants", "octants"])), 
        ("reportComponent", EnumOf(["total", "quadrants", "octants"])),
        ("useScene", BoolArg), 
        ("difference", BoolArg), 
    ],
    synopsis="calculate volume buried by ligands around a center",
    url="https://github.com/QChASM/SEQCROW/wiki/Commands#percentVolumeBuried",
)


def _vbur(
    session,
    model,
    ligand_atoms,
    center,
    key_atoms,
    radius=3.5,
    radii="UMN",
    scale=1.17, 
    method="Lebedev", 
    radialPoints=20, 
    angularPoints=1454, 
    minimumIterations=25,
    displaySphere=None,
    pointSpacing=0.1,
    intersectionScale=6,
    palette="rainbow",
    steric_map=False,
    useScene=False,
    num_pts=100,
    shape="circle",
    labels="none",
    reportComponent="total",
):
    profile = Profile()
    profile.enable()
    # get corresponding AaronTools Geometry
    rescol = ResidueCollection(model, bonds_matter=False)
    # get list of AaronTools ligand atoms
    # print("finding targets")
    targets = rescol.find([AtomSpec(a.atomspec) for a in ligand_atoms])
    # print("found targets")
    
    basis = None
    if useScene:
        oop_vector = session.view.camera.get_position().axes()[2]
        ip_vector = session.view.camera.get_position().axes()[1]
        x_vec = session.view.camera.get_position().axes()[0]
        basis = np.array([x_vec, ip_vector, oop_vector]).T

    center_xyz = center
    if not isinstance(center_xyz, np.ndarray):
        center_xyz = np.mean(center.coords, axis=0)

    elif labels != "none" or reportComponent != "total" or difference:
        if not key_atoms:
            raise RuntimeError
        oop_vector = np.zeros(3)
        for atom in key_atoms:
            oop_vector += center_xyz - atom.coord
        
        if len(key_atoms) == 1:
            ip_vector = perp_vector(oop_vector)
            x_vec = np.cross(ip_vector, oop_vector)
        else:
            coords = [atom.coord for atom in key_atoms]
            coords.append(center_xyz)
            coords = np.array(coords)
            ip_vector = perp_vector(coords)
            x_vec = np.cross(ip_vector, oop_vector)
            x_vec /= np.linalg.norm(x_vec)
            ip_vector = -np.cross(x_vec, oop_vector)
        ip_vector /= np.linalg.norm(ip_vector)

        basis = np.array([x_vec, ip_vector, oop_vector]).T

    out = [rescol]

    if steric_map:
        steric_info = rescol.steric_map(
            center=center_xyz,
            key_atoms=[AtomSpec(a) for a in key_atoms],
            radii=radii,
            oop_vector=oop_vector,
            ip_vector=ip_vector,
            radius=radius,
            return_basis=True,
            num_pts=num_pts,
            shape=shape,
            targets=targets,
        )
        out.append(steric_info)


    # print("calculating buried volume")
    vbur = rescol.percent_buried_volume(
        targets=targets,
        basis=basis,
        center=center_xyz,
        radius=radius,
        radii=radii,
        scale=scale,
        method=method,
        rpoints=int(radialPoints),
        apoints=int(angularPoints),
        min_iter=minimumIterations,
    )
    # print("done")
    
    out.append(vbur)
    
    if displaySphere:
        mdls = vbur_vis(
            session,
            rescol,
            targets,
            radii,
            scale,
            radius, 
            center_xyz, 
            pointSpacing, 
            intersectionScale,
            displaySphere,
            vbur,
            labels,
            basis=basis,
        )
        
        out.append(mdls)
    
    profile.disable()
    profile.print_stats()
    
    return out



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
        useScene=False,
        num_pts=100,
        shape="circle",
        labels="none",
        reportComponent="total",
        difference=False,
):
    
    out = []
    args = []
    kwargs = []
    rescols = []
    
    if center is not None and not isinstance(center, tuple):
        center = Atoms(center)
    
    models = {
        model:[atom for atom in model.atoms if onlyAtoms is not None and atom in onlyAtoms]
        for model in selection if isinstance(model, AtomicStructure)
    }
    
    s = "<pre>model\tcenter\t%Vbur\n"
    
    for model in models:
        targets = models[model]
        if len(models[model]) == 0:
            targets = None
        print(center)
        mdl_center = None
        if center is not None:
            if isinstance(center, tuple):
                mdl_center = np.array(center)
            elif isinstance(center, Atoms):
                mdl_center = model.atoms.intersect(center)

        if mdl_center is None:
            mdl_center = Atoms([a for a in model.atoms if a.is_metal])

        key_atoms = None

        if not useCentroid and not isinstance(center, np.ndarray):
            for c in mdl_center:
                args.append([
                    session,
                    model,
                    targets,
                    Atoms([c]),
                    key_atoms,
                ])
                
                kwargs.append({
                    "radii": radii,
                    "radius": radius,
                    "scale": scale,
                    "method": method,
                    "radialPoints": radialPoints,
                    "angularPoints": angularPoints,
                    "minimumIterations": minimumIterations,
                    "displaySphere": displaySphere,
                    "pointSpacing": pointSpacing,
                    "intersectionScale": intersectionScale,
                    "palette": palette,
                    "steric_map": steric_map,
                    "useScene": useScene,
                    "num_pts": num_pts,
                    "shape": shape,
                    "labels": labels,
                    "reportComponent": reportComponent,
                })

        else:
            args.append([
                session,
                model,
                targets,
                mdl_center,
                key_atoms,
            ])
            
            kwargs.append({
                "radii": radii,
                "radius": radius,
                "scale": scale,
                "method": method,
                "radialPoints": radialPoints,
                "angularPoints": angularPoints,
                "minimumIterations": minimumIterations,
                "displaySphere": displaySphere,
                "pointSpacing": pointSpacing,
                "intersectionScale": intersectionScale,
                "palette": palette,
                "steric_map": steric_map,
                "useScene": useScene,
                "num_pts": num_pts,
                "shape": shape,
                "labels": labels,
                "reportComponent": reportComponent,
            })

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        data = [
            executor.submit(_vbur, *arg, **kwarg)
            for arg, kwarg in zip(args, kwargs)
        ]
        results = [d.result() for d in data]

    print(results)
    
    if difference and displaySphere:
        if len(out) < 2:
            session.logger.warning(
                "difference of %s volume was requested, but only one cutout was drawn; calculate "
                "the buried volume for multiple centers to visualize the differences between them"
            )
        for i, data1 in enumerate(out):
            rescol1 = rescols[i]
            model1, center1, targets1, basis1, vbur1 = data1[:5]
            for j, data2 in enumerate(out[i+1:]):
                rescol2 = rescols[i + j + 1]
                model2, center2, targets2, basis2, vbur2 = data2[:5]
                mdl = vbur_difference_vis(
                    session,
                    rescol1, rescol2,
                    targets1, targets2,
                    radii,
                    scale,
                    radius,
                    center1, center2,
                    pointSpacing,
                    intersectionScale,
                    displaySphere,
                    vbur1, vbur2,
                    labels,
                    basis1, basis2,
                )
                model1.add(mdl)
                args = [
                    "color", mdl[0].atomspec, "red"
                    ";",
                    "transparency", mdl[0].atomspec, "50", 
                ]
                run(session, " ".join(args))
                args = [
                    "color", mdl[1].atomspec, "blue"
                    ";",
                    "transparency", mdl[1].atomspec, "50", 
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
        vbur,
        labels,
        basis=None,
):
    # from cProfile import Profile
    # 
    # profile = Profile()
    # profile.enable()

    # number of points is based on surface area
    n_grid = int(4 * np.pi * radius ** 2 / point_spacing)
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
            r_t = perp_vector(v_n)
            
            r0 = np.cross(r_t, v_n)
            r0 *= h / np.linalg.norm(r0)
            
            rot_angle = 2 * np.pi / n_added
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
                r_t = perp_vector(v_n)
                
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

    tol = 0
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
            dist_mat = distance_matrix(
                atom_sphere,
                np.array(atom_added_points[i]) - coords[i]
            )
            mask[np.min((dist_mat - tol), axis=1) < 0] = False

            atom_sphere = atom_sphere[mask]

            atom_sphere = np.array(atom_sphere)
            n_atom_grid = len(atom_sphere)
            atom_sphere = np.concatenate((
                atom_sphere,
                np.array(atom_added_points[i]) - coords[i]
            ))

        if len(atom_sphere) < 4:
            continue

        atom_hull = ConvexHull(atom_sphere / radius_list[i])
        tri = atom_hull.simplices

        atom_sphere += coords[i]

        # remove any points that are covered by another atom
        # only loop over n_atom_grid points so we don't remove
        # any points right on the intersection b/c of 
        # numerical issues
        del_count = 0
        atom_grid_dist = distance_matrix(atom_sphere, coords)
        center_atom_grid_dist = distance_matrix(atom_sphere, [center_coords])[:,0]
        keep_v = []
        for j in range(0, n_atom_grid):
            if center_atom_grid_dist[j] > radius:
                continue
            for k in range(0, len(coords)):
                if i == k:
                    continue
                if atom_grid_dist[j,k] < radius_list[k]:
                    break
            else:
                keep_v.append(j)
        
        keep_v.extend(
            np.arange(
                len(atom_sphere) - len(atom_added_points[i]),
                len(atom_sphere),
                dtype=int,
            )
        )
        
        new_ndx = {old: new for new, old in enumerate(keep_v)}

        if len(keep_v) == 0:
            continue
    
        mask = np.min(np.isin(tri, keep_v), axis=1)
        tri = tri[mask]
        if len(tri) < 1:
            continue
        tri = np.vectorize(new_ndx.get)(tri)
        
        mask = np.zeros(len(atom_sphere), dtype=bool)
        mask[keep_v] = True
        atom_sphere = atom_sphere[mask]

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

    if labels != "none":   
        d = model.new_drawing(labels)
        d.display_style = d.Mesh
        d.use_lighting = False
        d.casts_shadows = False
        d.pickable = False
        
        d_theta = np.pi / 180
        oct_radius = 1.01 * radius
        verts = [np.zeros(3)]
        triangles = []
        for k, v in enumerate(basis.T):            
            if labels == "quadrants" and k == 2:
                continue
            
            start_ndx = len(verts)
            prev_vert = oct_radius * perp_vector(v)
            verts.append(prev_vert)
            R = rotation_matrix(d_theta, v)

            for i in range(1, 360):
                triangles.append([0, start_ndx + i - 1, start_ndx + i])
                prev_vert = np.dot(R, prev_vert)
                verts.append(prev_vert)
            
            triangles.append([0, start_ndx, start_ndx + i - 1])
            
            for v2 in basis.T[:k]:
                v3 = np.cross(v, v2)
                v3 /= np.linalg.norm(v3)
                v3 *= oct_radius
                ndx = len(verts)
                verts.append(v)
                verts.append(v3)
                triangles.append([ndx, 0, ndx + 1])
                ndx = len(verts)
                verts.append(v)
                verts.append(-v3)
                triangles.append([ndx, 0, ndx + 1])
                ndx = len(verts)
                verts.append(-v)
                verts.append(-v3)
                triangles.append([ndx, 0, ndx + 1])
                ndx = len(verts)
                verts.append(-v)
                verts.append(v3)
                triangles.append([ndx, 0, ndx + 1])

        norms = np.array(verts) / oct_radius
        verts = np.array(verts) + center_coords
        triangles = np.array(triangles)
        
        d.set_geometry(verts, norms, triangles)
        d.set_edge_mask(2 * np.ones(len(triangles), dtype=int))
    
        label_list = []
        x = basis.T[0]
        x = x / np.linalg.norm(x)
        y = basis.T[1]
        y = y / np.linalg.norm(y)
        z = basis.T[2]
        z = z / np.linalg.norm(z)
        if labels == "octants":
            for i, val in enumerate(vbur):
                coordinates = np.zeros(3)
    
                if any(i == n for n in [1, 2, 5, 6]):
                    coordinates -= x
                else:
                    coordinates += x
                if any(i == n for n in [2, 3, 4, 5]):
                    coordinates -= y
                else:
                    coordinates += y
                if i > 3:
                    coordinates -= z
                else:
                    coordinates += z
                if volume_type == "free":
                    l = "%.1f%%" % (100 / 8 - val)
                else:
                    l = "%.1f%%" % (val)
                coordinates /= np.linalg.norm(coordinates)
                coordinates *= radius
                coordinates += center_coords
                label_list.append(
                    VoidLabel(l, coordinates, session.main_view)
                )
        else:
            quad_vbur = [
                vbur[0] + vbur[7],
                vbur[1] + vbur[6],
                vbur[2] + vbur[5],
                vbur[3] + vbur[4],
            ]
            for i, val in enumerate(quad_vbur):
                coordinates = np.zeros(3)
                if any(i == n for n in [1, 2]):
                    coordinates -= x
                else:
                    coordinates += x
                if any(i == n for n in [2, 3]):
                    coordinates -= y
                else:
                    coordinates += y

                if volume_type == "free":
                    l = "%.1f%%" % (25 - val)
                else:
                    l = "%.1f%%" % (val)
                coordinates /= np.linalg.norm(coordinates)
                coordinates *= radius
                coordinates += center_coords
                label_list.append(
                    VoidLabel(l, coordinates, session.main_view)
                )
        label_object = VoidLabels(session)
        label_object.add_labels(label_list)
        model.add([label_object])
        return [model]
    
    return [model]
    


def vbur_difference_vis(
        session,
        geom1, geom2,
        targets1, targets2,
        radii,
        scale,
        radius, 
        center1, center2,
        point_spacing, 
        intersection_scale,
        volume_type,
        vbur1, vbur2,
        labels,
        basis1, basis2
):

    # number of points is based on surface area
    n_grid = int(4 * np.pi * radius**2 / point_spacing)

    # to display the difference between buried/free volumes, I use basically
    # the same procedure as the buried/free volume for a single structure
    # first, we need to draw a portion of a sphere for each atom
    # any vertices on these spheres that would be covered up by another
    # atom's sphere from the same structure is removed
    # vertices are added at the intersection of atom pairs to make it look
    # less jagged
    # then we need to determine whether the vertex belongs to model_a or model_b
    # model_a and model_b switch depending on whether we are showing the difference
    # in buried volume or in free volume
    # if a vertex is covered by geom1 atoms but not geom2 atoms, add it to model_a
    # for the flipped criteria, add the vertex to model_b

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
    
    models = []

    vertices1 = []
    normals1 = []
    triangles1 = []
    
    vertices2 = []
    normals2 = []
    triangles2 = []

    if basis1 is None:
        basis1 = np.eye(3)
    
    if basis2 is None:
        basis2 = np.eye(3)

    if volume_type == "buried":
        model_a = Surface("%%Vburied %s only" % geom1.name, session)
        model_b = Surface("%%Vburied %s only" % geom2.name, session)
    else:
        model_b = Surface("%%Vfree %s only" % geom1.name, session)
        model_a = Surface("%%Vfree %s only" % geom2.name, session)

    if isinstance(center1, np.ndarray):
        center_coords1 = center1
    else:
        center_coords1 = geom1.COM(center1)
    
    if not hasattr(center1, "__iter__"):
        center1 = [center1]
     
    if isinstance(center2, np.ndarray):
        center_coords2 = center2
    else:
        center_coords2 = geom2.COM(center2)

    if not hasattr(center2, "__iter__"):
        center = [center2]
    
    if targets1 is None:
        if len(center1) == 1:
            atoms1 = [atom for atom in geom1.atoms if atom not in center1]
        else:
            atoms1 = geom1.atoms
    else:
        atoms1 = geom1.find(targets1)
    
    if targets2 is None:
        if len(center2) == 1:
            atoms2 = [atom for atom in geom2.atoms if atom not in center2]
        else:
            atoms2 = geom2.atoms
    else:
        atoms2 = geom2.find(targets2)
    
    atoms_within_radius1 = []
    for atom in atoms1:
        # determine which atom's radii extend within the sphere
        # reduces the number of distances we need to calculate
        d = np.linalg.norm(center_coords1 - atom.coords)
        inner_edge = d - scale * radii_dict[atom.element]
        if inner_edge < radius:
            atoms_within_radius1.append(atom)
    
    atoms_within_radius2 = []
    for atom in atoms2:
        d = np.linalg.norm(center_coords2 - atom.coords)
        inner_edge = d - scale * radii_dict[atom.element]
        if inner_edge < radius:
            atoms_within_radius2.append(atom)
    
    
    # sort atoms based on their distance to the center
    # this makes is so we usually break out of looping over the atoms faster
    atoms_within_radius1.sort(
        key=lambda a, c=center_coords1: np.linalg.norm(a.coords - c)
    )
    atoms_within_radius2.sort(
        key=lambda a, c=center_coords2: np.linalg.norm(a.coords - c)
    )
    
    radius_list1 = np.array([
        scale * radii_dict[atom.element] for atom in atoms_within_radius1
    ])

    radius_list2 = np.array([
        scale * radii_dict[atom.element] for atom in atoms_within_radius2
    ])

    coords1 = geom1.coordinates(atoms_within_radius1)
    coords2 = geom2.coordinates(atoms_within_radius2)
    coords2 -= center_coords2
    h = np.dot(basis2.T, basis1)
    u, s, v = np.linalg.svd(h)
    R = np.matmul(v, u.T)
    if np.sign(np.linalg.det(R)) < 0:
        R[:, 2] *= -1
    coords2 = np.matmul(coords2, R.T)
    coords2 += center_coords1

    atom_dist1 = distance_matrix(coords1, coords1)
    atom_dist12 = distance_matrix(coords1, coords2)
    atom_dist2 = distance_matrix(coords2, coords2)
    
    sphere1 = fibonacci_sphere(num=n_grid, radius=radius)
    sphere2 = fibonacci_sphere(num=n_grid, radius=radius)
    
    # add points right where spheres intersect
    # this makes the intersections look less pokey
    d_ac1 = distance_matrix(coords1, [center_coords1])
    d_ac2 = distance_matrix(coords2, [center_coords1])
    center_added_points1 = []
    center_added_points2 = []
    atom_added_points1 = [[] for atom in atoms_within_radius1]
    pair_added_points1 = [[] for atom in atoms_within_radius1]
    atom_added_points2 = [[] for atom in atoms_within_radius2]
    pair_added_points2 = [[] for atom in atoms_within_radius2]
    for i in range(0, len(coords1)):
        r1 = radius_list1[i]    
        v_n = coords1[i] - center_coords1
        v_n /= np.linalg.norm(v_n)
        d = d_ac1[i, 0]
        # intersection with big sphere
        if d + r1 > radius:
            theta = np.arccos((r1 ** 2 - radius ** 2 - d ** 2) / (-2 * d * radius))
            h = radius * np.sin(theta)
            b = radius * np.cos(theta)
            p = b * v_n
            
            circ = 2 * np.pi * h
            n_added = int(np.ceil(intersection_scale * circ / point_spacing))
            r_t = perp_vector(v_n)
            
            r0 = np.cross(r_t, v_n)
            r0 *= h / np.linalg.norm(r0)
            
            rot_angle = 2 * np.pi / n_added
            R = rotation_matrix(rot_angle, v_n)
            prev_r = r0
            prev_r_list = []
            for x in np.linspace(0, 2*np.pi, num=n_added):
                prev_r = np.dot(R, prev_r)
                prev_r_list.append(prev_r)
            prev_r_list = np.array(prev_r_list)
            d_ep = distance_matrix(prev_r_list + p + center_coords1, coords1)
            # if the point is obscured by another atom, don't bother adding it
            # this saves time on triangulation
            diff_mat = d_ep - radius_list1[np.newaxis, :]
            diff_mat[:, i] = 1
            mask = np.invert(np.any(diff_mat < 0, axis=1))

            center_added_points1.extend(prev_r_list[mask] + p)
            atom_added_points1[i].extend(prev_r_list[mask] + p + center_coords1)
    
        for j in range(0, i):
            d = atom_dist1[i, j]
            r2 = radius_list1[j]
            if d < r1 + r2 and d > abs(r1 - r2):
                v_n = coords1[j] - coords1[i]
                v_n /= np.linalg.norm(v_n)
                theta = np.arccos((r2 ** 2 - r1 ** 2 - d ** 2) / (-2 * r1 * d))
                h = r1 * np.sin(theta)
                b = r1 * np.cos(theta)
                p = b * v_n
                
                circ = 2 * np.pi * h
                n_added = int(np.ceil(intersection_scale * circ / point_spacing))
                r_t = perp_vector(v_n)
                
                r0 = np.cross(r_t, v_n)
                r0 *= h / np.linalg.norm(r0)
    
                rot_angle = 2*np.pi / n_added
                R = rotation_matrix(rot_angle, v_n)
                prev_r = r0
                prev_r_list = []
                for x in np.linspace(0, 2 * np.pi, num=n_added):
                    prev_r = np.dot(R, prev_r)
                    prev_r_list.append(prev_r)
                prev_r_list = np.array(prev_r_list)
                norm_mask = np.linalg.norm(
                    center_coords1 - (prev_r_list + p + coords1[i]), axis=1
                ) < radius
                prev_r_list = prev_r_list[norm_mask]
                
                if not len(prev_r_list):
                    continue
                d_ep = distance_matrix(prev_r_list + p + coords1[i], coords1)
                diff_mat = d_ep - radius_list1
                diff_mat[:, i] = 1
                diff_mat[:, j] = 1
                mask = np.invert(np.any(diff_mat < 0, axis=1))
                if any(mask):
                    atom_added_points1[i].extend(prev_r_list[mask] + p + coords1[i])
                    atom_added_points1[j].extend(prev_r_list[mask] + p + coords1[i])
    
        for j in range(0, len(coords2)):
            d = atom_dist12[i, j]
            r2 = radius_list2[j]
            if d < r1 + r2 and d > abs(r1 - r2):
                v_n = coords2[j] - coords1[i]
                v_n /= np.linalg.norm(v_n)
                theta = np.arccos((r2 ** 2 - r1 ** 2 - d ** 2) / (-2 * r1 * d))
                h = r1 * np.sin(theta)
                b = r1 * np.cos(theta)
                p = b * v_n
                
                circ = 2 * np.pi * h
                n_added = int(np.ceil(intersection_scale * circ / point_spacing))
                r_t = perp_vector(v_n)
                
                r0 = np.cross(r_t, v_n)
                r0 *= h / np.linalg.norm(r0)
    
                rot_angle = 2 * np.pi / n_added
                R = rotation_matrix(rot_angle, v_n)
                prev_r = r0
                prev_r_list = []
                for x in np.linspace(0, 2 * np.pi, num=n_added):
                    prev_r = np.dot(R, prev_r)
                    prev_r_list.append(prev_r)
                prev_r_list = np.array(prev_r_list)
                norm_mask = np.linalg.norm(
                    center_coords1 - (prev_r_list + p + coords1[i]), axis=1
                ) < radius
                prev_r_list = prev_r_list[norm_mask]
                
                if not len(prev_r_list):
                    continue
                
                d_ep = distance_matrix(prev_r_list + p + coords1[i], coords1)
                diff_mat = d_ep - radius_list1
                diff_mat[:, i] = 1
                mask = np.invert(np.any(diff_mat < 0, axis=1))
                if any(mask):
                    prev_r_list = prev_r_list[mask]
                    excl_d_ep = distance_matrix(prev_r_list + p + coords1[i], coords2)
                    excl_diff_mat = excl_d_ep - radius_list2
                    excl_diff_mat[:, j] = 1
                    excl_mask = np.invert(np.any(excl_diff_mat < 0, axis=1))
                    if any(excl_mask):
                        pair_added_points1[i].extend(prev_r_list[excl_mask] + p + coords1[i])
                        pair_added_points2[j].extend(prev_r_list[excl_mask] + p + coords1[i])
    
    
    
    for i in range(0, len(coords2)):
        r1 = radius_list2[i]    
        v_n = coords2[i] - center_coords1
        v_n /= np.linalg.norm(v_n)
        d = d_ac2[i, 0]
        # intersection with big sphere
        if d + r1 > radius:
            theta = np.arccos((r1 ** 2 - radius ** 2 - d ** 2) / (-2 * d * radius))
            if np.isnan(theta):
                continue
            h = radius * np.sin(theta)
            b = radius * np.cos(theta)
            p = b * v_n
            
            circ = 2 * np.pi * h
            n_added = int(np.ceil(intersection_scale * circ / point_spacing))
            r_t = perp_vector(v_n)
            
            r0 = np.cross(r_t, v_n)
            r0 *= h / np.linalg.norm(r0)
            
            rot_angle = 2 * np.pi / n_added
            R = rotation_matrix(rot_angle, v_n)
            prev_r = r0
            prev_r_list = []
            for x in np.linspace(0, 2*np.pi, num=n_added):
                prev_r = np.dot(R, prev_r)
                prev_r_list.append(prev_r)
            prev_r_list = np.array(prev_r_list)
            d_ep = distance_matrix(prev_r_list + p + center_coords1, coords2)
            # if the point is obscured by another atom, don't bother adding it
            # this saves time on triangulation
            diff_mat = d_ep - radius_list2[np.newaxis, :]
            diff_mat[:, i] = 1
            mask = np.invert(np.any(diff_mat < 0, axis=1))

            center_added_points2.extend(prev_r_list[mask] + p)
            atom_added_points2[i].extend(prev_r_list[mask] + p + center_coords1)
    
        for j in range(0, i):
            d = atom_dist2[i, j]
            r2 = radius_list2[j]
            if d < r1 + r2 and d > abs(r1 - r2):
                v_n = coords2[j] - coords2[i]
                v_n /= np.linalg.norm(v_n)
                theta = np.arccos((r2 ** 2 - r1 ** 2 - d ** 2) / (-2 * r1 * d))
                h = r1 * np.sin(theta)
                b = r1 * np.cos(theta)
                p = b * v_n

                circ = 2 * np.pi * h
                n_added = int(np.ceil(intersection_scale * circ / point_spacing))
                r_t = perp_vector(v_n)
                
                r0 = np.cross(r_t, v_n)
                r0 *= h / np.linalg.norm(r0)
    
                rot_angle = 2 * np.pi / n_added
                R = rotation_matrix(rot_angle, v_n)
                prev_r = r0
                prev_r_list = []
                for x in np.linspace(0, 2 * np.pi, num=n_added):
                    prev_r = np.dot(R, prev_r)
                    prev_r_list.append(prev_r)
                prev_r_list = np.array(prev_r_list)
                norm_mask = np.linalg.norm(
                    center_coords1 - (prev_r_list + p + coords2[i]), axis=1
                ) < radius
                prev_r_list = prev_r_list[norm_mask]
                
                if not len(prev_r_list):
                    continue
                
                d_ep = distance_matrix(prev_r_list + p + coords2[i], coords2)
                diff_mat = d_ep - radius_list2
                diff_mat[:, i] = 1
                diff_mat[:, j] = 1
                mask = np.invert(np.any(diff_mat < 0, axis=1))
                if any(mask):
                    atom_added_points2[i].extend(prev_r_list[mask] + p + coords2[i])
                    atom_added_points2[j].extend(prev_r_list[mask] + p + coords2[i])

    tol = 0
    for i in range(0, len(coords1)):
        # get a grid of points around each atom
        # remove any points that are close to an intersection
        # this makes it less likely for the triangulation to choose
        # one of these points instead of one that we already added
        # then, if we have to remove a triangle involving one of these points later,
        # it won't leave a gap
        n_atom_grid = int(radius_list1[i] ** 2 * n_grid / radius ** 2)
        atom_sphere = fibonacci_sphere(radius=radius_list1[i], num=n_atom_grid)

        mask = np.ones(len(atom_sphere), dtype=bool)
        n_atom_grid = len(atom_sphere)
        if len(atom_added_points1[i]) > 0:

            dist_mat = distance_matrix(
                atom_sphere,
                np.array(atom_added_points1[i]) - coords1[i]
            )
            mask[np.min((dist_mat - tol), axis=1) < 0] = False
    
            atom_sphere = atom_sphere[mask]
    
            atom_sphere = np.array(atom_sphere)
            n_atom_grid = len(atom_sphere)
            atom_sphere = np.concatenate((
                atom_sphere,
                np.array(atom_added_points1[i]) - coords1[i],
            ))
            if pair_added_points1[i]:
                atom_sphere = np.concatenate((
                    atom_sphere,
                    np.array(pair_added_points1[i]) - coords1[i]
                ))
                
        if len(atom_sphere) < 4:
            continue

        atom_hull = ConvexHull(atom_sphere / radius_list1[i])
        tri = atom_hull.simplices
    
        atom_sphere += coords1[i]
        
        add_to_mdl_1_verts = []
        add_to_mdl_2_verts = []
    
        # remove any points that are covered by another atom
        # only loop over n_atom_grid points so we don't remove
        # any points right on the intersection b/c of 
        # numerical issues
        atom_grid_dist = distance_matrix(atom_sphere, coords1)
        excl_atom_grid_dist = distance_matrix(atom_sphere, coords2)
        center_atom_grid_dist = distance_matrix(atom_sphere, [center_coords1])[:,0]
        for j in range(0, len(atom_sphere) - len(pair_added_points1[i])):
            if j < n_atom_grid:
                if center_atom_grid_dist[j] > radius:
                    continue
                
                mask = np.ones(len(radius_list1), dtype=bool)
                mask[i] = False
                
                if np.any(atom_grid_dist[j, mask] < radius_list1[mask]):
                    continue

            if np.any(excl_atom_grid_dist[j, :] <= (radius_list2)):
                add_to_mdl_2_verts.append(j)
            
            if np.all(excl_atom_grid_dist[j, :] >= (radius_list2)):
                add_to_mdl_1_verts.append(j)
            
        add_to_mdl_1_verts.extend(
            np.arange(
                len(atom_sphere) - len(pair_added_points1[i]),
                len(atom_sphere),
                dtype=int
            )
        )
        add_to_mdl_2_verts.extend(
            np.arange(
                len(atom_sphere) - len(pair_added_points1[i]),
                len(atom_sphere),
                dtype=int
            )
        )
        
        if len(add_to_mdl_1_verts) > 3:
            new_order = {old: new for new, old in enumerate(add_to_mdl_1_verts)}
            mask = np.min(np.isin(tri, add_to_mdl_1_verts), axis=1)
            keep_atom_sphere = atom_sphere[add_to_mdl_1_verts]
            keep_tri = tri[mask]
            if len(keep_tri) > 1:
                keep_tri = np.vectorize(new_order.get)(keep_tri)
                norms = -(keep_atom_sphere - coords1[i]) / radius_list1[i]
                
                triangles1.extend(keep_tri + len(vertices1))
                vertices1.extend(keep_atom_sphere)
                normals1.extend(norms)
            
        if len(add_to_mdl_2_verts) > 3:
            new_order = {old: new for new, old in enumerate(add_to_mdl_2_verts)}
            mask = np.min(np.isin(tri, add_to_mdl_2_verts), axis=1)
            keep_atom_sphere = atom_sphere[add_to_mdl_2_verts]
            keep_tri = tri[mask]
            # mask = np.all(keep_tri <= len(atom_sphere) - len(pair_added_points1[i]), axis=1)
            # keep_tri = keep_tri[mask]
            if len(keep_tri) > 1:
                keep_tri = np.vectorize(new_order.get)(keep_tri)
                norms = -(keep_atom_sphere - coords1[i]) / radius_list1[i]
                
                triangles2.extend(keep_tri + len(vertices2))
                vertices2.extend(keep_atom_sphere)
                normals2.extend(norms)


    for i in range(0, len(coords2)):
        # get a grid of points around each atom
        # remove any points that are close to an intersection
        # this makes it less likely for the triangulation to choose
        # one of these points instead of one that we already added
        # then, if we have to remove a triangle involving one of these points later,
        # it won't leave a gap
        n_atom_grid = int(radius_list2[i] ** 2 * n_grid / radius ** 2)
        atom_sphere = fibonacci_sphere(radius=radius_list2[i], num=n_atom_grid)
        mask = np.ones(len(atom_sphere), dtype=bool)
        n_atom_grid = len(atom_sphere)
        if len(atom_added_points2[i]) > 0:
            dist_mat = distance_matrix(
                atom_sphere,
                np.array(atom_added_points2[i]) - coords2[i]
            )
            mask[np.min((dist_mat - tol), axis=1) < 0] = False
    
            atom_sphere = atom_sphere[mask]
    
            atom_sphere = np.array(atom_sphere)
            n_atom_grid = len(atom_sphere)
            atom_sphere = np.concatenate((
                atom_sphere,
                np.array(atom_added_points2[i]) - coords2[i],
            ))
            if pair_added_points2[i]:
                atom_sphere = np.concatenate((
                    atom_sphere,
                    np.array(pair_added_points2[i]) - coords2[i]
                ))
                
        if len(atom_sphere) < 4:
            continue

        atom_hull = ConvexHull(atom_sphere / radius_list2[i])
        tri = atom_hull.simplices
    
        atom_sphere += coords2[i]
        
        add_to_mdl_1_verts = []
        add_to_mdl_2_verts = []
    
        atom_grid_dist = distance_matrix(atom_sphere, coords2)
        excl_atom_grid_dist = distance_matrix(atom_sphere, coords1)
        center_atom_grid_dist = distance_matrix(atom_sphere, [center_coords1])[:,0]
        for j in range(0, len(atom_sphere) - len(pair_added_points2[i])):
            if j < n_atom_grid:
                if center_atom_grid_dist[j] > radius:
                    continue
                
                mask = np.ones(len(radius_list2), dtype=bool)
                mask[i] = False
                
                if np.any(atom_grid_dist[j, mask] < radius_list2[mask]):
                    continue

            if np.any(excl_atom_grid_dist[j, :] <= (radius_list1)):
                add_to_mdl_1_verts.append(j)
            
            if np.all(excl_atom_grid_dist[j, :] >= (radius_list1)):
                add_to_mdl_2_verts.append(j)

            
        add_to_mdl_1_verts.extend(
            np.arange(
                len(atom_sphere) - len(pair_added_points2[i]),
                len(atom_sphere),
                dtype=int
            )
        )
        add_to_mdl_2_verts.extend(
            np.arange(
                len(atom_sphere) - len(pair_added_points2[i]),
                len(atom_sphere),
                dtype=int
            )
        )
        

        if len(add_to_mdl_1_verts) > 3:
            new_order = {old: new for new, old in enumerate(add_to_mdl_1_verts)}
            mask = np.min(np.isin(tri, add_to_mdl_1_verts), axis=1)
            keep_atom_sphere = atom_sphere[add_to_mdl_1_verts]
            keep_tri = tri[mask]
            if len(keep_tri) > 1:
                keep_tri = np.vectorize(new_order.get)(keep_tri)
                norms = -(keep_atom_sphere - coords2[i]) / radius_list2[i]
                
                triangles1.extend(keep_tri + len(vertices1))
                vertices1.extend(keep_atom_sphere)
                normals1.extend(norms)
            
        if len(add_to_mdl_2_verts) > 3:
            new_order = {old: new for new, old in enumerate(add_to_mdl_2_verts)}
            mask = np.min(np.isin(tri, add_to_mdl_2_verts), axis=1)
            keep_atom_sphere = atom_sphere[add_to_mdl_2_verts]
            keep_tri = tri[mask]
            # mask = np.all(keep_tri <= len(atom_sphere) - len(pair_added_points2[i]), axis=1)
            # keep_tri = keep_tri[mask]
            if len(keep_tri) > 1:
                keep_tri = np.vectorize(new_order.get)(keep_tri)
                norms = -(keep_atom_sphere - coords2[i]) / radius_list2[i]
                
                triangles2.extend(keep_tri + len(vertices2))
                vertices2.extend(keep_atom_sphere)
                normals2.extend(norms)

    sphere = fibonacci_sphere(radius=radius, num=n_grid)
    if len(center_added_points1) > 1:
        mask = np.ones(len(sphere), dtype=bool)
        dist_mat = distance_matrix(
            sphere + center_coords1, np.array(center_added_points1)
        )
        mask[np.min((dist_mat - tol), axis=1) < 0] = False
    
        sphere = sphere[mask]
    
        sphere = np.array(sphere)
        
        sphere = np.concatenate((
            sphere,
            np.array(center_added_points1),
        ))
    
    if len(center_added_points2) > 1:
        mask = np.ones(len(sphere), dtype=bool)
        dist_mat = distance_matrix(
            sphere, np.array(center_added_points2)
        )
        mask[np.min((dist_mat - tol), axis=1) < 0] = False
    
        sphere = sphere[mask]
    
        sphere = np.array(sphere)
        n_sphere = len(sphere)
    
        sphere = np.concatenate((
            sphere,
            np.array(center_added_points2),
        ))

    center_hull = ConvexHull(sphere / radius)
    sphere += center_coords1
    tri = center_hull.simplices
    
    add_to_mdl_1_verts = []
    add_to_mdl_2_verts = []
    d_sphere_atoms1 = distance_matrix(sphere, coords1) - radius_list1[np.newaxis, :]
    d_sphere_atoms2 = distance_matrix(sphere, coords2) - radius_list2[np.newaxis, :]
    for j in range(0, len(sphere)):
        if np.any(d_sphere_atoms1[j] <= 1e-4) and np.all(d_sphere_atoms2[j] >= -1e-4):
            add_to_mdl_1_verts.append(j)
        elif np.any(d_sphere_atoms2[j] <= 1e-4) and np.all(d_sphere_atoms1[j] >= -1e-4):
            add_to_mdl_2_verts.append(j)
    

    if len(add_to_mdl_1_verts) > 3:
        new_order = {old: new for new, old in enumerate(add_to_mdl_1_verts)}
        mask = np.min(np.isin(tri, add_to_mdl_1_verts), axis=1)
        keep_sphere = sphere[add_to_mdl_1_verts]
        keep_tri = tri[mask]
        if len(keep_tri) > 1:
            keep_tri = np.vectorize(new_order.get)(keep_tri)
            norms = -keep_sphere / radius

            triangles1.extend(keep_tri + len(vertices1))
            vertices1.extend(keep_sphere)
            normals1.extend(norms)
        
    if len(add_to_mdl_2_verts) > 3:
        new_order = {old: new for new, old in enumerate(add_to_mdl_2_verts)}
        mask = np.min(np.isin(tri, add_to_mdl_2_verts), axis=1)
        keep_sphere = sphere[add_to_mdl_2_verts]
        keep_tri = tri[mask]
        if len(keep_tri) > 1:
            keep_tri = np.vectorize(new_order.get)(keep_tri)
            norms = -keep_sphere / radius

            triangles2.extend(keep_tri + len(vertices2))
            vertices2.extend(keep_sphere)
            normals2.extend(norms)

    # the triangles need to be reordered so the points are 
    # clockwise (or counterclockwise? i don't remember)
    vertices1 = np.array(vertices1)
    normals1 = np.array(normals1)
    triangles1 = np.array(triangles1)
    v1 = vertices1[triangles1[:,1]] - vertices1[triangles1[:,0]]
    v2 = vertices1[triangles1[:,2]] - vertices1[triangles1[:,0]]
    c = np.cross(v1, v2)
    mask = np.sum(c * normals1[triangles1[:,0]], axis=1) < 0
    triangles1[mask] = triangles1[mask, ::-1]

    vertices2 = np.array(vertices2)
    normals2 = np.array(normals2)
    triangles2 = np.array(triangles2)
    v1 = vertices2[triangles2[:,1]] - vertices2[triangles2[:,0]]
    v2 = vertices2[triangles2[:,2]] - vertices2[triangles2[:,0]]
    c = np.cross(v1, v2)
    mask = np.sum(c * normals2[triangles2[:,0]], axis=1) < 0
    triangles2[mask] = triangles2[mask, ::-1]

    model_a.set_geometry(vertices1, normals1, triangles1)
    model_b.set_geometry(vertices2, normals2, triangles2)

    if labels != "none":
        vbur = [v1 - v2 for v1, v2 in zip(vbur1, vbur2)]
        d = model_a.new_drawing(labels)
        d.display_style = d.Mesh
        d.use_lighting = False
        d.casts_shadows = False
        d.pickable = False
        
        d_theta = np.pi / 180
        oct_radius = radius + 1e-2
        verts = [np.zeros(3)]
        triangles = []
        for k, v in enumerate(basis1.T):            
            if labels == "quadrants" and k == 2:
                continue
            
            start_ndx = len(verts)
            prev_vert = oct_radius * perp_vector(v)
            verts.append(prev_vert)
            R = rotation_matrix(d_theta, v)

            for i in range(1, 360):
                triangles.append([0, start_ndx + i - 1, start_ndx + i])
                prev_vert = np.dot(R, prev_vert)
                verts.append(prev_vert)
            
            triangles.append([0, start_ndx, start_ndx + i - 1])
            
            for v2 in basis1.T[:k]:
                v3 = np.cross(v, v2)
                v3 /= np.linalg.norm(v3)
                v3 *= oct_radius
                ndx = len(verts)
                verts.append(v)
                verts.append(v3)
                triangles.append([ndx, 0, ndx + 1])
                ndx = len(verts)
                verts.append(v)
                verts.append(-v3)
                triangles.append([ndx, 0, ndx + 1])
                ndx = len(verts)
                verts.append(-v)
                verts.append(-v3)
                triangles.append([ndx, 0, ndx + 1])
                ndx = len(verts)
                verts.append(-v)
                verts.append(v3)
                triangles.append([ndx, 0, ndx + 1])

        norms = np.array(verts) / oct_radius
        verts = np.array(verts) + center_coords1
        triangles = np.array(triangles)
        
        d.set_geometry(verts, norms, triangles)
        d.set_edge_mask(2 * np.ones(len(triangles), dtype=int))
    
        label_list = []
        x = basis1.T[0]
        x = x / np.linalg.norm(x)
        y = basis1.T[1]
        y = y / np.linalg.norm(y)
        z = basis1.T[2]
        z = z / np.linalg.norm(z)
        if labels == "octants":
            for i, val in enumerate(vbur):
                coordinates = np.zeros(3)
    
                if any(i == n for n in [1, 2, 5, 6]):
                    coordinates -= x
                else:
                    coordinates += x
                if any(i == n for n in [2, 3, 4, 5]):
                    coordinates -= y
                else:
                    coordinates += y
                if i > 3:
                    coordinates -= z
                else:
                    coordinates += z
                if volume_type == "free":
                    l = "%.1f%%" % -val
                else:
                    l = "%.1f%%" % val
                coordinates /= np.linalg.norm(coordinates)
                coordinates *= radius
                coordinates += center_coords1
                label_list.append(
                    VoidLabel(l, coordinates, session.main_view)
                )
        else:
            quad_vbur = [
                vbur[0] + vbur[7],
                vbur[1] + vbur[6],
                vbur[2] + vbur[5],
                vbur[3] + vbur[4],
            ]
            for i, val in enumerate(quad_vbur):
                coordinates = np.zeros(3)
                if any(i == n for n in [1, 2]):
                    coordinates -= x
                else:
                    coordinates += x
                if any(i == n for n in [2, 3]):
                    coordinates -= y
                else:
                    coordinates += y

                if volume_type == "free":
                    l = "%.1f%%" % -val
                else:
                    l = "%.1f%%" % val
                coordinates /= np.linalg.norm(coordinates)
                coordinates *= radius
                coordinates += center_coords1
                label_list.append(
                    VoidLabel(l, coordinates, session.main_view)
                )
        label_object = VoidLabels(session)
        label_object.add_labels(label_list)
        model_a.add([label_object])

    if volume_type == "buried":
        return [model_a, model_b]
    
    return [model_b, model_a]
