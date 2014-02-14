class Token:
    def __init__(self, t, text=None):
        self._type = t
        self._text = text

    def __str__(self):
        return self._type

    def t(self):
        return self._type
    def text(self):
        return self._text
