class LexicalAnalyzer:
    def __init__(self):
        self.keywords = {'auto', 'int', 'float', 'return'}
        
    def analyze(self, text: str):
        lexemes = []
        errors = []
        
        row = 1
        col = 1
        
        state = 'START'
        buffer = ''
        start_col = 1
        
        i = 0
        text_len = len(text)
        
        while i < text_len:
            char = text[i]
            
            if state == 'START':
                buffer = ''
                start_col = col
                
                if char.isspace():
                    state = 'SPACE'
                    buffer += char
                elif char.isalpha() or char == '_':
                    state = 'IDENTIFIER'
                    buffer += char
                elif char.isdigit():
                    state = 'NUMBER'
                    buffer += char
                elif char == '+':
                    state = 'PLUS'
                    buffer += char
                elif char == '-':
                    state = 'MINUS'
                    buffer += char
                elif char == '*':
                    state = 'MULTIPLY'
                    buffer += char
                elif char == '/':
                    state = 'DIVIDE'
                    buffer += char
                elif char == '=':
                    state = 'ASSIGN'
                    buffer += char
                elif char == '[':
                    lexemes.append({'code': 5, 'type': 'Спецсимвол', 'lexeme': char, 'row': row, 'start_col': start_col, 'end_col': start_col})
                elif char == ']':
                    lexemes.append({'code': 6, 'type': 'Спецсимвол', 'lexeme': char, 'row': row, 'start_col': start_col, 'end_col': start_col})
                elif char == '(':
                    lexemes.append({'code': 7, 'type': 'Спецсимвол', 'lexeme': char, 'row': row, 'start_col': start_col, 'end_col': start_col})
                elif char == ')':
                    lexemes.append({'code': 8, 'type': 'Спецсимвол', 'lexeme': char, 'row': row, 'start_col': start_col, 'end_col': start_col})
                elif char == '{':
                    lexemes.append({'code': 9, 'type': 'Спецсимвол', 'lexeme': char, 'row': row, 'start_col': start_col, 'end_col': start_col})
                elif char == '}':
                    lexemes.append({'code': 10, 'type': 'Спецсимвол', 'lexeme': char, 'row': row, 'start_col': start_col, 'end_col': start_col})
                elif char == ',':
                    lexemes.append({'code': 11, 'type': 'Спецсимвол', 'lexeme': char, 'row': row, 'start_col': start_col, 'end_col': start_col})
                elif char == ';':
                    lexemes.append({'code': 12, 'type': 'Спецсимвол', 'lexeme': char, 'row': row, 'start_col': start_col, 'end_col': start_col})
                else:
                    state = 'ERROR'
                    buffer += char
                
                if state == 'START':
                    pass

            elif state == 'SPACE':
                if char.isspace():
                    buffer += char
                else:
                    lexemes.append({'code': 13, 'type': 'Разделитель', 'lexeme': buffer.replace('\n', '\\n').replace('\t', '\\t'), 'row': row, 'start_col': start_col, 'end_col': col - 1})
                    state = 'START'
                    i -= 1
                    col -= 1

            elif state == 'IDENTIFIER':
                if char.isalnum() or char == '_':
                    buffer += char
                else:
                    if buffer in self.keywords:
                        code = 3
                        l_type = 'Ключевое слово'
                    else:
                        code = 2
                        l_type = 'Идентификатор'
                    lexemes.append({'code': code, 'type': l_type, 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': col - 1})
                    state = 'START'
                    i -= 1
                    col -= 1

            elif state == 'NUMBER':
                if char.isdigit():
                    buffer += char
                else:
                    lexemes.append({'code': 1, 'type': 'Целое без знака', 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': col - 1})
                    state = 'START'
                    i -= 1
                    col -= 1

            elif state == 'PLUS':
                lexemes.append({'code': 4, 'type': 'Оператор', 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': start_col})
                state = 'START'
                i -= 1
                col -= 1
                
            elif state == 'MINUS':
                lexemes.append({'code': 4, 'type': 'Оператор', 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': start_col})
                state = 'START'
                i -= 1
                col -= 1

            elif state == 'MULTIPLY':
                lexemes.append({'code': 4, 'type': 'Оператор', 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': start_col})
                state = 'START'
                i -= 1
                col -= 1

            elif state == 'DIVIDE':
                lexemes.append({'code': 4, 'type': 'Оператор', 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': start_col})
                state = 'START'
                i -= 1
                col -= 1
                
            elif state == 'ASSIGN':
                lexemes.append({'code': 4, 'type': 'Оператор', 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': start_col})
                state = 'START'
                i -= 1
                col -= 1

            elif state == 'ERROR':
                errors.append({'code': 99, 'type': 'Недопустимый символ', 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': start_col, 'message': f"Недопустимый символ '{buffer}'"})
                lexemes.append({'code': 99, 'type': 'Недопустимый символ', 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': start_col})
                state = 'START'

            if char == '\n':
                if state != 'SPACE':
                    row += 1
                    col = 0
                else:
                    pass 
            
            if char == '\n' and state == 'SPACE':
                row += 1
                col = 0
            
            i += 1
            col += 1

        if state == 'SPACE':
             lexemes.append({'code': 13, 'type': 'Разделитель', 'lexeme': buffer.replace('\n', '\\n').replace('\t', '\\t'), 'row': row, 'start_col': start_col, 'end_col': col - 1})
        elif state == 'IDENTIFIER':
            if buffer in self.keywords:
                code = 3
                l_type = 'Ключевое слово'
            else:
                code = 2
                l_type = 'Идентификатор'
            lexemes.append({'code': code, 'type': l_type, 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': col - 1})
        elif state == 'NUMBER':
            lexemes.append({'code': 1, 'type': 'Целое без знака', 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': col - 1})
        elif state in ('PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'ASSIGN'):
            lexemes.append({'code': 4, 'type': 'Оператор', 'lexeme': buffer, 'row': row, 'start_col': start_col, 'end_col': start_col})

        return lexemes, errors
