from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsItemGroup, QMenu, QGraphicsTextItem
from PyQt6.QtCore import QLineF, QPointF
from PyQt6.QtGui import QPen, QAction, QIcon, QColor
import math


class LineParticipation(QGraphicsItemGroup):
    def __init__(self, items, scene):
        super().__init__(parent=None)
        self.scene = scene

        # Items
        self.item1 = items[0]
        self.pos1 = self.item1.mapToScene(self.item1.boundingRect().center())
        self.item2 = items[1]
        self.pos2 = self.item2.mapToScene(self.item2.boundingRect().center())

        # Primera línea
        self.line1 = QGraphicsLineItem(QLineF(self.pos1, self.pos2))
        self.pen = QPen(QColor(0, 0, 0), 2)  # Inicializa con color negro
        self.line1.setPen(self.pen)
        self.setZValue(-1)
        self.line1.setData(1, self.item1)
        self.line1.setData(2, self.item2)

        # Segunda línea
        self.line_2 = None
        self.cardinalidad = None

        # Agregar línea 1 al grupo
        self.addToGroup(self.line1)

        # Agregar datos
        self.setData(0, "Line P")
        self.setData(1, self.item1)
        self.setData(2, self.item2)
        self.setData(3, False)  # Participación total
        self.setData(4, self.line1)

    def boundingRect(self):
        # Devuelve el rectángulo envolvente alrededor de las líneas
        rect = self.line1.boundingRect()
        if self.line_2:
            rect = rect.united(self.line_2.boundingRect())
        return rect

    def shape(self):
        # Devuelve la forma de colisión personalizada
        path = self.line1.shape()
        if self.line_2:
            path.addPath(self.line_2.shape())
        return path

    def contextMenuEvent(self, event):
        items = self.childItems()
        for item in items:
            if item.contains(event.pos()):
                menu = QMenu()
                if not self.data(3):
                    # Modificar participacion
                    add_text_action = QAction("Total", menu)
                    add_text_action.triggered.connect(lambda: self.participacionTotal())
                    menu.addAction(add_text_action)
                else:
                    add_text_action = QAction("Parcial", menu)
                    add_text_action.triggered.connect(lambda: self.participacionParcial())
                    menu.addAction(add_text_action)

                add_cardinality = menu.addMenu("Cardinalidad")

                one_cardinality = QAction("1", add_cardinality)
                one_cardinality.triggered.connect(lambda: self.cardinality("1"))
                add_cardinality.addAction(one_cardinality)

                m_cardinality = QAction("M", add_cardinality)
                m_cardinality.triggered.connect(lambda: self.cardinality("M"))
                add_cardinality.addAction(m_cardinality)

                n_cardinality = QAction("N", add_cardinality)
                n_cardinality.triggered.connect(lambda: self.cardinality("N"))
                add_cardinality.addAction(n_cardinality)

                menu.exec(event.screenPos())

    def cardinality(self, car): # ----- MODIFICADO -----
        if self.cardinalidad is not None:
            self.scene.removeItem(self.cardinalidad)
        self.setData(6,car)
        self.cardinalidad = QGraphicsTextItem(car, self.line1)
        car_width = self.cardinalidad.boundingRect().width()
        car_height = self.cardinalidad.boundingRect().height()
        line = self.line1.line()

        if self.line1.data(1).data(0) == "Relation":
            relacion = self.line1.data(1)
            vector_x = line.p2().x() - line.p1().x() 
            vector_y = line.p2().y() - line.p1().y() 
        else:
            relacion = self.line1.data(2)
            vector_x = line.p1().x() - line.p2().x() 
            vector_y = line.p1().y() - line.p2().y() 

        rel_width = relacion.boundingRect().width()
        rel_height = relacion.boundingRect().height()
        
        vector_modulo = math.sqrt(vector_x ** 2 + vector_y ** 2)
        angulo = abs(math.degrees(math.atan(vector_y / vector_x)))

        # Relacion entre los 90 grados que oscila el anuglo y la diferencia entre width y height
        auxiliar = 90 / (rel_width / 2 - rel_height / 2)
        
        distancia = rel_width / 2 - angulo / auxiliar
        factor_escalar = (distancia + 5) / vector_modulo

        if self.line1.data(1).data(0) == "Relation":
            x = line.p1().x() + factor_escalar * vector_x
            y = line.p1().y() + factor_escalar * vector_y
        else:
            x = line.p2().x() + factor_escalar * vector_x
            y = line.p2().y() + factor_escalar * vector_y

        car_x_tl = x - car_width / 2
        car_y_tl = y - car_height / 2
        self.cardinalidad.setPos(car_x_tl, car_y_tl)

    def participacionTotal(self):
        self.setData(3, True)

        vector_x = self.line1.line().p2().x() - self.line1.line().p1().x()
        vector_y = self.line1.line().p2().y() - self.line1.line().p1().y()
        vector_modulo = math.sqrt(vector_x ** 2 + vector_y ** 2)

        dx = -3 * (vector_y / vector_modulo)
        dy = 3 * (vector_x / vector_modulo)

        x_1 = self.line1.line().p1().x() + dx
        y_1 = self.line1.line().p1().y() + dy
        x_2 = self.line1.line().p2().x() + dx
        y_2 = self.line1.line().p2().y() + dy

        self.line_2 = QLineF(QPointF(x_1, y_1), QPointF(x_2, y_2))
        self.line_2 = QGraphicsLineItem(self.line_2)
        self.line_2.setPen(self.pen)
        self.line_2.setZValue(-1)
        self.setData(5, self.line_2)
        self.addToGroup(self.line_2)
        self.scene.update()

    def participacionParcial(self):
        self.setData(3, False)
        self.scene.removeItem(self.line_2)
        self.line_2 = None
        self.scene.update()

    def select(self):
        pen = QPen(QColor(0, 0, 139), 2)  # Color azul oscuro
        self.line1.setPen(pen)
        if self.line_2:
            self.line_2.setPen(pen)

    def deselect(self):
        pen = QPen(QColor(0, 0, 0), 2)  # Color negro
        self.line1.setPen(pen)
        if self.line_2:
            self.line_2.setPen(pen)

    """ Método para eliminar la línea de participación """
    def delete(self):
        self.scene.aristas.removeArista(self)  # Remover de aristas
        self.scene.removeItem(self)
