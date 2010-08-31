#!/usr/bin/env python
# encoding: utf-8
"""
book.py

Created by George Sudarkoff on 2010-08-29.
Copyright (c) 2010 George Sudarkoff. All rights reserved.
"""

import os
import sys
import optparse
import glob
import inspect

parser = None
description = 'Book management script.'
epilog = 'Available commands:'


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class InvalidOperation(Exception): pass

class RuntimeError(Exception):
    def __init__(self, msg):
        self.msg = msg


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
        self.options = opts

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
# Book class incapsulates meta information about the book
# -----------------------------------------------------------------------------
class Book(object):
    def __init__(self, path=".", file_extension=".txt"):
        self.path = path
        self.file_extension = file_extension

    def stats(self):
        # set all the counters to zero
        self.lines = 0
        self.blanklines = 0
        self.sentences = 0
        self.words = 0

        for infile in glob.glob(os.path.join(self.path, '*' + self.file_extension)):
            try:
                textf = open(infile, 'r')
            except IOError:
                print 'Cannot open file %s for reading' % filename
                import sys
                sys.exit(0)

            # reads one line at a time
            for line in textf:
                self.lines += 1

                if line.startswith('\n'):
                    self.blanklines += 1
                else:
                    # assume that each sentence ends with . or ! or ?
                    # so simply count these characters
                    self.sentences += line.count('.') + line.count('!') + line.count('?')

                    # create a list of words
                    # use None to split at any whitespace regardless of length
                    # so for instance double space counts as one space
                    tempwords = line.split(None)
                    # word total count
                    self.words += len(tempwords)

            textf.close()
            self.pages = self.words / 300

        return (self.lines, self.blanklines, self.sentences, self.words, self.pages)


# -----------------------------------------------------------------------------
# Concrete operations
# -----------------------------------------------------------------------------
class Help(Operation):
    notes = 'Display help.'

    def invoke(self):
        lines = []
        lines.append("\n  Available Commands:")

        parser.print_help()

        for key, opClass in opsDict.items():
            args = opClass.args()
            usageString = "%s %s" % (opClass.name(), opClass.usage or args)
            lines.append('    %-19s %s' % (usageString, opClass.notes))

        print '\n'.join(lines)


class Stats(Operation):
    notes = 'Display various text stats.'

    def invoke(self, book_path):
        book = Book(book_path)
        lines, blanklines, sentences, words, pages = book.stats()

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
        if self.options.output_file is None:
            raise Usage("--output-file= not specified.")
        try:
            outfile = open(self.options.output_file, 'w')
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
        argv = sys.argv[1:]
    try:
        global parser
        parser = optparse.OptionParser("usage: %prog [options] command [arguments...]")
        parser.allow_interspersed_args = False
        parser.add_option("-v",
            action="store_true", dest="verbose",
            help="Verbose")

        outputFormatOptGroup = optparse.OptionGroup(parser, 'Output Format Options')
        outputFormatOptGroup.add_option(
            "--output-file",
            action="store", dest="output_file", metavar="OUTPUT",
            help="Output file name")
        outputFormatOptGroup.add_option(
           "--format",
           action="store", dest="format", metavar="FORMAT",
           type="choice", choices=['txt', 'html', 'epub'],
           default='txt',
           help="Output format (txt, html, epub)")
        parser.add_option_group(outputFormatOptGroup)

        opts, args = parser.parse_args(argv)

        # Perform requested operation
        operation = getOperationFromArgs(opts, args)
        if not operation:
            raise InvalidOperation()

        processedArgs = processArgs(opts, args)
        result = operation.invoke(*processedArgs)

    except Usage, err:
        sys.stderr.write("Usage error: %s\n\n" % str(err.msg))
        help = Help(opts)
        help.invoke()
        return 2

    except RuntimeError, err:
        sys.stderr.write("Runtime error: %s\n\n" % str(err.msg))
        return 3

    except InvalidOperation:
        sys.stderr.write("Invalid operation.\n")
        help = Help(opts)
        help.invoke()
        return 4

if __name__ == "__main__":
    sys.exit(main())
