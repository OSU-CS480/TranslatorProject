#--------------------------------------------
# INSTRUCTION
# Quoted strings are to be filled in by student
#

TRANSLATOR_CMD=./translator.py
TEST_CMD=./runtests.py

stutest.out:
	$(TEST_CMD) constexprs --verbose > stutest.out

proftest.out:
	cat $(PROFTEST)
	$(TRANSLATOR_CMD) $(PROFTEST) > proftest.out
	cat proftest.out
