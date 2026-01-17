from tokens import TokenType, Token

class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

        self.keywords = {
            "set": TokenType.SET,
            "to": TokenType.TO,
            "update": TokenType.UPDATE,
            "say": TokenType.SAY,
            "check": TokenType.CHECK,
            "then": TokenType.THEN,
            "otherwise": TokenType.OTHERWISE,
            "end": TokenType.END,
            "loop": TokenType.LOOP,
            "while": TokenType.WHILE,
            "do": TokenType.DO,
            "is": TokenType.IS,
            "not": TokenType.NOT,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "greater": TokenType.GREATER,
            "less": TokenType.LESS,
            "than": TokenType.THAN,
            "plus": TokenType.PLUS,
            "minus": TokenType.MINUS,
            "times": TokenType.TIMES,
            "over": TokenType.OVER,
            "with": TokenType.WITH,
            "return": TokenType.RETURN,
            "use": TokenType.USE,
            "python": TokenType.PYTHON,
            "call": TokenType.CALL,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
            "nothing": TokenType.NOTHING,
        }

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        
        if c == '(': self.add_token(TokenType.LEFT_PAREN)
        elif c == ')': self.add_token(TokenType.RIGHT_PAREN)
        elif c == ',': self.add_token(TokenType.COMMA)
        elif c == '.': self.add_token(TokenType.DOT)
        
        # We can support comments still? Maybe standard // is too C-like?
        # Let's keep it simple and maybe "note:" ? or just #?
        # Let's support # for comments as it's cleaner
        elif c == '#':
            while self.peek() != '\n' and not self.is_at_end():
                self.advance()
                
        elif c in [' ', '\r', '\t']:
            pass
        elif c == '\n':
            self.line += 1
            
        elif c == '"':
            self.string('"')
        elif c == "'":
            self.string("'")
            
        else:
            if self.is_digit(c):
                self.number()
            elif self.is_alpha(c):
                self.identifier()
            else:
                # In this new language, maybe we just ignore unknown symbols or error?
                # for now, error
                print(f"Evaluate Error: Unexpected character '{c}' at line {self.line}")

    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        
        # Noise Words Filter (v4)
        # These words are completely ignored (Lexer won't emit tokens for them)
        # This allows "set the x to 5" -> "set x to 5"
        if text.lower() in [
            "the", "a", "an", "was", "now", "please", "just", "so", 
            "basically", "every", "in", "of", "ok", "well", "hey", "bro", "like"
        ]:
            return 

        # Check against keywords
        type = self.keywords.get(text.lower(), TokenType.IDENTIFIER)
        self.add_token(type)


    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == '.' and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def string(self, quote_char):
        while self.peek() != quote_char and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            print(f"Evaluate Error: Unterminated string at line {self.line}")
            return

        self.advance()
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def peek(self):
        if self.is_at_end(): return '\0'
        return self.source[self.current]
    
    def peek_next(self):
        if self.current + 1 >= len(self.source): return '\0'
        return self.source[self.current + 1]

    def is_alpha(self, c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'

    def is_digit(self, c):
        return c >= '0' and c <= '9'

    def is_alpha_numeric(self, c):
        return self.is_alpha(c) or self.is_digit(c)

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self, type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))
