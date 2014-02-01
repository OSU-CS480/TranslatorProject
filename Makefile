#--------------------------------------------
# INSTRUCTION
# Quoted strings are to be filled in by student
#

TRANSLATOR_CMD=./translator.py
TEST_CMD=./runtests.py

stutest.out:
	tail -n +1 -- IBTLTrans/tests/tokenizer/testing_data/*.txt
	$(TEST_CMD) tokenizer > stutest.out

proftest.out:
	cat $(PROFTEST)
	$(TRANSLATOR_CMD) $(PROFTEST) > proftest.out
	cat proftest.out
