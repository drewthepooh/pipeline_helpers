# Python bioinformatics pipeline tools

My little attempt at consolodating some generally useful bioinformatics pipeline tools.

Usage:

## Initialization

    import dpipe
    dpipe.initLogger('/desired/path/to/logfile')

Import the module and initialize the log, which will go to both the console and a file called dpipe.log.

**IMPORTANT**: you must call initLogger before using any other dpipe function, as they depend on it.

If you want to use the dpipe logger in your own code (which I recommend), simply import the logging module and get the logger instance:

    import logging
    log = logging.getLogger('dpipe')
    log.info('Some info message in your code')  # Will go to console and file
    log.debug('Some debug message in your code')  # Will go to dpipe.log but not console.

## logwrap

A decorator that you can use to log function starts and ends, e.g.:

    @dpipe.logwrap
    def my_pipeline_function():
        print('Running...')

    my_pipeline_function()

Gives, as output:

    INFO [06/09/2013 23:45:24] --------- Beginning my_pipeline_function ---------
    Running...
    INFO [06/09/2013 23:45:24]  Finished my_pipeline_function

## callAndLog

Wrapper of the check_call function from the subprocess module. Logs each command to the log file (but not the console).

    dpipe.callAndLog['ls', 'l']

## working_dir

Context manager for changing the working directory, e.g.

    from dpipe import working_dir

    with working_dir('/path/to/directory'):
        # changes working directory
    # changes to original working directory

## ignored

Context manager to ignore specifed exceptions

Author: Raymond Hettinger (coming in Python 3.4). I added this so it can be used with older versions.

     with ignored(FileExistsError):
         os.mkdir('some_dir')


## subprocesses

Allows for easy parallel subprocess calls. subprocesses takes a template (as a list),
and an iterable of strings or tuples and executes commands formed from the template
by substituting dummies in the template with items from the iterable, e.g.

    from dpipe import Dummy

    d = Dummy()

    template = ['echo', d]
    dpipe.subprocesses(template, ['hello', 'world!', 'I', 'like', 'you!'])

    print()

    template = ['echo', d, d]
    adjectives = ['big', 'hairy', 'round']
    nouns = ['house', 'friend', 'balloon']
    dpipe.subprocesses(template, zip(adjectives, nouns))


Gives:

    hello
    world!
    I
    like
    you!

    big house
    hairy friend
    round balloon

The dummy must be an instance of the dpipe.Dummy class.
Will raise an error if the return code of each command is not zero. To disable this behavior set checkrc=False, e.g.

     dpipe.subprocesses(template, iterable, checkrc=False)

I can add the ability to redirect stdout if requested.
