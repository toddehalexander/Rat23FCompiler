from lexer import Lexer, SymbolTable, Assembly
from syntax_analyzer import parser


def main():
    try:
        # Get the input file name from the user
        input_file = input('Enter the input file name: ')

        # Check if the input file name is empty
        if input_file == '':
            print('Missing input file.')
            quit()

        # Get the output file name from the user
        output_file = input('Enter the output file name (press Enter for default): ')

        # Check if the output file name is empty
        if not output_file:
            output_file = 'output.txt'

        # Open the input file and perform lexical analysis
        with open(input_file, 'r') as code:
            lex = Lexer(code)
            lex.tokenize()

            # Perform syntax analysis
            syntax = parser(lex.tokens)
            syntax.parse()

            # Create symbol table and perform semantic analysis
            symbol = SymbolTable(syntax.tokens)
            symbol.parse()

            # Generate assembly code
            instructions = Assembly(syntax.tokens, symbol.table)
            instructions.parse()

            print('\nAssembly Code')
            for item in instructions.instructions:
                if item[2] != 'nil':
                    print(f"{item[0]:<8} {item[1]:<9} {item[2]:<10}")
                else:
                    print(f"{item[0]:<8} {item[1]:<9}")

            with open(output_file, 'w') as f:
                f.write('Symbol Table\n')
                f.write('Identifier   MemoryLocation   Type\n')
                for item in symbol.table:
                    f.write(f"{item['token']:<13} {item['memory']:<16} {item['lexeme']}\n")
                f.write('\nAssembly Code\n')
                for item in instructions.instructions:
                    if item[2] != 'nil':
                        f.write(f"{item[0]:<8} {item[1]:<9} {item[2]:<10}\n")
                    else:
                        f.write(f"{item[0]:<8} {item[1]:<9}\n")

            print(f"\nOutput written to {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        print('Invalid input or output file')
        quit()

if __name__ == '__main__':
    main()