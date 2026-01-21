from backend.app.moderation.parser import Parser
from datetime import datetime

class Ranker:
    def __init__(self, tokens, muted_words=None):
        self.tokens = tokens
        self.parser = Parser(tokens)
        self.has_offensive, self.offensive_spans = self.parser.parse()
        self.muted_words = muted_words or {}

    def calculate_severity(self):  # returns severity level as int
        """
        Severity levels:
        0 = NONE
        1 = LOW
        2 = MEDIUM
        3 = HIGH
        """

        if not self.has_offensive:
            return 0  # no offensive content

        severity_levels = []
        offensive_count = 0

        for span in self.offensive_spans:
            # span format: (start, end, type, offensive_word)
            offensive_type = span[2]
            offensive_count += 1

            if offensive_type == "single_offensive":
                severity_levels.append(1)   # LOW
            elif offensive_type == "repeated_offensive":
                severity_levels.append(2)   # MEDIUM
            elif offensive_type == "offensive+pronoun":
                severity_levels.append(3)   # HIGH

        # Adjust logic for multiple offensive roots without pronouns
        if offensive_count > 1 and all(span[2] == "single_offensive" for span in self.offensive_spans):
            severity_levels.append(2)  # Escalate to MEDIUM instead of HIGH

        # Multiple offensive expressions with pronouns → escalate to HIGH
        if any(span[2] == "offensive+pronoun" for span in self.offensive_spans):
            severity_levels.append(3)

        return max(severity_levels) if severity_levels else 0

    def get_action(self, severity):
        """
        Map severity to moderation action
        """
        actions = {
            0: "ALLOWED",  
            1: "MASKED",
            2: "FLAGGED",
            3: "BLOCKED"
        }
        return actions.get(severity, "ALLOWED")

    def rank_message(self):
        severity = self.calculate_severity()
        action = self.get_action(severity)

        return {
            "severity_level": severity,
            "severity_label": self._severity_label(severity),
            "action": action,
            "offensive_spans": self.offensive_spans
        }

    def _severity_label(self, severity):
        labels = {
            0: "NONE",
            1: "LOW",
            2: "MEDIUM",
            3: "HIGH"
        }
        return labels.get(severity, "NONE")

    def is_word_muted(self, word):
        """
        Check if a word is temporarily muted.
        """
        if word in self.muted_words:
            mute_expiry = self.muted_words[word]
            if datetime.utcnow() < mute_expiry:
                return True
        return False
