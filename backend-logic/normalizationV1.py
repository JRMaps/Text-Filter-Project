import re
import unicodedata

VARIANCE = {'1':'i','3':'e','4':'a','0':'o','@':'a','$':'s','()':'o','5':'s'}


def replacing(text: str) -> str: #funct to replace chars based on VARIANCE dict
    for key in sorted(VARIANCE.keys(), key=len, reverse=True):
        text = text.replace(key, VARIANCE[key])
    return text

def remove_accents(text: str) -> str: #funct to remove accents from chars
    # Normalize to NFD form (decomposed unicode)
    nfkd_form = unicodedata.normalize('NFD', text)
    # Remove combining marks (accents)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalization(text: str) -> str: #main funct to normalize text
    lower = text.lower()
    replaced = replacing(lower)
    noAccents = remove_accents(replaced)
    noNum = re.sub(r'\d+','', noAccents)
    noPunct = re.sub(r'[^\w\s]','', noNum)
    noExtraSpaces = re.sub(r'\s+',' ', noPunct)
    return noExtraSpaces.strip()


string = "H3ll0, Wörld! Th1s 1s @ t3st str1ng w1th s0me nümber5 & punctu@t10n. put@ng 1n@ m0"
normalized_string = normalization(string)
print(normalized_string)  # Output: "hello world this is a test string with some numbers punctuation