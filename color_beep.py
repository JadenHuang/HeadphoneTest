# -*- coding: utf-8 -*-
# requirement of python module: termcolor, colorama(win32)

__all__ = ["print_red", "print_green", "beep", "pass_big_font", "fail_big_font"]

from termcolor import colored, cprint
import os

# win32
if os.name == 'nt':
    import winsound
    import colorama

    colorama.init()


    def beep(frequency, duration):
        winsound.Beep(frequency, duration)
# posix
elif os.name == 'posix':
    def beep(frequency, duration):
        #  use command "apt-get install beep" to
        # install beep if your linux doesn't have it.
        os.system('beep -f %s -l %s' % (frequency, duration))
else:
    raise ImportError("Sorry: no implementation for your platform ('%s') available" % (os.name,))

pass_big_font = r"""
 ____   _    ____ ____
|  _ \ / \  / ___/ ___|
| |_) / _ \ \___ \___ \
|  __/ ___ \ ___) |__) |
|_| /_/   \_\____/____/
"""

fail_big_font = """
 _____ _    ___ _
|  ___/ \  |_ _| |
| |_ / _ \  | || |
|  _/ ___ \ | || |___
|_|/_/   \_\___|_____|
"""


def print_red(txt):
    cprint(txt, "red", attrs=['bold'])


def print_green(txt):
    cprint(txt, "green", attrs=['bold'])


if __name__ == "__main__":
    # print red
    print_red("Hello, world!")

    # print green
    print_green("Hello, world")

    # you can use termcolor library, it's better
    text = colored('Hello, World!', 'red', attrs=['reverse', 'blink'])
    print(text)
    cprint('Hello, World!', 'green', 'on_red')

    print_red_on_cyan = lambda x: cprint(x, 'red', 'on_cyan')
    print_red_on_cyan('Hello, World!')
    print_red_on_cyan('Hello, Universe!')

    for i in range(10):
        cprint(i, 'magenta')

    cprint("Attention!", 'red', attrs=['bold'])

    beep(1500, 800)
