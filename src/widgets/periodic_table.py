from chimerax.atomic.colors import element_color

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QPushButton, QGridLayout, QWidget, QStyle

from AaronTools.const import ELEMENTS, TMETAL


class ElementButton(QPushButton):
    Unchecked = 0
    Checked = 1
    Excluded = 2
    
    stateChanged = Signal([int])
    
    def __init__(self, element, *args, **kwargs):
        super().__init__(element, *args, **kwargs)

        self._tristate = False

        self.state = 0
        self.setMinimumWidth(int(1.3*self.fontMetrics().boundingRect("QQ").width()))
        self.setMaximumWidth(int(1.3*self.fontMetrics().boundingRect("QQ").width()))
        self.setMinimumHeight(int(1.5*self.fontMetrics().boundingRect("QQ").height()))
        self.setMaximumHeight(int(1.5*self.fontMetrics().boundingRect("QQ").height()))
        
        self.ele_color = tuple(list(element_color(ELEMENTS.index(element)))[:-1])
        self.setStyleSheet("QPushButton { background: ghostwhite; color: lightgray; font-weight: normal; }")

        self.clicked.connect(self._changeState)
    
    def _changeState(self, bool=None, state=None):
        if self._tristate:
            self.state = (self.state + 1) % 3        
        elif not self._tristate:
            self.state = (self.state + 1) % 2

        if state is not None:
            self.state = state

        if self.state == self.Unchecked:
            self.setStyleSheet("QPushButton { background: ghostwhite; color: lightgray; font-weight: normal; }")
        elif self.state == self.Checked:
            #weird function to decide if text color is white or black based on jmol color
            #it's harder to see white on green, but easier to see white on blue
            self.setStyleSheet("QPushButton { background: rgb(%i, %i, %i); color: %s; font-weight: bold; }" % (*self.ele_color, 'white' if sum(int(x < 150) - int(x > 250) for x in self.ele_color) - int(self.ele_color[1] > 200) + int(self.ele_color[2] > 200) >= 2 else 'black'))
        elif self.state == self.Excluded:
            self.setStyleSheet("QPushButton { background: black; color: gray; font-weight: normal; }")
        
        self.stateChanged.emit(self.state)
    
    def setState(self, state):
        self._changeState(state=state)
    
    def setTristate(self, b):
        self._tristate = b

class PeriodicTable(QWidget):
    elementSelectionChanged = Signal()
    
    def __init__(self, *args, initial_elements=[], select_multiple=True, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._elements = {ele: ElementButton(ele) for ele in ELEMENTS if not any(ele == x for x in ['Bq', 'X'])}
        for ele in self._elements.keys():
            self._elements[ele].setTristate(False)
            if select_multiple:
                self._elements[ele].stateChanged.connect(lambda state, ele=ele: self.elementSelectionChanged.emit())
            else:
                self._elements[ele].stateChanged.connect(lambda state, ele=ele: self._single_ele_clicked(state, ele))
        
        elements_widget = QWidget()
        elements_layout = QGridLayout(elements_widget)
        elements_layout.setContentsMargins(0, 0, 0, 0)

        elements_layout.addWidget(self._elements['H'],  0,  0, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['He'], 0, 17, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Li'], 1,  0, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Be'], 1,  1, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['B'],  1, 12, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['C'],  1, 13, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['N'],  1, 14, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['O'],  1, 15, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['F'],  1, 16, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ne'], 1, 17, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Na'], 2,  0, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Mg'], 2,  1, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Al'], 2, 12, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Si'], 2, 13, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['P'],  2, 14, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['S'],  2, 15, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Cl'], 2, 16, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ar'], 2, 17, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['K'],  3,  0, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ca'], 3,  1, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Sc'], 3,  2, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ti'], 3,  3, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['V'],  3,  4, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Cr'], 3,  5, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Mn'], 3,  6, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Fe'], 3,  7, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Co'], 3,  8, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ni'], 3,  9, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Cu'], 3, 10, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Zn'], 3, 11, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ga'], 3, 12, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ge'], 3, 13, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['As'], 3, 14, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Se'], 3, 15, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Br'], 3, 16, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Kr'], 3, 17, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Rb'], 4,  0, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Sr'], 4,  1, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Y'],  4,  2, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Zr'], 4,  3, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Nb'], 4,  4, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Mo'], 4,  5, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Tc'], 4,  6, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ru'], 4,  7, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Rh'], 4,  8, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Pd'], 4,  9, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ag'], 4, 10, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Cd'], 4, 11, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['In'], 4, 12, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Sn'], 4, 13, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Sb'], 4, 14, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Te'], 4, 15, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['I'],  4, 16, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Xe'], 4, 17, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Cs'], 5,  0, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ba'], 5,  1, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Hf'], 5,  3, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ta'], 5,  4, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['W'],  5,  5, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Re'], 5,  6, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Os'], 5,  7, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ir'], 5,  8, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Pt'], 5,  9, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Au'], 5, 10, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Hg'], 5, 11, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Tl'], 5, 12, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Pb'], 5, 13, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Bi'], 5, 14, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Po'], 5, 15, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['At'], 5, 16, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Rn'], 5, 17, Qt.AlignLeft | Qt.AlignTop)
        if 'Fr' in ELEMENTS:
            elements_layout.addWidget(self._elements['Fr'], 6,  0, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Ra'], 6,  1, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Rf'], 6,  3, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Db'], 6,  4, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Sg'], 6,  5, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Bh'], 6,  6, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Hs'], 6,  7, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Mt'], 6,  8, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Ds'], 6,  9, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Rg'], 6, 10, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Cn'], 6, 11, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Nh'], 6, 12, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Fl'], 6, 13, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Mc'], 6, 14, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Lv'], 6, 15, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Ts'], 6, 16, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Og'], 6, 17, Qt.AlignLeft | Qt.AlignTop)
        
        elements_layout.addWidget(self._elements['La'], 7,  2, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ce'], 7,  3, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Pr'], 7,  4, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Nd'], 7,  5, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Pm'], 7,  6, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Sm'], 7,  7, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Eu'], 7,  8, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Gd'], 7,  9, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Tb'], 7, 10, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Dy'], 7, 11, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Ho'], 7, 12, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Er'], 7, 13, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Tm'], 7, 14, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Yb'], 7, 15, Qt.AlignLeft | Qt.AlignTop)
        elements_layout.addWidget(self._elements['Lu'], 7, 16, Qt.AlignLeft | Qt.AlignTop)
        if 'Ac' in ELEMENTS:
            elements_layout.addWidget(self._elements['Ac'], 8,  2, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Th'], 8,  3, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Pa'], 8,  4, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['U'],  8,  5, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Np'], 8,  6, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Pu'], 8,  7, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Am'], 8,  8, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Cm'], 8,  9, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Bk'], 8, 10, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Cf'], 8, 11, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Es'], 8, 12, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Fm'], 8, 13, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Md'], 8, 14, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['No'], 8, 15, Qt.AlignLeft | Qt.AlignTop)
            elements_layout.addWidget(self._elements['Lr'], 8, 16, Qt.AlignLeft | Qt.AlignTop)
        
        if select_multiple:
            organic_button = QPushButton("organic chemists'")
            organic_button.setCheckable(True)
            organic_button.clicked.connect(self._select_ochem)
            #layout.addWidget(organic_button, 9, col, Qt.AlignTop)        
    
            z_lt_37_button = QPushButton("H-Kr")
            z_lt_37_button.setCheckable(True)
            z_lt_37_button.clicked.connect(self._select_z_lt_37)
            layout.addWidget(z_lt_37_button, 9, 0, Qt.AlignTop)        
    
            z_ge_37_button = QPushButton("row 5+")
            z_ge_37_button.setCheckable(True)
            z_ge_37_button.clicked.connect(self._select_z_ge_37)
            layout.addWidget(z_ge_37_button, 9, 1, Qt.AlignTop)
    
            z_le_86_button = QPushButton("H-Rn")
            z_le_86_button.setCheckable(True)
            z_le_86_button.clicked.connect(self._select_z_le_86)
            layout.addWidget(z_le_86_button, 9, 2, Qt.AlignTop)
    
            tm_button = QPushButton("transition metals")
            tm_button.setCheckable(True)
            tm_button.clicked.connect(self._select_tm)
            layout.addWidget(tm_button, 9, 3, Qt.AlignTop)       
    
            all_button = QPushButton("all")
            all_button.clicked.connect(self._select_all)
            all_button.clicked.connect(lambda *args: organic_button.setChecked(False))
            all_button.clicked.connect(lambda *args: tm_button.setChecked(False))        
            all_button.clicked.connect(lambda *args: organic_button.setChecked(False))
            all_button.clicked.connect(lambda *args: z_lt_37_button.setChecked(False))
            all_button.clicked.connect(lambda *args: z_ge_37_button.setChecked(False))
            all_button.clicked.connect(lambda *args: z_le_86_button.setChecked(False))
            layout.addWidget(all_button, 10, 0, Qt.AlignTop)
            
            invert = QPushButton("invert")
            invert.clicked.connect(self._invert)
            invert.clicked.connect(lambda *args: organic_button.setChecked(False))
            invert.clicked.connect(lambda *args: tm_button.setChecked(False))        
            invert.clicked.connect(lambda *args: organic_button.setChecked(False))
            invert.clicked.connect(lambda *args: z_lt_37_button.setChecked(False))
            invert.clicked.connect(lambda *args: z_ge_37_button.setChecked(False))
            invert.clicked.connect(lambda *args: z_le_86_button.setChecked(False))
            layout.addWidget(invert, 10, 2, Qt.AlignTop)
    
            clear = QPushButton("clear")
            clear.clicked.connect(self._clear)
            clear.clicked.connect(lambda *args: organic_button.setChecked(False))
            clear.clicked.connect(lambda *args: tm_button.setChecked(False))        
            clear.clicked.connect(lambda *args: organic_button.setChecked(False))
            clear.clicked.connect(lambda *args: z_lt_37_button.setChecked(False))
            clear.clicked.connect(lambda *args: z_ge_37_button.setChecked(False))
            clear.clicked.connect(lambda *args: z_le_86_button.setChecked(False))
            layout.addWidget(clear, 10, 1, Qt.AlignTop)
    
            reset = QPushButton("reset")
            reset.clicked.connect(self._reset)
            reset.clicked.connect(lambda *args: organic_button.setChecked(False))
            reset.clicked.connect(lambda *args: tm_button.setChecked(False))        
            reset.clicked.connect(lambda *args: organic_button.setChecked(False))
            reset.clicked.connect(lambda *args: z_lt_37_button.setChecked(False))
            reset.clicked.connect(lambda *args: z_ge_37_button.setChecked(False))
            reset.clicked.connect(lambda *args: z_le_86_button.setChecked(False))
            layout.addWidget(reset, 10, 3, Qt.AlignTop)
            
            layout.addWidget(elements_widget, 0, 0, 7, 4, Qt.AlignLeft | Qt.AlignTop)
    
            self.setSelectedElements(initial_elements)
            self._initial_elements = initial_elements
    
            layout.setRowStretch(0, 0)
            layout.setRowStretch(1, 0)
            layout.setRowStretch(2, 0)
            layout.setRowStretch(3, 0)
            layout.setRowStretch(4, 0)
            layout.setRowStretch(5, 0)
            layout.setRowStretch(6, 0)
            layout.setRowStretch(7, 0)
            layout.setRowStretch(8, 0)
            layout.setRowStretch(9, 0)
            layout.setRowStretch(10, 1)
            layout.setColumnStretch(0, 0)
            layout.setColumnStretch(1, 1)
            layout.setColumnStretch(2, 1)
            layout.setColumnStretch(3, 1)
        
        else:
            layout.addWidget(elements_widget)
            if len(initial_elements) > 0:
                self.setSelectedElements([initial_elements[0]])
                self._initial_elements = [initial_elements[0]]

    def _select_ochem(self, add):
        self.blockSignals(True)
        for ele in self._elements.keys():
            if any(ele == x for x in ['B', 'C', 'O', 'N', 'F', 'Cl', 'H', 'Br', 'I']):
                if add:
                    self._elements[ele].setState(ElementButton.Checked)
                else:
                    self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _select_all(self):
        self.blockSignals(True)
        for ele in self._elements.keys():
                self._elements[ele].setState(ElementButton.Checked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _select_tm(self, add):
        self.blockSignals(True)
        for ele in self._elements.keys():
            if any(ele == x for x in TMETAL.keys()):
                if add:
                    self._elements[ele].setState(ElementButton.Checked)
                else:
                    self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _select_z_lt_37(self, add):
        self.blockSignals(True)
        for ele in self._elements.keys():
            if ELEMENTS.index(ele) < 37:
                if add:
                    self._elements[ele].setState(ElementButton.Checked)
                else:
                    self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _select_z_le_86(self, add):
        self.blockSignals(True)
        for ele in self._elements.keys():
            if ELEMENTS.index(ele) <= 86:
                if add:
                    self._elements[ele].setState(ElementButton.Checked)
                else:
                    self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _select_z_ge_37(self, add):
        self.blockSignals(True)
        for ele in self._elements.keys():
            if ELEMENTS.index(ele) >= 37:
                if add:
                    self._elements[ele].setState(ElementButton.Checked)
                else:
                    self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _select_row_1(self, add):
        self.blockSignals(True)
        for ele in self._elements.keys():
            ndx = ELEMENTS.index(ele)
            if ndx <= 2 and ndx >= 1:
                if add:
                    self._elements[ele].setState(ElementButton.Checked)
                else:
                    self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _select_row_2(self, add):
        self.blockSignals(True)
        for ele in self._elements.keys():
            ndx = ELEMENTS.index(ele)
            if ndx <= 10 and ndx >= 3:
                if add:
                    self._elements[ele].setState(ElementButton.Checked)
                else:
                    self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _select_row_3(self, add):
        self.blockSignals(True)
        for ele in self._elements.keys():
            ndx = ELEMENTS.index(ele)
            if ndx <= 18 and ndx >= 11:
                if add:
                    self._elements[ele].setState(ElementButton.Checked)
                else:
                    self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _select_row_4(self, add):
        self.blockSignals(True)
        for ele in self._elements.keys():
            ndx = ELEMENTS.index(ele)
            if ndx <= 36 and ndx >= 19:
                if add:
                    self._elements[ele].setState(ElementButton.Checked)
                else:
                    self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _select_row_5(self, add):
        self.blockSignals(True)
        for ele in self._elements.keys():
            ndx = ELEMENTS.index(ele)
            if ndx <= 54 and ndx >= 37:
                if add:
                    self._elements[ele].setState(ElementButton.Checked)
                else:
                    self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _select_row_6(self, add):
        self.blockSignals(True)
        for ele in self._elements.keys():
            ndx = ELEMENTS.index(ele)
            if ndx <= 86 and ndx >= 55:
                if add:
                    self._elements[ele].setState(ElementButton.Checked)
                else:
                    self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _invert(self):
        self.blockSignals(True)
        for ele in self._elements.keys():
            if self._elements[ele].state == ElementButton.Checked:
                self._elements[ele].setState(ElementButton.Unchecked)
            else:
                self._elements[ele].setState(ElementButton.Checked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _clear(self):
        self.blockSignals(True)
        for ele in self._elements.keys():
            self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()

    def _single_ele_clicked(self, state, ele):
        if state == ElementButton.Checked:
            self.blockSignals(True)
            for ele2 in self._elements.keys():
                if ele2 == ele:
                    continue
                
                self._elements[ele2].setState(ElementButton.Unchecked)
            
            self.blockSignals(False)
        
        self.elementSelectionChanged.emit()

    def selectedElements(self, abbreviate=False):
        elements = []
        for ele in self._elements.keys():
            if self._elements[ele].state == ElementButton.Checked:
                elements.append(ele)
        
        if abbreviate:
            if all(x in elements for x in self._elements):
                elements = ['all']

            if all(x in elements for x in TMETAL):
                for x in TMETAL.keys():
                    elements.remove(x)
                
                elements.append('tm')

        return elements
    
    def _reset(self):
        self.setSelectedElements(self._initial_elements)
    
    def setSelectedElements(self, elements):
        self.blockSignals(True)
        for ele in self._elements.keys():
            if any(ele == x for x in elements):
                self._elements[ele].setState(ElementButton.Checked)
            else:
                self._elements[ele].setState(ElementButton.Unchecked)
        
        self.blockSignals(False)
        self.elementSelectionChanged.emit()
