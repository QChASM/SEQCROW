from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import StringArg, EnumOf
from chimerax.ui.options import InputFolderOption, EnumOption

from os import getenv, path

from sys import platform

class JobFinishedNotification(EnumOption):
    values = ['log notification', 'log and popup notifications']
    labels = ['log notification', 'log and popup notifications']

# 'settings' module attribute will be set by manager initialization
class _SEQCROWSettings(Settings):
    EXPLICIT_SAVE = {
        'AARONLIB': Value(getenv('AARONLIB', path.join(path.expanduser('~'), "AARON_libs")), StringArg),
        'ORCA_EXE': Value("orca.exe" if platform == "win32" else "orca", StringArg),
        'GAUSSIAN_EXE': Value("g09.exe" if platform == "win32" else "g09", StringArg),
        'PSI4_EXE': Value("psi4", StringArg),
        'SCRATCH_DIR': Value(path.join(path.expanduser('~'), "SEQCROW_SCRATCH"), StringArg), 
        'JOB_FINISHED_NOTIFICATION': Value('log notification', 
                                           EnumOf(JobFinishedNotification.values)
                                          ), 
    }


# file option (mostly the same as InputFolderOption)
class FileOption(InputFolderOption):
    """Option for specifying an existing file"""

    def get_value(self):
        return self.line_edit.text()

    def set_value(self, value):
        self.line_edit.setText(value)

    value = property(get_value, set_value)

    def _make_widget(self, initial_text_width="10em", start_folder=None, browser_title="Choose File", **kw):
        super()._make_widget(initial_text_width, start_folder, browser_title, **kw)


    def _launch_browser(self, *args):
        from PyQt5.QtWidgets import QFileDialog
        import os
        if self.start_folder is None or not os.path.exists(self.start_folder):
            start_folder = os.getcwd()
        else:
            start_folder = self.start_folder
        file = QFileDialog.getOpenFileName(self.widget, self.browser_title, start_folder, "All files (*)", "", QFileDialog.HideNameFilterDetails)
        #file is a tuple of (filename, selected filter)
        #unless no file was selected (e.g. dialog was closed by clicking 'cancel')
        if len(file) == 2:
            self.line_edit.setText(file[0])
            self.line_edit.returnPressed.emit()

def register_settings_options(session):
    settings_info = {
        "AARONLIB": (
            "Personal AaronTools library folder",
            InputFolderOption,
            "Directory containing your substituents (/Subs), ligands (/Ligands), rings (/Rings), and AARON templates (/TS_geoms)\nYou will need to restart ChimeraX for changes to take effect"),
    }
    
    job_settings_info = {
        "ORCA_EXE" : (
            "ORCA executable", 
            FileOption, 
            "Path to ORCA executable\nFull path is required for parallel/multithreaded execution"),
        
        "GAUSSIAN_EXE" : (
            "Gaussian executable", 
            FileOption, 
            "Path to Gaussian executable"),
        
        "PSI4_EXE" : (
            "Psi4 executable", 
            FileOption, 
            "Path to Psi4 executable"), 
        
        "SCRATCH_DIR" : (
            "Scratch directory",
            InputFolderOption,
            "Directory for staging QM jobs"),
        
        "JOB_FINISHED_NOTIFICATION" : (
            "Finished notification", 
            JobFinishedNotification, 
            "type of notification when job finished"),
    }
    
    for setting, setting_info in settings_info.items():
        opt_name, opt_class, balloon = setting_info
        
        def _opt_cb(opt, ses=session):
            import os
            from warnings import warn
            setting = opt.attr_name
            val = opt.value
            if setting == "AARONLIB":
                opt.settings.AARONLIB = val
                os.environ[setting] = val
                warn("Environment variable has been set for ChimeraX. Please restart ChimeraX for changes to take effect.")
            
        opt = opt_class(opt_name, getattr(settings, setting), _opt_cb,
            attr_name=setting, settings=settings, balloon=balloon, auto_set_attr=False)
        
        session.ui.main_window.add_settings_option("SEQCROW", opt)    
    
    for setting, setting_info in job_settings_info.items():
        opt_name, opt_class, balloon = setting_info
        
        def _opt_cb(opt, ses=session):
            import os
            from warnings import warn
            setting = opt.attr_name
            val = opt.value
        
        opt = opt_class(opt_name, getattr(settings, setting), _opt_cb,
            attr_name=setting, settings=settings, balloon=balloon, auto_set_attr=False)

        
        
        session.ui.main_window.add_settings_option("SEQCROW Jobs", opt)
