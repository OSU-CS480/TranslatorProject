from IBTLTrans.Token import Token

import pprint

class Parser:
    def __init__(self, tokens):
        self._graph = {}
        self._tokens = tokens

    def getAstStr(self):
        if self._graph != {}:
            return pprint.pformat(self._graph)
        else:
            return "AST could not be generated"

    def __str__(self):
        if self._graph != {}:
            return pprint.pformat(self._graph)
    
    # this is the T production in revisedgrammar.txt
    def parse(self):
        (tokens, error, graph) = self.s(self._tokens)

        if not error:
            self._graph["PROG"] = graph
        else:
            self._remainingTokens = tokens

        return not error
        
    def s(self, tokens):
        newGraph = {}

        (exprToks, error, exprGraph) = self.expr(tokens)

        if error:
            # nothing else to do for this production, return up an error
            return (tokens, True, {})
        else:
            # no error, continue or return up
            exprs = [exprGraph] # can be one or two for this production
            
            if exprToks == []:
                # return up no error, parsing complete
                newGraph["s"] = exprs
                return ([], False, newGraph)
            else:
                # continue consuming tokens, if possible
                (sToks, error, sGraph) = self.s(exprToks)

                if error:
                    return (tokens, False, {})
                else:
                    exprs.append(sGraph)
                    newGraph["s"] = exprs
                    return (sToks, error, newGraph)
            
    def expr(self, tokens):
        newGraph = {}
        exprs = []

        (operToks, error, operGraph) = self.oper(tokens)

        if error:
            # Not an operation, try stmt
            (stmtToks, error, stmtGraph) = self.stmt(tokens)

            if error: 
                # Fatal error
                return (tokens, True, {})
            else:
                # Sucessfully parsed a stmt
                exprs.append(stmtGraph)
                newGraph['expr'] = exprs
                return (stmtToks, False, newGraph)
        else:
            # Sucessfully parsed a operation
            exprs.append(operGraph)
            newGraph['expr'] = exprs
            return (operToks, False, newGraph)

    def oper(self, tokens):
        newGraph = {}
        exprs = []

        if tokens[0] == "T_LBRACKET":
            # Case 1: [T_ASSIGN T_ID oper]
            if tokens[1] == "T_ASSIGN" and tokens[2] == "T_ID":
                (operToks, error, operGraph) = self.oper(tokens[3:])

                if error:
                    # Error parsing for oper
                    return (tokens, True, operGraph)
                else:
                    # Sucessful parse of case 1
                    exprs.append(operGraph)
                    newGraph["oper"] = exprs
                    return (operToks, False, newGraph)

            elif self.binopPred(tokens[1]):
                # Case 2: [binop oper oper]
                (operToks, error, operGraph) = self.operToks(tokens[2:])
                if error:
                    # Error parsing 
                    return (tokens, True, {})
                exprs.append(operGraph)

                (operToks2, error, operGraph2) = self.oper(operToks)

                if error:
                    # Error parsing the second oper production
                    return(operToks, True, {})

                exprs.append(operGraph2)
                newGraph["oper"] = exprs
                return (operToks2, False, newGraph)

            elif self.unopPred(tokens[1]):
                # Case 3: [unop oper]
                (operToks, error, operGraph) = self.oper(tokens[2:])
                if error:
                    # Error parsing oper
                    return (tokens, True, {})
                else:
                    # Successful parse
                    exprs.append(operGraph)
                    newGraph["oper"] = exprs
                    return (operToks, False, newGraph)

    def varList(self, tokens):
        newGraph = {}
        exprs = []

        if tokens[0].t() == "T_LBRACKET" and self.typePred(tokens[1].t()) and tokens[2].t() == "T_ID" and tokens[3].t() == "T_RBRACKET":
            exprs.append({"type": tokens[1].t(), "identifier": tokens[2].text()})

            # base case
            if tokens[4].t() == "T_RBRACKET":
                newGraph["var"] = exprs
                return (tokens[4:], False, newGraph)
            else:
                # recursive case
                (varListTok, error, varListGraph) = self.varList(tokens[4:])
                exprs.append(varListGraph)

                newGraph["var"] = exprs
                return (varListTok, error, newGraph)
        else:
            return (tokens, True, {})

    def exprList(self, tokens):
        newGraph = {}
        exprs = []

        (exprToks, error, exprGraph) = self.expr(tokens)

        if error:
            return (tokens, True, {})

        exprs.append(exprGraph)
        if exprToks[0].t() == "T_RBRACKET":
            newGraph["expr"] = exprs
            return (exprToks, False, newGraph)

        (exprListTok, error, exprGraph2) = self.exprList(exprToks)

        if error:
            return (tokens, True, {})
        else:
            exprs.append(exprGraph2)
            newGraph["expr"] = exprs
            return (exprListTok, error, newGraph)
    # 
    # PREDICATES
    #
    def binopPred(self, token):
        return token in ["T_PLUS", "T_MINUS", "T_MULT", "T_DIV", "T_MOD", "T_EXP", "T_OR", "T_AND", 
                         "T_LT", "T_GT", "T_LTEQ", "T_GTEQ", "T_EQ", "T_NOTEQ"]
        
    def unopPred(self, token):
        return token in ["T_MINUS", "T_SIN", "T_COS", "T_TAN", "T_NOT"]
    
    def constPred(self, token):
        return token in ["T_CONSTSTR", "T_BOOL", "T_INT", "T_FLOAT"]

    def typePred(self, token):
        return token in ["T_STRING", "T_BOOLTYPE", "T_INTTYPE", "T_FLOATTYPE"]

    def startOfStmtPred(self, token):
        return token in ["T_LET", "T_WHILE", "T_IF", "T_STDOUT"]
