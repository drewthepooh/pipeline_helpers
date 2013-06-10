# Python Bioinformatics Pipeline Tools

Just my little attempt at making some generally useful bioinformatics pipeline tools in python.
This is very much a work in progress, as is the documentation.

Usage:

## Initialization

    import dpipe
    dpipe.initLogger('/desired/path/to/logfile')

Import the module and initialize the log, which will go to both the console and a file called dpipe.log. IMPORTANT: you must call initLogger before using any other dpipe function, as they depend on it.

If you want to use the logger in your own code, simply import the logging module and get the logger instance:

    import logging
    log = logging.getLogger('dpipe')
    log.info('Some info message')  # Will go to console and file
    log.debug('Some debug message')  # Will go to dpipe.log but not console.

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

## processes

Trivial (so trivial it's nearly useless) wrapper of the concurrent futures ProcessPoolExecutor map functionality. This function takes a function and an iterable and calls the function with each argument of the iterable in parallel.  Additional functionality (such as logging) will be added in the future.

    def myfun(num):
        return num**2

    dpipe.processes(myfun, [1, 2, 3, 4, 5])

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
