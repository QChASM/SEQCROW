# AaronTools uses a standard Python module that need to be redirected to
# ChimeraX's log
# This is a 'stream' for AaronTools' loggers
class LoggingLogger:
    name = "ChimeraX Log"
    def __init__(self, session):
        self._session = session
        self._msg = ""
        self._prev_msg = ""
    
    def write(self, msg):
        self._msg += msg
    
    def flush(self):
        if self._msg != self._prev_msg:
            self._session.logger.warning(self._msg)
            self._prev_msg = self._msg
        self._msg = ""