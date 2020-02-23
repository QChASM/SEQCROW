from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.ui.widgets.htmlview import HtmlView

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout

class LiteratureBrowser(ChildToolWindow):
    # Lit that makes you intellectually Richer
    #
    # this is lit
    #
    # take a look
    # it's in a peer-reviewed journal article
    # reading literature
    def __init__(self, tool_instance, title, url, **kwargs):
        super().__init__(tool_instance, title, **kwargs)
        
        self.start_link = url
        
        self._build_ui()
        
    def _build_ui(self):
        layout = QGridLayout()
        
        self.browser = HtmlView()
        self.browser.setUrl(self.start_link)
        layout.addWidget(self.browser)
        
        self.ui_area.setLayout(layout)
        
        self.manage(None, allowed_areas=Qt.NoDockWidgetArea) 
        #still docks if you double click it tho...
        #thanks Qt...