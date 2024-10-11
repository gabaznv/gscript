import re
import sys

# Lexer to tokenize the input code, including mathematical operators
def lex(code):
    tokens = []
    token_specification = [
        ('PRINT', r'print'),            # Match the 'print' keyword
        ('STRING', r'"[^"]*"'),         # Match strings enclosed in double quotes
        ('NUMBER', r'\d+'),             # Match numbers
        ('VARIABLE', r'[a-zA-Z_]\w*'),  # Match variable names (alphanumeric)
        ('EQUALS', r'='),               # Match assignment operator
        ('OP', r'[+\-*/]'),             # Match mathematical operators
        ('PAREN', r'[\(\)]'),           # Match parentheses
        ('SKIP', r'[ \t]+'),            # Skip over spaces and tabs
        ('MISMATCH', r'.'),             # Catch any other characters (invalid tokens)
    ]
    token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup
        value = match.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected token: {value}')
        else:
            tokens.append((kind, value))
    return tokens

# Parser to create an abstract syntax tree (AST) from tokens
def parse(tokens):
    if tokens[0][0] == 'PRINT' and tokens[1][0] == 'PAREN' and tokens[-1][0] == 'PAREN':
        # Handle print statements
        if tokens[2][0] in ('STRING', 'VARIABLE', 'NUMBER'):
            return {'action': 'print', 'value': tokens[2:]}  # return list of tokens for later evaluation
        else:
            raise SyntaxError('Expected a string, number, or variable')
    elif tokens[1][0] == 'EQUALS':
        # Handle variable assignment with mathematical expressions
        return {'action': 'assign', 'var_name': tokens[0][1], 'expression': tokens[2:]}  # Expression is all tokens after the '='
    else:
        raise SyntaxError('Invalid syntax')

# Evaluator for mathematical expressions
def evaluate_expression(expression, variables):
    expression_str = ''
    for token in expression:
        kind, value = token
        if kind == 'NUMBER':
            expression_str += value
        elif kind == 'VARIABLE':
            if value in variables:
                expression_str += str(variables[value])
            else:
                raise NameError(f'Undefined variable: {value}')
        elif kind == 'OP':
            expression_str += value
    return eval(expression_str)

# Interpreter to execute the parsed code
def interpret(parsed_code, variables):
    if parsed_code['action'] == 'print':
        value_tokens = parsed_code['value']
        if value_tokens[0][0] == 'STRING':
            print(value_tokens[0][1][1:-1])  # Strip the quotes from the string
        else:
            result = evaluate_expression(value_tokens, variables)
            print(result)  # Print evaluated result of mathematical expression or variable
    elif parsed_code['action'] == 'assign':
        var_name = parsed_code['var_name']
        expression = parsed_code['expression']
        result = evaluate_expression(expression, variables)
        variables[var_name] = result

# Putting everything together
def run_code(code, variables):
    tokens = lex(code)
    parsed_code = parse(tokens)
    interpret(parsed_code, variables)

# Function to run a .gscript file
def run_gscript_file(filename):
    with open(filename, 'r') as file:
        code_lines = file.readlines()
    
    variables = {}  # Dictionary to store variables
    for line in code_lines:
        run_code(line.strip(), variables)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: gscript <filename>.gscript")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    if not filename.endswith('.gscript') and not filename.endswith('.gs'):
        print("Error: File must end with '.gscript' or '.gs' extension.")
        sys.exit(1)
    
    run_gscript_file(filename)
