#!/usr/bin/python

import os
import sys
import subprocess
import tempfile

from IBTLTrans.Stages.Tokenizer import Tokenizer
from IBTLTrans.Stages.Parser import Parser
from IBTLTrans.Stages.TypeChecker import TypeChecker
from IBTLTrans.Stages.ForthGen import ForthGen
from IBTLTrans.Utils.Utils import Utils
        
def main():    
    if len(sys.argv) < 2 and sys.stdin.isatty():
        print("Usage translator.py <filename> [--lex,--parse,--ast, --forth]")
        print("\t--lex: show tokens\n\t--ast: show the abstract syntax tree generated")
        print("\t--parse: show parse tree\n\t--forth: show the forth code that is generated\n\t--halt: don't run the generated code")
    else:

        # read some command swittches
        showTokens = False
        showAst = False
        showForthCode = False
        stayInRepl = False # if true, don't add a bye to the outputted code
        showParseTree = False
        runForthCode = True

        if "--lex" in sys.argv:
            showTokens = True

        if "--repl" in sys.argv:
            stayInRepl = True
        
        if "--ast" in sys.argv:
            showAst = True

        if "--forth" in sys.argv:
            showForthCode = True

        if "--parse" in sys.argv:
            showParseTree = True

        if "--halt" in sys.argv:
            runForthCode = False

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
            print("Tokens:")
            for tok in toks:
                print(tok)

        # parse input
        p = Parser(toks)
        if p.parse():
            if showParseTree:
                print("Parse tree:")
                print(p)
        else:
            print("Parser failed to parse the string")
            return 1

        # generate perform type checking
        typeCheck = TypeChecker(p.getParseTree())

        if not typeCheck.generateAST():
            print("Could not generate AST")
            return 1

        if showAst:
            print("AST:")
            print(typeCheck)

        # get Forth code
        forth = ForthGen(typeCheck)
        if not forth.toForth():
            print("Code could not generate Forth code from input")
            return 1

        if not stayInRepl:
            forth.addBye()

        if showForthCode:
            print("Forth code:")
            print(forth.getForth())

        if runForthCode:
            # create new tempfile with forth code in it
            tempForth = tempfile.NamedTemporaryFile(delete=False)
            tempForth.write(forth.getForth())
            tempForth.close()

            # send to Gforth to execute
            returnVal = subprocess.call(["gforth", tempForth.name])

            os.unlink(tempForth.name) # delete the temp file
            return returnVal
        else:
            return 0

if __name__ == "__main__":
    main()
