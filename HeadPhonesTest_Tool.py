"""A generic class to build line-oriented command interpreters.

Interpreters constructed with this class obey the following conventions:

1. End of file on input is processed as the command 'EOF'.
2. A command is parsed out of each line by collecting the prefix composed
   of characters in the identchars member.
3. A command `foo' is dispatched to a method 'do_foo()'; the do_ method
   is passed a single argument consisting of the remainder of the line.
4. Typing an empty line repeats the last command.  (Actually, it calls the
   method `emptyline', which may be overridden in a subclass.)
5. There is a predefined `help' method.  Given an argument `topic', it
   calls the command `help_topic'.  With no arguments, it lists all topics
   with defined help_ functions, broken into up to three topics; documented
   commands, miscellaneous help topics, and undocumented commands.
6. The command '?' is a synonym for `help'.  The command '!' is a synonym
   for `shell', if a do_shell method exists.
7. If completion is enabled, completing commands will be done automatically,
   and completing of commands args is done by calling complete_foo() with
   arguments text, line, begidx, endidx.  text is string we are matching
   against, all returned matches must begin with it.  line is the current
   input line (lstripped), begidx and endidx are the beginning and end
   indexes of the text being matched, which could be used to provide
   different completion depending upon which position the argument is in.

The `default' method may be overridden to intercept commands for which there
is no do_ method.

The `completedefault' method may be overridden to intercept completions for
commands that have no complete_ method.

The data member `self.ruler' sets the character used to draw separator lines
in the help messages.  If empty, no ruler line is drawn.  It defaults to "=".

If the value of `self.intro' is nonempty when the cmdloop method is called,
it is printed out on interpreter startup.  This value may be overridden
via an optional argument to the cmdloop() method.

The data members `self.doc_header', `self.misc_header', and
`self.undoc_header' set the headers used for the help function's
listings of documented functions, miscellaneous topics, and undocumented
functions respectively.

These interpreters use raw_input; thus, if the readline module is loaded,
they automatically support Emacs-like command history and editing features.
"""

import string
import subprocess
import collections
from RF_programmer import RFProgram
from customization import CustomizationOfCSRA64215
from Product_programmer import ProductProgram
import color_beep as tips
from rf_test import RFTest ,RFTestOfQC30xFxA
import customization as custom
from global_settings import g
from asylog import Asylog
from config import Config
import color_beep as tips
import traceback

__all__ = ["Cmd"]

PROMPT = ' >> '
IDENTCHARS = string.ascii_letters + string.digits + '_'

f=open("version.txt")
ver = f.readline().strip('\n')
f.close()

__version__ = "1.0.0 svn"+ver

class Cmd:
    """A simple framework for writing line-oriented command interpreters.

    These are often useful for test harnesses, administrative tools, and
    prototypes that will later be wrapped in a more sophisticated interface.

    A Cmd instance or subclass instance is a line-oriented interpreter
    framework.  There is no good reason to instantiate Cmd itself; rather,
    it's useful as a superclass of an interpreter class you define yourself
    in order to inherit Cmd's methods and encapsulate action methods.

    """
    prompt = PROMPT
    identchars = IDENTCHARS
    ruler = '='
    lastcmd = ''
    intro = None
    doc_leader = ""
    doc_header = "Documented commands (type help <topic>):"
    misc_header = "Miscellaneous help topics:"
    undoc_header = "Undocumented commands:"
    nohelp = "*** No help on %s"
    use_rawinput = 1
    
    

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        """Instantiate a line-oriented interpreter framework.

        The optional argument 'completekey' is the readline name of a
        completion key; it defaults to the Tab key. If completekey is
        not None and the readline module is available, command completion
        is done automatically. The optional arguments stdin and stdout
        specify alternate input and output file objects; if not specified,
        sys.stdin and sys.stdout are used.

        """
        import sys

        self.cfg = Config()  # product config
        self.asylog = Asylog()
        self.g = g()
        #print (self.g.serial)
        #raw_input("Press any key")
        self.asylog.change_filter(self.g.module, self.g.station,self.g.serial)
        self.asylog.start()
        self.logger = self.asylog.getLogger()
        self.product_name=self.cfg.get_product_name()
        self.asylog.change_filter(self.cfg.get_product_name(), self.g.station, self.g.serial)
        
        if stdin is not None:
            self.stdin = stdin
        else:
            self.stdin = sys.stdin
        if stdout is not None:
            self.stdout = stdout
        else:
            self.stdout = sys.stdout
        self.cmdqueue = []
        self.completekey = completekey

        self.menu_up = "HeadPhones Test"
        self.menu_down = "{} Test Tool".format(self.cfg.get_product_name())

        self.customization = custom.CustomizationOfCSRA64215()
        self.logger.info("HeadPhonesTest_Tool ver : {}".format(__version__))

    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        """

        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey+": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro)+"\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = raw_input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line[:-1] # chop \n
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass


    def precmd(self, line):
        """Hook method executed just before the command line is
        interpreted, but after the input prompt is generated and issued.

        """

        cmd, arg, line = self.parseline(line)
        return line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        cmd, arg, line = self.parseline(line)
        if cmd not in ["Q", "EOF", "KeyInt"]:
            subprocess.call("pause", shell=True)
            subprocess.call("cls", shell=True)
            self.stdout.write('\n%s\n\n' % self.__banner(self.menu_up, self.menu_down, __version__))
            self.__menu()
        return stop


  # changeStation: change current TestBench Station ID
    #         1 - Station ID changed successfully
    #
    def changeStation(self):
        self.stdout.write('\n')
        try:
            user_input = raw_input
        except NameError:
            user_input = input
        ret = user_input(u'Input Testbench Station ID [' + self.g.station + ']: ')

        if len(ret) > 1:
            self.g.station = ret
            msg = u'Testbench Station ID changed to STN:[' + self.g.station + ']'
            self.asylog.change_filter(self.g.module, self.g.station, self.g.serial)
            self.logger.info(msg)
        else:
            self.stdout.write('\n')

    #
    # changeSerial: change current Serial ID of DUT being processed
    #
    #         1 - Serial ID changed successfully
    #
    def changeSerial(self):
        self.stdout.write('\n')
        try:
            user_input = raw_input
        except NameError:
            user_input = input

        ret = user_input(u'Input DUT Serial ID [' + self.g.serial + ']: ').strip()

        if len(ret) > 0 and ret != self.g.serial:
            oldserial = self.g.serial
            self.g.serial = ret
            msg = 'DUT Serial ID changed from SID-OLD:[' + oldserial + '] to SID-NEW:[' + self.g.serial + ']'
            #asylog.stop_dut_log(oldserial)
            self.logger.info(msg)

        else:
            self.logger.critical("The input DUT Serial {} is invalid ".format(ret))
            print ret




    def postloop(self):
        """Hook method executed once when the cmdloop() method is about to
        return.

        """
        pass

    def parseline(self, line):
        """Parse the line into a command name and a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' and 'args' may be None if the line couldn't be parsed.
        """
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        elif line[0] == '!':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars: i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.

        This may be overridden, but should not normally need to be;
        see the precmd() and postcmd() methods for useful execution hooks.
        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        cmd, arg, line = self.parseline(line)
        stop = None
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if cmd == '':
            return self.default(line)
        else:
            try:
                func = getattr(self, 'do_' + cmd)
                
            except AttributeError:
                return self.default(line)

            try:

                self.asylog.change_filter(self.g.module, self.g.station, self.g.serial)
                stop =func(arg)
                if cmd not in ["Q", "EOF", "KeyInt"]:
                    tips.print_green(tips.pass_big_font)
            except Exception as err:
                self.logger.critical(self.error_msg(err))
                if self.cfg.get_debug_enable():
                    tips.print_red(tips.fail_big_font)

            return stop


    def emptyline(self):
        """Called when an empty line is entered in response to the prompt.

        If this method is not overridden, it repeats the last nonempty
        command entered.

        """
        if self.lastcmd:
            return self.onecmd(self.lastcmd)

    def default(self, line):
        """Called on an input line when the command prefix is not recognized.

        If this method is not overridden, it prints an error message and
        returns.

        """
        self.stdout.write('*** Unknown syntax: %s\n'%line)

    def completedefault(self, *ignored):
        """Method called to complete an input line when no command-specific
        complete_*() method is available.

        By default, it returns an empty list.

        """
        return []

    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        return [a[3:] for a in self.get_names() if a.startswith(dotext)]

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        if state == 0:
            import readline
            origline = readline.get_line_buffer()
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped
            if begidx>0:
                cmd, args, foo = self.parseline(line)
                if cmd == '':
                    compfunc = self.completedefault
                else:
                    try:
                        compfunc = getattr(self, 'complete_' + cmd)
                    except AttributeError:
                        compfunc = self.completedefault
            else:
                compfunc = self.completenames
            self.completion_matches = compfunc(text, line, begidx, endidx)
        try:
            return self.completion_matches[state]
        except IndexError:
            return None

    def get_names(self):
        # This method used to pull in base class attributes
        # at a time dir() didn't do it yet.
        return dir(self.__class__)

    def complete_help(self, *args):
        commands = set(self.completenames(*args))
        topics = set(a[5:] for a in self.get_names()
                     if a.startswith('help_' + args[0]))
        return list(commands | topics)

    def do_help(self, arg):
        if arg:
            # XXX check arg syntax
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc=getattr(self, 'do_' + arg).__doc__
                    if doc:
                        self.stdout.write("%s\n"%str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n"%str(self.nohelp % (arg,)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd=name[3:]
                    if cmd in help:
                        cmds_doc.append(cmd)
                        del help[cmd]
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)
            self.stdout.write("%s\n"%str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,   15,80)
            self.print_topics(self.misc_header,  help.keys(),15,80)
            self.print_topics(self.undoc_header, cmds_undoc, 15,80)

    def close(self):
        try:
            self.asylog.stop()

        except AttributeError:
            pass

    def do_Q(self, line):
        """Quit/Exit\n"""
        self.close()
        return True

    def do_EOF(self, line):
        self.close()
        return True

    def do_KeyInt(self, line):
        """KeyboardInterrupt"""
        self.close()
        return True

    def log_filter_after_test(self, serial=None, station=None):
        if serial:
            self.g.serial = serial

        if station:
            self.g.station = station

        self.asylog.change_filter(self.cfg.get_product_name(), self.g.station, self.g.serial)

    def log_filter_before_test(self):
        self.asylog.change_filter('MAIN', self.g.station, '000000000000')

    def do_1(self, line):
        """F1-1 Programming RF Firmware"""
        self.logger.info('-->Performing Programming RF Firmware: {}'.format(self.product_name))
        RF_programmer = RFProgram()
        RF_programmer.RF_Flashing() 

    def do_2(self, line):
        """F2-1 External Crystal Oscillator Test"""
        self.logger.info('-->Performing External Crystal Oscillator Test: {}'.format(self.product_name))
        self.rf_test.frequency_test()
      
    def do_3(self, line):   
        """F3-1 BT2.1 BER Test"""
        #self.rf_test.init_ble_module()
        self.logger.info('-->Performing BT2.1 BER Test: {}'.format(self.product_name))
        self.rf_test.BT_BER_LoopBack_Test()     
    def do_4(self, line):   
        """F4-1 BT2.1 Output Power Test"""
        #self.rf_test.init_ble_module()
        self.logger.info('-->Performing BT2.1 Output Power Test: {}'.format(self.product_name))
        self.rf_test.BT_power_test()

    def do_5(self, line):   
        """F5-1 Audio Test"""
        raise AppError("Test case not supported")
      
    def do_6(self, line):   
        """F6-1 Module Programming"""
        self.logger.info('-->Performing Module Programming: {}'.format(self.product_name))
        Product_programmer = ProductProgram()
        Product_programmer.Product_Flashing()
      
    def do_7(self, line):   
        """F7-1 Module Customization\n"""
        self.logger.info('-->Performing Module Customization: {}'.format(self.product_name))
        self.customization.Run()
      
    def do_8(self, line):   
        """F8-1 Integrated Test\n"""
        self.logger.info('-->Performing Integrated Test: {}'.format(self.product_name))
        app_config = self.cfg.get_app_config()
        test_sequence = app_config.find(".//test_case/test_sequence").text
        for i in test_sequence:
            if i in (string.ascii_letters + string.digits):
                eval("self.do_{}(None)".format(i.upper()))    

    def do_I(self, line):
        """Change Serial ID"""
        self.changeSerial()
    def note_I(self):
        return u"Change Serial ID  [{}]".format(self.g.serial)

    def do_T(self, line):
        """Change Station ID"""
        self.changeStation()
    def note_T(self):
        return u"Change Station ID [{}]".format(self.g.station)

    def print_topics(self, header, cmds, cmdlen, maxcol):
        if cmds:
            self.stdout.write("%s\n"%str(header))
            if self.ruler:
                self.stdout.write("%s\n"%str(self.ruler * len(header)))
            self.columnize(cmds, maxcol-1)
            self.stdout.write("\n")

    def columnize(self, list, displaywidth=80):
        """Display a list of strings as a compact set of columns.

        Each column is only as wide as necessary.
        Columns are separated by two spaces (one was not legible enough).
        """
        if not list:
            self.stdout.write("<empty>\n")
            return
        nonstrings = [i for i in range(len(list))
                        if not isinstance(list[i], str)]
        if nonstrings:
            raise TypeError, ("list[i] not a string for i in %s" %
                              ", ".join(map(str, nonstrings)))
        size = len(list)
        if size == 1:
            self.stdout.write('%s\n'%str(list[0]))
            return
        # Try every row count from 1 upwards
        for nrows in range(1, len(list)):
            ncols = (size+nrows-1) // nrows
            colwidths = []
            totwidth = -2
            for col in range(ncols):
                colwidth = 0
                for row in range(nrows):
                    i = row + nrows*col
                    if i >= size:
                        break
                    x = list[i]
                    colwidth = max(colwidth, len(x))
                colwidths.append(colwidth)
                totwidth += colwidth + 2
                if totwidth > displaywidth:
                    break
            if totwidth <= displaywidth:
                break
        else:
            nrows = len(list)
            ncols = 1
            colwidths = [0]
        for row in range(nrows):
            texts = []
            for col in range(ncols):
                i = row + nrows*col
                if i >= size:
                    x = ""
                else:
                    x = list[i]
                texts.append(x)
            while texts and not texts[-1]:
                del texts[-1]
            for col in range(len(texts)):
                texts[col] = texts[col].ljust(colwidths[col])
            self.stdout.write("%s\n"%str("  ".join(texts)))
    def preloop(self):
        self.stdout.write('\n%s\n\n' % self.__banner(self.menu_up, self.menu_down, __version__))
        self.__menu()
        self.rf_test = RFTestOfQC30xFxA()

    def error_msg(self, err):
        return "{}: {}".format(err.__class__.__name__, err)


    def __banner(self, up='up', down='down', version="0.0.0"):
        # display start up message
        FB = u'**'

        up_down = [up, down + " v{}".format(version)]
        for index, item in enumerate(up_down):
            item += (len(item) % 2) * ' '
            up_down[index] = item

        max_len = max(len(i) for i in up_down)
        for index, item in enumerate(up_down):
            div = (max_len - len(item)) / 2 + 3
            item = ' ' * int(div) + item + ' ' * int(div)
            up_down[index] = item

        bottom_top = int(len(up_down[0]) / 2 + 6) * FB
        for index, item in enumerate(up_down):
            item = FB * 3 + item + FB * 3
            up_down[index] = item

        up_down.insert(0, bottom_top)
        up_down.insert(len(up_down), bottom_top)
        return '\n'.join(up_down)

    def __menu(self):
        names = self.get_names()
        menu = {}
        help = {}
        for name in names:
            if name[:5] == 'note_':
                help[name[5:]] = 1
        names.sort()
        # There can be duplicates if routines overridden
        prevname = ''
        for name in names:
            if len(name[3:]) == 1 and name[:3] == 'do_':
                if name == prevname:
                    continue
                prevname = name
                cmd = name[3:]
                if cmd in help:
                    func = getattr(self, 'note_' + cmd)
                    menu[cmd] = func()
                    del help[cmd]
                else:
                    menu[cmd] = getattr(self, name).__doc__
        ob = collections.OrderedDict(sorted(menu.items()))
        last = "Q"
        self.stdout.write('\n')
        for k, v in ob.items():
            if k != last:
                self.stdout.write('    %s. %s\n' % (k, v))
        self.stdout.write('    %s. %s\n' % (last, ob[last]))
        self.menu = ob



if __name__ == '__main__':
    app = None

    #try:
    app = Cmd()
    app.cmdloop()
    #except Exception as e:
        #app.logger.critical(app.error_msg(e))
        #if app:
         #  app.close()
        #subprocess.call("pause", shell=True)