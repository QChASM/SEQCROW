import re

import numpy as np 

from Qt.QtCore import QLocale
from Qt.QtGui import (
    QValidator,
)
from Qt.QtWidgets import (
    QSpinBox,
    QDoubleSpinBox,
)

class FPSSpinBox(QSpinBox):
    """spinbox that makes sure the value goes evenly into 60"""
    def validate(self, text, pos):
        if pos < len(text) or pos == 0:
            return (QValidator.Intermediate, text, pos)
        
        try:
            value = int(text)
        except:
            return (QValidator.Invalid, text, pos)
        
        if 60 % value != 0:
            if pos == 1:
                return (QValidator.Intermediate, text, pos)
            else:
                return (QValidator.Invalid, text, pos)
        elif value > self.maximum():
            return (QValidator.Invalid, text, pos)
        elif value < self.minimum():
            return (QValidator.Invalid, text, pos)
        else:
            return (QValidator.Acceptable, text, pos)
    
    def fixUp(self, text):
        try:
            value = int(text)
            new_value = 1
            for i in range(1, value+1):
                if 60 % i == 0:
                    new_value = i
            
            self.setValue(new_value)
        
        except:
            pass
    
    def stepBy(self, step):
        val = self.value()
        while step > 0:
            val += 1
            while 60 % val != 0:
                val += 1
            step -= 1
        
        while step < 0:
            val -= 1
            while 60 % val != 0:
                val -= 1
            step += 1
        
        self.setValue(val)


class ScientificValidator(QValidator):
    """validator for scientific notation"""
    
    def __init__(self, minimum, maximum, decimals, parent=None):
        super().__init__(parent)
        self._minimum = minimum
        self._maximum = maximum
        self._decimals = decimals
        self.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
    
    def validate(self, text, ndx):
        if re.match("-?\d+(?:\.\d{0,%i})?(?:[Ee]-?\d+)?$" % self._decimals, text, re.MULTILINE):
            val = float(text)
            if val < self._minimum or val > self._maximum:
                if self.parent().hasFocus():
                    return (QValidator.Intermediate, text, ndx)
                return (QValidator.Invalid, text, ndx)
            return (QValidator.Acceptable, text, ndx)
        
        if re.match("-?\d+(?:\.(?:\d{,%i}?(?:[Ee]-?)?))?$" % self._decimals, text, re.MULTILINE) or not text:
            return (QValidator.Intermediate, text, ndx)
        if re.match("-?\d+(?:[Ee]-?)$", text, re.MULTILINE) or not text:
            return (QValidator.Intermediate, text, ndx)
        if re.match("-?\d+\.$", text, re.MULTILINE) or not text:
            return (QValidator.Intermediate, text, ndx)
        
        return (QValidator.Invalid, text, ndx)
    
    def fixup(self, text):
        if not text:
            return 0
        val = float(text)
        if val < self._minimum:
            return str(self._minimum)
        if val > self._maximum:
            return str(self._maximum)
        return text

class ScientificSpinBox(QDoubleSpinBox):
    """spinbox for floating point values in scientific notation"""
    def __init__(
        self,
        minimum=0,
        maximum=100,
        decimals=2,
        prefix=None,
        maxAbsoluteCharacteristic=None,
        stepMultiplier=1,
        suffix=None,
        default=None,
        tooltip=None, 
        mapping=None,
        parent=None,
    ):
        super().__init__(parent)
        if maximum < minimum:
            raise ValueError("maximum < minimum")
        if maxAbsoluteCharacteristic:
            assert(maxAbsoluteCharacteristic > 0)
        self.maxAbsoluteCharacteristic = maxAbsoluteCharacteristic
        assert(stepMultiplier > 0)
        self.stepMultiplier = stepMultiplier
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.mapping = mapping
        if default is None:
            try:
                min_char = int(np.log10(abs(minimum)))
            except ValueError:
                min_char = 0
            min_mant = minimum / (10 ** min_char)
            if min_mant < 1:
                min_mant *= 10
                min_char -= 1
            try:
                max_char = int(np.log10(abs(maximum)))
            except ValueError:
                max_char = 0
            max_mant = maximum / (10 ** max_char)
            if max_mant < 1:
                max_mant *= 10
                max_char -= 1
            
            mean_mant = 0.5 * (max_mant + min_mant)
            mean_char = 0.5 * (max_char + min_char)
            default = mean_mant * 10 ** (mean_char)
        
        self.setValue(default)
        if tooltip is not None:
            self.setToolTip(tooltip)
        if prefix:
            self.setPrefix(prefix)
        if suffix:
            self.setSuffix(suffix)
    
        self._validator = ScientificValidator(minimum, maximum, decimals, self.lineEdit())
        self.lineEdit().setValidator(self._validator)
        self.setDecimals(decimals)

    def setMinimum(self, value):
        self._minimum = value
        self.lineEdit().validator()._minimum = value
        super().setMinimum(value)

    def setMaximum(self, value):
        self._maximum = value
        self.lineEdit().validator()._maximum = value
        super().setMaximum(value)

    def setDecimals(self, value):
        super().setDecimals(value)
        self.lineEdit().validator()._decimals = value

    def minimum(self):
        return self._minimum

    def maximum(self):
        return self._maximum

    def valueFromText(self, text):
        return float(text)
    
    def textFromValue(self, value):
        """
        :param float value: floating point number
        
        :returns: string for floating point number; according to the 
            Qt6 documentation, the string should not include the prefix
            or suffix
        :rtype: str
        """
        # split value into characteristic and mantissa
        mantissa, characteristic = self.getMantissaCharacteristic(value)
        
        fmt = "%%.%ife%%i" % self.decimals()
        out = fmt % (mantissa, characteristic)
        return out
    
    def validate(self, text, ndx):
        if re.match("-?\d+(?:\.\d{0,%i})?(?:[Ee]-?\d+)?$" % self.decimals(), text, re.MULTILINE):
            val = float(text)
            if val < self.minimum() or val > self.maximum():
                return (QValidator.Invalid, text, ndx)
    
            if self.maxAbsoluteCharacteristic:
                mant, char = self.getMantissaCharacteristic(val)
                if abs(char) > self.maxAbsoluteCharacteristic:
                    return (QValidator.Invalid, text, ndx)
            
            return (QValidator.Acceptable, text, ndx)
        
        if self.lineEdit().hasFocus():        
            if re.match("-?\d+(?:\.(?:\d{,%i}?(?:[Ee]-?)?))?$" % self.decimals(), text, re.MULTILINE) or not text:
                return (QValidator.Intermediate, text, ndx)
            if re.match("-?\d+(?:[Ee]-?)$", text, re.MULTILINE) or not text:
                return (QValidator.Intermediate, text, ndx)
            if re.match("-?\d+\.$", text, re.MULTILINE) or not text:
                return (QValidator.Intermediate, text, ndx)

        return (QValidator.Invalid, text, ndx)
    
    def fixup(self, value):
        return
    
    def stepBy(self, n):
        if n < 0:
            for i in range(0, abs(n)):
                self.stepDown()
        elif n > 0:
            for i in range(0, n):
                self.stepUp()
    
    def getMantissaCharacteristic(self, value=None):
        if value is None:
            value = self._unmappedValue()
        try:
            characteristic = 0 if value == 0 else int(np.log10(abs(value)))
        except (ValueError, OverflowError):
            characteristic = 0

        # need to round now, otherwise we can get like
        # 10.00e2 instead of 1.00e3
        mantissa = value / (10 ** characteristic)
        mantissa = round(mantissa, self.decimals() + 1)
        if abs(mantissa) < 1 and abs(mantissa) > 0:
            mantissa *= 10
            characteristic -= 1
        
        return mantissa, characteristic
    
    def stepUp(self):
        value = self._unmappedValue()
        mantissa, characteristic = self.getMantissaCharacteristic()
        # if characteristic == 0:
        #     characteristic = -self.decimals()
        #     if self.maxAbsoluteCharacteristic:
        #         characteristic = -(self.maxAbsoluteCharacteristic - 1)
        #     elif self.maxAbsoluteCharacteristic and abs(characteristic) > self.maxAbsoluteCharacteristic:
        #         characteristic = -(self.maxAbsoluteCharacteristic - 1)
        
        characteristic -= 1
        value = value + self.stepMultiplier * 10 ** characteristic
        mantissa, characteristic = self.getMantissaCharacteristic(value)
        if self.maxAbsoluteCharacteristic and (
            value < 0 and abs(characteristic) > self.maxAbsoluteCharacteristic
        ):
            value = 0

        # val = self._unmappedValue() * 10
        # if val == 0:
        #     val = 10 ** -self.decimals()
        #     if self.maxAbsoluteCharacteristic:
        #         val = 10 ** -self.maxAbsoluteCharacteristic
        # elif val < 0:
        #     val /= 100
        # if self.maxAbsoluteCharacteristic:
        #     try:
        #         char = 0 if val == 0 else np.log10(abs(val))
        #     except (OverflowError, ValueError):
        #         char = 0
        #     if abs(char) > self.maxAbsoluteCharacteristic:
        #         val = 0
            
        self.setValue(min(value, self.maximum()))

    def stepDown(self):
        value = self._unmappedValue()
        mantissa, characteristic = self.getMantissaCharacteristic()
        # if characteristic == 0:
        #     characteristic = -self.decimals()
        #     if self.maxAbsoluteCharacteristic:
        #         characteristic = -(self.maxAbsoluteCharacteristic - 1)
        #     elif self.maxAbsoluteCharacteristic and abs(characteristic) > self.maxAbsoluteCharacteristic:
        #         characteristic = -(self.maxAbsoluteCharacteristic - 1)
 
        characteristic -= 1
        value = value - self.stepMultiplier * 10 ** characteristic
        mantissa, characteristic = self.getMantissaCharacteristic(value)
        if self.maxAbsoluteCharacteristic and (
            value > 0 and abs(characteristic) > self.maxAbsoluteCharacteristic
        ):
            value = 0

        # val = self._unmappedValue() / 10
        # if val == 0:
        #     val = -(10 ** -self.decimals())
        #     if self.maxAbsoluteCharacteristic:
        #         val = -(10 ** -self.maxAbsoluteCharacteristic)
        # elif val < 0:
        #     val *= 100
        # if self.maxAbsoluteCharacteristic:
        #     try:
        #         char = 0 if val == 0 else np.log10(abs(val))
        #     except (OverflowError, ValueError):
        #         char = 0
        #     if abs(char) > self.maxAbsoluteCharacteristic:
        #         val = 0
            
        self.setValue(max(value, self.minimum()))
    
    def _unmappedValue(self):
        text = self.text()
        text = text.replace(self.prefix(), "", 1)
        text = text[::-1].replace(self.suffix()[::-1], "", 1)[::-1]
        try:
            val = float(text)
        except ValueError:
            val = 0
        return val
    
    def value(self):
        val = self._unmappedValue()
        if self.mapping:
            return self.mapping(val)
        return val

    def setValue(self, value):
        sendSignal = False

        mantissa, characteristic = self.getMantissaCharacteristic(value)

        value = mantissa * 10 ** characteristic
        
        if value != self._unmappedValue():
            sendSignal = True

        self.lineEdit().setText(
            self.prefix() +
            self.textFromValue(value) +
            self.suffix()
        )

