from collections import OrderedDict

import numpy as np

from chimerax.atomic import get_triggers
from chimerax.core.tools import ToolInstance
from chimerax.core.models import REMOVE_MODELS

from Qt.QtCore import Qt
from Qt.QtGui import QGuiApplication, QBrush, QColor
from Qt.QtWidgets import (
    QGridLayout,
    QWidget,
    QFileDialog,
    QTabWidget, 
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QPushButton,
    QComboBox,
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

from matplotlib.figure import Figure
import matplotlib.patheffects as pe

from SEQCROW.widgets import FakeMenu
from AaronTools.const import UNIT


keyboardModifiers = QGuiApplication.keyboardModifiers

#matplotlib doesn't keep track of changes made with my mouse controls
#i could figure out how to do better mouse controls...
#or i could just disable the undo/redo buttons on the navbar
#i do this by making a new class because for some reason the 
#NavigationToolbar2QT.toolitems attribute is not instance-specific
class NavigationToolbar(NavigationToolbar2QT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    toolitems = list(NavigationToolbar2QT.toolitems)
    for i in range(0, len(toolitems)):
        if toolitems[i][0] in ['Back', 'Forward']:
            toolitems[i] = None
    
    toolitems = tuple(ti for ti in toolitems if ti is not None and ti != (None, None, None, None))
    
    def home(self, *args, **kwargs):
        """make pressing the home button autoscale the axes instead of whatever
        it normally does"""
        for ax in self.canvas.figure.get_axes():
            ax.autoscale()
        self.canvas.draw()

class EnergyPlot(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    
    def __init__(
        self,
        session,
        model,
        filereader,
        xlabel="iteration",
        ylabel=r"energy ($E_h$)",
        y_data=None,
    ):
        super().__init__(session, model.name)
        
        self.major_unit = None
        self.minor_unit = None
        self.minor_conversion = 1
        self.unit_type = "Energy"
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)    
        
        self.structure = model
        self.filereader = filereader

        self.display_name = "Thing per iteration for %s" % model.name     

        self._last_mouse_xy = None
        self._dragged = False
        self._min_drag = 10	# pixels
        self._drag_mode = None
        self.xlabel = xlabel
        self.ylabel = ylabel

        self.opened = False

        if y_data is None and "y_data" in filereader:
            y_data = filereader["y_data"]

        self._build_ui(y_data)
        if not self.opened:
            self.delete()
            return

        try:
            y_units = filereader["y_units"]
            self.energy_widgets[1].setCurrentIndex(y_units)
            self.switch_units(delete_unit_selector=False)
        except KeyError:
            pass

        self.press = None
        self.drag_prev = None
        self.dragging = False
        
        self._model_closed = self.session.triggers.add_handler(REMOVE_MODELS, self.check_closed_models)
        self._model_closed = self.session.triggers.add_handler(REMOVE_MODELS, self.check_closed_models)
        
        global_triggers = get_triggers()
        self._changes = global_triggers.add_handler("changes", self.check_changes)
        
        self.circle_current_cs()

    def _build_ui(self, y_data):
        layout = QGridLayout()
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        self.figure = Figure(figsize=(2,2))
        self.canvas = Canvas(self.figure)
        
        nrg_plot = QWidget()
        nrg_plot_layout = QGridLayout(nrg_plot)
        tabs.addTab(nrg_plot, "energy")
        
        ax = self.figure.add_axes((0.25, 0.20, 0.6, 0.60))

        fr = self.filereader
        if fr["all_geom"] is None:
            self.opened = False
            return

        if y_data is None:
            self.major_unit = "$E_h$"
            self.minor_unit = "kcal/mol"
            self.minor_conversion = UNIT.HART_TO_KCAL
            self.unit_type = "Energy"
            self.abbreviated_type = "E"
            
            self.data = OrderedDict()
            info = []
            for i, (step, cs_id) in enumerate(zip(fr["all_geom"], self.structure.coordset_ids)):
                info = step["data"]
                if "energy" not in info:
                    continue

                else:
                    self.data[cs_id] = {"energy": {"value": info["energy"]}}
                    if "gradient" in info:
                        self.data[cs_id].update(info["gradient"])
            
            if len(self.data) < len(self.structure.coordset_ids):
                if "energy" in info and "energy" in fr and info["energy"] != fr["energy"]:
                    self.data[self.structure.coordset_ids[-1]] = {"energy": {"value": fr["energy"]}}
                
                    if (
                        "gradient" in info and
                        "gradient" in fr and
                        info["gradient"] != fr["gradient"]
                    ) or (
                        "gradient" in fr and
                        not "gradient" in info
                    ):
                        self.data[self.structure.coordset_ids[-1]].update(fr["gradient"])
    
            if len(self.data) <= 1:
                self.opened = False
                # self.session.logger.error("not enough iterations to plot - %i found" % len(data))
                return
    
            self.xs = [x for x, y in self.data.items() if "energy" in y]
            self.ys = [y["energy"]["value"] for y in self.data.values()]

        else:
            self.ys = y_data
            self.xs = list(range(1, len(y_data) + 1))
            self.data = {i + 1: {} for i in range(0, len(y_data))}

        se = np.ptp(self.ys)
    
        self.nrg_plot = ax.plot(self.xs, self.ys, marker='o', c="#898989", markersize=3)
        self.nrg_plot = self.nrg_plot[0]
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_ylim(bottom=(min(self.ys) - se/10), top=(max(self.ys) + se/10))
        
        min_y = min(self.ys)
        minlocs = [cs_id for i, cs_id in enumerate(self.xs) if self.ys[i] == min_y]
        mins = [min_y for m in minlocs]        
        
        max_y = max(self.ys)
        maxlocs = [cs_id for i, cs_id in enumerate(self.xs) if self.ys[i] == max_y]
        maxs = [max_y for m in maxlocs]
    
        ax.scatter(minlocs, mins, marker='*', c='blue', s=25, zorder=100)
        ax.scatter(maxlocs, maxs, marker='*', c='red', s=25, zorder=100)
    
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0), useOffset=True)
        ax.ticklabel_format(axis='x', style='plain', useOffset=False)
        
        self.canvas.mpl_connect('button_release_event', self.unclick)
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.mpl_connect('motion_notify_event', self.drag)
        self.canvas.mpl_connect('scroll_event', self.zoom)

        self.annotation = ax.annotate(
            "", xy=(0,0),
            xytext=(0, 10),
            textcoords="offset points",
            fontfamily='sans-serif',
            path_effects=[pe.withStroke(linewidth=2, foreground="white")],
        )
        self.annotation.set_visible(False)

        ax.autoscale()
        self.canvas.draw()
        self.canvas.setMinimumWidth(400)
        self.canvas.setMinimumHeight(200)
        nrg_plot_layout.addWidget(self.canvas, 0, 0, 1, 3)
        
        toolbar_widget = QWidget()
        toolbar = NavigationToolbar(self.canvas, toolbar_widget)

        toolbar.setMaximumHeight(32)
        self.toolbar = toolbar
        nrg_plot_layout.addWidget(toolbar, 1, 0, 1, 3)
        
        self.energy_widgets = []
        if y_data is not None:
            nrg_type_widget = QLabel("unit type:")
            self.energy_widgets.append(nrg_type_widget)
            nrg_plot_layout.addWidget(nrg_type_widget, 2, 0, 1, 1)
            
            unit_types = QComboBox()
            self.energy_widgets.append(unit_types)
            unit_types.addItem("Energy (Hartree)")
            unit_types.setItemData(0, ["Eₕ", "kcal/mol", UNIT.HART_TO_KCAL, "E", "Energy"])
            unit_types.addItem("Energy (kcal/mol)")
            unit_types.setItemData(1, ["kcal/mol", None, 1, "E", "Energy"])
            unit_types.addItem("Energy (kJ/mol)")
            unit_types.setItemData(2, ["kJ/mol", "kcal/mol", 1. / 4.184, "E", "Energy"])
            unit_types.addItem("RMSD (Å)")
            unit_types.setItemData(3, ["Å", None, 1, "RMSD", "RMSD"])
            unit_types.addItem("time (fs)")
            unit_types.setItemData(4, ["fs", None, 1, "t", "time"])
            unit_types.addItem("time (ns)")
            unit_types.setItemData(5, ["ns", None, 1, "t", "time"])
            
            nrg_plot_layout.addWidget(unit_types, 2, 1, 1, 1)
            
            set_units = QPushButton("set")
            self.energy_widgets.append(set_units)
            set_units.clicked.connect(self.switch_units)
            nrg_plot_layout.addWidget(set_units, 2, 2, 1, 1)

        conv_widget = QWidget()
        conv_layout = QGridLayout(conv_widget)
        tabs.addTab(conv_widget, "convergence")
        
        conv_table = QTableWidget()
        conv_table.setEditTriggers(QTableWidget.NoEditTriggers)
        color = QColor(200, 235, 210)
        black = QColor(0, 0, 0)
        brush = QBrush(color)
        black_brush = QBrush(black)
        keys = set()
        for data in self.data.values():
            keys.update(set(data.keys()))
        keys = sorted(keys)
        conv_table.setColumnCount(len(keys))
        conv_table.setHorizontalHeaderLabels(keys)
        conv_table.setSelectionBehavior(QTableWidget.SelectRows)
        conv_table.setSelectionMode(QTableWidget.SingleSelection)
        for key, value in sorted(self.data.items(), key=lambda a: a[0]):
            row = conv_table.rowCount()
            conv_table.insertRow(row)
        
            for ndx, label in enumerate(keys):
                if label not in value:
                    continue
                widget = QTableWidgetItem()
                try:
                    if label == "energy":
                        widget.setData(Qt.DisplayRole, "%.5f" % float(value[label]["value"]))
                    else:
                        widget.setData(Qt.DisplayRole, "%.2e" % float(value[label]["value"]))
                    widget.setData(Qt.UserRole, key)
                    widget.setTextAlignment(Qt.AlignRight)
                    try:
                        if value[label]["converged"]:
                            widget.setBackground(brush)
                            widget.setForeground(black_brush)
                    except KeyError:
                        pass
                    
                    conv_table.setItem(row, ndx, widget)
                
                except ValueError:
                    continue
            

        for i in range(0, conv_table.columnCount()):
            conv_table.resizeColumnToContents(i)
        
        conv_table.itemSelectionChanged.connect(self.set_table_cs_id)
        self.conv_table = conv_table
        conv_layout.addWidget(conv_table)

        
        #menu bar for saving stuff
        menu = FakeMenu()
        file = menu.addMenu("Export")
        file.addAction("Save CSV...")
        
        file.triggered.connect(self.save)
        
        self._menu = menu
        layout.setMenuBar(menu)

        self.tool_window.ui_area.setLayout(layout)
        
        self.tool_window.manage(None)
        
        conv_table.scrollToBottom()
        self.tabs = tabs

        self.opened = True

    def switch_units(self, delete_unit_selector=True):
        major, minor, conversion, abbr_type, data_type = self.energy_widgets[1].currentData(role=Qt.UserRole)
        self.filereader["y_units"] = self.energy_widgets[1].currentIndex()
        self.major_unit = major
        self.minor_unit = minor
        self.minor_conversion = conversion
        self.unit_type = data_type
        self.abbreviated_type = abbr_type
        self.ylabel = "%s (%s)" % (self.unit_type, self.major_unit)
        if delete_unit_selector:
            for widget in self.energy_widgets:
                widget.deleteLater()
        ax = self.figure.gca()
        ax.set_ylabel(self.ylabel)
        self.canvas.draw()
        
        self.tabs.setTabText(1, self.unit_type)
        self.conv_table.setRowCount(0)
        if self.minor_unit:
            self.conv_table.setColumnCount(2)
            self.conv_table.setHorizontalHeaderLabels(
                [self.major_unit, self.minor_unit]
            )
        else:
            self.conv_table.setColumnCount(1)
            self.conv_table.setHorizontalHeaderLabels([self.major_unit])
        
        min_y = min(self.ys)
        for val in self.ys:
            row = self.conv_table.rowCount()
            self.conv_table.insertRow(row)
            major_item = QTableWidgetItem(repr(val))
            major_item.setData(Qt.UserRole, row + 1)
            self.conv_table.setItem(row, 0, major_item)
            if self.minor_unit:
                minor_item = QTableWidgetItem("%.2f" % (self.minor_conversion * (val - min_y)))
                self.conv_table.setItem(row, 1, minor_item)

    def check_changes(self, trigger_name=None, changes=None):
        if changes is not None:
            if self.structure in changes.modified_atomic_structures():
                self.circle_current_cs()

    def circle_current_cs(self):
        ax = self.figure.gca()
        for i, line in enumerate(ax.lines):
            if line.get_label() == "current_cs":
                ax.lines[i].remove()
                break
        
        cs_id = self.structure.active_coordset_id
        if cs_id not in self.xs:
            self.canvas.draw()
            return
        ax.plot(
            cs_id,
            self.ys[self.xs.index(cs_id)],
            marker='o',
            markersize=5,
            color='k',
            zorder=-1,
            fillstyle='none',
            label="current_cs",
        )
        self.canvas.draw()

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
        if filename:
            s = "iteration,data\n"
            for cs_id, nrg in zip(self.xs, self.ys):
                s += "%i,%f\n" % (cs_id, nrg)
                
            with open(filename, 'w') as f:
                f.write(s.strip())
                
            print("saved to %s" % filename)
    
    def set_table_cs_id(self):
        selection = self.conv_table.selectedItems()
        if not selection:
            return
        item = selection[0]
        cs_id = item.data(Qt.UserRole)
        self.structure.active_coordset_id = cs_id
    
    def zoom(self, event):
        if event.xdata is None:
            return
        a = self.figure.gca()
        x0, x1 = a.get_xlim()
        x_range = x1 - x0
        xdiff = -0.05 * event.step * x_range
        xshift = 0.2 * (event.xdata - (x0 + x1)/2)
        nx0 = x0 - xdiff + xshift
        nx1 = x1 + xdiff + xshift
        
        y0, y1 = a.get_ylim()
        y_range = y1 - y0
        ydiff = -0.05 * event.step * y_range
        yshift = 0.2 * (event.ydata - (y0 + y1)/2)
        ny0 = y0 - ydiff + yshift
        ny1 = y1 + ydiff + yshift

        a.set_xlim(nx0, nx1)
        a.set_ylim(ny0, ny1)
        self.canvas.draw()
    
    def move(self, dx, dy):
        win = self.tool_window.ui_area
        w,h = win.width(), win.height()
        if w == 0 or h == 0:
            return
        a = self.figure.gca()
        x0, x1 = a.get_xlim()
        xs = dx/w * (x1-x0)
        nx0, nx1 = x0-xs, x1-xs
        y0, y1 = a.get_ylim()
        ys = dy/h * (y1-y0)
        ny0, ny1 = y0-ys, y1-ys
        a.set_xlim(nx0, nx1)
        a.set_ylim(ny0, ny1)
        self.canvas.draw()

    def onclick(self, event):
        if self.toolbar.mode != "":
            return

        self.press = event.x, event.y, event.xdata, event.ydata

    def unclick(self, event):
        if self.toolbar.mode != "":
            return

        modifiers = keyboardModifiers()
        #matplotlib's mouse event never sets the 'key' attribute for me
        #That's fine.
        #I'll just get my key presses from pyqt5.
        if modifiers != Qt.NoModifier and event.button == 1:
            a = self.figure.gca()
            a.autoscale()
            self.canvas.draw()        

        elif not self.dragging and event.button == 1 and event.key is None:
            self.change_coordset(event)
            
        self.press = None
        self.drag_prev = None
        self.dragging = False

    def change_coordset(self, event):
        if event.xdata is not None:
            x = int(round(event.xdata))
            if x > self.structure.num_coordsets:
                self.structure.active_coordset_id = self.structure.num_coordsets
            elif x < 1:
                self.structure.active_coordset_id = 1
            else:
                self.structure.active_coordset_id = x

    def update_label(self, cs_id, ndx, align_left, align_bottom):
        self.annotation.xy = (cs_id, self.ys[ndx])
        if self.major_unit:
            text = "%s=%s %s" % (self.abbreviated_type, repr(self.ys[ndx]), self.major_unit)
            if self.ys[ndx] == max(self.ys):
                text += " (maxima)" 
            elif self.ys[ndx] == min(self.ys):
                text += " (minima)"
            if self.minor_unit:
                text += "\n"
                text += "$\Delta %s$ = %.1f kcal/mol" % (
                    self.abbreviated_type,
                    self.minor_conversion * (self.ys[ndx] - self.ys[0]),
                )
        
        else:
            text = "%s\n" % repr(self.ys[ndx])
            text += r"$\Delta$ = %f" % (self.ys[ndx] - self.ys[0])
        
        self.annotation.set_text(text)
        if align_left:
            self.annotation.set_ha("left")
        else:
            self.annotation.set_ha("right")
    
        if align_bottom:
            self.annotation.set_va("bottom")
        else:
            self.annotation.set_va("top")
    
    def update_hover(self, cs_id, ndx):  
        ax = self.figure.gca()
        for i, line in enumerate(ax.lines):
            if line.get_label() == "hover":
                ax.lines[i].remove()
                break
        
        ax.plot(
            cs_id,
            self.ys[ndx],
            marker='o',
            markersize=5,
            color='gray',
            zorder=-1,
            label="hover",
        )
    
    def drag(self, event):
        modifiers = keyboardModifiers()
        if self.toolbar.mode != "":
            return
        #matplotlib's mouse event never sets the 'key' attribute for me
        #That's fine.
        #I'll just get my key presses from pyqt5.
        elif modifiers != Qt.NoModifier:
            return
        elif event.button == 1:
            vis = self.annotation.get_visible()
            if event.xdata:
                cs_id = max(self.xs[0], int(round(event.xdata)))
                cs_id = min(self.xs[-1], cs_id)
                ndx = self.xs.index(cs_id)
                self.update_hover(cs_id, ndx)
                w, h = self.canvas.get_width_height()
                self.update_label(
                    cs_id, ndx, event.x < w / 2, event.y < h / 2
                )
                self.annotation.set_visible(True)
                self.canvas.draw()
            return self.change_coordset(event)
        elif self.press is None:
            vis = self.annotation.get_visible()
            on_item, ndx = self.nrg_plot.contains(event)
            if on_item:
                ndx = ndx['ind'][0]
                cs_id = self.xs[ndx]
                w, h = self.canvas.get_width_height()
                self.update_label(
                    cs_id, ndx, event.x < w / 2, event.y < h / 2
                )
                self.update_hover(cs_id, ndx)
                self.annotation.set_visible(True)
                self.canvas.draw()
            else:
                if vis:
                    self.annotation.set_visible(False)
                    ax = self.figure.gca()
                    for i, line in enumerate(ax.lines):
                        if line.get_label() == "hover":
                            ax.lines[i].remove()
                            break
                    self.canvas.draw()
            return
        elif event.button != 2:
            return
            
        x, y, xpress, ypress = self.press
        dx = event.x - x
        dy = event.y - y
        drag_dist = np.linalg.norm([dx, dy])
        if self.dragging or drag_dist >= self._min_drag or event.button == 2:
            self.dragging = True
            if self.drag_prev is not None:
                x, y, xpress, ypress = self.drag_prev
                dx = event.x - x
                dy = event.y - y
            
            self.drag_prev = event.x, event.y, event.xdata, event.ydata
            self.move(dx, dy)

    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")

    def check_closed_models(self, name, models):
        if self.structure in models:
            global_triggers = get_triggers()
            global_triggers.remove_handler(self._changes)
            self.delete()
    
    def delete(self):
        if self.opened:
            self.session.triggers.remove_handler(self._model_closed)
            global_triggers = get_triggers()
            global_triggers.remove_handler(self._changes)

        super().delete()
