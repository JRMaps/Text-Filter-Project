import re
from normalizationV1 import normalization

TOKEN_OFFENSIVE = "OFFENSIVE"
TOKEN_PRONOUN = "PRONOUN"
TOKEN_WORD = "WORD"
TOKEN_UNKNOWN = "UNKNOWN"
#help breakdown offensive words in Filipino language
OFFENSIVE_ROOT = r'(puta|gago|bobo|tanga|yawa|pakshet|leche|tarantado|chupa|puki|puke)'
PREFIX = r'(pinag|pag|mag|ma|na|pa)?'
SUFFIX = r'(han|hin|an|ng)?'

OFFENSIVE_PATTERN = re.compile(
    rf'^{PREFIX}{OFFENSIVE_ROOT}{SUFFIX}$',
    re.IGNORECASE
)

WORD_PATTERN = re.compile(r'^[a-z]+$')

PRONOUNS = {   #added pronoun token for Filipino language
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
