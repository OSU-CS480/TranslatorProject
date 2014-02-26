from IBTLTrans.Token import Token

import pprint

class ForthGen:
    # TODO: restructure to _opToSym = {"T_INT": {"T_PLUS": "+", ...}, "T_FLOAT": {"T_PLUS": "f+", ...}}
    # _opToSym = {"T_PLUS": "+", "T_MINUS": "-", "T_MULT": "*", "T_DIV": "/", "T_GTEQ": ">=", "T_GT" : ">", "T_LTEQ" : "<", "T_LT" : "<", "T_EXP" : "^", "T_NOTEQ" : "!=", "T_NOT" : "!", "T_MOD" : "%", "T_AND" : "and", "T_OR" : "or", "T_TAN" : "tan", "T_COS" : "cos", "T_SIN" : "sin"}
    
    _opToSym = {"T_INT": {"T_PLUS": "+", "T_MINUS": "-", "T_MULT": "*"}, "T_FLOAT": {"T_PLUS": "f+", "T_MULT": "f*"}}

    _ops = ["T_PLUS", "T_MINUS", "T_MULT", "T_DIV", "T_GTEQ", "T_GT", "T_LTEQ", "T_LT", "T_EXP", "T_NOTEQ", "T_NOT", "T_MOD", "T_AND", "T_OR", "T_TAN", "T_COS", "T_SIN"]
    _consts = ["T_INT", "T_BOOL", "T_CONSTSTR", "T_FLOAT"]

    def __init__(self, parseTree):
        self._pt = parseTree
        self._ast = {}
        self._cmds = ""
        self._error = False

    def generateAST(self):
        self._ast["T"] = self.emitAST(self._pt["T"])
        return not self._error

    # take in the parse tree parts as input, reconstruct a type annotated tree as the AST
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
            elif self.operTok(tree.keys()) != None:
                key = self.operTok(tree.keys())
                branch = self.emitAST(tree[key])

                # TODO: right now types returned by operations are assumed to be the type of their inputs, this is not always true

                # determine the of this operation by inspecting 
                # the branch that will be sent up

                # for now, all of the types must match up
                # TODO: implicit casting here if required for the course?

                # left branch (will always exist for unops and binops)
                t = branch[0]["type"]

                if len(branch) > 1:
                    t2 = branch[1]["type"]
                    if t != t2:
                        print("Type mismatch: got %s and %s for operation %s" % (t, t2, tree.keys()[0]))
                        self._error = True

                return {key: branch, "type": t}
            elif self.constTok(tree.keys()) != None:
                key = self.constTok(tree.keys())
                return {key: tree[key], "type": key}
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
                self.emit(tree["expr"])
            elif tree.has_key("e"):
                return # epsilon production
            elif self.operTok(tree.keys()) != None:
                oper = self.operTok(tree.keys())
                self.emit(tree[oper])

                # see if the type of the expression matches the token
                if ForthGen._opToSym.has_key(tree["type"]):
                    # see if this type has the associated token
                    if ForthGen._opToSym[tree["type"]].has_key(oper):
                        self._cmds += "%s " % ForthGen._opToSym[tree["type"]][oper]
                    else:
                        print("cannot apply %s to an expression of type %s" % (oper, tree["type"]))
                        self._error = True
                else:
                    print("no operations for type %s" % tree["type"])
                    self._error = True
            elif self.constTok(tree.keys()) != None:
                const = self.constTok(tree.keys())

                # modify literals and constants in such a way that Forth will interpret them correctly
                forthified = tree[const]
                if tree["type"] == "T_FLOAT":
                    forthified += "e"

                self._cmds += "%s " % forthified

    def execute(self):
        print(todo)

    def operTok(self, keys):
        return self.keyInList(keys, ForthGen._ops)

    def constTok(self, keys):
        return self.keyInList(keys, ForthGen._consts)

    def keyInList(self, keys, l):
        for key in keys:
            if key == "type":
                continue

            for item in l:
                if key == item:
                    return key

