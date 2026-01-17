from ast_nodes import *
from tokens import Token

class AstPrinter:
    def print(self, statements):
        for stmt in statements:
            if stmt:
                print(stmt.accept(self))

    def visit_block_stmt(self, stmt):
        builder = "(block "
        for statement in stmt.statements:
            builder += str(statement.accept(self)) + " "
        builder += ")"
        return builder

    def visit_expression_stmt(self, stmt):
        return self.parenthesize(";", stmt.expression)
    
    def visit_print_stmt(self, stmt):
        return self.parenthesize("print", stmt.expression)
    
    def visit_var_stmt(self, stmt):
        if stmt.initializer is None:
            return self.parenthesize2("var", stmt.name)
        return self.parenthesize2("var", stmt.name, stmt.initializer)
    
    def visit_if_stmt(self, stmt):
        if stmt.else_branch is None:
            return self.parenthesize2("if", stmt.condition, stmt.then_branch)
        return self.parenthesize2("if-else", stmt.condition, stmt.then_branch, stmt.else_branch)

    def visit_while_stmt(self, stmt):
        return self.parenthesize2("while", stmt.condition, stmt.body)
    
    def visit_assign_expr(self, expr):
        return self.parenthesize2("=", expr.name, expr.value)

    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr):
        if expr.value is None: return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)
    
    def visit_variable_expr(self, expr):
        return expr.name.lexeme
    
    def visit_logical_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def parenthesize(self, name, *exprs):
        builder = f"({name}"
        for expr in exprs:
            builder += " " + str(expr.accept(self))
        builder += ")"
        return builder

    def parenthesize2(self, name, *parts):
        builder = f"({name}"
        for part in parts:
            if isinstance(part, (Expr, Stmt)):
                builder += " " + str(part.accept(self))
            elif isinstance(part, Token):
                builder += " " + part.lexeme
            else:
                builder += " " + str(part)
        builder += ")"
        return builder

import sys
from lexer import Lexer
from parser import Parser

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 ast_printer.py <filename>")
        return

    filename = sys.argv[1]
    with open(filename, 'r') as file:
        source = file.read()

    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    if statements:
        printer = AstPrinter()
        printer.print(statements)

if __name__ == '__main__':
    main()
