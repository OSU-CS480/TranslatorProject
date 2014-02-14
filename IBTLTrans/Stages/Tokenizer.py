from IBTLTrans import DFA
from IBTLTrans.DFAs import *

class Tokenizer:
    def __init__(self, file_str):
        self._file_str = file_str
        self._tokens = []
        
        # NOTE: set order of DFAs to precedence desired (typesDFA before identifierDFA, etc)
        
        # these are all of the DFAs that are comprised of only a single keyword
        self._keywords = ['while', 'if', 'else', 'true', 'false', 'stdout', 'let', 'tan', 'cos', 'sin', 'not', 'and', 'or']

        self._type_keywords = ['string', 'float', 'int', 'bool']
        
        self._single_keyword_dfas = []
        for key in self._keywords:
            self._single_keyword_dfas.append(KeywordDFA(key))

        for key in self._type_keywords:
            self._single_keyword_dfas.append(KeywordDFA(key, 'T_%s' % key.upper() + 'TYPE'))
            
        # the list of all DFAs
        self._dfas = [IntegerDFA(), FloatDFA()] + self._single_keyword_dfas + [BinopDFA(), ExpressionDFA(), StringConstDFA(), IdentifierDFA()]
        
    def resetDFAs(self):
        for dfa in self._dfas:
            dfa.reset()
            
    def unreadDFAs(self):
        for dfa in self._dfas:
            dfa.unread()
            
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
            failedDFAs = 0
            acceptingDFAs = 0
            for dfa in self._dfas:
                dfa.read(c)
                
                if dfa.inFailState():
                    failedDFAs += 1
                    
                if dfa.inAcceptingState():
                    acceptingDFAs += 1

            # did this new char cause all DFAs to fail?
            if failedDFAs == len(self._dfas):
                # unread this char from all DFAs, look for the first DFA to accept and declare that the token
                
                self.unreadDFAs()
                
                # see if any accept after the unread
                found = False
                for dfa in self._dfas:
                    # only use the first accepting DFA
                    if dfa.inAcceptingState() and not found:
                        found = True
                        self._tokens.append(str(dfa))

                if not found:
                    self._tokens.append("T_INVALID")
                    return self._tokens
                
                # skip to the next possible token
                i = self.skipToNextToken(i)
                self.resetDFAs()
                
                # done with this token, skip until the next whitespace
                if not found:
                    i = self.skipOverToken(i)
                    if i < 0:
                        break
            else:
                # at least one DFA still accepting, continue
                i += 1
        
        # done reading input, see if any of the DFAs are accepting
        
        inStartState = 0
        for dfa in self._dfas:
            if dfa.inStartState():
                inStartState += 1
            elif dfa.inAcceptingState():
                self._tokens.append(str(dfa))
                return self._tokens
                
        if inStartState != len(self._dfas):
            # some extra not fully formed token exists, emit error
            self._tokens.append("T_INVALID")
            
        return self._tokens
