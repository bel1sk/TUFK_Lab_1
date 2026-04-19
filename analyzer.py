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

class SyntaxAnalyzer:
    def __init__(self, lexemes):
        self.lexemes = [l for l in lexemes if l['code'] != 13 and l['code'] != 99]
        self.pos = 0
        self.errors = []
        
    def current(self):
        if self.pos < len(self.lexemes):
            return self.lexemes[self.pos]
        return None

    def advance(self):
        self.pos += 1

    def match(self, expected_lexeme, sync_set):
        curr = self.current()
        if curr and curr['lexeme'] == expected_lexeme:
            self.advance()
            return True
        else:
            self.report_error(f"Ожидалось '{expected_lexeme}'", curr)
            self.neutralize(sync_set)
            return False

    def match_type(self, expected_type, sync_set):
        curr = self.current()
        if curr and curr['type'] == expected_type:
            self.advance()
            return True
        else:
            self.report_error(f"Ожидался тип лексемы '{expected_type}'", curr)
            self.neutralize(sync_set)
            return False

    def report_error(self, message, lexeme):
        if lexeme:
            self.errors.append({
                "lexeme": lexeme['lexeme'],
                "row": lexeme['row'],
                "col": lexeme['start_col'],
                "message": message
            })
        else:
            self.errors.append({
                "lexeme": "EOF",
                "row": "-",
                "col": "-",
                "message": message
            })

    def neutralize(self, sync_set):
        while self.current():
            curr = self.current()
            if curr['lexeme'] in sync_set or curr['type'] in sync_set:
                return
            self.advance()

    def parse(self):
        if not self.lexemes:
            self.report_error("Пустой файл или отсутствуют значимые лексемы", None)
            return self.errors
            
        self.parse_Program()
        if self.pos < len(self.lexemes):
            self.report_error("Неожиданные символы в конце файла", self.current())
            
        return self.errors

    def parse_Program(self):
        sync = {';', '}'}
        self.match('auto', sync.union({'Идентификатор', '=', '{'}))
        self.match_type('Идентификатор', sync.union({'=', '{'}))
        self.parse_Init(sync)

    def parse_Init(self, sync_set):
        curr = self.current()
        if curr and curr['lexeme'] == '=':
            self.match('=', {'['})
            self.parse_Lambda(sync_set.union({';'}))
            self.match(';', sync_set)
        elif curr and curr['lexeme'] == '{':
            self.match('{', {'['})
            self.parse_Lambda(sync_set.union({'}'}))
            self.match('}', {';'})
            self.match(';', sync_set)
        else:
            self.report_error("Ожидалось '=' или '{' для инициализации", curr)
            self.neutralize(sync_set.union({'['}))
            curr2 = self.current()
            if curr2 and curr2['lexeme'] == '[':
                self.parse_Lambda(sync_set.union({';'}))
                self.match(';', sync_set)

    def parse_Lambda(self, sync_set):
        self.match('[', {']'})
        self.match(']', {'('})
        self.match('(', {'int', 'float', ')'})
        self.parse_ArgList({')'})
        self.match(')', {'{'})
        self.match('{', {'return'})
        self.match('return', {'Идентификатор', 'Целое без знака', '('})
        self.parse_Expression({';'})
        self.match(';', {'}'})
        self.match('}', sync_set)

    def parse_ArgList(self, sync_set):
        curr = self.current()
        if curr and curr['lexeme'] in ('int', 'float'):
            self.parse_Type({'Идентификатор'})
            self.match_type('Идентификатор', sync_set.union({','}))
            self.parse_ArgListTail(sync_set)
        else:
            pass 

    def parse_ArgListTail(self, sync_set):
        curr = self.current()
        if curr and curr['lexeme'] == ',':
            self.match(',', {'int', 'float'})
            self.parse_Type({'Идентификатор'})
            self.match_type('Идентификатор', sync_set.union({','}))
            self.parse_ArgListTail(sync_set)
        else:
            pass 

    def parse_Type(self, sync_set):
        curr = self.current()
        if curr and curr['lexeme'] in ('int', 'float'):
            self.advance()
        else:
            self.report_error("Ожидался тип данных (int, float)", curr)
            self.neutralize(sync_set)

    def parse_Expression(self, sync_set):
        self.parse_Term(sync_set.union({'+', '-'}))
        self.parse_ExpTail(sync_set)

    def parse_ExpTail(self, sync_set):
        curr = self.current()
        if curr and curr['lexeme'] in ('+', '-'):
            self.parse_AddOp({'Идентификатор', 'Целое без знака', '('})
            self.parse_Term(sync_set.union({'+', '-'}))
            self.parse_ExpTail(sync_set)
        else:
            pass 

    def parse_AddOp(self, sync_set):
        curr = self.current()
        if curr and curr['lexeme'] in ('+', '-'):
            self.advance()
        else:
            self.report_error("Ожидался оператор сложения/вычитания", curr)
            self.neutralize(sync_set)

    def parse_Term(self, sync_set):
        self.parse_Factor(sync_set.union({'*', '/'}))
        self.parse_TermTail(sync_set)

    def parse_TermTail(self, sync_set):
        curr = self.current()
        if curr and curr['lexeme'] in ('*', '/'):
            self.parse_MultOp({'Идентификатор', 'Целое без знака', '('})
            self.parse_Factor(sync_set.union({'*', '/'}))
            self.parse_TermTail(sync_set)
        else:
            pass 

    def parse_MultOp(self, sync_set):
        curr = self.current()
        if curr and curr['lexeme'] in ('*', '/'):
            self.advance()
        else:
            self.report_error("Ожидался оператор умножения/деления", curr)
            self.neutralize(sync_set)

    def parse_Factor(self, sync_set):
        curr = self.current()
        if curr and curr['type'] == 'Идентификатор':
            self.advance()
        elif curr and curr['type'] == 'Целое без знака':
            self.advance()
        elif curr and curr['lexeme'] == '(':
            self.match('(', {'Идентификатор', 'Целое без знака', '('})
            self.parse_Expression(sync_set.union({')'}))
            self.match(')', sync_set)
        else:
            self.report_error("Ожидался операнд (идентификатор, число, открывающая скобка)", curr)
            self.neutralize(sync_set)
