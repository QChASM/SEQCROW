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
            "asdf"),
    }
    for setting, setting_info in settings_info.items():
        opt_name, opt_class, balloon = setting_info
        opt = opt_class(opt_name, getattr(settings, setting), None,
            attr_name=setting, settings=settings, balloon=balloon)
        session.ui.main_window.add_settings_option("ChimAARON Environment", opt)