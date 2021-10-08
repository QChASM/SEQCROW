import os.path

from AaronTools.test import prefix
from chimerax.core.commands import run
from TestManager import TestWithSession


class SubstituentSterimolToolTest(TestWithSession):
    
    mol = os.path.join(prefix, "test_files", "benzene.xyz")

    def test_sterimol(self):
        run(self.session, "open %s" % self.mol)
        run(self.session, "select ~@H1")
        
        sterimol_tool = self.open_tool("Substituent Sterimol")
        self.assertTrue(bool(sterimol_tool))

        sterimol_tool.L_style.setCurrentIndex(0)
        sterimol_tool.radii_option.setCurrentIndex(1)

        sterimol_tool.calc_sterimol_button.click()
        
        csv = sterimol_tool.get_csv()
        delim_name = sterimol_tool.settings.delimiter
        if delim_name == "comma":
            delim = ","
        elif delim_name == "tab":
            delim = "\t"
        elif delim_name == "semicolon":
            delim = ";"
        elif delim_name == "space":
            delim = " "

        ref = delim.join(
            ["substituent_atom", "bonded_atom", "B1", "B2", "B3", "B4", "B5", "L\n"]
        ) + delim.join(
            ["benzene", "/a:1@C2", "1.70", "1.70", "3.26", "3.26", "3.26", "6.46\n"]
        )

        csv_lines = csv.splitlines()
        ref_lines = ref.splitlines()
        
        self.assertEqual(len(csv_lines), len(ref_lines))

        for ref, test in zip(ref_lines, csv_lines):
            if ref != test:
                self.session.logger.warning("%s != %s" % (ref, test))
            self.assertEqual(ref, test)

        sterimol_tool.delete()
