#!/usr/bin/python

import os
import glob

topLevelDir = "IBTLTrans"
testingDir = "tests"
testDataDir = "testing_data"

def main():
    import sys

    if len(sys.argv) < 2:
        print("usage: ./runtests.py <test_suite>")
    else:
        name = sys.argv[1].lower()

        if name == "tokenizer":
            files = glob.glob(os.sep.join([topLevelDir, testingDir, name, testDataDir, '*']))
            files.sort()

            inputFiles = filter(lambda x: x[-3:] == "txt", files)
            answerFiles = filter(lambda x: x[-3:] == "ans", files)

            if (len(inputFiles) != len(answerFiles)) or len(inputFiles) == 0:
                print("Missing an answer file (.ans) or input file (.txt)")
            else:
                from IBTLTrans.Stages.Tokenizer import Tokenizer

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
                    # lenghts are not necessarily the same
                    # the input file could have some extra tokens after 
                    # an invalid token

                    print("Starting test fixture: %s" % fixtureName)
                    failed = False
                    for i in range(0, len(tokens)):
                        if tokens[i] != answers[i]:
                            print("Mismatched token %d: got %s, correct %s" % (i, tokens[i], answers[i]))
                            failed = True
                            break
                        else:
                            print("Matched token %d: %s" % (i, tokens[i]))

                            if tokens[i] == "T_INVALID":
                                break

                    if not failed:
                        print("Test fixture succeeded")
                    else:
                        print("Test fixture failed")
                print("Test suite complete")
if __name__ == "__main__":
    main()
