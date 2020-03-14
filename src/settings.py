from chimerax.core.settings import Settings
from chimerax.core.configfile import Value
from chimerax.core.commands.cli import StringArg

from os import getenv

def tuple2str(t):
    """converts tuple to str and cuts off ()"""
    return str(t)[1:-1]
    
class _SEQCROSettings(Settings):
    EXPLICIT_SAVE = {
        'AARONLIB': Value(getenv('AARONLIB', None), StringArg, str),
    }

# 'settings' module attribute will be set by manager initialization

def register_settings_options(session):
    from chimerax.ui.options import InputFolderOption
    settings_info = {
        'AARONLIB': (
            "Personal AaronTools library folder",
            InputFolderOption,
            "Directory containing your substituents (/Subs), ligands (/Ligands), rings (/Rings), and AARON templates (/TS_geoms)\nYou will need to restart ChimeraX for changes to take effect"),
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
        
        session.ui.main_window.add_settings_option("SEQCRO", opt)
