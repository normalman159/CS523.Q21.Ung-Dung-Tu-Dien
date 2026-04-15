from __future__ import annotations

from PyQt6.QtCore import QObject

from src.radix_trie import RadixTrie
from src.UI.main_window import DictionaryWindow


class Controller(QObject):
    def __init__(self, trie: RadixTrie, view: DictionaryWindow) -> None:
        super().__init__()
        self.trie = trie
        self.view = view
        self._connect_signals()
        self.refresh_view()

    def _connect_signals(self) -> None:
        self.view.add_requested.connect(self.handle_add_word)
        self.view.delete_requested.connect(self.handle_delete_word)
        self.view.search_requested.connect(self.handle_search_word)

    def refresh_view(self) -> None:
        self.view.redraw_tree(self.trie.root)

    def handle_add_word(self) -> None:
        word = self.view.get_add_word()
        definition = self.view.get_add_definition()

        if not word or not definition:
            self.view.show_error("Lỗi", "Vui lòng nhập đầy đủ từ và định nghĩa.")
            return

        if self.view.word_exists(word):
            self.view.show_error("Lỗi", "Từ này đã tồn tại!")
            return

        try:
            self.trie.insert(word, definition)
        except ValueError as error:
            self.view.show_error("Lỗi", str(error))
            return

        self.view.append_history(word, definition)
        self.view.show_message("Thành công", f"Đã thêm từ: {word}")
        self.view.clear_add_inputs()
        self.refresh_view()

    def handle_delete_word(self) -> None:
        word = self.view.get_delete_word()
        if not word:
            self.view.show_error("Lỗi", "Vui lòng nhập từ cần xóa.")
            return

        deleted = self.trie.delete(word)
        if deleted:
            self.view.remove_history(word)
            self.view.show_message("Thành công", f"Đã xóa từ: {word}")
            self.view.clear_delete_input()
            self.refresh_view()
            return

        self.view.show_error("Lỗi", f"Không tìm thấy từ: {word}")

    def handle_search_word(self) -> None:
        word = self.view.get_search_word()
        if not word:
            self.view.set_search_result("Vui lòng nhập từ cần tra cứu.")
            self.view.reset_tree_colors()
            return

        # Thực hiện manual tracing path để gửi UI Highlight
        path = []
        current = self.trie.root
        remaining = word
        path.append(current)

        found = False
        definition = None

        while remaining:
            child = current.children.get(remaining[0])
            if child is None or not remaining.startswith(child.label):
                break
            
            path.append(child)
            remaining = remaining[len(child.label) :]
            current = child

        if not remaining and current.definition is not None:
            found = True
            definition = current.definition
        
        # Bật highlight và làm mờ các thành phần khác
        self.view.highlight_search_path(path, found)

        if found:
            self.view.set_search_result(f"{word}:\n{definition}")
        else:
            self.view.set_search_result(f"Không tìm thấy định nghĩa của từ: {word}")
