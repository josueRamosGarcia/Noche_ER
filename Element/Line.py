# Imports de PyQt6
from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtCore import QLineF
from PyQt6.QtGui import QPen

class Line(QGraphicsLineItem):
    """
    Clase que representa una línea de conexión entre dos elementos en el diagrama.
    Hereda de QGraphicsLineItem para la representación gráfica de la línea.
    """
    
    # Constantes de clase
    LINE_WIDTH = 2
    Z_VALUE = -1
    DATA_TYPE_KEY = 0
    DATA_ITEM1_KEY = 1
    DATA_ITEM2_KEY = 2

    def __init__(self, items):
        """
        Inicializa una nueva línea entre dos elementos.
        
        Args:
            items (list): Lista de dos elementos a conectar.
                         Debe contener exactamente dos elementos.
        
        Raises:
            ValueError: Si items no contiene exactamente dos elementos.
        """
        if len(items) != 2:
            raise ValueError("La lista de items debe contener exactamente dos elementos")

        self._setup_line(items)
        self._setup_style()
        self._setup_data(items)

    def _setup_line(self, items):
        """Configura la línea entre los dos elementos."""
        item1, item2 = items
        pos1 = self._get_item_center(item1)
        pos2 = self._get_item_center(item2)
        super().__init__(QLineF(pos1, pos2))

    def _get_item_center(self, item):
        """Obtiene el centro de un elemento en coordenadas de la escena."""
        return item.mapToScene(item.boundingRect().center())

    def _setup_style(self):
        """Configura el estilo visual de la línea."""
        self.pen = QPen()
        self.pen.setWidth(self.LINE_WIDTH)
        self.setPen(self.pen)
        self.setZValue(self.Z_VALUE)

    def _setup_data(self, items):
        """Configura los datos de la línea."""
        self.setData(self.DATA_TYPE_KEY, "Line")
        self.setData(self.DATA_ITEM1_KEY, items[0])
        self.setData(self.DATA_ITEM2_KEY, items[1])