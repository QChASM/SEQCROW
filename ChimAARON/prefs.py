from chimera import preferences

INPUT_FILES = "input files"
ENVIRONMENT = "environment variables"

options = {
    INPUT_FILES: {},
    ENVIRONMENT: {}
}

prefs = preferences.addCategory("ChimAARON",
                preferences.HiddenCategory,
                optDict=options)
