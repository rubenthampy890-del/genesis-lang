class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        key = name
        if hasattr(name, 'lexeme'):
            key = name.lexeme
            
        if key in self.values:
            return self.values[key]
        
        if self.enclosing:
            return self.enclosing.get(name)

        raise RuntimeError(f"Undefined variable '{key}'.")

    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        raise RuntimeError(f"Undefined variable '{name.lexeme}'.")
