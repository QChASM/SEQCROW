from chimera import preferences

INPUT_FILES = "input files"

options = {
    INPUT_FILES: {}
}

prefs = preferences.addCategory("ChimAARON", 
                preferences.HiddenCategory,
                optDict=options)
