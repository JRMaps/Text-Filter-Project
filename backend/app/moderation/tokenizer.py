import re
from backend.app.moderation.normalizationV1 import normalization

TOKEN_OFFENSIVE = "OFFENSIVE"
TOKEN_PRONOUN   = "PRONOUN"
TOKEN_LINK      = "LINK"    
TOKEN_WORD      = "WORD"
TOKEN_UNKNOWN   = "UNKNOWN"

OFFENSIVE_ROOTS = {
    "puta", "putang", "ina",
    "gago", "bobo", "tanga", "yawa",
    "pakshet", "leche", "tarantado",
    "chupa", "puki", "puke", "ulol",
    "putangina"
}

PRONOUNS = {
    "ka", "mo", "kayo", "siya", "niya",
    "nila", "namin", "ninyo", "tayo", "ikaw"
}

# ✅ NEW (minimal)
LINK_WORDS = {"ay"}

# ✅ Extend vocab for recursive splitter
VOCAB = OFFENSIVE_ROOTS | PRONOUNS | LINK_WORDS

WORD_PATTERN = re.compile(r'^[a-z]+$')


# 🔹 Recursive splitter (unchanged)
def split_lexeme(text):
    results = []

    def backtrack(pos, path):
        if pos == len(text):
            results.append(path)
            return

        for word in sorted(VOCAB, key=len, reverse=True):
            if text.startswith(word, pos):
                backtrack(pos + len(word), path + [word])

    backtrack(0, [])
    return results


def tokenize(text):
    tokens = []
    normalized = normalization(text)
    lexemes = normalized.split()

    for lex in lexemes:
        # direct match
        if lex in OFFENSIVE_ROOTS:
            tokens.append((TOKEN_OFFENSIVE, lex))

        elif lex in PRONOUNS:
            tokens.append((TOKEN_PRONOUN, lex))

        elif lex in LINK_WORDS:           
            tokens.append((TOKEN_LINK, lex))

        elif WORD_PATTERN.fullmatch(lex):
            splits = split_lexeme(lex)
            if splits:
                # greedy first split
                for part in splits[0]:
                    if part in OFFENSIVE_ROOTS:
                        tokens.append((TOKEN_OFFENSIVE, part))
                    elif part in PRONOUNS:
                        tokens.append((TOKEN_PRONOUN, part))
                    elif part in LINK_WORDS:
                        tokens.append((TOKEN_LINK, part))
            else:
                tokens.append((TOKEN_WORD, lex))
        else:
            tokens.append((TOKEN_UNKNOWN, lex))

    return tokens

