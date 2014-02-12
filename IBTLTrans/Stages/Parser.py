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
        # TODO
        
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
            
    def exprPrime(self, tokens):
    