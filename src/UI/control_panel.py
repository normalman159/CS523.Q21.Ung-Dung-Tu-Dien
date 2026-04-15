from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem
)

class HistoryTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["STT", "Từ", "Định nghĩa"])
        vertical_header = self.table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(False)
        
        header = self.table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(True)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 150)
        
        layout.addWidget(self.table)
        
        self.words: list[tuple[str, str]] = []

    def word_exists(self, word: str) -> bool:
        """Kiểm tra xem từ đã tồn tại trong lịch sử chưa"""
        for w, _ in self.words:
            if w == word:
                return True
        return False

    def append_row(self, word: str, definition: str) -> None:
        self.words.append((word, definition))
        self._render_table()

    def remove_row(self, word: str) -> None:
        self.words = [item for item in self.words if item[0] != word]
        self._render_table()

    def clear_table(self) -> None:
        self.words.clear()
        self._render_table()

    def _render_table(self) -> None:
        self.table.setRowCount(0)
        for i, (w, d) in enumerate(self.words):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(w))
            self.table.setItem(i, 2, QTableWidgetItem(d))


class ControlPanel(QWidget):
    add_requested = pyqtSignal()
    delete_requested = pyqtSignal()
    search_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        # Word Addition Tab
        self.tab_add = QWidget()
        tab_add_layout = QVBoxLayout(self.tab_add)
        self.add_word_input = QLineEdit()
        self.add_word_input.setPlaceholderText("Nhập từ cần thêm")
        self.add_def_input = QTextEdit()
        self.add_def_input.setPlaceholderText("Nhập định nghĩa")
        self.add_def_input.setAcceptRichText(False)
        self.add_btn = QPushButton("Thêm")
        
        tab_add_layout.addWidget(QLabel("Từ:"))
        tab_add_layout.addWidget(self.add_word_input)
        tab_add_layout.addWidget(QLabel("Định nghĩa:"))
        tab_add_layout.addWidget(self.add_def_input)
        tab_add_layout.addWidget(self.add_btn)
        
        # Word Deletion Tab
        self.tab_del = QWidget()
        tab_del_layout = QVBoxLayout(self.tab_del)
        self.del_word_input = QLineEdit()
        self.del_word_input.setPlaceholderText("Nhập từ muốn xóa")
        self.del_btn = QPushButton("Xóa")
        
        tab_del_layout.addWidget(QLabel("Từ cần xóa:"))
        tab_del_layout.addWidget(self.del_word_input)
        tab_del_layout.addWidget(self.del_btn)
        tab_del_layout.addStretch()
        
        # Search Tab
        self.tab_search = QWidget()
        tab_search_layout = QVBoxLayout(self.tab_search)
        self.search_word_input = QLineEdit()
        self.search_word_input.setPlaceholderText("Nhập từ muốn tìm kiếm")
        self.search_btn = QPushButton("Tra cứu")
        self.search_result = QTextEdit()
        self.search_result.setReadOnly(True)
        self.search_result.setPlaceholderText("Kết quả sẽ hiển thị ở đây")
        self.search_result.setAcceptRichText(False)
        
        tab_search_layout.addWidget(QLabel("Từ cần tra cứu:"))
        tab_search_layout.addWidget(self.search_word_input)
        tab_search_layout.addWidget(self.search_btn)
        tab_search_layout.addWidget(QLabel("Kết quả:"))
        tab_search_layout.addWidget(self.search_result)
        
        self.tabs.addTab(self.tab_add, "Thêm từ")
        self.tabs.addTab(self.tab_del, "Xóa từ")
        self.tabs.addTab(self.tab_search, "Tra cứu")
        
        self.history_table = HistoryTable()
        
        layout.addWidget(self.tabs, stretch=0)
        layout.addSpacing(10)
        layout.addWidget(QLabel("Dữ liệu đã nhập (Lịch sử):"))
        layout.addWidget(self.history_table, stretch=1)
        
        self.add_btn.clicked.connect(self.add_requested.emit)
        self.del_btn.clicked.connect(self.delete_requested.emit)
        self.search_btn.clicked.connect(self.search_requested.emit)
