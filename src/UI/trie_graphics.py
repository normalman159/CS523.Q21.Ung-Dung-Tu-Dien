from __future__ import annotations

from PyQt6.QtGui import QColor, QBrush, QPen, QFont
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsItemGroup,
    QGraphicsRectItem,
)

from src.radix_trie import Node


class TreeLayoutEngine:
    def __init__(self, node_diameter: float, h_gap: float, v_gap: float):
        self.node_diameter = node_diameter
        self.h_gap = h_gap
        self.v_gap = v_gap
        self.subtree_widths: dict[int, float] = {}
        self.positions: dict[int, tuple[float, float]] = {}

    def compute(self, root: Node) -> dict[int, tuple[float, float]]:
        self.subtree_widths.clear()
        self.positions.clear()
        self._compute_widths(root)
        self._assign_positions(root, 0.0, 0)
        return self.positions

    def _compute_widths(self, node: Node) -> float:
        node_id = id(node)
        if not node.children:
            self.subtree_widths[node_id] = self.node_diameter
            return self.node_diameter

        total_width = sum(self._compute_widths(child) for child in node.children.values())
        if len(node.children) > 1:
            total_width += self.h_gap * (len(node.children) - 1)
        
        w = max(self.node_diameter, total_width)
        self.subtree_widths[node_id] = w
        return w

    def _assign_positions(self, node: Node, left: float, depth: int) -> None:
        node_id = id(node)
        width = self.subtree_widths[node_id]
        center_x = left + width / 2.0
        center_y = 40.0 + depth * self.v_gap
        self.positions[node_id] = (center_x, center_y)

        if not node.children:
            return

        total_children_width = sum(self.subtree_widths[id(child)] for child in node.children.values())
        if len(node.children) > 1:
            total_children_width += self.h_gap * (len(node.children) - 1)
        child_left = left + (width - total_children_width) / 2.0

        for child in node.children.values():
            child_width = self.subtree_widths[id(child)]
            self._assign_positions(child, child_left, depth + 1)
            child_left += child_width + self.h_gap


class TrieNodeItem(QGraphicsItemGroup):
    def __init__(self, x: float, y: float, diameter: float, text: str, is_terminal: bool, node_ref: Node, is_root: bool = False):
        super().__init__()
        self.node_ref = node_ref
        self.is_terminal = is_terminal
        self.is_root = is_root

        self.base_bg = QColor("#ffffff") if (is_terminal or is_root) else QColor("#000000")
        self.base_border = QColor("#000000")
        self.base_text = QColor("#000000")

        if self.is_root:
            rect_w, rect_h = 40.0, 24.0
            self.shape_item = QGraphicsRectItem(-rect_w/2, -rect_h/2, rect_w, rect_h)
        elif self.is_terminal:
            radius = 16.0
            self.shape_item = QGraphicsEllipseItem(-radius, -radius, radius * 2, radius * 2)
        else:
            radius = 8.0
            self.shape_item = QGraphicsEllipseItem(-radius, -radius, radius * 2, radius * 2)

        self.shape_item.setBrush(QBrush(self.base_bg))
        self.shape_item.setPen(QPen(self.base_border, 2))
        self.addToGroup(self.shape_item)

        if is_terminal or is_root:
            self.text_item = QGraphicsTextItem(text)
            font = QFont()
            font.setPointSize(9)
            if is_root:
                font.setBold(True)
            self.text_item.setFont(font)
            self.text_item.setDefaultTextColor(self.base_text)
            
            bounds = self.text_item.boundingRect()
            self.text_item.setPos(-bounds.width() / 2, -bounds.height() / 2)
            self.addToGroup(self.text_item)
        else:
            self.text_item = None

        self.setPos(x, y)

    def set_highlight(self, is_target: bool = False, found: bool = True) -> None:
        if found:
            highlight_color = QColor("#ffcc00")
            bg_color = QColor("#ffd700") if is_target else QColor("#ffea70")
            text_color = QColor("#000000")
        else:
            highlight_color = QColor("#ff0000")
            bg_color = highlight_color if is_target else QColor("#ff9999")
            text_color = QColor("#ffffff") if is_target else highlight_color

        if not (self.is_terminal or self.is_root):
            bg_color = highlight_color

        self.shape_item.setBrush(QBrush(bg_color))
        self.shape_item.setPen(QPen(highlight_color, 2))
        if self.text_item:
            self.text_item.setDefaultTextColor(text_color)

    def set_dimmed(self) -> None:
        dimmed_bg = QColor("#ffffff") if (self.is_terminal or self.is_root) else QColor("#cbd5e0")
        dimmed_color = QColor("#cbd5e0")
        
        self.shape_item.setBrush(QBrush(dimmed_bg))
        self.shape_item.setPen(QPen(dimmed_color, 1))
        if self.text_item:
            self.text_item.setDefaultTextColor(dimmed_color)

    def reset_colors(self) -> None:
        self.shape_item.setBrush(QBrush(self.base_bg))
        self.shape_item.setPen(QPen(self.base_border, 2))
        if self.text_item:
            self.text_item.setDefaultTextColor(self.base_text)


class TrieEdgeItem(QGraphicsItemGroup):
    def __init__(self, x1: float, y1: float, x2: float, y2: float, label_text: str, target_node: Node):
        super().__init__()
        self.target_node = target_node
        
        self.base_line = QColor("#000000")
        self.base_text = QColor("#000000")

        self.line = QGraphicsLineItem(x1, y1, x2, y2)
        self.line.setPen(QPen(self.base_line, 2))
        self.addToGroup(self.line)

        label_x = x1 + (x2 - x1) * 0.70
        label_y = y1 + (y2 - y1) * 0.70
        
        self.text_item = QGraphicsTextItem(label_text)
        self.text_item.setDefaultTextColor(self.base_text)
        bounds = self.text_item.boundingRect()
        
        pad_x = 4.0
        pad_y = 2.0
        rect_w = bounds.width() + pad_x * 2
        rect_h = bounds.height() + pad_y * 2
        
        self.rect_item = QGraphicsRectItem(label_x - rect_w / 2, label_y - rect_h / 2, rect_w, rect_h)
        self.rect_item.setBrush(QBrush(QColor("#ffffff")))
        self.rect_item.setPen(QPen(self.base_line, 1))
        
        self.addToGroup(self.rect_item)
        
        self.text_item.setPos(label_x - bounds.width() / 2, label_y - bounds.height() / 2)
        self.addToGroup(self.text_item)

    def set_highlight(self, found: bool = True) -> None:
        highlight_color = QColor("#ffcc00") if found else QColor("#ff0000")
        text_color = QColor("#886600") if found else QColor("#ff0000")
        
        self.line.setPen(QPen(highlight_color, 2))
        self.rect_item.setPen(QPen(highlight_color, 1))
        self.text_item.setDefaultTextColor(text_color)
        font = self.text_item.font()
        font.setBold(True)
        self.text_item.setFont(font)

    def set_dimmed(self) -> None:
        dimmed_color = QColor("#cbd5e0")
        self.line.setPen(QPen(dimmed_color, 1))
        self.rect_item.setPen(QPen(dimmed_color, 1))
        self.text_item.setDefaultTextColor(dimmed_color)
        font = self.text_item.font()
        font.setBold(False)
        self.text_item.setFont(font)

    def reset_colors(self) -> None:
        self.line.setPen(QPen(self.base_line, 2))
        self.rect_item.setPen(QPen(self.base_line, 1))
        self.text_item.setDefaultTextColor(self.base_text)
        font = self.text_item.font()
        font.setBold(False)
        self.text_item.setFont(font)
