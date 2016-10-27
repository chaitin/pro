import antlr4
import sys

class SyntaxError(Exception):
    pass

class proErrorListener(antlr4.error.ErrorListener.ErrorListener):
    def __init__(self, src):
        super(proErrorListener, self).__init__()

        self.src = src

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        lines = self.src.split('\n')
        text = ''
        for i in xrange(line - 10, line + 10):
            if i >= 0 and i < len(lines):
                h = '+ ' if i != line else '> '
                text += '%d: %s %s\n' % (i, h, lines[i])
        sys.stderr.write(text)
        raise SyntaxError(msg)
