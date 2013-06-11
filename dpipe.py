import logging
import functools
import pprint
import subprocess
import os
from os.path import join as pjoin
from concurrent import futures
import sys
from contextlib import contextmanager


def initLogger(path):
    format = '%(levelname)s [%(asctime)s] %(message)s'
    datefmt = '%m/%d/%Y %H:%M:%S'

    global log
    log = logging.getLogger('dpipe')
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt=format, datefmt=datefmt)
    ch.setFormatter(formatter)
    log.addHandler(ch)
    fh = logging.FileHandler(pjoin(path, 'dpipe.log'))
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)


def logwrap(func):
    '''Decorator which will wrap functions so that the beginning
    and end is logged.'''

    @functools.wraps(func)
    def log_wrapper(*args, **kwargs):
        log.info('{:-^50}'.format(' Beginning ' + func.__name__ + ' '))
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


def processes(func, iterable):
    '''Takes a function and an iterable and calls the function with each argument of the
    iterable in parallel.'''

    with futures.ProcessPoolExecutor() as executor:
        result = executor.map(func, iterable)
    return result


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

    def __init__(self, template, iterable, *, checkrc=True, stdout=None, run=True):
        self.template = template
        self.iterable = list(iterable)
        self.dummy_indices = [i for i, v in enumerate(template) if isinstance(v, Dummy)]
        self.stdout = stdout
        self.checkrc = checkrc

        self._sanity_check()

        if run:
            self._execute_children()

    def _sanity_check(self):
        assert isinstance(self.template, list), 'Template must be a list'
        if all(isinstance(x, str) for x in self.iterable):
            self.iterable = [(x,) for x in self.iterable]
        elif all(isinstance(x, tuple) for x in self.iterable):
            pass
        else:
            raise TypeError('Objects in iterable must be all strings or all tuples')

        dummy_count = sum(1 for t in self.template if isinstance(t, Dummy))
        length = len(self.iterable[0])
        for item in self.iterable:
            assert len(item) == length, 'Items in iterable not uniform in length'
        assert length == dummy_count, 'Number of dummies does not match iterable item length'

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
            handlers.append((subprocess.Popen(command, stdout=self.stdout), command))

        if self.checkrc:
            for h in handlers:
                rc = h[0].wait()
                if rc:
                    cmd = h[1]
                    raise subprocess.CalledProcessError(rc, cmd)
