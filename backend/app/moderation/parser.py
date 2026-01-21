class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.offensive_spans = []

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def match(self, token_type):
        if self.current() and self.current()[0] == token_type:
            tok = self.current()
            self.pos += 1
            return tok
        return None

    def parse(self):
        while self.pos < len(self.tokens):
            start = self.pos
            kind = self.O()
            if kind:
                # Instead of combining words, add each offensive word as a separate span
                for i in range(start, self.pos):
                    offensive_word = self.tokens[i][1]
                    self.offensive_spans.append((i, i + 1, kind, offensive_word))
            else:
                self.pos += 1
        return bool(self.offensive_spans), self.offensive_spans

    # O → OFFENSIVE PRONOUN | OFFENSIVE OFFENSIVE | OFFENSIVE
    def O(self):
        start = self.pos

        if self.offensive_pronoun():
            return "offensive+pronoun"

        self.pos = start
        if self.repeated_offensive():
            return "repeated_offensive"

        self.pos = start
        if self.single_offensive():
            return "single_offensive"

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