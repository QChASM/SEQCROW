import os
import subprocess

from PyQt5.QtCore import QThread, pyqtSignal

from time import asctime, localtime

class LocalJob(QThread):
    def __init__(self, name, session, theory, kw_dict):
        self.name = name
        self.session = session
        self.theory = theory
        self.kw_dict = kw_dict
        
        self.process = None
        self.started = False
        self.start_time = None
        
        super().__init__()
        
    def kill(self):
        if self.process is not None:
            self.process.terminate()
    
    def run(self):
        """overwrite to execute job"""
        pass


class ORCAJob(LocalJob):
    def __repr__(self):
        return "local ORCA job %s" % self.name

    def run(self):
        self.started = True
        self.start_time = asctime(localtime())
        
        scratch_dir = os.path.join(
                        os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
                        "%s %s" % (self.name, self.start_time.replace(':', '.')), \
                    )
        
        scratch_dir = scratch_dir.replace(' ', '_')
        
        cwd = os.getcwd()
        
        if not os.path.exists(scratch_dir):
            os.makedirs(scratch_dir)

        infile = self.name + '.inp'
        self.theory.write_orca_input(self.kw_dict, os.path.join(scratch_dir, infile))

        executable = os.path.abspath(self.session.seqcrow_settings.settings.ORCA_EXE)
        outfile = open(os.path.join(scratch_dir, self.name + '.out'), 'w')
        
        args = [executable, infile]
        
        log = open(os.path.join(scratch_dir, "seqcrow_log.txt"), 'w')
        log.write("executing:\n%s\n\n" % " ".join(args))

        if " " in infile:
            raise RuntimeError("ORCA input files cannot contain spaces")

        try:
            self.process = subprocess.Popen(args, cwd=scratch_dir, stdout=outfile, stderr=log)
            self.process.communicate()

        except:
            self.process = None

        print("finished")

        return 


class GaussianJob(LocalJob):
    def run(self):
        self.start_time = asctime(localtime())
        
        scratch_dir = os.path.join(
                        self.session.seqcrow_settings.settings.SCRATCH_DIR, \
                        "%s %s" % (self.name, self.start_time.replace(':', '.')), \
                    )
        
        cwd = os.getcwd()
        
        if not os.path.exists(scratch_dir):
            os.makedirs(scratch_dir)
            
        os.chdir(scratch_dir)

        self.theory.write_orca_input(self.kw_dict, self.name + '.inp')

        executable = self.session.seqcrow_settings.settings.ORCA_EXE
        infile = self.name
        outfile = os.path.splitext(infile)[0] + '.out'
        
        args = [executable, infile, '>', outfile]

        self.process = subprocess.Popen(args)

        try:
            stdout, stderr = self.process.communicate()
            self.process = None
            self.finished.emit()
            return (stdout, stderr)

        except Exception as e:
            self.finished.emit()
            return e


class Psi4Job(LocalJob):
    def run(self):
        self.start_time = asctime(localtime())
        
        scratch_dir = os.path.join(
                        self.session.seqcrow_settings.settings.SCRATCH_DIR, \
                        "%s %s" % (self.name, self.start_time.replace(':', '.')), \
                    )
        
        cwd = os.getcwd()
        
        if not os.path.exists(scratch_dir):
            os.makedirs(scratch_dir)
            
        os.chdir(scratch_dir)

        self.theory.write_orca_input(self.kw_dict, self.name + '.inp')

        executable = self.session.seqcrow_settings.settings.ORCA_EXE
        infile = self.name
        outfile = os.path.splitext(infile)[0] + '.out'
        
        args = [executable, infile, '>', outfile]

        self.process = subprocess.Popen(args)

        try:
            stdout, stderr = self.process.communicate()
            self.process = None
            self.finished.emit()
            return (stdout, stderr)

        except Exception as e:
            self.finished.emit()
            return e