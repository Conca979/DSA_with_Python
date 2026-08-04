class Vertex:
  def __init__(self, val=None):
    self.val = val
    self.out_edges = dict()  # name: weight
    self.in_edges = dict()  # name: weight

class Graph:
  def __init__(self):
    self.vertices = dict()  # name: vertex object
    self._vertex_count = 0
    self._edge_count = 0

  def add_vertex(self, v, val=None):
    if v in self.vertices:
      return 0
    else:
      self.vertices[v] = Vertex(val)
      self._vertex_count += 1
      return 1

  def remove_vertex(self, v):
    if v in self.vertices:
      # if bidirection
      for adj_v in self.vertices[v].in_edges:
        self.vertices[adj_v].out_edges.pop(v, None)

      del self.vertices[v]
      self._vertex_count -= 1

      return 1
    else:
      return 0

  def add_edge(self, v1, v2, weight=1, bidirection=False, update_w=False):  # direction from v1 to v2
    if v1 in self.vertices and v2 in self.vertices:
      self.vertices[v1].out_edges[v2] = weight
      self.vertices[v2].in_edges[v1] = weight
      if bidirection or update_w:
        self.vertices[v1].in_edges[v2] = weight
        self.vertices[v2].out_edges[v1] = weight

      self._edge_count += 1
      return 1
    else:
      return 0

  def remove_edge(self, v1, v2, bidirection=False):  # direction from v1 to v2
    if v1 in self.vertices and v2 in self.vertices:
      self.vertices[v1].out_edges.pop(v2, None)
      self.vertices[v2].in_edges.pop(v1, None)
      if bidirection:
        self.vertices[v2].out_edges.pop(v1, None)
        self.vertices[v1].in_edges.pop(v2, None)

      self._edge_count -= 1
      return 1
    else:
      return 0

  def show(self):
    vertices = {v:{} for v in self.vertices}
    for v in self.vertices:
      for adj_v, w in self.vertices[v].out_edges.items():
        vertices[v][adj_v] = w

    return vertices

  def get_neighbors(self, v):
    if v in self.vertices:
      return self.vertices[v].out_edges

    else:
      return 0

  def get_weight(self, v1, v2):
    if v1 in self.vertices and v2 in self.vertices:
      if v1 in self.vertices[v2].in_edges:
        return self.vertices[v2].in_edges[v1]
      elif v1 in self.vertices[v2].out_edges:
        return self.vertices[v2].out_edges[v1]
      else:
        return None


# ----------------------
graph = Graph()

graph.add_vertex('A', 3)
graph.add_vertex('B', 4)
graph.add_vertex('C', 5)

graph.add_edge('A', 'B', bidirection=True)
graph.add_edge('A', 'C', bidirection=True)
graph.add_edge('C', 'B')

for v, adj_v in graph.show().items():
  print(v, adj_v)

print('-'*30)

for v, adj_v in graph.show().items():
  print(v, adj_v)

print('-'*30)

print(graph.get_neighbors(v='A'))

print('-'*30)

print(graph._edge_count, graph._vertex_count)