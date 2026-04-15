from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from src.controller import Controller
from src.radix_trie import RadixTrie
from src.UI.main_window import DictionaryWindow


def main() -> int:
    app = QApplication(sys.argv)
    trie = RadixTrie()
    view = DictionaryWindow()
    controller = Controller(trie, view)
    view.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())