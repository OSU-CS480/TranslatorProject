class DFA:
    def __init__(self):
        self._curState = 'start'
        self._lastState = 'start'
        self._text = ""
        self._storeText = False
        self._rules = {'start': {}, 'fail': {}, 'blackhole': {}}
        
    def addState(self, id):
        self._rules[id] = {}

    # set if this DFA should store text (useful for consts and ids)
    # does not store on default
    def storeText(self, store):
        self._storeText = store
        
    def addAcceptingString(self, str, tokenName):
        for c in str[:-1]:
            self.addState(c)
            
        self.addState(tokenName)
        
        beginningStates = ['start'] + list(str)
        endingStates = list(str[:-1]) + [tokenName]
        for i in range(0, len(str)):
            self.addTransition(str[i], beginningStates[i], endingStates[i])
                
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

            # store back texts only for DFAs that look for consts and ids
            if self._storeText:
                self._text += (c)
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
        self._text = ""

    def text(self):
        return self._text
        
    def __str__(self):
        return self._curState
