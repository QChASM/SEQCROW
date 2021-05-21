import os.path

import numpy as np
from AaronTools.test import prefix
from chimerax.core.commands import run
from TestManager import TestWithSession


class LookDownCmdTest(TestWithSession):
    benzene = os.path.join(prefix, "test_files", "benzene.xyz")

    def test_lookDown(self):
        ref = np.array([
            [ 0.30800362, -1.95765456,  1.66545748],
            [ 0.6681431 , -0.80451809,  2.36334551],
            [ 1.02715012,  0.34904777,  1.66647893],
            [ 1.02726614,  0.34945534,  0.27105172],
            [ 0.667658  , -0.803584  , -0.4266011 ],
            [ 0.30761687, -1.95712286,  0.27062938],
            [ 0.66760504, -0.80502953,  3.46299949],
            [ 1.31042307,  1.25818933,  2.21649218],
            [ 0.667658  , -0.803584  , -1.526362  ],
            [ 0.02396892, -2.86594109, -0.27957353],
            [ 1.30793153,  1.25109415, -0.27335053],
            [ 0.02703742, -2.85895643,  2.21026364]
        ])
        
        run(self.session, "open %s" % self.benzene)
        run(self.session, "lookDown @C5 atom2 @H3")
        
        mdl = self.session.models.list()[0]
        test = mdl.active_coordset.xyzs
        
        self.assertEqual(test.shape, ref.shape)
        
        for r, t in zip(ref, test):
            self.assertTrue(np.isclose(np.linalg.norm(r - t), 0))
