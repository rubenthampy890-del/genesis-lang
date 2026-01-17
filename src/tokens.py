from enum import Enum, auto

class TokenType(Enum):
    # Single-character tokens (Mostly for structure if needed, but we rely on keywords)
    LEFT_PAREN = auto()  # ( - useful for grouping math
    RIGHT_PAREN = auto() # )
    COMMA = auto()
    DOT = auto()
    
    # We treat newlines as statement separators in this new version, or just optional
    EOF = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords (The core of the new syntax)
    SET = auto()    # set
    TO = auto()     # to
    UPDATE = auto() # update (for assignment)
    SAY = auto()    # say (print)
    
    CHECK = auto()      # check (if)
    THEN = auto()       # then (start block)
    OTHERWISE = auto()  # otherwise (else)
    END = auto()        # end (close block)
    
    LOOP = auto()   # loop
    WHILE = auto()  # while
    DO = auto()     # do
    
    # Logic / Comparison
    IS = auto()      # is (==)
    NOT = auto()     # not (!= if used with is, or unary !)
    AND = auto()     # and
    OR = auto()      # or
    GREATER = auto() # greater
    LESS = auto()    # less
    THAN = auto()    # than
    
    # Math
    PLUS = auto()   # plus (+)
    MINUS = auto()  # minus (-)
    TIMES = auto()  # times (*)
    OVER = auto()   # over (/)
    
    # Function / Integration Keywords
    WITH = auto()   # with (args)
    RETURN = auto() # return
    USE = auto()    # use (import)
    PYTHON = auto() # python (bridge)
    CALL = auto()   # call (invoke)
    
    TRUE = auto()
    FALSE = auto()
    NOTHING = auto() # null

class Token:
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self):
        return f"{self.type.name} {self.lexeme} {self.literal}"
