import re
from backend.app.moderation.normalizationV1 import normalization

TOKEN_OFFENSIVE = "OFFENSIVE"
TOKEN_PRONOUN   = "PRONOUN"
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

VOCAB = OFFENSIVE_ROOTS | PRONOUNS

WORD_PATTERN = re.compile(r'^[a-z]+$')


# 🔹 Recursive splitter
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
        elif WORD_PATTERN.fullmatch(lex):
            # try recursive split
            splits = split_lexeme(lex)
            if splits:
                # take the first valid split (greedy)
                for part in splits[0]:
                    if part in OFFENSIVE_ROOTS:
                        tokens.append((TOKEN_OFFENSIVE, part))
                    elif part in PRONOUNS:
                        tokens.append((TOKEN_PRONOUN, part))
            else:
                tokens.append((TOKEN_WORD, lex))
        else:
            tokens.append((TOKEN_UNKNOWN, lex))

    return tokens


