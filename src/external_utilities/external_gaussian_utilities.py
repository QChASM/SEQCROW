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

from AaronTools.utils.utils import available_memory, get_filename, get_outfile
from SEQCROW.widgets.options import Choices, IntegerOption


class CubeGen(QWidget):
    update = Signal()

    def __init__(self, session, *args, **kwargs):
        """fill in UI widgets and set some defaults"""
        super().__init__(*args, **kwargs)
        self.session = session
        
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        description = QLabel("Gaussian tool for creating files to visualize orbitals, densities, etc.")
        self.layout.addRow(description)
        
        exe_browse = QWidget()
        exe_browse_layout = QGridLayout(exe_browse)
        margins = exe_browse_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        exe_browse_layout.setContentsMargins(*new_margins)
        self.exe_path = QLineEdit()
        # TODO: load default from settings
        exe_default = "cubegen"
        if platform == "win32":
            exe_default += ".exe"
        dirname = os.path.dirname(self.session.seqcrow_settings.settings.GAUSSIAN_EXE)
        self.exe_path.setText(os.path.join(dirname, exe_default))

        self.exe_browse_button = QPushButton("browse...")
        self.exe_browse_button.clicked.connect(self.open_set_exe_path)
        exe_browse_layout.addWidget(self.exe_path, 0, 0, Qt.AlignVCenter)
        exe_browse_layout.addWidget(self.exe_browse_button, 0, 1, Qt.AlignVCenter)
        exe_browse_layout.setColumnStretch(0, 1)
        exe_browse_layout.setColumnStretch(1, 0)
        self.layout.addRow("executable path:", exe_browse)

        infile_browse = QWidget()
        infile_browse_layout = QGridLayout(infile_browse)
        margins = infile_browse_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        infile_browse_layout.setContentsMargins(*new_margins)
        self.infile_path = QLineEdit()
        self.infile_path.setPlaceholderText("your Fchk file")

        self.infile_browse_button = QPushButton("browse...")
        self.infile_browse_button.clicked.connect(self.open_set_infile_path)
        infile_browse_layout.addWidget(self.infile_path, 0, 0, Qt.AlignVCenter)
        infile_browse_layout.addWidget(self.infile_browse_button, 0, 1, Qt.AlignVCenter)
        infile_browse_layout.setColumnStretch(0, 1)
        infile_browse_layout.setColumnStretch(1, 0)
        self.layout.addRow("Fchk path:", infile_browse)

        outfile_browse = QWidget()
        outfile_browse.setToolTip("""output destination\ncertain pattern substitutions can be made:
        $infile will be replaced with the basename of the input fchk file
        $kind will be replaced with the type of data in the cube file""")
        outfile_browse_layout = QGridLayout(outfile_browse)
        margins = outfile_browse_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        outfile_browse_layout.setContentsMargins(*new_margins)
        self.outfile_path = QLineEdit()
        self.outfile_path.setText("$infile-$kind.cube")

        self.outfile_browse_button = QPushButton("browse...")
        self.outfile_browse_button.clicked.connect(self.open_set_outfile_path)
        outfile_browse_layout.addWidget(self.outfile_path, 0, 0, Qt.AlignVCenter)
        outfile_browse_layout.addWidget(self.outfile_browse_button, 0, 1, Qt.AlignVCenter)
        outfile_browse_layout.setColumnStretch(0, 1)
        outfile_browse_layout.setColumnStretch(1, 0)
        self.layout.addRow("output destination:", outfile_browse)

        self.plot_type = QComboBox()
        self.plot_type.addItems([
            "molecular orbital",
            "electron density",
            "spin density",
            "electrostatic potential",
            "magnetically-induced current density",
            "magnetic shielding density",
        ])
        self.layout.addRow("plot type:", self.plot_type)

        self.orbital_number = Choices(
            options={
                "Homo": "HOMO",
                "Lumo": "LUMO",
                "All": "All",
                "OccA": "occupied α orbitals",
                "OccB": "occupied β orbitals",
                "Valence": "all valence orbitals",
                "Virtual": "all virtual orbitals",
                IntegerOption(
                    minimum=1,
                    maximum=1000000,
                    default=1,
                ): "orbital number",
            }
        )
        self.orbital_number.setToolTip("first orbital is number 1")
        self.layout.addRow("orbital:", self.orbital_number)

        self.density_type = QComboBox()
        self.density_type.addItem("SCF", "SCF")
        self.density_type.addItem("MP2", "MP2")
        self.density_type.addItem("coupled cluster", "CC")
        self.density_type.addItem("configuration interaction", "CI")
        self.layout.addRow("density type:", self.density_type)

        self.operator = QComboBox()
        self.operator.addItems(["not applicable", "α", "β"])
        self.layout.addRow("spin operator:", self.operator)

        self.magnetic_field_direction = QComboBox()
        self.magnetic_field_direction.addItems(["X", "Y", "Z"])
        self.layout.addRow("magnetic field direction:", self.magnetic_field_direction)

        self.induced_field_direction = QComboBox()
        self.induced_field_direction.addItems(["X", "Y", "Z"])
        self.layout.addRow("induced field direction:", self.induced_field_direction)

        self.nucleus = QSpinBox()
        self.nucleus.setMinimum(1)
        self.nucleus.setMaximum(1000000)
        self.layout.addRow("nucleus number:", self.nucleus)

        self.grid_points = QSpinBox()
        self.grid_points.setMinimum(1)
        self.grid_points.setMaximum(1000)
        self.grid_points.setSingleStep(5)
        self.grid_points.setValue(80)
        self.grid_points.setSuffix("³")
        self.layout.addRow("grid points:", self.grid_points)

        self.memory = QSpinBox()
        self.memory.setMinimum(1)
        self.memory.setMaximum(100000000)
        self.memory.setSingleStep(500)
        self.memory.setSuffix(" MB")
        self.memory.setValue(4000)
        self.layout.addRow("memory limit:", self.memory)

        self.nprocs = QSpinBox()
        self.nprocs.setMaximum(os.cpu_count())
        self.nprocs.setMinimum(1)
        self.layout.addRow("processors:", self.nprocs)

        self.run = QPushButton("do it")
        self.run.clicked.connect(self.run_executable)
        self.layout.addRow(self.run)

        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        self.layout.addRow(self.status)
        
        self.plot_type.currentTextChanged.connect(self.update_plot_options)
        self.update_plot_options(self.plot_type.currentText())

    def update_plot_options(self, text):
        # some plot types don't use certain options
        # we hide them so they aren't distracting
        if text == "molecular orbital":
            self.layout.setRowVisible(self.orbital_number, True)
            self.layout.setRowVisible(self.operator, True)
            self.layout.setRowVisible(self.density_type, False)
            self.layout.setRowVisible(self.nprocs, False)
            self.layout.setRowVisible(self.magnetic_field_direction, False)
            self.layout.setRowVisible(self.induced_field_direction, False)
            self.layout.setRowVisible(self.nucleus, False)

        if text == "electron density":
            self.layout.setRowVisible(self.orbital_number, False)
            self.layout.setRowVisible(self.operator, True)
            self.layout.setRowVisible(self.density_type, True)
            self.layout.setRowVisible(self.nprocs, False)
            self.layout.setRowVisible(self.magnetic_field_direction, False)
            self.layout.setRowVisible(self.induced_field_direction, False)
            self.layout.setRowVisible(self.nucleus, False)

        if text == "spin density":
            self.layout.setRowVisible(self.orbital_number, False)
            self.layout.setRowVisible(self.operator, False)
            self.layout.setRowVisible(self.density_type, True)
            self.layout.setRowVisible(self.nprocs, False)
            self.layout.setRowVisible(self.magnetic_field_direction, False)
            self.layout.setRowVisible(self.induced_field_direction, False)
            self.layout.setRowVisible(self.nucleus, False)

        if text == "electrostatic potential":
            self.layout.setRowVisible(self.orbital_number, False)
            self.layout.setRowVisible(self.operator, False)
            self.layout.setRowVisible(self.density_type, True)
            self.layout.setRowVisible(self.nprocs, True)
            self.layout.setRowVisible(self.magnetic_field_direction, False)
            self.layout.setRowVisible(self.induced_field_direction, False)
            self.layout.setRowVisible(self.nucleus, False)

        if text == "magnetically-induced current density":
            self.layout.setRowVisible(self.orbital_number, False)
            self.layout.setRowVisible(self.operator, False)
            self.layout.setRowVisible(self.density_type, False)
            self.layout.setRowVisible(self.nprocs, False)
            self.layout.setRowVisible(self.magnetic_field_direction, True)
            self.layout.setRowVisible(self.induced_field_direction, False)
            self.layout.setRowVisible(self.nucleus, False)

        if text == "magnetic shielding density":
            self.layout.setRowVisible(self.orbital_number, False)
            self.layout.setRowVisible(self.operator, False)
            self.layout.setRowVisible(self.density_type, False)
            self.layout.setRowVisible(self.nprocs, False)
            self.layout.setRowVisible(self.magnetic_field_direction, True)
            self.layout.setRowVisible(self.induced_field_direction, True)
            self.layout.setRowVisible(self.nucleus, True)

    def run_executable(self, *args):
        # run different functions for different types of plots
        # each function determines what should be passed to orca_plot
        kind = self.plot_type.currentText()
        self.update.emit()
        if kind == "molecular orbital":
            self.run_orbitals(kind)
        
        elif kind in ["electron density", "spin density"]:
            self.run_density(kind)

        elif kind == "electrostatic potential":
            self.run_esp(kind)
        
        elif kind == "magnetically-induced current density":
            self.run_magind_density(kind)

        elif kind == "magnetic shielding density":
            self.run_magshield_density(kind)
        
        else:
            self.session.logger.warning("unknown plot type: %s" % kind)

    def run_subprocess(self, args):
        """
        runs orca_plot with the specified codes and returns the stdout and stderr
        the sequence of codes should, at the end, exit orca_plot
        otherwise ChimeraX will hang
        """
        # args[3] is the input file path
        if not args[3]:
            self.logger.error("you must specify an Fchk file")
            return "", ""
        
        exe_path = self.exe_path.text()
        memory = self.memory.value()
        
        self.session.logger.info("running <pre>%s</pre>" % " ".join(args), is_html=True)
        
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

        env = os.environ.copy()
        env["GAUSS_MEMDEF"] = "%iMB" % memory
        kwargs = {"env": env}
        if platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        infile = self.infile_path.text()
        try:
            proc = subprocess.Popen(
                args,
                encoding="utf-8",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(infile),
                **kwargs
            )
        except (FileNotFoundError, OSError):
            self.session.logger.error("%s does not exist. Ensure your path to cubegen is set correctly" % self.exe_path.text())
            self.status.showMessage("Failed to run cubegen - see log for more details", 5000)
            return "", ""
        
        if proc.poll() is not None:
            proc.kill()
        
        stdout, stderr = proc.communicate()
        if stderr:
            self.status.showMessage("failed to generate plot - see log for more details")
            self.session.logger.error("Error running cubegen - see log for details")
            self.session.logger.warning("<pre>" + stderr + "</pre>", is_html=True)
            self.session.logger.warning("<pre>" + stdout + "</pre>", is_html=True)
        else:
            self.status.showMessage("done running cubegen", 5000)
        
        return stdout, stderr

    def print_open_link(self, path):
        link = "<a class='cxcmd' href='cxcmd:open \"%s\"'>%s</a>" % (path, path)
        self.session.logger.info("output file: %s" % link, is_html=True)

    def run_orbitals(self, orbital_type):
        self.status.showMessage("starting to generate %s ..." % orbital_type)
        infile = self.infile_path.text()

        spin = self.operator.currentIndex()
        mo = "MO="
        if spin == 1:
            mo = "AMO="
        elif spin == 2:
            mo = "BMO="
        
        outfile = get_outfile(
            self.outfile_path.text(),
            infile=get_filename(infile, include_parent_dir=True),
            kind=mo + str(self.orbital_number.value()),
        )
        
        args = [
            self.exe_path.text(),
            "1",
            mo + str(self.orbital_number.value()),
            infile,
            outfile,
            str(self.grid_points.value()),
        ]

        stdout, stderr = self.run_subprocess(args)
        if os.path.exists(outfile):
            self.print_open_link(outfile)

    def run_density(self, density_type):
        self.status.showMessage("starting to generate %s ..." % density_type)
        infile = self.infile_path.text()

        dens = "Density="
        if "spin" not in density_type:
            spin = self.operator.currentIndex()
            if spin == 1:
                dens = "Alpha="
            if spin == 2:
                dens = "Beta="
        else:
            dens = "Spin="
        
        outfile = get_outfile(
            self.outfile_path.text(),
            infile=get_filename(infile, include_parent_dir=True),
            kind=dens + str(self.density_type.currentData()),
        )
        
        args = [
            self.exe_path.text(),
            "1",
            dens + str(self.density_type.currentData()),
            infile,
            outfile,
            str(self.grid_points.value()),
        ]
        
        stdout, stderr = self.run_subprocess(args)
        if os.path.exists(outfile):
            self.print_open_link(outfile)

    def run_esp(self, esp_type):
        self.status.showMessage("starting to generate %s ..." % esp_type)
        infile = self.infile_path.text()
        outfile = get_outfile(
            self.outfile_path.text(),
            infile=get_filename(infile, include_parent_dir=True),
            kind="Potential=%s" % self.density_type.currentData(),
        )
        args = [
            self.exe_path.text(),
            str(self.nprocs.value()),
            "Potential=%s" % self.density_type.currentData(),
            infile,
            outfile,
            str(self.grid_points.value()),
        ]
        
        stdout, stderr = self.run_subprocess(args)
        if os.path.exists(outfile):
            self.print_open_link(outfile)

    def run_magind_density(self, density_type):
        self.status.showMessage("starting to generate %s ..." % density_type)
        infile = self.infile_path.text()
        kind = "CurrentDensity=%s" % self.magnetic_field_direction.currentText()
        outfile = get_outfile(
            self.outfile_path.text(),
            infile=get_filename(infile, include_parent_dir=True),
            kind=kind,
        )
        args = [
            self.exe_path.text(),
            "1",
            kind,
            infile,
            outfile,
            str(self.grid_points.value()),
        ]
        
        stdout, stderr = self.run_subprocess(args)
        if os.path.exists(outfile):
            self.print_open_link(outfile)

    def run_magshield_density(self, density_type):
        self.status.showMessage("starting to generate %s ..." % density_type)
        infile = self.infile_path.text()
        kind = "ShieldingDensity=%s%s%i" % (
            self.magnetic_field_direction.currentText(),
            self.induced_field_direction.currentText(),
            self.nucleus.value(),
        )
        outfile = get_outfile(
            self.outfile_path.text(),
            infile=get_filename(infile, include_parent_dir=True),
            kind=kind,
        )
        args = [
            self.exe_path.text(),
            "1",
            kind,
            infile,
            outfile,
            str(self.grid_points.value()),
        ]
        
        stdout, stderr = self.run_subprocess(args)
        if os.path.exists(outfile):
            self.print_open_link(outfile)

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
            filter="Gaussian Formatted Checkpoint Files (*.fchk)",
            directory=dirname
        )

        if filename:
            self.infile_path.setText(filename)

    def open_set_outfile_path(self):
        filename, _ = QFileDialog.getSaveFileName(filter="Gaussian Cube files (*.cube)")

        if filename:
            self.outfile_path.setText(filename)

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
            outfile_path = kwargs["outfile_path"]
            self.outfile_path.setText(outfile_path)
        except KeyError:
            pass
        
        try:
            grid_points = kwargs["grid_points"]
            self.grid_points.setValue(grid_points)
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
        out["outfile_path"] = self.outfile_path.text()
        out["grid_points"] = self.grid_points.value()
        out["memory"] = self.memory.value()

        return out


class FormCHK(QWidget):
    update = Signal()

    def __init__(self, session, *args, **kwargs):
        """fill in UI widgets and set some defaults"""
        super().__init__(*args, **kwargs)
        self.session = session

        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        description = QLabel("Gaussian tool for converting checkpoints files into a text format")
        self.layout.addRow(description)
        
        exe_browse = QWidget()
        exe_browse_layout = QGridLayout(exe_browse)
        margins = exe_browse_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        exe_browse_layout.setContentsMargins(*new_margins)
        self.exe_path = QLineEdit()
        # TODO: load default from settings
        exe_default = "formchk"
        if platform == "win32":
            exe_default += ".exe"
        dirname = os.path.dirname(self.session.seqcrow_settings.settings.GAUSSIAN_EXE)
        self.exe_path.setText(os.path.join(dirname, exe_default))

        self.exe_browse_button = QPushButton("browse...")
        self.exe_browse_button.clicked.connect(self.open_set_exe_path)
        exe_browse_layout.addWidget(self.exe_path, 0, 0, Qt.AlignVCenter)
        exe_browse_layout.addWidget(self.exe_browse_button, 0, 1, Qt.AlignVCenter)
        exe_browse_layout.setColumnStretch(0, 1)
        exe_browse_layout.setColumnStretch(1, 0)
        self.layout.addRow("executable path:", exe_browse)

        infile_browse = QWidget()
        infile_browse_layout = QGridLayout(infile_browse)
        margins = infile_browse_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        infile_browse_layout.setContentsMargins(*new_margins)
        self.infile_path = QLineEdit()
        self.infile_path.setPlaceholderText("your Chk file")

        self.infile_browse_button = QPushButton("browse...")
        self.infile_browse_button.clicked.connect(self.open_set_infile_path)
        infile_browse_layout.addWidget(self.infile_path, 0, 0, Qt.AlignVCenter)
        infile_browse_layout.addWidget(self.infile_browse_button, 0, 1, Qt.AlignVCenter)
        infile_browse_layout.setColumnStretch(0, 1)
        infile_browse_layout.setColumnStretch(1, 0)
        self.layout.addRow("Chk path:", infile_browse)

        outfile_browse = QWidget()
        outfile_browse.setToolTip("""output destination\ncertain pattern substitutions can be made:
        $infile will be replaced with the basename of the input fchk file""")
        outfile_browse_layout = QGridLayout(outfile_browse)
        margins = outfile_browse_layout.contentsMargins()
        new_margins = (margins.left(), 0, margins.right(), 0)
        outfile_browse_layout.setContentsMargins(*new_margins)
        self.outfile_path = QLineEdit()
        self.outfile_path.setText("$infile.fchk")

        self.outfile_browse_button = QPushButton("browse...")
        self.outfile_browse_button.clicked.connect(self.open_set_outfile_path)
        outfile_browse_layout.addWidget(self.outfile_path, 0, 0, Qt.AlignVCenter)
        outfile_browse_layout.addWidget(self.outfile_browse_button, 0, 1, Qt.AlignVCenter)
        outfile_browse_layout.setColumnStretch(0, 1)
        outfile_browse_layout.setColumnStretch(1, 0)
        self.layout.addRow("output destination:", outfile_browse)

        self.run = QPushButton("do it")
        self.run.clicked.connect(self.run_executable)
        self.layout.addRow(self.run)

        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        self.layout.addRow(self.status)

    def run_executable(self, *args):
        exe_path = self.exe_path.text()
        
        kwargs = {}
        if platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        infile = self.infile_path.text()
        outfile = get_outfile(
            self.outfile_path.text(),
            infile=get_filename(infile, include_parent_dir=True),
        )
        
        args = [exe_path, infile, outfile]
        self.session.logger.info("running <pre>%s</pre>" % " ".join(args), is_html=True)

        try:
            proc = subprocess.Popen(
                args,
                encoding="utf-8",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(infile),
                **kwargs
            )
        except (FileNotFoundError, OSError):
            self.session.logger.error("%s does not exist. Ensure your path to formchk is set correctly" % self.exe_path.text())
            self.status.showMessage("Failed to run formchk - see log for more details", 5000)
            return "", ""
        
        if proc.poll() is not None:
            proc.kill()
        
        stdout, stderr = proc.communicate()
        if stderr:
            self.status.showMessage("failed to generate fchk file - see log for more details")
            self.session.logger.error("Error running formchk - see log for details")
            self.session.logger.warning("<pre>" + stderr + "</pre>", is_html=True)
            self.session.logger.warning("<pre>" + stdout + "</pre>", is_html=True)
        else:
            self.status.showMessage("done running formchk", 5000)
        
        self.print_open_link(outfile)
        
        return stdout, stderr

    def print_open_link(self, path):
        link = "<a class='cxcmd' href='cxcmd:open \"%s\"'>%s</a>" % (path, path)
        self.session.logger.info("output file: %s" % link, is_html=True)

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
            filter="Gaussian Checkpoint Files (*.fchk)",
            directory=dirname
        )

        if filename:
            self.infile_path.setText(filename)

    def open_set_outfile_path(self):
        filename, _ = QFileDialog.getSaveFileName(filter="Gaussian Formatted Checkpoint Files (*.fchk)")

        if filename:
            self.outfile_path.setText(filename)

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
            outfile_path = kwargs["outfile_path"]
            self.outfile_path.setText(outfile_path)
        except KeyError:
            pass

    def get_values(self):
        out = dict()
        out["exe_path"] = self.exe_path.text()
        out["infile_path"] = self.infile_path.text()
        out["outfile_path"] = self.outfile_path.text()

        return out
