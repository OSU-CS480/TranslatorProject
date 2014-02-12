class Parser():

    def __init__(self, tokens):
        self._tokens = tokens
        
     def parse(self):
        s()
        return 
        
    def s(self):
        if self._tokens[0] == "T_LPAREN":
            toks = expr(self, self._tokens[1:]
            
            if toks[0] == "T_RPAREN":
                sPrime(self, toks[1:])
            else:
                # error
        else:
            # error
            
    def expr(self, tokens):
        if intbinop(self, tokens[0]):
            toks = intexpr(self, tokens[1:]
            toks = intexpr(self, toks)
        elif intbinop(self, tokens[0]):
            toks = intexpr(self, tokens[1:]
        
    def sPrime(self, tokens):
        if tokens[0] == "T_LPAREN":
            toks = expr(self, tokens[1:]
            
            if toks[0] == "T_RPAREN":
                sPrime(self, toks[1:])
            else:
                # error
        elif tokens[0] == "T_ASSIGN" and tokens[1] == "T_ID":
            exprPrime(self, tokens[2:]
        else:
            # epsilon rule
            return tokens
    
    # accepted integer binops
    def intbinop(self, token):
        token in ["T_PLUS", "T_MINUS", "T_MULT", "T_DIV", "T_MOD", "T_EXP"]
        
    def intunop(self, token):
        token in ["T_MINUS", "T_SIN", "T_COS", "T_TAN"]
    