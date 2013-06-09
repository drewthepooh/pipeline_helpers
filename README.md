# Python Bioinformatics Pipeline Tools

Just my little attempt at making some generally useful bioinformatics pipeline tools in python.
This is very much a work in progress, as is the documentation.

Usage:

## Initialization

    import dpipe

This will automatically initialize the log, which will go to both the console and a file called log.log.  By default the log file will be placed in the current directory.  If you want to specify a different directory add the line:

    log_file_path = '/desired/path/'

Before the import statement.

## Logwrap

A decorator that you can use to log function starts and ends, e.g.:

    @dpipe.logwrap
    def my_pipeline_function():
        print('Running...')

    my_pipeline_function()

Gives, as output:

    INFO [06/09/2013 23:45:24] --------- Beginning my_pipeline_function ---------
    Running...
    INFO [06/09/2013 23:45:24]  Finished my_pipeline_function

## sub_call

Wrapper of the check_call function from the subprocess module. Logs each command to the log file (but not the console).

    dpipe.sub_call['ls', 'l']

## processes

Trivial (so trivial it's nearly useless) wrapper of the concurrent futures ProcessPoolExecutor map functionality. This function takes a function and an iterable and calls the function with each argument of the iterable in parallel.

    def myfun(num):
        return num**2

    dpipe.processes(myfun, [1, 2, 3, 4, 5])

## subprocesses

Allows for easy parallel subprocess calls. subprocesses takes a command (as a list), and an iterable of strings or tuples and executes the command with each item from the iterable substituted in for a dummy, e.g.

    from dpipe import Dummy

    command = ['echo', Dummy()]
    dpipe.subprocesses(command, ['hello', 'world!', 'I', 'like', 'you!'])

    print()

    command = ['echo', dpipe.Dummy(), dpipe.Dummy()]
    adjectives = ['big', 'hairy', 'round']
    nouns = ['house', 'friend', 'balloon']
    dpipe.subprocesses(command, zip(adjectives, nouns))


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
Will raise an error if the return code of the inputted command is not 0.
