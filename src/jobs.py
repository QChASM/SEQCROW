from sys import platform
import os
import subprocess
from time import asctime, localtime, sleep
from pathlib import Path
from shutil import rmtree

from AaronTools.fileIO import FileReader
from AaronTools.geometry import Geometry
from AaronTools.theory import OptimizationJob

from chimerax.core.commands import run
from chimerax.ui.options import BooleanOption

from jinja2 import Template

from Qt.QtCore import QThread

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.managers import ADD_FILEREADER


def allow_chk2fchk(theory):
    """determine whether we should allow the option to convert
    .chk files to .fchk files"""
    try:
        return "chk" in theory.kwargs["link0"]
    except KeyError:
        return False


class LocalJob(QThread):
    """
    base class for jobs running using local hardware and software
    
    attributes:
    format_name - output file format
    info_type - program running job
    exec_options - dict() of options that are available when preparing to
        run the job locally
        keys are kwargs passed when creating the job instance, as well
        as the labels for the options (underscores will be replaced with
        spaces)
        values are tuples:
            - first is the option type (see chimerax.ui.options)
            - second are kwargs used to instantiate the option
            - third (option) is a function used to determine whether the
                option is available
                function takes a Theory instance as the only argument and
                returns either True or False for whether the option should
                be enabled
                if no third option is given, the option is always available
    
    after the job has started/finished, the following attributes will be set:
    scratch_dir - directory where the job was run
    start_time - time and date the job started
    output_name - output file(s) - can be a string if there is only one file
    """
    format_name = None
    info_type = None
    exec_options = {
        "delete_everything_but_output_file": (
            BooleanOption, {"default": False},
        ),
    }
    
    """job for running computational chemistry software on local hardware"""
    def __init__(
        self,
        name,
        session,
        theory,
        geometry=None,
        auto_update=False,
        auto_open=False,
        **job_options,
    ):
        """base class of local ORCA, Gaussian, and Psi4 jobs
        name        str - name of job
        session     chimerax session object
        theory      AaronTools.theory.Theory or a dictionary with a saved job's settings
        """
        self.name = name
        self.session = session
        self.theory = theory
        self.geometry = geometry
        if geometry:
            self.theory.geometry = geometry
        else:
            self.geometry = self.theory.geometry
        self.auto_update = auto_update
        self.auto_open = auto_open
        self.killed = False
        self.error = False
        self.output_name = None
        self.scratch_dir = None
        self.process = None
        self.start_time = None
        self.job_options = job_options
        
        super().__init__()

    def kill(self):
        self.session.logger.warning("killing %s..." % self)

        if self.process is not None:
            self.process.kill()
            self.process.wait()
            self.session.logger.warning(
                "%s might finish an in-progess calculation step before exiting" % self
            )
        
        self.killed = True
       
        #use exit b/c terminate can cause chimera to freeze
        super().exit(1)

    def run(self):
        """overwrite to execute job"""
        pass

    def terminate(self):
        if self.process is not None:
            self.process.kill()
            
        super().terminate()
    
    def write_file(self, filename):
        try:
            input_info = self.session.seqcrow_qm_input_manager.get_info(self.info_type)
        except KeyError:
            input_info = self.session.conformer_search_manager.get_info(self.info_type)
        contents, warnings = input_info.get_file_contents(self.theory)
        self.input_files = []
        if isinstance(contents, dict):
            name, ext = os.path.splitext(filename)
            for key, item in contents.items():
                if "." in key:
                    fname = os.path.join(
                        os.path.dirname(filename), key
                    )
                else:
                    fname = name + ".%s" % key
                outname = os.path.basename(fname)
                item = item.replace("{{ name }}", name)
                self.input_files.append(fname)
                with open(fname, "w") as f:
                    f.write(item)
        else:
            outname = os.path.basename(filename)
            name, ext = os.path.splitext(outname)
            contents = contents.replace("{{ name }}", name)
            self.input_files.append(filename)
            with open(filename, "w") as f:
                f.write(contents)
    
    def get_json(self):
        from AaronTools.geometry import Geometry

        d = {
            "theory": self.theory,
            "geometry": Geometry(self.geometry),
        }

        d['output'] = self.output_name
        d['scratch'] = self.scratch_dir

        d['server'] = 'local'
        d['start_time'] = self.start_time
        d['name'] = self.name
        d['depend'] = None
        d['auto_update'] = False
        d['auto_open'] = self.auto_open or self.auto_update
        d['job_options'] = self.job_options

        return d

    def update_structure(self, structure):
        """
        overwrite to update structure (AtomicStructure) with the
        coordinates from this job's output file
        required for "update structure" option to work when launching
        a job if the output file is not parsable by AaronTools
        """
        if isinstance(self.output_name, str):
            fr = FileReader(self.output_name, just_geom=False, get_all=True)
            rescol = ResidueCollection(fr)
            rescol.update_chix(structure)
            self.session.filereader_manager.triggers.activate_trigger(
                ADD_FILEREADER, ([structure], [fr])
            )
        elif hasattr(self.output_name, "__iter__"):
            if isinstance(self.output_name, dict):
                for fmt, path in self.output_name.items():
                    fr = FileReader(
                        (self.output_name, fmt),
                        just_geom=False,
                        get_all=True,
                    )
                    rescol = ResidueCollection(fr)
                    rescol.update_chix(structure)
                    self.session.filereader_manager.triggers.activate_trigger(
                        ADD_FILEREADER, ([structure], [fr])
                    )
            else:
                for file in self.output_name:
                    fr = FileReader(self.output_name, just_geom=False, get_all=True)
                    rescol = ResidueCollection(fr)
                    rescol.update_chix(structure)
                    self.session.filereader_manager.triggers.activate_trigger(
                        ADD_FILEREADER, ([structure], [fr])
                    )

    def open_structure(self):
        if isinstance(self.output_name, str):
            args = ["open", "\"%s\"" % self.output_name, "format", self.format_name]
            # if self.theory.job_type and any(
            #     isinstance(job, OptimizationJob) for job in self.theory.job_type
            # ):
            #     args.extend(["coordsets", "true"])
            run(self.session, " ".join(args))
        
        elif hasattr(self.output_name, "__iter__"):
            if isinstance(self.output_name, dict):
                for fmt, path in self.output_name.items():
                    if not isinstance(path, str):
                        for f in path:
                            args = [
                                "open",
                                "\"%s\"" % f,
                                "format",
                                fmt,
                            ]
                            # if self.theory.job_type and any(
                            #     isinstance(job, OptimizationJob) for job in self.theory.job_type
                            # ):
                            #     args.extend(["coordsets", "true"])
                            run(self.session, " ".join(args))
                    
                    else:
                        args = [
                            "open",
                            "\"%s\"" % path,
                            "format",
                            fmt,
                        ]
                        # if self.theory.job_type and any(
                        #     isinstance(job, OptimizationJob) for job in self.theory.job_type
                        # ):
                        #     args.extend(["coordsets", "true"])
                        run(self.session, " ".join(args))
        
            else:
                for file in self.output_name:
                    run(self.session, "open \"%s\"" % file)

    def get_errors(self):
        check_for_errors = []
        if isinstance(self.output_name, str):
            check_for_errors.append((self.output_name, self.format_name, None))

        elif hasattr(self.output_name, "__iter__"):
            if isinstance(self.output_name, dict):
                for fmt, path in self.output_name.items():
                    check_for_errors.append((path, fmt, None))

            else:
                for file in self.output_name:
                    check_for_errors.append(file)
        
        error_codes = []
        error_msgs = []
        frs = []
        for file in check_for_errors:
            try:
                fr = FileReader(file, just_geom=False)
                frs.append(fr)
                error = fr["error"]
                error_msg = fr["error_msg"]
                error_codes.append(error)
                error_msgs.append(error_msg)
            except (NotImplementedError, KeyError, FileNotFoundError):
                continue
        
        return error_codes, error_msgs, frs

    def remove_extra_files(self):
        keep_files = [
            os.path.join(self.scratch_dir, "seqcrow_log.txt"),
            *self.input_files,
        ]
        if isinstance(self.output_name, str):
            keep_files.append(self.output_name)
        else:
            keep_files.extend(self.output_name)
        
        keep_paths = [Path(f) for f in keep_files]
        
        for f in os.listdir(self.scratch_dir):
            fname = os.path.join(self.scratch_dir, f)
            fpath = Path(fname)
            if not any(fpath == path for path in keep_paths):
                print("deleting", fname)
                if fpath.is_file():
                    os.remove(fname)
                elif fpath.is_dir():
                    rmtree(fname)


class ORCAJob(LocalJob):
    format_name = "out"
    info_type = "ORCA"

    def __repr__(self):
        return "local ORCA job \"%s\"" % self.name

    def run(self):
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR),
            "%s %s" % (self.name, self.start_time.replace(':', '.')),
        )

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        infile = self.name + '.inp'
        infile = infile.replace(' ', '_')
        infile_path = os.path.join(self.scratch_dir, infile)
        self.write_file(infile_path)
        executable = os.path.abspath(self.session.seqcrow_settings.settings.ORCA_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.ORCA_EXE

        self.output_name = os.path.join(self.scratch_dir, self.name.replace(' ', '_') + '.out')
        outfile = open(self.output_name, 'w')

        args = [executable, infile]

        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        log.close()
        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'a')

        if " " in infile:
            raise RuntimeError("ORCA input files cannot contain spaces")

        try:
            if platform == "win32":
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
            else:        
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log)
        except FileNotFoundError:
            self.session.logger.error(
                "job could not start because ORCA executable (%s) was not found\n" % executable +
                "ensure the correct path to executable is specified in the \"SEQCROW Jobs\"\n" +
                "settings in Favorites/Preferences > Settings..."
            )
            return

        self.process.communicate()
        self.process = None

        if self.job_options.get("delete_everything_but_output_file", False):
            self.remove_extra_files()

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "ORCA"
        return d


class GaussianJob(LocalJob):
    format_name = "log"
    info_type = "Gaussian"
    exec_options = {
        "convert_chk_files_to_fchk": (
            BooleanOption, {"default": False}, allow_chk2fchk,
        ),
        "delete_everything_but_output_file": (
            BooleanOption, {"default": False},
        ),
    }
    
    def __repr__(self):
        return "local Gaussian job \"%s\"" % self.name

    def run(self):
        self.start_time = asctime(localtime())
        
        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
            "%s %s" % (self.name, self.start_time.replace(':', '.')), \
        )
        
        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        if platform == "win32":
            infile = self.name + '.gjf'
        else:
            infile = self.name + '.com'

        infile_path = os.path.join(self.scratch_dir, infile)
        self.write_file(infile_path)

        executable = os.path.abspath(self.session.seqcrow_settings.settings.GAUSSIAN_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.GAUSSIAN_EXE
            
        self.output_name = os.path.join(self.scratch_dir, self.name + '.log')
        
        args = [executable, infile, self.output_name]
        
        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        try:
            if platform == "win32":
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log)
        except FileNotFoundError:
            self.session.logger.error(
                "job could not start because Gaussian executable (%s) was not found\n" % executable +
                "ensure the correct path to executable is specified in the \"SEQCROW Jobs\"\n" +
                "settings in Favorites/Preferences > Settings..."
            )
            return
        
        self.process.communicate()
        self.process = None

        if self.job_options.get("fchk_the_chk_file", False):
            gau_exe_dir = os.path.dirname(executable)
            formchk = os.path.join(gau_exe_dir, "formchk")
            _, ext = os.path.splitext(executable)
            formchk += ext
            for f in os.listdir(self.scratch_dir):
                _, ext = os.path.splitext(f)
                if ext.lower() == ".chk":
                    fchk_name = self.name + ".fchk"
                    args = [formchk, f, fchk_name]
                    if platform == "win32":
                        self.process = subprocess.Popen(
                            args,
                            cwd=self.scratch_dir,
                            stdout=log,
                            stderr=log,
                            creationflags=subprocess.CREATE_NO_WINDOW,
                        )
                    else:
                        self.process = subprocess.Popen(
                            args,
                            cwd=self.scratch_dir,
                            stdout=log,
                            stderr=log,
                        )
                    if not isinstance(self.output_name, list):
                        self.output_name = [self.output_name]
                    self.output_name.append(
                        os.path.join(self.scratch_dir, fchk_name)
                    )

        if self.job_options.get("delete_everything_but_output_file", False):
            self.remove_extra_files()

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "Gaussian"
        return d


class Psi4Job(LocalJob):
    format_name = "dat"
    info_type = "Psi4"

    def __repr__(self):
        return "local Psi4 job \"%s\"" % self.name

    def run(self):
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
            "%s %s" % (self.name, self.start_time.replace(':', '.')), \
        )

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        infile = self.name + '.in'
        infile_path = os.path.join(self.scratch_dir, infile)
        self.write_file(infile_path)

        executable = os.path.abspath(self.session.seqcrow_settings.settings.PSI4_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.PSI4_EXE

        self.output_name = os.path.join(self.scratch_dir, self.name + '.out')

        args = [executable, infile, self.output_name]

        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        try:
            if platform == "win32":
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log)
        except FileNotFoundError:
            self.session.logger.error(
                "job could not start because Psi4 executable (%s) was not found\n" % executable +
                "ensure the correct path to executable is specified in the \"SEQCROW Jobs\"\n" +
                "settings in Favorites/Preferences > Settings..."
            )
            return
            
        for f in os.listdir(self.scratch_dir):
            if f.lower().endswith("fchk") or f.lower().endswith("fch"):
                self.output_name = {
                    "out": self.output_name,
                    "fchk": os.path.join(self.scratch_dir, f),
                }

        self.process.communicate()
        self.process = None

        if self.job_options.get("delete_everything_but_output_file", False):
            self.remove_extra_files()

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "Psi4"
        return d


class SQMJob(LocalJob):
    format_name = "sqmout"
    info_type = "SQM"
    def __repr__(self):
        return "local sqm job \"%s\"" % self.name

    def run(self):
        from chimerax.amber_info import amber_bin
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
            "%s %s" % (self.name, self.start_time.replace(':', '.')), \
        )

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        infile = self.name + '.mdin'
        infile_path = os.path.join(self.scratch_dir, infile)
        self.write_file(infile_path)

        sqm_exe = os.path.join(amber_bin, "sqm")
        if not os.path.exists(sqm_exe):
            # add .exe for windows only?
            sqm_exe += ".exe"

        self.output_name = os.path.join(self.scratch_dir, self.name + '.sqmout')

        args = [sqm_exe, "-i", infile_path, "-o", self.output_name]

        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        if platform == "win32":
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log)

        self.process.communicate()
        self.process = None

        if self.job_options.get("delete_everything_but_output_file", False):
            self.remove_extra_files()

    def get_json(self):
        d = super().get_json()
        d["format"] = "SQM"
        return d


class QChemJob(LocalJob):
    format_name = "out"
    info_type = "Q-Chem"

    def __repr__(self):
        return "local Q-Chem job \"%s\"" % self.name

    def run(self):
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
            "%s %s" % (self.name, self.start_time.replace(':', '.')), \
        )

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        infile = self.name.replace(" ", "_") + '.inp'
        infile_path = os.path.join(self.scratch_dir, infile)
        self.write_file(infile_path)

        executable = os.path.abspath(self.session.seqcrow_settings.settings.QCHEM_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.QCHEM_EXE

        self.output_name = os.path.join(self.scratch_dir, self.name.replace(" ", "_") + '.out')
        outfile = open(self.output_name, 'w')

        args = [
            executable,
            "-nt %i" % self.theory.processors,
            infile,
        ]

        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        try:
            if platform == "win32":
                self.process = subprocess.Popen(
                    args, cwd=self.scratch_dir, stdout=outfile, stderr=log,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.process = subprocess.Popen(
                    args, cwd=self.scratch_dir, stdout=outfile, stderr=log
                )
        except FileNotFoundError:
            self.session.logger.error(
                "job could not start because Q-Chem executable (%s) was not found\n" % executable +
                "ensure the correct path to executable is specified in the \"SEQCROW Jobs\"\n" +
                "settings in Favorites/Preferences > Settings..."
            )
            return

        self.process.communicate()
        self.process = None

        if self.job_options.get("delete_everything_but_output_file", False):
            self.remove_extra_files()

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "Q-Chem"
        return d


class XTBJob(LocalJob):
    format_name = "xyz"
    info_type = "xTB"

    def __repr__(self):
        return "local xTB job \"%s\"" % self.name

    def run(self):
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR),
            "%s %s" % (self.name, self.start_time.replace(':', '.')),
        )

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        infile = self.name
        infile_path = os.path.join(self.scratch_dir, infile)
        self.write_file(infile_path)
        executable = os.path.abspath(self.session.seqcrow_settings.settings.XTB_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.XTB_EXE

        args, warnings = self.theory.get_xtb_cmd(return_warnings=False, split_words=True)
        args[0] = executable
        for i, arg in enumerate(args):
            args[i] = arg.replace("{{ name }}", self.name)
        
        self.output_name = os.path.join(self.scratch_dir, self.name + '.out')
        outfile = open(self.output_name, 'w')

        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        log.close()
        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'a')

        try:
            if platform == "win32":
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
            else:        
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log)
        except FileNotFoundError:
            self.session.logger.error(
                "job could not start because xTB executable (%s) was not found\n" % executable +
                "ensure the correct path to executable is specified in the \"SEQCROW Jobs\"\n" +
                "settings in Favorites/Preferences > Settings..."
            )
            return

        self.process.communicate()
        self.process = None

        self.output_name = dict()
        for f in os.listdir(self.scratch_dir):
            if f.endswith("xyz"):
                if "xyz" in self.output_name :
                    self.output_name["xyz"].append(os.path.join(self.scratch_dir, f))
                    continue
                self.output_name["xyz"] = [os.path.join(self.scratch_dir, f)]
            elif f.endswith("g98.out"):
                self.output_name["log"] = os.path.join(self.scratch_dir, f)
            elif f.endswith("mol"):
                self.output_name["sdf"] = os.path.join(self.scratch_dir, f)

        if self.job_options.get("delete_everything_but_output_file", False):
            self.remove_extra_files()

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "xTB"
        return d


class CRESTJob(LocalJob):
    format_name = "xyz"
    info_type = "CREST"
    exec_options = {}

    def __repr__(self):
        return "local CREST job \"%s\"" % self.name

    def write_file(self, infile_path):
        self.geometry.write(
            theory=self.theory, style="crest", outfile=infile_path
        )

    def run(self):
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR),
            "%s %s" % (self.name, self.start_time.replace(':', '.')),
        )

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        self.name = self.name.replace(" ", "_")
        infile = self.name
        infile_path = os.path.join(self.scratch_dir, infile)
        self.write_file(infile_path)
        executable = os.path.abspath(self.session.seqcrow_settings.settings.CREST_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.CREST_EXE

        xtb_executable = os.path.abspath(self.session.seqcrow_settings.settings.XTB_EXE)
        if not os.path.exists(xtb_executable):
            xtb_executable = self.session.seqcrow_settings.settings.XTB_EXE

        if "command_line" in self.theory.kwargs:
            if not any(x == "xnam" for x in self.theory.kwargs["command_line"]):
                self.theory.kwargs["command_line"]["xnam"] = [xtb_executable]
        else:
            self.theory.kwargs["command_line"] = {"xnam": [xtb_executable]}
            
        args, warnings = self.theory.get_crest_cmd(return_warnings=False, split_words=True)
        args[0] = executable
        for i, arg in enumerate(args):
            args[i] = arg.replace("{{ name }}", self.name)

        self.output_name = os.path.join(self.scratch_dir, self.name + '.out')
        outfile = open(self.output_name, 'w')

        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        log.close()
        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'a')

        try:
            if platform == "win32":
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
            else:        
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log)
        except FileNotFoundError:
            self.session.logger.error(
                "job could not start because CREST executable (%s) was not found\n" % executable +
                "ensure the correct path to executable is specified in the \"SEQCROW Jobs\"\n" +
                "settings in Favorites/Preferences > Settings..."
            )
            return
            
        self.process.communicate()
        self.process = None

        for f in ["crest_conformers", "tautomers", "deprotonated", "protomers"]:
            test_file = os.path.join(self.scratch_dir, f + ".xyz")
            if os.path.exists(test_file):
                self.output_name = test_file

        if self.job_options.get("delete_everything_but_output_file", False):
            self.remove_extra_files()

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "CREST"
        return d

    def open_structure(self):
        fr = FileReader(self.output_name, get_all=True)
        
        for i, (comment, _) in enumerate(fr.all_geom):
            fr.all_geom[i] = (*fr.all_geom[i], {"energy": float(comment)})
        fr.other["energy"] = float(fr.comment)
        
        geom = ResidueCollection(fr, refresh_ranks=False).copy(
            comment=fr.comment, copy_atoms=True
        )
        structure = geom.get_chimera(
            self.session, coordsets=True, filereader=fr
        )
        self.session.filereader_manager.triggers.activate_trigger(
            ADD_FILEREADER, ([structure], [fr])
        )
        try:
            from SEQCROW.tools.per_frame_plot import EnergyPlot
            nrg_plot = EnergyPlot(self.session, structure, fr, xlabel="conformer")
            if not nrg_plot.opened:
                nrg_plot.delete()
        except Exception as e:
            self.session.logger.warning(repr(e))
        structure.name = self.name
        self.session.models.add([structure])


class LocalClusterJob(LocalJob):
    format_name = None
    """
    job for submitting computational chemistry jobs to a queueing
    system (e.g. Slurm, PBS, etc.) that is running on local hardware
    """
    def __init__(
        self,
        name,
        session,
        theory,
        file_type,
        queue_type=None,
        geometry=None,
        auto_update=False,
        auto_open=False,
        template=None,
        walltime=2,
        processors=4,
        memory=8,
        template_kwargs=None,
    ):
        """
        base class of local ORCA, Gaussian, and Psi4 cluster jobs
        name        str - name of job
        session     chimerax session object
        theory      AaronTools.theory.Theory or a dictionary with a saved job's settings
        """
        super().__init__(name, session, theory)

        self.name = name
        self.session = session
        self.theory = theory
        if geometry:
            self.theory.geometry = geometry
        self.auto_update = auto_update
        self.auto_open = auto_open
        self.killed = False
        self.error = False
        self.output_name = None
        self.scratch_dir = None
        self.process = None
        self.start_time = None
        self.submitted = False
        self.template = template
        self.walltime = walltime
        self.processors = processors
        self.memory = memory
        self.info_type = file_type
        self.queue_type = queue_type
        self.cluster_type = session.seqcrow_cluster_scheduling_software_manager.get_queue_manager(
            queue_type
        ).get_template(file_type)()
        self.format_name = self.cluster_type.expected_output_ext
        self.template_kwargs = dict()
        if template_kwargs:
            self.template_kwargs = template_kwargs

    def __repr__(self):
        return "local cluster %s job \"%s\"" % (
            self.info_type, self.name
        )
   
    def run(self):
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR),
            "%s_%s" % (self.name, self.start_time.replace(':', '.').replace(" ", "_")),
        )

        if " " in self.scratch_dir:
            self.session.logger.warning(
                "spaces in the full path to SEQCROW's scratch directory"
                "may cause issues with submitting jobs to clusters"
            )

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)
        
        if self.cluster_type.expected_input_ext:
            infile = self.name.replace(" ", "_") + "." + self.cluster_type.expected_input_ext
        else:
            infile = self.name.replace(" ", "_")
        
        if isinstance(self.cluster_type.expected_output_ext, str):
            outfile = self.name.replace(" ", "_") + "." + self.cluster_type.expected_output_ext
        else:
            if not isinstance(self.cluster_type.expected_output_ext, str):
                outfile = []
                for f in self.cluster_type.expected_output_ext:
                    outfile.append(f)
            outfile = self.cluster_type.expected_output_ext
        infile_path = os.path.join(self.scratch_dir, infile)
        if isinstance(outfile, str):
            self.output_name = os.path.join(self.scratch_dir, outfile)
        else:
            self.output_name = [
                os.path.join(self.scratch_dir, f) for f in outfile
            ]

        self.write_file(infile_path)
        self.cluster_type.submit_job(
            infile_path,
            self.walltime,
            self.processors,
            self.memory,
            template=self.template,
            template_kwargs=self.template_kwargs,
        )

        if isinstance(self.output_name, list):
            self.output_name = [f for f in self.output_name if os.path.exists(f)]

        return 
    
    def kill(self):
        self.session.logger.warning("killing %s..." % self)

        if self.isRunning():
            self.session.logger.warning(
                "stopping cluster jobs is not implemented"
            )
        
        self.killed = True
       
        #use exit b/c terminate can cause chimera to freeze
        super().exit(1)
    
    def get_json(self):
        from AaronTools.geometry import Geometry

        d = {
            "theory": self.theory,
            "geometry": Geometry(self.theory.geometry),
        }

        d['output'] = self.output_name
        d['scratch'] = self.scratch_dir

        d['server'] = 'cluster'
        d['memory'] = self.memory
        d['processors'] = self.processors
        d['walltime'] = self.walltime
        d['file_type'] = self.info_type
        d['start_time'] = self.start_time
        d['name'] = self.name
        d['template'] = self.template
        d['queue_type'] = self.queue_type
        d['depend'] = None
        d['auto_update'] = False
        d['auto_open'] = self.auto_open or self.auto_update
        d['template_kwargs'] = self.template_kwargs

        return d


class TSSJob(LocalJob):    
    def __init__(
        self,
        name,
        session,
        theory,
        reactant,
        product,
        file_type,
        algorithm_kwargs,
        auto_update=False,
        auto_open=False,
        **job_options,
    ):
        super().__init__(
            name, session, theory,
            auto_open=auto_open, auto_update=auto_update
        )
        self.reactant = reactant
        self.product = product
        self.file_type = file_type
        self.algorithm_kwargs = algorithm_kwargs
        self.job_options = job_options

    def write_file(self, filename, **kwargs):
        input_info = self.session.tss_finder_manager.get_info(
            self.tss_algorithm
        )
        self.input_files = []
        if input_info.get_file_contents:
            if callable(input_info.get_file_contents):
                contents, warnings = input_info.get_file_contents(
                    self.reactant, self.product, self.theory, **kwargs
                )
            else:
                contents, warnings = input_info.get_file_contents[
                    self.file_type
                ](self.reactant, self.product, self.theory, **kwargs)

        else:
            file_info = self.session.seqcrow_qm_input_manager.get_info(
                self.file_type
            )
            contents, warnings = file_info.get_file_contents(self.theory)

        if isinstance(contents, dict):
            name, ext = os.path.splitext(filename)
            for key, item in contents.items():
                if "." in key:
                    fname = os.path.join(
                        os.path.dirname(filename), key
                    )
                else:
                    fname = name + ".%s" % key
                outname = os.path.basename(fname)
                item = item.replace("{{ name }}", name)
                self.input_files.append(fname)
                with open(fname, "w") as f:
                    f.write(item)
        else:
            outname = os.path.basename(filename)
            name, ext = os.path.splitext(outname)
            contents = contents.replace("{{ name }}", name)
            self.input_files.append(filename)
            with open(filename, "w") as f:
                f.write(contents)
    
    def get_json(self):
        d = super().get_json()
        d.pop("geometry")
        d["reactant"] = Geometry(self.reactant)
        d["product"] = Geometry(self.product)
        d["file_type"] = self.file_type
        d["algorithm_kwargs"] = self.algorithm_kwargs
        return d


class ClusterTSSJob(LocalClusterJob):
    def __init__(
        self,
        name,
        session,
        theory,
        reactant,
        product,
        file_type,
        tss_algorithm,
        algorithm_kwargs,
        auto_update=False,
        auto_open=False,
        queue_type=None,
        template=None,
        walltime=2,
        processors=4,
        memory=8,
        template_kwargs=None,
    ):
        super().__init__(
            name, session, theory, file_type,
            queue_type=queue_type, template=template, walltime=walltime,
            processors=processors, memory=memory, template_kwargs=template_kwargs,
            auto_open=auto_open, auto_update=auto_update,
        )
        self.reactant = reactant
        self.product = product
        self.file_type = file_type
        self.tss_algorithm = tss_algorithm
        self.name = name
        self.session = session
        self.theory = theory
        self.algorithm_kwargs = algorithm_kwargs
        
        self.killed = False
        self.error = False
        self.output_name = None
        self.scratch_dir = None
        self.process = None
        self.start_time = None
        self.submitted = False
        self.template = template
        self.walltime = walltime
        self.processors = processors
        self.memory = memory
        self.info_type = file_type
        self.queue_type = queue_type
        self.cluster_type = session.seqcrow_cluster_scheduling_software_manager.get_queue_manager(
            queue_type
        ).get_template(file_type)()
        self.template_kwargs = dict()
        self.format_name = self.cluster_type.expected_output_ext
        if template_kwargs:
            self.template_kwargs = template_kwargs

    def write_file(self, filename, **kwargs):
        input_info = self.session.tss_finder_manager.get_info(
            self.tss_algorithm
        )
        self.input_files = []
        if input_info.get_file_contents:
            if callable(input_info.get_file_contents):
                contents, warnings = input_info.get_file_contents(
                    self.reactant, self.product, self.theory, **kwargs
                )
            else:
                contents, warnings = input_info.get_file_contents[
                    self.file_type
                ](self.reactant, self.product, self.theory, **kwargs)

        else:
            file_info = self.session.seqcrow_qm_input_manager.get_info(
                self.file_type
            )
            contents, warnings = file_info.get_file_contents(self.theory)

        if isinstance(contents, dict):
            name, ext = os.path.splitext(filename)
            for key, item in contents.items():
                if "." in key:
                    fname = os.path.join(
                        os.path.dirname(filename), key
                    )
                else:
                    fname = name + ".%s" % key
                outname = os.path.basename(fname)
                item = item.replace("{{ name }}", name)
                self.input_files.append(fname)
                with open(fname, "w") as f:
                    f.write(item)
        else:
            outname = os.path.basename(filename)
            name, ext = os.path.splitext(outname)
            contents = contents.replace("{{ name }}", name)
            self.input_files.append(filename)
            with open(filename, "w") as f:
                f.write(contents)

    def get_json(self):
        d = super().get_json()
        d.pop("geometry")
        d["reactant"] = Geometry(self.reactant)
        d["product"] = Geometry(self.product)
        d["file_type"] = self.file_type
        d['tss_algorithm'] = self.tss_algorithm
        d['algorithm_kwargs'] = self.algorithm_kwargs

        d['output'] = self.output_name
        d['scratch'] = self.scratch_dir

        d['server'] = 'cluster'
        d['template'] = self.template
        d['queue_type'] = self.queue_type
        d['file_type'] = self.info_type
        d['start_time'] = self.start_time
        d['processors'] = self.processors
        d['memory'] = self.memory
        d['walltime'] = self.walltime
        d['name'] = self.name
        d['depend'] = None
        d['auto_update'] = False
        d['auto_open'] = self.auto_open or self.auto_update
        
        return d


class SerialRavenJob(TSSJob):
    format_name = "xyz"
    info_type = "Raven"
    tss_algorithm = "GPR growing string method"
    
    def __repr__(self):
        return "serial Raven job using %s \"%s\"" % (
            self.file_type, self.name
        )
    
    def run(self):
        from sys import executable as python_exe
        
        import Raven
        
        from chimerax.core.commands import run
        from SEQCROW.residue_collection import ResidueCollection
        
        raven_path = os.path.dirname(Raven.__file__)
        raven_exe = os.path.join(raven_path, "bin", "raven.py")
        
        self.start_time = asctime(localtime())
        
        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
            "%s %s" % (self.name, self.start_time.replace(':', '.')), \
        )
        
        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        if self.file_type.lower() == "gaussian":
            qm_executable = os.path.abspath(
                self.session.seqcrow_settings.settings.GAUSSIAN_EXE
            )
            if not os.path.exists(qm_executable):
                qm_executable = self.session.seqcrow_settings.settings.GAUSSIAN_EXE

        if self.file_type.lower() == "orca":
            qm_executable = os.path.abspath(
                self.session.seqcrow_settings.settings.ORCA_EXE
            )
            if not os.path.exists(qm_executable):
                qm_executable = self.session.seqcrow_settings.settings.ORCA_EXE

        if self.file_type.lower() == "psi4":
            qm_executable = os.path.abspath(
                self.session.seqcrow_settings.settings.PSI4_EXE
            )
            if not os.path.exists(qm_executable):
                qm_executable = self.session.seqcrow_settings.settings.PSI4_EXE

        if self.file_type.lower() == "q-chem":
            qm_executable = os.path.abspath(
                self.session.seqcrow_settings.settings.QCHEM_EXE
            )
            if not os.path.exists(qm_executable):
                qm_executable = self.session.seqcrow_settings.settings.QCHEM_EXE
        
        self.write_file(
            os.path.join(self.scratch_dir, "%s.ini" % self.name),
            **self.algorithm_kwargs
        )
        self.input_files.append(os.path.join(self.scratch_dir, "raven.json"))
        
        self.output_name = os.path.join(
            self.scratch_dir, "path.xyz"
        )
        
        args = [
            python_exe, "-m",
            "Raven", "serial", "executable", qm_executable, "%s.ini" % self.name,
        ]
        if self.algorithm_kwargs["restart"]:
            args.extend(["restart", self.algorithm_kwargs["restart"]])
        
        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))
        log.flush()

        if platform == "win32":
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log)

        self.process.communicate()
        self.process = None

        self.output_name = []
        for f in os.listdir(self.scratch_dir):
            # if not any(f.startswith(s) for s in ["ts", "min"]):
            #     continue
            if f.endswith("xyz"):
                self.output_name.append(os.path.join(self.scratch_dir, f))

        if self.job_options.get("delete_everything_but_output_file", False):
            self.remove_extra_files()

    def get_json(self):
        d = super().get_json()
        d["format"] = "Raven"
        d["file_type"] = self.file_type
        return d


class ParallelRavenJob(ClusterTSSJob):
    format_name = "xyz"

    def __repr__(self):
        return "local cluster %s job \"%s\"" % (
            self.info_type, self.name
        )
    
    def run(self):
        from sys import executable as python_exe
        
        import Raven
        
        from chimerax.core.commands import run
        from SEQCROW.residue_collection import ResidueCollection
        
        raven_path = os.path.dirname(Raven.__file__)
        raven_exe = os.path.join(raven_path, "bin", "raven.py")
        
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR),
            "%s_%s" % (self.name, self.start_time.replace(':', '.').replace(" ", "_")),
        )
        
        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        extra_kwargs = {
            "Job": {
                "queue_type": self.queue_type,
                "wall": self.walltime,
                "memory": self.memory,
            }
        }

        self.write_file(
            os.path.join(self.scratch_dir, "%s.ini" % self.name),
            **extra_kwargs, **self.algorithm_kwargs
        )

        job_file = os.path.join(self.scratch_dir, "%s.job" % self.name)
        with open(job_file, "w") as f:
            if not isinstance(self.template, Template):
                self.template = Template(self.template)
            tm = self.template.render(**self.template_kwargs)
            f.write(tm)

        self.output_name = os.path.join(
            self.scratch_dir, "path.xyz"
        )
        
        args = [
            python_exe, "-m",
            "Raven", "parallel", "%s.ini" % self.name, "template", job_file,
        ]
        if self.algorithm_kwargs["restart"]:
            args.extend(["restart", self.algorithm_kwargs["restart"]])
        
        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))
        log.flush()

        if platform == "win32":
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log)

        self.process.communicate()
        self.process = None

        self.output_name = []
        for f in os.listdir(self.scratch_dir):
            # if not any(f.startswith(s) for s in ["ts", "min"]):
            #     continue
            if f.endswith("xyz"):
                self.output_name.append(os.path.join(self.scratch_dir, f))
    
    def kill(self):
        self.session.logger.warning("killing %s..." % self)

        if self.isRunning():
            self.session.logger.warning(
                "stopping cluster jobs is not implemented; no new jobs will start, but running jobs will finish"
            )
            
            self.to_kill = True
        else:
            self.killed = True
       
        #use exit b/c terminate can cause chimera to freeze
        super().exit(1)
    
    def get_json(self):
        d = super().get_json()
        d.pop("geometry")
        d["format"] = "Raven"
        d["reactant"] = self.reactant
        d["product"] = self.product
        d["raven_kwargs"] = self.raven_kwargs
        return d


class GaussianSTQNJob(TSSJob):
    tss_algorithm = "synchornous transit-guided quasi-Newton"
    format_name = "log"
    
    def __repr__(self):
        return "local ORCA QST job \"%s\"" % self.name

    def run(self):
        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
            "%s %s" % (self.name, self.start_time.replace(':', '.')), \
        )
        
        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        if platform == "win32":
            infile = self.name + '.gjf'
        else:
            infile = self.name + '.com'

        infile_path = os.path.join(self.scratch_dir, infile)
        self.write_file(infile_path)

        executable = os.path.abspath(self.session.seqcrow_settings.settings.GAUSSIAN_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.GAUSSIAN_EXE
            
        self.output_name = os.path.join(self.scratch_dir, self.name + '.log')
        
        args = [executable, infile, self.output_name]
        
        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        try:
            if platform == "win32":
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log)
        except FileNotFoundError:
            self.session.logger.error(
                "job could not start because Gaussian executable (%s) was not found\n" % executable +
                "ensure the correct path to executable is specified in the \"SEQCROW Jobs\"\n" +
                "settings in Favorites/Preferences > Settings..."
            )
            return

        self.process.communicate()
        self.process = None

        if self.job_options.get("delete_everything_but_output_file", False):
            self.remove_extra_files()

        return 
    
    def get_json(self):
        d = super().get_json()
        d["format"] = "Gaussian STQN"
        return d


class ORCANEBJob(TSSJob):
    tss_algorithm = "nudged elastic band"
    format_name = "out"

    def __repr__(self):
        return "local ORCA NEB job \"%s\"" % self.name

    def run(self):
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR),
            "%s %s" % (self.name, self.start_time.replace(':', '.')),
        )

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        self.theory.geometry = self.reactant
        self.product.write(
            outfile=os.path.join(self.scratch_dir, "product.xyz"),
        )
        infile = self.name + '.inp'
        infile = infile.replace(' ', '_')
        infile_path = os.path.join(self.scratch_dir, infile)
        self.write_file(infile_path)
        executable = os.path.abspath(self.session.seqcrow_settings.settings.ORCA_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.ORCA_EXE

        self.output_name = os.path.join(self.scratch_dir, self.name.replace(' ', '_') + '.out')
        outfile = open(self.output_name, 'w')

        args = [executable, infile]

        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        log.close()
        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'a')

        if " " in infile:
            raise RuntimeError("ORCA input files cannot contain spaces")

        try:
            if platform == "win32":
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
            else:        
                self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log)
        except FileNotFoundError:
            self.session.logger.error(
                "job could not start because ORCA executable (%s) was not found\n" % executable +
                "ensure the correct path to executable is specified in the \"SEQCROW Jobs\"\n" +
                "settings in Favorites/Preferences > Settings..."
            )
            return
            
        self.process.communicate()
        self.process = None

        if self.job_options.get("delete_everything_but_output_file", False):
            self.remove_extra_files()

        return 
    
    def get_json(self):
        d = super().get_json()
        d["format"] = "ORCA NEB"
        return d


class QChemFSMJob(TSSJob):
    tss_algorithm = "freezing string method"
    format_name = "out"

    def __repr__(self):
        return "local Q-Chem FSM job \"%s\"" % self.name

    def run(self):
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
            "%s %s" % (self.name, self.start_time.replace(':', '.')), \
        )

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        infile = self.name.replace(" ", "_") + '.inp'
        infile_path = os.path.join(self.scratch_dir, infile)
        self.write_file(infile_path)

        executable = os.path.abspath(self.session.seqcrow_settings.settings.QCHEM_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.QCHEM_EXE

        self.output_name = os.path.join(self.scratch_dir, self.name.replace(" ", "_") + '.out')
        outfile = open(self.output_name, 'w')

        args = [
            executable,
            "-nt %i" % self.theory.processors,
            infile,
        ]

        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        try:
            if platform == "win32":
                self.process = subprocess.Popen(
                    args, cwd=self.scratch_dir, stdout=outfile, stderr=log,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.process = subprocess.Popen(
                    args, cwd=self.scratch_dir, stdout=outfile, stderr=log
                )
        except FileNotFoundError:
            self.session.logger.error(
                "job could not start because Q-Chem executable (%s) was not found\n" % executable +
                "ensure the correct path to executable is specified in the \"SEQCROW Jobs\"\n" +
                "settings in Favorites/Preferences > Settings..."
            )
            return
            
        self.process.communicate()
        self.process = None

        if self.job_options.get("delete_everything_but_output_file", False):
            self.remove_extra_files()

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "Q-Chem FSM"
        return d

