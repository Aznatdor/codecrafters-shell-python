class Node:
    def __init__(self):
        self.children = dict()
        self.endNode = False


class Trie:
    def __init__(self):
        self.root = Node()


    def getMatchings(self, word: str) -> None | list[str]:
        # BEGIN FUNCTION
        def dfs(root: Node, curWord: str = "") -> list[str]:
            if root.endNode:
                matches.append(curWord)

            for (child, nextNode) in root.children.items():
                dfs(nextNode, curWord + child)
        # END FUNCTION

        curNode = self.root
        matches = []
        
        for char in word:
            # no matching
            if char not in curNode.children:
                return None
            curNode = curNode.children[char]

        dfs(curNode, word)

        return matches

    def insert(self, word: str) -> None:
        curNode = self.root
        for char in word:
            curNode = curNode.children.setdefault(char, Node())
        curNode.endNode = True

def main():
    root = Trie()

    root.insert("world")
    root.insert("word")
    root.insert("war")

    for word in ["w", "wo", "wok", "word"]:
        print("Matched", word, root.getMatchings(word))


if __name__ == "__main__":
    main()
