import heapq as hp

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

  def add_edge(self, v1, v2, weight=1, bidirection=False, update_w=None):  # direction from v1 to v2
    if v1 in self.vertices and v2 in self.vertices:
      self.vertices[v1].out_edges[v2] = weight
      self.vertices[v2].in_edges[v1] = weight
      if bidirection or update_w:
        self.vertices[v1].in_edges[v2] = weight if update_w is None else update_w
        self.vertices[v2].out_edges[v1] = weight if update_w is None else update_w

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

  def DFS(self, v):
    def _run(v):
      for adj_v in self.vertices[v].out_edges:
        if adj_v not in visisted:
          result.append(adj_v)
          visisted.add(adj_v)
          _run(v=adj_v)

    visisted = set(v)
    result = [v]

    _run(v=v)
    return result

  def BFS(self, v):
    def _run(v):
      this_level_vertices = []
      for adj_v in self.vertices[v].out_edges:
        if adj_v not in visisted:
          this_level_vertices.append(adj_v)
          visisted.add(adj_v)

      return this_level_vertices

    visisted = set(v)
    result = [v]
    this_level_vertices = [v]

    while len(this_level_vertices) != 0:
      t = []
      for _v in this_level_vertices:
        t += _run(_v)

      this_level_vertices = t
      result += t

    return result

  def unweighted_shorest_path(self, v1, v2):
    def _run(current_level_vertices, current_level):
      if len(distance) == self._vertex_count:
        return None

      new_level_vertices = []
      for v in current_level_vertices:
        for adj_v in self.vertices[v].out_edges:
          if adj_v == v2:
            distance[adj_v] = current_level + 1
            return current_level + 1
          
          if adj_v not in distance:
            distance[adj_v] = current_level + 1
            new_level_vertices.append(adj_v)
            continue

      return _run(current_level_vertices=new_level_vertices, current_level=current_level+1)

    def _trace_back(current_level, current_v):
      if current_level == 0:
        return 1

      prv_level_vertices = {key for key, val in distance.items() if val == current_level - 1}
      for adj_v in self.vertices[current_v].in_edges:
        if adj_v in prv_level_vertices:
          result.append(adj_v)
          total_weight[0] += self.vertices[current_v].in_edges[adj_v]
          return _trace_back(current_level=current_level-1, current_v=adj_v)
      else:
        return 0

    result = [v2]
    distance = {v1: 0}
    total_weight = [0]

    if v1 not in graph.vertices or v2 not in graph.vertices:
      return None

    if v1 == v2:
      return result, 0

    level = _run(current_level_vertices=[v1], current_level=0)
    if level is None:
      return None
    
    _trace_back(current_level=level, current_v=v2)
    return result[::-1], total_weight[0]

  # Dijkstras algorithm
  def weighted_shortest_path(self, v1, v2):
    # min-priority queue
    # structure: [shortest_dis, vertex, prv_vertex, availability]
    vertex_tracker = dict()
    min_priority_heap = []

    def push(token):  # over-writting instead of in-place assignment
      if token[1] in vertex_tracker:
        vertex_tracker[token[1]][-1] = False

      vertex_tracker[token[1]] = token
      hp.heappush(min_priority_heap, token + [True])

    def pop():
      while len(min_priority_heap) != 0:
        token = hp.heappop(min_priority_heap)
        if token[-1] is False:
          continue

        del vertex_tracker[token[1]]
        return token

    def _run(priority_token):
      push(priority_token)

      if priority_token[1] == v2:
        visisted[priority_token[1]] = priority_token
        visisted_vertex_tracker.add(priority_token[1])
        return

      # s_p_v = vertex_tracker[priority_v][0]  # smallest_total_cost_to_priority_v
      for adj_v in self.vertices[priority_token[1]].out_edges:
        if adj_v in visisted_vertex_tracker:
          continue

        c_a_v = self.vertices[priority_token[1]].out_edges[adj_v]  # cost_to_visis_adj_v
        new_cost = priority_token[0] + c_a_v
        if adj_v not in vertex_tracker:
          push([new_cost, adj_v, priority_token[1]])
        else:
          token = vertex_tracker[adj_v]
          if new_cost < token[0]:
            push([new_cost, adj_v, priority_token[1]])

      t = pop()  # expected to mark priority_token as visisted
      visisted[t[1]] = t 
      visisted_vertex_tracker.add(t[1])
      if len(vertex_tracker) == 0:
        return
      
      new_priority_v = pop()  # need to pop in order to clear out the old token
      return _run(new_priority_v)

    def trace_back(cur_v):
      result.append(cur_v)
      prv_v = visisted[cur_v][2]  # previous vertice
      if prv_v is not None:
        trace_back(prv_v)

    visisted_vertex_tracker = set()
    visisted = dict()
    result = []

    if v1 not in self.vertices or v2 not in self.vertices:
      return None

    _run([0, v1, None])

    if v2 not in visisted_vertex_tracker:
      return None

    trace_back(v2)
    return result[::-1], visisted[v2][0]

# ----------------------
# small graph
vertices = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
edges = [['A', 'B', False], ['B', 'C', False], ['C', 'D', False], ['D', 'A', False], ['E', 'A', True], ['E', 'C', False], ['G', 'F', True], ['H', 'G', False], ['I', 'H', False], ['C', 'F', True], ['D', 'E', True], ['G', 'I', True]]

# Complex graph
vertices = [
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
  'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
  'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD',
  'AE', 'AF', 'AG', 'AH', 'AI'
]

edges = [
  # Cluster 1: Highly cyclic core (A to J)
  ['A', 'B', 4, True],   ['B', 'C', 7, False],  ['C', 'D', 3, False],  ['D', 'A', 11, True],
  ['A', 'E', 8, False],  ['E', 'F', 2, True],   ['F', 'G', 14, False], ['G', 'H', 5, False],
  ['H', 'E', 9, True],   ['C', 'I', 6, False],  ['I', 'J', 3, True],   ['J', 'A', 12, False],
  ['B', 'G', 15, False], ['F', 'I', 4, False],  ['D', 'H', 7, False],

  # Bridge links between Cluster 1 and Cluster 2
  ['J', 'K', 18, False], ['E', 'L', 5, True],

  # Cluster 2: Dense bi-directional ring (K to P)
  ['K', 'L', 3, True],   ['L', 'M', 6, True],   ['M', 'N', 9, False],  ['N', 'O', 4, True],
  ['O', 'P', 11, False], ['P', 'K', 8, True],   ['K', 'M', 13, False], ['L', 'N', 2, True],
  ['O', 'K', 7, False],  ['N', 'P', 5, True],

  # Bridge links between Cluster 2 and Cluster 3
  ['P', 'Q', 16, False], ['M', 'R', 10, True],

  # Cluster 3: Directed Flow Network with inner shortcuts (Q to W)
  ['Q', 'R', 4, False],  ['R', 'S', 7, False],  ['S', 'T', 3, False],  ['T', 'U', 8, True],
  ['U', 'V', 5, False],  ['V', 'W', 12, False], ['W', 'Q', 19, False], ['Q', 'S', 6, True],
  ['R', 'U', 11, False], ['T', 'V', 4, True],   ['S', 'W', 15, False],

  # Bridge links between Cluster 3 and Cluster 4
  ['W', 'X', 9, True],   ['U', 'Y', 14, False],

  # Cluster 4: Interleaved Lattice Web (X to AI)
  ['X', 'Y', 3, True],    ['Y', 'Z', 8, False],   ['Z', 'AA', 4, True],   ['AA', 'AB', 6, False],
  ['AB', 'AC', 5, True],  ['AC', 'AD', 11, False],['AD', 'AE', 3, True],  ['AE', 'AF', 7, False],
  ['AF', 'AG', 9, True],  ['AG', 'AH', 4, False], ['AH', 'AI', 6, True],  ['AI', 'X', 13, False],
  ['X', 'Z', 10, False],  ['Y', 'AA', 5, True],   ['Z', 'AB', 7, False],  ['AA', 'AC', 3, True],
  ['AB', 'AD', 8, False], ['AC', 'AE', 4, True],  ['AD', 'AF', 12, False],['AE', 'AG', 5, True],
  ['AF', 'AH', 6, False], ['AG', 'AI', 8, True],  ['AH', 'X', 15, True],

  # Long-range feedback & cross-cutting links (Creates global cycles & shortcut paths)
  ['AI', 'A', 22, False], ['AF', 'E', 17, True],  ['AC', 'I', 19, False], ['Z', 'M', 14, True],
  ['Y', 'Q', 25, False],  ['V', 'D', 20, False],  ['T', 'H', 11, True],   ['N', 'B', 16, False]
]

graph = Graph()

for v in vertices:
  graph.add_vertex(v)

for e in edges:
  graph.add_edge(v1=e[0], v2=e[1], bidirection=e[3], weight=e[2])

for v, adj_v in graph.show().items():
  print(v, adj_v)


def run(v1, v2):
  print('-'*30)
  print(graph.unweighted_shorest_path(v1, v2))
  print(graph.weighted_shortest_path(v1, v2))

run('A', 'AC')
run('A', 'Y')
run('A', 'Q')
run('A', 'I')
run('G', 'Z')