def register_selectors(logger):
    from chimerax.core.commands import register_selector
    register_selector("tm", tm_selector, logger, desc="transition metals")
    
def tm_selector(session, models, results):
    """select transition metals using AaronTools' TMETAL dictionary"""
    from chimerax.atomic import AtomicStructure, Atoms
    from AaronTools.const import TMETAL
        
    atoms = []
    for model in models:
        if isinstance(model, AtomicStructure):
            for atom in model.atoms:
                if atom.element.name in TMETAL:
                    atoms.append(atom)
    
    #need to add a Collection, not just a list of atoms
    results.add_atoms(Atoms(atoms))