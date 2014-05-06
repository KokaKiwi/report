#!/usr/bin/env python
"""
Rust bug report utility.

Usage:
    ./report.py [-q] [-c FILE] [<bugdirs>]...

Options:
    -h --help           Show this help and exit.
    -v --version        Show program version and exit.
    -q --quiet          Quiet mode.
    -c --config FILE    Config file. [default: conf.toml]
    [<bugdirs>]...      Bug directories.
"""
import os
import io
import tempfile
import shutil
import subprocess
import toml
from prompter import prompt
from docopt import docopt
from gist import Gist

__author__ = 'KokaKiwi <kokakiwi@kokakiwi.net>'
__version__ = '0.1.0'

here = os.path.dirname(__file__)
here = os.path.abspath(here)

SCHEMA_FILENAME = 'schema.toml'

QUIET = False

CMD_LINE = '$ {cmd}\n'

# WTF prompter? With default='no' return True?!
def yesno(msg, default = True, **kwargs):
    import prompter

    d = 'yes' if default else 'no'
    r = prompter.yesno(msg, default = d, **kwargs)
    if not default:
        r = not r

    return r

def run_command(cwd, cmd, out = None, inf = None, env = None):
    if not QUIET:
        print('Running:', cmd)

    out.write(CMD_LINE.format(cmd = cmd))

    args = {}
    args['cwd'] = cwd
    args['env'] = env
    args['stdout'] = subprocess.PIPE
    args['stderr'] = subprocess.STDOUT
    args['stdin'] = inf
    args['shell'] = True

    p = subprocess.Popen(cmd, **args)
    r = p.wait()

    if out:
        out.write(p.stdout.read().decode('utf-8'))

    return r

class Report(object):
    def __init__(self, conf, bugdir):
        self.conf = conf

        self.bugdir = os.path.join(here, bugdir)
        self.bugdir_name = os.path.basename(bugdir)

        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir_name = os.path.join(self.tmpdir.name, self.bugdir_name)

        shutil.copytree(self.bugdir, self.tmpdir_name)

        schema_file = os.path.join(self.bugdir, SCHEMA_FILENAME)
        with open(schema_file) as f:
            self.schema = toml.loads(f.read())

    def __call__(self):
        commands = self.run_commands()

        if yesno('Upload to gist?', default = False):
            r = self.upload_gist(commands)
            print('Gist URL:', r['url'])

        if yesno('Display result?', default = False):
            for (filename, content) in commands.items():
                print('{filename}:'.format(filename = filename))
                print(content)

    @property
    def title(self):
        return self.schema.get('title')

    def run_commands(self):
        commands = {}

        for entry in self.schema.get('commands', []):
            out = io.StringIO()

            for cmd in entry.get('command', []):
                command = cmd.get('command')
                if not isinstance(command, str):
                    continue

                env = cmd.get('env')

                cwd = self.tmpdir_name
                cmd_dir = cmd.get('dir')
                if isinstance(cmd_dir, str):
                    cwd = os.path.join(cwd, cmd_dir)

                inf = None
                cmd_input = cmd.get('input')
                if isinstance(cmd_input, str):
                    in_file = os.path.join(self.bugdir, cmd_input)
                    inf = open(in_file)

                run_command(cwd, command, out = out, inf = inf, env = env)

            filename = entry.get('file')
            if isinstance(filename, str):
                commands[filename] = out.getvalue()

        return commands

    def upload_gist(self, commands):
        username = self.conf['github'].get('username')
        api_key = self.conf['github'].get('api_key')
        public = self.conf['github'].get('public', True)

        gist = Gist(username = username, api_key = api_key, public = public)
        gist.description = self.title

        for filename in self.schema.get('files', []):
            path = os.path.join(self.bugdir, filename)
            with open(path) as f:
                content = f.read()

            gist.add_file(filename, content)

        for (filename, content) in commands.items():
            gist.add_file(filename, content)

        return gist.create()

def main(bugdirs, conf_filename):
    conf_file = os.path.join(here, conf_filename)
    with open(conf_file) as f:
        conf = toml.loads(f.read())

    for bugdir in bugdirs:
        report = Report(conf, bugdir)
        report()

if __name__ == '__main__':
    args = docopt(__doc__, version = __version__)

    if args['--quiet']:
        QUIET = True

    main(args['<bugdirs>'], args['--config'])
