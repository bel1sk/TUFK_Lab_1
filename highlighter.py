import re
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt

class SyntaxHighlighter(QSyntaxHighlighter):
    """
    Basic syntax highlighter for the compiler project.
    Highlights keywords like int, float, if, else, while, return, etc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlighting_rules = []

        # Keyword Format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("darkBlue"))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        keywords = [
            'int', 'float', 'void', 'char', 'bool',
            'if', 'else', 'while', 'for', 'return',
            'switch', 'case', 'break', 'continue',
            'true', 'false', 'struct', 'class'
        ]

        # Use word boundaries \b to match exact words
        for word in keywords:
            pattern = re.compile(f'\\b{word}\\b')
            self._highlighting_rules.append((pattern, keyword_format))

        # Comment Format (Single line //)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("darkGreen"))
        comment_format.setFontItalic(True)
        self._highlighting_rules.append((re.compile('//[^\n]*'), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self._highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)
