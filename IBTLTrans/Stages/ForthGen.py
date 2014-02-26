from IBTLTrans.Token import Token

class ForthGen:
    def __init__(self, ast):
        self._ast = ast
        self._cmds = ""
        self._error = False
        self._opToSym = {"T_PLUS": "+", "T_MINUS": "-", "T_MULT": "*", "T_DIV": "/"}

    def generate(self):
        self.emit(self._ast["T"])
        return not self._error

    def getForth(self):
        return self._cmds

    def emit(self, tree):
        if type(tree) is list:
            for leaf in tree:
                self.emit(leaf)

        elif type(tree) is dict:
            # only one derivation to follow

            if tree.get("S"):
                self.emit(tree["S"])
            elif tree.get("S'"):
                self.emit(tree["S'"])
            elif tree.get("expr"):
                self.emit(tree["expr"])
            elif tree.get("e"):
                return # epsilon production
            elif self.operTok(tree.keys()[0]):
                # is an operation
                key = tree.keys()[0]
                self.emit(tree[key])
                self._cmds += "%s " % self._opToSym[key]
            elif self.constTok(tree.keys()[0]):
                key = tree.keys()[0]
                self._cmds += "%s " % tree[key]
            # elif tree.get("T_PLUS"):
            #     self.emit(tree["T_PLUS"])
            #     self._cmds += "+ "
            # elif tree.get("T_INT"):
            #     self._cmds += "%s " % tree["T_INT"]

    def execute(self):
        print(todo)

    def operTok(self, op):
        return op in ["T_PLUS", "T_MINUS", "T_MULT", "T_DIV"]

    def constTok(self, t):
        return t in ["T_INT", "T_BOOL", "T_CONSTSTR", "T_FLOAT"]

