import argparse
import lexer

EPSILON = 'epsilon'
START = 'S'
VERTICAL_BAR = 'VERTICAL_BAR'
CLOSE_BRACKET_FOR_OUTPUT = 'CLOSE_BRACKET_FOR_OUTPUT'

NAME = 'python vcparser.py'
DESCRIPTION = 'this is a parser for the VC programming language. It takes a source file and outputs an abstract syntax tree in the form of a nested list.'
EPILOG = 'this is a part of the VC compiler project | author: duongoku'

rules = {}
non_terminals = set()
terminals = set()
firsts = {}
follows = {}
dynamic_tokens = set()

def load_data(filename='grammar.dat'):
    """
    Parameters
    ----------
    filename : str, optional
        the name of the file to load, by default 'grammar.dat'

    Returns
    -------
    None
    """
    global rules, non_terminals, terminals, START, dynamic_tokens

    start_is_set = False

    with open(filename, 'r') as f:
        # The first line is the list of dynamic tokens
        # Which means that they are terminals in the grammar but they are not keywords
        # E.g. the token 'FLOAT_LITERAL' is a dynamic token
        # because it is a terminal in the grammar but it is not a keyword
        dynamic_tokens_string = f.readline()
        dynamic_tokens = set(map(lambda x: x.strip(), dynamic_tokens_string.strip().split('|')))

        for line in f:
            if line.strip():
                # Split the line into the left hand side and the right hand side
                temp = line.strip().split('->')
                temp[0] = temp[0].strip()

                # START symbol is the first left hand side symbol in the grammar
                if not start_is_set:
                    START = temp[0]
                    start_is_set = True
                
                # Split the right hand side into a list of rules
                temp_split = temp[1].split('|')
                temp_split = list(map(lambda x: x.replace(VERTICAL_BAR, '|'), temp_split))
                if temp[0] not in rules:
                    rules[temp[0]] = list()
                rules[temp[0]] += list(map(lambda x: x.strip().split(' '),temp_split))

                # Add left hand side symbol to the set of non-terminals
                non_terminals.add(temp[0])

    # Add all terminals to the set of terminals
    for rule in rules:
        for i in range(len(rules[rule])):
            for j in range(len(rules[rule][i])):
                if rules[rule][i][j] not in non_terminals:
                    terminals.add(rules[rule][i][j])

    # print(rules)
    # print(non_terminals)
    # print(terminals)
    # print()

def first(symbol_list):
    """
    Parameters
    ----------
    symbol_list : list
        a list of symbols (a string of symbols)

    Returns
    -------
    set
        the set of firsts of the given symbol list
    """

    # Use a global dictionary to cache the firsts of each symbol
    # Caching helps to reduce the number of recursive calls
    global firsts
    if len(symbol_list) == 0:
        return set()
    
    symbol = symbol_list[0]
    temp_first = set()

    if symbol in firsts:
        # If the first of the symbol is already cached, then use the cached value
        temp_first = firsts[symbol].copy()
    else:
        if symbol not in non_terminals:
            # If the symbol is a terminal, then the first of the symbol is the symbol itself
            temp_first.add(symbol)
        else:
            for rule in rules[symbol]:
                if rule[0] not in non_terminals:
                    # If the leading symbol of the rule is a terminal, then add it to the first set
                    temp_first.add(rule[0])
                else:
                    i = 0
                    temp = first([rule[0]])
                    while EPSILON in temp and i < len(rule) - 1:
                        # While the first of the leading symbol of the rule contains epsilon
                        # And the leading symbol is not the last symbol in the rule
                        # Then we need to add the first of the next symbol in the rule
                        temp -= {EPSILON}
                        temp |= first([rule[i + 1]])
                        i += 1
                    temp_first |= temp

    if EPSILON in temp_first and len(symbol_list) > 1:
        # If the first of the first symbol in the symbol list contains epsilon
        # Then we need to add the first of remaining symbols in the symbol list
        temp_first -= {EPSILON}
        temp_first |= first(symbol_list[1:])

    firsts[symbol] = temp_first.copy()
    return temp_first.copy()

def follow(symbol):
    """
    Parameters
    ----------
    symbol : str
        The symbol to find the follow of

    Returns
    -------
    set
        The set of follows of the given symbol
    """
    
    # Use a global dictionary to cache the follows of each symbol
    # Caching helps to reduce the number of recursive calls
    global follows
    if symbol in follows:
        return follows[symbol].copy()
    
    follows[symbol] = set()

    if symbol == START:
        # The follow of the start symbol is $
        follows[symbol].add('$')
    for rule in rules:
        for i in range(len(rules[rule])):
            if symbol in rules[rule][i]:
                if symbol == rules[rule][i][-1]:
                    # If the symbol is the last symbol in the rule
                    # Then the follow of the symbol is the follow of the left hand side symbol
                    if rule != symbol:
                        follows[symbol] |= follow(rule)
                else:
                    if rules[rule][i][rules[rule][i].index(symbol) + 1] not in non_terminals:
                        # If the next symbol of the symbol is a terminal
                        # Then the follow of the symbol is the next symbol
                        follows[symbol].add(rules[rule][i][rules[rule][i].index(symbol) + 1])
                    else:
                        # Else add the first set of the next to last symbols in the rule to the follow set
                        follows[symbol] |= first(rules[rule][i][rules[rule][i].index(symbol) + 1:])
                        if EPSILON in follows[symbol]:
                            follows[symbol] -= {EPSILON}
                            follows[symbol] |= follow(rule)

    return follows[symbol].copy()

def get_parse_table(rules):
    """
    Parameters
    ----------
    rules : dict
        The rules of the grammar

    Returns
    -------
    parse_table : dict
        The parse table of the grammar
    """

    parse_table = {}
    for rule in rules:
        for i in range(len(rules[rule])):
            temp = first(rules[rule][i])
            for symbol in temp:
                # For each symbol in the first set of the right hand side of the rule
                # Add the rule to the parse table
                if (rule, symbol) not in parse_table:
                    parse_table[(rule, symbol)] = []
                if rules[rule][i] not in parse_table[(rule, symbol)]:
                    parse_table[(rule, symbol)].append(rules[rule][i])
            if EPSILON in temp:
                # In case the first set of the rule contains epsilon
                # Then add the follow set of the rule to the parse table
                for symbol in follow(rule):
                    if (rule, symbol) not in parse_table:
                        parse_table[(rule, symbol)] = []    
                    if rules[rule][i] not in parse_table[(rule, symbol)]:                    
                        parse_table[(rule, symbol)].append(rules[rule][i])
                if '$' in follow(rule):
                    # If the follow set of the rule contains $
                    # Then add the rule to the parse table
                    if (rule, '$') not in parse_table:
                        parse_table[(rule, '$')] = []
                    if rules[rule][i] not in parse_table[(rule, '$')]:
                        parse_table[(rule, '$')].append(rules[rule][i])

    
    # Check for conflicts in the parse table
    for rule in parse_table:
        if len(parse_table[rule]) > 1:
            print('The grammar is not LL(1)')
            print(f'Conflicts in the parse table for {rule}')
            print(rule, parse_table[rule])
            exit()

    return parse_table

def parse(parse_table, token_list):
    """
    Parameters
    ----------
    parse_table : dict
        The parse table
    token_list : list
        The list of tokens

    Returns
    -------
    result : list
        The abstract syntax tree in the form of a nested list
    """

    # print(token_list)
    # print()

    result = []
    stack = ['$']
    stack.append(START)
    token_list.append({'token': '$', 'type': '$'})
    while len(stack) > 0:
        if stack[-1] == EPSILON:
            stack.pop()
            continue
        # Pop CLOSE_BRACKET_FOR_OUTPUT out for output
        # The purpose of CLOSE_BRACKET_FOR_OUTPUT is to group the output
        if stack[-1] == CLOSE_BRACKET_FOR_OUTPUT:
            result.append(')')
            stack.pop()
            continue
        # print(stack)
        current_token = token_list[0]['token']
        if token_list[0]['type'] in dynamic_tokens:
            # If the token is a dynamic token then take the type of the token
            # If not, use the token value itself
            # This is to match the token type in the parse table
            current_token = token_list[0]['type']
        if stack[-1] == current_token:
            # Pop if match
            # Replace ( and ) with OPEN_BRACKET and CLOSE_BRACKET
            # to avoid confusion with the output
            result.append(token_list[0]['token'].replace('(', 'OPEN_BRACKET').replace(')', 'CLOSE_BRACKET'))
            # result.append('(' + token_list[0]['token'] + ')')
            stack.pop()
            token_list.pop(0)
        elif stack[-1] in terminals:
            return f'Error: Expecting {stack[-1]} but got {current_token}'
        elif (stack[-1], current_token) not in parse_table:
            return f'Error: Expecting {stack[-1]} but got {current_token}'
        else:
            # Push next if not match
            temp = parse_table[(stack[-1], current_token)]
            stack.pop()
            if len(temp[0]) > 1:
                # If there are more than one child in the left hand side of the rule
                # Then push CLOSE_BRACKET_FOR_OUTPUT to the stack to group them
                # print(temp[0])
                stack.append(CLOSE_BRACKET_FOR_OUTPUT)
                result.append('(')
            stack += temp[0][::-1]

    stack = []
    
    # Remove unnecessary brackets
    for i in range(len(result)):
        if result[i] == '(':
            stack.append('(')
        elif result[i] == ')':
            temp = []
            count = 0
            while stack[-1] != '(':
                count += 1
                temp.append(stack.pop())
            temp = temp[::-1]
            stack.pop()
            if count > 1:
                stack.append('( '+' '.join(temp)+' )')
            else:
                stack.append(' '.join(temp))
        else:
            stack.append(result[i])

    # Revert the parentheses to their original form
    return stack[0].replace('OPEN_BRACKET', '(').replace('CLOSE_BRACKET', ')')

def indent(nest):
    """
    Parameters
    ----------
    nest : int
        The number of indents to add.

    Returns
    -------
    str
        A string of indents.
    """

    return '{}   '.format('|') * nest

def pretty_print(str):
    """
    Parameters
    ----------
    str : str
        A string representation of a nested list.

    Returns
    -------
    str
        A pretty printed version of the string.
    """

    # Pretty print script from https://gist.github.com/kodo-pp/89cefb17a8772cd9fd7b875d94fd29c7
    nest = 0
    comma = False
    result = ''
    for c in str:
        if c != ' ':
            if comma:
                comma = False
                result += '\n'
                result += indent(nest)
        if c in '[({<':
            result += c + '\n'
            nest += 1
            result += indent(nest)
        elif c in '])}>':
            result += '\n'
            nest -= 1
            result += indent(nest)
            result += c
        elif c == ',':
            comma = True
            result += ','
        elif c != ' ':
            result += c
        elif c == ' ':
            if not comma or nest <= 0:
                result += c
    return result


if __name__ == '__main__':
    # Parse the command line arguments
    parser = argparse.ArgumentParser(
        prog=NAME,
        description=DESCRIPTION,
        epilog=EPILOG,
    )

    parser.add_argument("filename")
    parser.add_argument("lexer_data", nargs="?", default="dfa.dat")
    parser.add_argument("parser_data", nargs="?", default="grammar.dat")
    args = parser.parse_args()

    filename = args.filename
    lexer_data = args.lexer_data
    parser_data = args.parser_data

    load_data(parser_data)
    # load_data('test_ll1.dat')
    # load_data('ll1_refactoring.dat')
    
    # temp = ''
    
    # print()
    for rule in rules:
        first([rule])
        # print(f'First({rule}) = {first([rule])}'.replace(EPSILON, 'ε'))
        # temp += f'{rule}\t\t\t\t\t\t{{{", ".join(list(first([rule])))}}}\n'.replace(EPSILON, 'ε')
    

    # print()
    for rule in rules:
        follow(rule)
        # print(f'Follow({rule}) = {follow(rule)}')
        # temp += f'{rule}\t\t\t\t\t\t{{{", ".join(list(follow(rule)))}}}\n'.replace(EPSILON, 'ε')

    # print()
    p = get_parse_table(rules)
    # for i in p:
    #     if len(p[i]) > 1 or False:
    #         print(i, p[i])

    token_list = lexer.run_lexer(filename, lexer_data, True)
    result = parse(p, token_list)

    # Remove extension from filename
    filename = filename.split(".")
    filename = ".".join(filename[:-1])
    output_filename = filename + ".vcps"
    with open(output_filename, "w+") as file:
        file.write(pretty_print(result))
    
    print("Exported AST to: " + output_filename)