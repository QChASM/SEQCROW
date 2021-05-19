import os
import subprocess
from time import asctime, localtime

from PyQt5.QtCore import QThread

from SEQCROW.theory import SEQCROW_Theory

from AaronTools.theory import Theory
from AaronTools.geometry import Geometry


from sys import platform

class LocalJob(QThread):
    format_name = None
    """name of format for open command"""
    def __init__(self, name, session, theory, geometry=None, auto_update=False, auto_open=False):
        """base class of local ORCA, Gaussian, and Psi4 jobs
        name        str - name of job
        session     chimerax session object
        theory      SEQCROW.theory.SEQCROW_Theory or a dictionary with a saved job's settings
        """
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
        
        super().__init__()

    def kill(self):
        self.session.logger.warning("killing %s..." % self)

        if self.process is not None:
            self.process.kill()
            self.process.wait()
            self.session.logger.warning("%s might finish an in-progess calculation step before exiting" % self)
        
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
    
    def get_json(self):
        d = {
            "theory": self.theory,
            "geometry": Geometry(self.theory.geometry),
        }

        d['output'] = self.output_name
        d['scratch'] = self.scratch_dir

        d['server'] = 'local'
        d['start_time'] = self.start_time
        d['name'] = self.name
        d['depend'] = None
        d['auto_update'] = False
        d['auto_open'] = self.auto_open or self.auto_update

        return d

    def update_structure(self, structure):
        """
        overwrite to update structure (AtomicStructure) with the
        coordinates from this job's output file
        required for "update structure" option to work when launching
        a job if the output file is not parsable by AaronTools
        """
        raise NotImplementedError(
            "no update_structure method for %s" % (
                self.__class__.name
            )
        )


class ORCAJob(LocalJob):
    format_name = "out"
    def __repr__(self):
        return "local ORCA job \"%s\"" % self.name

    def run(self):
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR),
            "%s %s" % (self.name, self.start_time.replace(':', '.')),
        )

        cwd = os.getcwd()

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        infile = self.name + '.inp'
        infile = infile.replace(' ', '_')
        infile_path = os.path.join(self.scratch_dir, infile)
        self.theory.geometry.write(theory=self.theory, outfile=infile_path, style="orca")

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

        if platform == "win32":
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        else:        
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log)

        self.process.communicate()
        self.process = None

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "ORCA"
        return d


class GaussianJob(LocalJob):
    format_name = "log"
    def __repr__(self):
        return "local Gaussian job \"%s\"" % self.name

    def run(self):
        self.start_time = asctime(localtime())
        
        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
            "%s %s" % (self.name, self.start_time.replace(':', '.')), \
        )

        cwd = os.getcwd()
        
        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        if platform == "win32":
            infile = self.name + '.gjf'
        else:
            infile = self.name + '.com'

        infile_path = os.path.join(self.scratch_dir, infile)
        self.theory.geometry.write(theory=self.theory, outfile=infile_path, style="gaussian")

        executable = os.path.abspath(self.session.seqcrow_settings.settings.GAUSSIAN_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.GAUSSIAN_EXE
            
        self.output_name = os.path.join(self.scratch_dir, self.name + '.log')
        
        args = [executable, infile, self.output_name]
        
        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        if platform == "win32":
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log)

        self.process.communicate()
        self.process = None

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "Gaussian"
        return d


class Psi4Job(LocalJob):
    format_name = "dat"
    def __repr__(self):
        return "local Psi4 job \"%s\"" % self.name

    def run(self):
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
            "%s %s" % (self.name, self.start_time.replace(':', '.')), \
        )

        cwd = os.getcwd()

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        infile = self.name + '.in'
        infile_path = os.path.join(self.scratch_dir, infile)
        self.theory.geometry.write(theory=self.theory, outfile=infile_path, style="psi4")

        executable = os.path.abspath(self.session.seqcrow_settings.settings.PSI4_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.PSI4_EXE

        self.output_name = os.path.join(self.scratch_dir, self.name + '.out')

        args = [executable, infile, self.output_name]

        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        if platform == "win32":
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log)

        self.process.communicate()
        self.process = None

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "Psi4"
        return d


class SQMJob(LocalJob):
    format_name = "sqmout"

    def __repr__(self):
        return "local sqm job \"%s\"" % self.name

    def run(self):
        import sys
        self.start_time = asctime(localtime())

        self.scratch_dir = os.path.join(
                        os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
                        "%s %s" % (self.name, self.start_time.replace(':', '.')), \
                    )

        cwd = os.getcwd()

        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        infile = self.name + '.mdin'
        infile_path = os.path.join(self.scratch_dir, infile)
        self.theory.geometry.write(theory=self.theory, outfile=infile_path, style="sqm")

        exec_dir = os.path.dirname(sys.executable)
        sqm_exe = os.path.join(exec_dir, "amber20", "bin", "sqm")
        if not os.path.exists(sqm_exe):
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

    def get_json(self):
        d = super().get_json()
        d["format"] = "SQM"
        return d
