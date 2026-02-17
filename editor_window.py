import os
from PyQt6.QtWidgets import (QMainWindow, QPlainTextEdit, QSplitter, QApplication, 
                             QMessageBox, QFileDialog, QToolBar, QStatusBar, QWidget, QVBoxLayout, QMenu)
from PyQt6.QtGui import QAction, QFont, QCloseEvent, QIcon, QKeySequence
from PyQt6.QtCore import Qt, QSize
from highlighter import SyntaxHighlighter

class CompilerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compiler Project - Language Processor")
        self.resize(1000, 700)
        
        self.current_file = None
        self.is_modified = False
        
        self.setup_ui()
        self.setup_actions()
        self.setup_menus()
        self.setup_toolbar()
        
        # Apply syntax highlighting
        self.highlighter = SyntaxHighlighter(self.code_editor.document())
        
        # Connect modification signal
        self.code_editor.textChanged.connect(self.document_modified)
        
        self.update_status_bar()

    def setup_ui(self):
        # Central widget is a localized splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Code Editor (Top)
        self.code_editor = QPlainTextEdit()
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.code_editor.setFont(font)
        splitter.addWidget(self.code_editor)
        
        # Output Area (Bottom)
        self.output_area = QPlainTextEdit()
        self.output_area.setFont(font)
        self.output_area.setReadOnly(True)
        # Placeholder text for output
        self.output_area.setPlaceholderText("Compiler output will appear here...")
        splitter.addWidget(self.output_area)
        
        # Set initial splitter sizes (70% code, 30% output)
        splitter.setSizes([500, 200])
        
        self.setCentralWidget(splitter)
        self.setStatusBar(QStatusBar())

    def setup_actions(self):
        style = self.style()
        
        # --- File Actions ---
        self.new_act = QAction(style.standardIcon(style.StandardPixmap.SP_FileIcon), "&Новый", self)
        self.new_act.setShortcut(QKeySequence.StandardKey.New)
        self.new_act.triggered.connect(self.new_file)
        
        self.open_act = QAction(style.standardIcon(style.StandardPixmap.SP_DialogOpenButton), "&Открыть...", self)
        self.open_act.setShortcut(QKeySequence.StandardKey.Open)
        self.open_act.triggered.connect(self.open_file)
        
        self.save_act = QAction(style.standardIcon(style.StandardPixmap.SP_DriveFDIcon), "&Сохранить", self)
        self.save_act.setShortcut(QKeySequence.StandardKey.Save)
        self.save_act.triggered.connect(self.save_file)
        
        self.save_as_act = QAction("Сохранить &как...", self)
        self.save_as_act.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_act.triggered.connect(self.save_file_as)
        
        self.exit_act = QAction(style.standardIcon(style.StandardPixmap.SP_DialogCloseButton), "В&ыход", self)
        self.exit_act.setShortcut("Ctrl+Q")
        self.exit_act.triggered.connect(self.close)

        # --- Edit Actions ---
        self.undo_act = QAction(style.standardIcon(style.StandardPixmap.SP_ArrowBack), "&Отменить", self)
        self.undo_act.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_act.triggered.connect(self.code_editor.undo)
        
        self.redo_act = QAction(style.standardIcon(style.StandardPixmap.SP_ArrowForward), "&Повторить", self)
        self.redo_act.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_act.triggered.connect(self.code_editor.redo)
        
        self.cut_act = QAction(style.standardIcon(style.StandardPixmap.SP_DialogResetButton), "&Вырезать", self) # Using Reset icon as generic 'cut' alternative if scissors not avail
        self.cut_act.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_act.triggered.connect(self.code_editor.cut)
        
        self.copy_act = QAction(style.standardIcon(style.StandardPixmap.SP_FileIcon), "&Копировать", self) # Generic file icon
        self.copy_act.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_act.triggered.connect(self.code_editor.copy)
        
        self.paste_act = QAction(style.standardIcon(style.StandardPixmap.SP_DialogOkButton), "&Вставить", self) # Generic OK check
        self.paste_act.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_act.triggered.connect(self.code_editor.paste)
        
        self.delete_act = QAction("&Удалить", self)
        self.delete_act.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_act.triggered.connect(lambda: self.code_editor.textCursor().removeSelectedText())
        
        self.select_all_act = QAction("В&ыделить все", self)
        self.select_all_act.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.select_all_act.triggered.connect(self.code_editor.selectAll)

        # --- Text Info Actions ---
        self.info_actions = {}
        info_items = [
            ("Постановка задачи", "Разработка текстового редактора с будущей интеграцией компилятора."),
            ("Грамматика", "Информация о грамматике языка (будет добавлена позже)."),
            ("Классификация грамматики", "Классификация согласно иерархии Хомского."),
            ("Метод анализа", "Описание выбранного метода синтаксического анализа."),
            ("Диагностика и нейтрализация ошибок", "Стратегии обработки ошибок компиляции."),
            ("Тестовый пример", "Пример кода на целевом языке."),
            ("Список литературы", "1. Ахо, Лам, Сетхи, Ульман «Компиляторы...»\n2. Документация Python/PyQt6"),
            ("Исходный код программы", "Код данного редактора.")
        ]
        
        for name, text in info_items:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, t=text, n=name: self.show_info_dialog(n, t))
            self.info_actions[name] = action

        # --- Run Action ---
        self.run_act = QAction(style.standardIcon(style.StandardPixmap.SP_MediaPlay), "&Пуск", self)
        self.run_act.setShortcut("F5")
        self.run_act.triggered.connect(self.run_analysis)

        # --- Help Actions ---
        self.help_act = QAction(style.standardIcon(style.StandardPixmap.SP_DialogHelpButton), "&Справка", self)
        self.help_act.setShortcut(QKeySequence.StandardKey.HelpContents)
        self.help_act.triggered.connect(lambda: self.show_info_dialog("Справка", "Справка по работе с редактором."))
        
        self.about_act = QAction("О &программе", self)
        self.about_act.triggered.connect(self.show_about_dialog)

    def setup_menus(self):
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu("&Файл")
        file_menu.addAction(self.new_act)
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.save_as_act)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)
        
        # Правка
        edit_menu = menubar.addMenu("&Правка")
        edit_menu.addAction(self.undo_act)
        edit_menu.addAction(self.redo_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_act)
        edit_menu.addAction(self.copy_act)
        edit_menu.addAction(self.paste_act)
        edit_menu.addAction(self.delete_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_all_act)
        
        # Текст
        text_menu = menubar.addMenu("&Текст")
        for name in self.info_actions:
            text_menu.addAction(self.info_actions[name])
            
        # Пуск
        run_menu = menubar.addMenu("П&уск")
        run_menu.addAction(self.run_act)
        
        # Справка
        help_menu = menubar.addMenu("&Справка")
        help_menu.addAction(self.help_act)
        help_menu.addAction(self.about_act)

    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.new_act)
        toolbar.addAction(self.open_act)
        toolbar.addAction(self.save_act)
        toolbar.addSeparator()
        toolbar.addAction(self.undo_act)
        toolbar.addAction(self.redo_act)
        toolbar.addSeparator()
        toolbar.addAction(self.cut_act)
        toolbar.addAction(self.copy_act)
        toolbar.addAction(self.paste_act)
        toolbar.addSeparator()
        toolbar.addAction(self.run_act)
        toolbar.addSeparator()
        toolbar.addAction(self.help_act)
        toolbar.addAction(self.about_act)

    def update_status_bar(self):
        filename = self.current_file if self.current_file else "Новый файл"
        modified_marker = "*" if self.is_modified else ""
        self.statusBar().showMessage(f"{filename}{modified_marker}")
        self.setWindowTitle(f"Compiler Project - {filename}{modified_marker}")

    # --- File Operations ---
    def new_file(self):
        if self.maybe_save():
            self.code_editor.clear()
            self.output_area.clear()
            self.current_file = None
            self.is_modified = False
            self.update_status_bar()

    def open_file(self):
        if self.maybe_save():
            path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Text Files (*.txt);;All Files (*)")
            if path:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.code_editor.setPlainText(f.read())
                    self.current_file = path
                    self.is_modified = False
                    self.update_status_bar()
                    self.output_area.appendPlainText(f"Файл загружен: {path}")
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл:\n{e}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.toPlainText())
                self.is_modified = False
                self.update_status_bar()
                return True
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")
                return False
        else:
            return self.save_file_as()

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "Text Files (*.txt);;All Files (*)")
        if path:
            self.current_file = path
            return self.save_file()
        return False

    def document_modified(self):
        if not self.is_modified:
            self.is_modified = True
            self.update_status_bar()

    def maybe_save(self):
        if not self.is_modified:
            return True
        
        ret = QMessageBox.warning(
            self, "Сохранение изменений",
            "Документ был изменен.\nСохранить изменения?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
        )
        
        if ret == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif ret == QMessageBox.StandardButton.Cancel:
            return False
        return True

    def closeEvent(self, event: QCloseEvent):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

    # --- Dialogs & Logic ---
    def show_info_dialog(self, title, content):
        QMessageBox.information(self, title, content)

    def show_about_dialog(self):
        QMessageBox.about(self, "О программе", 
                          "<h3>Compiler Project</h3>"
                          "<p>Простой текстовый редактор с подсветкой синтаксиса.</p>"
                          "<p>Разработан как часть курсового проекта.</p>")

    def run_analysis(self):
        # Stub for future compiler logic
        code = self.code_editor.toPlainText()
        self.output_area.setPlainText("--- Запуск анализатора ---\n")
        self.output_area.appendPlainText("Анализ завершен (заглушка).")
        # Here we would call the lexer/parser
        if not code.strip():
             self.output_area.appendPlainText("Внимание: Пустой исходный код.")
