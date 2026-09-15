import random
from typing import Optional
# Optional indicates a parameter, variable or return value can hold a specified data type or None

class Node:
  def __init__(self, val:float, left: Optional['Node']=None, right: Optional['Node']=None) -> None:
    self.val = val
    self.left = left
    self.right = right

class BSTree:
  def __init__(self):
    self.root: Optional[Node] = None
    self.nodes: int = 0
  
  def insert(self, val: float) -> None:
    def _insert(node: Node, val: float=val):
      if node.val > val:
        if node.left is None:
          node.left = Node(val=val)
        else: _insert(node= node.left, val=val)
      else:
        if node.right is None:
          node.right = Node(val=val)
        else:
          _insert(node= node.right, val=val)

    if self.root is None:
      self.root = Node(val=val)
      self.nodes += 1
    else:
      _insert(node= self.root, val=val)
      self.nodes += 1

  def DFS(self, type: int=1) -> list[float]:
    arr: list[float] = []

    def _run(node: Optional['Node']=self.root) -> Optional[list[float]]:
      if node is None:
        return

      if type == 1:  # in-order traversal
        _run(node=node.left)
        arr.append(node.val)
        _run(node=node.right)
      elif type == 2:  # pre-order traversal
        arr.append(node.val)
        _run(node=node.left)
        _run(node=node.right)
      else:   # post-order traversal
        _run(node.left)
        _run(node.right)
        arr.append(node.val)

    _run()
    return arr

  # search for a node object with value of val
  def search(self, val: float) -> Optional[Node]:
    def _run(node: Optional[Node]=self.root, val: float=val) -> Optional[Node]:
      if node is None:
        return None
      
      if node.val == val:
        return node
      else:
        if node.val < val:
          return _run(node=node.right, val=val)
        else:
          return _run(node=node.left, val=val)
      
    return _run(node=self.root, val=val)
  
  def level(self, node: Optional[Node]) -> int:
    def _run(node: Optional[Node]=self.root) -> int:
      if node is None:
        return 0
      
      return 1 + max(_run(node.left), _run(node.right))
    
    return _run(node=node)
  
  # LOT = level order traversal
  def LOT(self, level: int) -> list[Node]:
    arr: list[Node] = []

    def _run(node: Optional[Node]=self.root, cur_lv: int=0) -> None:
      if node is None:
        return
      
      if cur_lv == level:
        arr.append(node)
      else:
        _run(node=node.left, cur_lv=cur_lv+1)
        _run(node=node.right, cur_lv=cur_lv+1)

    _run()
    return arr

  # return min node
  def min(self, node: Optional[Node]=None) -> Optional[Node]:
    def _run(node: Optional[Node]) -> Optional[Node]:
      if node is None:
        return None
      
      if node.left is None:
        return node
      else:
        return _run(node=node.left)

    target_node = node if node is not None else self.root
    return _run(target_node)

  # return max node
  def max(self, node: Optional[Node]=None) -> Optional[Node]:
    def _run(node: Optional[Node]) -> Optional[Node]:
      if node is None:
        return None
      
      if node.right is None:
        return node
      else:
        return _run(node=node.right)

    target_node = node if node is not None else self.root
    return _run(target_node)

  def visual(self) -> None:
    vals: list[float] = self.DFS(type=1)

    def space(val: Optional[float]=None, s: int=1) -> Optional[str]:
      max_node = self.max()
      if max_node is None:
        return None
    
      if val is None:
        return ' '*len(str(max_node.val))*s
      
      r = len(str(max_node.val))
      r_val = len(str(val))
      return str(val) + ' '*(r-r_val)*s

    for lv in range(self.level(self.root)):
      LOT = [node.val for node in self.LOT(lv)]
      LOT_position = [vals.index(val) for val in LOT]
      for i in range(LOT_position[-1]+1):
        print(space() if i not in LOT_position else space(vals[i]), end='')
      print('')

  # find parent node
  def _prt(self, val: float) -> Optional[Node]:
    def _run(val: float, node: Optional[Node]) -> Optional[Node]:
      if node is None:
        return None
      
      if node.left and node.left.val == val:
        return node
      elif node.right and node.right.val == val:
        return node
      else:
        return _run(val, node=node.left) or _run(val, node=node.right)
    
    return _run(val=val, node=self.root)

  def del_(self, val: float) -> None:
    # node in need to be deleted
    node_del = self.search(val)
    if node_del is None:
      return
    else:
      self.nodes -= 1
    node_del_prt = self._prt(val)

    # if root node
    if node_del_prt is None:
      # if leaf node
      if node_del.left is None and node_del.right is None:
        self.root = None
      # else: a sub node
      else:
        if node_del.right:
          min_subtree = self.min(node_del.right)
          if min_subtree is None: return
    
          if min_subtree is node_del.right:
            self.root = min_subtree
            min_subtree.left = node_del.left
          else:
            min_subtree_prt = self._prt(min_subtree.val)
            if min_subtree_prt is None: return
            
            min_subtree.left = self.root.left
            self.root = min_subtree_prt.left
            min_subtree_prt.left = min_subtree.right
            min_subtree.right = node_del.right
        else:
          max_subtree = self.max(node_del.left)
          if max_subtree is node_del.left:
            self.root = max_subtree
            max_subtree.right = node_del.right
          else:
            max_subtree_prt = self._prt(max_subtree.val)
            max_subtree.right = self.root.right
            self.root = max_subtree_prt.right
            max_subtree_prt.right = max_subtree.left
            max_subtree.left = node_del.left
    else:
      # if leaf node
      if node_del.left is None and node_del.right is None:
        if node_del_prt.val > val:
          node_del_prt.left = None
        else:
          node_del_prt.right = None
      # else: a sub node
      else:
        if node_del.right:
          min_subtree = self.min(node_del.right)
          if min_subtree is node_del.right:
            if node_del_prt.val > val:
              node_del_prt.left = min_subtree
            else:
              node_del_prt.right = min_subtree
            min_subtree.left = node_del.left
          else:
            min_subtree_prt = self._prt(min_subtree.val)
            if node_del_prt.val > val:
              node_del_prt.left = min_subtree_prt.left
            else:
              node_del_prt.right = min_subtree_prt.left
            min_subtree_prt.left = min_subtree.right
            min_subtree.right = node_del.right
            min_subtree.left = node_del.left
        else:
          max_subtree = self.max(node_del.left)
          if max_subtree is node_del.left:
            if node_del_prt.val > node_del.val:
              node_del_prt.left = max_subtree
            else:
              node_del_prt.right = max_subtree
            max_subtree.right = node_del.right
          else:
            max_subtree_prt = self._prt(max_subtree.val)
            if node_del_prt.val > node_del.val:
              node_del_prt.left = max_subtree_prt.right
            else:
              node_del_prt.right = max_subtree_prt.right
            max_subtree_prt.right = max_subtree.left
            max_subtree.left = node_del.left
            max_subtree.right = node_del.right

  def isBalanced(self, node: Optional[Node]=None) -> bool:
    def _run(node: Optional[Node]=self.root) -> bool:
      if node is None:
        return True
      
      l = self.level(node=node.left)
      r = self.level(node=node.right)

      if abs(l - r) > 1:
        return False
      else:
        return _run(node=node.left) and _run(node=node.right)

    target_node = self.root if node is None else node
    return _run(target_node)

  # node reference rotation
  def balance(self) -> None:
    if self.root is None:
      return None

    # single rotation
    def right_rotation(node: Node) -> None:
      prt = self._prt(val=node.val)
      if prt is None: # if root node
        t = self.root
        self.root = self.root.left
        t.left = self.root.right
        self.root.right = t
      else:  # inner node
        if prt.val > node.val:
          prt.left = prt.left.left
          node.left = prt.left.right
          prt.left.right = node
        else:
          prt.right = prt.right.left
          node.left = prt.right.right
          prt.right.right = node

    # single rotation
    def left_rotation(node: Optional[Node]) -> None:
        if node is None: return
        prt = self._prt(val=node.val)
        if prt is None:  # if root node
          t = self.root
          self.root = self.root.right
          t.right = self.root.left
          self.root.left = t
        else:
          if prt.val > node.val:
            prt.left = prt.left.right
            node.right = prt.left.left
            prt.left.left = node
          else:
            prt.right = prt.right.right
            node.right = prt.right.left
            prt.right.left = node

    def _balance_factor(node: Node) -> int:
      return self.level(node.left) - self.level(node.right)

    def _run(node: Node):
      # balance from leaf to root
      if node.left:
        _run(node=node.left)
      if node.right:
        _run(node=node.right)
      
      # left rotation
      while _balance_factor(node=node) < -1:
        # check if double rotation needed
        if node.right is not None and _balance_factor(node.right) > 0:
          right_rotation(node=node.right)

        left_rotation(node=node)

      # right rotation
      while _balance_factor(node=node) > 1:
        # check if double rotation needed
        if node.left is not None and _balance_factor(node.left) < 0:
          left_rotation(node=node.left)

        right_rotation(node=node)

    return _run(self.root)

# ------------------------------------------------

arr = random.sample(range(1, 200), 100)
# arr = [20,10,30,40]
tree = BSTree()

for val in arr:
  tree.insert(val=val)

print(arr)
tree.visual()
print("Before balance: ", tree.isBalanced())
print("-"*40)

tree.balance()
print("After balance: ", tree.isBalanced())
tree.visual()
print("-"*40)