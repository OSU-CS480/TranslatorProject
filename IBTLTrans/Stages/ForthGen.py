from IBTLTrans.Token import Token

import pprint

class ForthGen:
    _opToSym = {"T_PLUS": "+", "T_MINUS": "-", "T_MULT": "*", "T_DIV": "/", "T_GTEQ": ">=", "T_GT" : ">", "T_LTEQ" : "<", "T_LT" : "<", "T_EXP" : "^", "T_NOTEQ" : "!=", "T_NOT" : "!", "T_MOD" : "%", "T_AND" : "and", "T_OR" : "or", "T_TAN" : "tan", "T_COS" : "cos", "T_SIN" : "sin"}
    def __init__(self, parseTree):
        self._pt = parseTree
        self._ast = {}
        self._cmds = ""
        self._error = False

    # TODO: dummy function for now
    def generateAST(self):
        self._ast = self._pt
        return True

    def getAST(self):
        return self._ast

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
                self._cmds += "%s " % ForthGen._opToSym[key]
            elif self.constTok(tree.keys()[0]):
                key = tree.keys()[0]
                self._cmds += "%s " % tree[key]

    def execute(self):
        print(todo)

    def operTok(self, op):
        return op in ["T_PLUS", "T_MINUS", "T_MULT", "T_DIV", "T_GTEQ", "T_GT", "T_LTEQ", "T_LT", "T_EXP", "T_NOTEQ", "T_NOT", "T_MOD", "T_AND", "T_OR", "T_TAN", "T_COS", "T_SIN"]

    def constTok(self, t):
        return t in ["T_INT", "T_BOOL", "T_CONSTSTR", "T_FLOAT"]

