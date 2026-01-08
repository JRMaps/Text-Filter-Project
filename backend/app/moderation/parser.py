class Parser: # A simple recursive descent parser for offensive content
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.offensive_spans = []

    def current(self): # returns current token or None
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, token_type): # returns token if matches, else None
        if self.current() and self.current()[0] == token_type:
            token = self.current()
            self.pos += 1
            return token
        return None

    def parse(self): # returns (accepted: bool, offensive_spans: list)
        while self.pos < len(self.tokens):
            start = self.pos
            offensive_type = self.O()
            if offensive_type:
                self.offensive_spans.append((start, self.pos, offensive_type))
            else:
                self.pos += 1
        return len(self.offensive_spans) > 0, self.offensive_spans

    # Grammar Rules: O → OFFENSIVE PRONOUN | OFFENSIVE OFFENSIVE | OFFENSIVE
    def O(self):
        start = self.pos

        if self.offensive_pronoun():
            return "pronoun"

        self.pos = start
        if self.repeated_offensive():
            return "repeated"

        self.pos = start
        if self.single_offensive():
            return "single"

        self.pos = start
        return None

    def single_offensive(self):
        return self.match("OFFENSIVE") is not None

    def repeated_offensive(self):
        start = self.pos
        if self.match("OFFENSIVE") and self.match("OFFENSIVE"):
            return True
        self.pos = start
        return False

    def offensive_pronoun(self):
        start = self.pos
        if self.match("OFFENSIVE") and self.match("PRONOUN"):
            return True
        self.pos = start
        return False
