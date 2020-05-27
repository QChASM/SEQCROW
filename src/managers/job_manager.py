import os

from AaronTools.fileIO import FileReader

from chimerax.core.toolshed import ProviderManager
from chimerax.core.triggerset import TriggerSet
from chimerax.core.commands import run

from SEQCROW.jobs import LocalJob, GaussianJob, ORCAJob, Psi4Job
from SEQCROW.managers import FILEREADER_ADDED
from SEQCROW.residue_collection import ResidueCollection

from PyQt5.QtCore import QThread

JOB_FINISHED = "job finished"
JOB_STARTED = "job started"
JOB_QUEUED = "job added"

class JobManager(ProviderManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.local_jobs = []
        self.remote_jobs = []
        self.paused = False
        self._thread = None

        self.triggers = TriggerSet()
        self.triggers.add_trigger(JOB_FINISHED)
        self.triggers.add_handler(JOB_FINISHED, self.job_finished)
        self.triggers.add_trigger(JOB_STARTED)
        self.triggers.add_handler(JOB_STARTED, self.job_started)
        self.triggers.add_trigger(JOB_QUEUED)
        self.triggers.add_handler(JOB_QUEUED, self.check_queue)
    
    def __setattr__(self, attr, val):
        if attr == "paused":
            if val:
                print("paused SEQCROW queue")
            else:
                print("unpaused SEQCROW queue")
        
        super().__setattr__(attr, val)
    
    @property
    def jobs(self):
        return self.local_jobs + self.remote_jobs
        
    @property
    def has_job_running(self):
        if self._thread is None:
            return False
        else:
            return self._thread.isRunning()
    
    def add_provider(self):
        self._thread = None

    def job_finished(self, trigger_name, job):
        print("%s: %s" % (trigger_name, job))
        if isinstance(job, LocalJob):
            self._thread = None

        if job.auto_update and not job.theory.structure.deleted:
            if os.path.exists(job.output_name):
                finfo = job.output_name
                if isinstance(job, GaussianJob):
                    finfo = (job.output_name, "com", None)                
                elif isinstance(job, ORCAJob):
                    finfo = (job.output_name, "out", None)                
                elif isinstance(job, Psi4Job):
                    #coming eventually...
                    finfo = (job.output_name, "dat", None)
                    
                fr = FileReader(finfo, get_all=True, just_geom=False)
                
                job.session.filereader_manager.triggers.activate_trigger(FILEREADER_ADDED, ([job.theory.structure], [fr]))

                rescol = ResidueCollection(fr, refresh_connected=True)
                rescol.update_chix(job.theory.structure)
            
            if fr.all_geom is not None and len(fr.all_geom) > 1:
                coordsets = rescol.all_geom_coordsets(fr)

                job.theory.structure.remove_coordsets()
                job.theory.structure.add_coordsets(coordsets)

                for i, coordset in enumerate(coordsets):
                    job.theory.structure.active_coordset_id = i + 1
                    
                    for atom, coord in zip(job.theory.structure.atoms, coordset):
                        atom.coord = coord
                
                job.theory.structure.active_coordset_id = job.theory.structure.num_coordsets

        elif job.auto_open:
            run(job.session, "open \"%s\"" % job.output_name, log=False)
            
        self.check_queue()
        pass
    
    def job_started(self, trigger_name, job):
        print("%s: %s" % (trigger_name, job))
        pass
    
    def add_job(self, job):
        if isinstance(job, LocalJob):
            self.local_jobs.append(job)
            self.triggers.activate_trigger(JOB_QUEUED, job)
            
    def check_queue(self, *args):
        if not self.has_job_running:
            unstarted_local_jobs = []
            for job in self.local_jobs:
                if job.start_time is None and not job.killed:
                    unstarted_local_jobs.append(job)
                    
            if len(unstarted_local_jobs) > 0 and not self.paused:
                start_job = unstarted_local_jobs.pop(0)

                self._thread = start_job
                start_job.finished.connect(lambda data=start_job: self.triggers.activate_trigger(JOB_FINISHED, data))
                start_job.started.connect(lambda data=start_job: self.triggers.activate_trigger(JOB_STARTED, data))
                start_job.start()

            else:
                self._thread = None