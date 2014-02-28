import pprint

class ForthGen:
    # TODO: restructure to opToSym = {"T_INT": {"T_PLUS": "+", ...}, "T_FLOAT": {"T_PLUS": "f+", ...}}
    # opToSym = {"T_PLUS": "+", "T_MINUS": "-", "T_MULT": "*", "T_DIV": "/", "T_GTEQ": ">=", "T_GT" : ">", "T_LTEQ" : "<", "T_LT" : "<", "T_EXP" : "^", "T_NOTEQ" : "!=", "T_NOT" : "!", "T_MOD" : "%", "T_AND" : "and", "T_OR" : "or", "T_TAN" : "tan", "T_COS" : "cos", "T_SIN" : "sin"}
    
    opToSym = {"T_INT": 
               {"T_AND": "and", "T_OR": "or", "T_MOD": "mod", "T_GT": ">", "T_LT": "<", "T_GTEQ": ">=", "T_LTEQ": "<=", "T_PLUS": "+", "T_MINUS": "-", "T_MULT": "*", "T_NOTEQ": "<>", "T_NOT": "negate"}, 
               "T_FLOAT": 
               {"T_PLUS": "f+", "T_MULT": "f*", "T_DIV": "f/", "T_SIN": "fsin", "T_COS": "fcos", "T_TAN": "ftan", "T_NOT": "fnegate", "T_EXP": "f**", "T_EQ": "f=", "T_NOTEQ": "f<>", "T_LT": "f<", "T_GT": "f>", "T_LTEQ": "f<=", "T_GTEQ": "f>="}}

    ops = ["T_PLUS", "T_MINUS", "T_MULT", "T_DIV", "T_GTEQ", "T_GT", "T_LTEQ", "T_LT", "T_EXP", "T_NOTEQ", "T_NOT", "T_MOD", "T_AND", "T_OR", "T_TAN", "T_COS", "T_SIN"]

    consts = ["T_INT", "T_BOOL", "T_CONSTSTR", "T_FLOAT"]

    # take in an instance of the type checker that has completed running
    def __init__(self, tc):
        self._tc = tc
        self._ast = tc.getAST()
        self._ifASTs = tc.getIfFncASTs()

        self._cmds = ""
        self._error = False

    def toForth(self):
        # first, emit each if function
        for fnc in self._ifASTs:
            self.emit(fnc["T"])
            self._cmds += "\n" # astetically only

        self.emit(self._ast["T"])
        return not self._error

    def addBye(self):
        self._cmds += "bye"

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

            elif tree.has_key("forth_literal"):
                self.emit(tree["forth_literal"])
                
                # after the expression has been emitted, emit the command string
                self._cmds += tree["forth_literal"]["cmd"]
            elif tree.has_key("T_STDOUT"):
                # printing taken care of by the encapsulated forth_literal branch
                self.emit(tree["T_STDOUT"])

            elif ForthGen.operTok(tree.keys()) != None:
                # TODO: determine how to handle casting to types (nothing about it in the assignment so far)
                # do operations on floats and ints always cast the ints to floats?
                # are floats ever cast back to ints?

                # TODO: move this section into the ast generation
                oper = ForthGen.operTok(tree.keys())
                self.emit(tree[oper])

                self._cmds += "%s " % ForthGen.opToSym[tree["type"]][oper]

            elif ForthGen.constTok(tree.keys()) != None:
                const = ForthGen.constTok(tree.keys())

                # modify literals and constants in such a way that Forth will interpret them correctly
                forthified = tree[const]
                if tree["type"] == "T_FLOAT":
                    forthified += "e"

                if tree["type"] == "T_CONSTSTR":
                    forthified = self.forthStr(forthified)

                self._cmds += "%s " % forthified

    # format a string literal for output by Forth
    # the string returned, when seen by forth will cause it to be immediantly printed
    def forthStr(self, s):
        s = s[1:-1] # strip off quotes
        s.replace("\n", " \" CR .\"") # replace all newlines

        # remove extra quotes at the end if the string ended in a newline
        if s[-3:] == " .\"":
            s = s[:-3]

        # TODO: replace tabs and other \ deliminated chars

        return ".\" %s \"" % s

    @classmethod
    def operTok(cls, keys):
        return ForthGen.keyInList(keys, ForthGen.ops)

    @classmethod
    def constTok(cls, keys):
        return ForthGen.keyInList(keys, ForthGen.consts)

    @classmethod
    def keyInList(cls, keys, l):
        for key in keys:
            if key == "type":
                continue

            for item in l:
                if key == item:
                    return key

