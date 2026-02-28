import re
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("blue"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            'int', 'float', 'void', 'char', 'bool',
            'if', 'else', 'while', 'for', 'return',
            'switch', 'case', 'break', 'continue',
            'true', 'false', 'struct', 'class'
        ]
        for word in keywords:
            pattern = re.compile(rf'\b{word}\b')
            self._highlighting_rules.append((pattern, keyword_format))

        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("red"))
        operator_format.setFontWeight(QFont.Weight.Bold)
        operators = [
            r'\+', r'-', r'\*', r'/', r'%', r'=', r'==', r'!=',
            r'<', r'>', r'<=', r'>=', r'&&', r'\|\|', r'!'
        ]
        for op in operators:
            pattern = re.compile(op)
            self._highlighting_rules.append((pattern, operator_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("purple"))
        
        pattern = re.compile(r'\b\d+\.?\d*|\.\d+\b')
        self._highlighting_rules.append((pattern, number_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("gray"))
        comment_format.setFontItalic(True)
        self._highlighting_rules.append((re.compile(r'//[^\n]*'), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self._highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)
