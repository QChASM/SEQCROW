import os.path

from AaronTools.test import prefix, validate
from AaronTools.theory import BasisSet, Basis
from chimerax.core.commands import run
from PyQt5.QtCore import Qt
from TestManager import TestWithSession


class QMInputBuilderToolTest(TestWithSession):
    
    benzene = os.path.join(prefix, "test_files", "benzene.xyz")
    met_cat = os.path.join(prefix, "test_files", "catalysts", "tm_multi-lig.xyz")

    def test_gaussian_opt(self):
        run(self.session, "open %s" % self.benzene)
        
        qm_input_tool = self.open_tool("Build QM Input")
        self.assertTrue(bool(qm_input_tool))
        
        ndx = qm_input_tool.file_type.findText("Gaussian", Qt.MatchExactly)
        qm_input_tool.file_type.setCurrentIndex(ndx)

        qm_input_tool.job_widget.do_geom_opt.setCheckState(Qt.Checked)
        qm_input_tool.job_widget.ts_opt.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.do_freq.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.charge.setValue(0)
        qm_input_tool.job_widget.multiplicity.setValue(1)
        qm_input_tool.job_widget.nprocs.setValue(0)
        qm_input_tool.job_widget.mem.setValue(0)

        ndx = qm_input_tool.job_widget.solvent_option.findText("None", Qt.MatchExactly)
        qm_input_tool.job_widget.solvent_option.setCurrentIndex(ndx)
        
        qm_input_tool.method_widget.setMethod("wB97X-D")
        qm_input_tool.method_widget.setGrid("SuperFineGrid")
        qm_input_tool.method_widget.setDispersion("None")
        
        basis = BasisSet("def2-SVP")
        qm_input_tool.basis_widget.setBasis(basis)
        
        qm_input_tool.other_keywords_widget.setKeywords({})
        
        contents, warnings = qm_input_tool.get_file_contents()
        qm_input_tool.delete()
        if warnings:
            # there were warnings - I don't expect any
            self.assertTrue(False)
        
        ref_file = """#n wB97XD/def2SVP opt Integral=(grid=SuperFineGrid) 

benzene_1-NO2_4-Cl.xyz 12,11=>H

0 1
C     -1.97696    -2.32718     0.00126
C     -2.36814    -1.29554     0.85518
C     -1.67136    -0.08735     0.85440
C     -0.58210     0.08919     0.00026
C     -0.19077    -0.94241    -0.85309
C     -0.88848    -2.15056    -0.85289
H     -3.22679    -1.43483     1.52790
H     -1.98002     0.72606     1.52699
H      0.66766    -0.80358    -1.52636
H     -0.57992    -2.96360    -1.52585
H     -0.03766     1.03348    -0.00013
H     -2.52191    -3.27117     0.00170



"""
        
        content_lines = contents.splitlines()
        ref_lines = ref_file.splitlines()
        
        self.assertEqual(len(content_lines), len(ref_lines))
        
        for ref, test in zip(ref_lines, content_lines):
            self.assertEqual(ref, test)

    def test_gaussian_tm_sp(self):
        run(self.session, "open %s" % self.met_cat)

        qm_input_tool = self.open_tool("Build QM Input")
        self.assertTrue(bool(qm_input_tool))
        
        ndx = qm_input_tool.file_type.findText("Gaussian", Qt.MatchExactly)
        qm_input_tool.file_type.setCurrentIndex(ndx)

        qm_input_tool.job_widget.do_geom_opt.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.do_freq.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.charge.setValue(0)
        qm_input_tool.job_widget.multiplicity.setValue(1)
        qm_input_tool.job_widget.nprocs.setValue(0)
        qm_input_tool.job_widget.mem.setValue(0)

        ndx = qm_input_tool.job_widget.solvent_option.findText("None", Qt.MatchExactly)
        qm_input_tool.job_widget.solvent_option.setCurrentIndex(ndx)
        
        qm_input_tool.method_widget.setMethod("B3LYP")
        qm_input_tool.method_widget.setGrid("SuperFineGrid")
        qm_input_tool.method_widget.setDispersion("None")
        
        basis = BasisSet(
            basis=[
                Basis(
                    "def2-TZVP",
                    elements=["H", "C", "N", "O", "P"],
                ),
                Basis(
                    "SDD",
                    elements=["Ru"]
                )
            ],
            ecp="Ru SDD"
        )
        qm_input_tool.basis_widget.setBasis(basis)
        
        qm_input_tool.other_keywords_widget.setKeywords({})
        
        contents, warnings = qm_input_tool.get_file_contents()
        qm_input_tool.delete()
        if warnings:
            # there were warnings - I don't expect any
            self.assertTrue(False)
        
        ref_file = """#n B3LYP/genecp Integral=(grid=SuperFineGrid) 

F:22-8;8-3;3-4

0 1
H     -1.32054    -0.75890    -4.97019
C     -0.83710    -0.67504    -3.98693
C     -1.94818    -0.44720    -2.97055
O     -2.60335     0.62340    -3.03491
H     -2.15763    -1.15349    -2.24784
H     -0.27898    -1.59632    -3.81264
H     -0.14406     0.16910    -4.01642
Ru    -0.62191     0.26814     0.06452
H     -0.87528    -0.29689    -1.62782
H     -0.64154     0.77071     1.63835
N     -2.22027     1.67036    -0.35156
N     -2.41708    -0.87753     0.60051
C     -3.38272     1.38551     0.51399
H     -1.96741     2.65271    -0.26188
H     -2.47077     1.51040    -1.33734
C     -3.67190    -0.11908     0.39143
H     -2.48854    -1.76419     0.10163
H     -2.32916    -1.12467     1.58359
H     -4.23094     1.95099     0.18896
H     -3.17970     1.65524     1.52934
H     -4.05898    -0.33036    -0.58347
H     -4.39170    -0.40689     1.12895
P      1.07205     1.71869    -0.34745
P      0.81151    -1.37184     0.70896
C      0.55526     3.14500    -1.41523
C      1.97994     2.59379     1.00651
C      2.49260     0.93221    -1.24347
C     -0.11544    -2.48291     1.86409
C      1.60408    -2.58882    -0.43067
C      2.34100    -0.80590     1.59984
C      0.82744     4.48948    -1.13825
C     -0.25736     2.85102    -2.51851
C      3.14155     3.31828     0.70808
C      1.54835     2.54133     2.33290
C      3.33578     0.04627    -0.58629
C      2.60045     1.09163    -2.65079
C     -0.54933    -3.74618     1.44682
C     -0.64383    -1.96605     3.05866
C      2.33984    -3.67519     0.06065
C      1.54474    -2.38323    -1.80618
C      3.33694    -0.12514     0.90812
C      2.46312    -0.97926     3.00323
C      0.32389     5.50137    -1.95561
H      1.42639     4.76771    -0.27860
C     -0.75232     3.85682    -3.34145
H     -0.53079     1.82144    -2.71815
C      3.85126     3.97307     1.70883
H      3.50559     3.36279    -0.31548
C      2.26924     3.17905     3.34133
H      0.65677     1.97347     2.57940
C      4.28462    -0.72389    -1.34298
C      3.51379     0.38421    -3.38194
H      1.94937     1.79380    -3.16019
C     -1.46313    -4.47789     2.20565
H     -0.19139    -4.16842     0.51384
C     -1.54169    -2.70268     3.82536
H     -0.38472    -0.96029     3.37605
C      2.97321    -4.55113    -0.81434
H      2.41820    -3.84020     1.13279
C      2.18627    -3.25197    -2.68724
H      1.01491    -1.51377    -2.18064
C      4.45682     0.42048     1.62607
C      3.50924    -0.44591     3.70435
H      1.71903    -1.55347     3.54106
C     -0.46011     5.19061    -3.06285
H      0.54641     6.53809    -1.71862
H     -1.37864     3.59473    -4.18971
C      3.42240     3.89544     3.03272
H      4.75240     4.52500     1.45765
H      1.92962     3.10901     4.37111
C      4.37499    -0.54687    -2.75091
C      5.13058    -1.69490    -0.73828
H      3.58576     0.52763    -4.45722
C     -1.95775    -3.96357     3.39945
H     -1.78959    -5.45264     1.85394
H     -1.93165    -2.28048     4.74724
C      2.89822    -4.34014    -2.19222
H      3.53800    -5.39223    -0.42206
H      2.14147    -3.06592    -3.75679
C      4.52546     0.28009     3.03897
C      5.51015     1.12556     0.97778
H      3.57546    -0.58565     4.78041
H     -0.85051     5.98165    -3.69692
H      3.98664     4.38925     3.81887
C      5.30218    -1.31658    -3.50131
C      6.01244    -2.43204    -1.48800
H      5.06355    -1.86999     0.32991
H     -2.67024    -4.53306     3.98918
H      3.40448    -5.01737    -2.87435
C      5.61174     0.85060     3.75500
C      6.55752     1.65159     1.69023
H      5.47918     1.26388    -0.09684
C      6.10652    -2.24058    -2.88574
H      5.35443    -1.16301    -4.57638
H      6.63929    -3.17577    -1.00421
C      6.61007     1.52076     3.09726
H      5.63680     0.73814     4.83603
H      7.34699     2.18698     1.17049
H      6.81024    -2.83022    -3.46624
H      7.43996     1.95142     3.65012

C H N O P 0
def2TZVP
****
Ru 0
SDD
****

Ru 0
SDD


"""
        
        content_lines = contents.splitlines()
        ref_lines = ref_file.splitlines()
        
        self.assertEqual(len(content_lines), len(ref_lines))
        
        for ref, test in zip(ref_lines, content_lines):
            self.assertEqual(ref, test)

    def test_orca_opt(self):
        run(self.session, "open %s" % self.benzene)

        qm_input_tool = self.open_tool("Build QM Input")
        self.assertTrue(bool(qm_input_tool))
        
        ndx = qm_input_tool.file_type.findText("ORCA", Qt.MatchExactly)
        qm_input_tool.file_type.setCurrentIndex(ndx)

        qm_input_tool.job_widget.do_geom_opt.setCheckState(Qt.Checked)
        qm_input_tool.job_widget.ts_opt.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.do_freq.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.charge.setValue(0)
        qm_input_tool.job_widget.multiplicity.setValue(1)
        qm_input_tool.job_widget.nprocs.setValue(0)
        qm_input_tool.job_widget.mem.setValue(0)

        ndx = qm_input_tool.job_widget.solvent_option.findText("None", Qt.MatchExactly)
        qm_input_tool.job_widget.solvent_option.setCurrentIndex(ndx)
        
        qm_input_tool.method_widget.setMethod("M06-2X")
        qm_input_tool.method_widget.setGrid("Grid7")
        qm_input_tool.method_widget.setDispersion("Zero-damped Grimme D3")
        
        basis = BasisSet("def2-TZVP")
        qm_input_tool.basis_widget.setBasis(basis)
        
        qm_input_tool.other_keywords_widget.setKeywords({})
        
        contents, warnings = qm_input_tool.get_file_contents()
        qm_input_tool.delete()
        if warnings:
            # there were warnings - I don't expect any
            self.assertTrue(False)
        
        ref_file = """#benzene_1-NO2_4-Cl.xyz 12,11=>H
! M062X D3 Grid7 FinalGrid7 def2-TZVP Opt

*xyz 0 1
C    -1.976956  -2.327177   0.001258
C    -2.368139  -1.295544   0.855179
C    -1.671361  -0.087354   0.854401
C    -0.582097   0.089190   0.000262
C    -0.190773  -0.942409  -0.853088
C    -0.888480  -2.150555  -0.852891
H    -3.226790  -1.434829   1.527903
H    -1.980024   0.726060   1.526994
H     0.667658  -0.803584  -1.526362
H    -0.579922  -2.963602  -1.525852
H    -0.037665   1.033485  -0.000129
H    -2.521911  -3.271171   0.001704
*
"""
        
        content_lines = contents.splitlines()
        ref_lines = ref_file.splitlines()
        
        self.assertEqual(len(content_lines), len(ref_lines))
        
        for ref, test in zip(ref_lines, content_lines):
            self.assertEqual(ref, test)

    def test_orca_numfreq(self):
        run(self.session, "open %s" % self.benzene)

        qm_input_tool = self.open_tool("Build QM Input")
        self.assertTrue(bool(qm_input_tool))
        
        ndx = qm_input_tool.file_type.findText("ORCA", Qt.MatchExactly)
        qm_input_tool.file_type.setCurrentIndex(ndx)

        qm_input_tool.job_widget.do_geom_opt.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.do_freq.setCheckState(Qt.Checked)
        qm_input_tool.job_widget.raman.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.num_freq.setCheckState(Qt.Checked)
        qm_input_tool.job_widget.temp.setValue(298.15)
        qm_input_tool.job_widget.charge.setValue(0)
        qm_input_tool.job_widget.multiplicity.setValue(1)
        qm_input_tool.job_widget.nprocs.setValue(0)
        qm_input_tool.job_widget.mem.setValue(0)

        ndx = qm_input_tool.job_widget.solvent_option.findText("None", Qt.MatchExactly)
        qm_input_tool.job_widget.solvent_option.setCurrentIndex(ndx)
        
        qm_input_tool.method_widget.setMethod("M06-2X")
        qm_input_tool.method_widget.setGrid("Grid7")
        qm_input_tool.method_widget.setDispersion("None")
        
        basis = BasisSet("def2-SVP")
        qm_input_tool.basis_widget.setBasis(basis)
        
        qm_input_tool.other_keywords_widget.setKeywords({})
        
        contents, warnings = qm_input_tool.get_file_contents()
        qm_input_tool.delete()
        if warnings:
            # there were warnings - I don't expect any
            self.assertTrue(False)
        
        ref_file = """#benzene_1-NO2_4-Cl.xyz 12,11=>H
! M062X Grid7 FinalGrid7 def2-SVP NumFreq
%freq
    Temp    298.15
end

*xyz 0 1
C    -1.976956  -2.327177   0.001258
C    -2.368139  -1.295544   0.855179
C    -1.671361  -0.087354   0.854401
C    -0.582097   0.089190   0.000262
C    -0.190773  -0.942409  -0.853088
C    -0.888480  -2.150555  -0.852891
H    -3.226790  -1.434829   1.527903
H    -1.980024   0.726060   1.526994
H     0.667658  -0.803584  -1.526362
H    -0.579922  -2.963602  -1.525852
H    -0.037665   1.033485  -0.000129
H    -2.521911  -3.271171   0.001704
*
"""
        
        content_lines = contents.splitlines()
        ref_lines = ref_file.splitlines()
        
        self.assertEqual(len(content_lines), len(ref_lines))
        
        for ref, test in zip(ref_lines, content_lines):
            self.assertEqual(ref, test)

    def test_psi4_opt(self):
        run(self.session, "open %s" % self.benzene)

        qm_input_tool = self.open_tool("Build QM Input")
        self.assertTrue(bool(qm_input_tool))
        
        ndx = qm_input_tool.file_type.findText("Psi4", Qt.MatchExactly)
        qm_input_tool.file_type.setCurrentIndex(ndx)

        qm_input_tool.job_widget.do_geom_opt.setCheckState(Qt.Checked)
        qm_input_tool.job_widget.ts_opt.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.do_freq.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.charge.setValue(0)
        qm_input_tool.job_widget.multiplicity.setValue(1)
        qm_input_tool.job_widget.nprocs.setValue(0)
        qm_input_tool.job_widget.mem.setValue(0)
        
        qm_input_tool.method_widget.setMethod("HF")
        qm_input_tool.method_widget.setGrid("Default")
        qm_input_tool.method_widget.setDispersion("None")
        
        basis = BasisSet("def2-SVP")
        qm_input_tool.basis_widget.setBasis(basis)
        
        qm_input_tool.other_keywords_widget.setKeywords({})
        
        contents, warnings = qm_input_tool.get_file_contents()
        qm_input_tool.delete()
        if warnings:
            # there were warnings - I don't expect any
            self.assertTrue(False)
        
        ref_file = """#benzene_1-NO2_4-Cl.xyz 12,11=>H
basis {
    assign    def2-SVP
}

molecule {
     0 1
     C       -1.97696       -2.32718        0.00126
     C       -2.36814       -1.29554        0.85518
     C       -1.67136       -0.08735        0.85440
     C       -0.58210        0.08919        0.00026
     C       -0.19077       -0.94241       -0.85309
     C       -0.88848       -2.15056       -0.85289
     H       -3.22679       -1.43483        1.52790
     H       -1.98002        0.72606        1.52699
     H        0.66766       -0.80358       -1.52636
     H       -0.57992       -2.96360       -1.52585
     H       -0.03766        1.03348       -0.00013
     H       -2.52191       -3.27117        0.00170
}

nrg = optimize('HF')
"""

        content_lines = contents.splitlines()
        ref_lines = ref_file.splitlines()
        
        self.assertEqual(len(content_lines), len(ref_lines))
        
        for ref, test in zip(ref_lines, content_lines):
            self.assertEqual(ref, test)

    def test_psi4_sp(self):
        run(self.session, "open %s" % self.benzene)

        qm_input_tool = self.open_tool("Build QM Input")
        self.assertTrue(bool(qm_input_tool))
        
        ndx = qm_input_tool.file_type.findText("Psi4", Qt.MatchExactly)
        qm_input_tool.file_type.setCurrentIndex(ndx)

        qm_input_tool.job_widget.do_geom_opt.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.do_freq.setCheckState(Qt.Unchecked)
        qm_input_tool.job_widget.charge.setValue(0)
        qm_input_tool.job_widget.multiplicity.setValue(1)
        qm_input_tool.job_widget.nprocs.setValue(0)
        qm_input_tool.job_widget.mem.setValue(0)
        
        qm_input_tool.method_widget.setMethod("CCSD(T)")
        qm_input_tool.method_widget.setGrid("Default")
        qm_input_tool.method_widget.setDispersion("None")
        
        basis = BasisSet("aug-cc-pVDZ")
        qm_input_tool.basis_widget.setBasis(basis)
        
        qm_input_tool.other_keywords_widget.setKeywords({"job":{"energy":[]}})
        
        contents, warnings = qm_input_tool.get_file_contents()
        qm_input_tool.delete()
        if warnings:
            # there were warnings - I don't expect any
            self.assertTrue(False)
        
        ref_file = """#benzene_1-NO2_4-Cl.xyz 12,11=>H
basis {
    assign    aug-cc-pVDZ
}

molecule {
     0 1
     C       -1.97696       -2.32718        0.00126
     C       -2.36814       -1.29554        0.85518
     C       -1.67136       -0.08735        0.85440
     C       -0.58210        0.08919        0.00026
     C       -0.19077       -0.94241       -0.85309
     C       -0.88848       -2.15056       -0.85289
     H       -3.22679       -1.43483        1.52790
     H       -1.98002        0.72606        1.52699
     H        0.66766       -0.80358       -1.52636
     H       -0.57992       -2.96360       -1.52585
     H       -0.03766        1.03348       -0.00013
     H       -2.52191       -3.27117        0.00170
}

nrg = energy('CCSD(T)')
"""

        content_lines = contents.splitlines()
        ref_lines = ref_file.splitlines()
        
        self.assertEqual(len(content_lines), len(ref_lines))
        
        for ref, test in zip(ref_lines, content_lines):
            self.assertEqual(ref, test)