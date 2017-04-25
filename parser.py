class CodeSpace(object):
    def __init__(self, lines):
        """

        :param lines:

        :type lines: Iterator[Iterator[int]]
        """
        self._lines = []
        for line in lines:
            self._lines.append([self.disassamble(c)
                                for c in line])
        self._height = len(self._lines)
        self._width = max(len(line) for line in self._lines)

    @classmethod
    def disassamble(cls, charcode):
        """

        :param charcode:
        :return:

        :type charcode: int
        :rtype: Union[(int, int, int), None]
        """
        if 0xAC00 <= charcode <= 0xD7A3:
            n = charcode - 0xAC00
            return n // 588, n // 28 % 21, n % 28
        return None

    def __getitem__(self, item):
        """

        :param item:
        :return:

        :type item: (int, int)
        :rtype: Union[(int, int, int), None]
        """
        row, col = item
        if 0 <= row < self._height:
            if 0 <= col < len(self._lines[row]):
                return self._lines[row][col]
        raise KeyError()

    def __contains__(self, item):
        """

        :param item:
        :return:

        :type item: (int, int)
        :rtype: bool
        """
        row, col = item
        if 0 <= row < self._height:
            if 0 <= col < len(self._lines[row]):
                return True
        return False


def parse(source):
    """
    :param source: aheui source code in unicode string
    :return: CodeSpace object

    :type source: str
    :rtype: CodeSpace
    """
    return CodeSpace([ord(c) for c in line]
                     for line in source.split(u'\n'))
