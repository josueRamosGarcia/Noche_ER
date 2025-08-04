from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QMenu, QInputDialog
from PyQt6.QtGui import QPen, QAction, QColor
from Element.MouseInteractionMixin import MouseInteractionMixin

class  WeakEntity(MouseInteractionMixin, QGraphicsRectItem):

    #Variable para almacenar el elemento copiado
    copied_item = None

    def __init__(self,pos,scene,width=100,height=35):
        self.scene = scene
        self.id = id(self)
        # Calcular la posición para que el elemento esté centrado en el punto de clic
        self.x_tl = pos.x() - (width/2)
        self.y_tl = pos.y() - (height/2)
        self.height = height
        self.width = width
        # Llama al contructor y pasa parametros
        super().__init__(self.x_tl, self.y_tl, width, height)

        #Bandera primer cambio de texto
        self.primer_cambio = False

        self.borde = None

        # Datos para actualizar lineas al cambiar texto
        self.item = self

        # Da formato predeterminado
        self.setData(0,"Entidad")
        self.setData(1,"Entidad debil")          # Texto

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
        new_atribute_width = text_width + 30
        self.setRect(self.x_tl, self.y_tl, new_atribute_width, self.height)

        text_x_tl = self.x_tl + ((new_atribute_width - text_width) / 2)
        text_y_tl = self.y_tl + ((self.height - text_height) / 2)

        self.text.setPos(text_x_tl, text_y_tl)
        self.text.setDefaultTextColor(QColor(0,0,0))

        # Crea borde interno
        if self.primer_cambio:
            self.scene.removeItem(self.borde)
        self.borde = QGraphicsRectItem(
            self.boundingRect().topLeft().x()+5,
            self.boundingRect().topLeft().y()+5,
            self.boundingRect().width()-10,
            self.boundingRect().height()-10,
            self
        )
        self.borde.setPen(QPen())
        
        self.scene.identificar_lineas(self.item)
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
        WeakEntity.copied_item = self

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