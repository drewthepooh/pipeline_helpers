from .dpipe import subprocesses, Dummy
import unittest

####### subprocesses tests


class SanityCheck(unittest.TestCase):

    dummy = Dummy()
    template = ['echo', dummy]

    def test_fail_template(self):
        '''sanity check should fail with non-list template'''
        template = ('echo', self.dummy)
        iterable = ['hello', 'world!']
        with self.assertRaises(AssertionError):
            s = subprocesses(template, iterable, run=False)

    def test_fail_iterable_types(self):
        '''sanity check should fail if iterable is not all strings or all lists'''
        iterable = ['hello', ('world',)]
        with self.assertRaises(TypeError):
            s = subprocesses(self.template, iterable, run=False)

    def test_fail_iterable_length(self):
        '''sanity check should fail if items in iterable not uniform in length'''
        iterable = [('how', 'are'), ('you?',)]
        with self.assertRaises(AssertionError):
            s = subprocesses(self.template, iterable, run=False)

    def test_fail_dummy_count(self):
        '''should fail if iterable item length does not match number of dummy values'''
        iterable = [('a', 'b', 'c'), ('d', 'e', 'f')]
        template = ['echo', self.dummy, 'something', self.dummy, self.dummy, self.dummy]
        with self.assertRaises(AssertionError):
            s = subprocesses(template, iterable, run=False)


class CommandsCheck(unittest.TestCase):

    dummy = Dummy()

    def test_good_string(self):
        '''should pass with known string inputs'''
        knowninputs = (['echo', self.dummy], ['hello', 'world!', 'goodbye', 'now'])
        knownoutput = [
                            ['echo', 'hello'],
                            ['echo', 'world!'],
                            ['echo', 'goodbye'],
                            ['echo', 'now']
                        ]
        output = subprocesses(*knowninputs, run=False)._get_commands()
        self.assertEqual(knownoutput, output)

    def test_good_tuple(self):
        '''should pass with known tuple inputs'''
        knowninputs = (['hey', self.dummy, 'name', self.dummy, self.dummy],
                       [('my', 'is', 'drew'),
                        ('joels', 'aint', 'drew'),
                        ('johns', 'isgottabe', 'johnny')])
        knownoutput = [
                            ['hey', 'my', 'name', 'is', 'drew'],
                            ['hey', 'joels', 'name', 'aint', 'drew'],
                            ['hey', 'johns', 'name', 'isgottabe', 'johnny'],
                        ]
        output = subprocesses(*knowninputs, run=False)._get_commands()
        self.assertEqual(knownoutput, output)


if __name__ == '__main__':
    unittest.main()
