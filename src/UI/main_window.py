from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QSplitter, QVBoxLayout, QWidget, QMessageBox

from src.radix_trie import Node
from src.UI.control_panel import ControlPanel
from src.UI.trie_graphics import TreeLayoutEngine, TrieNodeItem, TrieEdgeItem

class DictionaryWindow(QWidget):
    NODE_DIAMETER = 42
    HORIZONTAL_GAP = 60
    VERTICAL_GAP = 120

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ứng dụng từ điển")
        self.resize(1200, 800)

        self.control_panel = ControlPanel()
        
        self.scene = QGraphicsScene(self)
        self.graphics_view = QGraphicsView(self.scene)
        self.graphics_view.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
        )
        self.graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        self._node_items: dict[int, TrieNodeItem] = {}
        self._edge_items: dict[int, TrieEdgeItem] = {}

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.graphics_view)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

    @property
    def add_requested(self):
        return self.control_panel.add_requested
    
    @property
    def delete_requested(self):
        return self.control_panel.delete_requested
    
    @property
    def search_requested(self):
        return self.control_panel.search_requested

    def get_add_word(self) -> str:
        return self.control_panel.add_word_input.text().strip()

    def get_add_definition(self) -> str:
        return self.control_panel.add_def_input.toPlainText().strip()
        
    def clear_add_inputs(self) -> None:
        self.control_panel.add_word_input.clear()
        self.control_panel.add_def_input.clear()

    def get_delete_word(self) -> str:
        return self.control_panel.del_word_input.text().strip()
        
    def clear_delete_input(self) -> None:
        self.control_panel.del_word_input.clear()

    def get_search_word(self) -> str:
        return self.control_panel.search_word_input.text().strip()
        
    def set_search_result(self, msg: str) -> None:
        self.control_panel.search_result.setPlainText(msg)

    def word_exists(self, word: str) -> bool:
        return self.control_panel.history_table.word_exists(word)

    def append_history(self, word: str, definition: str) -> None:
        self.control_panel.history_table.append_row(word, definition)
        
    def remove_history(self, word: str) -> None:
        self.control_panel.history_table.remove_row(word)

    # Hiển thị thông báo dạng Alert (Popup)
    def show_message(self, title: str, text: str) -> None:
        QMessageBox.information(self, title, text)
        
    def show_error(self, title: str, text: str) -> None:
        QMessageBox.warning(self, title, text)

    def redraw_tree(self, root: Node) -> None:
        self.scene.clear()
        self._node_items.clear()
        self._edge_items.clear()

        engine = TreeLayoutEngine(self.NODE_DIAMETER, self.HORIZONTAL_GAP, self.VERTICAL_GAP)
        positions = engine.compute(root)

        self._draw_edges(root, positions)
        self._draw_nodes(root, positions, "")

        scene_rect = self.scene.itemsBoundingRect().adjusted(-40, -40, 40, 40)
        self.scene.setSceneRect(scene_rect)
        self.graphics_view.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)

    def _draw_edges(self, node: Node, positions: dict[int, tuple[float, float]]):
        node_id = id(node)
        if node_id not in positions: return
        x1, y1 = positions[node_id]
        radius = self.NODE_DIAMETER / 2

        for child in node.children.values():
            child_id = id(child)
            if child_id in positions:
                x2, y2 = positions[child_id]
                edge_item = TrieEdgeItem(x1, y1 + radius, x2, y2 - radius, child.label, child)
                self.scene.addItem(edge_item)
                self._edge_items[child_id] = edge_item
                self._draw_edges(child, positions)

    def _draw_nodes(self, node: Node, positions: dict[int, tuple[float, float]], path_text: str):
        node_id = id(node)
        if node_id in positions:
            x, y = positions[node_id]
            is_root = (path_text == "")

            if is_root:
                display_text = "root"
            elif node.is_terminal:
                stt = "?"
                for i, (w, _) in enumerate(self.control_panel.history_table.words):
                    if w == path_text:
                        stt = str(i + 1)
                        break
                display_text = stt
            else:
                display_text = ""

            node_item = TrieNodeItem(x, y, self.NODE_DIAMETER, display_text, node.is_terminal, node, is_root=is_root)
            self.scene.addItem(node_item)
            self._node_items[node_id] = node_item

            for child in node.children.values():
                self._draw_nodes(child, positions, path_text + child.label)

    def highlight_search_path(self, visited_nodes: list[Node], found: bool = False) -> None:
        visited_ids = {id(n) for n in visited_nodes}

        for n_id, node_item in self._node_items.items():
            if n_id in visited_ids:
                is_target = found and (n_id == id(visited_nodes[-1]))
                node_item.set_highlight(is_target, found=found)
            else:
                node_item.set_dimmed()

        for child_id, edge_item in self._edge_items.items():
            if child_id in visited_ids:
                edge_item.set_highlight(found=found)
            else:
                edge_item.set_dimmed()

    def reset_tree_colors(self) -> None:
        for node_item in self._node_items.values():
            node_item.reset_colors()
            
        for edge_item in self._edge_items.values():
            edge_item.reset_colors()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if not self.scene.sceneRect().isNull():
            self.graphics_view.fitInView(
                self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio
            )
