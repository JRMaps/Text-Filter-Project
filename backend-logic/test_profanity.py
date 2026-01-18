from tokenizer import tokenize
from parser import Parser

def run_test(text):
    tokens = tokenize(text)
    parser = Parser(tokens)
    accepted, spans = parser.parse()

    print("=" * 50)
    print("INPUT:", text)
    print("TOKENS:", tokens)
    print("ACCEPTED:", accepted)
    print("SPANS:", spans)


tests = [
    # basic
    "gago",
    "gago ka",
    "bobo gago",

    # combined
    "gagoka",
    "putangina",
    "putanginamo",

    # obfuscated
    "put@ng 1n@ m0",
    "g@go k@",

    # mixed sentence
    "ikaw ay isang putanginamo talaga",

    # non-offensive (should fail)
    "maganda ka",
    "putahe",
    "tangina sauce",

    # repetition
    "gagobobo",
]

for t in tests:
    run_test(t)
