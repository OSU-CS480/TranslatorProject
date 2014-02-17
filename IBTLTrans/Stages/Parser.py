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
        if not error and tokens[0].t() == "T_RBRACKET" and len(tokens) == 1:
            self._graph["T"] = graph
            return True

        return False
        
    def s(self, tokens, prime=False):
        # check for right bracket / left bracket
        if tokens[0].t() == "T_LBRACKET" and tokens[1].t() == "T_RBRACKET":
            (sPrimeToks, error, sPrimeGraph) = self.s(tokens[2:], True)
            newGraph = {}
            if prime:
                newGraph["S'"] = [{"S'": []}, {"S'": sPrimeGraph}]
            else:
                newGraph["S"] = [{"S": []}, {"S'": sPrimeGraph}]

            return (sPrimeToks, error, newGraph)
        else:
            # try expr S'

            (exprToks, error, exprGraph) = self.expr(tokens)

            if not error:
                (sPrimeToks, error, sPrimeGraph) = self.s(exprToks, True)
                return (sPrimeToks, error, {"S": [exprGraph, sPrimeGraph]})

            # try [S] S'
            if tokens[0].t() == "T_LBRACKET":
                (sToks, error, sGraph) = self.s(tokens[1:])
                if not error:
                    if sToks[0].t() == "T_RBRACKET":
                        (sPrimeToks, error, sPrimeGraph) = self.s(sToks[1:], True)
                        newGraph = {}
                        if prime:
                            newGraph["S'"] = [{"S": [sGraph]}, {"S'": sPrimeGraph}]
                        else:
                            newGraph["S"] = [{"S": [sGraph]}, {"S'": sPrimeGraph}]

                        return (sPrimeToks, error, newGraph)

            if prime:
                return (tokens, False, {"e": []})
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

        return (tokens, True, {})

    def oper(self, tokens):
        newGraph = {}
        exprs = []

        if tokens[0].t() == "T_LBRACKET":
            # Case 1: [T_ASSIGN T_ID oper]
            if tokens[1].t() == "T_ASSIGN" and tokens[2].t() == "T_ID":
                exprs.append({"T_ID": tokens[2].text()})
                (operToks, error, operGraph) = self.oper(tokens[3:])

                if error:
                    # Error parsing for oper
                    return (tokens, True, operGraph)
                else:
                    # Sucessful parse of case 1
                    if operToks[0].t() == "T_RBRACKET":
                        exprs.append(operGraph)
                        newGraph["T_ASSIGN"] = exprs
                        return (operToks[1:], False, newGraph)
                    else:
                        return (operToks, True, {})

            elif self.binopPred(tokens[1].t()):
                # Case 2: [binop oper oper]
                (operToks, error, operGraph) = self.oper(tokens[2:])
                if error:
                    # Error parsing 
                    return (tokens, True, {})
                exprs.append(operGraph)

                (operToks2, error, operGraph2) = self.oper(operToks)

                if error:
                    # Error parsing the second oper production
                    return(tokens, True, {})

                # Check for right bracket
                if operToks2[0].t() == "T_RBRACKET":
                    exprs.append(operGraph2)
                    newGraph[tokens[1].t()] = exprs
                    return (operToks2[1:], False, newGraph)
                else:
                    return (tokens, True, {})

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
                        return (tokens, True, {})
            else:
                return (tokens, True, {})
                        
        # no left bracket
        elif self.constPred(tokens[0].t()):
            # Case 4: consts
            newGraph[tokens[0].t()] = tokens[0].text()
            return (tokens[1:], False, newGraph)

        elif tokens[0].t() == "T_ID":
            newGraph[tokens[0].t()] = tokens[0].text()
            return(tokens[1:], False, newGraph)
        else:
            return (tokens, True, {})

    def stmt(self, tokens):
        newGraph = {}
        exprs = []

        if tokens[0].t() != "T_LBRACKET":
            return (tokens, True, {})

        if self.startOfStmtPred(tokens[1].t()):
            if tokens[1].t() == "T_STDOUT":
                (exprToks, error, exprGraph) = self.expr(tokens[2:], True)

                if error:
                    return (tokens, True, {})
                else:
                    if exprToks[0].t() == "T_RBRACKET":
                        exprs.append(exprGraph)
                        newGraph["T_STDOUT"] = exprs
                        return (exprToks[1:], False, newGraph)
                    else:
                        return (tokens, True, {})
            elif tokens[1].t() == "T_LET":
                # get the predicate
                if tokens[2].t() == "T_LBRACKET":
                    (varToks, error, varGraph) = self.varList(tokens[3:])

                    if not error and varToks[0].t() == "T_RBRACKET" and varToks[1].t() == "T_RBRACKET":
                        exprs.append(varGraph)
                        newGraph["T_LET"] = exprs
                        return (varToks[2:], False, newGraph)
                    else:
                        return (tokens, True, {})

                else:
                    return (tokens, True, {})
                
            elif tokens[1].t() == "T_WHILE":
                # get the predicate 
                (predExpr, error, predGraph) = self.expr(tokens[2:])
            
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
                
            elif tokens[1].t() == "T_IF":
                # get the predicate

                (predExpr, error, predGraph) = self.expr(tokens[2:])

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
