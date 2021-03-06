from IBTLTrans.DFA import DFA
from IBTLTrans.Utils import Utils

notAllowedInIds = Utils.Utils.characterList('"', '\'') + [',', '/', ':', ';', '?', '@', '\\', '`', '~', '|', '{', '}']
notAllowedInNums = ['_'] + notAllowedInIds

class ExpressionDFA(DFA):
    def __init__(self):
        DFA.__init__(self)
        
        self.addState('T_RBRACKET')
        self.addState('T_LBRACKET')
        
        self.addTransition('[', 'start', 'T_LBRACKET')
        self.addTransition(']', 'start', 'T_RBRACKET')

class BinopDFA(DFA):
    def __init__(self):
        DFA.__init__(self)
        
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
        
        self.addState('T_ASSIGN')
        self.addState('T_EQ')
        self.addState('colon')
        self.addTransition(':', 'start', 'colon')
        self.addTransition('=', 'colon', 'T_ASSIGN')
        self.addTransition('=', 'start', 'T_EQ')
        
        self.addState('T_LT')
        self.addState('T_LTEQ')
        self.addTransition('<', 'start', 'T_LT')
        self.addTransition('=', 'T_LT', 'T_LTEQ')
        self.addTransition('>', 'T_LT', 'T_NOTEQ')
        
        self.addState('T_GT')
        self.addState('T_GTEQ')
        self.addTransition('>', 'start', 'T_GT')
        self.addTransition('=', 'T_GT', 'T_GTEQ')

class FloatDFA(DFA):
    def __init__(self):
        DFA.__init__(self)
        self.storeText(True)

        self.addState('LeftFloat')
        self.addState('RightFloat')
        self.addState('T_FLOAT')
        self.addState('exponent')
        self.addState('exponent_negative')

        self.addTransition('.', 'start', 'RightFloat')

        for c in Utils.Utils.characterList('0', '9'):
            self.addTransition(c, 'RightFloat', 'T_FLOAT')
            self.addTransition(c, 'start', 'LeftFloat')
            self.addTransition(c, 'LeftFloat', 'LeftFloat')

        self.addTransition('.', 'LeftFloat', 'T_FLOAT')
        self.addTransition('e', 'LeftFloat', 'exponent')

        for c in Utils.Utils.characterList('0', '9'):
            self.addTransition(c, 'T_FLOAT', 'T_FLOAT')

        self.addTransition('e', 'T_FLOAT', 'exponent')
        self.addTransition('-', 'exponent', 'exponent_negative')
        
        self.addAlternateEndState("exponent_accept", "T_FLOAT")
        for c in Utils.Utils.characterList('0', '9'):
            self.addTransition(c, 'exponent_negative', 'exponent_accept')
            self.addTransition(c, 'exponent', 'exponent_accept')
            self.addTransition(c, 'exponent_accept', 'exponent_accept')

class IdentifierDFA(DFA):
    def __init__(self):
        DFA.__init__(self)
        self.storeText(True)
        
        self.addState('T_ID')
        
        allowedInIds = Utils.Utils.characterList('A', 'Z') + Utils.Utils.characterList('a', 'z') + [ord('_')]
        for c in allowedInIds:
            self.addTransition(c, 'start', 'T_ID')
            self.addTransition(c, 'T_ID', 'T_ID')
            
        # can't start with a number
        for c in Utils.Utils.characterList('0', '9'):
            self.addTransition(c, 'T_ID', 'T_ID')

class IntegerDFA(DFA):
    def __init__(self):
        DFA.__init__(self)
        self.storeText(True)
        
        self.addState('T_INT')
        
        for i in range(0, 10):
            self.addTransition(str(i), 'start', 'T_INT')
            self.addTransition(str(i), 'T_INT', 'T_INT')

class KeywordDFA(DFA):
    def __init__(self, keyword, finalstate=None):
        DFA.__init__(self)
        self._keyword = keyword

        if finalstate == None:
            finalstate = 'T_%s' % keyword.upper()

        self.addAcceptingString(keyword, finalstate)

class StringConstDFA(DFA):
    def __init__(self):
        DFA.__init__(self)
        self.storeText(True)
        
        self.addState('T_CONSTSTR')
        self.addState('regular_char')
        self.addState('backslash_delim')
        
        self.addTransition('"', 'start', 'regular_char')
        self.addTransition('"', 'regular_char', 'T_CONSTSTR')
        self.addTransition('\\', 'regular_char', 'backslash_delim')
        
        # stay in regular_char with any character except " or \
        allowedChars = Utils.Utils.characterList(' ', '~')
        del allowedChars[ord('\\') - ord(' ')]
        del allowedChars[ord('"') - ord(' ')]
        
        for c in allowedChars:
            self.addTransition(c, 'regular_char', 'regular_char')
            
        for c in ['\\', '"', 'b', 'n', 't', 'r']:
            self.addTransition(c, 'backslash_delim', 'regular_char')
