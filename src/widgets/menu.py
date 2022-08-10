from Qt.QtCore import Qt
from Qt.QtWidgets import QPushButton, QHBoxLayout, QWidget, QMenu


class FakeMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def addMenu(self, text):
        """adds a menu titled 'text' and returns the corresponding QMenu"""
        pushbutton = QPushButton(text)
        pushbutton.setFlat(True)
        menu = QMenu(pushbutton)
        pushbutton.setMenu(menu)
        self.layout.addWidget(pushbutton, stretch=0, alignment=Qt.AlignLeft)
        n_widgets = self.layout.count()
        self.layout.setStretch(n_widgets - 1, 1)
        if n_widgets > 1:
            self.layout.setStretch(n_widgets - 2, 0)
        return menu