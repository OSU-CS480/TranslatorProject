#!/usr/bin/python

import sys

from IBTLTrans.Stages.Tokenizer import Tokenizer
from IBTLTrans.Stages.Parser import Parser
from IBTLTrans.Utils.Utils import Utils
        
def main():    
    if len(sys.argv) < 2:
        print("Usage translator.py <filename> [--lex,--ast]")
    else:

        # read some command swittches
        showTokens = False
        showAst = True
        if "--lex" in sys.argv:
            showTokens = True
        
        if "--ast" in sys.argv:
            showAst = True

        f = open(sys.argv[1], "r")
        t = Tokenizer(f.read())
        toks = t.tokenize()
        
        if showTokens:
            for tok in toks:
                print(tok)

        # parser
        p = Parser(toks)
        if p.parse():
            if showAst:
                print(p.getAstStr())
            
            return 0
        else:
            print("Parser failed to parse the string")
            return 1

        f.close()
        
if __name__ == "__main__":
    main()
