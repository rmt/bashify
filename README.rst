Bashify
-------

Bashify is a simple python library (also executable as a script) to generate
bash scripts that contain files and commands to run, with support for piping
data as standard input to the commands that are run.

It will create a temporary directory, change to it, extract all the files from
the script, run all the commands in the script, then delete the temporary
directory.

It's useful for creating pipe-able scripts, for example:
``curl http://example.com/script.sh | bash`` or
``cat script.sh | ssh myhost bash``

It depends on standard commands like ``mktemp``, ``base64``, ``chmod``
