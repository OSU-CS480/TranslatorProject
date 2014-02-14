import pprint

class Parser:
    def __init__(self, tokens):
        self._tokens = tokens
    
    # this is the T production in revisedgrammar.txt
    def parse(self):
        (tokens, error, graph) = self.s(self._tokens, {})

        if not error:
            print("parser succeeded")
            newGraph = {}
            newGraph["PROG"] = graph
            pprint.pprint(newGraph)
        else:
            print("parser failed: %s" % tokens)
        
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

    # def numexpr(self, tokens):
    #     if tokens[0] != "T_LBRACKET":
    #         # must be either an integer or an identifier

    #         if tokens[0] != "T_INT" and tokens[0] != "T_FLOAT":
    #             # has to be an identifier

    #             if tokens[0] != "T_ID":
    #                 # return up an error
    #                 return (tokens, True)
    #             else:
    #                 return (tokens[1:], False)
    #         else:
    #             # both cases (int or float) will remove one terminal
    #             return (tokens[1:], False)
    #     else:
    #         # either a unary operation or binary operation

    #         toks = tokens[1:]

    #         if self.numbinopPred(toks[0]) and self.numunopPred(toks[0]):
    #             # must be one of the operators both have in common, see how many exprs can be attained

    #             (numexpr1Toks, error) = self.numexpr(toks[1:])
    #             if error:
    #                 # not a valid numexpr
    #                 return (tokens, True)
    #             else:
    #                 # try getting another expression out of it
    #                 (numexpr2Toks, error) = self.numexpr(numexpr1Toks)
    #                 if error:
    #                     # must be a unop
                        
    #                     if numexpr1Toks[0] == "T_RBRACKET":
    #                         return (numexpr1Toks[1:], False)
    #                     else:
    #                         # statement not properly closed
    #                         return (tokens, True)
    #                 else:
    #                     # must be a binop

    #                     if numexpr2Toks[0] == "T_RBRACKET":
    #                         return (numexpr2Toks[1:], False)
    #                     else:
    #                         # statement not properly closed
    #                         return (tokens, True)
    #         else:
    #             if self.numbinopPred(toks[0]):
    #                 (numexpr1Toks, error) = self.numexpr(toks[1:])
    #                 if error:
    #                     return (tokens, True)

    #                 (numexpr2Toks, error) = self.numexpr(numexpr1Toks)
    #                 if error:
    #                     return (tokens, True)
    #                 if numexpr2Toks[0] == "T_RBRACKET":
    #                     return (numexpr2Toks[1:], False)
    #                 else:
    #                     return (tokens, True)
    #             elif self.numunopPred(toks[0]):
    #                 (numexpr1Toks, error) = self.numexpr(toks[1:])
                    
    #                 if error:
    #                     return (tokens, True)
    #                 else:
    #                     # check for right bracket
    #                     if numexpr1Toks[0] == "T_RBRACKET":
    #                         return (numexpr1Tok[1:], False)
    #                     else:
    #                         return (tokens, True)
    #             else:
    #                 return (tokens, False)
    
    # def strexpr(self, tokens, graph):
    #     if tokens[0] == "T_LBRACKET":
    #         if tokens[1] != "T_PLUS":
    #             return (tokens, True, graph)

    #         (strexpr1Toks, error, g1) = self.strexpr(tokens[2:], graph)
    #         if error:
    #             return (tokens, True, graph)

    #         (strexpr2Toks, error, g2) = self.strexpr(strexpr1Toks, graph)
    #         if error:
    #             return (tokens, True, graph)
            
    #         if strexpr2Toks[0] == "T_RBRACKET":
    #             graph["T_PLUS"]=[g1,g2]
    #             return (strexpr2Toks[1:], False, graph)
    #         else:
    #             return (tokens, True)
    #     elif tokens[0] == "T_CONSTSTR":
    #         return (tokens[1:], False, {"T_CONSTSTR": "a str"})
    #     elif tokens[0] == "T_ID":
    #         return (tokens[1:], False, {"T_ID": "an id"})
    #     else:
    #         return (tokens, True, graph)

    # 
    # PREDICATES
    #
    def binopPred(self, token):
        return token in ["T_PLUS", "T_MINUS", "T_MULT", "T_DIV", "T_MOD", "T_EXP"]
        
    def unopPred(self, token):
        return token in ["T_MINUS", "T_SIN", "T_COS", "T_TAN"]
    
    def constPred(self, token):
        return token in ["T_CONSTSTR", "T_BOOL", "T_INT", "T_FLOAT"]
