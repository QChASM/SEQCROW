import os.path

from AaronTools.test import prefix
from chimerax.core.commands import run
from TestManager import TestWithSession


class ConeAngleToolTest(TestWithSession):
    
    cat = os.path.join(prefix, "test_files", "catalysts", "tm_single-lig.xyz")

    def test_calc_cone_angle(self):
        run(self.session, "open %s" % self.cat)
        run(self.session, "select P")
        run(self.session, "select connected")
        
        cone_tool = self.open_tool("Cone Angle")
        self.assertTrue(bool(cone_tool))

        cone_tool.cone_option.setCurrentIndex(1)
        cone_tool.radii_option.setCurrentIndex(1)
        cone_tool.set_ligand_button.click()
        
        run(self.session, "select Cu")
        
        cone_tool.calc_cone_button.click()
        
        csv = cone_tool.get_csv()
        delim_name = cone_tool.settings.delimiter
        if delim_name == "comma":
            delim = ","
        elif delim_name == "tab":
            delim = "\t"
        elif delim_name == "semicolon":
            delim = ";"
        elif delim_name == "space":
            delim = " "

        ref = delim.join(["model", "center_atom", "cone_angle\n"]) + delim.join(["tm_single-lig", "/a:1@Cu1", "234.14"])

        csv_lines = csv.splitlines()
        ref_lines = ref.splitlines()
        
        self.assertEqual(len(csv_lines), len(ref_lines))

        for ref, test in zip(ref_lines, csv_lines):
            if ref != test:
                self.session.logger.warning("%s != %s" % (ref, test))
            self.assertEqual(ref, test)

        cone_tool.delete()
