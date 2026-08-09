from random import randint

class Trie: 
  def __init__(self, words = None):
    self.root = []
    #
    if words is not None:
      for word in words:
        self.add(word)

  class Node:
    def __init__(self, val):
      self.val = val
      self.nexts = []
      self.isWord = False

  def add(self, inputWord):
    def _add_(word, node, i):
      if len(word) == 1:
        t = self.Node(word)
        t.isWord = word
        node.nexts.append(t)
        return
      #
      if i < len(word):
        for n in node.nexts:
          if n.val == word[i]:
            _add_(word, n, i + 1)
            return
        # if no child found
        t = self.Node(inputWord[i])
        #
        if i == len(inputWord) - 1:
          t.isWord = True
        #
        node.nexts.append(t)
        _add_(word, t, i + 1)

    for node in self.root:
      if node.val == inputWord[0]:
        _add_(inputWord, node, 1)
        break
    else:
      t = self.Node(inputWord[0])
      self.root.append(t)
      _add_(inputWord, t, 1)

  def delWord(self, word):
    def _run_(word, i, branch, nodeDel, cNode):
      if i == len(word): # end of word
        if len(cNode.nexts) == 0:
          branch.remove(nodeDel)
        else:
          cNode.isWord = False
      else:
        if len(cNode.nexts) >= 2 or cNode.isWord:
          branch = cNode.nexts
          for n in cNode.nexts:
            if n.val == word[i]:
              _run_(word, i + 1, branch, n, n)
              break
        else: # no branching
          _run_(word, i + 1, branch, nodeDel, cNode.nexts[0])

    for node in self.root:
      if node.val == word[0]:
        _run_(word, 1, self.root, node, node)
        break
    else:
      print(f"There is no word '{word}'")

  def allWords(self):
    result = []
    #
    def _run_(node, word):
      word += node.val
      if node.isWord:
        result.append(word)
      #
      for n in node.nexts:
        _run_(n, word)
    #
    for node in self.root:
      _run_(node, '')
    return result
  
  def _delRandWord_(self): # for deletion debugging
    words = self.allWords()
    print(f"{'-'*20}\n", self.allWords())

    for _ in range(len(words)):
      t = words[randint(0, len(words) - 1)]
      self.delWord(t)
      print(f'deleted {t} -> {self.allWords()}')
      words.remove(t)
    print(f"{'-'*20}")