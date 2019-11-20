class Record:
    def __init__(self, name, cat_dict, ligPrefix="Lig", subPrefix="Sub", ligand=None, substitution=None, positions=None, component=None, perl=False, hidden=False):
        self.name = name
        self.cats = cat_dict
        self.ligPrefix = ligPrefix
        self.subPrefix = subPrefix
        self.ligand = ligand
        self.substitution = substitution
        self.positions = positions
        self.component = component
        self.perl = perl
        self.hidden = hidden
            
class InputManager:
    def __init__(self):
        self.records = {}
        
    def newRecord(self, name, model_str, *args, **kwargs):
        from chimera import replyobj
        from chimera.selection import OSLSelection
        from ChimAARON import ChimeraMolecule2AaronGeometry
        from AaronTools.catalyst import Catalyst
        
        mols = OSLSelection(model_str).molecules()

        cats = {}
        for i, mol in enumerate(mols):
            geom = ChimeraMolecule2AaronGeometry(mol)
            cat = Catalyst(geom, comment=mol.name)
                        
            replyobj.status("renaming atoms and adding tags...")
            for arn_atom in cat.atoms:
                chimatom = mol.atoms[geom.atoms.index(arn_atom)]
                tag = None
                for key in cat.components:
                    for c, component in enumerate(sorted(cat.components[key])):
                        if arn_atom in component.atoms:
                            tag = "%s.%i.%i" % (key, c, component.atoms.index(arn_atom) + 1)
                            chimatom.tag = tag
                            arn_atom.add_tag(tag)
            
                if arn_atom in sorted(cat.center):
                    tag = "center.%i" % cat.center.index(arn_atom)
                    chimatom.tag = tag
                    arn_atom.add_tag(tag)
            
            cat.rebuild()
                        
            cats[mol] = cat
        
        self.records[name] = [Record(name, cats, *args, **kwargs)]
         
    def get_input(self, name, perl=True, **kwargs):
        out = ""
        if "header" in kwargs:
            header = kwargs["header"]
        else:
            header = self.get_header(perl=perl, **kwargs)
            
            
        ligs_n_subs = self.get_namespace_input(name, perl)
    
        return header + ligs_n_subs
    
    @classmethod
    def get_header(cls, **kwargs):
    
        basis_kw, str_kw, float_kw, int_kw, bool_kw = cls.AARONKeyWords()

        if "perl" in kwargs:
            perl = kwargs["perl"]
        
        header = ""
        for kw in basis_kw:
            if kw in kwargs and kwargs[kw]:
                for val in kwargs[kw]:
                    header += "%s=%s\n" % (kw, val)
        
        for kw in str_kw:
            if kw in kwargs and kwargs[kw]:
                header += "%s=%s\n" % (kw, kwargs[kw])
            
        for kw in float_kw:
            if kw in kwargs and kwargs[kw]:
                header+= "%s=%.2f\n" % (kw, kwargs[kw])
            
        for kw in int_kw:
            if kw in kwargs and kwargs[kw]:
                header += "%s=%i\n" % (kw, kwargs[kw])
        
        for kw in bool_kw:
            if kw in kwargs:
                if kwargs[kw]:
                    header += "%s=true\n" % (kw)
                elif not kwargs[kw] and kwargs[kw] is not None:
                    header += "%s=false\n" % (kw)
        
        return header
    
    def get_namespace_input(self, name, perl):
        rec = self.records[name]
    
        out = "&Ligands\n%s1: None\n" % rec[0].ligPrefix
        if len([record for record in rec if record.component == "ligand"]) + \
           len([record for record in rec if record.ligand is not None]) \
           > 0:

            i = 2
            for record in rec[1:]:
                if record.ligand is None or record.substitution is not None and not record.hidden:
                    continue
                
                out += "%s%i: ligand=%s\n" % (record.ligPrefix, i, record.ligand)
                i += 1
                
            for record in rec[1:]:
                if record.component != "ligand" or record.hidden:
                    continue
                
                if record.ligand is not None:
                    out += "%s%i: ligand=%s " % (record.ligPrefix, i, record.ligand)
                else:
                    out += "%s%i: " % (record.ligPrefix, i)
                                
                for j in range(0, len(record.substitution)):
                    out += "%s=%s " % (",".join(str(p) for p in record.positions[j][int(perl)]), record.substitution[j])
                
                out += "\n"
                
                i += 1
                    
        out += "&\n&Substrates\n"
        
        for i, sub in enumerate([record for record in rec if record.component != "ligand" and record.substitution is not None and not record.hidden]):
            out += "%s%i: " % (sub.subPrefix, i+1)
            for j in range(0, len(sub.substitution)):
                out += "%s=%s " % (",".join(str(p) for p in sub.positions[j][int(perl)]), sub.substitution[j])
            
            out += "\n"
        
        out += "&\n"
        
        return out
        
    @classmethod
    def AARONKeyWords(cls):
        basis_kw = ["low_basis", "basis", "high_basis", "ecp", "high_ecp"]
        str_kw = ["method", "high_solvent", "high_solvent_model", "low_method", "solvent_model", "solvent", \
                    "grid", "gen", "emp_dispersion", "custom", "reaction_type", "template"]
        float_kw = ["temperature", "rmsd_cutoff", "d_cutoff"]
        int_kw = ["charge", "mult", "n_procs", "wall", "short_procs", "short_wall"]
        bool_kw = ["denfit", "input_conformers", "full_conformers"]
        
        return (basis_kw, str_kw, float_kw, int_kw, bool_kw)
    
    def mapLigand(self, name, chim_atoms, ligand_name, replace, ligPrefix=None):
        from ChimAARON import AaronGeometry2ChimeraMolecule
        from chimera import openModels

        mol = chim_atoms[0].molecule
        
        target_tags = []
        for atom in chim_atoms:
            if atom.molecule != mol:
                raise RuntimeError("Select atoms on one molecule only: %s" % " ".join(target_tags))
            target_tags.append(atom.tag)
                
        specified_rec = None
        for rec in self.records[name]:
            if mol in rec.cats:
                specified_rec = rec
    
        if specified_rec is None:
            raise RuntimeError("unable to determine record family of selected molecules")
        
        if ligPrefix is None:
            ligPrefix = specified_rec.ligPrefix
        
        cat_dict = specified_rec.cats
       
        new_cat_dict = {}
        for key in cat_dict:
            new_cat = cat_dict[key].copy()
            new_cat.map_ligand([ligand_name], target_tags)
            for lig in new_cat.components['ligand']:
                if not all([any([tag.startswith('ligand') for tag in atom.tags]) for atom in lig.atoms]):
                    lignum = new_cat.components['ligand'].index(lig)
                    for i, atom in enumerate(lig.atoms):
                        tag = "ligand.%i.%i" % (lignum, i + 1)
                        atom.add_tag(tag)
                        
            nameList = []
            for atom in new_cat.atoms:
                tag = [tag for tag in atom.tags if any([tag.startswith(component) for component in ['ligand.', 'substrate.', 'center.']])][0]
                nameList.append(tag)
                
            new_mol = AaronGeometry2ChimeraMolecule(new_cat, nameList)
            new_cat_dict[new_mol] = new_cat
            openModels.add([new_mol])
            
            if replace:
                openModels.close(key)
            
        self.records[name].append(Record(name, new_cat_dict, ligPrefix=ligPrefix, ligand=ligand_name, hidden=replace))
                
    def subSomething(self, name, chim_atoms, sub_name, replace, ligPrefix=None, subPrefix=None):
        from ChimAARON import AaronGeometry2ChimeraMolecule
        from chimera import openModels
        
        mol = chim_atoms[0].molecule
        
        target_tags = []
        for atom in chim_atoms:
            if atom.molecule != mol:
                raise RuntimeError("Select atoms on one molecule only: %s" % " ".join(target_tags))
            target_tags.append(atom.tag)
                
        specified_rec = None
        for rec in self.records[name]:
            if mol in rec.cats:
                specified_rec = rec
    
        if specified_rec is None:
            raise RuntimeError("unable to determine record family of selected molecules")
        
        if ligPrefix is None:
            ligPrefix = specified_rec.ligPrefix
            
        if subPrefix is None:
            subPrefix = specified_rec.subPrefix
        
        cat_dict = specified_rec.cats
       
        if specified_rec.substitution is None:
            substitution = []
            parent_component = None
            positions = []
        else:
            substitution = [s for s in specified_rec.substitution]
            parent_component = specified_rec.component
            positions = [p for p in specified_rec.positions]
                
        substitution.append(sub_name)
        
        new_positions = [[],[]]
        new_cat_dict = {}
        sub_component = None
        for key in cat_dict:
            new_cat = cat_dict[key].copy()

            for target in target_tags:
                if len(new_positions[1]) < len(target_tags):
                    atom = new_cat.find(target)[0]
                    for chimatom in chim_atoms:
                        if target.startswith('ligand'):
                            new_positions[1].append(mol.atoms.index(chimatom) - sum([len(c.atoms) for c in new_cat.components['substrate']]) - len(new_cat.center) + 1)
                        else:
                            new_positions[1].append(mol.atoms.index(chimatom) + 1)
                            
                if target == "new":
                    raise RuntimeError("selected atom was added from a substitution - AARON cannot substitute this")
                
                new_cat.substitute(sub_name, target)
            
            nameList = []
            for atom in new_cat.atoms:
                tags = [tag for tag in atom.tags if any([tag.startswith(component) for component in ['ligand.', 'substrate.', 'center.']])]
                if len(tags) == 0:
                    tag = "new"
                else:
                    tag = tags[0]
                    
                nameList.append(tag)
                
            new_mol = AaronGeometry2ChimeraMolecule(new_cat, nameList)
            new_cat_dict[new_mol] = new_cat
                
            openModels.add([new_mol])

            if replace:
                openModels.close(key)
                
        for targ in target_tags:
            info = targ.split('.')
            comp_name = info[0]
            if parent_component is not None and comp_name != parent_component:
                raise RuntimeError("Cannot substitute on %s after substituting on %s.\nAn entry will not be made for this substitution." \
                                    % (comp_name, parent_component))
            comp_ndx = int(info[1])
            new_positions[0].extend([sum([len(new_cat.components[comp_name][i].atoms) for i in range(0, comp_ndx)]) + int(info[2])])
        
        positions.append(new_positions)
        
        if comp_name == "ligand":
            ligand = specified_rec.ligand
        else:
            ligand = None
        
        self.records[name].append(Record(name, new_cat_dict, \
                                               ligPrefix=ligPrefix, \
                                               subPrefix=subPrefix, \
                                               substitution=substitution, \
                                               positions=positions, \
                                               component=comp_name, \
                                               ligand=ligand, \
                                               hidden=replace))             
    