
class State(Exception):
    operation = ''
    lastcmd = ''

    def __str__(self):
        return f'State(lastcmd="{self.lastcmd}", exception="{self.exception}")'

class Ok(State):
    def __init__(self, lastcmd):
        self.operation = lastcmd

class Error(State):
    def __init__(self, lastcmd, exception):
        self.operation = lastcmd
        self.exception = exception
