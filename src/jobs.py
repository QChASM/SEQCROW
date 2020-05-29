import os
import subprocess

from PyQt5.QtCore import QThread, pyqtSignal

from time import asctime, localtime

from sys import platform

class LocalJob(QThread):
    def __init__(self, name, session, theory, kw_dict, auto_update=False, auto_open=False):
        self.name = name
        self.session = session
        self.theory = theory
        self.kw_dict = kw_dict
        self.auto_update = auto_update
        self.auto_open = auto_open
        self.killed = False
        
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
    def __repr__(self):
        return "local ORCA job \"%s\"" % self.name

    def run(self):
        self.start_time = asctime(localtime())
        
        self.scratch_dir = os.path.join(
                        os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
                        "%s %s" % (self.name, self.start_time.replace(':', '.')), \
                    )

        cwd = os.getcwd()
        
        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        infile = self.name + '.inp'
        infile = infile.replace(' ', '_')
        self.theory.write_orca_input(self.kw_dict, os.path.join(self.scratch_dir, infile))

        executable = os.path.abspath(self.session.seqcrow_settings.settings.ORCA_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.ORCA_EXE
            
        self.output_name = os.path.join(self.scratch_dir, self.name.replace(' ', '_') + '.out')
        outfile = open(self.output_name, 'w')
        
        args = [executable, infile]
        
        log = open(os.path.join(self.scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        if " " in infile:
            raise RuntimeError("ORCA input files cannot contain spaces")

        if platform == "win32":
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        else:        
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log)
        
        self.process.communicate()
        self.process = None

        return 


class GaussianJob(LocalJob):
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

        infile = self.name + '.gjf'
        self.theory.write_gaussian_input(self.kw_dict, os.path.join(self.scratch_dir, infile))

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


class Psi4Job(LocalJob):
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

        infile = self.name + '.in4'
        self.theory.write_psi4_input(self.kw_dict, os.path.join(self.scratch_dir, infile))

        executable = os.path.abspath(self.session.seqcrow_settings.settings.PSI4_EXE)
        if not os.path.exists(executable):
            executable = self.session.seqcrow_settings.settings.PSI4_EXE

        self.output_name = os.path.join(self.scratch_dir, self.name + '.dat')
        
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
