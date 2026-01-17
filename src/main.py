import sys
import os
from lexer import Lexer
from parser import Parser, ParseError
from interpreter import Interpreter

# Intellisense (Autocomplete)
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.styles import Style
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

GENESIS_KEYWORDS = [
    'say', 'set', 'check', 'loop', 'while', 'is', 'less', 'greater', 'than', 
    'plus', 'minus', 'times', 'over', 'true', 'false', 'python', 'call', 
    'to', 'with', 'end', 'otherwise', 'please', 'just', 'basically', 'examples', 'exit',
    'update', 'return', 'use', 'then', 'now'
]

COMPLETER = WordCompleter(GENESIS_KEYWORDS, ignore_case=True) if HAS_PROMPT_TOOLKIT else None

def run(source, interpreter, repl_mode=False):
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()

    # For now, just print tokens if we want debug
    # for token in tokens: print(token)

    parser = Parser(tokens)
    
    # In REPL, we might want to accept expressions dynamically, but our parser expects a list of declarations.
    # For simplicity, we just look for statements.
    statements = parser.parse()

    # Stop if there was a syntax error.
    if statements is None: return

    interpreter.interpret(statements)

def run_file(path):
    try:
        with open(path, 'r') as file:
            source = file.read()
        interpreter = Interpreter()
        run(source, interpreter)

    except FileNotFoundError:
        print(f"❌ Oops! I couldn't find the file '{path}'.")
    except Exception as e:
        print(f"❌ System Error: {e}")

def run_prompt():
    interpreter = Interpreter()
    print("✨ Genesis Language REPL (v4.1)")
    print("   - Type 'exit' to quit.")
    print("   - Type 'examples' to see cool demos.")
    print("   (Intellisense Enabled)" if HAS_PROMPT_TOOLKIT else "   (Basic Mode)")

    session = None
    if HAS_PROMPT_TOOLKIT:
        style = Style.from_dict({
            'completion-menu.completion': 'bg:#008888 #ffffff',
            'completion-menu.completion.current': 'bg:#00aaaa #000000',
            'scrollbar.background': 'bg:#88aaaa',
            'scrollbar.button': 'bg:#222222',
        })
        session = PromptSession(completer=COMPLETER, style=style)

    while True:
        try:
            line = ""
            if HAS_PROMPT_TOOLKIT:
                line = session.prompt("> ")
            else:
                line = input("> ")

            if line.strip() == "exit": break
            if not line: continue
            
            # --- Examples Menu ---
            if line.strip() == "examples":
                print("\n📂 Available Examples:")
                examples_dir = os.path.join(os.path.dirname(__file__), "../examples")
                
                # Check if dir exists
                if not os.path.exists(examples_dir):
                    print(f"   ❌ Could not find examples folder at {examples_dir}")
                    continue

                files = [f for f in os.listdir(examples_dir) if f.endswith(".gen")]
                files.sort()
                
                for i, f in enumerate(files):
                    print(f"   {i+1}. {f}")
                
                print("\n   Which one to run? (Enter number)")
                
                choice = ""
                if HAS_PROMPT_TOOLKIT and session:
                    choice = session.prompt("   > ")
                else:
                    choice = input("   > ")

                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(files):
                        target = os.path.join(examples_dir, files[idx])
                        print(f"\n🚀 Running {files[idx]}...\n")
                        try:
                            # Create a fresh interpreter for the example to ensure clean state
                            # But wait, run_file creates a new interpreter internally.
                            run_file(target)
                        except Exception as e:
                            print(f"❌ Script Error: {e}")
                        
                        print("\n✨ Done.")
                    else:
                        print("❌ Invalid number.")
                continue
            # ---------------------

            run(line, interpreter, repl_mode=True)
            
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
             print(f"❌ Error: {e}")

def main():
    if len(sys.argv) > 2:
        print("Usage: python3 main.py [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()

if __name__ == '__main__':
    main()
