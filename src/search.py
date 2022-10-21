'''
The search.py module implements the functionality for the word search
'''

from collections import namedtuple

_DIRECTIONS = [
    (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, -1), (-1, 1)
]

FoundSearch = namedtuple('FoundSearch', ['r', 'c', 'dx', 'dy'])

class Searcher:
    def __init__(self, contents: [[str]]) -> None:
        self._contents = contents

    def search(self, word) -> ([FoundSearch] or None):
        '''
        Searches for a word in the grid and returns the
        coordinates and direction of the found location
        '''
        finds = []
        if len(word) == 0:
            return
        for r in range(len(self._contents)):
            for c in range(len(self._contents[r])):
                if self._contents[r][c] == word[0]:
                    result = self._search_at_location(r, c, word)
                    if result:
                        dx, dy = result
                        finds.append(FoundSearch(r=r, c=c, dx=dx, dy=dy))
        return finds if len(finds) > 0 else None

    def _search_at_location(self, r, c, word) -> (int, int):
        '''
        Searches for a word in every direction within a coordinate
        '''
        for dx, dy in _DIRECTIONS:
            if self._search_direction(0, r, c, word, dx, dy):
                return dx, dy
        return None

    def _search_direction(self, ind: int, r: int, c: int, word: str, dx: int, dy: int) -> bool:
        '''
        Recursively searches for a word in a given direction
        '''
        # print(f'ind: {ind} r, c: {(r, c)}, word: {word}, dx, dy: {dx, dy}')
        if (r < 0 or c < 0) or \
                (r >= len(self._contents)) or (c >= len(self._contents[r])) or \
                ind == len(word) or word[ind] != self._contents[r][c]:  # out of range
            return False
        if ind == len(word) - 1 and word[ind] == self._contents[r][c]:  # reached end (base case)
            return True
        return True and self._search_direction(ind + 1, r + dy, c + dx, word, dx, dy)


if __name__ == '__main__':
    m = \
        [['a', 'b', 'c', 'd'],
         ['e', 'f', 'g', 'h'],
         ['a', 'b', 'd', 'd'],
         ['b', 'c', 'g', 'd']]
    s = Searcher(m)
    print(s.search('dd'))
