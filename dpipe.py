import logging
import functools
import pprint
import subprocess
from os.path import join as pjoin
from concurrent import futures
import sys


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


class Dummy:
    pass


def subprocesses(template, iterable, stdout=None):
    '''Allows for easy parallel subprocess calls. subprocesses takes a template (as a list),
    and an iterable of strings or tuples and executes commands formed from the template
    by substituting dummies in the template with each item from the iterable.'''

    iterable = list(iterable)

    # Sanity checks
    assert isinstance(template, list), 'Template must be a list'
    if all(isinstance(x, str) for x in iterable):
        iterable = [(x,) for x in iterable]
    elif all(isinstance(x, tuple) for x in iterable):
        pass
    else:
        raise TypeError('Objects in iterable must be all strings or all tuples')

    dummy_count = sum(1 for t in template if isinstance(t, Dummy))
    length = len(iterable[0])
    for item in iterable:
        assert len(item) == length, 'Items in iterable not uniform in length'
    assert length == dummy_count, 'Number of dummies does not match iterable item length'

    dummy_indices = [i for i, v in enumerate(template) if isinstance(v, Dummy)]

    def log_and_append(handlers, command):
        pretty_command = pprint.pformat(command, indent=4)
        log.debug('Running command:\n{}'.format(pretty_command))
        handlers.append((subprocess.Popen(command, stdout=stdout), command))

    handlers = []
    for item in iterable:
        command = template[:]
        for it, dummy_index in zip(item, dummy_indices):
            command[dummy_index] = it
        log_and_append(handlers, command)

    for h in handlers:
        rc = h[0].wait()
        if rc:
            cmd = h[1]
            raise subprocess.CalledProcessError(rc, cmd)

