import re
from normalizationV1 import normalization

# Token types to be used in parsing

TOKEN_OFFENSIVE = "OFFENSIVE"
TOKEN_PRONOUN = "PRONOUN"
TOKEN_WORD = "WORD"
TOKEN_UNKNOWN = "UNKNOWN"

# Base offensive roots 
OFFENSIVE_ROOTS = {
    "puta", "gago", "bobo", "tanga", "yawa",
    "pakshet", "leche", "tarantado",
    "chupa", "puki", "puke"
}

# Prefixes (Extandable)
PREFIXES = {
    "pinag", "pag", "mag", "ma", "na", "pa"
}

# Suffixes (Extendable)
SUFFIXES = {
    "han", "hin", "an", "ng"
}

# Build regex dynamically
PREFIX_PATTERN = r'(' + '|'.join(PREFIXES) + r')?'
ROOT_PATTERN = r'(' + '|'.join(OFFENSIVE_ROOTS) + r')'
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


def tokenize(text: str):
    tokens = []
    normalized_text = normalization(text)
    lexemes = normalized_text.split()

    for lexeme in lexemes:
        if OFFENSIVE_PATTERN.fullmatch(lexeme):
            tokens.append((TOKEN_OFFENSIVE, lexeme))
        elif lexeme in PRONOUNS:
            tokens.append((TOKEN_PRONOUN, lexeme))
        elif WORD_PATTERN.fullmatch(lexeme):
            tokens.append((TOKEN_WORD, lexeme))
        else:
            tokens.append((TOKEN_UNKNOWN, lexeme))

    return tokens
