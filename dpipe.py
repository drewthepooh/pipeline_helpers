import logging
import logging.config
import functools
import pprint
import subprocess
from os.path import join as pjoin
from concurrent import futures
from multiprocessing import cpu_count

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
    '''
    Decorator which will wrap functions so that the beginning
    and end is logged.
    '''
    @functools.wraps(func)
    def log_wrapper(*args, **kwargs):
        log.info('{:-^50}'.format(' Beginning ' + func.__name__ + ' '))
        output = func(*args, **kwargs)
        log.info(' Finished ' + func.__name__ + ' ')
        return output
    return log_wrapper


def sub_call(command, stdout=None, shell=False):
    '''
    Logs subprocess commands.
    '''
    pretty_command = pprint.pformat(command, indent=4)
    log.debug('running command:\n{}'.format(pretty_command))
    if stdout:
        log.debug('writing to: ' + stdout.name)
    subprocess.check_call(command, stdout=stdout, shell=shell)


def processes(func, iterable):
    with futures.ProcessPoolExecutor() as executor:
        result = executor.map(func, iterable)
    return result


class Dummy:
    pass


def subprocesses(command, iterable):
    assert isinstance(command, list), 'Command must be a list'
    handlers = []
    for item in iterable:
        for i, cm in enumerate(command):
            if isinstance(cm, Dummy):
                command[i] = item
                handlers.append(subprocess.Popen(command))
                command[i] = Dummy()

    for h in handlers:
        rc = h.wait()
        assert rc == 0, 'subprocess return with non-0 return code'


