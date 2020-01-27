from chimerax.core.settings import Settings

class _ChimAARONSettings(Settings):
    EXPLICIT_SAVE = {
        'AARONLIB': None,
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
            setting = opt.attr_name
            val = opt.value
            if setting == "AARONLIB":
                opt.settings.AARONLIB = val
                
            os.environ[setting] = val
            
        opt = opt_class(opt_name, getattr(settings, setting), _opt_cb,
            attr_name=setting, settings=settings, balloon=balloon, auto_set_attr=False)
        
        session.ui.main_window.add_settings_option("ChimAARON", opt)