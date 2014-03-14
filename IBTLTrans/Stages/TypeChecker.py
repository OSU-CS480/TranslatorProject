from IBTLTrans.Stages.ForthGen import ForthGen

import pprint

# transform a parse tree into an abstract syntax tree (ast)
# adds new nodes for ForthGen to know extra Forth syntax to emit
# adds nodes for casting as well
class TypeChecker:
    # store the parse tree
    def __init__(self, pt):
        self._pt = pt
        self._ast = {}
        self._ifFunctions = [] # store all if expressions as their own functions
        self._whileFunctions = [] # whiles also need to be compiled
        self._variables = []
        self._floatVariables = []

        self._extraFncs = [] # extra functions that must be programmed in direct forth
        self._addedPowFnc = False # used so these definitions are only added once
        self._error = False

    def __str__(self):
        return pprint.pformat(self._ast)

    def getAST(self):
        return self._ast

    def getVariables(self):
        return (self._variables, self._floatVariables)

    def getIfFncASTs(self):
        return self._ifFunctions

    def getWhileFncASTs(self):
        return self._whileFunctions

    def getExtraFncASTs(self):
        return self._extraFncs

    # build the ast, identify to the user if there was an error in building it
    def generateAST(self):
        self._ast["T"] = self.emitAST(self._pt["T"])
        return not self._error

    def emitAST(self, tree):
        # go back up the call stack if there's an error
        if self._error:
            return

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
            elif tree.has_key("T_IF"):
                ifFunction = self.processIf(tree["T_IF"])
                return {"forth_literal": {"cmd": "%s " % ifFunction }}
            elif tree.has_key("T_WHILE"):
                whileFnc = self.processWhile(tree["T_WHILE"])
                return {"forth_literal": {"cmd": "%s " % whileFnc }}
            # let does not emit any code, it just stores variables
            # TODO: deal with variable scope later
            elif tree.has_key("T_LET"):
                self.emitAST(tree["T_LET"][0])
            elif tree.has_key("var"):
                self.emitAST(tree["var"])
            elif tree.has_key("identifier"):
                ident = tree["identifier"]
                if tree["type"] == "T_FLOATTYPE":
                    # TODO: fix vars that conflict with forth keywords
                    if not (ident in self._floatVariables) and not (ident in self._variables):
                        self._floatVariables.append(ident)
                    else:
                        print("Redeclared identifier float %s" % ident)
                else:
                    # anything else goes to the variables
                    if not (ident in self._variables) and not (ident in self._floatVariables):
                        self._variables.append(ident)
                    else:
                        print("Redeclared identifier %s" % ident)

            elif tree.has_key("T_ASSIGN"):
                # make sure this variable exists
                ident = tree["T_ASSIGN"][0]["T_ID"]
                if ident in self._variables:
                    isFloat = False
                elif ident in self._floatVariables:
                    isFloat = True
                else:
                    print("Variable %s doesn't exist" % ident)
                    self._error = True
                    return

                # process oper to assign
                branch = self.emitAST(tree["T_ASSIGN"][1])

                # branch type mus match variable type
                if isFloat and branch["type"] != "T_FLOAT":
                    self._error = True
                    print("Assigning a %s type operation to float %s" % (branch["type"], ident))
                elif not isFloat and branch["type"] == "T_FLOAT":
                    self._error = True
                    print("Assigning a float type operation to a non float variable %s" % ident)

                # return up a new branch that stores the variable
                if not isFloat:
                    return {"expr": [branch, {"forth_literal": {"cmd": "%s ! " % ident}}]}
                else:
                    return {"expr": [branch, {"forth_literal": {"cmd": "%s f! " % ident}}]}

            elif tree.has_key("T_STDOUT"):
                # get type of the expression for stdout to determine how to print the value

                branch = self.emitAST(tree["T_STDOUT"])

                print(branch)
                if branch[0]["expr"][0].has_key("type"):
                    t = branch[0]["expr"][0]["type"]

                    if t == "T_INT" or t == "T_BOOL":
                        # add new node to ast to signal to forth to print out
                        # handle ints and bools the same, both are on the int stack

                        branch[0]["cmd"] = ". " # this forth code will be added after evaling the expr
                        return {"T_STDOUT" : [{"forth_literal": branch[0] }]}
                    elif t == "T_FLOAT":
                        branch[0]["cmd"] = "f. "
                        return {"T_STDOUT" : [{"forth_literal": branch[0] }]}
                    elif t == "T_CONSTSTR":
                        # just return up the branch

                        # if this is printing out a const string, then pad it
                        forthCmd = "pad count type "
                        if branch[0]['expr'][0]['type'] == "T_CONSTSTR":
                            # pad place makes the string
                            forthCmd = "pad place " + forthCmd

                        # pad count type prints out the string on the stack
                        branch[0]['expr'].append({'forth_literal': {'cmd': forthCmd}})
                        return {"T_STDOUT": branch}
                    elif t == "T_STRING":
                        branch[0]['expr'].append({'forth_literal': {'cmd': "pad count type "}})
                        return {"T_STDOUT": branch}
                    else:
                        print("Not sure how to print type of %s" % t)
                        self._error = True
                else:
                    print("can't use stdout on this expression")
                    self._error = True

            elif ForthGen.operTok(tree.keys()) != None:
                oper = ForthGen.operTok(tree.keys())
                branch = self.emitAST(tree[oper])

                # determine if this function needs to be added in
                if oper == "T_EXP" and not self._addedPowFnc:
                    self._addedPowFnc = True
                    self.addPowFnc()

                # SPECIAL CASES

                # special case for using T_MINUS as negate
                if oper == "T_MINUS" and len(branch) == 1:
                    return self.negateToNegativeMult(branch)

                if oper in ForthGen.trigUnops and branch[0]["type"] == "T_INT":
                    return self.unopFloatCast(branch, oper, "T_FLOAT")

                # TODO: right now types returned by operations are assumed to be the type of their inputs
                # this is not always true

                # determine the of this operation by inspecting 
                # the branch that will be sent up

                # FIRST CHECK: do the types match (if this is a binop)
                # left branch (will always exist for unops and binops)
                t = branch[0]["type"]
                exprType = t

                recast = False
                if len(branch) > 1:
                    t2 = branch[1]["type"]

                    # cast the first argument as a float
                    if t == "T_INT" and t2 == "T_FLOAT":
                        #t = branch[0]["type"] = "T_FLOAT"
                        exprType = "T_FLOAT"
                        branch[0] = [{"expr": [branch[0], {"forth_literal": {"cmd": "s>f "}}]}]
                        recast = True
                    elif t == "T_FLOAT" and t2 == "T_INT":
                        #t2 = branch[1]["type"] = "T_FLOAT"
                        exprType = "T_FLOAT"
                        branch[1] = [{"expr": [branch[1], {"forth_literal": {"cmd": "s>f "}}]}]
                        recast = True
                    elif t == "T_CONSTSTR" and t2 == "T_CONSTSTR":
                        print("2 consts")
                        # return from here since there are multiple operators to do string concat
                        return self.processStrConcat(branch[0], branch[1])

                    elif (t == "T_CONSTSTR" and t2 == "T_STRING") or (t == "T_STRING" and t2 == "T_CONSTSTR"):
                        print("const and a str")
                        return self.processStrConcat(branch[0], branch[1])

                    if t != t2 and not recast:
                        print("Type mismatch: got %s and %s for operation %s" % (t, t2, oper))
                        self._error = True

                # SECOND CHECK: the operator given can operate on these type(s)
                if ForthGen.opToSym.has_key(t):
                    if ForthGen.opToSym[exprType].has_key(oper):
                        return {oper: branch, "type": exprType}
                    else:
                        print("Type error: Type %s cannot be used with operator %s" % (exprType, oper))
                        self._error = True
                else:
                    print("Type error: type %s has no operations associated with it" % exprType)
                    self._error = True

            elif tree.has_key("T_ID"):
                # see if this id is a float or non float id
                ident = tree["T_ID"]

                if ident in self._variables:
                    # TODO: for now, these are going to just be either ints or floats
                    return {"forth_literal": {"cmd": "%s @ " % ident}, "type": "T_INT"}
                elif ident in self._floatVariables:
                    return {"forth_literal": {"cmd": "%s f@ " % ident}, "type": "T_FLOAT"}
                else:
                    self._error = True
                    print("Undefined variable %s" % ident)

            elif ForthGen.constTok(tree.keys()) != None:
                key = ForthGen.constTok(tree.keys())
                t = key

                if t == "T_TRUE" or t == "T_FALSE":
                    t = "T_BOOL"

                return {key: tree[key], "type": t}
            elif tree.has_key("e"):
                return {"e": []} # terminal branch, return up
            else:
                print("Undefined parse tree branch with keys: %s" % tree.keys())
                self._error = True
                return
        else:
            print("Error in parse tree")
            return

    # tree is tree["T_IF"]
    # 
    # processIf takes an if expression and turns it into a function that 
    # will be printed at the very beginning of the program
    def processIf(self, tree):
        branch = self.emitAST(tree)

        exprName = "ifexpr" + str(len(self._ifFunctions))

        # TODO: check if the condition of the if expression is of type T_BOOL

        # function with else
        if len(branch) == 3:
            functionTree = {"T" : {"S": [{"expr": [{"forth_literal": {"cmd": ": %s " % exprName }}]}, {"S'": [{"expr": [branch[0]]}, {"S'": [{"expr": [{"forth_literal": {"cmd": "if "}}]}, {"S'": [{"expr": [branch[1]]}, {"S'": [{"expr": [{"forth_literal": {"cmd": "else "}}]}, {"S'": [{"expr": [branch[2]]}, {"S'": [{"expr": [{"forth_literal": {"cmd": "endif ; "}}]}, {"S'": [{"e": []}]}]}]}]}]}]}]}]}}

        else:
            functionTree = {"T" : {"S": [{"expr": [": %s " % exprName]}, {"S'": [{"expr": [branch[0]]}, {"S'": [{"expr": [{"forth_literal": {"cmd": "if "}}]}, {"S'": [{"expr": [branch[1]]}, {"S'": [{"expr": [{"forth_literal": {"cmd": "endif ; "}}]}, {"S'": [{"e": []}]}]}]}]}]}]}}

        self._ifFunctions.append(functionTree)
        
        # return up a forth_literal to call the function
        return exprName

    def processWhile(self, tree):
        condition = tree[0]

        # emit the ast for the condition and get it's type
        conditionBranch = self.emitAST(condition)

        # type of the conditionbranch must be boolean
        # TODO: modify ForthGen so that operators that take in ints like > and < have the return type of bool instead of int
        # if conditionBranch["type"] != "T_BOOL":
        #     self._error = True

        # remove the first branch as it's the condition
        branch = self.emitAST(tree[1:])

        exprName = "whileexpr" + str(len(self._whileFunctions))

        # violating the production that an expr should only have two nodes, will still emit correctly
        # splice in the rest of the while expression into the returned up branch
        branch.append({"expr": [{"forth_literal": {"cmd": "dup while "}}, conditionBranch, {"forth_literal": {"cmd": "repeat ; "}}]})

        fncTree = {"T" : {"S": [{"expr": [{"forth_literal": {"cmd": ": %s begin " % exprName}}, {"expr": branch}]}]}}
        self._whileFunctions.append(fncTree)

        return exprName

    # encode forth_literals that will correctly append the strings
    # TODO: fix for muliple concats
    def processStrConcat(self, lBranch, rBranch):
        if lBranch['type'] == "T_CONSTSTR":
            newBranch = {'expr': [lBranch, {'expr': [{'forth_literal': {'cmd': 'pad place '}}]}]}
        else:
            newBranch = {'expr': [lBranch, {'expr': [{'forth_literal': {'cmd': 'pad +place '}}]}]}

        newBranch['expr'][1]['expr'].append({'expr': [rBranch, {'forth_literal': {'cmd': 'pad +place '}}]})
        return {'expr': newBranch, 'type': 'T_STRING'}
        # newBranch = {'expr': [lBranch, {'expr': [{'forth_literal': {'cmd': 'pad place '}}]}]}

        # newBranch['expr'][1]['expr'].append({'expr': [rBranch, {'forth_literal': {'cmd': 'pad +place '}}]})

        # newExpr = {'expr': newBranch, 'type': 'T_STRING'}
        # return newExpr

        # working code for single concats only
        #return {'type': 'T_STRING', 'expr': [lBranch, {'expr': [{'forth_literal': {'cmd': 'pad place '}}, {'expr': [rBranch, {'forth_literal': {'cmd': 'pad +place '}}]}]}]}

    # return up a modified branch, replacing the - with an explicit mulitply by -1
    def negateToNegativeMult(self, branch):
        # basic type check, the expr in here should be a float or int
        t = branch[0]["type"]

        if not (t == "T_FLOAT" or t == "T_INT"):
            self._error = True
            print("Type error: type %s used with T_MINUS (can only use T_INT or T_FLOAT)" % t)
            return

        if t == "T_FLOAT":
            negOne = "-1.0e"

        if t == "T_INT":
            negOne = "-1"

        return {"T_MULT": [{"expr": branch[0]}, {t: negOne, "type": t}], "type": t}

    # cast a unop to a desired type
    def unopFloatCast(self, branch, oper, castTo):
        return {"type": castTo, oper: [{"expr": branch}, {"forth_literal": {"cmd": "s>f "}}]}

    def addPowFnc(self):
        # 1 swap swap ?do dup * loop ;
        self._extraFncs.append({"T": {"S": [{"forth_literal": {"cmd": ": pow_fnc 1 swap swap ?do dup * loop ;\n"}}, {"S'": [{"e": []}]}]}})
