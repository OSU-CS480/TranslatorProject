import pprint

class Parser:
    def __init__(self, tokens):
        self._graph = {}
        self._tokens = tokens

    def __str__(self):
        if self._graph != {}:
            return pprint.pformat(self._graph)
        else:
            return self._remainingTokens
    
    # this is the T production in revisedgrammar.txt
    def parse(self):
        (tokens, error, graph) = self.s(self._tokens, {})

        if not error:
            self._graph["PROG"] = graph
        else:
            self._remainingTokens = tokens

        return not error
        
    def s(self, tokens, graph):
        (exprToks, error, exprGraph) = self.expr(tokens, graph)
        if error:
            # nothing else to do for this production, return up an error
            return (tokens, True, graph)
        else:
            # no error, continue or return up
            exprs = [exprGraph] # can be one or two for this production
            
            if exprToks == []:
                # return up no error, parsing complete
                newGraph = {}
                newGraph["s"] = exprs
                return ([], False, newGraph)
            else:
                # continue consuming tokens, if possible
                (sToks, error, sGraph) = self.s(exprToks, graph)

                if error:
                    return (tokens, error, graph)
                else:
                    exprs.append(sGraph)
                    newGraph = {}
                    newGraph["s"] = exprs
                    return (sToks, error, newGraph)
            
    def expr(self, tokens, graph, prime=False):
        newGraph = {}
        exprs = []

        # expr' specific productions
        if prime:
            if self.constPred(tokens[0]):
                newGraph[tokens[0]] = "some const"
                return (tokens[1:], False, newGraph)
            elif tokens[0] == "T_ID":
                newGraph["T_ID"] = "some id"
                return (tokens[1:], False, newGraph)

        # if expr' (prime set to True) hasn't returned by here, must be some sort of expression
        if tokens[0] != "T_LBRACKET":
            return (tokens, True, graph)

        # could be an assignment
        if tokens[1] == "T_ASSIGN":
            # in expr' assignment is not allowed
            if prime:
                return (tokens, True, graph)

            (exprToks, error, exprGraph) = self.expr(tokens[2:], graph, True)

            if error:
                return (tokens, True, graph)
            else:
                # an identifier must follow
                if exprToks[0] != "T_ID" or exprToks[1] != "T_RBRACKET":
                    return (tokens, True, graph)
                else:
                    newGraph["assign"] = [exprGraph, "id (assign)"]
                    return (exprToks[1:-1], error, newGraph)
        else:
            # must be binop or unop

            # T_MINUS can be either, one or more expressions may follow
            if tokens[1] == "T_MINUS":
                (expr1Toks, error, expr1Graph) = self.expr(tokens[2:], graph, True)

                if error:
                    # error on first expression, not the right production
                    return (tokens, True, graph)
                
                exprs.append(expr1Graph)
                (expr2Toks, error, expr2Graph) = self.expr(expr2Toks, graph, True)
                
                if error:
                    # could have meant the unop version of -

                    if expr1Toks[0] == "T_RBRACKET":
                        newGraph["T_MINUS"] = exprs
                        return (expr1Toks[1:], False, newGraph)
                    else:
                        return (tokens, True, graph)
                else:
                    # binop verion of -
                    if expr2Toks[0] == "T_RBRACKET":
                        exprs.append(expr2Graph)
                        newGraph["T_MINUS"] = exprs
                        return (expr2Toks[1:], False, newGraph)
                    else:
                        return (tokens, True, graph)
            else:
                if self.binopPred(tokens[1]):
                    # strictly binary operation

                    (expr1Toks, error, expr1Graph) = self.expr(tokens[2:], graph, True)

                    if error:
                        return (tokens, True, graph)
                
                    exprs.append(expr1Graph)
                    (expr2Toks, error, expr2Graph) = self.expr(expr1Toks, graph, True)
                
                    if error:
                        return (tokens, True, graph)
                    else:
                        if expr2Toks[0] == "T_RBRACKET":
                            exprs.append(expr2Graph)
                            newGraph[tokens[1]] = exprs
                            return (expr2Toks[1:], error, newGraph)
                        else:
                            return (tokens, True, graph)
                else:
                    # strictly unary operation

                    (exprToks, error, exprGraph) = self.expr(tokens[2:], graph, True)

                    if error:
                        # error on first expression, not the right production
                        return (tokens, True, graph)
                    else:
                        if exprToks[0] == "T_RBRACKET":
                            exprs.append(exprGraph)
                            newGraph[tokens[1]] = exprs
                            return (exprToks[1:], error, newGraph)
                        else:
                            return (tokens, True, graph)

    # 
    # PREDICATES
    #
    def binopPred(self, token):
        return token in ["T_PLUS", "T_MINUS", "T_MULT", "T_DIV", "T_MOD", "T_EXP"]
        
    def unopPred(self, token):
        return token in ["T_MINUS", "T_SIN", "T_COS", "T_TAN"]
    
    def constPred(self, token):
        return token in ["T_CONSTSTR", "T_BOOL", "T_INT", "T_FLOAT"]

    def typePred(self, token):
        return token in ["T_STRING", "T_BOOLTYPE", "T_INTTYPE", "T_FLOATTYPE"]

    def startOfStmtPred(self, token):
        return token in ["T_LET", "T_WHILE", "T_IF", "T_STDOUT"]
