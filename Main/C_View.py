from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtGui import QWheelEvent, QMouseEvent, QPainter
from PyQt6.QtCore import Qt, QPoint, QPointF

class MainView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        self.zoom_factor = 1.0
        self.zoom_in_limit = 3.0
        self.zoom_out_limit = 0.5
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.last_mouse_pos = QPoint()

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Calcular el factor de zoom basado en el ángulo del scroll
            delta = event.angleDelta().y()
            zoom_factor = 1.0 + (delta / 1200.0)  # Hacer el zoom más gradual
            
            new_zoom_factor = self.zoom_factor * zoom_factor

            if new_zoom_factor <= self.zoom_in_limit and new_zoom_factor >= self.zoom_out_limit:
                self.zoom_factor = new_zoom_factor
                self.scale(zoom_factor, zoom_factor)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.last_mouse_pos = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
            delta = event.pos() - self.last_mouse_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_mouse_pos = event.pos()
            # Llamar a expandScene para ajustar los límites de la escena
            scene_pos = self.mapToScene(event.pos())
            self.scene().expandScene(scene_pos, self.zoom_factor)
        else:
            super().mouseMoveEvent(event)


    def getVisibleSceneRect(self):
        rect = self.viewport().rect()  # Obtener el rectángulo de la vista
        return self.mapToScene(rect).boundingRect()


    def getZoomFactor(self):
        return self.zoom_factor

    def resetView(self):
        # Resetear el zoom
        self.zoom_factor = 1.0
        self.resetTransform()
        
        # Resetear la posición de la escena
        self.scene().setSceneRect(1, 1, 1278, 718)
        
        # Centrar la vista
        self.centerOn(self.scene().sceneRect().center())
        
        # Actualizar la vista
        self.viewport().update()  