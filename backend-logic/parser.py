from tokenizer import tokenize

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.offensive_spans = []

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, token_type):
        if self.current() and self.current()[0] == token_type:
            token = self.current()
            self.pos += 1
            return token
        return None

    def parse(self):
        start_pos = self.pos
        if self.S():
            return True, self.offensive_spans
        self.pos = start_pos
        return False, []

    def S(self):
        start = self.pos
        if self.O():
            self.offensive_spans.append((start, self.pos))
            return True

        self.pos = start
        if self.O() and self.O():
            return True

        self.pos = start
        return False

    def O(self):
        return (
            self.B() or
            self.A() or
            self.R() or
            self.C()
        )

    def B(self):
        return self.match('OFFENSIVE') is not None

    def A(self):
        return self.match('OFFENSIVE') is not None

    def R(self):
        start = self.pos
        if self.match('OFFENSIVE') and self.match('OFFENSIVE'):
            return True
        self.pos = start
        return False

    def C(self):
        start = self.pos
        if self.match('OFFENSIVE') and self.match('PRONOUN'):
            return True
        self.pos = start
        return False
