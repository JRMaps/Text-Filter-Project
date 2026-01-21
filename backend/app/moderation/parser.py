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
                # Store each offensive token with its span
                for i in range(start, self.pos):
                    offensive_word = self.tokens[i][1]
                    self.offensive_spans.append((i, i + 1, kind, offensive_word))
            else:
                self.pos += 1
        return bool(self.offensive_spans), self.offensive_spans

    # ---------------- O RULE ----------------
    # O → OFFENSIVE PRONOUN | OFFENSIVE OFFENSIVE | OFFENSIVE
    #   | PRONOUN OFFENSIVE | PRONOUN LINK OFFENSIVE
    def O(self):
        start = self.pos

        # 1️⃣ PRONOUN LINK OFFENSIVE
        if self.pronoun_link_offensive():
            return "PRONOUN LINK OFFENSIVE"

        self.pos = start
        # 2️⃣ PRONOUN OFFENSIVE
        if self.pronoun_offensive():
            return "PRONOUN OFFENSIVE"

        self.pos = start
        # 3️⃣ OFFENSIVE PRONOUN
        if self.offensive_pronoun():
            return "OFFENSIVE PRONOUN"

        self.pos = start
        # 4️⃣ OFFENSIVE OFFENSIVE
        if self.repeated_offensive():
            return "OFFENSIVE OFFENSIVE"

        self.pos = start
        # 5️⃣ single OFFENSIVE
        if self.single_offensive():
            return "OFFENSIVE"

        self.pos = start
        return None

    # ---------------- HELPER RULES ----------------
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

    def pronoun_offensive(self):
        start = self.pos
        if self.match("PRONOUN") and self.match("OFFENSIVE"):
            return True
        self.pos = start
        return False

    def pronoun_link_offensive(self):
        start = self.pos
        if self.match("PRONOUN") and self.match("LINK") and self.match("OFFENSIVE"):
            return True
        self.pos = start
        return False
