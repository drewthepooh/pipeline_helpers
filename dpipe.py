import logging
import logging.config
import functools
import pprint
import subprocess
from os.path import join as pjoin
from concurrent import futures
from multiprocessing import cpu_count
import collections

import __main__

try:
    log_file_path = __main__.log_file_path
except AttributeError:
    print('\n' + ('>'*55))
    print('''WARNING: Log file will be stored in the current directory.
If you would like to specify a different directory, add
a variable called "log_file_path" before importing dpipe.''')
    print('<'*55 + '\n')
    log_file_path = '.'

format = '%(levelname)s [%(asctime)s] %(message)s'
datefmt = '%m/%d/%Y %H:%M:%S'

log = logging.getLogger('log')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(fmt=format, datefmt=datefmt)
ch.setFormatter(formatter)
log.addHandler(ch)
fh = logging.FileHandler(pjoin(log_file_path, 'log.log'))
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
        log.info(' Finished ' + func.__name__ + ' ')
        return output
    return log_wrapper


def sub_call(command, stdout=None, shell=False):
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


def subprocesses(command, iterable):
    '''Allows for easy parallel subprocess calls. subprocesses takes a command (as a list),
    and an iterable of strings or tuples and executes the command with each item from
    the iterable substituted in for a dummy'''

    # Start sanity checks
    iterable = list(iterable)
    assert isinstance(command, list), 'Command must be a list'
    if all(isinstance(x, str) for x in iterable):
        strings = True
    elif all(isinstance(x, tuple) for x in iterable):
        strings = False
    else:
        raise TypeError('Objects in iterable must be all strings or all tuples')

    dummy_count = sum(1 for cm in command if isinstance(cm, Dummy))
    if strings:
        assert dummy_count == 1, 'Number of dummies does not match iterable item length'
    else:
        length = len(iterable[0])
        for item in iterable:
            assert len(item) == length, 'Items in iterable not uniform in length'
        assert length == dummy_count, 'Number of dummies does not match iterable item length'
    # End sanity checks

    dummy_indices = (command.index(x) for x in command if isinstance(x, Dummy))

    def log_and_append(handlers, command):
        pretty_command = pprint.pformat(command, indent=4)
        log.debug('Running command:\n{}'.format(pretty_command))
        handlers.append(subprocess.Popen(command_copy))

    handlers = []
    if strings:
        for item in iterable:
            command_copy = command[:]
            for dummy_index in dummy_indices:
                command_copy[dummy_index] = item
            log_and_append(handlers, command_copy)
    else:
        for item in iterable:
            command_copy = command[:]
            for it, dummy_index in zip(item, dummy_indices):
                command_copy[dummy_index] = it
            log_and_append(handlers, command_copy)

    for h in handlers:
        rc = h.wait()
        assert rc == 0, 'subprocess return with non-0 return code'
