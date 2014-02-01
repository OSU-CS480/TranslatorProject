class Utils(object):
    # goes to last character inclusive, ASCII only

    @classmethod
    def characterList(cls, startChar, endChar):
        return list(map(chr, list(range(ord(startChar), ord(endChar) + 1))))
