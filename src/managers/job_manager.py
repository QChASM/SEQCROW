import os

from AaronTools.fileIO import FileReader

from chimerax.core.toolshed import ProviderManager
from chimerax.core.triggerset import TriggerSet
from chimerax.core.commands import run

from json import load, dump

from PyQt5.QtWidgets import QMessageBox, QApplication

from SEQCROW.jobs import LocalJob, GaussianJob, ORCAJob, Psi4Job
from SEQCROW.managers import ADD_FILEREADER
from SEQCROW.residue_collection import ResidueCollection

JOB_FINISHED = "job finished"
JOB_STARTED = "job started"
JOB_QUEUED = "job changed"

class JobManager(ProviderManager):
    def __init__(self, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.session = session
        self.local_jobs = []
        self.remote_jobs = []
        self.unknown_status_jobs = []
        self.paused = False
        self._thread = None
        self.queue_dict = {}

        self.triggers = TriggerSet()
        self.triggers.add_trigger(JOB_FINISHED)
        self.triggers.add_handler(JOB_FINISHED, self.job_finished)
        self.triggers.add_trigger(JOB_STARTED)
        self.triggers.add_handler(JOB_STARTED, self.job_started)
        self.triggers.add_trigger(JOB_QUEUED)
        self.triggers.add_handler(JOB_QUEUED, self.check_queue)
        self.triggers.add_handler(JOB_QUEUED, self.write_json)
        self.session.triggers.add_handler('app quit', self.write_json)

    def __setattr__(self, attr, val):
        if attr == "paused":
            if val:
                print("paused SEQCROW queue")
            else:
                print("resumed SEQCROW queue")
        
        super().__setattr__(attr, val)

    @property
    def jobs(self):
        return self.local_jobs + self.remote_jobs

    @property
    def has_job_running(self):
        return any([job.isRunning() for job in self.local_jobs])

    def add_provider(self, *args, **kwargs):
        self._thread = None

    def init_queue(self):
        scr_dir = os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR)
        self.jobs_list_filename = os.path.join(scr_dir, "job_list-2.json")
        if os.path.exists(self.jobs_list_filename):
            with open(self.jobs_list_filename, 'r') as f:
                queue_dict = load(f)

            if 'check' in queue_dict:
                for job in queue_dict['check']:
                    if job['server'] == 'local':
                        if job['format'] == 'Psi4':
                            local_job = Psi4Job(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])

                        elif job['format'] == 'ORCA':
                            local_job = ORCAJob(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])

                        elif job['format'] == 'Gaussian':
                            local_job = GaussianJob(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])

                        if 'output' in job and os.path.exists(job['output']):
                            fr = FileReader(job['output'], just_geom=False)
                            if 'finished' in fr.other and fr.other['finished']:
                                local_job.isFinished = lambda *args, **kwargs: True
                            else:
                                local_job.isRunning = lambda *args, **kwargs: True
                                self.unknown_status_jobs.append(local_job)

                            local_job.output_name = job['output']
                            local_job.scratch_dir = job['scratch']

                        self.local_jobs.append(local_job)

            for job in queue_dict['queued']:
                if job['server'] == 'local':
                    if job['format'] == 'Psi4':
                        local_job = Psi4Job(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])
                    
                    elif job['format'] == 'ORCA':
                        local_job = ORCAJob(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])
                    
                    elif job['format'] == 'Gaussian':
                        local_job = GaussianJob(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])
                
                    self.local_jobs.append(local_job)
                    self.session.logger.info("added %s (%s job) from previous session" % (job['name'], job['format']))

            for job in queue_dict['finished']:
                if job['server'] == 'local':
                    if job['format'] == 'Psi4':
                        local_job = Psi4Job(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])
                        
                    elif job['format'] == 'ORCA':
                        local_job = ORCAJob(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])
                    
                    elif job['format'] == 'Gaussian':
                        local_job = GaussianJob(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])
                
                    #shh it's finished
                    local_job.isFinished = lambda *args, **kwargs: True
                    local_job.output_name = job['output']
                    local_job.scratch_dir = job['scratch']
                    self.local_jobs.append(local_job)

            if 'error' in queue_dict:
                for job in queue_dict['error']:
                    if job['server'] == 'local':
                        if job['format'] == 'Psi4':
                            local_job = Psi4Job(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])
                            
                        elif job['format'] == 'ORCA':
                            local_job = ORCAJob(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])
                        
                        elif job['format'] == 'Gaussian':
                            local_job = GaussianJob(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])
                    
                        #shh it's finished
                        local_job.isFinished = lambda *args, **kwargs: True
                        local_job.error = True
                        local_job.output_name = job['output']
                        local_job.scratch_dir = job['scratch']
                        self.local_jobs.append(local_job)

            if 'killed' in queue_dict:
                for job in queue_dict['killed']:
                    if job['server'] == 'local':
                        if job['format'] == 'Psi4':
                            local_job = Psi4Job(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])

                        elif job['format'] == 'ORCA':
                            local_job = ORCAJob(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])

                        elif job['format'] == 'Gaussian':
                            local_job = GaussianJob(job['name'], self.session, job, auto_update=job['auto_update'], auto_open=job['auto_open'])

                        #shh it's finished
                        local_job.isFinished = lambda *args, **kwargs: True
                        local_job.killed = True
                        local_job.output_name = job['output']
                        local_job.scratch_dir = job['scratch']
                        self.local_jobs.append(local_job)

            self.paused = queue_dict['job_running']

            if len(queue_dict['queued']) > 0:
                self.check_queue()
            
            if self.paused:
                self.session.logger.warning("SEQCROW's queue has been paused because a local job was running when ChimeraX was closed. The queue can be resumed with SEQCROW's job manager tool")

    def write_json(self, *args, **kwargs):
        d = {'finished':[], 'queued':[], 'check':[], 'error':[], 'killed':[]}
        job_running = False
        for job in self.jobs:
            if not job.killed:
                if not job.isFinished() and not job.isRunning():
                    d['queued'].append(job.get_json())

                elif job.isFinished() and not job.error:
                    d['finished'].append(job.get_json())
                
                elif job.isFinished() and job.error:
                    d['error'].append(job.get_json())

                elif job.isRunning():
                    d['check'].append(job.get_json())
                    job_running = True
            
            elif job.isFinished():
                d['killed'].append(job.get_json())

        d['job_running'] = job_running

        with open(self.jobs_list_filename, 'w') as f:
            dump(d, f)

    def job_finished(self, trigger_name, job):
        if self.session.seqcrow_settings.settings.JOB_FINISHED_NOTIFICATION == \
          'log and popup notifications' and self.session.ui.is_gui:
            #it's just an error message for now
            #TODO: make my own logger
            self.session.logger.error("%s: %s" % (trigger_name, job))
        
        else:
            job.session.logger.info("%s: %s" % (trigger_name, job))

        if isinstance(job, LocalJob):
            self._thread = None
            if not hasattr(job, "output_name") or \
               not os.path.exists(job.output_name):
                job.error = True
            
            else:
                fr = FileReader(job.output_name, just_geom=False)
                #XXX: finished is not added to the FileReader for ORCA and Psi4 when finished = False
                if 'finished' not in fr.other or not fr.other['finished']:
                    job.error = True

        if job.auto_update and not job.theory.structure.deleted:
            if os.path.exists(job.output_name):
                finfo = job.output_name
                if isinstance(job, GaussianJob):
                    finfo = (job.output_name, "log", None)
                elif isinstance(job, ORCAJob):
                    finfo = (job.output_name, "out", None)
                elif isinstance(job, Psi4Job):
                    finfo = (job.output_name, "dat", None)

                fr = FileReader(finfo, get_all=True, just_geom=False)
                if len(fr.atoms) > 0:
                    job.session.filereader_manager.triggers.activate_trigger(ADD_FILEREADER, ([job.theory.structure], [fr]))
    
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
            if hasattr(job, "output_name") and os.path.exists(job.output_name):
                run(job.session, "open \"%s\" coordsets true" % job.output_name)
            else:
                self.session.logger.error("could not open output of %s" % repr(job))
            
        self.triggers.activate_trigger(JOB_QUEUED, trigger_name)
        pass
    
    def job_started(self, trigger_name, job):
        job.session.logger.info("%s: %s" % (trigger_name, job))
        pass
    
    def add_job(self, job):
        if isinstance(job, LocalJob):
            self.local_jobs.append(job)
            self.triggers.activate_trigger(JOB_QUEUED, job)

    def increase_priotity(self, job):
        if isinstance(job, LocalJob):
            ndx = self.local_jobs.index(job)
            if ndx != 0:
                self.local_jobs.remove(job)
                new_ndx = 0
                for i in range(min(ndx-1, len(self.local_jobs)-1), -1, -1):
                    if not self.local_jobs[i].killed and \
                            not self.local_jobs[i].isFinished() and \
                            not self.local_jobs[i].isRunning():
                        new_ndx = i
                        break
                        
                self.local_jobs.insert(new_ndx, job)    
                
                self.triggers.activate_trigger(JOB_QUEUED, job)

    def decrease_priotity(self, job):
        if isinstance(job, LocalJob):
            ndx = self.local_jobs.index(job)
            if ndx != (len(self.local_jobs) - 1):
                self.local_jobs.remove(job)
                new_ndx = len(self.local_jobs)
                for i in range(ndx, len(self.local_jobs)):
                    if not self.local_jobs[i].killed and \
                            not self.local_jobs[i].isFinished() and \
                            not self.local_jobs[i].isRunning():
                        new_ndx = i + 1
                        break
                        
                self.local_jobs.insert(new_ndx, job)
                
                self.triggers.activate_trigger(JOB_QUEUED, job)

    def check_queue(self, *args):
        for job in self.unknown_status_jobs:
            if isinstance(job, LocalJob):
                fr = FileReader(job.output_name, just_geom=False)
                if 'finished' in fr.other and fr.other['finished']:
                    job.isFinished = lambda *args, **kwargs: True
                    job.isRunning = lambda *args, **kwargs: False
                    self.unknown_status_jobs.remove(job)
                    self.triggers.activate_trigger(JOB_FINISHED, job)
                    return
        
        if not self.has_job_running:
            unstarted_local_jobs = []
            for job in self.local_jobs:
                if not job.isFinished() and not job.killed:
                    unstarted_local_jobs.append(job)
                    
            if len(unstarted_local_jobs) > 0 and not self.paused:
                start_job = unstarted_local_jobs.pop(0)

                self._thread = start_job
                start_job.finished.connect(lambda data=start_job: self.triggers.activate_trigger(JOB_FINISHED, data))
                start_job.started.connect(lambda data=start_job: self.triggers.activate_trigger(JOB_STARTED, data))
                start_job.start()

            else:
                self._thread = None