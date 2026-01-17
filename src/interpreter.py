from tokens import TokenType
from ast_nodes import *
from environment import Environment
import time
import importlib

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class RuntimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token

class GenesisFunction:
    def __init__(self, declaration):
        self.declaration = declaration

    def call(self, interpreter, arguments):
        environment = Environment(interpreter.environment) # Closure? No, globals for now + dynamic scope issues? 
        # Actually proper closures require capturing closure at definition time.
        # For simplicity v1: just new env with global parent? No, scope is static.
        # "environment" param in interpret() creates local scope.
        # But we need closure support for 'global' variables to work?
        # Let's assume global scope is available via chain.
        # We need to capture the environment where function was defined? 
        # Let's stick to dynamic for MVP or use the interpreter's 'globals' if we track them.
        # BETTER: The interpreter passes its current environment, but really we should capture 'closure'
        
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
            
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as returnValue:
            return returnValue.value
        return None

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"    

class Interpreter:
    def __init__(self):
        self.environment = Environment()
        self.python_modules = {} # Store imported python modules

    def interpret(self, statements):
        try:
            for statement in statements:
                if statement:
                    self.execute(statement)
        except RuntimeError as error:
            line_info = f"[line {error.token.line}]" if error.token else ""
            print(f"{error}\n{line_info}")

    def execute(self, stmt):
        stmt.accept(self)

    def evaluate(self, expr):
        return expr.accept(self)
    

    def visit_function_stmt(self, stmt):
        function = GenesisFunction(stmt)
        # We define it in the current environment
        self.environment.define(stmt.name.lexeme, function)

    def visit_return_stmt(self, stmt):
        value = None
        if stmt.value != None:
            value = self.evaluate(stmt.value)
        raise ReturnException(value)

    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if isinstance(callee, GenesisFunction):
            function = callee
            if len(arguments) != function.arity():
                raise RuntimeError(expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")
            return function.call(self, arguments)
        
        elif callable(callee):
            # It's a Python function!
            try:
                return callee(*arguments)
            except Exception as e:
                raise RuntimeError(expr.paren, f"Python Error: {e}")
        else:
             raise RuntimeError(expr.paren, "Can only call functions.")


    def visit_use_stmt(self, stmt):
        try:
            module = importlib.import_module(stmt.module_name)
            # We define the module in the environment so lookup works
            # We use the module name as the variable name (e.g. "math")
            # But wait, logic might need to strip quotes if parser kept them? 
            # Parser: module_name.literal. If it was a string "math", it is just math.
            
            # Simple heuristic: "math" -> define math
            # "os.path" -> define os? Or define path? Standard python: "import os" -> os. "import os.path" -> os (with path).
            # Let's map module name to the LAST part or just the whole thing?
            # Genesis user: use python "math". -> math.pi
            # Genesis user: use python "os". -> os.system
            
            name = stmt.module_name.split('.')[-1] # Simple default
            # Actually, to make 'python math.pi' work, we need 'math' in our python_modules dict or environment.
            # My parser returns PythonAccess with chain starting with "math".
            # So I should store it in a special dictionary in Interpreter?
            self.python_modules[name] = module
            
        except ImportError as e:
            raise RuntimeError(None, f"Could not import python module '{stmt.module_name}': {e}")

    def visit_python_access_expr(self, expr):
        # expr.property_chain is ['math', 'pi'] or ['resp', 'code']
        base_name = expr.property_chain[0]
        
        obj = None
        
        # 1. Check if it is a variable in the environment (e.g. 'resp' from 'set resp to ...')
        try:
            obj = self.environment.get(base_name)
        except Exception:
            # Not a variable, proceed to check modules
            pass
            
        # 2. If not a variable, check explicit imported modules (e.g. 'math')
        if obj is None:
            if base_name in self.python_modules:
                obj = self.python_modules[base_name]
            else:
                 raise RuntimeError(None, f"Name '{base_name}' is not a defined variable or loaded python module.")
        
        # 3. Traverse the chain
        for prop in expr.property_chain[1:]:
            try:
                obj = getattr(obj, prop)
            except AttributeError:
                raise RuntimeError(None, f"Object '{base_name}' has no attribute '{prop}'.")
            
        return obj


    def visit_block_stmt(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer != None:
            value = self.evaluate(stmt.initializer)
        
        self.environment.define(stmt.name.lexeme, value)

    def visit_if_stmt(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch != None:
            self.execute(stmt.else_branch)

    def visit_while_stmt(self, stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_variable_expr(self, expr):
        return self.environment.get(expr.name)

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        if expr.operator.type == TokenType.NOT:
            return not self.is_truthy(right)

        return None

    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        
        if expr.operator.type == TokenType.OVER:
            self.check_number_operands(expr.operator, left, right)
            if float(right) == 0:
                raise RuntimeError(expr.operator, "Division by zero.")
            return float(left) / float(right)
            
        if expr.operator.type == TokenType.TIMES:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
            
        if expr.operator.type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            if isinstance(left, str):
                return left + self.stringify(right)
            if isinstance(right, str):
                return self.stringify(left) + right
            raise RuntimeError(expr.operator, "Operands must be two numbers or two strings.")
        
        if expr.operator.type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        if expr.operator.type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        
        # 'is' (EQUAL)
        if expr.operator.type == TokenType.IS:
            return self.is_equal(left, right)
            
        # 'is not' (NOT)
        if expr.operator.type == TokenType.NOT:
            return not self.is_equal(left, right)

        return None
    
    def visit_logical_expr(self, expr):
        left = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left): return left
        else:
            if not self.is_truthy(left): return left
        
        return self.evaluate(expr.right)

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float): return
        raise RuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float): return
        raise RuntimeError(operator, "Operands must be numbers.")

    def is_truthy(self, object):
        if object is None: return False
        if isinstance(object, bool): return bool(object)
        return True

    def is_equal(self, a, b):
        if a is None and b is None: return True
        if a is None: return False
        return a == b

    def stringify(self, object):
        if object is None: return "nothing"
        if isinstance(object, float):
            text = str(object)
            if text.endswith(".0"):
                text = text[0:len(text)-2]
            return text
        if isinstance(object, bool):
            return "true" if object else "false"
        return str(object)
