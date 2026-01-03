from tokenizer import tokenize
class Parser:
    def __init__(self, tokens): # Initialize with a list of tokens
        self.tokens = tokens
        self.pos = 0
        self.offensive_spans = [] # List to hold spans of offensive sequences

    def current(self): # Get the current token
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, token_type): # Match and consume a token of a specific type
        if self.current() and self.current()[0] == token_type:
            token = self.current()
            self.pos += 1
            return token
        return None

    def parse(self): # Main parse function to find offensive sequences
        while self.pos < len(self.tokens):
            start = self.pos
            if self.O():
                self.offensive_spans.append((start, self.pos))
            else:
                self.pos += 1  # move forward if no match
        return len(self.offensive_spans) > 0, self.offensive_spans

    # Grammar Rules
    def O(self):
        return (
            self.single_offensive() or
            self.repeated_offensive() or
            self.offensive_pronoun()
        )

    def single_offensive(self): # Match a single offensive token
        return self.match("OFFENSIVE") is not None

    def repeated_offensive(self): # Match two consecutive offensive tokens
        start = self.pos
        if self.match("OFFENSIVE") and self.match("OFFENSIVE"):
            return True
        self.pos = start
        return False

    def offensive_pronoun(self): # Match an offensive token followed by a pronoun
        start = self.pos
        if self.match("OFFENSIVE") and self.match("PRONOUN"):
            return True
        self.pos = start
        return False
