# methods for the TSS finder tool

from configparser import ConfigParser

from AaronTools.utils.utils import combine_dicts

from chimerax.ui.options import FloatOption, Option, IntOption

from Qt.QtCore import Qt
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


class SymbolicEnumOption(EnumOption):
    def _make_widget(self, *, values=None, labels=None):
        self.widget = QComboBox()
        if labels and values:
            self.values = values
            self.labels = labels
            self.widget.addItems(labels)
            for i, value in enumerate(values):
                self.widget.setItemData(i, value)
        return self.widget
    
    def get_value(self):
        return self.widget.currentData(Qt.UserRole)
    
    def set_value(self, value):
        ndx = self.widget.findText(value, Qt.MatchExactly)
        if ndx < 0:
            ndx = self.widget.findData(value, Qt.UserRole, Qt.MatchExactly)
        self.widget.setCurrentIndex(ndx)
    

class TSSFinder:
    # list of software packages that this can work with
    available_for = []
    
    restart_filter = None
    
    get_file_contents = None
    
    cluster_job_cls = None
    
    local_job_cls = None
    
    options = dict()
    
    save_file_filter = None
    
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

def get_orca_neb_file_contents(
    reactant, product, theory
):
    theory.geometry = reactant
    orca_inp, warnings = reactant.write(
        theory=theory, outfile=False, style="orca", return_warnings=True,
    )
    xyz = product.write(style="xyz", outfile=False)
    return {"inp": orca_inp, "xyz": xyz}, warnings

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
                "JOB_TYPE": "FSM",
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

def get_raven_input(
    reactant,
    product,
    theory,
    exec_type=None,
    rms_force_tol=None,
    max_force_tol=None,
    nodes=11,
    similarity_falloff=5,
    kernel="rbf",
    variance_threshold=1e-3,
    **kwargs,
):
    print("kwargs", kwargs)
    config = ConfigParser()
    config.add_section("Theory")
    config.add_section("Job")
    config.add_section("Raven")

    for section in kwargs:
        if not kwargs[section]:
            continue
        if not hasattr(kwargs[section], "__iter__"):
            continue
        if isinstance(kwargs[section], str):
            continue
        for option, value in kwargs[section].items():
            config.set(section, option, str(value))
    
    if theory.processors:
        config.set("Job", "procs", str(theory.processors))
    if theory.memory:
        config.set("Job", "exec_memory", str(theory.memory))
    if exec_type:
        config.set("Job", "exec_type", exec_type)

    if theory.method:
        config.set("Theory", "method", theory.method.name)
    if not theory.method.is_semiempirical:
        if theory.basis.basis:
            theory.basis.refresh_elements(reactant)
            basis_info = ""
            for basis in theory.basis.basis:
                basis_info += " ".join(basis.elements)
                if basis.aux_type:
                    basis_info += " aux %s" % basis.aux_type
                basis_info += " %s" % basis.name
                if basis.user_defined:
                    basis_info += " %s" % basis.user_defined
                basis_info += "\n       "
            config.set("Theory", "basis", basis_info.strip())
        
        if theory.basis.ecp:
            theory.basis.refresh_elements(reactant)
            ecp_info = ""
            for basis in theory.basis.ecp:
                ecp_info += " ".join(basis.elements)
                ecp_info += " %s" % basis.name
                if basis.user_defined:
                    ecp_info += " %s" % basis.user_defined
                ecp_info += "\n      "
            config.set("Theory", "ecp", ecp_info.strip())
    if theory.solvent:
        config.set("Theory", "solvent", theory.solvent.solvent)
        config.set("Theory", "solvent_model", theory.solvent.solvent_model)
    if theory.empirical_dispersion:
        config.set("Theory", "empirical_dispersion", theory.empirical_dispersion.name)
    if theory.grid:
        config.set("Theory", "grid", theory.grid.name)
    config.set("Theory", "charge", str(theory.charge))
    config.set("Theory", "multiplicity", str(theory.multiplicity))

    config.set("Raven", "reactant", "reactant.xyz")
    config.set("Raven", "product", "product.xyz")
    config.set("Raven", "rms_force_tol", "%.3e" % rms_force_tol)
    config.set("Raven", "max_force_tol", "%.3e" % max_force_tol)
    config.set("Raven", "similarity_falloff", "%.3f" % similarity_falloff)
    config.set("Raven", "variance_threshold", "%.3e" % variance_threshold)
    config.set("Raven", "kernel", kernel)
    config.set("Raven", "nodes", str(nodes))

    ini_file = ""
    for section in config.sections():
        ini_file += "[%s]\n" % section
        for option in config.options(section):
            value = config.get(section, option)
            ini_file += "%s = %s\n" % (option, value)
        
        ini_file += "\n"
    
    out = {
        "ini": ini_file,
        "reactant.xyz": reactant.write(outfile=False),
        "product.xyz": product.write(outfile=False),
    }
    
    _, warnings = reactant.write(
        theory=theory, outfile=False, style=exec_type, return_warnings=True
    )
    
    return out, warnings


class STQN(TSSFinder):
    """
    synchronous transit-guided quasi-Newton method
    available in Gaussian with opt=QST2
    we don't take guesses (yet?), so no opt=QST3
    """
    available_for = ["Gaussian"]
        
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

    fixup_theory = {
        "ORCA": fixup_orca_neb_theory
    }

    restart_filter = "XYZ pathway files (*.xyz)"
    
    get_file_contents = {
        "ORCA": get_orca_neb_file_contents,
    }


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
    
    save_file_filter = "Raven input files (*.ini)"
    
    available_for = ["Gaussian", "ORCA", "Psi4", "Q-Chem"]
    
    options = {
        "nodes": (
            IntOption, {
                "min": 5,
                "max": 25,
                "default": 11,
            }
        ),
        "kernel": (
            SymbolicEnumOption, {
                "values": [
                    "RBF",
                    "matern52",
                ],
                "labels": [
                    "radial basis function",
                    "Matérn ν=5/2",
                ],
            }
        ),
        "similarity_falloff": (
            FloatOption, {
                "min": 1,
                "max": 20.,
                "step": 0.5,
                "default": 7.5,
            }
        ),
        "variance_threshold": (
            FloatOption, {
                "min": 0.0,
                "max": 0.5,
                "step": 0.0005,
                "decimal_places": 5,
                "default": 0.001,
            }
        ),
        "rms_force_tol": (
            FloatOption, {
                "min": 1e-3,
                "max": 2e-2,
                "decimal_places": 4,
                "step": 5e-4,
                "default": 2.5e-3,
                "name": "RMS force tol.",
            }
        ),
        "max_force_tol": (
            FloatOption, {
                "min": 1e-3,
                "max": 2e-2,
                "decimal_places": 4,
                "step": 5e-4,
                "default": 2.5e-3,
                "name": "max. force tol.",
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
    
    get_file_contents = {
        "Gaussian": lambda *args, exec_type="gaussian", **kwargs: get_raven_input(
            *args, exec_type=exec_type, **kwargs
        ),
        "ORCA": lambda *args, exec_type="orca", **kwargs: get_raven_input(
            *args, exec_type=exec_type, **kwargs
        ),
        "Psi4": lambda *args, exec_type="psi4", **kwargs: get_raven_input(
            *args, exec_type=exec_type, **kwargs
        ),
        "Q-Chem": lambda *args, exec_type="qchem", **kwargs: get_raven_input(
            *args, exec_type=exec_type, **kwargs
        ),
    }
