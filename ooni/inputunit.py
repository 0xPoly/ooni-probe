#-*- coding: utf-8 -*-
#
# inputunit.py 
# -------------
# IN here we have functions related to the creation of input
# units. Input units are how the inputs to be fed to tests are
# split up into.
#
# :authors: Arturo Filastò
# :license: see included LICENSE file


class InputUnitFactory(object):
    """
    This is a factory that takes the size of input units to be generated a set
    of units that is a python iterable item and outputs InputUnit objects
    containing inputUnitSize elements.

    This object is a python iterable, this means that it does not need to keep
    all the elements in memory to be able to produce InputUnits.
    """
    inputUnitSize = 10
    def __init__(self, inputs=[]):
        self._inputs = iter(inputs)
        self._idx = 0
        self._ended = False

    def __iter__(self):
        return self

    def next(self):
        input_unit_elements = []

        if self._ended:
            raise StopIteration

        for i in xrange(self._idx, self._idx + self.inputUnitSize):
            try:
                input_unit_elements.append(self._inputs.next())
            except StopIteration:
                self._ended = True
                break
        self._idx += self.inputUnitSize

        if not input_unit_elements:
            raise StopIteration

        return InputUnit(input_unit_elements)

class InputUnit(object):
    """
    This is a python iterable object that contains the input elements to be
    passed onto a TestCase.
    """
    def __init__(self, inputs=[]):
        self._inputs = iter(inputs)

    def __repr__(self):
        return "<%s inputs=%s>" % (self.__class__, self._inputs)

    def __add__(self, inputs):
        for input in inputs:
            self._inputs.append(input)

    def __iter__(self):
        return self

    def next(self):
        return self._inputs.next()

    def append(self, input):
        self._inputs.append(input)

