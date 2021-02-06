import os
import subprocess
from time import asctime, localtime

from Qt.QtCore import QThread, Signal

from SEQCROW.theory import SEQCROW_Theory

from AaronTools.theory import Theory


from sys import platform

class LocalJob(QThread):
    format_name = None
    """name of format for open command"""
    def __init__(self, name, session, theory, kw_dict={}, auto_update=False, auto_open=False):
        """base class of local ORCA, Gaussian, and Psi4 jobs
        name        str - name of job
        session     chimerax session object
        theory      SEQCROW.theory.SEQCROW_Theory or a dictionary with a saved job's settings
        kw_dict     dictionary - everything that isn't in self.theory (not used if theory is a dict)
        """
        self.name = name
        self.session = session
        self.theory = theory
        self.kw_dict = kw_dict
        self.auto_update = auto_update
        self.auto_open = auto_open
        self.killed = False
        self.error = False
        
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
        if isinstance(self.theory, Theory):
            self.theory.geometry.write(theory=self.theory, outfile=infile_path, style="orca", **self.kw_dict)
        else:
            SEQCROW_Theory.orca_input_from_dict(self.theory, infile_path)

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
        if self.start_time is None:
            #we don't need to keep the theory stuff around if the job has started
            if isinstance(self.theory, Theory):
                d = SEQCROW_Theory.get_orca_json(self.theory, **self.kw_dict)
            else:
                d = self.theory.copy()
        else:
            d = {}
            d['output'] = self.output_name
            d['scratch'] = self.scratch_dir

        d['server'] = 'local'
        d['start_time'] = self.start_time
        d['name'] = self.name
        d['format'] = "ORCA"
        d['depend'] = None
        d['auto_update'] = False
        d['auto_open'] = self.auto_open or self.auto_update

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
        if isinstance(self.theory, Theory):
            self.theory.geometry.write(theory=self.theory, outfile=infile_path, style="gaussian", **self.kw_dict)
        else:
            SEQCROW_Theory.gaussian_input_from_dict(self.theory, infile_path)
            
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
        if self.start_time is None:
            #we don't need to keep the theory stuff around if the job has started
            if isinstance(self.theory, Theory):
                d = SEQCROW_Theory.get_gaussian_json(self.theory, **self.kw_dict)
            else:
                d = self.theory.copy()

        else:
            d = {}
            d['output'] = self.output_name
            d['scratch'] = self.scratch_dir
        
        d['server'] = 'local'
        d['start_time'] = self.start_time
        d['name'] = self.name
        d['format'] = "Gaussian"
        d['depend'] = None
        d['auto_update'] = False
        d['auto_open'] = self.auto_open or self.auto_update

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
        if isinstance(self.theory, Theory):
            self.theory.geometry.write(theory=self.theory, outfile=infile_path, style="psi4", **self.kw_dict)
        else:
            SEQCROW_Theory.psi4_input_from_dict(self.theory, infile_path)

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
        if self.start_time is None:
            #we don't need to keep the theory stuff around if the job has started
            if isinstance(self.theory, Theory):
                d = SEQCROW_Theory.get_psi4_json(self.theory, **self.kw_dict)
            else:
                d = self.theory.copy()

        else:
            d = {}
            d['output'] = self.output_name
            d['scratch'] = self.scratch_dir

        d['server'] = 'local'
        d['start_time'] = self.start_time
        d['name'] = self.name
        d['format'] = "Psi4"
        d['depend'] = None
        d['auto_update'] = False
        d['auto_open'] = self.auto_open or self.auto_update

        return d
