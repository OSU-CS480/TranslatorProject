#!/usr/bin/python

import sys
import subprocess

from IBTLTrans.Stages.Tokenizer import Tokenizer
from IBTLTrans.Stages.Parser import Parser
from IBTLTrans.Stages.ForthGen import ForthGen
from IBTLTrans.Utils.Utils import Utils
        
def main():    
    if len(sys.argv) < 2 and sys.stdin.isatty():
        print("Usage translator.py <filename> [--lex,--parse,--ast, --forth]")
        print("\t--lex: show tokens\n\t--ast: show the abstract syntax tree generated")
        print("\t--parse: show parse tree\n\t--forth: show the forth code that is generated")
    else:

        # read some command swittches
        showTokens = False
        showAst = False
        showForthCode = True
        showParseTree = False

        if "--lex" in sys.argv:
            showTokens = True
        
        if "--ast" in sys.argv:
            showAst = True

        if "--forth" in sys.argv:
            showForthCode = True

        if "--parse" in sys.argv:
            showParseTree = True

        # stackoverflow.com/a/6024166/854854

        if sys.stdin.isatty():
            f = open(sys.argv[1], "r")
            t = Tokenizer(f.read())
            f.close()
        else:
            t = Tokenizer(sys.stdin.read())

        toks = t.tokenize()
        # see if the last token is an invalid (or if no tokens were parsed)
        if toks == []:
            print("No tokens could be read from the input")
            return 1
        elif toks[-1:][0].t() == "T_INVALID":
            print("Syntax error")
            return 1
        
        # print tokens if the user wants to see them
        if showTokens:
            for tok in toks:
                print(tok)

        # parse input
        p = Parser(toks)
        if p.parse():
            if showParseTree:
                print(p)
        else:
            print("Parser failed to parse the string")
            return 1

        # generate Forth code
        forth = ForthGen(p.getParseTree())

        if not forth.generateAST():
            print("Could not generate AST")
            return 1

        if showAst:
            print(forth.getAST())

        if not forth.generate():
            print("Code could not generate Forth code from input")
            return 1

        if showForthCode:
            print(forth.getForth())

        # send to Gforth to execute
        subprocess.call("echo " + forth.getForth() + " .s | gforth", shell=True)
        return 0

if __name__ == "__main__":
    main()
