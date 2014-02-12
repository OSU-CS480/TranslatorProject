class Parser():

    def __init__(self, tokens):
        self._tokens = tokens
        
    # this is the T production in revisedgrammar.txt
     def parse(self):
        (tokens, error) = s(self._tokens)
        
        return not error
        
    def s(self, tokens):
        (exprToks, error) = expr(tokens)
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
                return s(exprToks)
            
    def expr(self, tokens):
        (numexprToks, error) = numexpr(tokens)
        
        if error:
            # must not be an integer expression
            (strexprToks, error) = strexpr(tokens)

            if error:
                (boolexprToks, error) = boolexpr(tokens)

                if error:
                    (stmtToks, error) = stmt(tokens)

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

            if numbinop:
                # toks[1:] must be succeeded by 2 numexprs
            elif numunop:
                # toks[1:] must be succeeded by 1 numexpr
            else:
                # return up an error
                return (tokens, True)

    
    # 
    # PREDICATES
    #
    def numbinop(self, token):
        return token in ["T_PLUS", "T_MINUS", "T_MULT", "T_DIV", "T_MOD", "T_EXP"]
        
    def numunop(self, token):
        return token in ["T_MINUS", "T_SIN", "T_COS", "T_TAN"]
    
