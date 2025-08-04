# Imports de PyQt6
from PyQt6.QtWidgets import (
    QGraphicsPolygonItem,
    QGraphicsTextItem,
    QInputDialog,
    QMenu
)
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QPolygonF, QColor, QAction, QPen
# Importación del Mixin para manejo de interacciones del mouse
from Element.MouseInteractionMixin import MouseInteractionMixin

class Relation(MouseInteractionMixin, QGraphicsPolygonItem):
    """
    Clase que representa una relación en el diagrama.
    Hereda de MouseInteractionMixin para manejo de eventos del mouse
    y de QGraphicsPolygonItem para la representación gráfica.
    """
    copied_item = None  # Variable de clase para almacenar el elemento copiado

    def __init__(self,pos,scene,width=90,height=55):
        self.scene = scene
        self.id = id(self)
        # Obtener puntos
        self.x = pos.x()
        self.y = pos.y()
        self.width = width
        self.height = height
        
        points = [
            QPointF(self.x, self.y - height / 2),
            QPointF(self.x + width / 2, self.y),
            QPointF(self.x, self.y + height / 2),
            QPointF(self.x - width / 2, self.y),
        ]
        # Llama al contructor y pasa parametros
        super().__init__(QPolygonF(points))

        #Bandera primer cambio de texto
        self.primer_cambio = False

        self.setData(0,"Relation")
        self.setData(1,"Relacion")

        #self.text = QGraphicsTextItem(self.data(1), self)
        self.set_texto()

    ''' Asignat texto
    Si hay texto anterio se elimina y se crea nuevo item con
    el atributo actual
    Se obtienen medidas de textItem y se ajusta el elipseItem
    Se agrega texto y se da color'''
    def set_texto(self):
        if self.primer_cambio:
            self.scene.removeItem(self.text)
        self.text = QGraphicsTextItem(self.data(1), self)

        text_width = self.text.boundingRect().width()
        text_height = self.text.boundingRect().height()
        self.width = text_width + 40
        self.height = 55 * (self.width / 100)
        points = [
            QPointF(self.x, self.y-self.height/2),
            QPointF(self.x+self.width/2, self.y),
            QPointF(self.x, self.y+self.height/2),
            QPointF(self.x-self.width/2, self.y),
        ]
        self.setPolygon(QPolygonF(points))
        text_x_tl = self.boundingRect().topLeft().x() + ((self.width - text_width) / 2)
        text_y_tl = self.boundingRect().topLeft().y() + ((self.height - text_height) / 2)

        self.text.setPos(text_x_tl, text_y_tl)
        self.text.setDefaultTextColor(QColor(0,0,0))
        self.primer_cambio = True
    

    def contextMenuEvent(self, event):
        menu = QMenu()

        # Modificar texto
        add_text_action = QAction("Nombre", menu)
        add_text_action.triggered.connect(lambda: self.add_text())
        menu.addAction(add_text_action)

        menu.exec(event.screenPos())

    """ Metodo de texxto
    Muestra un cuadro de diálogo para añadir texto al cuadrado."""
    def add_text(self):
        text, ok = QInputDialog.getText(None, "Nombre", "Introduce el nombre:", text=self.data(1))
        if ok and text:
           self.setData(1,text)
           self.set_texto()

    """ Método para eliminar el elemento seleccionado"""
    def delete(self):
        # Eliminar las aristas asociadas
        aristas_a_eliminar = [
            arista for arista in self.scene.aristas.allAristas()
            if arista.data(1) == self or arista.data(2) == self
        ]
        for arista in aristas_a_eliminar:
            self.scene.aristas.removeArista(arista)
            self.scene.removeItem(arista)

        self.scene.nodos.removeNodo(self) # Eliminar nodo de la lista de nodos
        self.scene.removeItem(self)

    """ Método para copiar el elemento
    Guarda el elemento copiado en la variable de clase copied_item """
    def copy(self):
        Relation.copied_item = self

    """ Método para obtener la posición en x, y de la entidad con respecto a la escena """
    def get_scene_position(self):
        scene_pos = self.mapToScene(QRectF(self.boundingRect()).center())
        return (scene_pos.x(), scene_pos.y())