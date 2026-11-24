# ========================================
# LEXICAL ANALYZER
# Converts a raw input string into tokens.
# Whitespace is optional: "a b # d" and "ab#d" give the same tokens.
# ========================================

TERMINALS = {"a", "b", "c", "d", "#", "@"}


class LexicalError(Exception):
    pass


def lexer(source):
    """Scan the source string left to right and return a list of tokens.
    Each token is (type, lexeme, position). The token type is the
    terminal symbol itself, which is what the parsing table uses."""
    tokens = []
    i = 0
    while i < len(source):
        ch = source[i]
        if ch.isspace():          # skip whitespace
            i += 1
        elif ch in TERMINALS:     # recognized terminal
            tokens.append((ch, ch, i))
            i += 1
        else:                     # anything else is a lexical error
            raise LexicalError(f"invalid character {ch!r} at position {i}")
    return tokens


# ========================================
# PART A: GRAMMAR-SPECIFIC CONFIGURATION
#   X  -> U X'
#   X' -> # U X' | @ U X' | epsilon
#   U  -> a U' | d
#   U' -> b | c
# ========================================

START = "X"

NONTERMINALS = {"X", "X'", "U", "U'"}

# (Nonterminal, Lookahead) -> RHS. Empty tuple () is epsilon.
TABLE = {
    ("X", "a"): ("U", "X'"),
    ("X", "d"): ("U", "X'"),

    ("X'", "#"): ("#", "U", "X'"),
    ("X'", "@"): ("@", "U", "X'"),
    ("X'", "$"): (),

    ("U", "a"): ("a", "U'"),
    ("U", "d"): ("d",),

    ("U'", "b"): ("b",),
    ("U'", "c"): ("c",),
}


# ========================================
# PART B: GENERIC LL(1) PARSER
# ========================================

def parse(tokens, start, nonterminals, table):
    tokens = list(tokens) + ["$"]
    stack = ["$", start]
    pos = 0

    print(f"{'PARSING STACK':<25} {'REMAINING INPUT':<25} PARSER ACTION")
    print("-" * 80)

    while stack:
        top = stack[-1]
        lookahead = tokens[pos]

        stack_text = " ".join(stack)
        input_text = " ".join(tokens[pos:])

        # ACCEPT
        if top == "$" and lookahead == "$":
            print(f"{stack_text:<25} {input_text:<25} ACCEPT")
            return True

        # PREDICT: top is a nonterminal
        if top in nonterminals:
            rhs = table.get((top, lookahead))
            if rhs is None:
                action = f"ERROR: no M[{top}, {lookahead}]"
                print(f"{stack_text:<25} {input_text:<25} {action}")
                return False

            stack.pop()
            stack.extend(reversed(rhs))   # epsilon pushes nothing

            production = " ".join(rhs) if rhs else "epsilon"
            action = f"Predict {top} -> {production}"

        # MATCH: top is a terminal
        elif top == lookahead:
            stack.pop()
            pos += 1
            action = f"Match {top}"

        # ERROR: terminal mismatch
        else:
            action = f"ERROR: expected {top}, found {lookahead}"
            print(f"{stack_text:<25} {input_text:<25} {action}")
            return False

        print(f"{stack_text:<25} {input_text:<25} {action}")

    return False


# ========================================
# PART C: TEST THE PARSER
# ========================================

test_inputs = [
    ("Assigned input (valid)", "a b # d @ a c"),
    ("Additional valid",       "d # a b @ d"),
    ("Invalid",                "a # d"),   # U' sees '#', M[U', #] is empty
]

for label, source in test_inputs:
    print(f"\n=== {label} ===")
    print("Input:", source)
    try:
        token_list = lexer(source)
        print("Tokens:", [t[0] for t in token_list])
        result = parse([t[0] for t in token_list], START, NONTERMINALS, TABLE)
    except LexicalError as e:
        print("Lexical error:", e)
        result = False
    print("Result:", "ACCEPTED" if result else "REJECTED")
