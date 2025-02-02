# Generated from pym.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .pymParser import pymParser
else:
    from pymParser import pymParser

# This class defines a complete listener for a parse tree produced by pymParser.
class pymListener(ParseTreeListener):

    # Enter a parse tree produced by pymParser#program.
    def enterProgram(self, ctx:pymParser.ProgramContext):
        pass

    # Exit a parse tree produced by pymParser#program.
    def exitProgram(self, ctx:pymParser.ProgramContext):
        pass


    # Enter a parse tree produced by pymParser#statement.
    def enterStatement(self, ctx:pymParser.StatementContext):
        pass

    # Exit a parse tree produced by pymParser#statement.
    def exitStatement(self, ctx:pymParser.StatementContext):
        pass


    # Enter a parse tree produced by pymParser#varDeclaration.
    def enterVarDeclaration(self, ctx:pymParser.VarDeclarationContext):
        pass

    # Exit a parse tree produced by pymParser#varDeclaration.
    def exitVarDeclaration(self, ctx:pymParser.VarDeclarationContext):
        pass


    # Enter a parse tree produced by pymParser#expressionStatement.
    def enterExpressionStatement(self, ctx:pymParser.ExpressionStatementContext):
        pass

    # Exit a parse tree produced by pymParser#expressionStatement.
    def exitExpressionStatement(self, ctx:pymParser.ExpressionStatementContext):
        pass


    # Enter a parse tree produced by pymParser#assignmentStatement.
    def enterAssignmentStatement(self, ctx:pymParser.AssignmentStatementContext):
        pass

    # Exit a parse tree produced by pymParser#assignmentStatement.
    def exitAssignmentStatement(self, ctx:pymParser.AssignmentStatementContext):
        pass


    # Enter a parse tree produced by pymParser#ifStatement.
    def enterIfStatement(self, ctx:pymParser.IfStatementContext):
        pass

    # Exit a parse tree produced by pymParser#ifStatement.
    def exitIfStatement(self, ctx:pymParser.IfStatementContext):
        pass


    # Enter a parse tree produced by pymParser#AndExpr.
    def enterAndExpr(self, ctx:pymParser.AndExprContext):
        pass

    # Exit a parse tree produced by pymParser#AndExpr.
    def exitAndExpr(self, ctx:pymParser.AndExprContext):
        pass


    # Enter a parse tree produced by pymParser#MulDivExpr.
    def enterMulDivExpr(self, ctx:pymParser.MulDivExprContext):
        pass

    # Exit a parse tree produced by pymParser#MulDivExpr.
    def exitMulDivExpr(self, ctx:pymParser.MulDivExprContext):
        pass


    # Enter a parse tree produced by pymParser#EqualityExpr.
    def enterEqualityExpr(self, ctx:pymParser.EqualityExprContext):
        pass

    # Exit a parse tree produced by pymParser#EqualityExpr.
    def exitEqualityExpr(self, ctx:pymParser.EqualityExprContext):
        pass


    # Enter a parse tree produced by pymParser#ComparisonExpr.
    def enterComparisonExpr(self, ctx:pymParser.ComparisonExprContext):
        pass

    # Exit a parse tree produced by pymParser#ComparisonExpr.
    def exitComparisonExpr(self, ctx:pymParser.ComparisonExprContext):
        pass


    # Enter a parse tree produced by pymParser#PrimaryExpr.
    def enterPrimaryExpr(self, ctx:pymParser.PrimaryExprContext):
        pass

    # Exit a parse tree produced by pymParser#PrimaryExpr.
    def exitPrimaryExpr(self, ctx:pymParser.PrimaryExprContext):
        pass


    # Enter a parse tree produced by pymParser#NotExpr.
    def enterNotExpr(self, ctx:pymParser.NotExprContext):
        pass

    # Exit a parse tree produced by pymParser#NotExpr.
    def exitNotExpr(self, ctx:pymParser.NotExprContext):
        pass


    # Enter a parse tree produced by pymParser#ParenExpr.
    def enterParenExpr(self, ctx:pymParser.ParenExprContext):
        pass

    # Exit a parse tree produced by pymParser#ParenExpr.
    def exitParenExpr(self, ctx:pymParser.ParenExprContext):
        pass


    # Enter a parse tree produced by pymParser#AddSubExpr.
    def enterAddSubExpr(self, ctx:pymParser.AddSubExprContext):
        pass

    # Exit a parse tree produced by pymParser#AddSubExpr.
    def exitAddSubExpr(self, ctx:pymParser.AddSubExprContext):
        pass


    # Enter a parse tree produced by pymParser#OrExpr.
    def enterOrExpr(self, ctx:pymParser.OrExprContext):
        pass

    # Exit a parse tree produced by pymParser#OrExpr.
    def exitOrExpr(self, ctx:pymParser.OrExprContext):
        pass


    # Enter a parse tree produced by pymParser#NumberLiteral.
    def enterNumberLiteral(self, ctx:pymParser.NumberLiteralContext):
        pass

    # Exit a parse tree produced by pymParser#NumberLiteral.
    def exitNumberLiteral(self, ctx:pymParser.NumberLiteralContext):
        pass


    # Enter a parse tree produced by pymParser#StringLiteral.
    def enterStringLiteral(self, ctx:pymParser.StringLiteralContext):
        pass

    # Exit a parse tree produced by pymParser#StringLiteral.
    def exitStringLiteral(self, ctx:pymParser.StringLiteralContext):
        pass


    # Enter a parse tree produced by pymParser#BooleanLiteral.
    def enterBooleanLiteral(self, ctx:pymParser.BooleanLiteralContext):
        pass

    # Exit a parse tree produced by pymParser#BooleanLiteral.
    def exitBooleanLiteral(self, ctx:pymParser.BooleanLiteralContext):
        pass


    # Enter a parse tree produced by pymParser#Variable.
    def enterVariable(self, ctx:pymParser.VariableContext):
        pass

    # Exit a parse tree produced by pymParser#Variable.
    def exitVariable(self, ctx:pymParser.VariableContext):
        pass


del pymParser