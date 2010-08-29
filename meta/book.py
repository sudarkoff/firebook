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


help_message = '''
Book management script.
'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


class Book(object):
    def __init__(self, path="."):
        self.path = path

    def stats(self):
        # set all the counters to zero
        lines, blanklines, sentences, words = 0, 0, 0, 0

        for infile in glob.glob(os.path.join(self.path, '*.txt')):
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

        return (lines, blanklines, sentences, words, pages)

    def combine(self, output_file):
        files, lines = 0, 0
        try:
            self.output = open(output_file, 'w')
        except IOError:
            print 'Cannot open file %s for writing' % output_file
            import sys
            sys.exit(0)

        for infile in glob.glob(os.path.join(self.path, '*.txt')):
            try:
                # use a text file you have, or google for this one ...
                # TODO: loop through files in a directory
                textf = open(infile, 'r')
                files += 1
            except IOError:
                print 'Cannot open file %s for reading' % filename
                import sys
                sys.exit(0)

            # copy text to the output file
            text = textf.read()
            self.output.write("<!-- %s -->\n\n" % infile)
            self.output.write(text)
            self.output.write("\n\n\n")
            textf.close()

        self.output.close()

        return files


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "ho:v", [
                "help",
                "output=",
                "verbose"
            ])
        except getopt.error, msg:
            raise Usage(msg)

        # option processing
        for option, value in opts:
            if option == "-v":
                verbose = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-o", "--output"):
                output = value

        book = Book(argv[1])
        # (lines, blanklines, sentences, words, pages) = book.stats()
        # print "Lines      : ", lines
        # print "Blank lines: ", blanklines
        # print "Sentences  : ", sentences
        # print "Words      : ", words
        # print "Pages      : ", pages

        files = book.combine(output)
        print "Files     : ", files

    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
