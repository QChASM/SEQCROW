import os

from AaronTools.fileIO import FileReader, read_types
from AaronTools.json_extension import ATDecoder, ATEncoder

from chimerax.core.toolshed import ProviderManager
from chimerax.core.triggerset import TriggerSet
from chimerax.core.commands import run

from json import load, dump

from SEQCROW.jobs import LocalJob, LocalClusterJob, ParallelRavenJob, TSSJob

JOB_FINISHED = "job finished"
JOB_STARTED = "job started"
JOB_QUEUED = "job changed"

class JobManager(ProviderManager):
    def __init__(self, session, *args, **kwargs):
        super().__setattr__("initialized", False)
        self.session = session
        self.local_jobs = []
        self.remote_jobs = []
        self.unknown_status_jobs = []
        self.paused = False
        self._thread = None
        self.queue_dict = {}
        self.formats = {}

        self.triggers = TriggerSet()
        self.triggers.add_trigger(JOB_FINISHED)
        self.triggers.add_handler(JOB_FINISHED, self.job_finished)
        self.triggers.add_trigger(JOB_STARTED)
        self.triggers.add_handler(JOB_STARTED, self.job_started)
        self.triggers.add_trigger(JOB_QUEUED)
        self.triggers.add_handler(JOB_QUEUED, self.check_queue)
        self.triggers.add_handler(JOB_QUEUED, self.write_json)
        
        super().__init__(*args, **kwargs)

    def __setattr__(self, attr, val):
        if attr == "paused" and self.initialized:
            if val:
                self.session.logger.info("paused SEQCROW queue")
            else:
                self.session.logger.info("resumed SEQCROW queue")
        
        super().__setattr__(attr, val)

    @property
    def jobs(self):
        return self.local_jobs + self.remote_jobs

    @property
    def has_job_running(self):
        return any([job.isRunning() for job in self.local_jobs])

    @property
    def has_local_job_running(self):
        return any([job.isRunning() for job in self.local_jobs if not isinstance(job, LocalClusterJob)])

    def add_provider(self, bundle_info, name, **kw):
        # if name in self.formats:
        #     self.session.logger.warning(
        #         "local job type %s from %s supplanted that from %s" % (
        #             name, bundle_info.name, self.formats[name].name
        #         )
        #     )
        self.formats[name] = bundle_info

    def init_queue(self):
        """reads cached job list to fill in the queue"""
        scr_dir = os.path.abspath(self.session.seqcrow_settings.settings.SCRATCH_DIR)
        self.jobs_list_filename = os.path.join(scr_dir, "job_list-3.json")
        if os.path.exists(self.jobs_list_filename):
            with open(self.jobs_list_filename, 'r') as f:
                queue_dict = load(f, cls=ATDecoder)

            for section in ["check", "queued", "finished", "error", "killed"]:
                if section not in queue_dict:
                    continue
                for job in queue_dict[section]:
                    if job['server'] == 'local':
                        for name, bi in self.formats.items():
                            if name == job["format"]:
                                job_cls = bi.run_provider(
                                    self.session,
                                    name,
                                    self
                                )
                                args = [
                                    job['name'],
                                    self.session,
                                    job['theory'],
                                ]
                                kwargs = dict()
                                if name == "Raven":
                                    args.extend([
                                        job["reactant"],
                                        job["product"],
                                        job["file_type"],
                                        "GPRGSM",
                                    ])
                                    kwargs = job["raven_kwargs"]
                                if issubclass(job_cls, TSSJob):
                                    args.extend([
                                        job["reactant"],
                                        job["product"],
                                        job["file_type"],
                                    ])
                                break
                        else:
                            self.session.logger.warning(
                                "local job provider for %s jobs is no longer installed," % job["format"] +
                                "job named '%s' will be removed from the queue" % job["name"]
                            )
                    
                    elif job['server'] == "cluster":
                        args = [
                            job['name'],
                            self.session,
                            job['theory'],
                            job['file_type'],
                        ]
                        if "format" in job and job["format"] == "Raven":
                            job_cls = ParallelRavenJob
                            args.extend([
                                job["reactant"],
                                job["product"],
                                "GPRGSM",
                            ])
                            kwargs = job["raven_kwargs"]
                        else:
                            job_cls = LocalClusterJob
                            kwargs = {
                                "geometry": job['geometry'],
                            }
                   
                        kwargs["queue_type"] = job["queue_type"]
                        kwargs["template_kwargs"] = job["template_kwargs"]
                        kwargs["template"] = job["template"]
                        kwargs["processors"] = job["processors"]
                        kwargs["walltime"] = job["walltime"]
                        kwargs["memory"] = job["memory"]

                        print(job_cls)
                        print(args)
                        print(kwargs)

                    else:
                        self.session.logger.warning("job with unknown server: %s" % job['server'])
                        continue
                    
                    local_job = job_cls(
                        *args,
                        auto_update=job['auto_update'],
                        auto_open=job['auto_open'],
                        **kwargs
                    )

                    if section == "check":
                        if 'output' in job and job['output'] and os.path.exists(job['output']):
                            fr = FileReader(job['output'], just_geom=False)
                            if 'finished' in fr.other and fr.other['finished']:
                                local_job.isFinished = lambda *args, **kwargs: True
                            else:
                                local_job.isRunning = lambda *args, **kwargs: True
                                self.unknown_status_jobs.append(local_job)
    
                    elif section == "finished":
                        #shh it's finished
                        local_job.isFinished = lambda *args, **kwargs: True
                        local_job.output_name = job['output']
                        local_job.scratch_dir = job['scratch']
                                
                    elif section == "error":
                        #shh it's finished
                        local_job.isFinished = lambda *args, **kwargs: True
                        local_job.isFinished = lambda *args, **kwargs: True
                        local_job.error = True
                        local_job.output_name = job['output']
                        local_job.scratch_dir = job['scratch']
                                
                    elif section == "killed":
                        local_job.isFinished = lambda *args, **kwargs: True
                        local_job.isFinished = lambda *args, **kwargs: True
                        local_job.killed = True
                        local_job.output_name = job['output']
                        local_job.scratch_dir = job['scratch']
    
                        local_job.output_name = job['output']
                        local_job.scratch_dir = job['scratch']

                    self.local_jobs.append(local_job)
                    # self.session.logger.info("added %s (%s job) from previous session" % (job['name'], job['format']))

            self.paused = queue_dict['job_running']

            if len(queue_dict['queued']) > 0:
                self.check_queue()
            
            if self.paused:
                self.session.logger.warning("SEQCROW's queue has been paused because a local job was running when ChimeraX was closed. The queue can be resumed with SEQCROW's job manager tool")

        self.initialized = True

    def remove_local_job(self, job):
        """remove a local job from the list of jobs and update the json"""
        self.local_jobs.remove(job)
        self.write_json()

    def write_json(self, *args, **kwargs):
        """updates the list of cached jobs"""
        d = {'finished':[], 'queued':[], 'check':[], 'error':[], 'killed':[]}
        job_running = False
        for job in self.jobs:
            # print(job.name)
            if not job.killed:
                if not job.isFinished() and not job.isRunning():
                    d['queued'].append(job.get_json())
                    # print("queued")
                    
                elif job.isFinished() and not job.error:
                    d['finished'].append(job.get_json())
                    # print("finished")

                elif job.isFinished() and job.error:
                    d['error'].append(job.get_json())
                    # print("error")

                elif job.isRunning():
                    d['check'].append(job.get_json())
                    job_running = True
                    # print("check")

            elif job.isFinished() and job.killed:
                d['killed'].append(job.get_json())
                # print("killed")

        d['job_running'] = job_running

        if not self.initialized:
            self.init_queue()

        #check if SEQCROW scratch directory exists before trying to write json
        if not os.path.exists(os.path.dirname(self.jobs_list_filename)):
            os.makedirs(os.path.dirname(self.jobs_list_filename))

        with open(self.jobs_list_filename, 'w') as f:
            dump(d, f, cls=ATEncoder, indent=4)

    def job_finished(self, trigger_name, job):
        """when a job is finished, open or update the structure as requested"""

        from SEQCROW.managers import ADD_FILEREADER
        from SEQCROW.residue_collection import ResidueCollection


        if self.session.seqcrow_settings.settings.JOB_FINISHED_NOTIFICATION == \
          'log and popup notifications' and self.session.ui.is_gui:
            #it's just an error message for now
            #TODO: make my own logger
            self.session.logger.error("%s: %s" % (trigger_name, job))
        
        else:
            job.session.logger.info("%s: %s" % (trigger_name, job))

        if isinstance(job, LocalJob):
            self._thread = None
            if (
                not hasattr(job, "output_name") or
                not job.output_name or (
                    isinstance(job.output_name, str) and
                    not os.path.exists(job.output_name)
                ) or (
                    not isinstance(job.output_name, str) and
                    hasattr(job.output_name, "__iter__") and
                    not all(os.path.exists(f) for f in job.output_name)
                )
            ):
                job.error = True
            
            else:
                try:
                    if isinstance(job.output_name, str):
                        fr = FileReader(job.output_name, just_geom=False)
                        if 'finished' not in fr.other or not fr.other['finished']:
                            job.error = True
                    else:
                        for f in job.output_name:
                            fr = FileReader(f, just_geom=False)
                            if 'finished' in fr.other and not fr.other['finished']:
                                job.error = True
                except NotImplementedError:
                    pass
        
        self.triggers.activate_trigger(JOB_QUEUED, trigger_name)

        if job.auto_update and (
            job.theory.geometry.chix_atomicstructure is not None and
            not job.theory.geometry.chix_atomicstructure.deleted
        ):
            job.update_structure(job.theory.geometry.chix_atomicstructure)

        elif job.auto_open or job.auto_update:
            job.open_structure()

    def job_started(self, trigger_name, job):
        """prints 'job started' notification to log"""
        job.session.logger.info("%s: %s" % (trigger_name, job))
        pass
    
    def add_job(self, job):
        """add job (LocalJob instance) to the queue"""
        if not self.initialized:
            self.init_queue()
        if isinstance(job, LocalJob):
            self.local_jobs.append(job)
            self.triggers.activate_trigger(JOB_QUEUED, job)

    def increase_priotity(self, job):
        """move job (LocalJob) up one position in the queue"""
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
        """move job (LocalJob) down one position in the queue"""
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
        """check to see if a waiting job can run"""
        for job in self.unknown_status_jobs:
            if isinstance(job, LocalJob):
                try:
                    fr = FileReader(job.output_name, just_geom=False)
                    if 'finished' in fr.other and fr.other['finished']:
                        job.isFinished = lambda *args, **kwargs: True
                        job.isRunning = lambda *args, **kwargs: False
                        self.unknown_status_jobs.remove(job)
                        self.triggers.activate_trigger(JOB_FINISHED, job)
                except NotImplementedError:
                    self.session.logger.warning("cannot determine status of job %s" % job)
                    continue
        
        if not self.has_local_job_running:
            unstarted_local_jobs = []
            for job in self.local_jobs:
                if not job.isFinished() and not job.killed:
                    # print("unstarted job:", job)
                    unstarted_local_jobs.append(job)
                    
            if len(unstarted_local_jobs) > 0 and not self.paused:
                start_job = unstarted_local_jobs.pop(0)

                self._thread = start_job
                start_job.finished.connect(lambda data=start_job: self.triggers.activate_trigger(JOB_FINISHED, data))
                start_job.started.connect(lambda data=start_job: self.triggers.activate_trigger(JOB_STARTED, data))
                start_job.start()

            else:
                self._thread = None
