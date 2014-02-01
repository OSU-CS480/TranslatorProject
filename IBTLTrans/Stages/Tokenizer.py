from IBTLTrans import NFA
from IBTLTrans.NFAs import *

class Tokenizer:
    def __init__(self, file_str):
        self._file_str = file_str
        self._tokens = []
        
        # NOTE: set order of NFAs to precedence desired (typesNFA before identifierNFA, etc)
        
        # these are all of the NFAs that are comprised of only a single keyword
        self._keywords = ['string', 'float', 'int', 'bool', 'while', 'if', 'else', 'true', 'false', 'stdout', 'let', 'tan', 'cos', 'sin', 'not', 'and', 'or']
        
        self._single_keyword_nfas = []
        for key in self._keywords:
            self._single_keyword_nfas.append(KeywordNFA(key))
            
        # the list of all NFAs
        self._nfas = [IntegerNFA()] + self._single_keyword_nfas + [BinopNFA(), ExpressionNFA(), StringConstNFA(), IdentifierNFA()]
        
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
                for nfa in self._nfas:
                    # only use the first accepting NFA
                    if nfa.inAcceptingState() and not found:
                        found = True
                        self._tokens.append(str(nfa))

                if not found:
                    self._tokens.append("T_INVALID")
                    return self._tokens
                
                # skip to the next possible token
                i = self.skipToNextToken(i + 1)
                self.resetNFAs()
                
                # done with this token, skip until the next whitespace
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
