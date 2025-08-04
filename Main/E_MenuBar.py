from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction

class MenuBar(QMenuBar):
    def __init__(self, parent=None, scene=None):
        super().__init__(parent)
        self.scene = scene

        # Crear los menús
        archivo_menu = self.addMenu("Archivo")
        editar_menu = self.addMenu("Editar")
        ver_menu = self.addMenu("Ver")
        ayuda_menu = self.addMenu("Ayuda")

        # Crear acciones para el menú Archivo
        nuevo_action = QAction("Nuevo", self)
        abrir_action = QAction("Abrir", self)
        guardar_action = QAction("Guardar", self)
        salir_action = QAction("Salir", self)

        # Añadir acciones al menú Archivo
        archivo_menu.addAction(nuevo_action)
        archivo_menu.addAction(abrir_action)
        archivo_menu.addAction(guardar_action)
        archivo_menu.addSeparator()
        archivo_menu.addAction(salir_action)

        # Crear acciones para el menú Ver
        acercar_action = QAction("Acercar", self)
        alejar_action = QAction("Alejar", self)
        tema_action = QAction("Cambiar modo (Oscuro/claro)", self)

        # Añadir acciones al menú Ver
        ver_menu.addAction(acercar_action)
        ver_menu.addAction(alejar_action)
        ver_menu.addAction(tema_action)

        # Crear acciones para el menú Editar
        cortar_action = QAction("Cortar", self)
        copiar_action = QAction("Copiar", self)
        pegar_action = QAction("Pegar", self)

        # Añadir acciones al menú Editar
        editar_menu.addAction(cortar_action)
        editar_menu.addAction(copiar_action)
        editar_menu.addAction(pegar_action)

        # Crear acciones para el menú Ayuda
        acerca_de_action = QAction("Acerca de", self)

        # Añadir acción al menú Ayuda
        ayuda_menu.addAction(acerca_de_action)

        # Conectar la acción Salir a una función para cerrar la aplicación
        salir_action.triggered.connect(parent.close)



    

