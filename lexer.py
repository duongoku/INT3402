import argparse
import json
import time

WHITESPACES = " \t\n\r\f"
NEWLINE = "\r\n"
EXCLUDE = "EXCLUDE"

NAME = "python lexer.py"
DESCRIPTION = "this is a lexer for the VC programming language. It takes a source file and outputs a list of tokens."
EPILOG = "this is a part of the VC compiler project | author: duongoku"

def read_file(path: str):
    with open(path, "r") as file:
        return file.read()
    
def check_match(match: str, char: str):
    if match.startswith(EXCLUDE):
        return char not in match[len(EXCLUDE):]
    return char in match

def lexer(source: str, nodes: dict, keywords: list, special_literals: list, separators: str):
    STARTING_STATE = "0"
    for id in nodes:
        if nodes[id]["starting"]:
            STARTING_STATE = id
            break

    tokens = []
    token = ""
    state = STARTING_STATE
    line = 1
    new_line_stack = ""
    position = 0
    start = position
    index = 0

    while index < len(source):
        char = source[index]
        index += 1
        position += 1
        
        if state == STARTING_STATE and char in WHITESPACES:
            if char not in NEWLINE:
                new_line_stack = ""
            else:
                new_line_stack += char
                line += 1
                position = 0
            if new_line_stack.endswith(NEWLINE):
                new_line_stack = ""
                line -= 1
            continue

        children = nodes[state]["children"]
        found = False
        for match in children.keys():
            if check_match(match, char):
                state = children[match]
                if len(token) == 0:
                    start = position
                token += char
                found = True
                break
            
        if not found:
            index -= 1
            position -= 1
            if nodes[state]["terminal"] and (char in separators or token[-1] in separators):
                if token in keywords:
                    tokens.append({"token": token, "type": "KEYWORD", "line": line, "start": start, "end": position})
                elif token in special_literals:
                    tokens.append({"token": token, "type": "SPECIAL_LITERAL", "line": line, "start": start, "end": position})
                else:
                    tokens.append({"token": token, "type": nodes[state]["terminal_type"], "line": line, "start": start, "end": position})
                if token.endswith("\n"):
                    line += 1
                    position = 0
                token = ""
                state = STARTING_STATE
            else:
                error_msg = f"Error while parsing '{token}': invalid character at line {line}({position}): '{char}', "
                expecting = list(nodes[state]['children'].keys())
                for i in range(len(expecting)):
                    if expecting[i].startswith(EXCLUDE):
                        expecting[i] = "everything except '" + expecting[i][len(EXCLUDE):] + "'"
                    elif len(expecting[i]) == 1:
                        expecting[i] = "'" + expecting[i] + "'"
                    else:
                        expecting[i] = "one of {'" + "', '".join(expecting[i]) + "'}"
                expecting = sorted(expecting, key=lambda x: x.startswith("everything except"))
                error_msg += f"expected: {' or '.join(expecting)}"
                error_msg = error_msg.encode("unicode_escape").decode("utf-8")
                error_msg = error_msg.replace("\\\\", "\\")
                print(error_msg)
                token = ""
                state = STARTING_STATE
            
    if token:
        if nodes[state]["terminal"]:
            if token in keywords:
                tokens.append({"token": token, "type": "KEYWORD", "line": line, "start": start, "end": position})
            elif token in special_literals:
                tokens.append({"token": token, "type": "SPECIAL_LITERAL", "line": line, "start": start, "end": position})
            else:
                tokens.append({"token": token, "type": nodes[state]["terminal_type"], "line": line, "start": start, "end": position})

    return tokens

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=NAME,
        description=DESCRIPTION,
        epilog=EPILOG,
    )
    parser.add_argument("filename")
    parser.add_argument("datafile", nargs="?", default="dfa.dat")
    parser.add_argument("-n", "--no-comments", action="store_true", help="remove comments tokens from the output")
    args = parser.parse_args()

    filename = args.filename
    datafile = args.datafile
    no_comments = args.no_comments

    source = read_file(filename)
    with open(datafile, "r") as file:
        data = json.load(file)
        KEYWORDS = data["keywords"]
        SPECIAL_LITERALS = data["special_literals"]
        SEPARATORS = data["separators"]
        TOKEN_TYPES = data["terminal_types"]
        nodes = data["nodes"]

    print("Parsing file: " + filename)
    start = time.time()
    result = lexer(source, nodes, KEYWORDS, SPECIAL_LITERALS, SEPARATORS)
    end = time.time()
    print(f"Done in {end-start:.3f} seconds.")

    
    if no_comments:
        result = [token for token in result if token["type"] != "COMMENT"]

    verbose = "======= The VC compiler ======="
    for token in result:
        verbose += f"\nKind = {TOKEN_TYPES.index(token['type'])} [{token['type']}]"
        verbose += f", spelling = \"{token['token']}\""
        verbose += f", position = {token['line']}({token['start']})..{token['line']}({token['end']})"

    output = ""
    for token in result:
        output += token["token"]
        output += "\n"

    verbose_filename = filename.split(".")[0] + ".verbose.vctok"
    with open(verbose_filename, "w+") as file:
        file.write(verbose)

    output_filename = filename.split(".")[0] + ".vctok"
    with open(output_filename, "w+") as file:
        file.write(output)

    print("Exported tokens to: " + output_filename)
    print("Exported verbose tokens to: " + verbose_filename)
