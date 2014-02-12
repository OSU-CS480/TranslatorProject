from IBTLTrans.DFA import DFA
from IBTLTrans.Utils import Utils

notAllowedInIds = Utils.Utils.characterList('"', '\'') + [',', '/', ':', ';', '?', '@', '\\', '`', '~', '|', '{', '}']
notAllowedInNums = ['!', '_'] + notAllowedInIds

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

class FloatDFA(DFA):
    def __init__(self):
        DFA.__init__(self)

        self.addState('LeftFloat')

        for c in Utils.Utils.characterList('0', '9'):
            self.addTransition(c, 'start', 'LeftFloat')

        for c in Utils.Utils.characterList('0', '9'):
            self.addTransition(c, 'LeftFloat', 'LeftFloat')

        self.addState('T_FLOAT')
        self.addTransition('.', 'LeftFloat', 'T_FLOAT')

        for c in Utils.Utils.characterList('0', '9'):
            self.addTransition(c, 'T_FLOAT', 'T_FLOAT')

        self.addTransition('.', 'T_FLOAT', 'blackhole')

        for i in Utils.Utils.characterList('a', 'z'):
            self.addTransition(i, 'T_FLOAT', 'blackhole')
            
        for i in Utils.Utils.characterList('A', 'Z'):
            self.addTransition(i, 'T_FLOAT', 'blackhole')

        for c in notAllowedInNums:
            self.addTransition(c, 'T_FLOAT', 'blackhole')

class IdentifierDFA(DFA):
    def __init__(self):
        DFA.__init__(self)
        
        self.addState('T_ID')
        
        allowedInIds = Utils.Utils.characterList('A', 'Z') + Utils.Utils.characterList('a', 'z') + [ord('_')]
        for c in allowedInIds:
            self.addTransition(c, 'start', 'T_ID')
            self.addTransition(c, 'T_ID', 'T_ID')
            
        # can't start with a number
        for c in Utils.Utils.characterList('0', '9'):
            self.addTransition(c, 'T_ID', 'T_ID')

        self.addTransition('.', 'T_ID', 'blackhole')

        for c in notAllowedInIds:
            self.addTransition(c, 'T_ID', 'blackhole')

class IntegerDFA(DFA):
    def __init__(self):
        DFA.__init__(self)
        
        self.addState('T_INT')
        self.addState('is_negative')
        
        self.addTransition('-', 'start', 'is_negative')
        
        for i in range(0, 10):
            self.addTransition(str(i), 'start', 'T_INT')
            self.addTransition(str(i), 'is_negative', 'T_INT')
            self.addTransition(str(i), 'T_INT', 'T_INT')

        for i in Utils.Utils.characterList('a', 'z'):
            self.addTransition(i, 'T_INT', 'blackhole')
            
        for i in Utils.Utils.characterList('A', 'Z'):
            self.addTransition(i, 'T_INT', 'blackhole')

        for c in notAllowedInNums:
            self.addTransition(c, 'T_INT', 'blackhole')

class KeywordDFA(DFA):
    def __init__(self, keyword):
        DFA.__init__(self)
        self._keyword = keyword
        self.addAcceptingString(keyword, 'T_%s' % keyword.upper())

class StringConstDFA(DFA):
    def __init__(self):
        DFA.__init__(self)
        
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
