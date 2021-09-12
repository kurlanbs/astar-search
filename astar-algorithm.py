import pygame
import math
from queue import PriorityQueue
import time

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Búsqueda heurística con A*")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

"""Clase spot define los atributos y funciones de los nodos 
en árbol representado por una tabla(grid) 
"""
class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = PURPLE

	def make_path(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False

"""Función que implementa la distancia Manhattan o geometría del taxista
	P1: Punto inicial 
	P2: Punto final 
	Return: Distancia entre P1 y P2
"""
def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		print("Ruta:{}".format(current.get_pos()))
		time.sleep(0.5)
		draw()

"""Función que implementa el algoritmo A* con las siguientes variables:

	count: Contador para realizar el recorrido de cada nodo
	open_set: Cola priorizada que se encarga de almacenar los nodos abiertos
	g_score: Costo real de llegar del nodo inicial (param: start) al destino (g_score[current]+1)
	f_score: Costo real de llegar al nodo destino (g_score[current]+1) más el costo estimado de llegar a nodo meta(param:end)
"""
def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	step_find=0
	print("**Origen {} -> destino {}".format(start.get_pos(),end.get_pos(),f_score[start]))
	
	while not open_set.empty():
		step_find=step_find+1
		print("Paso: {}".format(step_find))
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)
		
		if current == end:
			print("Objetivo encontrado")
			print("Destino:{}".format(end.get_pos()))
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		print("Origen:{}".format(current.get_pos()))
		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				temp_h_score=h(neighbor.get_pos(), end.get_pos())
				f_score[neighbor] = temp_g_score + temp_h_score
				
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()
					print("open  node: P{}|F({})=g({})+h({})".format(neighbor.get_pos(),f_score[neighbor],temp_g_score,temp_h_score))
		draw()

		if current != start:
			current.make_closed()
			print("close node: P{}".format(current.get_pos()))
			time.sleep(0.5)

	return False

"""Funciones auxiliares para animar el algoritmo
"""
def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)
	return grid

def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()

"""Función principal, se encarga de ejecutar el problema planteado sobre el algoritmo de búsqueda.
El Problema es dividido de manera manual en 6 problemas independientes que corresponden a la siguiente ejecución:
	Subproblema 0: Que parte de las posiciones definidas en el ejercicio, en este punto se considera como destino al punto (0,2). 
				   Para ejecutar el recorrido presionar la barra espaciadora.
	Subproblema 1: Carga presionando la TECLA 1, que parte del objetivo del subproblema0 (0,2) y tiene como destino (2,3). 
				   Para ejecutar el recorrido ejecutar la barra espaciadora.
	Subproblema 2: Carga presionando la TECLA 2, que parte del objetivo del subproblema1 (2,3) y tiene como destino (0,0). 
				   Para ejecutar el recorrido ejecutar la barra espaciadora.
	Subproblema 3: Carga presionando la TECLA 3, que parte del objetivo del subproblema2 (0,0) y tiene como destino (3,3). 
				   Para ejecutar el recorrido ejecutar la barra espaciadora.
	Subproblema 4: Carga presionando la TECLA 4, que parte del objetivo del subproblema3 (3,3) y tiene como destino (3,0). 
				   Para ejecutar el recorrido ejecutar la barra espaciadora.
	Subproblema 5: Carga presionando la TECLA 5, que parte del objetivo del subproblema4 (3,0) y tiene como destino (1,3). 
	               Para ejecutar el recorrido ejecutar la barra espaciadora.
	Final: Carga presionando la TECLA 6, muestra el resultado final.
"""
def main(win, width):
	ROWS = 4
	grid = make_grid(ROWS, width)
	start = None
	end = None
	run = True
	count_goal=0

	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			##inicial
			if count_goal == 0:
				print("\n**Subproblema 0")
				spot = grid[2][2]
				start = spot
				start.make_start()

				spot = grid[0][2]
				end = spot
				end.make_end()

				spot = grid[1][0]
				spot.make_barrier()
				spot = grid[1][1]
				spot.make_barrier()
				spot = grid[0][0]
				spot.make_barrier()
				spot = grid[3][0]
				spot.make_barrier()
				count_goal=count_goal+1

			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)
							
					algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
	
				##M2	
				if event.key == pygame.K_1:
					print("\n**Subproblema 1")
					start = None
					end = None
					grid = make_grid(ROWS, width)

					spot = grid[0][2]
					start = spot
					start.make_start()

					spot = grid[2][3]
					end = spot
					end.make_end()

					spot = grid[0][0]
					spot.make_barrier()
					spot = grid[1][0]
					spot.make_barrier()
					spot = grid[1][1]
					spot.make_barrier()
					spot = grid[3][0]
					spot.make_barrier()
					
				#M1
				if event.key == pygame.K_2:
					print("\n**Subproblema 2")
					start = None
					end = None
					grid = make_grid(ROWS, width)

					spot = grid[2][3]
					start = spot
					start.make_start()

					spot = grid[0][0]
					end = spot
					end.make_end()

					spot = grid[1][0]
					spot.make_barrier()
					spot = grid[1][1]
					spot.make_barrier()
					spot = grid[3][0]
					spot.make_barrier()


				if event.key == pygame.K_3:
					print("\n**Subproblema 3")
					start = None
					end = None
					grid = make_grid(ROWS, width)

					spot = grid[0][0]
					start = spot
					start.make_start()

					spot = grid[3][3]
					end = spot
					end.make_end()

					spot = grid[1][0]
					spot.make_barrier()
					spot = grid[1][1]
					spot.make_barrier()
					spot = grid[2][3]
					spot.make_barrier()
					spot = grid[3][0]
					spot.make_barrier()

				if event.key == pygame.K_4:
					print("\n**Subproblema 4")
					start = None
					end = None
					grid = make_grid(ROWS, width)

					spot = grid[3][3]
					start = spot
					start.make_start()

					spot = grid[3][0]
					end = spot
					end.make_end()

					spot = grid[1][0]
					spot.make_barrier()
					spot = grid[1][1]
					spot.make_barrier()
					spot = grid[2][3]
					spot.make_barrier()

				if event.key == pygame.K_5:
					print("\n**Subproblema 5")
					start = None
					end = None
					grid = make_grid(ROWS, width)

					spot = grid[3][0]
					start = spot
					start.make_start()

					spot = grid[1][3]
					end = spot
					end.make_end()

					spot = grid[1][0]
					spot.make_barrier()
					spot = grid[1][1]
					spot.make_barrier()
					spot = grid[2][3]
					spot.make_barrier()
					spot = grid[3][3]
					spot.make_barrier()

				if event.key == pygame.K_6:
					start = None
					end = None
					grid = make_grid(ROWS, width)

					spot = grid[1][0]
					spot.make_barrier()
					spot = grid[1][1]
					spot.make_barrier()
					spot = grid[2][3]
					spot.make_barrier()
					spot = grid[3][3]
					spot.make_barrier()
					spot = grid[1][3]
					spot.make_barrier()

	pygame.quit()

main(WIN, WIDTH)