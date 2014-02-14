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
            
    def expr(self, tokens, prime=False):
        newGraph = {}
        exprs = []

        # expr' specific productions
        if prime:
            if self.constPred(tokens[0].t()):
                newGraph[tokens[0].t()] = tokens[0].text()
                return (tokens[1:], False, newGraph)
            elif tokens[0].t() == "T_ID":
                newGraph["T_ID"] = tokens[0].text()
                return (tokens[1:], False, newGraph)

        # if expr' (prime set to True) hasn't returned by here, must be some sort of expression
        if tokens[0].t() != "T_LBRACKET":
            return (tokens, True, {})

        # could be an assignment
        if tokens[1].t() == "T_ASSIGN":
            # in expr' assignment is not allowed
            if prime:
                return (tokens, True, {})

            (exprToks, error, exprGraph) = self.expr(tokens[2:], True)

            if error:
                return (tokens, True, {})
            else:
                # an identifier must follow
                if exprToks[0].t() != "T_ID" or exprToks[1].t() != "T_RBRACKET":
                    return (tokens, True, {})
                else:
                    newGraph["T_ASSIGN"] = [exprGraph, exprToks[0].text()]
                    return (exprToks[1:-1], error, newGraph)

        # either statement, binop, or unop

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
                (predExpr, error, predGraph) = self.expr(tokens[2:], True)
                
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
                (predExpr, error, predGraph) = self.expr(tokens[2:], True)

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

        # checking for binop or unop

        # T_MINUS can be either, one or more expressions may follow
        if tokens[1].t() == "T_MINUS":
            (expr1Toks, error, expr1Graph) = self.expr(tokens[2:], True)

            if error:
                # error on first expression, not the right production
                return (tokens, True, {})
                
            exprs.append(expr1Graph)
            (expr2Toks, error, expr2Graph) = self.expr(expr2Toks, True)
            
            if error:
                # could have meant the unop version of -

                if expr1Toks[0].t() == "T_RBRACKET":
                    newGraph["T_MINUS"] = exprs
                    return (expr1Toks[1:], False, newGraph)
                else:
                    return (tokens, True, {})
            else:
                # binop verion of -
                if expr2Toks[0].t() == "T_RBRACKET":
                    exprs.append(expr2Graph)
                    newGraph["T_MINUS"] = exprs
                    return (expr2Toks[1:], False, newGraph)
                else:
                    return (tokens, True, {})
        else:
            if self.binopPred(tokens[1].t()):
                # strictly binary operation

                (expr1Toks, error, expr1Graph) = self.expr(tokens[2:], True)

                if error:
                    return (tokens, True, {})
                
                exprs.append(expr1Graph)
                (expr2Toks, error, expr2Graph) = self.expr(expr1Toks, True)
                
                if error:
                    return (tokens, True, {})
                else:
                    if expr2Toks[0].t() == "T_RBRACKET":
                        exprs.append(expr2Graph)
                        newGraph[tokens[1].t()] = exprs
                        return (expr2Toks[1:], error, newGraph)
                    else:
                        return (tokens, True, {})
            else:
                # strictly unary operation

                (exprToks, error, exprGraph) = self.expr(tokens[2:], True)

                if error:
                    # error on first expression, not the right production
                    return (tokens, True, {})
                else:
                    if exprToks[0].t() == "T_RBRACKET":
                        exprs.append(exprGraph)
                        newGraph[tokens[1].t()] = exprs
                        return (exprToks[1:], error, newGraph)
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
