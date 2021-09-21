# Bashify

Bashify is a simple python library (also executable as a script) to generate
bash scripts that contain files and commands to run, with support for piping
data as standard input to the commands that are run.

It will create a temporary directory, change to it, extract all the files from
the script, run all the commands in the script, then delete the temporary
directory.

It's useful for creating pipe-able scripts, for example:

    curl http://example.com/script.sh | bash
    cat script.sh | ssh myhost bash

It depends on standard commands like ``mktemp``, ``base64``, ``chmod``


# Using it as a module
    
    >>> import sys, bashify
    >>> b = bashify.Bashify()
    >>> b.add_file("test.txt", data=b"optionally set file contents programmatically")
    >>> b.add_command("cat test.txt")
    >>> b.dump(sys.stdout)
    #!/bin/bash
    # SECTION: INIT
    set -e
    mytmpdir=`mktemp -d`
    test -d "$mytmpdir" || exit 255
    function bashify_cleanup { cd /; rm -rf "$mytmpdir"; }
    trap bashify_cleanup EXIT
    cd "$mytmpdir"
    
    # SECTION: FILES
    base64 -d > test.txt <<"EOF_b64"
    b3B0aW9uYWxseSBzZXQgZmlsZSBjb250ZW50cyBwcm9ncmFtbWF0aWNhbGx5
    EOF_b64
    # SECTION: COMMANDS
    cat test.txt
    >>> 


# Using it as a script

    $ ./bashify.py --help
    usage: bashify.py [-h] [--files [FILE [FILE ...]]] [--stdin] [--output OUTPUT]
                      script [args [args ...]]
    
    positional arguments:
      script
      args
    
    optional arguments:
      -h, --help            show this help message and exit
      --files [FILE [FILE ...]], -f [FILE [FILE ...]]
                            add files to script: filename[=destfilename]
      --stdin, -i           embed our stdin as script's stdin
      --output OUTPUT, -o OUTPUT
                            where to write script [stdout]
    $ cat hello_world.sh
    #!/bin/bash
    
    if [ -n "$1" ]; then
        NAME="$1"
    else
        NAME="World"
    fi
    
    echo "Hello, $NAME!"
    
    if [[ -e README.md ]]; then
      head -6 README.md | tail -5
    fi
    
    cat
    $ echo "That's all, Folks..." | ./bashify.py --stdin --files README.md --output myscript.sh -- hello_world.sh Bob
    $ ./myscript.sh
    Hello, Bob!
    
    Bashify is a simple python library (also executable as a script) to generate
    bash scripts that contain files and commands to run, with support for piping
    data as standard input to the commands that are run.
    
    That's all, Folks...
