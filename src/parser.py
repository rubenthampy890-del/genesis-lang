from tokens import TokenType, Token
from ast_nodes import *

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.had_error = False


    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements


    def declaration(self):
        try:
            # Allow 'and' to start a new sentence (connector)
            while self.match(TokenType.AND): pass
            
            if self.match(TokenType.TO):
                return self.function("function")
            if self.match(TokenType.USE):
                return self.use_statement()
            if self.match(TokenType.SET):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def function(self, kind):
        # to name with arg1, arg2 do ... end
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        
        parameters = []
        if self.match(TokenType.WITH):
            if not self.check(TokenType.DO):
                while True:
                    if len(parameters) >= 255:
                        self.error(self.peek(), "Can't have more than 255 parameters.")
                    
                    parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                    if not self.match(TokenType.COMMA): break
        
        self.consume(TokenType.DO, f"Expect 'do' before {kind} body.")
        body = self.block()
        # block consumes END, so we are good.
        
        return Function(name, parameters, body)

    def statement(self):
        # 1. Parse the core statement (e.g. say "hi")
        stmt = self.core_statement()
        
        # 2. Check for modifiers (Natural Syntax)
        
        # Postfix If: ... if x > 5
        if self.match(TokenType.CHECK):
            condition = self.expression()
            stmt = If(condition, Block([stmt]), None)

        # Postfix Times: ... 5 times
        # We look for NUMBER then TIMES
        if self.check(TokenType.NUMBER):
            # Peek ahead to see if 'times' follows
            if self.tokens[self.current + 1].type == TokenType.TIMES:
                count = self.expression() # Consumes the number
                self.consume(TokenType.TIMES, "Expect 'times' after number.")
                stmt = Times(count, stmt)

        return stmt

    def core_statement(self):
        if self.match(TokenType.CHECK):
            return self.if_statement()
        if self.match(TokenType.LOOP):
            return self.while_statement()
        if self.match(TokenType.SAY):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.UPDATE):
            return self.assignment_statement()
        
        # v5 Statements
        if self.match(TokenType.SPEAK):
            return self.speak_statement()
        if self.match(TokenType.DRAW):
            return self.draw_statement()
        if self.match(TokenType.ASK):
            return self.ask_statement()
            
        return self.expression_statement()

    def speak_statement(self):
        expr = self.expression()
        return Speak(expr)

    def ask_statement(self):
        expr = self.expression()
        return Ask(expr)

    def draw_statement(self):
        # draw "circle" with 100
        # draw "forward" with 50
        command = self.expression() # Expects string or identifier usually
        
        args = []
        if self.match(TokenType.WITH):
             if not self.check(TokenType.EOF):
                while True:
                    args.append(self.expression())
                    if not self.match(TokenType.COMMA): break
        
        return Draw(command, args)

    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check(TokenType.END) and not self.check(TokenType.OTHERWISE) and not self.check(TokenType.EOF):
            value = self.expression()
        
        # In this language, do we need semicolon? No.
        return Return(keyword, value)


    def if_statement(self):
        # check condition ...
        condition = self.expression()
        self.consume(TokenType.THEN, "Expect 'then' after check condition.")
        
        then_branch = Block(self.block())
        else_branch = None
        
        if self.match(TokenType.OTHERWISE):
            else_branch = Block(self.block())
            
        return If(condition, then_branch, else_branch)

    def print_statement(self):
        value = self.expression()
        return Print(value)

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name after 'set'.")
        self.consume(TokenType.TO, "Expect 'to' after variable name.")
        initializer = self.expression()
        return Var(name, initializer)
        
    def assignment_statement(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name after 'update'.")
        self.consume(TokenType.TO, "Expect 'to' after variable name.")
        value = self.expression()
        return Assign(name, value)

    def while_statement(self):
        self.consume(TokenType.WHILE, "Expect 'while' after 'loop'.")
        condition = self.expression()
        self.consume(TokenType.DO, "Expect 'do' after loop condition.")
        body = Block(self.block())
        return While(condition, body)

    def use_statement(self):
        self.consume(TokenType.PYTHON, "Expect 'python' after 'use'.")
        module_name = self.consume(TokenType.STRING, "Expect module name string.")
        return Use(module_name.literal)

    def block(self):
        statements = []
        while not self.check(TokenType.END) and not self.check(TokenType.OTHERWISE) and not self.is_at_end():
            # Allow 'and' inside blocks too
            while self.match(TokenType.AND): pass
            
            statements.append(self.declaration())
        
        if self.check(TokenType.END):
            self.advance() 
            
        return statements


    def expression_statement(self):
        expr = self.expression()
        return Expression(expr)

    def expression(self):
        return self.logic_or()

    def logic_or(self):
        expr = self.logic_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logic_and()
            expr = Logical(expr, operator, right)
        return expr

    def logic_and(self):
        expr = self.equality()
        
        while self.check(TokenType.AND):
            # Look ahead: If 'and' is followed by a statement keyword, 
            # it is a sentence connector, NOT a logical operator.
            # We break/return so the expression ends, and declaration() picks up the 'and'.
            next_token = self.tokens[self.current + 1] # Peek next
            if next_token.type in [
                TokenType.SAY, TokenType.SET, TokenType.UPDATE, 
                TokenType.CHECK, TokenType.LOOP, TokenType.TO, 
                TokenType.USE, TokenType.RETURN, TokenType.EOF,
                TokenType.PYTHON # "and use python", "and python math.pi" -> python token? "use" is USE.
            ]:
                break
                
            self.advance() # Consume AND
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
            
        return expr


    def equality(self):
        expr = self.comparison()
        
        # We handle 'is' here, which can be 'is' (==), 'is not' (!=), 
        # 'is less than' (<), 'is greater than' (>)
        while self.match(TokenType.IS, TokenType.GREATER, TokenType.LESS):
            operator_token = self.previous()
            
            # Handle 'is ...'
            if operator_token.type == TokenType.IS:
                if self.match(TokenType.NOT):
                    operator_token = Token(TokenType.NOT, "is not", None, operator_token.line)
                elif self.match(TokenType.LESS):
                    operator_token = Token(TokenType.LESS, "is less", None, operator_token.line)
                    if self.match(TokenType.THAN): pass
                elif self.match(TokenType.GREATER):
                    operator_token = Token(TokenType.GREATER, "is greater", None, operator_token.line)
                    if self.match(TokenType.THAN): pass
            
            # Handle 'greater than', 'less than' (without 'is')
            elif operator_token.type in [TokenType.GREATER, TokenType.LESS]:
                if self.match(TokenType.THAN): pass
                
            right = self.comparison()
            expr = Binary(expr, operator_token, right)
        return expr

    def comparison(self):
        # Comparison operators are now handled in equality() to support 'is less than'
        return self.term()

    def term(self):
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.OVER, TokenType.TIMES):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        
        if self.match(TokenType.CALL):
            return self.call()

        if self.match(TokenType.PYTHON):
            return self.python_access()
            
        return self.primary()

    def python_access(self):
        # python math.pi
        chain = []
        chain.append(self.consume(TokenType.IDENTIFIER, "Expect python module name.").lexeme)
        
        while self.match(TokenType.DOT):
            chain.append(self.consume(TokenType.IDENTIFIER, "Expect property name.").lexeme)
            
        return PythonAccess(chain)

    def call(self):
        # call name with arg1, arg2
        # OR call python module.func with ...
        
        callee = None
        callee_token = self.peek() # For error reporting
        
        if self.match(TokenType.PYTHON):
            callee = self.python_access()
        else:
            callee_name = self.consume(TokenType.IDENTIFIER, "Expect function name after 'call'.")
            callee = Variable(callee_name)
        
        arguments = []
        if self.match(TokenType.WITH):
             if not self.check(TokenType.EOF): # simple check, real logic is loop
                while True:
                    arguments.append(self.expression()) # arguments are expressions
                    if not self.match(TokenType.COMMA): break
        
        return Call(callee, callee_token, arguments)



    def primary(self):
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.NOTHING): return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self.error(self.peek(), "Expect expression.")

    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def consume(self, type, message):
        if self.check(type): return self.advance()
        raise self.error(self.peek(), message)

    def check(self, type):
        if self.is_at_end(): return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end(): self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def error(self, token, message):
        if token.type == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)
        return ParseError()

    def report(self, line, where, message):
        print(f"⚠️  Code Error [line {line}]: {message}")
        self.had_error = True

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.peek().type in [TokenType.SET, TokenType.SAY, TokenType.CHECK, TokenType.LOOP, TokenType.UPDATE]:
                return
            self.advance()
