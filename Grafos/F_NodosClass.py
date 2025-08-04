class Nodos:
    def __init__(self):
        self.nodos = []

    def setNodo(self, nodo):
        self.nodos.append(nodo)

    def allNodos(self):
        return self.nodos

    def removeNodo(self, nodo):
        if nodo in self.nodos:
            self.nodos.remove(nodo)
