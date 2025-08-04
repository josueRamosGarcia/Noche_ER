#  Imports de PyQt6
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsItem

class MouseInteractionMixin:
    """
    Mixin para manejar interacciones del mouse con elementos gráficos.
    Proporciona funcionalidad básica de arrastre y selección.
    """
    
    # Colores por defecto
    BACKGROUND_COLOR = QColor(230, 230, 230)
    Z_DEFAULT = 0
    Z_SELECTED = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_defaults()
        self._setup_mouse_interaction()

    def _setup_defaults(self):
        """Configura los valores por defecto del item."""
        self.setBrush(QBrush(self.BACKGROUND_COLOR))
        self.pen = QPen()
        self.setPen(self.pen)
        self.setZValue(self.Z_DEFAULT)

    def _setup_mouse_interaction(self):
        """Configura las interacciones del mouse."""
        self.setAcceptedMouseButtons(
            Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton
        )
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def _update_scene(self):
        """Actualiza la escena de manera segura."""
        if hasattr(self, 'scene') and self.scene is not None:
            self.scene.update()

    def mousePressEvent(self, event):
        """Maneja el evento de presionar el mouse."""
        super().mousePressEvent(event)
        self.setZValue(self.Z_SELECTED)
        self._update_scene()
        
    def mouseReleaseEvent(self, event):
        """Maneja el evento de soltar el mouse."""
        super().mouseReleaseEvent(event)
        self.setZValue(self.Z_DEFAULT)
        self._update_scene()
        
    def mouseMoveEvent(self, event):
        """Maneja el evento de mover el mouse."""
        super().mouseMoveEvent(event)
        self._update_scene()