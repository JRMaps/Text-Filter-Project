from parser import Parser

class Ranker:
    def __init__(self, tokens):
        self.tokens = tokens
        self.parser = Parser(tokens)
        self.has_offensive, self.offensive_spans = self.parser.parse()

    def calculate_severity(self): # returns severity level as int
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

        for span in self.offensive_spans:
            # span format: (start, end, type)
            offensive_type = span[2]

            if offensive_type == "single":
                severity_levels.append(1)   # LOW
            elif offensive_type == "repeated":
                severity_levels.append(2)   # MEDIUM
            elif offensive_type == "pronoun":
                severity_levels.append(3)   # HIGH

        # Multiple offensive expressions → escalate to HIGH
        if len(self.offensive_spans) > 1:
            severity_levels.append(3)

        return max(severity_levels) if severity_levels else 0

    def get_action(self, severity):
        """
        Map severity to moderation action
        """
        actions = {
            0: "allowed",
            1: "masked",     # e.g., ****
            2: "flagged",    # review
            3: "blocked"     # reject message
        }
        return actions.get(severity, "allowed")

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
