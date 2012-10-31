# -*- encoding: utf-8 -*-
#
# :authors: Arturo "hellais" Filastò <art@fuffa.org>
# :licence: see LICENSE

import sys
import os
import itertools
import traceback

from twisted.trial import unittest, itrial, util
from twisted.internet import defer, utils
from twisted.python import usage

from ooni.utils import log

pyunit = __import__('unittest')

class InputTestSuite(pyunit.TestSuite):
    """
    This in an extension of a unittest test suite. It adds support for inputs
    and the tracking of current index via idx.
    """

    # This is used to keep track of the tests that are associated with our
    # special test suite
    _tests = None
    def run(self, result, idx=0):
        log.debug("Running test suite")
        self._idx = idx
        while self._tests:
            if result.shouldStop:
                log.debug("Detected that test should stop")
                log.debug("Stopping...")
                break
            test = self._tests.pop(0)

            try:
                log.debug("Setting test attributes with %s %s" %
                            (self.input, self._idx))

                test.input = self.input
                test._idx = self._idx
            except Exception, e:
                log.debug("Error in setting test attributes")
                log.debug("This is probably because the test case you are "\
                          "running is not a nettest")
                log.debug(e)

            log.debug("Running test")
            # XXX we may want in a future to put all of these tests inside of a
            # thread pool and run them all in parallel
            test(result)
            log.debug("Ran.")

            self._idx += 1
        return result


class TestCase(unittest.TestCase):
    """
    This is the monad of the OONI nettest universe. When you write a nettest
    you will subclass this object.

    * inputs: can be set to a static set of inputs. All the tests (the methods
      starting with the "test_" prefix) will be run once per input.  At every
      run the _input_ attribute of the TestCase instance will be set to the
      value of the current iteration over inputs.  Any python iterable object
      can be set to inputs.

    * inputFile: attribute should be set to an array containing the command
      line argument that should be used as the input file. Such array looks
      like this:

          ``["commandlinearg", "c", "The description"]``

      The second value of such arrray is the shorthand for the command line
      arg.  The user will then be able to specify inputs to the test via:

          ``ooniprobe mytest.py --commandlinearg path/to/file.txt``

      or

          ``ooniprobe mytest.py -c path/to/file.txt``


    * inputProcessor: should be set to a function that takes as argument an
      open file descriptor and it will yield the input to be passed to the
      test instance.

    * name: should be set to the name of the test.

    * author: should contain the name and contact details for the test author.
      The format for such string is as follows:

          ``The Name <email@example.com>``

    * version: is the version string of the test.
    """
    name = "I Did Not Change The Name"
    author = "Jane Doe <foo@example.com>"
    version = "0"

    inputFile = None
    inputs    = [None]

    report = {}
    report['errors'] = []

    optParameters = None
    optFlags      = None
    subCommands   = None

    def deferSetUp(self, ignored, result):
        """
        If we have the reporterFactory set we need to write the header. If
        such method is not present we will only run the test skipping header
        writing.
        """
        if result.reporterFactory.firstrun:
            log.debug("Detecting first run. Writing report header.")
            d1 = result.reporterFactory.writeHeader()
            d2 = unittest.TestCase.deferSetUp(self, ignored, result)
            dl = defer.DeferredList([d1, d2])
            return dl
        else:
            log.debug("Not first run. Running test setup directly")
            return unittest.TestCase.deferSetUp(self, ignored, result)

    def inputProcessor(self, fp):
        log.debug("Running default input processor")
        for x in fp.readlines():
            yield x.strip()
        fp.close()

    def getOptions(self):
        log.debug("Getting options for test")
        if self.inputFile:
            try:
                fp = open(self.inputFile) ## xxx fixme:
            except Exception, e:          ## bad news to leave file
                log.err(e)                ## descriptors open
            else:
                from_file = self.__input_file_processor__(fp)
                self.inputs = itertools.chain(processor, from_file)
        elif self.inputFile is False:
            log.debug("%s specified that it doesn't need inputFile."
                      % self.__class__.__name__)
            self.inputs = processed
        else:
            raise BrokenImplementation

        return self.inputs

    def getOptions(self):
        '''
        for attr in attributes:
            if not attr.name is 'optParameters' or attr.name is 'optFlags':
                continue
            elif attr.name is 'optParameters':
                cls._optParameters = attr.object
            elif attr.name is 'optFlags':
                log.debug("Applying %s.%s = %s to data descriptor..."
                          % (cls.__name__, "_"+attr.name, attr.object))
                cls._optParameters = attr.object
            else:
                log.debug("How did we get here? attr.name = %s" % attr.name)
        '''
        if self.localOptions:
            if self.inputs[0] is not None or self.inputFile is not None:
                self.__get_inputs__()
            return self.localOptions
        else:
            raise Exception, "could not find cls.localOptions! 234"

        # if options:
        #     return options
        # else:
        #     ## is this safe to do? it might turn Hofstaeder...
        #     return self.__dict__
        ####################
        ## original return
        ####################
        #return {'inputs': self.inputs,
        #        'name': self.name,
        #        'version': self.version}

    def __repr__(self):
        return "<%s inputs=%s>" % (self.__class__, self.inputs)

