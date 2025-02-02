# Generated from pym.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .pymParser import pymParser
else:
    from pymParser import pymParser

# This class defines a complete generic visitor for a parse tree produced by pymParser.

class pymVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by pymParser#program.
    def visitProgram(self, ctx:pymParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#statement.
    def visitStatement(self, ctx:pymParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#varDeclaration.
    def visitVarDeclaration(self, ctx:pymParser.VarDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#expressionStatement.
    def visitExpressionStatement(self, ctx:pymParser.ExpressionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#assignmentStatement.
    def visitAssignmentStatement(self, ctx:pymParser.AssignmentStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#ifStatement.
    def visitIfStatement(self, ctx:pymParser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#AndExpr.
    def visitAndExpr(self, ctx:pymParser.AndExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#MulDivExpr.
    def visitMulDivExpr(self, ctx:pymParser.MulDivExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#EqualityExpr.
    def visitEqualityExpr(self, ctx:pymParser.EqualityExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#ComparisonExpr.
    def visitComparisonExpr(self, ctx:pymParser.ComparisonExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#PrimaryExpr.
    def visitPrimaryExpr(self, ctx:pymParser.PrimaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#NotExpr.
    def visitNotExpr(self, ctx:pymParser.NotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#ParenExpr.
    def visitParenExpr(self, ctx:pymParser.ParenExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#AddSubExpr.
    def visitAddSubExpr(self, ctx:pymParser.AddSubExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#OrExpr.
    def visitOrExpr(self, ctx:pymParser.OrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#NumberLiteral.
    def visitNumberLiteral(self, ctx:pymParser.NumberLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#StringLiteral.
    def visitStringLiteral(self, ctx:pymParser.StringLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#BooleanLiteral.
    def visitBooleanLiteral(self, ctx:pymParser.BooleanLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by pymParser#Variable.
    def visitVariable(self, ctx:pymParser.VariableContext):
        return self.visitChildren(ctx)



del pymParser