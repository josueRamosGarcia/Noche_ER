from PyQt6.QtWidgets import QToolBar, QWidget, QSizePolicy
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QSize, Qt

class ToolBar:
    def __init__(self, mainWindow, scene):
        # Variables de toolbar
        self.mainWindow = mainWindow
        self.scene = scene
        self.is_alternate_icon = False  # Variable para seguir el estado del icono

        # Barra de herramientas lateral con íconos para seleccionar figuras
        toolbar = QToolBar("Herramientas", self.mainWindow)
        toolbar.setIconSize(QSize(80, 60))
        
        # Área donde se va a designar
        self.mainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar)
    
        # Color de fondo
        toolbar.setStyleSheet("QToolBar { background-color: #D3D3D3; }")

        ''' Crear acciones para cada figura
        1- Crea icono
        2- Crea acción con icono, nombre y ventana
        3- Asigna método a la acción
        4- Añade la acción al toolbar'''
        icon = QIcon(r"Icons\Entity.png")
        entity_action = QAction(icon, "Entity", toolbar)
        entity_action.triggered.connect(lambda:self.select_element("Entity"))
        entity_action.triggered.connect(self.scene.deselectItems)
        toolbar.addAction(entity_action)

        icon = QIcon(r"Icons\WeakEntity.png")
        weak_entity_action = QAction(icon, "WeakEntity", toolbar)
        weak_entity_action.triggered.connect(lambda:self.select_element("WeakEntity"))
        weak_entity_action.triggered.connect(self.scene.deselectItems)
        toolbar.addAction(weak_entity_action)

        icon = QIcon(r"Icons\Atribute.png")
        atribute_action = QAction(icon, "Atribute", toolbar)
        atribute_action.triggered.connect(lambda:self.select_element("Atribute"))
        atribute_action.triggered.connect(self.scene.deselectItems)
        toolbar.addAction(atribute_action)

        icon = QIcon(r"Icons\Relation.png")
        relation_action = QAction(icon, "Relation", toolbar)
        relation_action.triggered.connect(lambda:self.select_element("Relation"))
        relation_action.triggered.connect(self.scene.deselectItems)
        toolbar.addAction(relation_action)

        # Crear y agregar un widget elástico
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)

        # Crear y agregar el nuevo botón al final de la barra de herramientas
        self.icon1 = QIcon(r"Icons\sol.png")
        self.icon2 = QIcon(r"Icons\luna.png")
        self.new_action = QAction(self.icon1, "Change Mode", toolbar)
        self.new_action.triggered.connect(self.change_mode)
        self.new_action.triggered.connect(self.scene.deselectItems)
        toolbar.addAction(self.new_action)

        # Añadir botón de reset view
        reset_action = QAction("⟳", toolbar)  # Símbolo Unicode más grande para reset
        reset_action.setToolTip("Reset View")  # Tooltip para mostrar al pasar el mouse
        reset_action.triggered.connect(self.reset_view)
        toolbar.addAction(reset_action)

    def select_element(self, element):
        self.scene.element = element

    def change_mode(self):
        # Código para cambiar el fondo de la escena
        #self.scene.setBackgroundBrush(Qt.GlobalColor.darkGray)
        # Cambiar icono
        if self.is_alternate_icon:
            self.new_action.setIcon(self.icon1)
            self.scene.setBackgroundBrush(Qt.GlobalColor.white)
        else:
            self.new_action.setIcon(self.icon2)
            self.scene.setBackgroundBrush(Qt.GlobalColor.darkGray)
        self.is_alternate_icon = not self.is_alternate_icon

    def reset_view(self):
        self.scene.views()[0].resetView()
