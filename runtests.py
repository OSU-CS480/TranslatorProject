#!/usr/bin/python

from IBTLTrans.Token import Token

import subprocess as sub
import tempfile
import os
import glob

topLevelDir = "IBTLTrans"
testingDir = "tests"
testDataDir = "testing_data"

def main():
    import sys

    if len(sys.argv) < 2:
        print("usage: ./runtests.py <test_suite> [--verbose]")
    else:
        name = sys.argv[1].lower()
        
        verbose = "--verbose" in sys.argv

        if name == "tokenizer":
            files = glob.glob(os.sep.join([topLevelDir, testingDir, name, testDataDir, '*']))
            files.sort()

            inputFiles = filter(lambda x: x[-3:] == "txt", files)
            answerFiles = filter(lambda x: x[-3:] == "ans", files)

            if (len(inputFiles) != len(answerFiles)) or len(inputFiles) == 0:
                print("Missing an answer file (.ans) or input file (.txt)")
            else:
                from IBTLTrans.Stages.Tokenizer import Tokenizer
                
                # run failure test first
                failureTestFile = open(os.sep.join([topLevelDir, testingDir, name, testDataDir, 'failure_tests']), 'r')
                badTokens = failureTestFile.read().split('~')

                print("Starting failure test for bad tokens")
                count = 0
                countInvalid = 0
                for tok in badTokens:
                    t = Tokenizer(tok)
                    ans = t.tokenize()
                    count += 1

                    if ans[0].t() != 'T_INVALID':
                        print("Expected T_INVALID on `%s', got %s" % (tok, ans))
                        countInvalid += 1

                print("Failure test completed. Of %d tokens %d were marked incorrectly\n" % (count, countInvalid))

                for i in range(0, len(inputFiles)):
                    # tokenize input
                    inputFile = open(inputFiles[i], "r")
                    t = Tokenizer(inputFile.read())
                    inputFile.close()
                    fixtureName = inputFiles[i][inputFiles[i].rfind('/') + 1:-4]

                    tokens = t.tokenize()

                    # read from answers
                    answerFile = open(answerFiles[i], "r")
                    answers = answerFile.read().split(" ")
                    answerFile.close()

                    # compare
                    # lengths are not necessarily the same
                    # the input file could have some extra tokens after 
                    # an invalid token

                    print("Starting test fixture: %s" % fixtureName)
                    failed = False
                    for i in range(0, len(tokens)):
                        if tokens[i].t() != answers[i]:
                            print("Mismatched token %d: got %s, correct %s" % (i, tokens[i].t(), answers[i]))
                            failed = True
                        else:
                            print("Matched token %d: %s" % (i, tokens[i].t()))

                            if tokens[i].t() == "T_INVALID":
                                break

                    if not failed:
                        print("Test fixture succeeded\n")
                    else:
                        print("Test fixture failed\n")
                print("Test suite complete")
        elif name == "parser":
            files = glob.glob(os.sep.join([topLevelDir, testingDir, name, testDataDir, '*']))
            files.sort()

            inputFiles = filter(lambda x: x[-3:] == "txt", files)
            answerFiles = filter(lambda x: x[-3:] == "ans", files)
            failureFiles = filter(lambda x: x[-4:] == "fail", files)

            if (len(inputFiles) != len(answerFiles)) or len(inputFiles) == 0:
                print("Missing an answer file (.ans) or input file (.txt)")
            else:
                from IBTLTrans.Stages.Tokenizer import Tokenizer
                from IBTLTrans.Stages.Parser import Parser

                # run failure tests, if any
                failCount = 0
                for failFile in failureFiles:
                    fileHandle = open(failFile, "r")
                    fileContents = fileHandle.read()
                    t = Tokenizer(fileContents)
                    fileHandle.close()
                    tokens = t.tokenize()

                    p = Parser(tokens)
                    p.parse()
                    pt = p.getParseTree()

                    if verbose:
                        print("Reading in failure file %s:\n%s\n" % (failFile, fileContents))

                    if pt != {}:
                        failCount += 1
                        print("Input parsed when it shouldn't have\nInput: %s\nParse tree generated: %s\n" % (fileContents, str(p)))

                        if verbose:
                            print("Parse tree parsed is %s" % str(p))
                    else:
                        if verbose:
                            print("Input failed to parse, successfully")

                if failCount != 0:
                    print("%d out of %d files succeeded when they shouldn't have\n" % (failCount, len(failureFiles)))
                else:
                    print("Failure test cases succeeded\n")

                print("Starting parser test fixture")
                failCount = 0
                for i in range(0, len(inputFiles)):
                    # tokenize input
                    inputFile = open(inputFiles[i], "r")
                    contents = inputFile.read()
                    t = Tokenizer(contents)
                    inputFile.close()
                    fixtureName = inputFiles[i][inputFiles[i].rfind('/') + 1:-4]
                    tokens = t.tokenize()

                    p = Parser(tokens)
                    p.parse()

                    # removing whitespace
                    # stackoverflow.com/a/3739939/854854
                    pt = str(p)
                    pt = "".join(pt.split())

                    if verbose:
                        print("Reading in file %s:\n%s\n" % (inputFiles[i], contents))

                    # read from answers
                    answerFile = open(answerFiles[i], "r")
                    answer = answerFile.read()

                    answer = "".join(answer.split())
                    answerFile.close()

                    # compar
                    if pt != answer:
                        failCount += 1
                        print("parse tree returned did not match the answer file")
                        print("correct is: %s" % answer)

                        if verbose:
                            print("parse tree generated was: %s" % pt)
                    else:
                        if verbose:
                            print("parse tree generated (matches answer file): %s" % pt)
                            print("\n")

                if failCount != 0:
                    print("Parser test fixture failed. %d out of %d failed" % (failCount, len(inputFiles)))
                else:
                    print("Parser test fixture succeeded")
        elif name == "constexprs" or name == "semantics":
            files = glob.glob(os.sep.join([topLevelDir, testingDir, name, testDataDir, '*']))
            files.sort()

            inputFiles = filter(lambda x: x[-3:] == "txt", files)
            answerFiles = filter(lambda x: x[-3:] == "ans", files)
            failureFiles = filter(lambda x: x[-4:] == "fail", files)

            if (len(inputFiles) != len(answerFiles)) or len(inputFiles) == 0:
                print("Missing an answer file (.ans) or input file (.txt)")
            else:
                from IBTLTrans.Stages.Tokenizer import Tokenizer
                from IBTLTrans.Stages.Parser import Parser
                from IBTLTrans.Stages.TypeChecker import TypeChecker
                from IBTLTrans.Stages.ForthGen import ForthGen

                # run failure tests, if any
                failCount = 0
                for failFile in failureFiles:
                    fileHandle = open(failFile, "r")
                    fileContents = fileHandle.read()

                    if verbose:
                        print("Reading in failure file %s:\n%s\n" % (failFile, fileContents))

                    t = Tokenizer(fileContents)
                    fileHandle.close()
                    tokens = t.tokenize()

                    p = Parser(tokens)
                    p.parse()
                    tc = TypeChecker(p.getParseTree())

                    if tc.generateAST():
                        failCount += 1
                        print("Type checker succeeded when it shouldn't have")

                        if verbose:
                            print("AST generated is %s" % str(tc))
                    else:
                            print("AST could not be generated, successfully")

                if failCount != 0:
                    print("%d out of %d files succeeded when they shouldn't have\n" % (failCount, len(failureFiles)))
                else:
                    print("Failure test cases succeeded\n")

                print("Starting %s test fixture" % name)
                failCount = 0
                for i in range(0, len(inputFiles)):
                    # tokenize input
                    inputFile = open(inputFiles[i], "r")
                    contents = inputFile.read()

                    if verbose:
                        print("Reading in file %s:\n%s\n" % (inputFiles[i], contents))

                    t = Tokenizer(contents)
                    inputFile.close()
                    fixtureName = inputFiles[i][inputFiles[i].rfind('/') + 1:-4]
                    tokens = t.tokenize()

                    p = Parser(tokens)
                    if not p.parse():
                        print("Failed: could not parse the input")
                        failCount += 1
                        continue

                    tc = TypeChecker(p.getParseTree())

                    if not tc.generateAST():
                        print("There were type errors in this input file")
                        failCount += 1
                    else:
                        forth = ForthGen(tc)

                        if not forth.toForth():
                            print("Could not generate Forth code for this input")
                            failCount += 1
                        else:
                            forth.addBye()

                            answerFile = open(answerFiles[i], "r")
                            answer = answerFile.read()
                            answerFile.close()

                            # bye for byte comparison with generated forth code
                            if answer == forth.getForth():
                                if verbose:
                                    print("Forth code matched")
                            else:
                                failCount += 1

                                print("Forth code generated did not match answer file")
                                if verbose:
                                    print("Forth generated is\n%s" % forth.getForth())
                                    print("Answer file is\n%s" % answer)

                if failCount != 0:
                    print("%s test fixture failed. %d out of %d failed" % (name, failCount, len(inputFiles)))
                else:
                    print("%s test fixture succeeded" % name)
        else:
            print("Could not find test suite %s" % name)

if __name__ == "__main__":
    main()
