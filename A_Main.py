import sys  
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtGui import QGuiApplication, QIcon, QSurfaceFormat
from PyQt6.QtCore import Qt
from Main.B_Scene import MainScene
from Main.C_View import MainView
from Main.D_ToolBar import ToolBar
from Main.E_MenuBar import MenuBar

def check_hardware_acceleration():
    print("\n=== Información de Aceleración por Hardware ===")
    
    # Configuración optimizada de OpenGL
    fmt = QSurfaceFormat()
    fmt.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
    fmt.setSamples(16)  # Aumentado para mejor calidad visual
    fmt.setSwapInterval(1)  # VSync activado
    fmt.setDepthBufferSize(24)  # Profundidad de buffer optimizada
    fmt.setStencilBufferSize(8)  # Buffer de stencil para efectos
    fmt.setAlphaBufferSize(8)  # Buffer alfa para transparencias
    fmt.setRedBufferSize(8)  # Configuración de color optimizada
    fmt.setGreenBufferSize(8)
    fmt.setBlueBufferSize(8)
    fmt.setStereo(False)  # Desactivar 3D estéreo si no se necesita
    QSurfaceFormat.setDefaultFormat(fmt)
    
    # Obtener información del renderizador actual
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication([])
    
    # Obtener información de la pantalla
    screen = app.primaryScreen()
    print(f"Resolución de pantalla: {screen.size().width()}x{screen.size().height()}")
    print(f"Profundidad de color: {screen.depth()}")
    print(f"Frecuencia de actualización: {screen.refreshRate()} Hz")
    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Da formato a la ventana
        self.setWindowTitle("Noche beta")
        self.setGeometry(0, 0, 1280, 720)

        #self.setWindowIcon(QIcon(r"C:\Users\eduar\OneDrive\Escritorio\Proyecto NOCHE\Icons\noche.png"))
        self.setWindowIcon(QIcon(r"Icons\noche.png"))

        # Centrar la ventana
        self.center()

        # Declarar scene y view
        self.scene = MainScene()
        self.view = MainView(self.scene)

        # Establecer self.view como widget central
        self.setCentralWidget(self.view)

        # Crear toolbar
        self.toolbar = ToolBar(self, self.scene)

        # Crear y establecer el menú bar
        menu_bar = MenuBar(self, self.scene)
        self.setMenuBar(menu_bar)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        super().keyPressEvent(event)

    def center(self): 
        # Obtener el tamaño de la ventana 
        frame_geometry = self.frameGeometry() 

        # Obtener la resolución de la pantalla y la posición del centro 
        screen = QGuiApplication.primaryScreen() 
        screen_center = screen.availableGeometry().center() 

        # Mover el rectángulo de la ventana al centro de la pantalla 
        frame_geometry.moveCenter(screen_center) 

        # Mover la ventana a la nueva posición
        self.move(frame_geometry.topLeft())

# Esto asegura que el código de ejecución de la aplicación
# solo corra si estás ejecutando este archivo directamente y
# no si lo estás importando como un módulo en otro proyecto.
if __name__ == '__main__':
    # Verificar aceleración por hardware antes de iniciar la aplicación
    check_hardware_acceleration()
    
    aplicacion = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    # .exec() es el loop principal de la aplicacion
    # sys.exit() termina la aplicacion de manera limpia
    sys.exit(aplicacion.exec())