import re

import numpy as np 

from Qt.QtCore import Qt, QLocale
from Qt.QtGui import (
    QDoubleValidator,
    QValidator,
    QPainter,
)
from Qt.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QLineEdit,
    QPushButton,
    QToolButton,
    QGridLayout,
    QAbstractButton,
    QStyle,
    QStyleOption,
)

# some widgets from another program I was making

class IntegerOption(QSpinBox):
    """spinbox for integer options"""
    
    def __init__(
        self,
        *args,
        minimum=0,
        maximum=100,
        increment=1,
        prefix=None,
        suffix=None,
        default=None,
        tooltip=None,
        mapping=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setSingleStep(increment)
        if default is not None:
            self.setValue(default)
        if tooltip is not None:
            self.setToolTip(tooltip)
        if prefix:
            self.setPrefix(prefix)
        if suffix:
            self.setSuffix(suffix)
        self.mapping = mapping
    
    def value(self):
        value = super().value()
        if self.mapping:
            return self.mapping(value)
        return value

    def wheelEvent(self, event):
        pass


class DecimalOption(QDoubleSpinBox):
    """spinbox for floating point options in standard notation"""

    def __init__(
        self,
        *args,
        minimum=0,
        maximum=100,
        increment=None,
        decimals=None,
        prefix=None,
        suffix=None,
        default=None,
        tooltip=None, 
        mapping=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        if decimals is None:
            decimals = max(2, abs(np.log10(maximum - minimum)))
        self.setDecimals(decimals)
        if increment is None:
            increment = 10 ** (1 - decimals)
        self.setSingleStep(increment)
        if default is not None:
            self.setValue(default)
        if tooltip is not None:
            self.setToolTip(tooltip)
        if prefix:
            self.setPrefix(prefix)
        if suffix:
            self.setSuffix(suffix)
        self.mapping = mapping
    
    def value(self):
        value = super().value()
        if self.mapping:
            return self.mapping(value)
        return value

    def wheelEvent(self, event):
        # prevent scroll wheel from chaning things
        # we do this b/c someone could be scrolling through the
        # options and accidentally change something
        pass


class PercentOption(DecimalOption):
    """floating point option to use when value can range from 0 to 1"""
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            minimum=0.0,
            maximum=100.0,
            suffix="%",
            mapping=lambda x: x / 100,
            **kwargs,
        )


class BooleanOption(QCheckBox):
    """true/false option"""

    def __init__(
        self,
        *args,
        default=None,
        tooltip=None, 
        mapping=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if default is not None:
            self.setChecked(default)
        if tooltip is not None:
            self.setToolTip(tooltip)
        self.mapping = mapping
    
    def value(self):
        value = self.isChecked()
        if self.mapping:
            return self.mapping(value)
        return value


class Choices(QWidget):
    """thing for when there is a list of possible options"""
    def __init__(
        self,
        *args,
        options=None,
        map_none_to_nonetype=True,
        default=None,
        tooltip=None,
        mapping=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.map_none_to_nonetype = map_none_to_nonetype

        self._options = options
        self._ndx_map = dict()

        if tooltip is not None:
            self.setToolTip(tooltip)
        
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._choices = QComboBox()
        # prevent scroll wheel from chaning things
        # we do this b/c someone could be scrolling through the
        # options and accidentally change something
        self._choices.wheelEvent = lambda x: None
        self._layout.addWidget(self._choices, stretch=1)
        for i, item in enumerate(options):
            label = item
            if isinstance(options, dict):
                label = options[item]
            if not isinstance(label, str):
                raise TypeError("%s labels must be str" % self.__class__.__name__)
            self._choices.addItem(label)
            self._ndx_map[i] = item
            
        self._choices.currentIndexChanged.connect(self._check_selected_choice)
        
        if default is None:
            default = "none"
        
        ndx = self._choices.findText(
            default, flags=Qt.MatchFixedString
        )
        if ndx > 0:
            self._choices.setCurrentIndex(ndx)
        else:
            # make sure widgets show if the first item
            # has widgets
            self._check_selected_choice(0)
        self.mapping = mapping
    
    def _check_selected_choice(self, ndx):
        if not isinstance(self._options, dict):
            return
        old_widget = self._layout.itemAt(1)
        if old_widget:
            old_widget.widget().setParent(None)
        value = self._ndx_map[ndx]
        if not isinstance(value, QWidget):
            return
        self._layout.addWidget(value, stretch=3)
    
    def value(self):
        ndx = self._choices.currentIndex()
        value = self._ndx_map[ndx]
        if isinstance(value, str):
            if self.map_none_to_nonetype and value.lower() == "none":
                return None
            if self.mapping:
                return self.mapping(value)
            return value
        value = value.value()
        if self.mapping:
            return self.mapping(value)
        return value
