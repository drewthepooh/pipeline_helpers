import logging
import logging.config
import functools
import pprint
import subprocess
import os
from os.path import join as pjoin
from concurrent import futures
import sys
from contextlib import contextmanager
import json
import shutil


with open(pjoin(os.path.dirname(__file__), 'logconfig.json')) as f:
    configDict = json.load(f)

logging.config.dictConfig(configDict)
log = logging.getLogger('dpipe')


def setLogPath(path):
    # Move the log to the new directory
    shutil.move('dpipe.log', path)
    # Re-initialize logger if called
    configDict['handlers']['file']['filename'] = pjoin(path, 'dpipe.log')
    logging.config.dictConfig(configDict)


def logwrap(func):
    '''Decorator which will wrap functions so that the beginning
    and end is logged.'''

    @functools.wraps(func)
    def log_wrapper(*args, **kwargs):
        log.info(format((' Beginning ' + func.__name__ + ' '), '-^50'))
        output = func(*args, **kwargs)
        log.info('Finished ' + func.__name__ + ' ')
        return output
    return log_wrapper


def callAndLog(command, stdout=None, shell=False):
    '''Logs subprocess commands.'''

    pretty_command = pprint.pformat(command, indent=4)
    log.debug('running command:\n{}'.format(pretty_command))
    if stdout:
        log.debug('writing to: ' + stdout.name)
    subprocess.check_call(command, stdout=stdout, shell=shell)


@contextmanager
def working_dir(new_dir):
    old_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)


@contextmanager
def ignored(*exceptions):
    '''Context manager to ignore specifed exceptions
    Author: Raymond Hettinger'''
    try:
        yield
    except exceptions:
        pass


class Dummy:
    pass


class subprocesses:
    '''Allows for easy parallel subprocess calls. subprocesses takes a template (as a list),
    and an iterable of strings or tuples and executes commands formed from the template
    by substituting dummies in the template with each item from the iterable.'''

    def __init__(self, template, iterable, *, checkrc=True, run=True):

        if isinstance(template, list):
            self.template = template
        else:
            raise TypeError('Expected a list for template')

        self.dummy_indices = [i for i, v in enumerate(template) if isinstance(v, Dummy)]

        iterable = list(iterable)
        if all(isinstance(x, str) for x in iterable):
            self.iterable = [(x,) for x in iterable]
        elif all(isinstance(x, tuple) for x in iterable):
            self.iterable = iterable
        else:
            raise TypeError('Expected all strings or all tuples in iterable')

        dummy_count = len(self.dummy_indices)
        length = len(self.iterable[0])
        for item in self.iterable:
            assert len(item) == length, 'Items in iterable not uniform in length'
        assert length == dummy_count, 'Number of dummies does not match iterable item length'

        self.checkrc = checkrc

        if run:
            self._execute_children()

    def _get_commands(self):
        commands = []
        for item in self.iterable:
            command = self.template[:]
            for it, dummy_index in zip(item, self.dummy_indices):
                command[dummy_index] = it
            commands.append(command)
        return commands

    def _execute_children(self):
        commands = self._get_commands()
        handlers = []
        for command in commands:
            pretty_command = pprint.pformat(command, indent=4)
            log.debug('Running command:\n{}'.format(pretty_command))
            handlers.append((subprocess.Popen(command), command))

        if self.checkrc:
            for h in handlers:
                rc = h[0].wait()
                if rc:
                    cmd = h[1]
                    raise subprocess.CalledProcessError(rc, cmd)
