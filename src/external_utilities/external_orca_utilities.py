from sys import platform
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import re

from Qt.QtCore import Qt, Signal
from Qt.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QFileDialog,
    QComboBox,
    QStatusBar,
    QMessageBox,
)

from AaronTools.utils.utils import available_memory

_orbital_types = [
    "molecular orbitals",
    "natural orbitals",
    "corresponding orbitals",
    "atomic orbitals",
]

_density_types = [
    "(scf) electron density",
    "(scf) spin density",
    "AutoCI relaxed density",
    "AutoCI unrelaxed density",
    "AutoCI relaxed spin density",
    "AutoCI unrelaxed spin density",
    "OO-RI-MP2 density",
    "OO-RI-MP2 spin density",
    "MP2 relaxed density",
    "MP2 unrelaxed density",
    "MP2 relaxed spin density",
    "MP2 unrelaxed spin density",
]

_esp_types = [
    "Electrostatic Potential",
]


class ORCA_plot(QWidget):
    update = Signal()

    def __init__(self, session, *args, **kwargs):
        """fill in UI widgets and set some defaults"""
        super().__init__(*args, **kwargs)
        self.session = session
        
        # things related to the data in the gbw file
        # number of orbitals
        self.n_orbitals = 0
        # number of spin operators (p sure its either 1 or 2)
        self.n_spins = 1
        # plot types - keys are names and values are code numbers
        self.plot_types = {}
        # top level options in orca_plot - keys are names and values are code numbers
        self.top_level_options = {}
        # file formats - keys are names and values are code numbers
        self.file_formats = {}
        # list of density names
        self.densities = []
        
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # I'm storing rows in a dict b/c I think
        # it's more intuitive when writing code to hide
        # irrelevant rows
        self.rows = {}
        
        description = QLabel("ORCA tool for creating files to visualize orbitals, densities, etc.")
        self.layout.addRow(description)
        
        exe_browse = QWidget()
        exe_browse_layout = QGridLayout(exe_browse)
        margins = exe_browse_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        exe_browse_layout.setContentsMargins(*new_margins)
        self.exe_path = QLineEdit()
        # TODO: load default from settings
        exe_default = "orca_plot"
        if platform == "win32":
            exe_default += ".exe"
        dirname = os.path.dirname(self.session.seqcrow_settings.settings.ORCA_EXE)
        self.exe_path.setText(os.path.join(dirname, exe_default))

        self.exe_browse_button = QPushButton("browse...")
        self.exe_browse_button.clicked.connect(self.open_set_exe_path)
        exe_browse_layout.addWidget(self.exe_path, 0, 0, Qt.AlignVCenter)
        exe_browse_layout.addWidget(self.exe_browse_button, 0, 1, Qt.AlignVCenter)
        exe_browse_layout.setColumnStretch(0, 1)
        exe_browse_layout.setColumnStretch(1, 0)
        self.layout.addRow("executable path:", exe_browse)
        
        self.rows["executable path"] = exe_browse
        
        infile_browse = QWidget()
        infile_browse_layout = QGridLayout(infile_browse)
        margins = infile_browse_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        infile_browse_layout.setContentsMargins(*new_margins)
        self.infile_path = QLineEdit()
        self.infile_path.setPlaceholderText("your GBW file")
        
        self.infile_browse_button = QPushButton("browse...")
        self.infile_browse_button.clicked.connect(self.open_set_infile_path)
        infile_browse_layout.addWidget(self.infile_path, 0, 0, Qt.AlignVCenter)
        infile_browse_layout.addWidget(self.infile_browse_button, 0, 1, Qt.AlignVCenter)
        infile_browse_layout.setColumnStretch(0, 1)
        infile_browse_layout.setColumnStretch(1, 0)
        self.layout.addRow("GBW path:", infile_browse)
        
        self.rows["GBW path"] = infile_browse

        self.plot_type = QComboBox()
        self.plot_type.addItems(["check available plots"])
        self.layout.addRow("plot type:", self.plot_type)
        
        self.rows["plot type"] = self.plot_type

        self.density = QComboBox()
        self.layout.addRow("density:", self.density)
        
        self.rows["density"] = self.density

        # TOCONSIDER: a checkbox to make all orbitals?
        # or another spinbox for a range of orbitals
        self.orbital_number = QSpinBox()
        self.orbital_number.setMinimum(0)
        self.orbital_number.setMaximum(self.n_orbitals)
        self.orbital_number.setSingleStep(1)
        self.orbital_number.setValue(0)
        self.orbital_number.setToolTip("first orbital is number 0")
        self.layout.addRow("orbital number:", self.orbital_number)

        self.rows["orbital number"] = self.orbital_number

        self.file_format = QComboBox()
        self.layout.addRow("file format:", self.file_format)
        
        self.rows["file format"] = self.file_format

        self.operator = QComboBox()
        self.operator.addItems(["α", "β"])
        self.layout.addRow("spin operator:", self.operator)
        
        self.rows["operator"] = self.operator

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        margins = grid_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        grid_layout.setContentsMargins(*new_margins)
        
        self.x_grid_points = QSpinBox()
        self.x_grid_points.setMinimum(1)
        self.x_grid_points.setMaximum(1000)
        self.x_grid_points.setSingleStep(5)
        self.x_grid_points.setValue(40)
        grid_layout.addWidget(QLabel("x:") , 0, 0, Qt.AlignVCenter | Qt.AlignRight)
        grid_layout.addWidget(self.x_grid_points, 0, 1, Qt.AlignVCenter)

        self.y_grid_points = QSpinBox()
        self.y_grid_points.setMinimum(1)
        self.y_grid_points.setMaximum(1000)
        self.y_grid_points.setSingleStep(5)
        self.y_grid_points.setValue(40)
        grid_layout.addWidget(QLabel("y:") , 0, 2, Qt.AlignVCenter | Qt.AlignRight)
        grid_layout.addWidget(self.y_grid_points, 0, 3, Qt.AlignVCenter)

        self.z_grid_points = QSpinBox()
        self.z_grid_points.setMinimum(1)
        self.z_grid_points.setMaximum(1000)
        self.z_grid_points.setSingleStep(5)
        self.z_grid_points.setValue(40)
        grid_layout.addWidget(QLabel("z:") , 0, 4, Qt.AlignVCenter | Qt.AlignRight)
        grid_layout.addWidget(self.z_grid_points, 0, 5, Qt.AlignVCenter)
        
        grid_layout.setColumnStretch(0, 0)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 0)
        grid_layout.setColumnStretch(3, 1)
        grid_layout.setColumnStretch(4, 0)
        grid_layout.setColumnStretch(5, 1)
        self.layout.addRow("grid points:", grid_widget)
        
        self.rows["x grid points"] = self.x_grid_points
        self.rows["y grid points"] = self.y_grid_points
        self.rows["y grid points"] = self.z_grid_points

        self.memory = QSpinBox()
        self.memory.setMinimum(1)
        self.memory.setMaximum(100000000)
        self.memory.setSingleStep(500)
        self.memory.setSuffix(" MB")
        self.memory.setValue(4000)
        self.layout.addRow("memory limit:", self.memory)
        
        self.rows["memory"] = self.memory

        self.run = QPushButton("do it")
        self.run.clicked.connect(self.run_executable)
        self.layout.addRow(self.run)
        
        self.rows["do it"] = self.run

        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        self.layout.addRow(self.status)
        
        self.rows["status"] = self.status

        self.plot_type.currentTextChanged.connect(self.update_plot_options)
        self.update_plot_options(self.plot_type.currentText())

    def update_plot_options(self, text):
        # some plot types don't use certain options
        # we hide them so they aren't distracting
        if text == "check available plots":
            self.layout.setRowVisible(self.rows["orbital number"], False)
            self.layout.setRowVisible(self.rows["operator"], False)
            self.layout.setRowVisible(self.rows["density"], False)
        
        if text in _orbital_types:
            self.layout.setRowVisible(self.rows["orbital number"], True)
            self.layout.setRowVisible(self.rows["operator"], self.n_spins > 1)
            self.layout.setRowVisible(self.rows["density"], False)

        if text in _density_types:
            self.layout.setRowVisible(self.rows["orbital number"], False)
            self.layout.setRowVisible(self.rows["operator"], False)
            self.layout.setRowVisible(self.rows["density"], True)
        
        if text in _esp_types:
            self.layout.setRowVisible(self.rows["orbital number"], False)
            self.layout.setRowVisible(self.rows["operator"], False)
            self.layout.setRowVisible(self.rows["density"], True)

    def run_executable(self, *args):
        # run different functions for different types of plots
        # each function determines what should be passed to orca_plot
        kind = self.plot_type.currentText()
        self.update.emit()
        if kind == "check available plots":
            self.run_check_available()
        
        elif kind in _orbital_types:
            self.run_orbitals(kind)
        
        elif kind in _density_types:
            self.run_density(kind)

        elif kind in _esp_types:
            self.run_esp(kind)
        
        else:
            self.session.logger.warning("unknown plot type: %s" % kind)

    def run_sequence(self, codes):
        """
        runs orca_plot with the specified codes and returns the stdout and stderr
        the sequence of codes should, at the end, exit orca_plot
        otherwise ChimeraX will hang
        """
        self.session.logger.info("(debugging info) this sequence: " + str(codes))
        exe_path = self.exe_path.text()
        infile = self.infile_path.text()
        memory = self.memory.value()
        if not infile:
            self.session.logger.error("You must specify a GBW file")
            return "", ""
        
        avail = available_memory()
        if memory * 1e6 > (0.9 * available_memory()):
            are_you_sure = QMessageBox.warning(
                self,
                "Memory Limit Warning",
                "Memory limit (%.1fMB) is above or close to\n" % memory +
                "the available memory (%.1fMB).\n" % (avail * 1e-6) +
                "Exceeding available memory might affect the stability of your\n"
                "computer or ChimeraX instance.\n\n" +
                "Press \"Ok\" to continue or \"Abort\" to cancel.",
                QMessageBox.Abort | QMessageBox.Ok,
                defaultButton=QMessageBox.Abort,
            )
            if are_you_sure != QMessageBox.Ok:
                return "", ""

        def start():
            kwargs = {}
            if platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            args = [exe_path, infile, "-i", "-m", str(memory)]
            self.session.logger.info("running " + " ".join(args))
            proc = subprocess.Popen(
                args,
                encoding="utf-8",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(infile),
                **kwargs
            )
            return proc
        
        def read(proc, seek=0, until=None):
            out = ""
            proc.stdout.seek(seek)
            while c := proc.stdout.readline():
                out += c
                if until is not None and re.search(until, c):
                    break
        
            return out
        
        def write(proc, msg):
            proc.stdin.write(msg + "\n")
            proc.stdin.flush()
        
        # run orca plot to get a list of available plots
        proc = start()
        # I initially used a different thread b/c I was going to switch
        # back and forth between reading and writing from the proc's
        # stdin and stdout
        # I ended up not doing that, so IDK of threads are needed
        for code in codes:
            with ThreadPoolExecutor(max_workers=1) as e:
                job = e.submit(write, proc, code)
                job.result()
            
        if proc.poll() is not None:
            proc.kill()
        
        # wait for orca_plot to finish
        # the codes should end by getting us back to the top level and exiting
        # if they don't, ChimeraX will hand
        stdout, stderr = proc.communicate()
        if stderr:
            self.status.showMessage("failed to generate plot - see log for more details")
            self.session.logger.error("Error running orca_plot - see log for details")
            self.session.logger.warning("<pre>" + stderr + "</pre>", is_html=True)
        else:
            self.status.showMessage("done running orca_plot", 5000)
        
        return stdout, stderr

    def scan_for_output_file(self, output):
        for line in output.splitlines():
            match = re.search("Output file: (.*)", line)
            if match:
                output = match.group(1).strip()
                os.path.split(output)
                cwd = os.path.dirname(self.infile_path.text())
                output = os.path.join(cwd, output)
                link = "<a class='cxcmd' href='cxcmd:open \"%s\"'>%s</a>" % (output, output)
                self.session.logger.info("output file: %s" % link, is_html=True)

    def run_orbitals(self, orbital_type):
        self.status.showMessage("starting to generate %s ..." % orbital_type)
        sequence = [
            self.top_level_options["Enter type of plot"],
            self.plot_types[orbital_type]
        ]

        sequence.extend([
            self.top_level_options["Enter number of grid intervals"],
            " ".join(str(func()) for func in [self.x_grid_points.value, self.y_grid_points.value, self.z_grid_points.value]),
        ])

        sequence.extend([
            self.top_level_options["Enter no of orbital to plot"],
            str(self.orbital_number.value()),
        ])

        if self.n_spins > 1:
            sequence.extend([
                self.top_level_options["Enter operator of orbital (0=alpha,1=beta)"],
                str(self.operator.currentIndex()),
            ])

        file_format = self.file_format.currentText()
        sequence.extend([
            self.top_level_options["Select output file format"],
            self.file_formats[file_format],
        ])

        sequence.append(self.top_level_options["Generate the plot"])
        sequence.append(self.top_level_options["exit this program"])

        stdout, stderr = self.run_sequence(sequence)

        # self.session.logger.info("<pre>" + stdout + "</pre>", is_html=True)
        if stdout:
            self.scan_for_output_file(stdout)

    def run_density(self, density_type):
        self.status.showMessage("starting to generate %s ..." % density_type)
        sequence = [
            self.top_level_options["Enter type of plot"],
            self.plot_types[density_type],
            "n",
            self.density.currentText(),
        ]

        sequence.extend([
            self.top_level_options["Enter number of grid intervals"],
            " ".join(str(func()) for func in [self.x_grid_points.value, self.y_grid_points.value, self.z_grid_points.value]),
        ])

        if "spin density" not in density_type.lower() and self.n_spins > 1:
            sequence.extend([
                self.top_level_options["Enter operator of orbital (0=alpha,1=beta)"],
                str(self.operator.currentIndex()),
            ])

        file_format = self.file_format.currentText()
        sequence.extend([
            self.top_level_options["Select output file format"],
            self.file_formats[file_format],
        ])

        sequence.append(self.top_level_options["Generate the plot"])
        sequence.append(self.top_level_options["exit this program"])

        stdout, stderr = self.run_sequence(sequence)

        # self.session.logger.info("<pre>" + stdout + "</pre>", is_html=True)
        if stdout:
            self.scan_for_output_file(stdout)

    def run_esp(self, esp_type):
        self.status.showMessage("starting to generate %s ..." % esp_type)
        sequence = [
            self.top_level_options["Enter type of plot"],
            self.plot_types[esp_type],
            self.density.currentText(),
        ]

        sequence.extend([
            self.top_level_options["Enter number of grid intervals"],
            " ".join(str(func()) for func in [self.x_grid_points.value, self.y_grid_points.value, self.z_grid_points.value]),
        ])

        file_format = self.file_format.currentText()
        sequence.extend([
            self.top_level_options["Select output file format"],
            self.file_formats[file_format],
        ])

        sequence.append(self.top_level_options["Generate the plot"])
        sequence.append(self.top_level_options["exit this program"])

        stdout, stderr = self.run_sequence(sequence)

        # self.session.logger.info("<pre>" + stdout + "</pre>", is_html=True)
        if stdout:
            self.scan_for_output_file(stdout)

    def run_check_available(self):
        """
        run orca_plot and press 1 to check the available plot types
        if esp is an option, check available densities
        """

        # for now, hope this doesn't change
        # otherwise, we'll have to run once to parse the top_level_options
        # then run again
        # 1 - list available plot types
        # 1 - select MO plots to close available plots types list
        # 9 - list available densities
        # 5 - list available file formats
        # 1 - select cube to close available file formats list
        # 12 - close orca_plot
        stdout, stderr = self.run_sequence(["1", "1", "9", "5", "1", "12"])

        # self.session.logger.info("<pre>" + stdout + "</pre>", is_html=True)
        
        self.n_orbitals = 0
        self.n_spins = 1
        self.plot_types = {}
        self.top_level_options = {}
        self.file_formats = {}
        self.densities = []
        reading_plots = False
        reading_top_level = True
        reading_densities = False
        reading_formats = False
        for line in stdout.splitlines():
            if "Searching for Ground State Electron or Spin Densities" in line:
                reading_plots = True
            if "Enter Type" in line:
                reading_plots = False
            
            orbital_match = re.search("Number of available orbitals :\s*(\d+)", line)
            if "Number of available orbitals" in line:
                self.n_orbitals = int(orbital_match.group(1))
            
            spin_match = re.search("Number of operators          :\s*(\d+)", line)
            if spin_match:
                self.n_spins = int(spin_match.group(1))

            if reading_top_level:
                match = re.search("(\d+) - (.*)", line)
                if match:
                    self.top_level_options[match.group(2).strip()] = match.group(1)

            if "exit this program" in line:
                reading_top_level = False

            if reading_plots:
                match1 = re.search("(\d+)\s+-\s+(.+)\.", line)
                match2 = re.search("(\d+)\s+-\s+(.+)", line)
                if "NOT AVAILABLE" in line:
                    continue
                if match1:
                    self.plot_types[match1.group(2).strip(".").strip()] = match1.group(1).strip()
                elif match2:
                    self.plot_types[match2.group(2).strip()] = match2.group(1)
        
            if not reading_densities and "Name of Density" in line:
                reading_densities = True
            if reading_densities and not line.strip():
                reading_densities = False
        
            if reading_densities:
                match = re.search("\d+:\s*(.*)", line)
                if match:
                    self.densities.append(match.group(1))
            
            if reading_formats:
                match = re.search("(\d+)\s+-\s+(.+)", line)
                if match:
                    self.file_formats[match.group(2).strip()] = match.group(1)

            if not reading_formats and "File-Format is presently" in line:
                reading_formats = True
            if reading_formats and "Enter Format:" in line:
                reading_formats = False

        items = []
        for plot_type in _orbital_types + _density_types + _esp_types:
            if plot_type in self.plot_types:
                items.append(plot_type)
        
        items.append("check available plots")
        
        self.plot_type.clear()
        self.plot_type.addItems(items)
        
        self.density.clear()
        self.density.addItems(self.densities)

        self.file_format.clear()
        self.file_format.addItems(self.file_formats.keys())
        ndx = self.file_format.findText("Gaussian cube", Qt.MatchContains)
        if ndx >= 0:
            self.file_format.setCurrentIndex(ndx)
        
        self.orbital_number.setMaximum(self.n_orbitals)

    def open_set_exe_path(self):
        filename, _ = QFileDialog.getOpenFileName(filter="orca_plot executable (*.exe)")

        if filename:
            self.exe_path.setText(filename)

    def open_set_infile_path(self):
        dirname = None
        current = self.infile_path.text()
        current_dirname = os.path.dirname(current)
        if current_dirname:
            dirname = current_dirname
        filename, _ = QFileDialog.getOpenFileName(
            filter="ORCA orbital files (*.gbw)",
            directory=current_dirname
        )

        if filename:
            self.infile_path.setText(filename)

    def set_values(self, **kwargs):
        try:
            exe_path = kwargs["exe_path"]
            self.exe_path.setText(exe_path)
        except KeyError:
            pass
        
        try:
            infile_path = kwargs["infile_path"]
            self.infile_path.setText(infile_path)
        except KeyError:
            pass

        try:
            grid_points = kwargs["x_grid_points"]
            self.x_grid_points.setValue(grid_points)
        except KeyError:
            pass

        try:
            grid_points = kwargs["y_grid_points"]
            self.y_grid_points.setValue(grid_points)
        except KeyError:
            pass

        try:
            grid_points = kwargs["z_grid_points"]
            self.z_grid_points.setValue(grid_points)
        except KeyError:
            pass
        
        try:
            memory = kwargs["memory"]
            self.memory.setValue(memory)
        except KeyError:
            pass

    def get_values(self):
        out = dict()
        out["exe_path"] = self.exe_path.text()
        out["infile_path"] = self.infile_path.text()
        out["x_grid_points"] = self.x_grid_points.value()
        out["y_grid_points"] = self.y_grid_points.value()
        out["z_grid_points"] = self.z_grid_points.value()
        out["memory"] = self.memory.value()
        
        return out
