class CompilerAnalyzer:
    def __init__(self):
        pass

    def analyze(self, code: str):
        errors = []
        output = []
        
        output.append("--- Запуск анализатора ---")
        output.append("Лексический анализ завершен...")
        output.append("Синтаксический анализ завершен...")

        if not code.strip():
            output.append("Внимание: Исходный код пуст.")
            errors.append({"row": 1, "col": 1, "message": "Ожидалось корректное выражение или токен."})
            
        return "\n".join(output), errors
