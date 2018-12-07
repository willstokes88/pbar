"""
Installation
===============
Unzip ``pbar-<version>.zip`` to a location of your choice, ``cd`` to the directory and run::

    python setup.py install

.. note::
    Ensure you install pbar to the correct Python interpreter. ``pbar`` is designed to work with Python3.

Verify the installation with::

    pip show pbar

Usage
=============
Basic
--------------
Importing the ``Bar`` class is the first step::

    from pbar import Bar

Initialise a ``Bar`` object with the total number of iterations required, and then call ``step()`` for each iteration::

    bar = Bar(100)
    for x in range(100):
        bar.step()
        # Do work in the loop here...

There is no need to manually closedown the progress bar as this is handled automatically when the bar completes.
However, if you wish to exit early from the loop, you can use the ``end()`` method::

    for x in range(100):
        bar.step()
        # Do some work in the loop here...

        if x == 75:
            bar.end()
            break

Calling ``end()`` ensures the buffers are flushed and the console line formatting returns to normal.

Logging
---------------
When using the progress bar, all log messages are captured. Once the bar completes (or ``end()`` is called manually)
the log messages are flushed and printed to the console.

The following example illustrates this concept::

    def work():
        log.info("Do some work!")

    bar = Bar(3)
    for idx in range(3):
        bar.step()
        work()
    log.info("Done!")

The above fragment of code would capture the logging from ``work()`` and then display it once the bar had completed::

    >>> [||||||||||||||||] 100%
    >>>
    >>> root:INFO: Do some work!
    >>> root:INFO: Do some work!
    >>> root:INFO: Do some work!
    >>> root:INFO: Done!

.. note::
    Whatever log formatting has been specified should be preserved.


Logging to file will continue as normal.

Customisation
---------------
The look of the bar and the information displayed can be customised by the user using key word arguments.

The default bar looks like this::

    [|||||||||              ] 42%

Use the following keyword arguments to customise the look of the bar::

    message         A message to the left of the progress bar (default = "")
    marker          The symbol used to the fill the bar ( | )
    bar_left        The left hand delimiter ([)
    bar_right       The right hand delimiter (])
    width           The width of the bar in characters (50)

The information displayed in the suffix (to the right of the bar) can also be customised using the ``suffix`` keyword
and a formatted string of the form ``{o.variable}``. ``variable`` can be any of the following::

    idx             The current iteration
    tot             The total number of iterations
    progress        The progress, as a percentage
    time            The current elapsed time as mins:secs

These can be combined to display information as you require::

    b = Bar(100, message="My progress bar", marker="*", suffix="{o.progress}% [{o.time}s]")

would produce a bar that looked like this...::

    My progress bar [******           ] 35% [00:12s]

"""

from sys import stdout
from math import ceil, floor
import logging
from time import time
from io import StringIO as strbuff

log = logging.getLogger(__name__)


class Bar(object):

    def __init__(self, tot, **kwargs):
        try:
            self.tot = int(tot)
            self.idx = 0

            self.visible = False
            self.pbar = []
            self.progress = 0
            self.tstart = None
            self.time = 0
            self.done = False

            # User customisation
            self.message = kwargs.get("message", "")
            self.marker = kwargs.get("marker", "|")[0]
            self.bar_left = kwargs.get("bar_left", "[")[0]
            self.bar_right = kwargs.get("bar_right", "]")[0]
            self.width = min(kwargs.get("width", 50), 100)
            self.inc = 100/self.width
            self.suffix = kwargs.get("suffix", "{o.progress}%")

            # Create a string buffer to hold the redirected logging output
            self.buff = strbuff()
            self.hbuff = logging.StreamHandler(self.buff)
            root = logging.getLogger()
            self.hbuff.setFormatter(logging.Formatter(root.handlers[0].formatter._fmt))
            self.hbuff.setLevel(root.level)
            self.streams = []

        except (ValueError, TypeError) as err:
            log.error(err)

    def step(self):
        """Increment the progress bar"""
        if self.idx == 0:
            self._start()

        self.idx += 1
        self.progress = int(ceil(float(self.idx)/float(self.tot)*100))
        self._update()

        if self.idx == self.tot:
            self.end()

    def end(self):
        """Destroy the progress bar once completed"""
        if not self.done:
            self.done = True
            stdout.flush()
            print("\n")
            stdout.flush()

            try:
                root = logging.getLogger()
                root.removeHandler(self.hbuff)
                for stream in self.streams:
                    root.addHandler(stream)
            except AttributeError:
                pass

            for logs in self.buff.getvalue().split("\n"):
                if logs.strip():
                    print(logs)

    def _start(self):
        """Initialise the bar and redirect the logging output"""
        # Redirect the logging
        root = logging.getLogger()
        for stream in root.handlers:
            if type(stream) is logging.StreamHandler:
                self.streams.append(stream)
                root.removeHandler(stream)

        root.addHandler(self.hbuff)

        self.visible = True
        self.tstart = time()

    def _update(self):
        """update the displayed progress bar"""
        elapsed = time() - self.tstart
        mins = floor(elapsed/60)
        secs = int(elapsed - (mins*60))
        self.time = "{:02d}:{:02d}".format(mins, secs)

        while len(self.pbar) * self.inc < self.progress:
            self.pbar.append(self.marker)

        bar = "{}{}{}{}".format(self.bar_left, "".join(self.pbar), " " * (self.width - len(self.pbar)), self.bar_right)
        disp = " ".join([self.message, bar, self.suffix.format(o=self)])

        stdout.flush()
        print("\r" + disp, end="")
        stdout.flush()

    def __del__(self):
        self.end()


