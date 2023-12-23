# Keywords, separators, and operators
keywords = ['get', 'put', 'return', 'integer', 'function', 'if', 'else', 'endif', 'while', 'real', 'boolean', 'float']
separators = ['(', ')', '{', '}', ';', ',', '#', '\t', ' ']
operators = ['-', '+', '/', '*', '=', '<', '>', '!', '|', '%', '<=', '=>', '==', '!=', '!']
# data types and memory address
MEMORY_ADDRESS = 7000
data_types = ['integer', 'boolean', 'float', 'real']


# Lexer class for tokenization
class Lexer:
    def __init__(self, file):
        # Initialize Lexer with the input file and an empty list for tokens
        self.file = file
        self.tokens = []

    # Tokenize the input file
    def tokenize(self):
        # Convert the input file into a list of characters
        characters = characterize(self.file)
        # Initialize state and current token
        state = ''
        current = []

        count = 0
        for char in characters:
            # Add each character to the current token
            current.append(char['char'])

            # If character is blank, reset the current token
            if char['char'] == ' ':
                current = []
            # Check for the start of a comment and ignore characters until the end of the comment
            elif state == '' and characters[count]['char'] == '[' and characters[count + 1]['char'] == '*':
                state = 'comment'
                current = []
            elif state == 'comment' and characters[count]['char'] == ']' and characters[count - 1]['char'] == '*':
                state = ''
                current = []
            elif state == 'comment':
                current = []
            # Check if the current token is a keyword
            elif ''.join(current) in keywords:
                self.tokens.append({'token': ''.join(current), 'lexeme': 'keyword', 'line': char['line']})
                current = []
            # Check if the current character is a separator
            elif char['char'] in separators:
                self.tokens.append({'token': char['char'], 'lexeme': 'separator', 'line': char['line']})
                current = []
            # Check if the current character is an operator
            elif char['char'] in operators:
                self.tokens.append({'token': char['char'], 'lexeme': 'operator', 'line': char['line']})
                current = []
            # As long as char isn't at the end, determine everything else
            elif char['char'] != 'endoffile':
                if is_endofword(characters[count + 1]['char']):
                    self.process_end_of_word(char, current)
                    current = []

            count += 1

    # Process the end of a word
    def process_end_of_word(self, char, current):
        # Determine the type of word and add it to the token list
        if is_int(''.join(current)):
            self.tokens.append({'token': ''.join(current), 'lexeme': 'int', 'line': char['line']})
        elif is_real(''.join(current)):
            self.tokens.append({'token': ''.join(current), 'lexeme': 'real', 'line': char['line']})
        elif is_identifier(''.join(current)):
            self.tokens.append({'token': ''.join(current), 'lexeme': 'identifier', 'line': char['line']})
        else:
            self.tokens.append({'token': ''.join(current), 'lexeme': 'undefined', 'line': char['line']})

# FSM and functions for token identification

def is_identifier(token):
    # Finite State Machine for identifying identifiers
    current_state = 0
    for char in token:
        if current_state == 0:
            if char.isalpha():
                current_state = 1
            else:
                return False
        if current_state == 1:
            if char.isalpha():
                pass
            elif char.isnumeric():
                pass
            elif char == '_':
                pass
            else:
                return False
    return current_state == 1

def is_int(token):
    # Finite State Machine for identifying integers
    current_state = 0
    for char in token:
        if current_state == 0:
            if char.isnumeric():
                current_state = 1
            else:
                return False
        elif current_state == 1:
            if char.isnumeric():
                pass
            else:
                return False
    return current_state == 1

def is_real(token):
    # Function to check if a token is a real number
    try:
        float(token)
        return True
    except ValueError:
        return False

# Function to determine comment start and end
def is_comment(state, char, next_char):
    if state == '' and char == '[' and next_char == '*':
        return True
    elif state == 'comment' and char != '*' and next_char != ']':
        return True
    elif state == 'comment' and char == '*' and next_char == ']':
        return False

# Function to check if the next character indicates the end of a word
def is_endofword(next_char):
    return next_char in separators or next_char in operators or next_char == 'endoffile' or next_char == ' '

# Function to convert a file into a list of characters
def characterize(file):
    charlist = []
    linecount = 1
    for line in file:
        for char in line:
            # Add each character to the list with line count if it's not blank
            if char != ' ' and char != '\n':
                newchar = {'char': char, 'line': linecount}
                charlist.append(newchar)
            # Add a blank to the list only once
            if char == ' ' or char == '\n':
                if charlist and charlist[-1]['char'] != ' ':
                    newchar = {'char': ' ', 'line': linecount}
                    charlist.append(newchar)
        linecount += 1
    # Add a character for the end of the file so we know when to stop
    newchar = {'char': 'endoffile', 'line': linecount + 1}
    charlist.append(newchar)
    return charlist


# SymbolTable class for managing the symbol table
class SymbolTable:
    def __init__(self, tokens):
        self.table = []
        self.tokens = tokens
        self.current_memory = MEMORY_ADDRESS

    # Get the previous token in the token list
    def getPreviousToken(self, token):
        index = self.tokens.index(token)
        prev_found = True
        increment = 1
        while prev_found:
            if self.tokens[index - increment]['lexeme'] != 'separator' and self.tokens[index - increment]['lexeme'] != 'operator':
                return self.tokens[index - increment]
            else:
                increment += 1

    # Get the next token in the token list
    def getNextToken(self, token):
        index = self.tokens.index(token)
        next_found = True
        increment = 1
        while next_found:
            if self.tokens[index + increment]['lexeme'] != 'separator' and self.tokens[index + increment]['lexeme'] != 'operator':
                next_found = False
                return self.tokens[index + increment]
            else:
                increment += 1

    # Find the type of a token in the productions
    def findType(self, token):
        check = token['productions'][len(token['productions']) - 1]
        check = check.split()
        if '<Identifier>' in check:
            # Check for various production rules to determine the type
            type_found = False
            new_token = token
            while not type_found:
                for production in new_token['productions']:
                    if production == '<Identifier>':
                        return 'identifier', True
                    # Check if the token is already in the symbol table
                    elif production == '<Expression> -> <Term>' or production == '<Assign> -> <Identifier>':
                        for item in self.table:
                            if item['token'] == new_token['token']:
                                return item['lexeme'], False
                        print("Variable " + token['token'] + ' is being used but is not declared.')
                        quit()
                    # Check for function parameter type
                    elif production == '<Parameter> -> <IDs> <Qualifier>':
                        new_token = self.getNextToken(new_token)
                        if new_token['lexeme'] == 'keyword' and new_token['token'] not in data_types:
                            for symbol in self.table:
                                if symbol['token'] == new_token[token]:
                                    return symbol['lexeme'], True
                        break
                    # Check for variable declaration type
                    elif production == '<Declaration> -> <IDs>' or production == '<IDs> -> <Identifier> , <IDs>' \
                            or (production == '<IDs> -> <Identifier>' and (
                            '<IDs> -> <Identifier> , <IDs>' in self.getPreviousToken(new_token)['productions'])):
                        new_token = self.getPreviousToken(new_token)
                        if new_token['lexeme'] == 'keyword' and new_token['token'] not in data_types:
                            for symbol in self.table:
                                if symbol['token'] == token['token']:
                                    return symbol['lexeme'], False
                        break
                    # Check for specific data types
                    elif production == '<Qualifier> -> integer' or production == '<Primary> -> <Integer>':
                        return 'integer', True
                    elif production == '<Qualifier> -> boolean' or production == '<Primary> -> true' or production == '<Primary> -> false':
                        return 'boolean', True
                    elif production == '<Qualifier> -> real' or production == '<Primary> -> <Real>':
                        return 'real', True
                    # Check for general identifier type
                    elif production == '<Identifier>' or production == '<Primary> -> <Identifier>' or production == '<IDs> -> <Identifier>':
                        for item in self.table:
                            if item['token'] == new_token['token']:
                                return item['lexeme'], False
                        return 'identifier', True
            return 'not found'
        # Check for specific data types in other productions
        elif '<Integer>' in check:
            return 'integer', False
        elif 'true' in check:
            return 'boolean', False
        elif 'false' in check:
            return 'boolean', False

    # Check if a token already exists in the symbol table
    def doesExist(self, token):
        for item in self.table:
            if token['token'] == item['token'] and self.findType(token)[0] == item['lexeme']:
                return True
        return False

    # Insert a symbol into the symbol table
    def insertSymbol(self, token):
        self.table.append({'token': token['token'], 'lexeme': self.findType(token)[0], 'memory': self.current_memory})
        self.current_memory += 1

    # Print the identifiers in the symbol table
    def printIdentifiers(self):
        print('{:^60}'.format('Symbol Table') + '\n')
        print('{:^20}'.format('Identifier') + '{:^20}'.format('Type') + '{:^20}'.format('Memory') + '\n')
        for token in self.table:
            print('{:^20}'.format(token['token']) + '{:^20}'.format(token['lexeme']) + '{:^20}'.format(str(token['memory']) + '\n'))
        print('\n')

    # Parse the token list and populate the symbol table
    def parse(self):
        for token in self.tokens:
            if token['lexeme'] == 'identifier':
                isbeingdeclared = self.findType(token)[1]
                if self.doesExist(token) and isbeingdeclared:
                    print('Error: token ' + token['token'] + ' is being declared twice.')
                    quit()
                elif isbeingdeclared:
                    self.insertSymbol(token)
        self.printIdentifiers()

# Assembly class for generating assembly code
class Assembly:
    def __init__(self, tokens, symbols):
        self.expressions = {'+': self.add, '-': self.sub, '*': self.mul, '/': self.div}
        self.relop = {'==': self.equ, '!=': self.neq, '>': self.grt, '<': self.les, '<=': self.leq, '=>': self.geq}
        self.instructions = []
        self.tokens = tokens
        self.symbols = symbols
        self.count = 0

    # Push an integer value onto the stack
    def pushi(self, iv):
        self.count += 1
        instruction = [self.count, 'PUSHI', iv]
        self.instructions.append(instruction)

    # Push the value at a memory location onto the stack
    def pushm(self, ml):
        self.count += 1
        instruction = [self.count, 'PUSHM', ml]
        self.instructions.append(instruction)

    # Pop the value from the stack to a memory location
    def popm(self, ml):
        self.count += 1
        instruction = [self.count, 'POPM', ml]
        self.instructions.append(instruction)

    # Print the top value of the stack
    def stdout(self):
        self.count += 1
        instruction = [self.count, 'STDOUT', 'nil']
        self.instructions.append(instruction)

    # Read input from the user and store it at a memory location
    def stdin(self):
        self.count += 1
        instruction = [self.count, 'STDIN', 'nil']
        self.instructions.append(instruction)

    # Add the top two values on the stack
    def add(self):
        self.count += 1
        instruction = [self.count, 'ADD', 'nil']
        self.instructions.append(instruction)

    # Subtract the top value on the stack from the second top value
    def sub(self):
        self.count += 1
        instruction = [self.count, 'SUB', 'nil']
        self.instructions.append(instruction)

    # Multiply the top two values on the stack
    def mul(self):
        self.count += 1
        instruction = [self.count, 'MUL', 'nil']
        self.instructions.append(instruction)

    # Divide the second top value on the stack by the top value
    def div(self):
        self.count += 1
        instruction = [self.count, 'DIV', 'nil']
        self.instructions.append(instruction)

    # Check if the second top value on the stack is greater than the top value
    def grt(self):
        self.count += 1
        instruction = [self.count, 'GRT', 'nil']
        self.instructions.append(instruction)

    # Check if the second top value on the stack is less than the top value
    def les(self):
        self.count += 1
        instruction = [self.count, 'LES', 'nil']
        self.instructions.append(instruction)

    # Check if the top two values on the stack are equal
    def equ(self):
        self.count += 1
        instruction = [self.count, 'EQU', 'nil']
        self.instructions.append(instruction)

    # Check if the top two values on the stack are not equal
    def neq(self):
        self.count += 1
        instruction = [self.count, 'NEQ', 'nil']
        self.instructions.append(instruction)

    # Check if the second top value on the stack is greater than or equal to the top value
    def geq(self):
        self.count += 1
        instruction = [self.count, 'GEQ', 'nil']
        self.instructions.append(instruction)

    # Check if the second top value on the stack is less than or equal to the top value
    def leq(self):
        self.count += 1
        instruction = [self.count, 'LEQ', 'nil']
        self.instructions.append(instruction)

    # Jump to a specified instruction if the top value on the stack is zero
    def jumpz(self, il):
        self.count += 1
        instruction = [self.count, 'JUMPZ', il]
        self.instructions.append(instruction)

    # Unconditional jump to a specified instruction
    def jump(self, il):
        self.count += 1
        instruction = [self.count, 'JUMP', il]
        self.instructions.append(instruction)

    # Label a specific instruction
    def label(self):
        self.count += 1
        instruction = [self.count, 'LABEL', 'nil']
        self.instructions.append(instruction)

    # Scan input for identifiers
    def scan(self, pos):
        while '<Scan> -> get (<IDs>);' not in self.tokens[pos]['productions']:
            pos += 1
        while self.tokens[pos]['token'] != ')':
            if self.tokens[pos]['lexeme'] == 'identifier':
                self.stdin()
                self.popm(self.getmemloc(self.tokens[pos]['token']))
            pos += 1
        pos += 2
        return pos

    # Print expressions to output
    def print(self, pos):
        while '<Print> -> put (<Expression>);' not in self.tokens[pos]['productions']:
            pos += 1
        pos += 2
        pos = self.getexpr(pos)
        self.stdout()
        pos += 1
        return pos

    # Process return statements
    def ret(self, pos):
        while '<Return> -> return; | return <Expression>;' not in self.tokens[pos]['productions']:
            pos += 1
        pos += 1
        if self.tokens[pos]['token'] == ';':
            pos += 1
        else:
            pos = self.getexpr(pos)
        return pos

    # Process assignment statements
    def assign(self, pos):
        while '<Assign> -> <Identifier> = <Expression>;' not in self.tokens[pos]['productions']:
            pos += 1
        ident = pos
        pos += 2
        pos = self.getexpr(pos)
        self.popm(self.getmemloc(self.tokens[ident]['token']))
        return pos

    # Process if statements
    def ifstat(self, pos):
        while self.tokens[pos]['token'] != 'if':
            pos += 1
        temp = pos
        pos += 2
        pos = self.getexpr(pos)
        relop = pos - 1
        if self.tokens[pos]['token'] + self.tokens[pos-1]['token'] in self.relop:
            pos += 1
        pos = self.getexpr(pos)
        self.getrelop(relop)
        self.jumpz(0)
        jump = self.count - 1
        end = 0
        for item in self.tokens[temp]['productions']:
            if item == '<Statement> -> <Scan>':
                pos = self.scan(pos)
            elif item == '<Statement> -> <Print>':
                pos = self.print(pos)
            elif item == '<Statement> -> <Return>':
                pos = self.ret(pos)
            elif item == '<Statement> -> <Assign>':
                pos = self.assign(pos)
            elif item == '<Statement> -> <If>':
                pos = self.ifstat(pos)
            elif item == '<Statement> -> <While>':
                pos = self.whilestat(pos)
            elif item == '<If> -> if (<Condition>) <Statement> else <Statement> endif':
                self.jump(end)
                self.instructions[jump][2] = self.count + 1
                end = self.count - 1
        if self.instructions[jump][2] == 0:
            self.instructions[jump][2] = self.count + 1
        if end != 0:
            self.instructions[end][2] = self.count + 1
        pos += 1
        if self.tokens[pos]['token'] == 'endif':
            pos += 1
        if self.tokens[pos]['token'] == '#':
            self.label()
        return pos

        # Process while statements
    def whilestat(self, pos):
        while self.tokens[pos]['token'] != 'while':
            pos += 1
        self.label()
        labelpos = self.count
        temp = pos
        pos += 2
        pos = self.getexpr(pos)
        relop = pos - 1
        if self.tokens[pos]['token'] + self.tokens[pos-1]['token'] in self.relop:
            pos += 1
        pos = self.getexpr(pos)
        self.getrelop(relop)
        self.jumpz(0)
        jump = self.count - 1
        for item in self.tokens[temp]['productions']:
            if item == '<Statement> -> <Scan>':
                pos = self.scan(pos)
            elif item == '<Statement> -> <Print>':
                pos = self.print(pos)
            elif item == '<Statement> -> <Return>':
                pos = self.ret(pos)
            elif item == '<Statement> -> <Assign>':
                pos = self.assign(pos)
            elif item == '<Statement> -> <If>':
                pos = self.ifstat(pos)
            elif item == '<Statement> -> <While>':
                pos = self.whilestat(pos)
        self.jump(labelpos)
        self.instructions[jump][2] = self.count + 1
        pos += 1
        if self.tokens[pos]['token'] == '#':
            self.label()
        return pos

    # Process expressions
    def getexpr(self, pos):
        operpos = -1
        while True:
            if self.tokens[pos]['lexeme'] == 'int' or self.tokens[pos]['lexeme'] == 'real':
                self.pushi(self.tokens[pos]['token'])
                if operpos != -1:
                    self.getoper(operpos)
                    operpos = -1
            elif self.tokens[pos]['token'] == 'true':
                self.pushi(1)
                if operpos != -1:
                    self.getoper(operpos)
                    operpos = -1
            elif self.tokens[pos]['token'] == 'false':
                self.pushi(0)
                if operpos != -1:
                    self.getoper(operpos)
                    operpos = -1
            elif self.tokens[pos]['lexeme'] == 'identifier':
                self.pushm(self.getmemloc(self.tokens[pos]['token']))
                # insert test for function
                if operpos != -1:
                    self.getoper(operpos)
                    operpos = -1
            elif self.tokens[pos]['token'] == '(':
                pos += 1
                pos = self.getexpr(pos)
                pos -= 1
                if operpos != -1:
                    self.getoper(operpos)
                    operpos = -1
            elif self.tokens[pos]['token'] in self.expressions:
                operpos = pos
            else:
                pos += 1
                break
            pos += 1
        return pos

    # Process operators
    def getoper(self, pos):
        method = self.expressions[self.tokens[pos]['token']]
        method()

    # Process relational operators
    def getrelop(self, pos):
        if self.tokens[pos]['token'] + self.tokens[pos+1]['token'] in self.relop:
            method = self.relop[self.tokens[pos]['token'] + self.tokens[pos + 1]['token']]
            method()
        else:
            method = self.relop[self.tokens[pos]['token']]
            method()

    # Get memory location of a token
    def getmemloc(self, token):
        for item in self.symbols:
            if item['token'] == token:
                return item['memory']

    # Process production rules
    def getprod(self, token, pos):
        for item in token['productions']:
            if item == '<Statement> -> <Scan>':
                pos = self.scan(pos)
            elif item == '<Statement> -> <Print>':
                pos = self.print(pos)
            elif item == '<Statement> -> <Return>':
                pos = self.ret(pos)
            elif item == '<Statement> -> <Assign>':
                pos = self.assign(pos)
            elif item == '<Statement> -> <If>':
                pos = self.ifstat(pos)
            elif item == '<Statement> -> <While>':
                pos = self.whilestat(pos)
        return pos

    # Find a specific token in the token list
    def find(self, tok, pos):
        val = {}
        if tok == '#':
            for token in self.tokens:
                if token['token'] == '#':
                    val = token
                    break
                pos += 1
        else:
            for token in self.tokens:
                if token['token'] == tok and self.tokens[pos - 1]['token'] == 'function':
                    val = self.tokens[pos - 1]
                    break
                pos += 1
        return val, pos

    # Parse the token list and generate assembly code
    def parse(self):
        main = self.find('#', 0)
        self.getprod(main[0], main[1])
