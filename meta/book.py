#!/usr/bin/env python
# encoding: utf-8
"""
book.py

Created by George Sudarkoff on 2010-08-29.
Copyright (c) 2010 George Sudarkoff. All rights reserved.
"""

import os
import sys
import getopt
import glob
import inspect


help_message = '''
Book management script.
'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class InvalidOperation(Exception): pass

class RuntimeError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Book(object):
    def __init__(self, path="."):
        self.path = path


# -----------------------------------------------------------------------------
# Operations
# -----------------------------------------------------------------------------

class Operation(object):
    """
    Base class for operations.

    To define new operations, subclass Operation and implement
    an appropriate invoke() method.
    """
    options = ''
    usage = ''
    notes = ''

    def __init__(self, opts):
        self.name = self.__class__.name()
        for option, value in opts:
            if option == "-v":
                self.verbose = True
            if option in ("-o", "--output"):
                self.output = value

    @classmethod
    def name(cls):
        return cls.__name__.lower()

    @classmethod
    def args(operation):
        allArgsStr = inspect.formatargspec(
            *inspect.getargspec(operation.invoke))[1:-1]
        allArgsList = allArgsStr.split(', ')

        return ' '.join(['<%s>' % arg for arg in allArgsList
            if arg not in ['self', 'host', 'vm']])

def getOperationByName(opts, name):
   ## `name` must be a string
   if not hasattr(name, 'endswith'):
       return None

   opClass = opsDict.get(name, None)

   if opClass:
       return opClass(opts)
   else:
       return None

def getOperationFromArgs(opts, args):
  for arg in args:
     operation = getOperationByName(opts, arg)
     if operation: return operation

def processArgs(opts, args):
  return [arg for arg in args if not getOperationByName(opts, arg)]


# -----------------------------------------------------------------------------
# Concrete operations
# -----------------------------------------------------------------------------
class Help(Operation):
    notes = 'Display help.'

    def invoke(self):
        lines = []

        # TODO: print a nice header
        # TODO: print help for available options
        lines.append(help_message)

        for key, opClass in opsDict.items():
            args = opClass.args()
            usageString = "%s %s %s %s" % (
                sys.argv[0].split("/")[-1], opClass.options, opClass.name(), opClass.usage or args)
            lines.append('    %-75s %s' % (usageString, opClass.notes))

        print '\n'.join(lines)


class Stats(Operation):
    notes = 'Display various text stats.'

    def invoke(self, book_path):
        # set all the counters to zero
        lines, blanklines, sentences, words = 0, 0, 0, 0

        for infile in glob.glob(os.path.join(book_path, '*.txt')):
            try:
                # use a text file you have, or google for this one ...
                # TODO: loop through files in a directory
                textf = open(infile, 'r')
            except IOError:
                print 'Cannot open file %s for reading' % filename
                import sys
                sys.exit(0)

            # reads one line at a time
            for line in textf:
                lines += 1

                if line.startswith('\n'):
                    blanklines += 1
                else:
                    # assume that each sentence ends with . or ! or ?
                    # so simply count these characters
                    sentences += line.count('.') + line.count('!') + line.count('?')

                    # create a list of words
                    # use None to split at any whitespace regardless of length
                    # so for instance double space counts as one space
                    tempwords = line.split(None)
                    # word total count
                    words += len(tempwords)

            textf.close()
            pages = words / 300

        print "Lines       :", lines
        print "Blank lines :", blanklines
        print "Sentences   :", sentences
        print "Words       :", words
        print "Pages       :", pages


class Compile(Operation):
    options = '--output=<output file>'
    usage = ''
    notes = 'Assemble the book.'

    def invoke(self, book_path):
        files, lines = 0, 0
        try:
            outfile = open(self.output, 'w')
        except IOError:
            raise RuntimeError('Cannot open file %s for writing' % self.output)

        for infile in glob.glob(os.path.join(book_path, '*.txt')):
            try:
                textf = open(infile, 'r')
                files += 1
            except IOError:
                raise RuntimeError('Cannot open file %s for reading' % infile)

            # copy text to the output file
            text = textf.read()
            outfile.write("[[%s]]\n" % infile)
            outfile.write(text)
            outfile.write("\n\n")
            textf.close()

        outfile.close()


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

globalsDict = dict(globals())
opsDict = dict(
   [(key.lower(), val)
    for key, val in globalsDict.items()
    if hasattr(val, 'invoke')]
   )

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "o:v", [
                "output=",
                "verbose"
            ])
        except getopt.error, msg:
            raise Usage(msg)

        # Perform requested operation
        result = None
        operation = getOperationFromArgs(opts, args)
        if not operation:
            raise InvalidOperation()

        processedArgs = processArgs(opts, args)
        result = operation.invoke(*processedArgs)

    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        help = Help(opts)
        help.invoke()
        return 2

    except RuntimeError, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        return 3

    except InvalidOperation:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": Invalid operation"
        help = Help(opts)
        help.invoke()
        return 4

if __name__ == "__main__":
    sys.exit(main())
