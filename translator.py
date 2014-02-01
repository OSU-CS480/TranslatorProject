#!/usr/bin/python

import sys

from IBTLTrans.Stages.Tokenizer import Tokenizer
from IBTLTrans.Utils.Utils import Utils
        
def main():    
    if len(sys.argv) != 2:
        print("Usage tokenizer.py <filename>")
    else:
        f = open(sys.argv[1], "r")
        t = Tokenizer(f.read())
        toks = t.tokenize()
        
        for tok in toks:
            print(tok)

        f.close()
        
if __name__ == "__main__":
    main()
