import numpy as np

from chimerax.core.tools import ToolInstance
from chimerax.ui import MainToolWindow

from Qt.QtCore import Qt
from Qt.QtWidgets import (
    QGridLayout,
    QGraphicsView,
    QGraphicsScene,
    QPushButton,
    QComboBox,
    QButtonGroup,
)


from SEQCROW.tools.structure_editing import _PTable
from SEQCROW.widgets import PeriodicTable, ElementButton


class MolGraphicsScene(QGraphicsScene):
    def __init__(self, *args, tools=None, element=None, **kwargs):
        self._tools = tools
        self._element = element
        super().__init__(*args, **kwargs)
    
    def mousePressEvent(self, event):
        print("click")
    
    def mouseReleaseEvent(self, event):
        point = event.scenePos()
        tool_id = self._tools.downId()
        if tool_id == 0:
            self.add_atom(self._element.text(), point)
            print("atom")
        if tool_id == 1:
            print("bond")
        elif tool_id == 2:
            print("eraser")
        print("unclick")

    def add_atom(self, element, point):
        atom = self.addText(element)
        rect = atom.boundingRect()
        x = point.x() - rect.width() / 2
        y = point.y() - rect.height() / 2
        atom.setPos(x, y)
    
    
class ToolButtonGroup:
    def __init__(self, *buttons, **kwargs):
        self.buttons = buttons
        for button in self.buttons:
            button.clicked.connect(lambda *args, b=button: self.toggle_buttons(b))
    
        self.buttons[0].setDown(True)
        if not isinstance(self.buttons[0], ElementButton):
            self.buttons[0].setCheckable(True)
            self.buttons[0].setChecked(True)
        else:
            self.buttons[0].setState(ElementButton.Checked)
        
        for button in self.buttons[1:]:
            button.setDown(False)
            if not isinstance(button, ElementButton):
                button.setCheckable(True)
                button.setChecked(False)
            else:
                button.setState(ElementButton.Unchecked)
    
    def toggle_buttons(self, button):
        button.setDown(True)
        if isinstance(button, ElementButton):
            button.setState(ElementButton.Checked)
        else:
            button.setChecked(True)
        
        for button2 in self.buttons:
            if button2 is button:
                continue
            if isinstance(button2, ElementButton):
                button2.setState(ElementButton.Unchecked)
            else:
                button2.setChecked(False)
            button2.setDown(False)
    
    def downId(self):
        res = 0
        for i, button in enumerate(self.buttons):
            if button.isChecked() or (isinstance(button, ElementButton) and button.state == ElementButton.Checked):
                print(i)
                res = i
        return res
    
    
class MolBuilder(ToolInstance):

    help = "TODO"
    SESSION_ENDURING = False
    SESSION_SAVE = False
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.tool_window = MainToolWindow(self)
        
        self.atoms = []
        self.coordinates = []
        self.connectivity = np.zeros((0,0))
        
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout()

        self.element_button = ElementButton("C")
        self.element_button.setState(ElementButton.Checked)
        self.element_button.clicked.disconnect(self.element_button._changeState)
        self.element_button.clicked.connect(self.open_ptable)
        layout.addWidget(self.element_button, 1, 0, 1, 1, Qt.AlignLeft)

        bond_button = QPushButton("bond")
        layout.addWidget(bond_button, 1, 1, 1, 1, Qt.AlignLeft)

        eraser = QPushButton("eraser")
        layout.addWidget(eraser, 1, 2, 1, 1, Qt.AlignLeft)

        self.tool_box = ToolButtonGroup(
            self.element_button,
            bond_button,
            eraser,
        )

        self.mol_scene = MolGraphicsScene(
            0, 0, 400, 350, tools=self.tool_box, element=self.element_button
        )
        mol_view = QGraphicsView(self.mol_scene)
        layout.addWidget(mol_view, 0, 0, 1, 6)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(None)

    def open_ptable(self):
        if self.tool_box.downId() != 0:
            return
        self.tool_window.create_child_window(
            "select element",
            window_class=_PTable,
            button=self.element_button,
        )
        self.element_button.setState(ElementButton.Checked)
