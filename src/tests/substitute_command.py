import os.path

from AaronTools.test import prefix, validate
from chimerax.core.commands import run
from SEQCROW.residue_collection import ResidueCollection
from TestManager import TestWithSession


class SubstituteCmdTest(TestWithSession):
    
    benzene = os.path.join(prefix, "test_files", "benzene.xyz")
    chlorobenzene = os.path.join(prefix, "test_files", "benzene_4-Cl.xyz")
    chlorobiphenyl = os.path.join(prefix, "test_files", "benzene_1-Ph_4-Cl.xyz")

    def test_substitute_modify(self):
        ref = ResidueCollection(self.chlorobiphenyl)
        
        run(self.session, "open %s" % self.benzene)
        run(self.session, "substitute #1/a:1@H5 substituent Cl minimize false")
        run(self.session, "substitute #1/a:1@H6 substituent Ph minimize false")
        mdl = self.session.models.list()[0]
        rescol = ResidueCollection(mdl)
        
        self.assertTrue(validate(ref, rescol))
    
    def test_substitute_copy(self):
        ref1 = ResidueCollection(self.chlorobenzene)
        ref2 = ResidueCollection(self.chlorobiphenyl)
        
        run(self.session, "open %s" % self.benzene)
        run(self.session, "substitute #1/a:1@H5 substituent Cl minimize false modify false")
        run(self.session, "substitute #2/a:1@H6 substituent Ph minimize false modify false")
        mdl1 = self.session.models.list()[1]
        rescol1 = ResidueCollection(mdl1)
        mdl2 = self.session.models.list()[2]
        rescol2 = ResidueCollection(mdl2)
        
        self.assertTrue(validate(ref1, rescol1))
        self.assertTrue(validate(ref2, rescol2))
    
