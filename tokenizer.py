class NFA:
	def __init__(self):
		self._curState = 'start'
		self._rules = {'start': {}, 'fail': {}}
		
	def addState(self, id):
		self._rules[id] = {}
				
	def addTransition(self, c, idFrom, idTo):
		if self._rules.get(idFrom) != None and self._rules.get(idTo) != None:
			self._rules[idFrom][c] = idTo
		
	# modified the state based on the current character
	def read(self, c):
		if self._curState == 'fail':
			return
			
		possibleTransitions = self._rules[self._curState]
		
		if possibleTransitions.get(c) != None:
			self._curState = possibleTransitions[c]
		else:
			self._curState = 'fail'
			
	def inAcceptingState(self):
		return self._curState[0:2] == "T_"
		
	def reset(self):
		self._curState = 'start'
		
	def __str__(self):
		return self._curState
		
	
class BinopNFA(NFA):
	def __init__(self):
		NFA.__init__(self)
		
		self.addState('T_PLUS')
		self.addTransition('+', 'start', 'T_PLUS')
		
		self.addState('colon')
		self.addTransition(':', 'start', 'colon')
		self.addState('T_EQ')
		self.addTransition('=', 'colon', 'T_EQ')
		
		self.addState('T_LT')
		self.addState('T_LTEQ')
		self.addTransition('<', 'start', 'T_LT')
		self.addTransition('=', 'T_LT', 'T_LTEQ')
		
		self.addState('T_GT')
		self.addState('T_GTEQ')
		self.addTransition('>', 'start', 'T_GT')
		self.addTransition('=', 'T_GT', 'T_GTEQ')
		
		# TODO: add simply way to add states for strings
		self.addState('o')
		self.addState('T_OR')
		self.addTransition('o', 'start', 'o')
		self.addTransition('r', 'o', 'T_OR')

class IntegerNFA(NFA):
	def __init__(self):
		NFA.__init__(self)
		
		self.addState('T_INT')
		self.addState('is_negative')
		
		self.addTransition('-', 'start', 'is_negative')
		
		for i in range(0, 10):
			self.addTransition(str(i), 'start', 'T_INT')
			self.addTransition(str(i), 'is_negative', 'T_INT')
			self.addTransition(str(i), 'T_INT', 'T_INT')

class StringConstNFA(NFA):
	def __init__(self):
		NFA.__init__(self)
		
		self.addState('T_CONSTSTR')
		self.addState('regular_char')
		self.addState('backslash_delim')
		
		self.addTransition('"', 'start', 'regular_char')
		self.addTransition('"', 'regular_char', 'T_CONSTSTR')
		self.addTransition('\\', 'regular_char', 'backslash_delim')
		
		# stay in regular_char with any character except " or \
		allowedChars = list(map(chr, list(range(ord(' '), ord('~') + 1))))
		del allowedChars[ord('\\') - ord(' ')]
		del allowedChars[ord('"') - ord(' ')]
		
		for c in allowedChars:
			self.addTransition(c, 'regular_char', 'regular_char')
			
		for c in ['\\', 'b', 'n', 't']:
			self.addTransition(c, 'backslash_delim', 'regular_char')

class Tokenizer:
	def __init__(self, file_str):
		self._file_str = file_str
		
		# NOTE: set order of NFAs to precedence desired (typesNFA before identifierNFA, etc)
		self._nfas = [BinopNFA(), IntegerNFA(), StringConstNFA()]
		
	# see which NFAs accepted
	def checkCompletedToken(self):
		inAnyState = False
		for nfa in self._nfas:
			if nfa.inAcceptingState():
			
				if not inAnyState:
					print(nfa)
					
				inAnyState = True # already have determined this lexeme
			nfa.reset()
						
		if not inAnyState:
			print("Invalid, last in: %s" % nfa)
				
	def start(self):
		#for c in self._file_str:
		i = 0
		while i < len(self._file_str):
			c = self._file_str[i]
			
			if i == len(self._file_str) - 1: # EOF
				if c != ' ' or c != '\t' or c != '\n':
					for nfa in self._nfas:
						nfa.read(c)
				break
			
			if c == ' ' or c == '\t' or c == '\n': # consume all whitespaces to the whitespace right before the next token
				while(self._file_str[i + 1] == ' ' or \
				self._file_str[i + 1] == '\t' or \
				self._file_str[i + 1] == '\n'):
					if i == len(self._file_str) - 1:
						break
					i += 1
					
				# read all NFAs for Accept state
				# consume white space and manually continue
				
				self.checkCompletedToken()
				
			else:
				# lex the next character
				for nfa in self._nfas:
					nfa.read(c)
			i += 1
		
		# done reading the file, see which NFAs are finalized
		self.checkCompletedToken()
		
def main():
	import sys
	
	if len(sys.argv) != 2:
		print("Usage tokenizer.py <filename>")
	else:
		f = open(sys.argv[1], "r")
		t = Tokenizer(f.read())
		t.start()
		
if __name__ == "__main__":
	main()