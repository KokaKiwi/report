report
======

Bug report utility.

Installation
============

In the repository directory:

```
$ ./env_setup.sh
$ source .venv/bin/activate
```

Usage
=====

```
$ ./report.py -h
Rust bug report utility.

Usage:
    ./report.py [-q] [-c FILE] [<bugdirs>]...

Options:
    -h --help           Show this help and exit.
    -v --version        Show program version and exit.
    -q --quiet          Quiet mode.
    -c --config FILE    Config file. [default: conf.toml]
    [<bugdirs>]...      Bug directories.
```

See `sample` directory to see an example usage.
