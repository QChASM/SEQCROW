# AaronTools uses a standard Python module that need to be redirected to
# ChimeraX's log
# This is a 'stream' for AaronTools' loggers
from time import sleep
from Qt.QtCore import QThread

class DelayForcePrint(QThread):
    def run(self):
        sleep(10)
        LoggingLogger.force_print_next = True


class LoggingLogger:
    name = "ChimeraX Log"
    force_print_next = False
    
    def __init__(self, session):
        self._session = session
        self._msg = ""
        self._prev_msg = ""
        self.delay_reset = DelayForcePrint()
    
    def write(self, msg):
        self._msg += msg
    
    def flush(self):
        if self._msg != self._prev_msg or LoggingLogger.force_print_next:
            self._session.logger.warning(self._msg)
            self._prev_msg = self._msg
        self._msg = ""
        LoggingLogger.force_print_next = False
        self.delay_reset.start()