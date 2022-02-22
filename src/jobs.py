from sys import platform
import os
import subprocess
from time import asctime, localtime, sleep

from AaronTools.fileIO import FileReader
from AaronTools.theory import OptimizationJob

from chimerax.core.commands import run

from Qt.QtCore import QThread

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.managers import ADD_FILEREADER


class SEQCROWSigKill(Exception):
    pass


class LocalJob(QThread):
    format_name = None
    info_type = None
    """job for running computational chemistry software on local hardware"""
    def __init__(
        self,
        name,
        session,
        theory,
        geometry=None,
        auto_update=False,
        auto_open=False,
    ):
        """base class of local ORCA, Gaussian, and Psi4 jobs
        name        str - name of job
        session     chimerax session object
        theory      AaronTools.theory.Theory or a dictionary with a saved job's settings
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
        input_info = self.session.seqcrow_qm_input_manager.get_info(self.info_type)
        contents, warnings = input_info.get_file_contents(self.theory)
        if isinstance(contents, dict):
            name, ext = os.path.splitext(outname)
            for key, item in contents.items():
                fname = name + ".%s" % key
                outname = os.path.basename(fname)
                item = item.replace("{{ name }}", name)
                with open(fname, "w") as f:
                    f.write(item)
        else:
            outname = os.path.basename(filename)
            name, ext = os.path.splitext(outname)
            contents = contents.replace("{{ name }}", name)
            with open(filename, "w") as f:
                f.write(contents)
    
    def get_json(self):
        from AaronTools.geometry import Geometry

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
        if isinstance(self.output_name, str):
            fr = FileReader(self.output_name, just_geom=False, all_geom=True)
            rescol = ResidueCollection(fr)
            residue_collection.update_chix(structure)
            self.session.filereader_manager.triggers.activate_trigger(
                ADD_FILEREADER, ([structure], [fr])
            )
        elif hasattr(self.output_name, "__iter__"):
            for file in self.output_name:
                fr = FileReader(self.output_name, just_geom=False, all_geom=True)
                rescol = ResidueCollection(fr)
                residue_collection.update_chix(structure)
                self.session.filereader_manager.triggers.activate_trigger(
                    ADD_FILEREADER, ([structure], [fr])
                )

    def open_structure(self):
        if isinstance(self.output_name, str):
            args = ["open", "\"%s\"" % self.output_name, "format", self.format_name]
            if self.theory.job_type and any(
                isinstance(job, OptimizationJob) for job in self.theory.job_type
            ):
                args.extend(["coordsets", "true"])
            run(self.session, " ".join(args))
        
        elif hasattr(self.output_name, "__iter__"):
            for file in self.output_name:
                run(self.session, "open \"%s\"" % file)


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
    info_type = "Gaussian"
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

        if platform == "win32":
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log)

        possible_fchk_name = os.path.join(
            self.scratch_dir, self.name + ".fchk"
        )
        if os.path.exists(possible_fchk_name):
            self.output_name = [
                self.output_name,
                possible_fchk_name
            ]

        self.process.communicate()
        self.process = None

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

        if platform == "win32":
            self.process = subprocess.Popen(
                args, cwd=self.scratch_dir, stdout=outfile, stderr=log,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            self.process = subprocess.Popen(
                args, cwd=self.scratch_dir, stdout=outfile, stderr=log
            )

        self.process.communicate()
        self.process = None

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "Q-Chem"
        return d


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

        infile = self.name.replace(" ", "_") + "." + self.cluster_type.expected_input_ext
        outfile = self.name.replace(" ", "_") + "." + self.cluster_type.expected_output_ext
        infile_path = os.path.join(self.scratch_dir, infile)
        self.output_name = os.path.join(self.scratch_dir, outfile)

        self.write_file(infile_path)
        self.cluster_type.submit_job(
            infile_path,
            self.walltime,
            self.processors,
            self.memory,
            template=self.template,
            template_kwargs=self.template_kwargs,
        )

        return 
    
    def kill(self):
        self.session.logger.warning("killing %s..." % self)

        if self.process is not None:
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


class SerialRavenJob(LocalJob):
    info_type = "Raven"
    format_name = "xyz"
    
    def __init__(
        self,
        name,
        session,
        theory,
        reactant,
        product,
        file_type,
        tss_algorithm,
        auto_update=False,
        auto_open=False,
        **raven_kwargs
    ):
        super().__init__(
            name, session, theory,
            auto_open=auto_open, auto_update=auto_update
        )
        self.reactant = reactant
        self.product = product
        self.file_type = file_type
        self.raven_kwargs = raven_kwargs
        self.to_kill = False
    
    def __repr__(self):
        return "serial %s job using %s \"%s\"" % (
            self.info_type, self.file_type, self.name
        )
    
    def run(self):
        from Raven.job_runner import SerialJobRunner
        from Raven.driver import RavenDriver
        from chimerax.core.commands import run
        from SEQCROW.residue_collection import ResidueCollection
        
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
        
        self.output_name = os.path.join(
            self.scratch_dir, "path.xyz"
        )

        job_runner = SerialJobRunner(
            self.file_type,
            qm_executable,
        )
        
        def log_func(s, outfile=os.path.join(self.scratch_dir, "seqcrow_log.txt")):
            with open(outfile, "a") as f:
                f.write(s + "\n")
        
        def seqcrow_killed(obj=self):
            if self.to_kill:
                raise SEQCROWSigKill("kill")
        
        try:
            driver = RavenDriver(
                self.reactant,
                self.product,
                self.theory,
                cwd=self.scratch_dir,
                nodes=self.raven_kwargs["nodes"],
                restart=self.raven_kwargs["restart"],
                kernel=self.raven_kwargs["kernel"],
                similarity_falloff=self.raven_kwargs["similarity_falloff"],
                log_func=log_func,
            )
            driver.optimize_string(
                self.raven_kwargs["rms_force_tol"],
                self.raven_kwargs["max_force_tol"],
                job_runner,
                variance_threshold=self.raven_kwargs["variance_threshold"],
                callback=seqcrow_killed,
            )
            driver.print_stationary_points()
        except SEQCROWSigKill:
            self.killed = True
            return
        
        self.output_name = []
        for f in os.listdir(self.scratch_dir):
            if f.endswith("xyz"):
                self.output_name.append(os.path.join(self.scratch_dir, f))
    
    def kill(self):
        self.session.logger.warning("killing %s..." % self)

        if self.isRunning():
            self.session.logger.warning(
                "the current iteration will finish"
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
        d["file_type"] = self.file_type
        d["raven_kwargs"] = self.raven_kwargs
        return d


class ParallelRavenJob(LocalClusterJob):
    format_name = "xyz"
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
        reactant,
        product,
        tss_algorithm,
        queue_type,
        auto_update=False,
        auto_open=False,
        template=None,
        walltime=2,
        processors=4,
        memory=8,
        template_kwargs=None,
        **raven_kwargs,
    ):
        """
        base class of local ORCA, Gaussian, and Psi4 cluster jobs
        name        str - name of job
        session     chimerax session object
        theory      AaronTools.theory.Theory or a dictionary with a saved job's settings
        """
        super().__init__(
            name,
            session,
            theory,
            file_type,
            queue_type=queue_type,
            auto_update=auto_update,
            auto_open=auto_open,
            template=template,
            walltime=walltime,
            processors=processors,
            memory=memory,
            template_kwargs=template_kwargs,
        )

        self.reactant = reactant
        self.product = product
        self.raven_kwargs = raven_kwargs
        self.to_kill = False

    def __repr__(self):
        return "local cluster %s job \"%s\"" % (
            self.info_type, self.name
        )
    
    def run(self):
        from Raven.job_runner import ParallelClusterJobRunner
        from Raven.driver import run_raven
        from chimerax.core.commands import run
        from SEQCROW.residue_collection import ResidueCollection
        
        self.start_time = asctime(localtime()).replace(" ", "_")
        
        self.scratch_dir = os.path.join(
            os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR), \
            "%s_%s" % (self.name, self.start_time.replace(':', '.')), \
        )
        
        if not os.path.exists(self.scratch_dir):
            os.makedirs(self.scratch_dir)

        exec_memory = self.memory
        if not exec_memory:
            exec_memory = self.theory.memory
        if not exec_memory:
            raise ValueError("memory must be non-zero for cluster jobs")

        walltime = self.walltime
        
        job_runner = ParallelClusterJobRunner(
            self.info_type,
            memory=exec_memory,
            walltime=self.walltime,
            template=self.template,
            wait=90,
            **self.template_kwargs,
        )

        self.output_name = os.path.join(
            self.scratch_dir, "path.xyz"
        )
        
        def log_func(s, outfile=os.path.join(self.scratch_dir, "seqcrow_log.txt")):
            with open(outfile, "a") as f:
                f.write(s + "\n")
        
        def seqcrow_killed(obj=self):
            if self.to_kill:
                raise SEQCROWSigKill("kill")
        
        try:
            driver = RavenDriver(
                self.reactant,
                self.product,
                self.theory,
                cwd=self.scratch_dir,
                nodes=self.raven_kwargs["nodes"],
                restart=self.raven_kwargs["restart"],
                kernel=self.raven_kwargs["kernel"],
                similarity_falloff=self.raven_kwargs["similarity_falloff"],
                log_func=log_func,
            )
            driver.optimize_string(
                self.raven_kwargs["rms_force_tol"],
                self.raven_kwargs["max_force_tol"],
                job_runner,
                variance_threshold=self.raven_kwargs["variance_threshold"],
                callback=seqcrow_killed,
            )
            driver.print_stationary_points()
        except SEQCROWSigKill:
            self.killed = True
            return

        self.output_name = []
        for f in os.listdir(self.scratch_dir):
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


class TSSJob(LocalJob):    
    def __init__(
        self,
        name,
        session,
        theory,
        reactant,
        product,
        file_type,
        tss_algorithm,
        auto_update=False,
        auto_open=False,
    ):
        super().__init__(
            name, session, theory,
            auto_open=auto_open, auto_update=auto_update
        )
        self.reactant = reactant
        self.product = product
        self.file_type = file_type
        self.tss_algorithm = tss_algorithm

    def write_file(self, filename):
        input_info = self.session.tss_finder_manager.get_info(
            self.tss_algorithm
        )
        if input_info.get_file_contents:
            if callable(input_info.get_file_contents):
                contents, warnings = input_info.get_file_contents(
                    self.reactant, self.product, self.theory,
                )
            else:
                contents, warnings = input_info.get_file_contents[
                    self.file_type
                ](self.reactant, self.product, self.theory)

        else:
            file_info = self.session.seqcrow_qm_input_manager.get_info(
                self.file_type
            )
        contents, warnings = file_info.get_file_contents(self.theory)

        if isinstance(contents, dict):
            name, ext = os.path.splitext(outname)
            for key, item in contents.items():
                fname = name + ".%s" % key
                outname = os.path.basename(fname)
                item = item.replace("{{ name }}", name)
                with open(fname, "w") as f:
                    f.write(item)
        else:
            outname = os.path.basename(filename)
            name, ext = os.path.splitext(outname)
            contents = contents.replace("{{ name }}", name)
            with open(filename, "w") as f:
                f.write(contents)
    
    def get_json(self):
        d = super().get_json()
        d.pop("geometry")
        d["reactant"] = self.reactant
        d["product"] = self.product
        d["file_type"] = self.file_type
        return d


class GaussianSTQNJob(TSSJob):
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

        if platform == "win32":
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=log, stderr=log)

        self.process.communicate()
        self.process = None

        return 
    
    def get_json(self):
        d = super().get_json()
        d["format"] = "Gaussian STQN"
        return d


class ORCANEBJob(TSSJob):
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

        if platform == "win32":
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        else:        
            self.process = subprocess.Popen(args, cwd=self.scratch_dir, stdout=outfile, stderr=log)

        self.process.communicate()
        self.process = None

        return 
    
    def get_json(self):
        d = super().get_json()
        d["format"] = "ORCA NEB"
        return d


class QChemFSMJob(TSSJob):
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

        if platform == "win32":
            self.process = subprocess.Popen(
                args, cwd=self.scratch_dir, stdout=outfile, stderr=log,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            self.process = subprocess.Popen(
                args, cwd=self.scratch_dir, stdout=outfile, stderr=log
            )

        self.process.communicate()
        self.process = None

        return 

    def get_json(self):
        d = super().get_json()
        d["format"] = "Q-Chem FSM"
        return d


class ClusterTSSJob(TSSJob):
    def __init__(
        self,
        name,
        session,
        theory,
        reactant,
        product,
        file_type,
        tss_algorithm,
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
            name, session, theory,
            auto_open=auto_open, auto_update=auto_update
        )
        self.reactant = reactant
        self.product = product
        self.file_type = file_type
        self.tss_algorithm = tss_algorithm
        self.name = name
        self.session = session
        self.theory = theory
        
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
   
    def get_json(self):
        d = super().get_json()
        d.pop("geometry")
        d["reactant"] = self.reactant
        d["product"] = self.product
        d["file_type"] = self.file_type

        d = {
            "theory": self.theory,
        }

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
    
