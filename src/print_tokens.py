import sys
from lexer import Lexer

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 print_tokens.py <filename>")
        return

    filename = sys.argv[1]
    with open(filename, 'r') as file:
        source = file.read()

    lexer = Lexer(source)
    tokens = lexer.scan_tokens()

    for token in tokens:
        print(token)

if __name__ == '__main__':
    main()
