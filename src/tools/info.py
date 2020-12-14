from SEQCROW.widgets import FilereaderComboBox

from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence, QClipboard
from PySide2.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, \
                            QTabWidget, QHeaderView, QSizePolicy, QMenuBar, QAction, \
                            QFileDialog, QApplication

from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow, ChildToolWindow
from chimerax.core.settings import Settings


class _InfoSettings(Settings):
    AUTO_SAVE = {
        "include_header": True,
        "delimiter": "tab",
    }
   
   
class Info(ToolInstance):
    
    help = "https://github.com/QChASM/SEQCROW/wiki/File-Info-Tool"
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)
        
        self.settings = _InfoSettings(self.session, name)
        
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout()
        
        self.file_selector = FilereaderComboBox(self.session)
        self.file_selector.currentIndexChanged.connect(self.fill_table)
        layout.insertWidget(0, self.file_selector, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Data', 'Value'])
        self.table.horizontalHeader().setStretchLastSection(False)            
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        layout.insertWidget(1, self.table, 1)
        
        
        menu = QMenuBar()
        
        export = menu.addMenu("&Export")
        copy = QAction("&Copy CSV to clipboard", self.tool_window.ui_area)
        copy.triggered.connect(self.copy_csv)
        shortcut = QKeySequence(Qt.CTRL + Qt.Key_C)
        copy.setShortcut(shortcut)
        export.addAction(copy)
        
        save = QAction("&Save CSV...", self.tool_window.ui_area)
        save.triggered.connect(self.save_csv)
        #this shortcut interferes with main window's save shortcut
        #I've tried different shortcut contexts to no avail
        #thanks Qt...
        #shortcut = QKeySequence(Qt.CTRL + Qt.Key_S)
        #save.setShortcut(shortcut)
        #save.setShortcutContext(Qt.WidgetShortcut)
        export.addAction(save)

        delimiter = export.addMenu("Delimiter")
        
        # comma = QAction("comma", self.tool_window.ui_area, checkable=True)
        # comma.setChecked(self.settings.delimiter == "comma")
        # comma.triggered.connect(lambda *args, delim="comma": self.settings.__setattr__("delimiter", delim))
        # delimiter.addAction(comma)
        
        tab = QAction("tab", self.tool_window.ui_area, checkable=True)
        tab.setChecked(self.settings.delimiter == "tab")
        tab.triggered.connect(lambda *args, delim="tab": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(tab)
        
        # space = QAction("space", self.tool_window.ui_area, checkable=True)
        # space.setChecked(self.settings.delimiter == "space")
        # space.triggered.connect(lambda *args, delim="space": self.settings.__setattr__("delimiter", delim))
        # delimiter.addAction(space)
        
        semicolon = QAction("semicolon", self.tool_window.ui_area, checkable=True)
        semicolon.setChecked(self.settings.delimiter == "semicolon")
        semicolon.triggered.connect(lambda *args, delim="semicolon": self.settings.__setattr__("delimiter", delim))
        delimiter.addAction(semicolon)
        
        add_header = QAction("&Include CSV header", self.tool_window.ui_area, checkable=True)
        add_header.setChecked(self.settings.include_header)
        add_header.triggered.connect(self.header_check)
        export.addAction(add_header)
        
        # comma.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        # comma.triggered.connect(lambda *args, action=space: action.setChecked(False))
        # comma.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        # tab.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        # tab.triggered.connect(lambda *args, action=space: action.setChecked(False))
        tab.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        # space.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        # space.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        # space.triggered.connect(lambda *args, action=semicolon: action.setChecked(False))
        
        # semicolon.triggered.connect(lambda *args, action=comma: action.setChecked(False))
        semicolon.triggered.connect(lambda *args, action=tab: action.setChecked(False))
        # semicolon.triggered.connect(lambda *args, action=space: action.setChecked(False))

        menu.setNativeMenuBar(False)
        self._menu = menu
        layout.setMenuBar(menu)


        if len(self.session.filereader_manager.list()) > 0:
            self.fill_table(0)
        
        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)
    
    def header_check(self, state):
        """user has [un]checked the 'include header' option on the menu"""
        if state:
            self.settings.include_header = True
        else:
            self.settings.include_header = False

    def get_csv(self):
        if self.settings.delimiter == "comma":
            delim = ","
        elif self.settings.delimiter == "space":
            delim = " "
        elif self.settings.delimiter == "tab":
            delim = "\t"
        elif self.settings.delimiter == "semicolon":
            delim = ";"
            
        if self.settings.include_header:
            s = delim.join(["Data", "Value"])
            s += "\n"
        else:
            s = ""
        
        for i in range(0, self.table.rowCount()):
            s += delim.join([item.data(Qt.DisplayRole) for item in [self.table.item(i, j) for j in range(0, 2)]])
            s += "\n"
        
        return s
    
    def copy_csv(self):
        app = QApplication.instance()
        clipboard = app.clipboard()
        csv = self.get_csv()
        clipboard.setText(csv)
        self.session.logger.status("copied to clipboard")

    def save_csv(self):
        """save data on current tab to CSV file"""
        filename, _ = QFileDialog.getSaveFileName(filter="CSV Files (*.csv)")
        if filename:
            s = self.get_csv()
   
            with open(filename, 'w') as f:
                f.write(s.strip())
                
            self.session.logger.status("saved to %s" % filename)
    
    def fill_table(self, ndx):
        self.table.setRowCount(0)
        
        if ndx < 0:
            return
        
        fr = self.file_selector.currentData()
        for info in fr.other.keys():
            if any(isinstance(fr.other[info], obj) for obj in [str, float, int]):
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                item = QTableWidgetItem()
                info_name = info.replace("_", " ")
                if info == "mass":
                    info_name += " (kg)"
                elif info == "temperature":
                    info_name += " (K)"
                elif any(info == s for s in ["energy", "ZPVE", "enthalpy", "free_energy", "E_ZPVE"]):
                    info_name += " (Hartree)"
                item.setData(Qt.DisplayRole, info_name)
                self.table.setItem(row, 0, item)
                
                value = QTableWidgetItem()
                val = str(fr.other[info])
                value.setData(Qt.DisplayRole, val)
                self.table.setItem(row, 1, value)
            
            elif hasattr(fr.other[info], "__iter__") and all(isinstance(x, float) for x in fr.other[info]):
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                item = QTableWidgetItem()
                info_name = info.replace("_", " ")
                if info == "rotational_temperature":
                    info_name += " (K)"
                item.setData(Qt.DisplayRole, info_name)
                self.table.setItem(row, 0, item)
                
                value = QTableWidgetItem()
                value.setData(Qt.DisplayRole, ", ".join(["%.4f" % x for x in fr.other[info]]))
                self.table.setItem(row, 1, value)
    
    def delete(self):
        self.file_selector.deleteLater()

        return super().delete()    
    
    def close(self):
        self.file_selector.deleteLater()

        return super().close()