class Parser():

    def __init__(self, tokens):
        self._tokens = tokens
        
    # this is the T production in revisedgrammar.txt
     def parse(self):
        (tokens, error) = s(self._tokens)
        
        return not error
        
    def s(self, tokens):
        (exprRet, error) = expr(tokens)
        if exprRet == [] and not error:
            # done parsing
            return ([], False)
        else:
            # more to parse
            return s(exprRet)
            
    def expr(self, tokens):
        intexprRet = intexpr(tokens)
        if intexprRet == []:
            return []

        floatexprRet = floatexprRet(intexprRet)
        if floatexprRet == []:
            return []

        strexprRet = strexpr(floatexprRet)
        if strexprRet == []:
            return []
        
        boolexprRet = boolexpr(strexprRet)
        if boolexprRet == []:
            return []

        stmtRet = stmt(boolexprRet)
        if stmtRet == []:
            return []

    def intexpr(self, tokens):
        if tokens[0] != "T_LBRACKET":
            return tokens # failed, try next expression
        
        if intbinop(tokens[1]):
            intexprRet = intexpr(tokens[2:])
            if intexprRet == []:
                return []

    
    # accepted integer binops
    def intbinop(self, token):
        token in ["T_PLUS", "T_MINUS", "T_MULT", "T_DIV", "T_MOD", "T_EXP"]
        
    def intunop(self, token):
        token in ["T_MINUS", "T_SIN", "T_COS", "T_TAN"]
    
