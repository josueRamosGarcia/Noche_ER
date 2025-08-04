import math
from PyQt6.QtWidgets import QGraphicsScene, QMenu, QGraphicsEllipseItem
from PyQt6.QtGui import QColor, QBrush, QPen, QKeyEvent, QAction, QMouseEvent
from PyQt6.QtCore import Qt, QLineF, QPointF, QTimer, QTime
from Element.Atribute import Atribute
from Element.Relation import Relation
from Element.Entity import Entity
from Element.WeakEntity import WeakEntity
from Element.Line import Line
from Grafos.F_NodosClass import Nodos
from Grafos.G_AristasClass import Aristas
from Element.LineParticipation import LineParticipation
from Main.F_SelectionBox import SelectionBox


class MainScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        # Formato de escena
        self.setBackgroundBrush(QBrush(QColor(250, 250, 250)))
        self.setSceneRect(1, 1, 1278, 718)

        # Variables de escena
        self.aristas = Aristas()
        self.nodos = Nodos()
        self.element = None
        self.item_under = None
        self.items_linea = []
        self.selected_item = None  # Variable para almacenar el ítem seleccionado
        self.selection_box = None
        self.selected_items_list = []  # Lista para almacenar los elementos seleccionados temporalamente
        self.mouse_pos = None  # Variable para almacenar la posición del ratón
        self.copied_items = []  #Variable para alamacenar los elementos seleccionados (PORTAPAPELES)
        self.temp_group = None  # Agrupación temporal para mover elementos
        self.mouse_pos = QPointF(0, 0)  # Inicializar con un valor por defecto
        self.mouse_offset = QPointF()
        self.relative_positions = []  #Guarda las posiciones al copiar
        self.temp_pos = []
        self.temp_cont = 0

        self.timer = QTimer()

        # Diccionario para almacenar las posiciones de los objetos
        self.object_positions = {}

    ''' Validacion de item bajo el click
    Si no hay nada regresa None
    Si es una linea regresa None
    Si el elemnto es un objeto hijo regresa el objeto padre
    Si es un objeto padre lo regresa '''

    def validItem(self, pos):
        item_under = self.itemAt(pos, self.views()[0].transform())
        if item_under is None:
            return None
        if item_under.data(0) == "Line":
            return None
        while isinstance(item_under.parentItem(), (WeakEntity, Atribute, Entity, Relation)):
            item_under = item_under.parentItem()
        return item_under

    def store_object_position(self, item):
        if item and hasattr(item, 'id'):
            self.object_positions[item.id] = QPointF(
                *item.get_scene_position())  # Almacenar posición usando id del objeto

    def get_object_position_by_id(self, object_id):
        return self.object_positions.get(object_id, None)  # Devolver la posición almacenada por id

    def mousePressEvent(self, event):
        self.mouse_pos = event.scenePos()  # Almacenar la posición del ratón
        if event.button() == Qt.MouseButton.LeftButton and self.element is not None:
            pos = event.scenePos()
            match self.element:
                case "Atribute":
                    item = Atribute(pos, self)
                case "Relation":
                    item = Relation(pos, self)
                case "Entity":
                    item = Entity(pos, self)
                case "WeakEntity":
                    item = WeakEntity(pos, self)

            self.addItem(item)

            self.store_object_position(item)  # Almacenar la posición del objeto

            self.nodos.setNodo(item)
            self.element = None
            self.update()
        elif event.button() == Qt.MouseButton.LeftButton and self.element is None:
            self.item_under = self.validItem(event.scenePos())
            if self.item_under is None:
                # Deseleccionar todos los elementos en la escena          
                self.deselectItems()
                self.selection_box = SelectionBox(event.scenePos(), self)
                self.addItem(self.selection_box)
                self.update()

            else:
                if (len(self.selected_items_list) <= 1) or self.item_under not in self.selected_items_list:
                    self.deselectItems()
                    self.selected_items_list = [self.item_under]
                    self.selectItem(self.item_under)
                    self.update()
        super().mousePressEvent(event)  # Mover esta línea al final

    def mouseDoubleClickEvent(self, event):
        item_under = self.validItem(event.scenePos())
        if item_under is None:
            return
        if event.button() == Qt.MouseButton.LeftButton and item_under not in self.items_linea and isinstance(item_under,
                                                                                                             (Atribute,
                                                                                                              Relation,
                                                                                                              Entity,
                                                                                                              WeakEntity)):
            self.items_linea.append(item_under)
            if len(self.items_linea) == 2:
                if any(item.data(0) == "Relation" for item in self.items_linea):
                    item = LineParticipation(self.items_linea, self)
                else:
                    item = Line(self.items_linea)
                self.addItem(item)
                self.aristas.setArista(item)
                self.items_linea.clear()
        self.update()

    def expandScene(self, pos, zoomFactor):
        scene_rect = self.sceneRect()
        new_rect = scene_rect
        margin = 600 / zoomFactor
        expand = 50 / zoomFactor

        if pos.x() > scene_rect.right() - (margin + 200):
            new_rect.setRight(scene_rect.right() + expand)
        if pos.y() > scene_rect.bottom() - margin:
            new_rect.setBottom(scene_rect.bottom() + expand)
        if pos.x() < scene_rect.left() + (margin + 200):
            new_rect.setLeft(scene_rect.left() - expand)
        if pos.y() < scene_rect.top() + margin:
            new_rect.setTop(scene_rect.top() - expand)

        self.setSceneRect(new_rect)

    def expandSceneItem(self, pos, zoomFactor):
        scene_rect = self.sceneRect()
        new_rect = scene_rect
        margin = 55
        expand = 60 / zoomFactor

        if pos.x() > scene_rect.right() - margin:
            new_rect.setRight(scene_rect.right() + expand)
        if pos.y() > scene_rect.bottom() - margin:
            new_rect.setBottom(scene_rect.bottom() + expand)
        if pos.x() < scene_rect.left() + margin:
            new_rect.setLeft(scene_rect.left() - expand)
        if pos.y() < scene_rect.top() + margin:
            new_rect.setTop(scene_rect.top() - expand)

        self.setSceneRect(new_rect)

    def moveElementWithinBounds(self, item, offset):
        # Obtener la posición del elemento y los datos de la vista
        new_pos = QPointF(*item.get_scene_position())
        view = self.views()[0]
        zoomFactor = view.getZoomFactor()
        h_scrollbar = view.horizontalScrollBar()
        v_scrollbar = view.verticalScrollBar()
        visible_rect = view.getVisibleSceneRect()

        # Ajustar los márgenes según el factor de zoom para una mejor experiencia
        # Con zoom alto necesitamos márgenes más grandes para evitar trabarse en esquinas
        margin_right = 1 + item.boundingRect().width() / 2
        margin_left = 1 + item.boundingRect().width() / 2
        margin_bottom = 1 + item.boundingRect().height() / 2
        margin_top = 1 + item.boundingRect().height() / 2

        margin_factor = min(2.0, max(1.0, zoomFactor / 2.0))

        # Velocidad de desplazamiento adaptada al zoom
        # Para zoom alto, movimientos más pequeños son mejor
        SCROLL_STEP = int(max(1, min(2, 4 / (zoomFactor * zoomFactor) if zoomFactor > 1.0 else 4)))

        # Tiempo de debounce más corto para zoom alto para mejor respuesta
        DEBOUNCE_TIME = int(100 / margin_factor)  # Reduce el tiempo con zoom alto

        # Inicializar el estado si no existe
        if not hasattr(self, '_auto_scroll_state'):
            self._auto_scroll_state = {
                'direction': None,
                'last_change_time': 0,
                'active_edge': None,
                'corner_detected': False,  # Nuevo flag para detectar esquinas
                'consecutive_frames': 0  # Contador para estabilidad
            }

        # Obtener tiempo actual
        import time
        current_time = int(time.time() * 1000)

        def update_scroll():
            nonlocal current_time

            # Determinar los bordes cercanos
            is_near_right = new_pos.x() > visible_rect.right() - margin_right
            is_near_left = new_pos.x() < visible_rect.left() + margin_left
            is_near_bottom = new_pos.y() > visible_rect.bottom() - margin_bottom
            is_near_top = new_pos.y() < visible_rect.top() + margin_top

            # Detectar si estamos en una esquina
            in_corner = (is_near_left or is_near_right) and (is_near_top or is_near_bottom)

            # Verificar si estamos cerca de algún borde
            near_horizontal = is_near_left or is_near_right
            near_vertical = is_near_top or is_near_bottom

            # Tiempo transcurrido desde el último cambio de dirección
            time_since_change = current_time - self._auto_scroll_state['last_change_time']
            can_change_direction = time_since_change > DEBOUNCE_TIME

            # Determinar la nueva dirección si es necesario
            new_direction = None
            new_edge = None

            # Gestión especial de esquinas
            if in_corner:
                # Si es la primera vez que detectamos la esquina
                if not self._auto_scroll_state['corner_detected']:
                    self._auto_scroll_state['corner_detected'] = True
                    # Si no hay dirección activa, elegir la más cercana al borde
                    if not self._auto_scroll_state['direction']:
                        # Calcular distancias al borde para decidir qué dirección priorizar
                        dist_right = abs(new_pos.x() - visible_rect.right())
                        dist_left = abs(new_pos.x() - visible_rect.left())
                        dist_bottom = abs(new_pos.y() - visible_rect.bottom())
                        dist_top = abs(new_pos.y() - visible_rect.top())

                        # Determinar qué borde está más cerca
                        min_h_dist = min(dist_right, dist_left)
                        min_v_dist = min(dist_bottom, dist_top)

                        if min_h_dist <= min_v_dist:
                            new_direction = 'horizontal'
                            new_edge = 'right' if dist_right < dist_left else 'left'
                        else:
                            new_direction = 'vertical'
                            new_edge = 'bottom' if dist_bottom < dist_top else 'top'

                        self._auto_scroll_state['last_change_time'] = current_time
                    else:
                        # Mantener la dirección actual en la esquina
                        new_direction = self._auto_scroll_state['direction']
                        new_edge = self._auto_scroll_state['active_edge']
                else:
                    # Ya habíamos detectado la esquina, mantener la dirección
                    new_direction = self._auto_scroll_state['direction']
                    new_edge = self._auto_scroll_state['active_edge']

                    # Incrementar el contador de frames consecutivos
                    self._auto_scroll_state['consecutive_frames'] += 1

                    # Si llevamos demasiado tiempo en la misma dirección en una esquina,
                    # considerar cambiar para evitar bloqueos
                    if self._auto_scroll_state['consecutive_frames'] > 30 and can_change_direction:
                        if new_direction == 'horizontal':
                            new_direction = 'vertical'
                            new_edge = 'bottom' if is_near_bottom else 'top'
                        else:
                            new_direction = 'horizontal'
                            new_edge = 'right' if is_near_right else 'left'

                        self._auto_scroll_state['consecutive_frames'] = 0
                        self._auto_scroll_state['last_change_time'] = current_time
            else:
                # No estamos en una esquina, resetear flag
                self._auto_scroll_state['corner_detected'] = False
                self._auto_scroll_state['consecutive_frames'] = 0

                # Lógica normal para bordes no en esquina
                if self._auto_scroll_state['direction'] == 'horizontal':
                    if near_horizontal:
                        new_direction = 'horizontal'
                        new_edge = 'right' if is_near_right else 'left'
                    elif can_change_direction and near_vertical:
                        new_direction = 'vertical'
                        new_edge = 'bottom' if is_near_bottom else 'top'
                        self._auto_scroll_state['last_change_time'] = current_time
                elif self._auto_scroll_state['direction'] == 'vertical':
                    if near_vertical:
                        new_direction = 'vertical'
                        new_edge = 'bottom' if is_near_bottom else 'top'
                    elif can_change_direction and near_horizontal:
                        new_direction = 'horizontal'
                        new_edge = 'right' if is_near_right else 'left'
                        self._auto_scroll_state['last_change_time'] = current_time
                else:
                    # Si no hay dirección activa, priorizar horizontal
                    if near_horizontal:
                        new_direction = 'horizontal'
                        new_edge = 'right' if is_near_right else 'left'
                        self._auto_scroll_state['last_change_time'] = current_time
                    elif near_vertical:
                        new_direction = 'vertical'
                        new_edge = 'bottom' if is_near_bottom else 'top'
                        self._auto_scroll_state['last_change_time'] = current_time

            # Actualizar el estado actual
            self._auto_scroll_state['direction'] = new_direction
            self._auto_scroll_state['active_edge'] = new_edge

            # Calcular el paso actual basado en el zoom y si estamos en una esquina
            current_step = SCROLL_STEP
            if in_corner:
                # Reducir aún más el paso en las esquinas para mayor precisión
                current_step = max(1, int(current_step * 0.5))

            # Aplicar el desplazamiento según la dirección y borde activo
            if new_direction == 'horizontal':
                if new_edge == 'right' and h_scrollbar.value() < h_scrollbar.maximum():
                    h_scrollbar.setValue(int(h_scrollbar.value() + current_step))
                elif new_edge == 'left' and h_scrollbar.value() > h_scrollbar.minimum():
                    h_scrollbar.setValue(int(h_scrollbar.value() - current_step))
            elif new_direction == 'vertical':
                if new_edge == 'bottom' and v_scrollbar.value() < v_scrollbar.maximum():
                    v_scrollbar.setValue(int(v_scrollbar.value() + current_step))
                elif new_edge == 'top' and v_scrollbar.value() > v_scrollbar.minimum():
                    v_scrollbar.setValue(int(v_scrollbar.value() - current_step))

            # Forzar actualización inmediata
            view.viewport().update()

        # Ajustar el intervalo según el factor de zoom
        timer_interval = max(8, int(16 / zoomFactor)) if zoomFactor > 1.0 else 16
        self.timer.singleShot(timer_interval, update_scroll)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.selection_box is not None:
            self.selection_box.update_size(event.scenePos())
        elif event.buttons() == Qt.MouseButton.LeftButton and self.selected_items_list:
            # Calcular el desplazamiento del ratón
            self.mouse_offset = event.scenePos() - self.mouse_pos
            self.mouse_pos = event.scenePos()

            # Obtener el rectángulo visible
            visible_rect = self.views()[0].getVisibleSceneRect()

            if len(self.selected_items_list) == 1:
                # Lógica original para un solo elemento
                item = self.selected_items_list[0]
                if isinstance(item, (WeakEntity, Atribute, Entity, Relation)):
                    # Calcular la nueva posición potencial
                    new_x = item.pos().x() + self.mouse_offset.x()
                    new_y = item.pos().y() + self.mouse_offset.y()

                    item_pos = QPointF(*item.get_scene_position())
                    iniPos = self.get_object_position_by_id(item.id)

                    # Obtener el tamaño del elemento
                    item_rect = item.boundingRect()
                    item_width = item_rect.width()
                    item_height = item_rect.height()

                    # Calcular márgenes de seguridad basados en el tamaño del elemento
                    margin_right = item_width / 2  # 50% del ancho del elemento
                    margin_left = item_width / 2
                    margin_bottom = item_height * 0.5  # 50% del alto del elemento
                    margin_top = item_height * 0.5

                    temp_x = iniPos.x().__ceil__()
                    temp_y = iniPos.y().__ceil__()

                    # Aplicar restricciones suavemente
                    # Restricción horizontal
                    if new_x + temp_x > visible_rect.right() - margin_right:
                        new_x = visible_rect.right() - temp_x - margin_right
                    elif new_x + temp_x < visible_rect.left() + margin_left:
                        new_x = visible_rect.left() - temp_x + margin_left

                    # Restricción vertical
                    if new_y + temp_y > visible_rect.bottom() - margin_bottom:
                        new_y = visible_rect.bottom() - margin_bottom - temp_y
                    elif new_y + temp_y < visible_rect.top() + margin_top:
                        new_y = visible_rect.top() + margin_top - temp_y

                    # Aplicar la nueva posición
                    item.setPos(new_x, new_y)
                    self.identificar_lineas(item)
                    self.moveElementWithinBounds(item, self.mouse_offset)
            else:
                # Nueva lógica para múltiples elementos
                selection_rect = None
                for item in self.selected_items_list:
                    if isinstance(item, (WeakEntity, Atribute, Entity, Relation)):
                        item_rect = item.sceneBoundingRect()
                        if selection_rect is None:
                            selection_rect = item_rect
                        else:
                            selection_rect = selection_rect.united(item_rect)

                if selection_rect:
                    # Calcular márgenes de seguridad basados en el tamaño total de la selección
                    margin_right = selection_rect.width() * 0.25  # 25% del ancho total
                    margin_left = selection_rect.width() * 0.25
                    margin_bottom = selection_rect.height() * 0.25  # 25% del alto total
                    margin_top = selection_rect.height() * 0.25

                    # Calcular la nueva posición potencial del rectángulo de selección
                    new_rect = selection_rect.translated(self.mouse_offset)

                    # Verificar límites y ajustar el desplazamiento si es necesario
                    adjusted_offset = self.mouse_offset

                    # Restricción horizontal
                    if new_rect.right() > visible_rect.right():
                        adjusted_offset.setX(visible_rect.right() - selection_rect.right())
                    elif new_rect.left() < visible_rect.left():
                        adjusted_offset.setX(visible_rect.left() - selection_rect.left())

                    # Restricción vertical
                    if new_rect.bottom() > visible_rect.bottom():
                        adjusted_offset.setY(visible_rect.bottom() - selection_rect.bottom())
                    elif new_rect.top() < visible_rect.top():
                        adjusted_offset.setY(visible_rect.top() - selection_rect.top())

                    # Aplicar el desplazamiento ajustado a todos los elementos
                    for item in self.selected_items_list:
                        if isinstance(item, (WeakEntity, Atribute, Entity, Relation)):
                            new_pos = item.pos() + adjusted_offset
                            item.setPos(new_pos)
                            self.identificar_lineas(item)
                            self.moveElementWithinBounds(item, adjusted_offset)

            self.update()
        else:
            super().mouseMoveEvent(event)
        self.update()

    def mouseReleaseEvent(self, event):
        if self.selection_box is not None:
            self.selection_box.finalize()
            self.selection_box = None
        self.item_under = None
        super().mouseReleaseEvent(event)
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        selected_items = self.selected_items_list
        if event.key() == Qt.Key.Key_Delete:
            if len(selected_items) > 0:
                self.delete_selection()
        elif event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if len(selected_items) > 0:
                self.copySelected()
        elif event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if len(self.copied_items) > 0:
                self.pasteSelected(self.mouse_pos)

        super().keyPressEvent(event)  # Mover esta línea al final
        self.update()

    def identificar_lineas(self, item):
        aristas = [
            arista for arista in self.aristas.allAristas()
            if item == arista.data(1) or item == arista.data(2)
        ]
        for arista in aristas:
            if arista.data(0) == "Line":
                self.moverLinea(item, arista)
            else:
                car = arista.data(6)
                if car is not None:
                    arista.cardinality(car)
                if arista.data(3):
                    self.moverLinea(item, arista.data(4))
                    self.moverLineaP(arista.data(4), arista.data(5))
                else:
                    self.moverLinea(item, arista.data(4))

    def moverLinea(self, item_under, arista):
        if item_under == arista.data(1):
            xy1 = item_under.mapToScene(item_under.boundingRect().center())
            xy2 = arista.line().p2()
        elif item_under == arista.data(2):
            xy1 = arista.line().p1()
            xy2 = item_under.mapToScene(item_under.boundingRect().center())
        line = QLineF(xy1, xy2)
        arista.setLine(line)

    def moverLineaP(self, linea1, linea2):
        vector_x = linea1.line().p2().x() - linea1.line().p1().x()
        vector_y = linea1.line().p2().y() - linea1.line().p1().y()
        vector_modulo = math.sqrt(vector_x ** 2 + vector_y ** 2)

        dx = -3 * (vector_y / vector_modulo)
        dy = 3 * (vector_x / vector_modulo)

        x_1 = linea1.line().p1().x() + dx
        y_1 = linea1.line().p1().y() + dy
        x_2 = linea1.line().p2().x() + dx
        y_2 = linea1.line().p2().y() + dy

        line = QLineF(QPointF(x_1, y_1), QPointF(x_2, y_2))
        linea2.setLine(line)

    def selectItem(self, item):
        if item is not None and isinstance(item, (Atribute, Relation, Entity, WeakEntity)):
            pen = QPen(QColor(0, 0, 139), 2)  # Color azul oscuro
            item.setPen(pen)
            item.setSelected(True)
        elif isinstance(item, LineParticipation):
            item.select()

    def deselectItems(self):
        for item in self.selected_items_list:
            if hasattr(item, 'setPen') and callable(item.setPen) and isinstance(item, (Entity, Atribute, WeakEntity,
                                                                                       Relation)):
                pen = QPen(QColor(0, 0, 0), 1)  # Color negro
                item.setPen(pen)
            elif isinstance(item, (Line)):
                pen = QPen(QColor(0, 0, 0), 2)  # Color negro
                item.setPen(pen)
            elif isinstance(item, (LineParticipation)):
                item.deselect()
            item.setSelected(False)

    #Checar opciones del menú contextual ---------------------------------------------------------------------

    def contextMenuEvent(self, event):
        item_under = self.itemAt(event.scenePos(), self.views()[0].transform())
        selected_items = self.selected_items_list

        if item_under is None and len(selected_items) > 0:
            # Menú contextual para elementos seleccionados
            menu = QMenu()
            delete_action = QAction("Eliminar Selección", menu)
            delete_action.triggered.connect(self.delete_selection)
            menu.addAction(delete_action)
            menu.exec(event.screenPos())
        elif item_under is None:
            # Menú contextual estándar
            menu = QMenu()
            # Acción para añadir una entidad
            add_entity_action = QAction("Añadir Entidad", menu)
            add_entity_action.triggered.connect(lambda: self.addEntity(event.scenePos()))
            menu.addAction(add_entity_action)
            # Acción para pegar el elemento copiado
            paste_action = QAction("Pegar", menu)
            paste_action.triggered.connect(lambda: self.paste(event.scenePos()))
            menu.addAction(paste_action)
            # Beta mostrar grafo
            mostrar_grafo = QAction("Mostrar Grafo", menu)
            mostrar_grafo.triggered.connect(lambda: self.mostrar_grafo_b())
            menu.addAction(mostrar_grafo)
            # Mostrar menu
            menu.exec(event.screenPos())
        else:
            super(MainScene, self).contextMenuEvent(
                event)  # Permitir que las entidades manejen su propio menú contextual

    """ def mostrar_grafo_b(self):
        for nodo in self.nodos.allNodos():
            print(nodo.data(1))
        print("-----------------") """

    # -------------------- INICIO GRAFO --------------------
    def mostrar_grafo_b(self):
        entidades = []
        relaciones = []

        for nodo in self.nodos.allNodos():
            if nodo.data(0) == "Entity":
                entidades.append(nodo)
            elif nodo.data(0) == "Relation":
                relaciones.append(nodo)

        for entidad in entidades:
            print(self.entidadMD(entidad))

    def entidadMD(self, entidad):
        llave = None
        atributos = []

        # Get entity conexions
        aristas = [
            arista for arista in self.aristas.allAristas()
            if entidad == arista.data(1) or entidad == arista.data(2)
        ]

        # Filtrar atributos
        for arista in aristas:
            if arista.data(1).data(0) == "Atribute":
                atributos.append(arista.data(1))
            elif arista.data(2).data(0) == "Atribute":
                atributos.append(arista.data(2))

        print(atributos)

        # Obtener atributos llaves
        for atributo in atributos:
            if atributo.data(2) == "Llave":
                llave = atributo
                atributos.remove(atributo)

        # Construir string
        string = f"{entidad.data(1)} ({llave.data(1)}(PK), "

        for atributo in atributos:
            compuesto = self.identificarAtributoC(atributo)
            if compuesto != False:
                string += compuesto
            else:
                string += f"{atributo.data(1)}, "

        return string[:-2] + ")"

    def identificarAtributoC(self, atributo):
        atributos = []

        aristasP = [
            arista for arista in self.aristas.allAristas()
            if atributo == arista.data(1) or atributo == arista.data(2)
        ]

        if len(aristasP) == 1:
            return False

        aristas = [
            arista for arista in aristasP
            if arista.data(1).data(0) == "Atribute"
               and arista.data(2).data(0) == "Atribute"
        ]

        for arista in aristas:
            if arista.data(1) != atributo:
                atributos.append(arista.data(1))
            elif arista.data(2) != atributo:
                atributos.append(arista.data(2))

        string = ""
        for atributo in atributos:
            string += f"{atributo.data(1)}, "

        return string

    def identificarRelaciones(self):
        pass

    # -------------------- FIN GRAFO --------------------

    def delete_selection(self):
        selected_items = self.selected_items_list
        for item in selected_items:
            if isinstance(item, (Atribute, Relation, Entity, WeakEntity, LineParticipation)):
                item.delete()
                self.items_linea.clear()
            self.removeItem(item)
        self.selected_items_list.clear()

    def addEntity(self, pos):
        item = Entity(pos, self)
        self.addItem(item)
        self.nodos.setNodo(item)

    def copySelected(self):
        self.copied_items = [item for item in self.selected_items_list if hasattr(item, 'copy')]
        print(self.selected_items_list)
        if self.copied_items:
            base_item = self.copied_items[0]
            if isinstance(base_item, (Atribute, Relation, Entity, WeakEntity)):
                base_pos = QPointF(*base_item.get_scene_position())
                self.relative_positions = [QPointF(*item.get_scene_position()) - base_pos for item in self.copied_items]

            # Guardar las aristas
            self.copied_aristas = [
                arista for arista in self.aristas.allAristas()
                if arista.data(1) in self.copied_items and arista.data(2) in self.copied_items
            ]

            # Guardar información adicional sobre la participación total
            self.lines_participation_total = {}
            for arista in self.copied_aristas:
                if isinstance(arista, LineParticipation) and arista.data(3):  # Si es participación total
                    self.lines_participation_total[arista] = arista.data(5)

        for item in self.copied_items:
            if isinstance(item, (Atribute, Relation, Entity, WeakEntity)):
                pos = item.get_scene_position()

    def pasteSelected(self, position):
        if not position or not self.copied_items:
            return

        base_pos = QPointF(self.relative_positions[0])  # Usar la primera posición guardada como base de referencia
        offset = position - base_pos  # Calcular el desplazamiento desde la posición base

        item_map = {}  # Para mapear los elementos copiados con sus nuevos elementos pegados
        pasted_items = []  # Lista para almacenar los nuevos elementos pegados

        for item, rel_pos in zip(self.copied_items, self.relative_positions):
            new_pos = position + rel_pos
            if isinstance(item, Entity):
                new_item = Entity(new_pos, self)
            elif isinstance(item, Atribute):
                new_item = Atribute(new_pos, self)
            elif isinstance(item, WeakEntity):
                new_item = WeakEntity(new_pos, self)
            elif isinstance(item, Relation):
                new_item = Relation(new_pos, self)
            else:
                continue  # No copiar si el tipo no es soportado
            new_item.setData(1, item.data(1))  # Copiar el texto
            new_item.set_texto()
            self.addItem(new_item)
            self.nodos.setNodo(new_item)
            self.store_object_position(new_item)  # Guardar la posición del nuevo elemento
            item_map[item] = new_item  # Guardar el mapeo del elemento original al nuevo elemento
            pasted_items.append(new_item)

        # Volver a crear las aristas utilizando el mapeo
        for arista in self.copied_aristas:
            new_item1 = item_map.get(arista.data(1))
            new_item2 = item_map.get(arista.data(2))
            if new_item1 and new_item2:
                if isinstance(arista, LineParticipation):
                    new_arista = LineParticipation([new_item1, new_item2], self)
                    # Restaurar participación total si aplica
                    if arista in self.lines_participation_total:
                        new_arista.participacionTotal()
                else:
                    new_arista = Line([new_item1, new_item2])
                self.addItem(new_arista)
                self.aristas.setArista(new_arista)

        self.copied_items = []
        self.relative_positions = []
        self.copied_aristas = []

        # Seleccionar todos los nuevos elementos pegados
        self.selected_items_list = pasted_items
        for item in pasted_items:
            self.selectItem(item)

    def receive_selected_items(self, selected_items):
        self.selected_items_list = [item for item in selected_items if
                                    isinstance(item, (Atribute, Relation, Entity, WeakEntity, Line, LineParticipation))]

        for item in self.selected_items_list:
            self.selectItem(item)
