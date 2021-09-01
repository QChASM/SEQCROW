import os.path

from AaronTools.test import prefix
from chimerax.core.commands import run
from TestManager import TestWithSession
from Qt.QtCore import Qt


class BuriedVolumeToolTest(TestWithSession):
    
    cat = os.path.join(prefix, "test_files", "catalysts", "tm_single-lig.xyz")

    def test_calc_vbur(self):
        run(self.session, "open %s" % self.cat)
        run(self.session, "select P")
        run(self.session, "select connected")
        
        vbur_tool = self.open_tool("Buried Volume")
        self.assertTrue(bool(vbur_tool))

        vbur_tool.radii_option.setCurrentIndex(1)
        vbur_tool.scale.setValue(1.17)
        vbur_tool.set_ligand_atoms.click()
        vbur_tool.radius.setValue(3.5)
        vbur_tool.method.setCurrentIndex(0)
        vbur_tool.radial_points.setCurrentIndex(1)
        vbur_tool.angular_points.setCurrentIndex(5)
        vbur_tool.use_centroid.setCheckState(Qt.Unchecked)
        vbur_tool.steric_map.setCheckState(Qt.Unchecked)
        vbur_tool.display_cutout.setCurrentIndex(0)
        vbur_tool.report_component.setCurrentIndex(0)
        
        run(self.session, "select Cu")
        
        vbur_tool.calc_vbur_button.click()
        
        csv = vbur_tool.get_csv()
        delim_name = vbur_tool.settings.delimiter
        if delim_name == "comma":
            delim = ","
        elif delim_name == "tab":
            delim = "\t"
        elif delim_name == "semicolon":
            delim = ";"
        elif delim_name == "space":
            delim = " "
        
        ref = delim.join(["model", "center", "%Vbur\n"]) + delim.join(["tm_single-lig.xyz", "/a:1@Cu1", "56.2"])

        csv_lines = csv.splitlines()
        ref_lines = ref.splitlines()
        
        self.assertEqual(len(csv_lines), len(ref_lines))

        for ref, test in zip(ref_lines, csv_lines):
            if ref != test:
                self.session.logger.warning("%s != %s" % (ref, test))
            self.assertEqual(ref, test)

        vbur_tool.delete()
