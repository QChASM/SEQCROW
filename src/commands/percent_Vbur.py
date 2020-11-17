import numpy as np

from io import BytesIO

from chimerax.core.commands import BoolArg, StringArg, CmdDesc, EnumOf, FloatArg, IntArg, ModelsArg
from chimerax.atomic import AtomsArg, AtomicStructure
from chimerax.bild.bild import read_bild

from AaronTools.substituent import Substituent
from AaronTools.const import VDW_RADII, BONDI_RADII

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.finders import AtomSpec

vbur_description = CmdDesc(required=[("selection", ModelsArg)], \
                               keyword=[("radii", EnumOf(["UMN", "Bondi"], 
                                                         case_sensitive=False,
                                                  ),
                                        ),
                                        ("radius", FloatArg), 
                                        ("scale", FloatArg), 
                                        ("method", EnumOf(["leb", "mc"], ["Lebedev", "Monte-Carlo"], 
                                                         case_sensitive=False,
                                                  ),
                                        ),
                                        ("radialPoints", EnumOf(["20", "32", "64", "75", "99", "127"])),                                        
                                        ("angularPoints", EnumOf(["110", "194", "302", "590", "974", "1454", "2030", "2702", "5810"])),                                        
                                        ("minimumIterations", IntArg), 
                                        ("scale", FloatArg), 
                                        ("onlyAtoms", AtomsArg), 
                                        ("centerAtoms", AtomsArg), 
                               ],
                               synopsis="calculate volume buried by ligands around a metal center"
                       )

def percent_vbur(session, 
                 selection, 
                 radii="UMN", 
                 radius=3.5, 
                 scale=1.17, 
                 method="Lebedev", 
                 radialPoints=20, 
                 angularPoints=1454, 
                 minimumIterations=25,
                 onlyAtoms=None,
                 centerAtoms=None,
    ):
    
    models = {model:[atom for atom in model.atoms if onlyAtoms is not None and atom in onlyAtoms] for model in selection if isinstance(model, AtomicStructure)}
    
    s = "<pre>model\tcenter atom\t%Vbur\n"
    
    for model in models:
        if len(models[model]) == 0:
            targets = None
        else:
            targets = [AtomSpec(atom.atomspec) for atom in models[model]]
        
        center = []
        if centerAtoms is not None:
            for atom in centerAtoms:
                if atom in model.atoms:
                    center.append(AtomSpec(atom.atomspec))
        
        rescol = ResidueCollection(model)
        
        if len(center) == 0:
            rescol.detect_components()
            center = rescol.center
            
        for c in center:
            vbur = rescol.percent_buried_volume(targets=targets,
                                                center=c,
                                                radius=radius,
                                                radii=radii,
                                                scale=scale,
                                                method=method,
                                                rpoints=int(radialPoints),
                                                apoints=int(angularPoints),
                                                min_iter=minimumIterations,
            )
            
            s += "%s\t%s\t%4.1f%%\n" % (model.atomspec, c.atomspec, vbur)
    
    s = s.strip()
    s += "</pre>"
    
    session.logger.info(s, is_html=True)
