import sys
import antlr4
from collections import OrderedDict
from .proLexer import proLexer
from .proParser import proParser
from .proVisitor import proVisitor
from .proErrorListener import proErrorListener

class SemanticError(Exception):
    pass

class Expression(object):
    constant = None
    _value = None

    @property
    def value(self):
        if self._value is not None:
            return self._value
        self._value = self.eval()
        return self._value

    def eval(self, ctx=None):
        return self._value

class BinaryExpression(Expression):
    def __init__(self, op, el, er):
        if not op in '+-*/^|&':
            raise SemanticError('unsupported op %s' % op)
        self.op = op

        if el.constant is False or er.constant is False:
            raise SemanticError('expression should be constant')

        self.constant = True
        self.expr_left = el
        self.expr_right = er

    def eval(self, ctx=None):
        lv = self.expr_left.eval(ctx)
        rv = self.expr_right.eval(ctx)
        if isinstance(lv, Address):
            # Address arithmetic
            if self.op == '+':
                return Address(lv.base, lv.offset + rv)
            elif self.op == '-':
                return Address(lv.base, lv.offset - rv)
        return eval('%d %s %d' % (lv, self.op, rv))

    def __repr__(self):
        try:
            return '(%r %s %r)' % (self.expr_left, self.op, self.expr_right)
        except TypeError:
            raise SemanticError('invalid binary operation')

class UnaryExpression(Expression):
    def __init__(self, op, e):
        if not op in '&':
            raise SemanticError('unsupported op %s' % op)
        self.op = op

        if not isinstance(e, (Var, Array)):
            raise SemanticError('invalid L-value')

        self.constant = True
        self.expr = e

    def eval(self, ctx=None):
        return self.expr.addr

    def __repr__(self):
        return '%s%r' % (self.op, self.expr)

class Symbol(Expression):
    constant = False
    def __init__(self, name):
        super(Symbol, self).__init__()
        self.name = name

        self._base = '_DATA'
        self._offset = None

    @property
    def addr(self):
        return Address(self._base, self._offset)

    def __str__(self):
        return self.name

class Array(Symbol):
    constant = True
    def __init__(self, name, initializer):
        super(Array, self).__init__(name)

        if not isinstance(initializer, Expression) or not initializer.constant:
            raise SemanticError('invalid array "%s"' % name)

        if isinstance(initializer, String):
            self.size = initializer.size
            self.data = initializer.value
        elif isinstance(initializer, Array):
            self.size = initializer.size
            self.data = initializer.data
        else:
            self.size = initializer.value
            self.data = '\x00' * self.size

        if len(self.data) > self.size:
            raise SemanticError('inconsitent array initializer')

    def eval(self, ctx=None):
        return self.addr

    def __repr__(self):
        data = self.data if len(self.data) < 0x20 else self.data[:0x20] + '...'
        return 'array %s[%d] = %r' % (self.name, self.size, data)

class Const(Symbol):
    constant = True
    def __init__(self, name, initializer):
        super(Const, self).__init__(name)
        if not isinstance(initializer, Expression) or not initializer.constant:
            raise SemanticError('invalid const initializer for "%s"' % name)
        self.size = 0
        self._value = initializer.value

    def __repr__(self):
        return '%s = %#x' % (self.name, self.value)

class Func(Symbol):
    constant = True
    def __init__(self, name, initializer):
        super(Func, self).__init__(name)
        self._base = initializer[0]
        self._offset = initializer[1] if len(initializer) > 1 else 0
        self.parse_signature(initializer[2] if len(initializer) > 2 else None)
        self.size = 0

    def eval(self, ctx=None):
        return self.addr

    def __repr__(self):
        return '%s = %r' % (self.name, self.addr)

    def __getattr__(self, name):
        if self.attr is not None and name in self.attr:
            return True
        return None

    def parse_signature(self, sig=None):
        ''' Func(gadget) signature is  Input, Output, Clobber, Attributes.
        Input/Output/Clobber are sets of registers, Attributes is special
        hint for compiler. They are seperated by ':', the registers in set
        are seperated by ','. If not signature is provided, the Func will
        be called with default calling convention.

        Current Attributes:
            va      variable arguments
            align   call stack should be aligned
        '''
        if sig is None:
            self.input = None
            self.output = None
            self.clobber = None
            self.attr = set()
            return

        regsets = []

        for regset in sig.split(':'):
            if regset == '':
                regsets.append([])
            else:
                regsets.append(regset.split(','))

        while len(regsets) < 4:
            regsets.append([])

        self.input = regsets[0]
        self.output = regsets[1]
        self.clobber = regsets[2]
        self.attr = set(regsets[3])


class Var(Symbol):
    constant = False
    def __init__(self, name, initializer):
        super(Var, self).__init__(name)
        self.size = 8
        if isinstance(initializer, Expression):
            if not initializer.constant:
                raise SemanticError('invalid var "%s"' % name)
            self._value = initializer.value

    def __repr__(self):
        r = 'var %s' % (self.name)
        if self._value:
            r += ' %#x' % self._value
        return r

class String(Expression):
    constant = True
    def __init__(self, value):
        self._value = value
        self.size = len(value) + 8 - len(value) % 8

    def __repr__(self):
        return `self._value`

class Int(Expression):
    constant = True
    def __init__(self, value):
        if isinstance(value, (int, long)):
            self._value = value
        elif isinstance(value, (str, unicode)) and '0x' in value.lower():
            self._value = int(value, 16)
        else:
            self._value = int(value)

    def __repr__(self):
        return '%#x' % self._value

class Address(BinaryExpression):
    def __init__(self, base, offset):
        super(Address, self).__init__('+', String(base), Int(offset))
        self.base = self.expr_left.value
        self.offset = self.expr_right.value

    def eval(self, ctx=None):
        if ctx is None:
            return (self.base, self.offset)
        else:
            base = ctx.get(self.base, None)
            if base is None:
                raise AttributeError('no relocating information for "%s"' % self.base)
            return base + self.offset

    def __repr__(self):
        return '<%s, %#x>' % (self.base, self.offset)

class Environment():
    def __init__(self):
        self.vars = OrderedDict()
        self._offset = 0

    def __setitem__(self, key, value):
        if key in self.vars:
            raise SemanticError('duplicated variable "%s"' % key)
        if value.name is None:
            if not isinstance(value, Array):
                raise SemanticError('anonymous symbol is not allowed for %r' % type(value))
            value.name = 'off_%x' % (self._offset)
        if not isinstance(value, (Const, Func)):
            # Const and Func are immediates in rop chain(.code), they do not
            # appear in .data
            value._offset = self._offset
            self._offset += value.size
        self.vars[key] = value

    def __getitem__(self, key):
        if not key in self.vars:
            raise SemanticError('undefined variable "%s"' % key)
        return self.vars[key]

    def __contains__(self, key):
        return key in self.vars

    @property
    def size(self):
        return self._offset

    def __repr__(self):
        r = ''
        for cls in (Const, Func, Var, Array):
            r += cls.__name__ + '\n'
            r += '\n'.join(map(repr, (v for v in self.vars.itervalues() if isinstance(v, cls))))
            r += '\n\n'
        return r

class Call(object):
    ''' a Call is `ret/jmp to a gadget with arguments` '''
    def __init__(self, func, args):
        self.func = func
        self.args = args
        if isinstance(func, Func) and func.sig is not None:
            # check signature if it's not a function with variable arguments
            reg_in = func.sig['input']
            if len(reg_in) != len(args) and func.va is not True:
                raise SemanticError('"%s" takes %d parameters, but %d is provided' % (func, len(reg_in), len(args)))
        elif isinstance(func, Const) and func.name == 'inline':
            for arg in args:
                if not arg.constant:
                    raise SemanticError('"%s" is not a constant in inline statement' % arg)

    def __repr__(self):
        return '%s(%s)' % (self.func.name, ', '.join(map(repr, self.args)))

class Program(proVisitor):
    def __init__(self, **kwargs):
        super(proVisitor, self).__init__(**kwargs)

        self.name = None
        self.env = Environment()

        # builtin variables
        self.env['undefined'] = Const('undefined', Int(0))
        self.env['inline'] = Const('inline', Int(1))

    def visitProgram(self, ctx):
        name = ctx.Identifier().getText()
        self.name = name
        statements = []
        for stmt in ctx.statement():
            if stmt.declaration():
                self.visitDeclaration(stmt.declaration())
            elif stmt.call_statement():
                statements.append(self.visitCall_statement(stmt.call_statement()))
        self.statements = statements
    
    def visitDeclaration(self, ctx):
        type = ctx.type_specifier().getText()
        name = ctx.Identifier().getText()

        initializer = None
        if ctx.initializer():
            initializer = self.visitInitializer(ctx.initializer(), name, type)

        cls = {'var':Var, 'func':Func, 'array':Array, 'const':Const}[type]
        self.env[name] = cls(name, initializer)

    def visitInitializer(self, ctx, name, type):
        if type == 'func':
            if not ctx.func_initializer():
                raise SemanticError('function initializer required for "%s"' % name)
        elif type == 'array':
            if not ctx.array_initializer():
                raise SemanticError('array initializer required for "%s"' % name)
        elif type == 'const' or type == 'var':
            if not ctx.expression_initializer():
                raise SemanticError('expression initializer required for "%s"' % name)
        return self.visitChildren(ctx)

    def visitExpression_initializer(self, ctx):
        return self.visitExpression(ctx.expression())

    def visitArray_initializer(self, ctx):
        return self.visitExpression(ctx.expression())

    def visitFunc_initializer(self, ctx):
        base = ctx.Identifier().getText()
        offset = ctx.Constant().getText() if ctx.Constant() else 0
        signature = ctx.String().getText()[1:-1].decode('string-escape') if ctx.String() else None
        return (base, offset, signature)

    def visitBinary_expression(self, ctx):
        el = self.visitPrimary_expression(ctx.getChild(0))
        op = ctx.binary_operator().getText()
        er = self.visitPrimary_expression(ctx.getChild(2))
        return BinaryExpression(op, el, er)

    def visitUnary_expression(self, ctx):
        op = ctx.unary_operator().getText()
        e = self.visitPrimary_expression(ctx.primary_expression())
        return UnaryExpression(op, e)

    def visitPrimary_expression(self, ctx):
        if ctx.Identifier():
            var = ctx.Identifier().getText()
            return self.env[var]
        elif ctx.Constant():
            return Int(ctx.Constant().getText())
        elif ctx.String():
            s = ctx.String().getText()[1:-1].decode('string-escape')
            _s = '$' + s
            if _s not in self.env:
                self.env[_s] = Array(None, String(s))
            return self.env[_s]
        elif ctx.expression():
            return self.visitExpression(ctx.expression())
        else:
            raise SemanticError('unknown primary expression "%s"' % ctx.getText())

    def visitCall_statement(self, ctx):
        func = self.env[ctx.Identifier().getText()]
        if not isinstance(func, (Func, Const, Var)):
            # Func will be relocated if ASLR is enabled, however Const/Var
            # can also be used a function
            raise SemanticError('"%s" is not a function' % func)
        args = self.visitArguments(ctx.arguments())
        return Call(func, args)

    def visitArguments(self, ctx):
        if ctx is None:
            return []
        return self.visitArguments(ctx.arguments()) + [self.visitExpression(ctx.expression())]

def parse(text):
    lexer = proLexer(antlr4.InputStream(text))
    lexer.removeErrorListeners()
    lexer.addErrorListener(proErrorListener(text))
    stream = antlr4.CommonTokenStream(lexer)

    parser = proParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(proErrorListener(text))
    tree = parser.program()

    prog = Program()
    prog.visit(tree)
    return prog

