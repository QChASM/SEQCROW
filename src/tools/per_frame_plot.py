import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.core.models import REMOVE_MODELS

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout, QWidget, QToolBar

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class EnergyPlot(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    
    def __init__(self, session, model):
        super().__init__(session, model.name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)    
        
        self.structure = model

        self.display_name = "Thing per iteration for %s" % model.name     

        self._last_mouse_xy = None
        self._dragged = False
        self._min_drag = 10	# pixels
        self._drag_mode = None

        self._build_ui()
        self.press = None
        self.drag_prev = None
        self.dragging = False
        
        self.session.triggers.add_handler(REMOVE_MODELS, self.check_closed_models)
        
    def _build_ui(self):
        font = self.tool_window.ui_area.font()
        font_name = QFont.family(font)
        layout = QGridLayout()
        
        self.figure = Figure(figsize=(2,2))
        self.canvas = Canvas(self.figure)
        
        ax = self.figure.add_axes((0.22, 0.22, 0.66, 0.66))

        data = []
        for step in self.structure.aarontools_filereader.all_geom:
            info = [item for item in step if isinstance(item, dict) and "energy" in item][0]
            data.append(info["energy"])

        self.ys = data

        se = np.ptp(data)
    
        self.nrg_plot = ax.plot(self.structure.coordset_ids, data, marker='o', c='gray')
        self.nrg_plot = self.nrg_plot[0]
        ax.set_xlabel('iteration', fontfamily=font_name)
        ax.set_ylabel(r'energy ($E_h$)', fontfamily=font_name)
        ax.set_ylim(bottom=(min(data) - se/10), top=(max(data) + se/10))
        
        ax.hlines(min(data), 1, self.structure.num_coordsets, colors='blue', linestyles='dashed')
        ax.hlines(max(data), 1, self.structure.num_coordsets, colors='red', linestyles='dashed')
    
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0), useOffset=True)
        ax.ticklabel_format(axis='x', style='plain', useOffset=False)
        
        self.canvas.draw()
        
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.mpl_connect('button_release_event', self.unclick)
        self.canvas.mpl_connect('motion_notify_event', self.drag)
        self.canvas.wheelEvent = self._wheel_event

        self.annotation = ax.annotate("", xy=(0,0), xytext=(0, 10), textcoords="offset points", fontfamily=font_name)
        self.annotation.set_visible(False)

        layout.addWidget(self.canvas)
        
        toolbar_widget = QWidget()
        toolbar = NavigationToolbar(self.canvas, toolbar_widget)
        toolbar.setMaximumHeight(24)
        self.toolbar = toolbar
        layout.addWidget(toolbar)
                
        self.tool_window.ui_area.setLayout(layout)
        
        self.tool_window.manage(None)
        
    def zoom(self, factor):
        '''
        Zoom plot objects by specified factor by changing
        the displayed limits of the plot.  Objects do not change size.
        '''
        a = self.figure.gca()
        x0, x1 = a.get_xlim()
        xmid, xsize = 0.5*(x0+x1), x1-x0
        xh = 0.5*xsize/factor
        nx0, nx1 = xmid-xh, xmid+xh
        y0, y1 = a.get_ylim()
        ymid, ysize = 0.5*(y0+y1), y1-y0
        yh = 0.5*ysize/factor
        ny0, ny1 = ymid-yh, ymid+yh
        a.set_xlim(nx0, nx1)
        a.set_ylim(ny0, ny1)
        self.canvas.draw()    
    
    def move(self, dx, dy):
        '''Move plot objects by delta values in window pixels.'''

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
        
    def _wheel_event(self, event):
        #copy-pasted from chimerax.interfaces.Graph
        delta = event.angleDelta().y()  # Typically 120 per wheel click, positive down.
        from math import exp
        factor = exp(delta / 1200)
        self.zoom(factor)

    def onclick(self, event):
        #print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #    ('double' if event.dblclick else 'single', event.button,
        #    event.x, event.y, event.xdata, event.ydata))
        if self.toolbar.mode != "":
            return
        self.press = event.x, event.y, event.xdata, event.ydata
        
        if event.dblclick and event.button == 2:
            a = self.figure.gca()
            a.autoscale()
            self.canvas.draw()
            
    def unclick(self, event):
        if self.toolbar.mode != "":
            return
            
        if not self.dragging and event.button == 1:
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
        self.annotation.set_text(repr(self.ys[ndx]))
    
    def drag(self, event):
        if self.toolbar.mode != "":
            return
        elif event.button == 1:
            return self.change_coordset(event)
        elif self.press is None:
            vis = self.annotation.get_visible()
            on_item, ndx = self.nrg_plot.contains(event)
            if on_item:
                self.update_label(ndx['ind'][0])
                self.annotation.set_visible(True)
                self.canvas.draw()
            else:
                if vis:
                    self.annotation.set_visible(False)
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
            
    def check_closed_models(self, name, models):
        if self.structure in models:
            self.delete()