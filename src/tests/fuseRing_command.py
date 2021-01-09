import os.path
import unittest

from AaronTools.test import prefix, validate
from chimerax.core.commands import run
from SEQCROW.residue_collection import ResidueCollection
from TestManager import TestWithSession


class FuseRingCmdTest(TestWithSession):
    
    benzene = os.path.join(prefix, "test_files", "benzene.xyz")
    naphthalene = os.path.join(prefix, "ref_files", "naphthalene.xyz")
    tetrahydronaphthalene = os.path.join(prefix, "ref_files", "tetrahydronaphthalene.xyz")

    def test_fuseRing_modify(self):
        ref = ResidueCollection(self.naphthalene)
        
        run(self.session, "open %s" % self.benzene)
        run(self.session, "fuseRing #1/a:1@H1 #1/a:1@H2 ring benzene")
        mdl = self.session.models.list()[0]
        rescol = ResidueCollection(mdl)
        
        self.assertTrue(validate(ref, rescol, thresh="loose"))
    
    def test_fuseRing_copy(self):
        ref1 = ResidueCollection(self.naphthalene)
        ref2 = ResidueCollection(self.tetrahydronaphthalene)
        
        run(self.session, "open %s" % self.benzene)
        run(self.session, "fuseRing #1/a:1@H1 #1/a:1@H2 ring benzene modify false")
        run(self.session, "fuseRing #1/a:1@H1 #1/a:1@H2 ring cyclohexane modify false")
        mdl1 = self.session.models.list()[1]
        rescol1 = ResidueCollection(mdl1)
        mdl2 = self.session.models.list()[2]
        rescol2 = ResidueCollection(mdl2)
        
        self.assertTrue(validate(ref1, rescol1, thresh="loose"))
        self.assertTrue(validate(ref2, rescol2, thresh="loose"))
    
