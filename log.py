class LogLevel:
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4

LOG_LEVEL = LogLevel.INFO

def debug(*args):
    if LOG_LEVEL <= LogLevel.DEBUG:
        print("DEBUG:", *args)

def info(*args):
    if LOG_LEVEL <= LogLevel.INFO:
        print("INFO:", *args)

def warn(*args):
    if LOG_LEVEL <= LogLevel.WARN:
        print("WARN:", *args)

def error(*args):
    if LOG_LEVEL <= LogLevel.ERROR:
        print("ERROR:", *args)
