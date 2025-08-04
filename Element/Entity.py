from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QMenu, QInputDialog
from PyQt6.QtGui import QColor, QAction, QMouseEvent, QBrush
from PyQt6.QtCore import QPointF, Qt
from Element.MouseInteractionMixin import MouseInteractionMixin
#from Main.B_Scene import MainScene

class Entity(MouseInteractionMixin, QGraphicsRectItem):
    copied_item = None  # Variable de clase para almacenar el elemento copiado

    def __init__(self, pos, scene, width=100, height=35):
        self.scene = scene
        self.id = id(self)
        # Calcular la posición para que el elemento esté centrado en el punto de clic
        self.x_tl = pos.x() - (width/2)
        self.y_tl = pos.y() - (height/2)
        self.height = height
        self.width = width
        super().__init__(self.x_tl, self.y_tl, width, height)

        # Datos para actualizar lineas al cambiar texto
        self.item = self

        #Bandera primer cambio de texto
        self.primer_cambio = False

        self.setData(0, "Entity")
        self.setData(1,"Entidad")          # Texto

        #self.text = QGraphicsTextItem(self.data(1), self)
        self.set_texto()

    ''' Asignat texto
    Si hay texto anterior se elimina y se crea nuevo item con
    el atributo actual
    Se obtienen medidas de textItem y se ajusta el rectángulo
    Se agrega texto y se da color'''
    def set_texto(self):
        if self.primer_cambio:
            self.scene.removeItem(self.text)
        self.text = QGraphicsTextItem(self.data(1), self)

        text_width = self.text.boundingRect().width()
        text_height = self.text.boundingRect().height()
        new_atribute_width = text_width + 30
        
        # Mantener el centro del elemento
        center_x = self.rect().center().x()
        center_y = self.rect().center().y()
        new_x = center_x - (new_atribute_width/2)
        new_y = center_y - (self.rect().height()/2)
        
        self.setRect(new_x, new_y, new_atribute_width, self.rect().height())

        text_x_tl = new_x + ((new_atribute_width - text_width) / 2)
        text_y_tl = new_y + ((self.rect().height() - text_height) / 2)

        self.text.setPos(text_x_tl, text_y_tl)
        self.text.setDefaultTextColor(QColor(0, 0, 0))
        self.scene.identificar_lineas(self)
        self.primer_cambio = True


    """ Menu contextual
    Evento que se activa al hacer clic derecho en el item
    Se crea menu
    Se añaden las acciones
    """
    def contextMenuEvent(self, event):
        menu = QMenu()

        # Modificar texto
        add_text_action = QAction("Nombre", menu)
        add_text_action.triggered.connect(lambda: self.add_text())
        menu.addAction(add_text_action)

        # Submenu modificar tipo de atributo
        atribute_type_menu = menu.addMenu("Tipo de atributo")

        atribute_derivade = QAction("Derivado", atribute_type_menu)
        atribute_derivade.triggered.connect(lambda: self.atribute_derivade())
        atribute_type_menu.addAction(atribute_derivade)

        atribute_simple = QAction("Simple", atribute_type_menu)
        atribute_simple.triggered.connect(lambda: self.atribute_simple())
        atribute_type_menu.addAction(atribute_simple)

        atribute_llave = QAction("Llave", atribute_type_menu)
        atribute_llave.triggered.connect(lambda: self.atribute_llave())
        atribute_type_menu.addAction(atribute_llave)

        # Copiar
        copy_action = QAction("Copiar", menu)
        copy_action.triggered.connect(lambda: self.copy())
        menu.addAction(copy_action)

        # Eliminar
        delete_action = QAction("Eliminar", menu)
        delete_action.triggered.connect(lambda: self.delete())
        menu.addAction(delete_action)

        menu.exec(event.screenPos())

    """ Metodo de texxto
    Muestra un cuadro de diálogo para añadir texto al cuadrado."""
    def add_text(self):
        text, ok = QInputDialog.getText(None, "Nombre", "Introduce el nombre:", text=self.data(1))
        if ok and text:
           self.setData(1,text)
           self.set_texto()

    """ Método para copiar el elemento
    Guarda el elemento copiado en la variable de clase copied_item """
    def copy(self):
        Entity.copied_item = self

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

    """ Método para obtener la posición en x, y de la entidad con respecto a la escena """
    def get_scene_position(self):
        scene_pos = self.mapToScene(self.rect().center())
        return (scene_pos.x(), scene_pos.y())





    
