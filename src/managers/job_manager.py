from chimerax.core.toolshed import ProviderManager
from chimerax.core.triggerset import TriggerSet
from chimerax.core.commands import run

from SEQCROW.jobs import LocalJob

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

        if job.auto_open:
            run(job.session, "open \"%s\"" % job.output_name, log=False)
        elif job.auto_update:
            print("auto update isn't done")
            pass
            
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
                if not job.started:
                    unstarted_local_jobs.append(job)
                    
            if len(unstarted_local_jobs) > 0 and not self.paused:
                start_job = unstarted_local_jobs.pop(0)

                self._thread = start_job
                start_job.finished.connect(lambda data=start_job: self.triggers.activate_trigger(JOB_FINISHED, data))
                start_job.start()
                self.triggers.activate_trigger(JOB_STARTED, start_job)

            else:
                self._thread = None