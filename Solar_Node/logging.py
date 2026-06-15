# Stub logging module for MicroPython compatibility with INA219

CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0

_level = INFO  # richiesto da ina219.py

def basicConfig(*args, **kwargs):
    global _level
    if "level" in kwargs:
        _level = kwargs["level"]

def getLogger(name=None):
    return DummyLogger()

class DummyLogger:
    def debug(self, *args, **kwargs): pass
    def info(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass
    def critical(self, *args, **kwargs): pass
    def exception(self, *args, **kwargs): pass
