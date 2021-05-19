import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.core.models import REMOVE_MODELS

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QGridLayout, QWidget, QMenuBar, QAction, QFileDialog

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.backend_bases import MouseEvent

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

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
    
    def __init__(self, session, model, filereader):
        super().__init__(session, model.name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)    
        
        self.structure = model
        self.filereader = filereader

        self.display_name = "Thing per iteration for %s" % model.name     

        self._last_mouse_xy = None
        self._dragged = False
        self._min_drag = 10	# pixels
        self._drag_mode = None

        self._build_ui()

        self.press = None
        self.drag_prev = None
        self.dragging = False
        
        self._model_closed = self.session.triggers.add_handler(REMOVE_MODELS, self.check_closed_models)

    def _build_ui(self):
        layout = QGridLayout()
        
        self.figure = Figure(figsize=(2,2))
        self.canvas = Canvas(self.figure)
        
        ax = self.figure.add_axes((0.15, 0.20, 0.80, 0.70))

        fr = self.filereader
        if fr.all_geom is None:
            self.opened = False
            return

        data = []
        for step in fr.all_geom:
            info = [item for item in step if isinstance(item, dict) and "energy" in item]
            if len(info) < 1:
                #we will be unable to load an enegy plot because some structure does not have an associated energy
                self.opened = False
                self.session.logger.error("not enough iterations to plot - %i found" % len(info))
                return
            else:
                info = info[0]
            data.append(info["energy"])
        
        if self.structure.num_coordsets > len(data):
            data.append(fr.other["energy"])

        self.ys = data

        se = np.ptp(data)
    
        self.nrg_plot = ax.plot(self.structure.coordset_ids, data, marker='o', c='gray', markersize=3)
        self.nrg_plot = self.nrg_plot[0]
        ax.set_xlabel('iteration')
        ax.set_ylabel(r'energy ($E_h$)')
        ax.set_ylim(bottom=(min(data) - se/10), top=(max(data) + se/10))
        
        minlocs = [self.structure.coordset_ids[i] for i in range(0, self.structure.num_coordsets) if data[i] == min(data)]
        mins = [min(data) for m in minlocs]        
        
        maxlocs = [self.structure.coordset_ids[i] for i in range(0, self.structure.num_coordsets) if data[i] == max(data)]
        maxs = [max(data) for m in maxlocs]
    
        ax.plot(minlocs, mins, marker='*', c='blue', markersize=5)
        ax.plot(maxlocs, maxs, marker='*', c='red', markersize=5)
    
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0), useOffset=True)
        ax.ticklabel_format(axis='x', style='plain', useOffset=False)
        
        self.canvas.mpl_connect('button_release_event', self.unclick)
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.mpl_connect('motion_notify_event', self.drag)
        self.canvas.mpl_connect('scroll_event', self.zoom)

        self.annotation = ax.annotate("", xy=(0,0), xytext=(0, 10), textcoords="offset points", fontfamily='Arial')
        self.annotation.set_visible(False)

        ax.autoscale()
        self.canvas.draw()
        self.canvas.setMinimumWidth(400)
        self.canvas.setMinimumHeight(200)
        layout.addWidget(self.canvas)
        
        toolbar_widget = QWidget()
        toolbar = NavigationToolbar(self.canvas, toolbar_widget)

        toolbar.setMaximumHeight(32)
        self.toolbar = toolbar
        layout.addWidget(toolbar)
        
        #menu bar for saving stuff
        menu = QMenuBar()
        file = menu.addMenu("&Export")
        file.addAction("&Save CSV...")
        
        file.triggered.connect(self.save)
        
        menu.setNativeMenuBar(False)
        self._menu = menu
        layout.setMenuBar(menu)
        
        self.tool_window.ui_area.setLayout(layout)
        
        self.tool_window.manage(None)
        
        self.opened = True

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
        if filename:
            s = "iteration,energy\n"
            for i, nrg in enumerate(self.ys):
                s += "%i,%f\n" % (self.structure.coordset_ids[i], nrg)
                
            with open(filename, 'w') as f:
                f.write(s.strip())
                
            print("saved to %s" % filename)
    
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

    def update_label(self, ndx):
        self.annotation.xy = (self.structure.coordset_ids[ndx], self.ys[ndx])
        if self.ys[ndx] == max(self.ys):
            self.annotation.set_text("%s (maxima)" % repr(self.ys[ndx]))
        elif self.ys[ndx] == min(self.ys):
            self.annotation.set_text("%s (minima)" % repr(self.ys[ndx]))
        else:
            self.annotation.set_text(repr(self.ys[ndx]))
    
    def update_hover(self, ndx):  
        ax = self.figure.gca()
        for line in ax.lines:
            if line.get_label() == "hover":
                ax.lines.remove(line)
                break
        
        hover_circle = ax.plot(
            self.structure.coordset_ids[ndx],
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
                ndx = max(0, int(round(event.xdata)) - 1)
                ndx = min(self.structure.num_coordsets - 1, ndx)
                self.update_hover(ndx)
                self.update_label(ndx)
                self.annotation.set_visible(True)
                self.canvas.draw()
            return self.change_coordset(event)
        elif self.press is None:
            vis = self.annotation.get_visible()
            on_item, ndx = self.nrg_plot.contains(event)
            if on_item:
                self.update_label(ndx['ind'][0])
                self.update_hover(ndx['ind'][0])
                self.annotation.set_visible(True)
                self.canvas.draw()
            else:
                if vis:
                    self.annotation.set_visible(False)
                    ax = self.figure.gca()
                    for line in ax.lines:
                        if line.get_label() == "hover":
                            ax.lines.remove(line)
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
            self.delete()
    
    def delete(self):
        self.session.triggers.remove_handler(self._model_closed)
        
        super().delete()    
    
    def close(self):
        self.session.triggers.remove_handler(self._model_closed)
        
        super().close()