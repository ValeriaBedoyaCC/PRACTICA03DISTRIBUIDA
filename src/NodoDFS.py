import simpy
from Nodo import *
from Canales.CanalRecorridos import *

# La unidad de tiempo
TICK = 1


class NodoDFS(Nodo):

    def __init__(self, id_nodo, vecinos, canal_entrada, canal_salida):
        ''' Constructor de nodo que implementa el algoritmo DFS. '''
        super().__init__(id_nodo, vecinos, canal_entrada, canal_salida)
        self.padre = id_nodo  # Convención inicial exigida en las instrucciones
        self.hijos = []
        self.visited = set()
        self.visitado = False  # Bandera interna para detectar si ya fue activado por un GO

    def dfs(self, env):
        ''' Algoritmo DFS secuencial/descentralizado determinista. '''
        # Si es el nodo raíz distinguido (nodo 0)
        if self.id_nodo == 0:
            self.padre = self.id_nodo
            self.hijos = []
            self.visited = set()
            self.visitado = True

            candidatos = [v for v in self.vecinos if v not in self.visited]
            if candidatos:
                k = min(candidatos)
                yield self.canal_salida.envia(("GO", self.id_nodo), [k])

        while True:
            msg = yield self.canal_entrada.get()
            tipo = msg[0]

            if tipo == "GO":
                _, j = msg
                if not self.visitado:
                    self.visitado = True
                    self.padre = j
                    self.hijos = []
                    self.visited = {j}

                    if self.visited == set(self.vecinos):
                        yield self.canal_salida.envia(("BACK", "yes", self.id_nodo), [j])
                    else:
                        candidatos = [v for v in self.vecinos if v not in self.visited]
                        k = min(candidatos)
                        yield self.canal_salida.envia(("GO", self.id_nodo), [k])
                else:
                    yield self.canal_salida.envia(("BACK", "no", self.id_nodo), [j])

            elif tipo == "BACK":
                _, resp, j = msg
                if resp == "yes":
                    if j not in self.hijos:
                        self.hijos.append(j)
                self.visited.add(j)

                if self.visited == set(self.vecinos):
                    if self.padre == self.id_nodo:
                        # Terminación global (nodo raíz termina el algoritmo)
                        break
                    else:
                        # Terminación local
                        yield self.canal_salida.envia(("BACK", "yes", self.id_nodo), [self.padre])
                else:
                    candidatos = [v for v in self.vecinos if v not in self.visited]
                    k = min(candidatos)
                    yield self.canal_salida.envia(("GO", self.id_nodo), [k])