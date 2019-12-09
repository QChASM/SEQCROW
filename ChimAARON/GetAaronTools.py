import Tkinter
import Tix
import sys
import os
import ChimAARON
import chimera

from chimera.baseDialog import ModelessDialog
from tkFileDialog import askdirectory

class GetAaronToolsDialog(ModelessDialog):
    title = "Get or Backport AaronTools"

    buttons = ("Close",)
    help = ("tutorials/setupGuide.html", ChimAARON)

    def __init__(self):
        if sys.version_info < (3,):
            self.NEED_FUTURE = True
        else:
            self.NEED_FUTURE = False

        self.CHECK_FOR_AARONTOOLS()

        try:
            import pip
            if int(pip.__version__.split('.')[0]) < 19:
                self.HAS_PIP = False
            else:
                self.HAS_PIP = True

        except ImportError:
            self.HAS_PIP = False

        print(self.NEED_FUTURE)
        print(self.HAS_AARONTOOLS)
        print(self.IMPORTED_AARONTOOLS)
        print(self.NEED_PIP)
        print(self.HAS_PIP)

        ModelessDialog.__init__(self)

    def CHECK_FOR_AARONTOOLS(self):
        try:
            import AaronTools
            self.HAS_AARONTOOLS = True
            for f in os.listdir(os.path.dirname(AaronTools.__file__)):
                if f.endswith('.py') and "new_fileIO" not in f:
                    exec "import AaronTools.%s" % ".".join(f.split('.')[:-1])
                    print(f)

            self.IMPORTED_AARONTOOLS = True

        except SyntaxError:
            self.HAS_AARONTOOLS = True
            self.IMPORTED_AARONTOOLS = False

        except ImportError:
            if not hasattr(self, "HAS_AARONTOOLS") and not self.HAS_AARONTOOLS:
                self.HAS_AARONTOOLS = False

            self.IMPORTED_AARONTOOLS = False

        if self.NEED_FUTURE or not self.HAS_AARONTOOLS:
            try:
                import pip
                self.NEED_PIP = False

            except ImportError:
                self.NEED_PIP = True

    def fillInUI(self, parent):
        from ChimAARON.prefs import ENVIRONMENT

        envPrefs = chimera.preferences.preferences.get('ChimAARON', ENVIRONMENT)
        if 'AARONLIB' in envPrefs:
            arnlib = envPrefs['AARONLIB']
        else:
            arnlib = None
            
        if 'HOME' in envPrefs:
            home = envPrefs['HOME']
        elif os.getenv('HOME', False):
            home = os.getenv('HOME', False)
        elif os.getenv('USERPROFILE', False):
            home = os.getenv('USERPROFILE', False)
        else:
            home = None

        self.envDisplayArea = Tkinter.LabelFrame(parent, text="AaronTools Environment")
        self.envDisplayArea.grid(row=0, column=0, sticky='nsew')
        self.envDisplayArea.rowconfigure(0, weight=1)
        self.envDisplayArea.columnconfigure(0, weight=1)

        row = 0

        self.AARONLIBButton = Tkinter.Button(self.envDisplayArea, anchor='w', text="set AARONLIB location", command=self.arnlibSelect, pady=0)
        self.AARONLIBButton.grid(row=row, column=0, sticky='w')

        self.envLabel = Tkinter.Label(self.envDisplayArea, anchor='w', text="Personal AaronTools Library Location: %s" % arnlib)
        self.envLabel.grid(row=row, column=1, sticky='ew')

        row += 1        
        
        self.homeButton = Tkinter.Button(self.envDisplayArea, anchor='w', text="set home directory", command=self.homeSelect, pady=0)
        self.homeButton.grid(row=row, column=0, sticky='w')

        self.homeLabel = Tkinter.Label(self.envDisplayArea, anchor='w', text="home directory: %s" % home)
        self.homeLabel.grid(row=row, column=1, sticky='ew')

        row += 1

        #display backport/setup instructions
        self.inputDisplayArea = Tkinter.LabelFrame(parent, text="Dependencies")
        self.inputDisplayArea.grid(row=1, column=0, sticky='nsew')
        self.inputDisplayArea.rowconfigure(0, weight=1)
        self.inputDisplayArea.columnconfigure(1, weight=1)

        row = 0

        self.installPipButton = Tkinter.Button(self.inputDisplayArea, text="install pip with ensurepip and update pip", command=self.installPip, pady=0)
        self.installPipButton.grid(row=row, column=0, sticky='sew')

        row += 1

        self.installDependenciesButton = Tkinter.Button(self.inputDisplayArea, text="install dependencies", command=self.installDependencies, pady=0)
        self.installDependenciesButton.grid(row=row, column=0, sticky='new')

        row += 1

        self.backportButton = Tkinter.Button(self.inputDisplayArea, text="pasteurize AaronTools", command=self.backportAaronTools, pady=0)
        self.backportButton.grid(row=row, column=0, sticky='new')
        self.backportButton.config(state="disabled")

        row += 1

        self.moreBackportsButton = Tkinter.Button(self.inputDisplayArea, text="fix misc. backporting", command=self.doAdditionalBackports, pady=0)
        self.moreBackportsButton.grid(row=row, column=0, sticky='new')
        self.moreBackportsButton.config(state="disabled")

        row += 1

        self.inputDisplay = Tkinter.Text(self.inputDisplayArea, wrap='word')
        self.inputDisplay.grid(row=0, column=1, rowspan=row, sticky='nsew')
        self.inputScroll = Tkinter.Scrollbar(self.inputDisplayArea, command=self.inputDisplay.yview)
        self.inputScroll.grid(row=0, column=2, rowspan=row, sticky='nsew')
        self.inputDisplay.rowconfigure(0, weight=1)
        self.inputDisplay.columnconfigure(0, weight=1)
        self.inputDisplay['yscrollcommand'] = self.inputScroll.set

        readme = """If you have installed ChimAARON from the QChASM GitHub alongside the ChimAARON-compatible AaronTools, you do not need to backport AaronTools.

To install dependencies, you'll have to bootstrap/install pip first. This can be done by pressing the 'install pip with ensurepip and update pip' button to the left.

Once pip is installed, you will be able to install the AaronTools dependencies (currently just `future`) with the 'install dependencies' button.

Fresh installations of AaronTools need to be backported to Python 2 for ChimAARON to work. Backporting is a two-step process: first, run the pasteurize script that was installed with `future`, and then fix random things that pasteurize doesn't. Please wait for pasteurize to finish before running 'fix misc. backporting'.

After all of that is complete, ChimAARON tools should function the next time you start Chimera."""

        self.inputDisplay.delete("1.0", Tkinter.END)
        self.inputDisplay.insert(Tkinter.END, readme)
        self.inputDisplay.config(state='disabled')

        self.testDisplayArea = Tkinter.LabelFrame(parent, text="Tests")
        self.testDisplayArea.grid(row=2, column=0, sticky='nsew')
        self.testDisplayArea.rowconfigure(0, weight=1)
        self.testDisplayArea.columnconfigure(0, weight=1)

        row = 0
        self.aaronToolsTestsButton = Tkinter.Button(self.testDisplayArea, text="run AaronTools tests", command=AaronToolsTestSelection, pady=0)
        self.aaronToolsTestsButton.grid(row=row, column=0, sticky='w')

        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

    def installPip(self):
        from chimera import replyobj
        import ensurepip
        import subprocess

        try:
            ensurepip.bootstrap()
        except AttributeError as e:
            replyobj.warning("encountered an error while bootstrapping pip:\n%s\n \
This error can occur when an old version of ensurepip tries to run a newer version of pip. \
We'll ignore this error and proceed with updating the current version of pip" % e)

        proc = subprocess.Popen([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = proc.communicate()
        replyobj.status(out[0])
        print(out[0])

    def installDependencies(self):
        from chimera import replyobj
        import subprocess
        import shutil

        print('installing future...')
        replyobj.status('installing future...')
        proc = subprocess.Popen([sys.executable, '-m', 'pip', 'install', 'future'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = proc.communicate()
        replyobj.status(out[0])
        print(out[0])
        if out[1]:
            replyobj.warning(out[1])

        """print('installing cclib...')
        replyobj.status('installing cclib...')
        proc = subprocess.Popen([sys.executable, '-m', 'pip', 'install', 'cclib'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = proc.communicate()
        replyobj.status(out[0])
        print(out[0])
        if out[1]:
            replyobj.warning(out[1])
        """

    def backportAaronTools(self):
        import subprocess
        from chimera import replyobj
        import AaronTools

        AaronTools_dir = os.path.dirname(AaronTools.__file__)

        print("AaronTools found in %s" % AaronTools_dir)
        replyobj.status("AaronTools found in %s" % AaronTools_dir)

        scripts_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
        for script in os.listdir(scripts_dir):
            if "pasteurize" in script:
                pasteurize_exe = os.path.join(scripts_dir, script)

        proc = subprocess.Popen([pasteurize_exe, '-w', AaronTools_dir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = proc.communicate()
        replyobj.status(out[0])
        print(out[0])
        if out[1]:
            replyobj.warning(out[1])

    def doAdditionalBackports(self):
        import AaronTools
        from chimera import replyobj
        from ChimAARON.backporter import backporter_main

        AaronTools_dir = os.path.dirname(AaronTools.__file__)

        print("AaronTools found in %s" % AaronTools_dir)
        replyobj.status("AaronTools found in %s" % AaronTools_dir)

        backporter_main(AaronTools_dir)

        utils_init = os.path.join(AaronTools_dir, 'utils', '__init__.py')

        if not os.path.exists(utils_init):
            with open(utils_init, 'a'):
                os.utime(utils_init, None)

    def arnlibSelect(self):
        from ChimAARON.prefs import prefs, ENVIRONMENT
        from copy import deepcopy
        from chimera import replyobj

        if 'AARONLIB' in prefs[ENVIRONMENT]:
            libPref = prefs[ENVIRONMENT]['AARONLIB']
        else:
            libPref = None

        arnlib = askdirectory(initialdir=libPref, title="Select AARONLIB directory")

        if arnlib:
            envPrefs = deepcopy(prefs[ENVIRONMENT])
            envPrefs['AARONLIB'] = arnlib
            prefs[ENVIRONMENT] = envPrefs

            libs = ['RingFrags', 'Subs', 'Ligands', 'TS_geoms']

            for lib in libs:
                libDir = os.path.join(arnlib, lib)
                if not os.path.exists(libDir):
                    os.makedirs(libDir)

            replyobj.status("set AARONLIB to %s and created library directories" % arnlib)
            replyobj.status("Restart Chimera for changes to take effect")
            self.envLabel.config(text="Personal AaronTools Library Location: %s" % arnlib)
    
    def homeSelect(self):
        from ChimAARON.prefs import prefs, ENVIRONMENT
        from copy import deepcopy
        from chimera import replyobj

        if 'HOME' in prefs[ENVIRONMENT]:
            libPref = prefs[ENVIRONMENT]['HOME']
        elif os.getenv('HOME', False):
            libPref = os.getenv('HOME', False)
        elif os.getenv('USERPROFILE', False):
            libPref = os.getenv('USERPROFILE', False)
        else:
            libPref = None

        home = askdirectory(initialdir=libPref, title="Select home directory")

        if home:
            envPrefs = deepcopy(prefs[ENVIRONMENT])
            envPrefs['HOME'] = home
            prefs[ENVIRONMENT] = envPrefs

            replyobj.status("set HOME to %s" % home)
            self.homeLabel.config(text="Home directory: %s" % home)

class AaronToolsTestSelection(ModelessDialog):
    title = "select AaronTools tests"
    
    def fillInUI(self, parent):
        import os
        import AaronTools

        cwd = os.getcwd()

        AaronTools_location = os.path.dirname(AaronTools.__file__)
        AaronTools_test_dir = os.path.join(AaronTools_location, 'test')

        os.chdir(AaronTools_test_dir)

        row = 0
        self.tests = {}
        self.run_test = {}
        for test in os.listdir(AaronTools_test_dir):
            if test.startswith('test') and test.endswith('.py'):
            
                self.run_test[test] = Tkinter.BooleanVar()
                self.run_test[test].set(True)
                self.tests[test] = Tkinter.Checkbutton(parent, text=test, indicatoron=Tkinter.TRUE, relief=Tkinter.FLAT, highlightthickness=0, variable=self.run_test[test])
                self.tests[test].grid(row=row, column=0, sticky='w')
                
                row += 1

        os.chdir(cwd)

    def Apply(self):
        self.run_tests()
  
    def run_tests(self):
        import sys
        import subprocess
        import os
        import AaronTools
        import chimera
        
        from ChimAARON.prefs import ENVIRONMENT

        cwd = os.getcwd()

        AaronTools_location = os.path.dirname(AaronTools.__file__)
        AaronTools_test_dir = os.path.join(AaronTools_location, 'test')

        envPrefs = chimera.preferences.preferences.get('ChimAARON', ENVIRONMENT)
        if 'AARONLIB' in envPrefs:
            os.environ['AARONLIB'] = envPrefs['AARONLIB']

        if os.getenv('PYTHONPATH', False):
            os.environ['PYTHONPATH'] = os.getenv('PYTHONPATH') + ":" + os.path.split(AaronTools_location)[0]
        else:
            os.environ['PYTHONPATH'] = os.path.split(AaronTools_location)[0]

        print(os.getenv('AARONLIB', 'AARONLIB not set'))
        print(os.getenv('PYTHONPATH'))

        chimera.replyobj.status('running AaronTools tests - see reply log for results')
        print(AaronTools_test_dir)

        os.chdir(AaronTools_test_dir)

        tests = [test for test in self.tests if self.run_test[test].get()]

        for test in tests:
            chimera.replyobj.info("running %s..." % test)
            proc = subprocess.Popen([sys.executable, os.path.join(AaronTools_test_dir, test)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out = proc.communicate()
            if out[0] is not None:
                chimera.replyobj.info(out[0])

        os.chdir(cwd)        
        