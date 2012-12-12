#-*- coding: utf-8 -*-
#
# inputunit.py 
# -------------
# IN here we have functions related to the creation of input
# units. Input units are how the inputs to be fed to tests are
# split up into.
#
# :authors: Arturo Filastò, Isis Lovecruft
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
    length = None
    def __init__(self, inputs=[]):
        """
        Args:
            inputs (iterable): inputs *must* be an iterable.
        """
        self._inputs = iter(inputs)
        self.inputs = iter(inputs)
        self._ended = False

    def __iter__(self):
        return self

    def __len__(self):
        """
        Returns the number of input units in the input unit factory.
        """
        if not self.length:
            self.length = sum(1 for _ in self._inputs)/self.inputUnitSize
        return self.length

    def next(self):
        input_unit_elements = []

        if self._ended:
            raise StopIteration

        for i in xrange(self.inputUnitSize):
            try:
                input_unit_elements.append(self.inputs.next())
            except StopIteration:
                self._ended = True
                break

        if not input_unit_elements:
            raise StopIteration

        return InputUnit(input_unit_elements)

class InputUnit(object):
    """
    This is a python iterable object that contains the input elements to be
    passed onto a :class:`ooni.nettest.NetTestCase`.
    """
    def __init__(self, inputs=[]):
        """
        Create an iterable from a list of inputs, which can be given to a NetTestCase.

        @param inputs: A list of inputs for a NetTestCase.
        """
        self._inputs = iter(inputs)
        # _inputs_copy is to avoid stealing things from
        # the iterator when __repr__ is called:
        self._inputs_copy = inputs

    def __str__(self):
        """Prints the original input list."""
        return "<%s inputs=%s>" % (self.__class__, self._inputs_copy)

    def __add__(self, inputs):
        """Add a list of inputs to the iterator."""
        for i in inputs:
            self._inputs.append(i)

    def __iter__(self):
        """Self explanatory."""
        return self

    def next(self):
        """Return the next item from the InputUnit iterator."""
        return self._inputs.next()

    def append(self, input):
        """Add an item to the end of the InputUnit iterator."""
        self._inputs.append(input)

