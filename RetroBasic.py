import sys

id = set([chr(e) for e in range(ord('A'), ord('Z')+1)])
line_num = set([str(i) for i in range(1, 1001)])
const = set([str(i) for i in range(0, 101)])
terminal = set(["+", "-", "IF", "<", "=", "PRINT", "GOTO", "STOP", "EOF"])
bcode_type = {
    "#line": 10,
    "#id": 11,
    "#const": 12,
    "#if": 13,
    "#goto": 14,
    "#print": 15,
    "#stop": 16,
    "#op": 17,
}
parsing_table = {
    "pgm": {"line_num": ["line", "pgm"], "EOF": ["EOF"]},
    "line": {"line_num": ["line_num", "stmt"]},
    "stmt": {"id": ["asgmnt"], "IF": ["if"], "PRINT": ["print"], "GOTO": ["goto"], "STOP": ["stop"]},
    "asgmnt": {"id": ["id", "=", "exp"]},
    "exp": {"id": ["term", "exp'"], "const": ["term", "exp'"]},
    "exp'": {"EOF": None, "line_num": None, "+": ["+", "term"], "-": ["-", "term"]},
    "term": {"id": ["id"], "const": ["const"]},
    "if": {"IF": ["IF", "cond", "line_num"]},
    "cond": {"id": ["term", "cond'"], "const": ["term", "cond'"]},
    "cond'": {"<": ["<", "term"], "=": ["=", "term"]},
    "print": {"PRINT": ["PRINT", "id"]},
    "goto": {"GOTO": ["GOTO", "line_num"]},
    "stop": {"STOP": ["STOP"]},
}
stack = ["EOF"]


def get_terminal_type(token):
    if token.isdigit():
        return "num"
    if token in id:
        return "id"
    if token in terminal:
        return token
    raise Exception('Wrong Input Grammar')


def match_terminal(token, top_stack):
    terminal_type = get_terminal_type(token)
    if terminal_type != "num":
        return terminal_type == top_stack
    else:
        return top_stack == "line_num" or top_stack == "const"


def get_rule(stack_top, token):
    terminal_type = get_terminal_type(token)
    if terminal_type != "num" and terminal_type in parsing_table[stack_top]:
        return parsing_table[stack_top][terminal_type]
    if "line_num" in parsing_table[stack_top]:
        return parsing_table[stack_top]["line_num"]
    if "const" in parsing_table[stack_top]:
        return parsing_table[stack_top]["const"]
    raise Exception("Wrong Grammar")


def parse(token):
    while not match_terminal(token, stack[-1]):
        stack_top = stack.pop()
        if stack_top not in parsing_table:
            raise Exception("Wrong Grammar")
        rule = get_rule(stack_top, token)
        if rule != None:
            stack.extend(rule[::-1])
    if(stack[-1] == 'line_num' and not 1 <= int(token) <= 1000):
        raise Exception("Wrong Grammar")
    if(stack[-1] == 'const' and not 0 <= int(token) <= 100):
        raise Exception("Wrong Grammar")
    return stack.pop()


def get_bcode(terminal_symbol, value):
    if(terminal_symbol == "line_num"):
        return ("#line", int(value))
    if(terminal_symbol == "id"):
        return ("#id", ord(value) - ord('A') + 1)
    if(terminal_symbol == "const"):
        return ("#const", int(value))
    if(terminal_symbol == "IF"):
        return ("#if", 0)
    if(terminal_symbol == "GOTO"):
        return ("#goto", int(value))
    if(terminal_symbol == "PRINT"):
        return ("#print", 0)
    if(terminal_symbol == "STOP"):
        return ("#stop", 0)
    if(terminal_symbol == "+"):
        return ("#op", 1)
    if(terminal_symbol == "-"):
        return ("#op", 2)
    if(terminal_symbol == "<"):
        return ("#op", 3)
    if(terminal_symbol == "="):
        return ("#op", 4)


def gen_bcode(parsed_list):
    bcode_list = []
    for i in range(len(parsed_list)):
        if(parsed_list[i][0] not in ["GOTO", "line_num"] or i == 0):
            bcode_list.append(get_bcode(parsed_list[i][0], parsed_list[i][1]))
        else:
            if(parsed_list[i][0] == 'line_num' and i != 0):
                bcode_list.append(get_bcode("GOTO", parsed_list[i][1]))
    return bcode_list


def to_bcode(tokens):
    parsed_list = []
    for token in tokens:
        parsed_list.append((parse(token), token))
    bcode_list = gen_bcode(parsed_list)
    bcode_string = ''
    for types, value in bcode_list:
        bcode_string = bcode_string + \
            str(bcode_type[types]) + ' ' + str(value) + ' '
    return bcode_string.strip()


file_name = str(sys.argv[1])
file = open(file_name, 'r')
outfile = open('output_gen'+'.txt', 'w')
for line_count, line in enumerate(file):
    if line_count == 0:
        stack.append("pgm")
    tokens = line.strip().split()
    bcode = to_bcode(tokens)
    print(bcode)
    outfile.write(bcode+'\n')
outfile.write('0\n')
file.close()
outfile.close()
