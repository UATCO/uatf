from collections import abc


class ListIterator(abc.Iterator):
    def __init__(self, element, size):
        self._element = element
        self._size = size
        self._cursor = 0

    def __next__(self):
        if self._cursor >= self._size:
            raise StopIteration()
        self._cursor += 1
        return self._element.item(self._cursor)
