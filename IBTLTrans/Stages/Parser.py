class Parser:
    def __init__(self, tokens):
        self._tokens = tokens
    
    # this is the T production in revisedgrammar.txt
    def parse(self):
        (tokens, error) = self.s(self._tokens)

        if not error:
            print("parser succeeded")
        else:
            print("parser failed: %s" % tokens)
        
        return not error
        
    def s(self, tokens):
        (exprToks, error) = self.expr(tokens)
        if error:
            # nothing else to do for this production, return up an error
            return (tokens, True)
        else:
            # no error, continue or return up
            
            if exprToks == []:
                # return up no error, parsing complete
                return ([], False)
            else:
                # continue consuming tokens, if possible
                return self.s(exprToks)
            
    def expr(self, tokens):
        (numexprToks, error) = self.numexpr(tokens)
        
        if error:
            # must not be an integer expression
            (strexprToks, error) = self.strexpr(tokens)

            if error:
                (boolexprToks, error) = self.boolexpr(tokens)

                if error:
                    (stmtToks, error) = self.stmt(tokens)

                    if error:
                        # return up an error
                        return (tokens, False)
                    else:
                        # return up a found statement
                        return (stmtToks, error)
                else:
                    return (boolexprToks, error)
            else:
                return (strexprToks, error)
        else:
            return (numexprToks, error)

    def numexpr(self, tokens):
        if tokens[0] != "T_LBRACKET":
            # must be either an integer or an identifier

            if tokens[0] != "T_INT" and tokens[0] != "T_FLOAT":
                # has to be an identifier

                if tokens[0] != "T_ID":
                    # return up an error
                    return (tokens, True)
                else:
                    return (tokens[1:], False)
            else:
                # both cases (int or float) will remove one terminal
                return (tokens[1:], False)
        else:
            # either a unary operation or binary operation

            toks = tokens[1:]

            if self.numbinopPred(toks[0]) and self.numunopPred(toks[0]):
                # must be one of the operators both have in common, see how many exprs can be attained

                (numexpr1Toks, error) = self.numexpr(toks[1:])
                if error:
                    # not a valid numexpr
                    return (tokens, True)
                else:
                    # try getting another expression out of it
                    (numexpr2Toks, error) = self.numexpr(numexpr1Toks)
                    if error:
                        # must be a unop
                        
                        if numexpr1Toks[0] == "T_RBRACKET":
                            return (numexpr1Toks[1:], False)
                        else:
                            # statement not properly closed
                            return (tokens, True)
                    else:
                        # must be a binop

                        if numexpr2Toks[0] == "T_RBRACKET":
                            return (numexpr2Toks[1:], False)
                        else:
                            # statement not properly closed
                            return (tokens, True)
            else:
                if self.numbinopPred(toks[0]):
                    (numexpr1Toks, error) = self.numexpr(toks[1:])
                    if error:
                        return (tokens, True)

                    (numexpr2Toks, error) = self.numexpr(numexpr1Toks)
                    if error:
                        return (tokens, True)
                    if numexpr2Toks[0] == "T_RBRACKET":
                        return (numexpr2Toks[1:], False)
                    else:
                        return (tokens, True)
                elif self.numunopPred(toks[0]):
                    (numexpr1Toks, error) = self.numexpr(toks[1:])
                    
                    if error:
                        return (tokens, True)
                    else:
                        # check for right bracket
                        if numexpr1Toks[0] == "T_RBRACKET":
                            return (numexpr1Tok[1:], False)
                        else:
                            return (tokens, True)
                else:
                    return (tokens, False)
    
    def strexpr(self, tokens):
        if tokens[0] == "T_LBRACKET":
            if tokens[1] != "T_PLUS":
                return (tokens, True)

            (strexpr1Toks, error) = self.strexpr(tokens[2:])
            if error:
                return (tokens, True)

            (strexpr2Toks, error) = self.strexpr(strexpr1Toks)
            if error:
                return (tokens, True)
            
            if strexpr2Toks[0] == "T_RBRACKET":
                return (strexpr2Toks[1:], False)
            else:
                return (tokens, True)
        elif tokens[0] == "T_CONSTSTR":
            return (tokens[1:], False)
        elif tokens[0] == "T_ID":
            return (tokens[1:], False)
        else:
            return (tokens, True)
    # 
    # PREDICATES
    #
    def numbinopPred(self, token):
        return token in ["T_PLUS", "T_MINUS", "T_MULT", "T_DIV", "T_MOD", "T_EXP"]
        
    def numunopPred(self, token):
        return token in ["T_MINUS", "T_SIN", "T_COS", "T_TAN"]
    
