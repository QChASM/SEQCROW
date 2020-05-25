import os

from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.tools import ToolInstance
from chimerax.core.commands import run

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QGridLayout, QTextBrowser, QPushButton, QTreeWidget, QTreeWidgetItem

from SEQCROW.managers.job_manager import JOB_QUEUED, JOB_STARTED, JOB_FINISHED
from SEQCROW.jobs import LocalJob

class JobQueue(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False

    NAME_COL = 0
    STATUS_COL = 1
    SERVER_COL = 2

    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.display_name = "Job Queue"
        
        self.tool_window = MainToolWindow(self)        

        self._build_ui()
        
        self._job_queued = self.session.seqcrow_job_manager.triggers.add_handler(JOB_QUEUED,
            lambda *args: self.fill_tree(*args)) 
        self._job_started = self.session.seqcrow_job_manager.triggers.add_handler(JOB_STARTED,
            lambda *args: self.fill_tree(*args))
        self._job_finished = self.session.seqcrow_job_manager.triggers.add_handler(JOB_FINISHED,
            lambda *args: self.fill_tree(*args)) 

        self.fill_tree()

    def _build_ui(self):
        layout = QGridLayout()
        
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        
        self.tree = QTreeWidget()
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.tree.setHeaderLabels(["Name", "Status", "Server"])
        self.tree.setUniformRowHeights(True)

        self.tree.setColumnWidth(0, 200)
        layout.addWidget(self.tree, 0, 0, 6, 1, Qt.AlignTop)
        
        row = 0
        
        pause_button = QPushButton("pause new jobs")
        pause_button.clicked.connect(self.pause_queue)
        layout.addWidget(pause_button, row, 1, 1, 1, Qt.AlignTop)
        
        row += 1
        
        resume_button = QPushButton("unpause queue")
        resume_button.clicked.connect(self.resume_queue)
        layout.addWidget(resume_button, row, 1, 1, 1, Qt.AlignTop)
        
        row += 1
        
        kill_button = QPushButton("kill selected")
        kill_button.clicked.connect(self.kill_running)
        layout.addWidget(kill_button,row, 1, 1, 1, Qt.AlignTop)

        row += 1

        open_button = QPushButton("open structure")
        open_button.clicked.connect(self.open_jobs)
        layout.addWidget(open_button, row, 1, 1, 1, Qt.AlignTop)
        
        row += 1

        log_button = QPushButton("view log")
        log_button.clicked.connect(self.open_log)
        layout.addWidget(log_button, row, 1, 1, 1, Qt.AlignTop)
        
        row += 1

        output_button = QPushButton("view raw output")
        output_button.clicked.connect(self.open_output)
        layout.addWidget(output_button, row, 1, 1, 1, Qt.AlignTop)
        
        row += 1

        for i in range(0, row-1):
            layout.setRowStretch(i, 0)
            
        layout.setRowStretch(row-1, 1)
        
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
        
    def fill_tree(self, trigger_name=None, trigger_job=None):        
        item_stack = [self.tree.invisibleRootItem()]
        
        self.tree.clear()

        jobs = self.session.seqcrow_job_manager.jobs

        for job in jobs:
            name = job.name
            parent = item_stack[0]
            item = QTreeWidgetItem(parent)
            item_stack.append(item)
            
            item.setData(self.NAME_COL, Qt.DisplayRole, job)
            item.setText(self.NAME_COL, name)
            
            if isinstance(job, LocalJob):
                if job.killed:
                    item.setText(self.STATUS_COL, "killed")
                    
                elif job.isRunning():
                    item.setText(self.STATUS_COL, "running")
                
                elif job.isFinished():
                    item.setText(self.STATUS_COL, "finished")

                else:
                    item.setText(self.STATUS_COL, "queued")
                    
                item.setText(self.SERVER_COL, "local")
    
            self.tree.expandItem(item)
    
        self.tree.resizeColumnToContents(self.NAME_COL)
        self.tree.resizeColumnToContents(self.SERVER_COL)

    def pause_queue(self):
        self.session.seqcrow_job_manager.paused = True
        
    def resume_queue(self):
        self.session.seqcrow_job_manager.paused = False
        self.session.seqcrow_job_manager.triggers.activate_trigger(JOB_QUEUED, "resume")
        
    def open_jobs(self):
        jobs = self.session.seqcrow_job_manager.jobs
        ndxs = list(set([item.row() for item in self.tree.selectedIndexes()]))
        for ndx in ndxs:
            job = jobs[ndx]
            if hasattr(job, "output_name"):
                run(job.session, "open \"%s\"" % job.output_name, log=False)

    def open_log(self):
        jobs = self.session.seqcrow_job_manager.jobs
        ndxs = list(set([item.row() for item in self.tree.selectedIndexes()]))
        for ndx in ndxs:
            job = jobs[ndx]
            if hasattr(job, "scratch_dir"):
                self.tool_window.create_child_window("%s log" % job.name, window_class=JobLog, scr_dir=job.scratch_dir)        
    
    def open_output(self):
        jobs = self.session.seqcrow_job_manager.jobs
        ndxs = list(set([item.row() for item in self.tree.selectedIndexes()]))
        for ndx in ndxs:
            job = jobs[ndx]
            if hasattr(job, "output_name"):
                self.tool_window.create_child_window("%s log" % job.name, window_class=JobOutput, file=job.output_name)        
            
    def kill_running(self):
        jobs = self.session.seqcrow_job_manager.jobs
        ndxs = list(set([item.row() for item in self.tree.selectedIndexes()]))
        for ndx in ndxs:
            job = jobs[ndx]
            job.terminate()
            job.wait()
            
        self.session.seqcrow_job_manager.triggers.activate_trigger(JOB_QUEUED, "kill")
            
    def delete(self):
        """overload delete"""
        self.session.seqcrow_job_manager.triggers.remove_handler(self._job_queued)
        self.session.seqcrow_job_manager.triggers.remove_handler(self._job_started)
        self.session.seqcrow_job_manager.triggers.remove_handler(self._job_finished)
        super().delete()
        
        
class JobLog(ChildToolWindow):
    def __init__(self, tool_instance, title, scr_dir=None, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)
        
        self._build_ui()
    
        with open(os.path.join(scr_dir, "seqcrow_log.txt"), "r") as f:
            lines = f.readlines()
            
        self.text.setText("".join(lines))
        
    def _build_ui(self):
        layout = QGridLayout()
        
        self.text = QTextBrowser()
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.text.setFont(font)
        layout.addWidget(self.text, 0, 0)
        
        self.ui_area.setLayout(layout)
        self.manage(None)        
        
        
class JobOutput(ChildToolWindow):
    def __init__(self, tool_instance, title, file=None, **kwargs):
        super().__init__(tool_instance, title, statusbar=False, **kwargs)
        
        self._build_ui()
    
        with open(file, "r") as f:
            lines = f.readlines()
            
        self.text.setText("".join(lines))

    def _build_ui(self):
        layout = QGridLayout()
        
        self.text = QTextBrowser()
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.text.setFont(font)
        layout.addWidget(self.text, 0, 0)
        
        self.ui_area.setLayout(layout)
        self.manage(None)    