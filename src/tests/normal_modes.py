import os.path

from AaronTools.test import prefix
from chimerax.core.commands import run
from TestManager import TestWithSession


class NormalModesToolTest(TestWithSession):
    
    formaldehyde = os.path.join(prefix, "test_files", "freq.log")

    def test_show_vec(self):
        run(self.session, "open %s" % self.formaldehyde)
        
        normal_mode_tool = self.open_tool("Visualize Normal Modes")
        self.assertTrue(bool(normal_mode_tool))
        
        normal_mode_tool.show_vec_button.click()
        self.assertTrue(len(self.session.models.list()) == 2)
        
        normal_mode_tool.close_vec_button.click()
        self.assertTrue(len(self.session.models.list()) == 1)

        normal_mode_tool.delete()

    def test_show_anim(self):
        run(self.session, "open %s" % self.formaldehyde)
        
        normal_mode_tool = self.open_tool("Visualize Normal Modes")
        self.assertTrue(bool(normal_mode_tool))
        
        normal_mode_tool.show_anim_button.click()
        # no new models should be open
        self.assertTrue(len(self.session.models.list()) == 1)

        mdl = self.session.models.list()[0]
        # num_coordsets should be the same as the requested number of frames
        self.assertTrue(mdl.num_coordsets == normal_mode_tool.anim_duration.value())
        
        normal_mode_tool.delete()
