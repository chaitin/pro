# Generated from pro.g4 by ANTLR 4.5.2
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by proParser.

class proVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by proParser#program.
    def visitProgram(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#statement.
    def visitStatement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#delimiter.
    def visitDelimiter(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#declaration.
    def visitDeclaration(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#type_specifier.
    def visitType_specifier(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#initializer.
    def visitInitializer(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#expression_initializer.
    def visitExpression_initializer(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#array_initializer.
    def visitArray_initializer(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#func_initializer.
    def visitFunc_initializer(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#call_statement.
    def visitCall_statement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#arguments.
    def visitArguments(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#expression.
    def visitExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#binary_expression.
    def visitBinary_expression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#unary_expression.
    def visitUnary_expression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#binary_operator.
    def visitBinary_operator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#unary_operator.
    def visitUnary_operator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by proParser#primary_expression.
    def visitPrimary_expression(self, ctx):
        return self.visitChildren(ctx)


