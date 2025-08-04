from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QPen, QColor, QBrush
from PyQt6.QtCore import QRectF, Qt

class SelectionBox(QGraphicsRectItem):
    
    def __init__(self, start_pos, scene):
        super().__init__()
        self.start_pos = start_pos
        self.scene = scene
        self.setPen(QPen(QColor(0, 0, 255), 2, Qt.PenStyle.DashLine))
        self.setBrush(QBrush(QColor(0, 0, 255, 50)))
        self.setRect(self.start_pos.x(), self.start_pos.y(), 0, 0)

    def update_size(self, current_pos):
        # Calcular las coordenadas del rectángulo
        x1 = min(self.start_pos.x(), current_pos.x())
        y1 = min(self.start_pos.y(), current_pos.y())
        x2 = max(self.start_pos.x(), current_pos.x())
        y2 = max(self.start_pos.y(), current_pos.y())
        
        # Actualizar el rectángulo con las coordenadas calculadas
        self.setRect(x1, y1, x2 - x1, y2 - y1)

    def finalize(self):
        rect = QRectF(self.rect())
        selected_items = self.scene.items(rect)
        self.scene.receive_selected_items(selected_items)

        if not selected_items:
            self.scene.removeItem(self)
            return
        self.scene.removeItem(self)


