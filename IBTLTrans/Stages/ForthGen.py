from IBTLTrans.Token import Token

import pprint

class ForthGen:
    # TODO: restructure to _opToSym = {"T_INT": {"T_PLUS": "+", ...}, "T_FLOAT": {"T_PLUS": "f+", ...}}
    _opToSym = {"T_PLUS": "+", "T_MINUS": "-", "T_MULT": "*", "T_DIV": "/", "T_GTEQ": ">=", "T_GT" : ">", "T_LTEQ" : "<", "T_LT" : "<", "T_EXP" : "^", "T_NOTEQ" : "!=", "T_NOT" : "!", "T_MOD" : "%", "T_AND" : "and", "T_OR" : "or", "T_TAN" : "tan", "T_COS" : "cos", "T_SIN" : "sin"}

    def __init__(self, parseTree):
        self._pt = parseTree
        self._ast = {}
        self._cmds = ""
        self._error = False

    def generateAST(self):
        # # TODO: dummy function for now
        # self._ast = self._pt
        # return True
        self._ast["T"] = self.emitAST(self._pt["T"])
        return not self._error

    # take in the parse tree parts as input, reconstruct a type annotated tree as the AST
    # {'T': {'S': [{'S': []}, {"S'": {'e': []}}]}}
    # {'T': {'S': [{'expr': [{'T_PLUS': [{'T_INT': '2'}, {'T_INT': '3'}]}]}, {'e': []}]}}
    def emitAST(self, tree):
        if type(tree) is list:
            subSProds = []
            for leaf in tree:
                subSProds.append(self.emitAST(leaf))
            return subSProds

        elif type(tree) is dict:
            if tree.has_key("S"):
                branch = self.emitAST(tree["S"])
                return {"S": branch}
            elif tree.has_key("S'"):
                branch = self.emitAST(tree["S'"])
                return {"S'": branch}
            elif tree.has_key("expr"):
                branch = self.emitAST(tree["expr"])
                return {"expr": branch}
            elif self.operTok(tree.keys()[0]):
                key = tree.keys()[0]
                branch = self.emitAST(tree[key])
                return {key: branch}
            elif self.constTok(tree.keys()[0]):
                key = tree.keys()[0]
                return {key: tree[key]}
            elif tree.has_key("e"):
                return {"e": []} # terminal branch, return up
            else:
                print("Undefined parse tree branch with keys: %s" % tree.keys())
                self._error = True
                return
        else:
            print("Error in parse tree")
            return

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

            if tree.has_key("S"):
                self.emit(tree["S"])
            elif tree.has_key("S'"):
                self.emit(tree["S'"])
            elif tree.has_key("expr"):
                # get the subexpressions to determine type

                # subexprs = tree["expr"][0][tree["expr"][0].keys()]
                # leftExprType = subexprs[0]
                # rightExprType = subexprs[1]

                self.emit(tree["expr"])
            elif tree.has_key("e"):
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

