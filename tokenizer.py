#!/usr/bin/python

# TODO: put this in some sort of util class
#
# goes to last character inclusive, ASCII only
def characterList(startChar, endChar):
    return list(map(chr, list(range(ord(startChar), ord(endChar) + 1))))

class NFA:
    def __init__(self):
        self._curState = 'start'
        self._lastState = 'start'
        self._rules = {'start': {}, 'fail': {}, 'blackhole': {}}
        
    def addState(self, id):
        self._rules[id] = {}
                
    def addTransition(self, c, idFrom, idTo):
        if self._rules.get(idFrom) != None and self._rules.get(idTo) != None:
            self._rules[idFrom][c] = idTo
        
    # modified the state based on the current character
    def read(self, c):
        if self._curState == 'fail':
            self._lastState = 'fail'
            return
        
        possibleTransitions = self._rules[self._curState]
        
        self._lastState = self._curState
        if possibleTransitions.get(c) != None:
            self._curState = possibleTransitions[c]
        else:
            self._curState = 'fail'
    
    def unread(self):
        if self._curState == 'blackhole':
            return
        else:
            self._curState = self._lastState
            self._lastState = 'double_unread_unknown_state'
            
    def inAcceptingState(self):
        return self._curState[0:2] == "T_"

    def inBlackhole(self):
        return self._curState == 'blackhole'
        
    def inFailState(self):
        return self._curState == 'fail' or self._curState == 'blackhole'
        
    def inStartState(self):
        return self._curState == 'start'
        
    def reset(self):
        self._curState = 'start'
        self._lastState = 'start'
        
    def __str__(self):
        return self._curState
        
    
class BinopNFA(NFA):
    def __init__(self):
        NFA.__init__(self)
        
        self.addState('T_PLUS')
        self.addTransition('+', 'start', 'T_PLUS')
        
        self.addState('T_MINUS')
        self.addTransition('-', 'start', 'T_MINUS')
        
        self.addState('T_MULT')
        self.addTransition('*', 'start', 'T_MULT')
        
        self.addState('T_DIV')
        self.addTransition('/', 'start', 'T_DIV')
        
        self.addState('T_MOD')
        self.addTransition('%', 'start', 'T_MOD')
        
        self.addState('T_EXP')
        self.addTransition('^', 'start', 'T_EXP')
        
        self.addState('T_NOT')
        self.addState('T_NOTEQ')
        self.addTransition('!', 'start', 'T_NOT')
        self.addTransition('=', 'T_NOT', 'T_NOTEQ')
        
        self.addState('colon')
        self.addTransition(':', 'start', 'colon')
        self.addState('T_EQ')
        self.addTransition('=', 'colon', 'T_EQ')
        
        self.addState('T_LT')
        self.addState('T_LTEQ')
        self.addTransition('<', 'start', 'T_LT')
        self.addTransition('=', 'T_LT', 'T_LTEQ')
        self.addTransition('>', 'T_LT', 'T_NOTEQ')
        
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

        for i in characterList('a', 'z'):
            self.addTransition(i, 'T_INT', 'blackhole')
            
        for i in characterList('A', 'Z'):
            self.addTransition(i, 'T_INT', 'blackhole')

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
        allowedChars = characterList(' ', '~')
        del allowedChars[ord('\\') - ord(' ')]
        del allowedChars[ord('"') - ord(' ')]
        
        for c in allowedChars:
            self.addTransition(c, 'regular_char', 'regular_char')
            
        for c in ['\\', '"', 'b', 'n', 't']:
            self.addTransition(c, 'backslash_delim', 'regular_char')
            
class IdentifierNFA(NFA):
    def __init__(self):
        NFA.__init__(self)
        
        self.addState('T_ID')
        
        allowedInIds = characterList('A', 'Z') + characterList('a', 'z') + [ord('_')]
        for c in allowedInIds:
            self.addTransition(c, 'start', 'T_ID')
            self.addTransition(c, 'T_ID', 'T_ID')
            
         # can't start with a number
        for c in characterList('0', '9'):
            self.addTransition(c, 'T_ID', 'T_ID')

class Tokenizer:
    def __init__(self, file_str):
        self._file_str = file_str
        self._tokens = []
        
        # NOTE: set order of NFAs to precedence desired (typesNFA before identifierNFA, etc)
        self._nfas = [IntegerNFA(), BinopNFA(), StringConstNFA(), IdentifierNFA()]
        
    def resetNFAs(self):
        for nfa in self._nfas:
            nfa.reset()
            
    def unreadNFAs(self):
        for nfa in self._nfas:
            nfa.unread()
            
    def endOfToken(self, i):
        if len(self._file_str) - 1 == i:
            return True
        else:
            return self._file_str[i + 1] in [' ', '\t', '\n', '\r']

    # advance current token to next non-whitespace character
    def skipToNextToken(self, idx):
        i = idx
        while i < len(self._file_str) and (self._file_str[i] in [' ', '\t', '\n', '\r']):
            i += 1
            
        return i
            
    def skipOverToken(self, idx):
        i = idx
        while i < len(self._file_str) and (self._file_str[i] not in [' ', '\t', '\n', '\r']):
            i += 1
            
        if i == len(self._file_str) - 1:
            return -1
        else:
            return i
                
    def tokenize(self):
        i = 0
        i = self.skipToNextToken(i)
        while i < len(self._file_str):
            c = self._file_str[i]
                
            # read the current character
            failedNFAs = 0
            acceptingNFAs = 0
            for nfa in self._nfas:
                nfa.read(c)
                
                if nfa.inFailState():
                    failedNFAs += 1
                    
                if nfa.inAcceptingState():
                    acceptingNFAs += 1

            # did this new char cause all NFAs to fail?
            if failedNFAs == len(self._nfas):
                # unread this char from all NFAs, look for the first NFA to accept and declare that the token
                
                self.unreadNFAs()
                
                # see if any accept after the unread
                found = False
                foundBlackhole = False
                for nfa in self._nfas:
                    # only use the first accepting NFA
                    if nfa.inAcceptingState() and not found:
                        found = True
                        self._tokens.append(str(nfa))

                    if nfa.inBlackhole():
                        foundBlackhole = True

                if not found:
                    self._tokens.append("T_INVALID")
                    return self._tokens
                
                # skip to the next possible token
                i = self.skipToNextToken(i + 1)
                self.resetNFAs()
                
                if not found:
                    i = self.skipOverToken(i + 1)
                    if i < 0:
                        break
            else:
                # at least one NFA still accepting, continue
                i += 1
        
        # done reading input, see if any of the NFAs are accepting
        
        inStartState = 0
        for nfa in self._nfas:
            if nfa.inStartState():
                inStartState += 1
            elif nfa.inAcceptingState():
                self._tokens.append(str(nfa))
                return self._tokens
                
        if inStartState != len(self._nfas):
            # some extra not fully formed token exists, emit error
            self._tokens.append("T_INVALID")
            
        return self._tokens
        
def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage tokenizer.py <filename>")
    else:
        f = open(sys.argv[1], "r")
        t = Tokenizer(f.read())
        toks = t.tokenize()
        
        for tok in toks:
            print(tok)
        
if __name__ == "__main__":
    main()
