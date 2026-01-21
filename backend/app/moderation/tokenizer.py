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
    "chupa", "puki", "puke"
}

PREFIXES = {"pinag", "pag", "mag", "ma", "na", "pa"}
SUFFIXES = {"han", "hin", "an", "ng"}

PREFIX_PATTERN = r'(' + '|'.join(PREFIXES) + r')?'
ROOT_PATTERN   = r'(' + '|'.join(OFFENSIVE_ROOTS) + r')'
SUFFIX_PATTERN = r'(' + '|'.join(SUFFIXES) + r')?'

OFFENSIVE_PATTERN = re.compile(
    rf'^{PREFIX_PATTERN}{ROOT_PATTERN}{SUFFIX_PATTERN}$',
    re.IGNORECASE
)

WORD_PATTERN = re.compile(r'^[a-z]+$')

PRONOUNS = {
    "ka", "mo", "kayo", "siya", "niya",
    "nila", "namin", "ninyo", "tayo", "ikaw"
}

VOCAB = OFFENSIVE_ROOTS | PRONOUNS


# 🔁 Recursive splitter
def split_recursively(text, pos=0, path=None, results=None):
    if path is None:
        path = []
    if results is None:
        results = []

    if pos == len(text):
        results.append(path)
        return results

    for word in sorted(VOCAB, key=len, reverse=True):
        if text.startswith(word, pos):
            split_recursively(
                text,
                pos + len(word),
                path + [word],
                results
            )

    return results


def tokenize(text: str):
    tokens = []
    normalized_text = normalization(text)
    lexemes = normalized_text.split()

    for lexeme in lexemes:
        # 1️⃣ direct offensive match
        if OFFENSIVE_PATTERN.fullmatch(lexeme):
            tokens.append((TOKEN_OFFENSIVE, lexeme))
            continue

        # 2️⃣ pronoun
        if lexeme in PRONOUNS:
            tokens.append((TOKEN_PRONOUN, lexeme))
            continue

        # 3️⃣ recursive split attempt
        if WORD_PATTERN.fullmatch(lexeme):
            splits = split_recursively(lexeme)

            if splits:
                # choose longest valid split (best signal)
                best = max(splits, key=len)

                for part in best:
                    if part in OFFENSIVE_ROOTS:
                        tokens.append((TOKEN_OFFENSIVE, part))
                    elif part in PRONOUNS:
                        tokens.append((TOKEN_PRONOUN, part))
                continue

            tokens.append((TOKEN_WORD, lexeme))
            continue

        # 4️⃣ fallback
        tokens.append((TOKEN_UNKNOWN, lexeme))

    return tokens

