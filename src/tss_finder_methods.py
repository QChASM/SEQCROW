# methods for the TSS finder tool

from AaronTools.utils.utils import combine_dicts

from chimerax.ui.options import FloatOption, Option, IntOption

from Qt.QtWidgets import QComboBox

from SEQCROW.jobs import (
    LocalClusterJob,
    ORCANEBJob,
    GaussianSTQNJob,
    QChemFSMJob,
    ParallelRavenJob,
    SerialRavenJob,
)


class EnumOption(Option):
    # this uses a combobox instead of a pushbutton with a menu
    values = tuple()

    @property
    def value(self):
        return self.get_value()
    
    @value.setter
    def value(self, val):
        return self.set_value(val)
    
    def get_value(self):
        return self.widget.currentText()
    
    def set_value(self, value):
        ndx = self.widget.findText(value)
        self.widget.setCurrentIndex(ndx)
    
    def _make_widget(self, *, values=None):
        self.widget = QComboBox()
        if values:
            self.values = values
            self.widget.addItems(values)
        return self.widget
    
    def set_multiple(self):
        raise NotImplementedError


class TSSFinder:
    # list of software packages that this can work with
    available_for = []
    
    restart_filter = None
    
    get_file_contents = None
    
    options = dict()
    
    @staticmethod
    def fixup_theory(theory, restart_file=None):
        """
        modify the input theory to run the necessary job type
        if this is a dictionary, programs are keys
        and the values are callable
        otherwise, this is callable and works for all programs
        
        restart_file - path to file that can be used to restart
            the job
        """
        pass


def fixup_gaussian_stqn_theory(theory, restart_file=None):
    theory.job_type = "opt"
    theory.kwargs = combine_dicts(
        {"route": {"opt": ["QST2"]}},
        theory.kwargs,
    )
    return theory

def get_gaussian_stqn_file_contents(reactant, product, theory):
    theory.geometry = reactant
    header, header_warnings = theory.make_header(
        style="gaussian", return_warnings=True
    )
    molecule, mol_warnings = theory.make_molecule(
        style="gaussian", return_warnings=True
    )
    footer, footer_warnings = theory.make_footer(
        style="gaussian", return_warnings=True
    )
    contents = header + molecule + footer
    contents = contents.rstrip()
    contents += "\n\nproduct\n\n%i %i\n" % (
        theory.charge, theory.multiplicity
    )
    theory.geometry = product
    molecule = theory.make_molecule(
        style="gaussian", return_warnings=False
    )
    footer, footer_warnings = theory.make_footer(
        style="gaussian", return_warnings=True
    )
    contents += molecule
    contents += footer
    warnings = header_warnings + mol_warnings + footer_warnings
    return contents, warnings
 
def fixup_orca_neb_theory(
    theory,
    restart_file=None,
    kind="standard",
    images=6,
    optimization_algorithm="BFGS",
):
    theory.job_type = None
    if kind == "standard":
        neb = "NEB"
    elif kind == "climbing image":
        neb = "NEB-CI"
    elif kind == "optimized TSS":
        neb = "NEB-TS"
    elif kind == "standard zoomed":
        neb = "Zoom-NEB"
    elif kind == "climbing image zoomed":
        neb = "Zoom-NEB-CI"
    elif kind == "optimized TSS zoomed":
        neb = "Zoom-NEB-TS"
    
    if optimization_algorithm == "L-BFGS":
        optimization_algorithm = "LBFGS"
    
    theory.kwargs = combine_dicts(
        {
            "simple": [neb],
            "blocks": {
                "neb": [
                    "product \"product.xyz\"",
                    "NImages %i" % images,
                    "Opt_Method %s" % optimization_algorithm,
                ],
            },
        },
        theory.kwargs,
    )
    
    if restart_file:
        theory.kwargs = combine_dicts(
            {
                "blocks": {
                    "neb": [
                        "Restart_ALLXYZFile \"%s\"" % restart_file,
                    ],
                },
            },
            theory.kwargs,
        )
    
    
    return theory

def fixup_qchem_fsm_theory(
    theory,
    restart_file=None,
    optimization_steps=2,
    interpolation="LST",
    optimization_algorithm="BFGS",
    nodes=10,
):
    theory.job_type = None
    if interpolation == "LST":
        interpolation = "2"
    else:
        interpolation = "1"
    
    if optimization_algorithm == "BFGS":
        optimization_algorithm = "2"
    else:
        optimization_algorithm = "1"
    
    theory.kwargs = combine_dicts(
        {
            "rem": {
                "JOBTYPE": "FSM",
                "FSM_NMODE": str(nodes),
                "FSM_NGRAD": str(optimization_steps),
                "FSM_MODE": interpolation,
                "FSM_OPT_MODE": optimization_algorithm,
            }
        },
        theory.kwargs,
    )
    return theory

def get_qchem_fes_file_contents(reactant, product, theory):
    fmt = "{:<3s} {: 9.5f} {: 9.5f} {: 9.5f}\n"
    header, header_warnings = theory.make_header(
        style="qchem", return_warnings=True,
    )
    mol = "$molecule\n"
    for atom in reactant.atoms:
        mol += fmt.format(atom.element, *atom.coords)
    mol += "****\n"
    for atom in product.atoms:
        mol += fmt.format(atom.element, *atom.coords)
    mol += "$end\n"


    out = header + mol
    warnings = header_warnings
    
    return out, warnings


class STQN(TSSFinder):
    """
    synchronous transit-guided quasi-Newton method
    available in Gaussian with opt=QST2
    we don't take guesses (yet?), so no opt=QST3
    """
    available_for = ["Gaussian"]
    
    special_contents = True
    
    local_job_cls = {
        "Gaussian": GaussianSTQNJob,
    }
    
    cluster_job_cls = {
        "Gaussian": LocalClusterJob,
    }
    
    fixup_theory = {
        "Gaussian": fixup_gaussian_stqn_theory
    }
    
    get_file_contents = {
        "Gaussian": get_gaussian_stqn_file_contents,
    }


class NEB(TSSFinder):
    available_for = ["ORCA"]
    
    options = {
        "images": (
            IntOption, {
                "min": 5,
                "max": 25,
            }
        ),
        "kind": (
            EnumOption, {
                "values": [
                    "standard",
                    "climbing image",
                    "optimized TSS",
                ],
            }
        ),
        "optimization_algorithm": (
            EnumOption, {
                "values": [
                    "L-BFGS",
                    "VPO",
                ],
            }
        ),
    }
    
    local_job_cls = {
        "ORCA": ORCANEBJob,
    }
    
    cluster_job_cls = {
        "ORCA": LocalClusterJob,
    }
    
    fixup_theory = {
        "ORCA": fixup_orca_neb_theory
    }

    restart_filter = "XYZ pathway files (*.xyz)"


class FSM(TSSFinder):
    available_for = ["Q-Chem"]
        
    options = {
        "nodes": (
            IntOption, {
                "min": 10,
                "max": 20,
            }
        ),
        "optimization_steps": (
            IntOption, {
                "min": 2,
                "max": 18,
            }
        ),
        "interpolation": (
            EnumOption, {
                "values": [
                    "LST",
                    "Cartesian",
                ],
            }
        ),
        "optimization_algorithm": (
            EnumOption, {
                "values": [
                    "BFGS",
                    "conjugate gradients",
                ],
            }
        ),
    }
    
    local_job_cls = {
    # haven't gotten Q-Chem jobs to work - some issue with
    # the environment variables
    #     "Q-Chem": QChemFSMJob,
    }
    
    cluster_job_cls = {
        "Q-Chem": LocalClusterJob,
    }
    
    fixup_theory = {
        "Q-Chem": fixup_qchem_fsm_theory
    }
    
    get_file_contents = {
        "Q-Chem": get_qchem_fes_file_contents,
    }


class GPRGSM(TSSFinder):
    available_for = ["Gaussian", "ORCA", "Psi4", "Q-Chem"]
    
    options = {
        "nodes": (
            IntOption, {
                "min": 5,
                "max": 25,
            }
        ),
        "kernel": (
            EnumOption, {
                "values": [
                    "RBF",
                ]
            }
        ),
        "similarity_falloff": (
            FloatOption, {
                "min": 0.1,
                "max": 10.,
                "step": 0.25,
                "default": 2,
            }
        ),
        "uncertainty_cutoff": (
            FloatOption, {
                "min": 0.0,
                "max": 0.5,
                "step": 0.05,
                "decimals": 3,
                "default": 0.1,
            }
        ),
    }
    
    local_job_cls = {
        "Gaussian": SerialRavenJob,
        "ORCA": SerialRavenJob,
        "Psi4": SerialRavenJob,
        "Q-Chem": SerialRavenJob,
    }

    cluster_job_cls = {
        "Gaussian": ParallelRavenJob,
        "ORCA": ParallelRavenJob,
        "Psi4": ParallelRavenJob,
        "Q-Chem": ParallelRavenJob,
    }
    
    restart_filter = "Raven JSON files (*.json)"
    
    @staticmethod
    def fixup_theory(theory, restart_file=None):
        theory.job_type = "force"
        return theory
    
