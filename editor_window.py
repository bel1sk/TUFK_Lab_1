import os
from PyQt6.QtWidgets import (QMainWindow, QPlainTextEdit, QSplitter, QApplication, 
                             QMessageBox, QFileDialog, QToolBar, QStatusBar, QWidget, 
                             QVBoxLayout, QMenu, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLabel, QTextEdit)
from PyQt6.QtGui import (QAction, QFont, QCloseEvent, QIcon, QKeySequence, QPainter, 
                         QColor, QTextFormat, QTextCursor)
from PyQt6.QtCore import Qt, QSize, QRect, pyqtSignal, QEvent

from highlighter import SyntaxHighlighter
from analyzer import LexicalAnalyzer, SyntaxAnalyzer


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    cursorPositionChangedSignal = pyqtSignal(int, int)
    modificationChangedSignal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.cursorPositionChanged.connect(self.emitCursorPosition)
        self.textChanged.connect(self.on_text_changed)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        
        self.current_file = None
        self.is_modified = False

        self.highlighter = SyntaxHighlighter(self.document())

        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

    def on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            self.modificationChangedSignal.emit(True)

    def emitCursorPosition(self):
        cursor = self.textCursor()
        row = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursorPositionChangedSignal.emit(row, col)

    def zoomIn(self, range: int = 1):
        font = self.font()
        font.setPointSize(font.pointSize() + range)
        self.setFont(font)

    def zoomOut(self, range: int = 1):
        font = self.font()
        font.setPointSize(max(1, font.pointSize() - range))
        self.setFont(font)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn()
            elif delta < 0:
                self.zoomOut()
            event.accept()
        else:
            super().wheelEvent(event)

    def lineNumberAreaWidth(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.GlobalColor.yellow).lighter(160)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.GlobalColor.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.GlobalColor.black)
                painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            blockNumber += 1


class CompilerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = 'ru'
        self.setAcceptDrops(True)
        self.analyzer = LexicalAnalyzer()
        
        self.i18n = {
            'ru': {
                'file': '&Файл', 'edit': '&Правка', 'text': '&Текст', 'run': 'П&уск',
                'help': '&Справка', 'lang': '&Язык',
                'new': '&Новый', 'open': '&Открыть...', 'save': '&Сохранить', 'save_as': 'Сохранить &как...',
                'exit': 'В&ыход', 'undo': '&Отменить', 'redo': '&Повторить', 'cut': '&Вырезать',
                'copy': '&Копировать', 'paste': '&Вставить', 'delete': '&Удалить', 'select_all': 'В&ыделить все',
                'run_act': '&Пуск', 'help_act': '&Справка', 'about': 'О &программе',
                'new_file': 'Новый файл', 'results': 'Результаты', 'errors': 'Ошибки',
                'row': 'Строка', 'col': 'Столбец', 'error_text': 'Текст ошибки',
                'code_col': 'Условный код', 'type_col': 'Тип лексемы', 'lexeme_col': 'Лексема', 'loc_col': 'Местоположение',
                'save_prompt': 'Документ был изменен.\nСохранить изменения?', 'save_title': 'Сохранение изменений',
                'loaded': 'Файл загружен: {}', 'error_open': 'Не удалось открыть файл:\n{}',
                'error_save': 'Не удалось сохранить файл:\n{}',
                'encoding': 'Кодировка: UTF-8', 'lang_status': 'Язык: Русский',
                'help_text': 'Текстовый редактор для курсового проекта.\n\nРеализованные функции:\n- Многовкладочный интерфейс с нумерацией строк\n- Подсветка синтаксиса для базовых конструкций\n- Изменение масштаба шрифта (Ctrl + Колесико)\n- Открытие файлов через Drag-and-Drop\n- Строка состояния с информацией о кодировке, языке и позиции курсора\n- Сохранение, открытие и редактирование текста\n- Интеграция с анализатором (заглушка)',
                'about_text': 'Compiler Project GUI v2\nАвтор: Гетман Денис Андреевич\nГруппа: АВТ-314'
            },
            'en': {
                'file': '&File', 'edit': '&Edit', 'text': '&Text', 'run': '&Run',
                'help': '&Help', 'lang': '&Language',
                'new': '&New', 'open': '&Open...', 'save': '&Save', 'save_as': 'Save &As...',
                'exit': 'E&xit', 'undo': '&Undo', 'redo': '&Redo', 'cut': '&Cut',
                'copy': '&Copy', 'paste': '&Paste', 'delete': '&Delete', 'select_all': 'Select &All',
                'run_act': '&Run', 'help_act': '&Help', 'about': '&About',
                'new_file': 'New file', 'results': 'Results', 'errors': 'Errors',
                'row': 'Row', 'col': 'Column', 'error_text': 'Error Message',
                'code_col': 'Code', 'type_col': 'Type', 'lexeme_col': 'Lexeme', 'loc_col': 'Location',
                'save_prompt': 'Document has been modified.\nSave changes?', 'save_title': 'Save Changes',
                'loaded': 'File loaded: {}', 'error_open': 'Failed to open file:\n{}',
                'error_save': 'Failed to save file:\n{}',
                'encoding': 'Encoding: UTF-8', 'lang_status': 'Language: English',
                'help_text': 'Text editor for course project.\n\nImplemented features:\n- Multi-tab interface with line numbers\n- Syntax highlighting for basic constructs\n- Font scaling (Ctrl + Mouse Wheel)\n- Drag-and-Drop file opening\n- Status bar with encoding, language, and cursor position\n- Saving, opening, and editing text\n- Analyzer integration (stub)',
                'about_text': 'Compiler Project GUI v2\nAuthor: Getman Denis Andreevich\nGroup: AVT-314'
            }
        }
        
        self.resize(1000, 700)
        self.setup_ui()
        self.setup_actions()
        self.setup_menus()
        self.setup_toolbar()
        
        self.new_file()
        self.update_ui_texts()

    def get_text(self, key):
        return self.i18n[self.current_lang].get(key, key)

    def setup_ui(self):
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)
        self.editor_tabs.currentChanged.connect(self.on_tab_changed)
        splitter.addWidget(self.editor_tabs)
        
        self.output_tabs = QTabWidget()
        
        self.results_table = QTableWidget(0, 4)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.cellClicked.connect(self.on_lexeme_clicked)
        self.output_tabs.addTab(self.results_table, "")
        
        self.errors_tab_widget = QWidget()
        errors_layout = QVBoxLayout()
        errors_layout.setContentsMargins(0, 0, 0, 0)
        self.errors_label = QLabel("Общее количество ошибок: 0")
        self.errors_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.errors_label.setStyleSheet("padding: 5px;")
        
        self.errors_table = QTableWidget(0, 3)
        self.errors_table.horizontalHeader().setStretchLastSection(True)
        self.errors_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.errors_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.errors_table.cellClicked.connect(self.on_error_clicked)
        
        errors_layout.addWidget(self.errors_label)
        errors_layout.addWidget(self.errors_table)
        self.errors_tab_widget.setLayout(errors_layout)
        self.output_tabs.addTab(self.errors_tab_widget, "")
        
        splitter.addWidget(self.output_tabs)
        splitter.setSizes([500, 200])
        self.setCentralWidget(splitter)
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.cursor_label = QLabel()
        self.encoding_label = QLabel()
        self.lang_label = QLabel()
        self.statusBar.addPermanentWidget(self.cursor_label)
        self.statusBar.addPermanentWidget(self.encoding_label)
        self.statusBar.addPermanentWidget(self.lang_label)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            font = self.results_table.font()
            if delta > 0:
                font.setPointSize(font.pointSize() + 1)
            elif delta < 0:
                font.setPointSize(max(1, font.pointSize() - 1))
            self.results_table.setFont(font)
            self.errors_table.setFont(font)
            event.accept()
        else:
            super().wheelEvent(event)

    def setup_actions(self):
        style = self.style()
        
        self.new_act = QAction(style.standardIcon(style.StandardPixmap.SP_FileIcon), "", self)
        self.new_act.setShortcut(QKeySequence.StandardKey.New)
        self.new_act.triggered.connect(self.new_file)
        
        self.open_act = QAction(style.standardIcon(style.StandardPixmap.SP_DialogOpenButton), "", self)
        self.open_act.setShortcut(QKeySequence.StandardKey.Open)
        self.open_act.triggered.connect(self.open_file)
        
        self.save_act = QAction(style.standardIcon(style.StandardPixmap.SP_DriveFDIcon), "", self)
        self.save_act.setShortcut(QKeySequence.StandardKey.Save)
        self.save_act.triggered.connect(self.save_file)
        
        self.save_as_act = QAction("", self)
        self.save_as_act.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_act.triggered.connect(self.save_file_as)
        
        self.exit_act = QAction(style.standardIcon(style.StandardPixmap.SP_DialogCloseButton), "", self)
        self.exit_act.setShortcut("Ctrl+Q")
        self.exit_act.triggered.connect(self.close)

        self.undo_act = QAction(style.standardIcon(style.StandardPixmap.SP_ArrowBack), "", self)
        self.undo_act.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_act.triggered.connect(self.forward_to_editor('undo'))
        
        self.redo_act = QAction(style.standardIcon(style.StandardPixmap.SP_ArrowForward), "", self)
        self.redo_act.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_act.triggered.connect(self.forward_to_editor('redo'))
        
        self.cut_act = QAction(style.standardIcon(style.StandardPixmap.SP_DialogResetButton), "", self)
        self.cut_act.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_act.triggered.connect(self.forward_to_editor('cut'))
        
        self.copy_act = QAction(style.standardIcon(style.StandardPixmap.SP_FileIcon), "", self)
        self.copy_act.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_act.triggered.connect(self.forward_to_editor('copy'))
        
        self.paste_act = QAction(style.standardIcon(style.StandardPixmap.SP_DialogOkButton), "", self)
        self.paste_act.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_act.triggered.connect(self.forward_to_editor('paste'))
        
        self.delete_act = QAction("", self)
        self.delete_act.triggered.connect(lambda: self.current_editor().textCursor().removeSelectedText() if self.current_editor() else None)
        
        self.select_all_act = QAction("", self)
        self.select_all_act.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.select_all_act.triggered.connect(self.forward_to_editor('selectAll'))

        self.run_act = QAction(style.standardIcon(style.StandardPixmap.SP_MediaPlay), "", self)
        self.run_act.setShortcut("F5")
        self.run_act.triggered.connect(self.run_analysis)

        self.help_act = QAction(style.standardIcon(style.StandardPixmap.SP_DialogHelpButton), "", self)
        self.help_act.triggered.connect(lambda: QMessageBox.information(self, self.get_text('help'), self.get_text('help_text')))
        
        self.about_act = QAction("", self)
        self.about_act.triggered.connect(lambda: QMessageBox.about(self, self.get_text('about'), self.get_text('about_text')))

        self.lang_ru_act = QAction("Русский", self)
        self.lang_ru_act.triggered.connect(lambda: self.set_language('ru'))
        self.lang_en_act = QAction("English", self)
        self.lang_en_act.triggered.connect(lambda: self.set_language('en'))

    def forward_to_editor(self, method_name):
        def handler():
            editor = self.current_editor()
            if editor and hasattr(editor, method_name):
                getattr(editor, method_name)()
        return handler

    def setup_menus(self):
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu("")
        self.file_menu.addAction(self.new_act)
        self.file_menu.addAction(self.open_act)
        self.file_menu.addAction(self.save_act)
        self.file_menu.addAction(self.save_as_act)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_act)
        
        self.edit_menu = menubar.addMenu("")
        self.edit_menu.addAction(self.undo_act)
        self.edit_menu.addAction(self.redo_act)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.cut_act)
        self.edit_menu.addAction(self.copy_act)
        self.edit_menu.addAction(self.paste_act)
        self.edit_menu.addAction(self.delete_act)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.select_all_act)
        
        self.text_menu = menubar.addMenu("")
        
        self.run_menu = menubar.addMenu("")
        self.run_menu.addAction(self.run_act)
        
        self.lang_menu = menubar.addMenu("")
        self.lang_menu.addAction(self.lang_ru_act)
        self.lang_menu.addAction(self.lang_en_act)

        self.help_menu = menubar.addMenu("")
        self.help_menu.addAction(self.help_act)
        self.help_menu.addAction(self.about_act)

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

    def set_language(self, lang):
        self.current_lang = lang
        self.update_ui_texts()
        self.update_status_bar()

    def update_ui_texts(self):
        self.setWindowTitle("Compiler Project - Language Processor")
        
        self.file_menu.setTitle(self.get_text('file'))
        self.edit_menu.setTitle(self.get_text('edit'))
        self.text_menu.setTitle(self.get_text('text'))
        self.run_menu.setTitle(self.get_text('run'))
        self.lang_menu.setTitle(self.get_text('lang'))
        self.help_menu.setTitle(self.get_text('help'))
        
        self.new_act.setText(self.get_text('new'))
        self.open_act.setText(self.get_text('open'))
        self.save_act.setText(self.get_text('save'))
        self.save_as_act.setText(self.get_text('save_as'))
        self.exit_act.setText(self.get_text('exit'))
        
        self.undo_act.setText(self.get_text('undo'))
        self.redo_act.setText(self.get_text('redo'))
        self.cut_act.setText(self.get_text('cut'))
        self.copy_act.setText(self.get_text('copy'))
        self.paste_act.setText(self.get_text('paste'))
        self.delete_act.setText(self.get_text('delete'))
        self.select_all_act.setText(self.get_text('select_all'))
        
        self.run_act.setText(self.get_text('run_act'))
        self.help_act.setText(self.get_text('help_act'))
        self.about_act.setText(self.get_text('about'))

        self.output_tabs.setTabText(0, self.get_text('results'))
        self.output_tabs.setTabText(1, self.get_text('errors'))
        
        self.results_table.setHorizontalHeaderLabels([self.get_text('code_col'), self.get_text('type_col'), self.get_text('lexeme_col'), self.get_text('loc_col')])
        self.errors_table.setHorizontalHeaderLabels(["Неверный фрагмент", self.get_text('loc_col'), self.get_text('error_text')])
        
        self.encoding_label.setText(self.get_text('encoding'))
        self.lang_label.setText(self.get_text('lang_status'))

        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            self.update_tab_title(i, editor)

    def update_status_bar(self):
        editor = self.current_editor()
        if editor:
            cursor = editor.textCursor()
            row = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.update_cursor_label(row, col)
        else:
            self.cursor_label.setText("")

    def update_cursor_label(self, row, col):
        t_row = self.get_text('row')
        t_col = self.get_text('col')
        self.cursor_label.setText(f"{t_row}: {row} | {t_col}: {col}")

    def current_editor(self):
        return self.editor_tabs.currentWidget()

    def new_file(self):
        editor = CodeEditor()
        editor.cursorPositionChangedSignal.connect(self.update_cursor_label)
        
        index = self.editor_tabs.addTab(editor, self.get_text('new_file'))
        self.editor_tabs.setCurrentIndex(index)
        
        editor.modificationChangedSignal.connect(lambda modified, idx=index: self.update_tab_title(self.editor_tabs.indexOf(editor), editor))

    def update_tab_title(self, index, editor):
        if index == -1: return
        title = os.path.basename(editor.current_file) if editor.current_file else self.get_text('new_file')
        if editor.is_modified:
            title += "*"
        self.editor_tabs.setTabText(index, title)

    def on_tab_changed(self, index):
        self.update_status_bar()

    def open_file(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, self.get_text('open'), "", "All Files (*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.new_file()
                editor = self.current_editor()
                editor.setPlainText(content)
                editor.current_file = path
                editor.is_modified = False
                self.update_tab_title(self.editor_tabs.currentIndex(), editor)
                self.results_table.setRowCount(0)
                self.errors_table.setRowCount(0)
            except Exception as e:
                QMessageBox.warning(self, "Error", self.get_text('error_open').format(e))

    def save_file(self):
        editor = self.current_editor()
        if not editor: return False
        
        if editor.current_file:
            try:
                with open(editor.current_file, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                editor.is_modified = False
                self.update_tab_title(self.editor_tabs.currentIndex(), editor)
                return True
            except Exception as e:
                QMessageBox.warning(self, "Error", self.get_text('error_save').format(e))
                return False
        else:
            return self.save_file_as()

    def save_file_as(self):
        editor = self.current_editor()
        if not editor: return False
        
        path, _ = QFileDialog.getSaveFileName(self, self.get_text('save_as'), "", "All Files (*)")
        if path:
            editor.current_file = path
            return self.save_file()
        return False

    def close_tab(self, index):
        editor = self.editor_tabs.widget(index)
        if editor.is_modified:
            self.editor_tabs.setCurrentIndex(index)
            ret = QMessageBox.warning(
                self, self.get_text('save_title'),
                self.get_text('save_prompt'),
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            if ret == QMessageBox.StandardButton.Save:
                if not self.save_file():
                    return False
            elif ret == QMessageBox.StandardButton.Cancel:
                return False
                
        self.editor_tabs.removeTab(index)
        if self.editor_tabs.count() == 0:
            self.new_file()
        return True

    def closeEvent(self, event: QCloseEvent):
        while self.editor_tabs.count() > 0:
            if not self.close_tab(0):
                event.ignore()
                return
            if self.editor_tabs.count() == 1:
                editor = self.editor_tabs.widget(0)
                if not editor.is_modified and not editor.current_file:
                    break
        event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.isLocalFile():
                self.open_file(url.toLocalFile())

    def highlight_in_editor(self, row, start_col, end_col):
        editor = self.current_editor()
        if not editor: return
        doc = editor.document()
        block = doc.findBlockByNumber(row - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            cursor.setPosition(block.position() + start_col - 1)
            cursor.setPosition(block.position() + end_col, QTextCursor.MoveMode.KeepAnchor)
            editor.setTextCursor(cursor)
            editor.setFocus()

    def on_lexeme_clicked(self, row, col):
        item_loc = self.results_table.item(row, 3)
        if item_loc:
            parts = item_loc.text().replace('(', '').replace(')', '').split(', ')
            r = int(parts[0].split(': ')[1])
            c_bounds = parts[1].split(': ')[1].split('-')
            start_c = int(c_bounds[0])
            end_c = int(c_bounds[1])
            self.highlight_in_editor(r, start_c, end_c)

    def on_error_clicked(self, row, col):
        item_loc = self.errors_table.item(row, 1)
        if item_loc:
            try:
                parts = item_loc.text().replace('(', '').replace(')', '').split(', ')
                r = int(parts[0].split(': ')[1])
                c = int(parts[1].split(': ')[1].split('-')[0])
                self.highlight_in_editor(r, c, c)
            except: pass

    def run_analysis(self):
        editor = self.current_editor()
        if not editor: return
        
        code = editor.toPlainText()
        
        lexemes, lex_errors = self.analyzer.analyze(code)

        syn_analyzer = SyntaxAnalyzer(lexemes)
        syn_errors = syn_analyzer.parse()
        
        all_errors = lex_errors + syn_errors
        
        self.results_table.setRowCount(0)
        self.errors_table.setRowCount(0)
        
        if len(all_errors) == 0:
            self.errors_label.setText("Ошибок не найдено. Анализ успешно завершен.")
            self.errors_label.setStyleSheet("padding: 5px; color: green;")
        else:
            self.errors_label.setText(f"Общее количество ошибок: {len(all_errors)}")
            self.errors_label.setStyleSheet("padding: 5px; color: red;")
        
        for i, lex in enumerate(lexemes):
            self.results_table.insertRow(i)
            self.results_table.setItem(i, 0, QTableWidgetItem(str(lex.get('code', ''))))
            self.results_table.setItem(i, 1, QTableWidgetItem(lex.get('type', '')))
            self.results_table.setItem(i, 2, QTableWidgetItem(lex.get('lexeme', '').replace(' ', '')))
            loc = f"(Row: {lex.get('row')}, Col: {lex.get('start_col')}-{lex.get('end_col')})"
            self.results_table.setItem(i, 3, QTableWidgetItem(loc))
        
        for i, error in enumerate(all_errors):
            self.errors_table.insertRow(i)
            self.errors_table.setItem(i, 0, QTableWidgetItem(str(error.get("lexeme", ""))))
            loc = f"(Row: {error.get('row', '-')}, Col: {error.get('col', '-')})"
            self.errors_table.setItem(i, 1, QTableWidgetItem(loc))
            self.errors_table.setItem(i, 2, QTableWidgetItem(str(error.get("message", ""))))
