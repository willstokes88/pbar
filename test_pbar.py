"""
Inspection tests for pbar
--------------------------
Unit tests for this does not really make sense
"""
from pbar import Bar
from time import sleep
import logging

import unittest
import nose.tools as nosetools


class TestPBar(unittest.TestCase):

    def setUp(self):
        self.duration = 5
        self.steps = 100

    @nosetools.nottest
    def delay(self):
        sleep(self.duration/self.steps)

    @nosetools.nottest
    def do(self, bar):
        for x in range(self.steps):
            bar.step()
            self.delay()

    def test_bar(self):
        print("Basic Bar")
        self.do(Bar(self.steps))

    def test_message(self):
        self.do(Bar(self.steps, message="A bar with a message"))

    def test_symbols(self):
        self.do(Bar(self.steps, message="A bar with different symbols", marker="*", bar_left="<", bar_right="}"))

    def test_width(self):
        self.do(Bar(self.steps, message="Width is 100", width=100))
        self.do(Bar(self.steps, message="Width is 20", width=20))

    def test_suffix(self):
        self.do(Bar(self.steps, message="Test suffix", suffix="{o.progress}% {o.idx} {o.time}"))

    def test_slow(self):
        self.duration=65
        self.do(Bar(self.steps, message="Slow (> 1 min!)", suffix="{o.time}s"))

    def test_log_capture(self):
        log = logging.getLogger(__name__)

        self.steps = 5
        bar = Bar(self.steps, message="Log capturing...")
        for x in range(self.steps):
            bar.step()
            log.info("A message!")
            self.delay()


