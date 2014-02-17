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
        # must start with a [
        if self._tokens[0].t() != "T_LBRACKET":
            return False

        (tokens, error, graph) = self.s(self._tokens[1:])

        # must end with a ]
        if not error and tokens[0].t() == "T_RBRACKET":
            self._graph["T"] = graph
            return True

        return False
        # (tokens, error, graph) = self.s(self._tokens)

        # if not error:
        #     self._graph["PROG"] = graph
        # else:
        #     self._remainingTokens = tokens

        # return not error
        
    def s(self, tokens, prime=False):
        newGraph = {}

        if tokens[0].t() == "T_LBRACKET":
            # either production [ ] or [S]
            
            # prime = True then try rule [ ] S'
            # prime = False then [ ]
            if tokens[1].t() == "T_RBRACKET":
                if prime:
                    (sPrimeTok, error, sPrimeGraph) = self.s(tokens[2:], True)
                    if not error:
                        newSGraph = {}
                        newSGraph["S"] = []
                        newGraph["S'"] = newSGraph
                        return (sPrimeTok, error, newGraph)
                    else:
                        return (tokens, True, {})
                else:
                    newGraph["S"] = []
                    return (tokens[2:], False, newGraph)

            # no immediate right bracket
            # prime = True then [S] S'
            # prime = False then [S]
            if prime:
                (sTok, error, sGraph) = self.s(tokens[1:])
                if not error:
                    # must be a closing bracket and another S'
                    if sTok[0].t() == "T_RBRACKET":
                        (sPrimeTok, error, sPrimeGraph) = self.s(sTok[1:], True)
                        if not error:
                            newGraph["S'"] = [sGraph, sPrimeGraph]
                            return (sPrimeTok, error, newGraph)
                    
                return (tokens, True, {})
            else:
                (sTok, error, sGraph) = self.s(tokens[1:])
                if not error:
                    if sTok[0].t() == "T_RBRACKET":
                        newGraph["S"] = [sGraph]
                        return (sTok[1:], error, newGraph)
                return (tokens, True, {})
        else:
            # does not start with a l bracket
            
            if not prime:
                (sPrimeTok, error, sPrimeGraph) = self.s(tokens, True)
                if not error:
                    newGraph["S"] = [sPrimeGraph]
                    return (sPrimeTok, error, newGraph)
            
            # must be an expr now
            (exprToks, error, exprGraph) = self.expr(tokens)
            if not error:
                # if this is a S then we are done
                if not prime:
                    newGraph["S"] = [exprGraph]
                    return (exprToks, error, newGraph)
            else:
                return (tokens, True, {})

            # must be S' now, needs another S' to follow
            (sPrimeToks, error, sPrimeGraph) = self.s(exprToks, True)
            if not error:
                newGraph["S'"] = [exprGraph, sPrimeGraph]
                return (sPrimeToks, error, newGraph)
            else:
                return (tokens, True, {})
            
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

        if tokens[0].t() == "T_LBRACKET":
            # Case 1: [T_ASSIGN T_ID oper]
            if tokens[1].t() == "T_ASSIGN" and tokens[2].t() == "T_ID":
                (operToks, error, operGraph) = self.oper(tokens[3:])

                if error:
                    # Error parsing for oper
                    return (tokens, True, operGraph)
                else:
                    # Sucessful parse of case 1
                    if operToks[0].t() == "T_RBRACKET":
                        exprs.append(operGraph)
                        newGraph["oper"] = exprs
                        return (operToks[1:], False, newGraph)
                    else:
                        return (operToks, True, {})

            elif self.binopPred(tokens[1].t()):
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

                # Check for right bracket
                if operToks2[0].t() == "T_RBRACKET":
                    exprs.append(operGraph2)
                    newGraph["oper"] = exprs
                    return (operToks2[1:], False, newGraph)
                else:
                    return (operToks2, True, {})

            elif self.unopPred(tokens[1].t()):
                # Case 3: [unop oper]
                (operToks, error, operGraph) = self.oper(tokens[2:])
                if error:
                    # Error parsing oper
                    return (tokens, True, {})
                else:
                    # Successful parse
                    # Check for right bracket
                    if operToks[0].t() == "T_RBRACKET":
                        exprs.append(operGraph)
                        newGraph["oper"] = exprs
                        return (operToks[1:], False, newGraph)
                    else:
                        return (operToks, True, {})
            elif self.constPred(tokens[0].t()):
                # Case 4: consts
                newGraph["oper"] = tokens[0].t()
                return (tokens[1:], False, newGraph)

            elif tokens[0].t() == "T_ID":
                newGraph["oper"] = "T_ID"
                return(tokens[1:], False, newGraph)
            else:
                return (tokens, True, {})
        return (tokens, True, {})

    def stmt(self, tokens):
        if self.startOfStmtPred(tokens[0].t()):
            if tokens[0].t() == "T_STDOUT":
                (exprToks, error, exprGraph) = self.expr(tokens[1:], True)

                if error:
                    return (tokens, True, {})
                else:
                    if exprToks[0].t() == "T_RBRACKET":
                        exprs.append(exprGraph)
                        newGraph["T_STDOUT"] = exprs
                        return (exprToks[1:], False, newGraph)
                    else:
                        return (tokens, True, {})
            elif tokens[0].t() == "T_LET":
                # get the predicate
                if tokens[1].t() == "T_LBRACKET":
                    (varToks, error, varGraph) = self.varList(tokens[2:])

                    if not error and varToks[0].t() == "T_RBRACKET" and varToks[1].t() == "T_RBRACKET":
                        exprs.append(varGraph)
                        newGraph["T_LET"] = exprs
                        return (varToks[2:], False, newGraph)
                    else:
                        return (tokens, True, {})

                else:
                    return (tokens, True, {})
                
            elif tokens[0].t() == "T_WHILE":
                # get the predicate 
                (predExpr, error, predGraph) = self.expr(tokens[1:], True)
            
                # Could not get predicate
                if error:
                    return (tokens, True, {})
                
                exprs.append(predGraph)

                # get the expressionlist
            
                (exprListExpr, error, exprListGraph) = self.exprList(predExpr)

                if error:
                    return (tokens, True, {})

                exprs.append(exprListGraph)

                if exprListExpr[0].t() == "T_RBRACKET":
                    newGraph["T_WHILE"] = exprs
                    return (exprListExpr[1:], False, newGraph)
                
                return (tokens, True, {})
                
            elif tokens[0].t() == "T_IF":
                # get the predicate
                (predExpr, error, predGraph) = self.expr(tokens[1:], True)

                if error:
                    return (tokens, True, {})

                exprs.append(predGraph)

                # get the expr to run on true
                (trueExpr, error, trueGraph) = self.expr(predExpr)

                if error:
                    return (tokens, True, {})

                exprs.append(trueGraph)
                # next condition is optional
                if trueExpr[0].t() == "T_RBRACKET":
                    # must have only a condition for the predicate being true
                    newGraph["T_IF"] = exprs
                    return (trueExpr[1:], False, newGraph)
                else:
                    # try for another expression

                    (otherwiseExpr, error, otherwiseGraph) = self.expr(trueExpr)

                    if not error and otherwiseExpr[0].t() == "T_RBRACKET":
                        exprs.append(otherwiseGraph)
                        newGraph["T_IF"] = exprs
                        return (otherwiseExpr[1:], False, newGraph)
                    else:
                        return (tokens, True, {})
            else:
                return (tokens, True, {})
        else:
            return (tokens, True, {})

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
