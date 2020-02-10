import numpy as np

from chimerax.core.tools import ToolInstance

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QWidget, QToolBar

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class EnergyPlot(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    
    def __init__(self, session, model):
        super().__init__(session, model.name)
        
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)    
        
        self._model = model

        self.display_name = "Thing per iteration for %s" % model.name     

        self._last_mouse_xy = None
        self._dragged = False
        self._min_drag = 10	# pixels
        self._drag_mode = None

        self._build_ui()
        
    def _build_ui(self):
        layout = QGridLayout()
        
        self.figure = Figure(figsize=(2,2))
        self.canvas = Canvas(self.figure)
        
        ax = self.figure.add_subplot(111)

        data = [i for i in range(0, self._model.num_coordsets)]
    
        ax.plot(data, marker='o', c='black')
    
        self.canvas.draw()

        self.canvas.wheelEvent = self._wheel_event
        self.canvas.mousePressEvent = self._mouse_press
        self.canvas.mouseMoveEvent = self._mouse_move
        self.canvas.mouseReleaseEvent = self._mouse_release

        layout.addWidget(self.canvas)
        
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
    
    def move(self, delta_x, delta_y):
        '''Move plot objects by delta values in window pixels.'''
        win = self.tool_window.ui_area
        w,h = win.width(), win.height()
        if w == 0 or h == 0:
            return
        a = self.figure.gca()
        x0, x1 = a.get_xlim()
        xs = delta_x/w * (x1-x0)
        nx0, nx1 = x0-xs, x1-xs
        y0, y1 = a.get_ylim()
        ys = delta_y/h * (y1-y0)
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

    def _mouse_press(self, event):
        self._last_mouse_xy = (event.x(), event.y())
        self._dragged = False
        b = event.button()
        from PyQt5.QtCore import Qt
        if b == Qt.LeftButton:
            if self.is_alt_key_pressed(event) or self.is_command_key_pressed(event):
                drag_mode = 'translate'
            else:
                drag_mode = 'select'
        elif b == Qt.MiddleButton:
            drag_mode = 'translate'
        elif b == Qt.RightButton:
            if self.is_ctrl_key_pressed(event):
                drag_mode = 'select'	# Click on object (same as ctrl-left)
            else:
                drag_mode = 'translate'
        else:
            drag_mode = None

        self._drag_mode = drag_mode
        
    def _mouse_move(self, event):
        if self._last_mouse_xy is None:
            self._mouse_press(event)
            return 	# Did not get mouse down

        x, y = event.x(), event.y()
        lx, ly = self._last_mouse_xy
        dx, dy = x-lx, y-ly
        if abs(dx) < self._min_drag and abs(dy) < self._min_drag:
            return
        self._last_mouse_xy = (x,y)
        self._dragged = True

        mode = self._drag_mode
        if mode == 'zoom':
            # Zoom
            h = self.tool_window.ui_area.height()
            from math import exp
            factor = exp(3*dy/h)
            self.zoom(factor)
        elif mode == 'translate':
            # Translate plot
            self.move(dx, -dy)
    
    def _mouse_release(self, event):
        if not self._dragged and self._drag_mode == 'select':
            pass
            #item = self._clicked_item(event.x(), event.y())
            #self.mouse_click(item, event)

        self._last_mouse_xy = None
        self._dragged = False
        self._drag_mode = None
        
    def is_alt_key_pressed(self, event):
        from PyQt5.QtCore import Qt
        return event.modifiers() & Qt.AltModifier

    def is_command_key_pressed(self, event):
        from PyQt5.QtCore import Qt
        import sys
        if sys.platform == 'darwin':
            # Mac command-key gives Qt control modifier.
            return event.modifiers() & Qt.ControlModifier
        return False

    def is_ctrl_key_pressed(self, event):
        from PyQt5.QtCore import Qt
        import sys
        if sys.platform == 'darwin':
            # Mac ctrl-key gives Qt meta modifier and Mac Command key gives Qt ctrl modifier.
            return event.modifiers() & Qt.MetaModifier
        return event.modifiers() & Qt.ControlModifier