#!/usr/bin/env python2
#
# Copyright 2014, Robert Thomson
# Released under the MIT license.
#

import sys
import os.path
from base64 import b64encode


def shell_quote(s):
    return "'" + s.replace("'", "'\\''") + "'"


class Bashify(object):
    """
    Basher will create an executable archive from a set of files, which just
    requires the common UNIX utilities 'bash', 'base64', 'mktemp' and 'chmod'
    to run.

    It will create a temporary directory, change to it, extract the files, run
    the commands in order, and then clean up after itself.

    >>> b = Bashify()
    >>> b.add_file("/path/to/important.data.gz")
    >>> b.add_command("gunzip important.data.gz")
    >>> b.add_script("/path/to/do_stuff.py", args=["-i", "important.data"])
    >>> # b.dump(sys.stdout)
    """
    def __init__(self):
        self.files = {}
        self.commands = []

    def add_file(self, filename, dest_filename=None):
        """
        Include the given file, and create it in the temporary directory
        with dest_filename.  If dest_filename is blank, use the basename
        of filename.

        @param filename: Local file to add to archive.
        @param dest_filename: Remote filename in temp directory.
        """
        if not dest_filename:
            dest_filename = os.path.basename(filename)
        with open(filename, 'rb') as fd:
            data = fd.read()
            self.files[dest_filename] = data

    def add_command(self, command, stdin=None):
        """
        Add a command to be run.  You can optionally specify
        stdin data which will be piped to the command.

        @param command: Command to run.  If it's a list or tuple, items
            will be shell-escaped and joined by spaces.
        @param stdin: An optional blob of data to be passed as standard
            input to the command.
        """
        if type(command) in (list, tuple):
            command = " ".join([shell_quote(x) for x in args])
        self.commands.append((command, stdin,))

    def add_script(self, filename, dest_filename=None, args=None, stdin=None):
        """
        Add a script, make it executable, and run it with optional
        standard input.

        @param filename: Local path to the executable file.
        @param dest_filename: What the file should be called remotely.
        @param args: Optional arguments to the command. It can be a
            string (passed verbatim, may result in multiple arguments) or
            a list or tuple of arguments, which will be shell-escaped.
        @param stdin: Optional blob of data to be passed as standard input.
        """
        if not dest_filename:
            dest_filename = os.path.basename(filename)
        self.add_file(filename, dest_filename)
        self.add_command("chmod 700 '{0}'".format(dest_filename))
        if args:
            if type(args) in (list, tuple):
                args = " ".join([shell_quote(x) for x in args])
            self.add_command("./'{0}' {1}".format(dest_filename, args), stdin)
        else:
            self.add_command("./'{0}'".format(dest_filename), stdin)

    def _dump_init(self, fd):
        fd.write('set -e\n')
        fd.write('mytmpdir=`mktemp -d`\n')
        fd.write('test -d "$mytmpdir" || exit 255\n')
        fd.write('function bashify_cleanup { cd /; rm -rf "$mytmpdir"; }\n')
        fd.write('trap bashify_cleanup EXIT\n')
        fd.write('cd "$mytmpdir"\n')
        fd.write('\n')

    def _dump_file(self, fd, filename, contents):
        fd.write('base64 -d > {0} <<"EOF_b64"\n'.format(filename,))
        fd.write(b64encode(contents))
        fd.write('\nEOF_b64\n')

    def _dump_command(self, fd, command, stdin):
        if stdin:
            fd.write('base64 -d <<"EOF_b64" | {0}\n'.format(command))
            fd.write(b64encode(stdin))
            fd.write('\nEOF_b64\n')
        else:
            fd.write("{0}\n".format(command))

    def dump(self, fd):
        fd.write('#!/bin/bash\n')
        fd.write('# SECTION: INIT\n')
        self._dump_init(fd)
        fd.write('# SECTION: FILES\n')
        for filename, contents in sorted(self.files.items()):
            self._dump_file(fd, filename, contents)
        fd.write('# SECTION: COMMANDS\n')
        for command, stdin, in self.commands:
            self._dump_command(fd, command, stdin)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        argv = sys.argv[1:]
        if argv[0] == "--stdin":
            stdin = sys.stdin.read()
            argv.pop(0)
        else:
            stdin = None
        script = argv[0]
        args = argv[1:]
        b = Bashify()
        b.add_script(script, args=args, stdin=stdin)
        b.dump(sys.stdout)
    else:
        print "Syntax: {0} [--stdin] <script file> [args]"
