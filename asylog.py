# -*- coding: utf-8 -*-
from six import with_metaclass
try:
    import Queue
except ImportError:
    import queue as Queue
from logutils.queue import QueueHandler, QueueListener
from datetime import datetime
import os
from .helpers import Singleton
import logging
import colorlog
from .config import Config


class Asylog(with_metaclass(Singleton, object)):
    '''
    Asylog is asynchronous and singleton logging class
    extened from python standard lib logging.
    requirement: python2.7, logutils(pip install logutils)
    '''

    def __init__(self):

        self.logger = colorlog.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        logging.addLevelName(logging.INFO, 'I')
        # colorlog.default_log_colors['I'] = "bold_green"
        logging.addLevelName(logging.CRITICAL, 'C')
        colorlog.default_log_colors['C'] = "bold_red"
        logging.addLevelName(logging.DEBUG, 'D')
        logging.addLevelName(logging.WARNING, 'W')

        SUCCESS = logging.DEBUG + 1
        logging.addLevelName(SUCCESS, 'success')
        colorlog.default_log_colors['success'] = "bold_green"
        setattr(self.logger, 'success', lambda message, *args: self.logger._log(SUCCESS, message, args))

        # Console log msg setting
        sh = colorlog.StreamHandler()
        sh.setLevel(logging.DEBUG + 1)
        sh_fmt = colorlog.ColoredFormatter('%(log_color)s> %(message)s')
        sh.setFormatter(sh_fmt)
        self.logger.addHandler(sh)

        # File log msg setting
        self.config = Config()

        folder_name = "{}_Log_{}".format(self.config.get_module_name(),
                                         datetime.now().year)
        folder_path = os.path.join(os.getcwd(), folder_name)
        self._make_sure_dir_exists(folder_path)

        filename = '{}.txt'.format(datetime.now().strftime("Log %Y%m%d"))
        self.log_path = os.path.join(folder_path, filename)

        fh = logging.FileHandler(self.log_path)
        fmt = logging.Formatter('%(asctime)s, %(levelname)s, %(module)s, %(station)s, %(serial)s, "%(message)s"',
                                datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(fmt)
        que = Queue.Queue(-1)
        queue_handler = QueueHandler(que)
        queue_handler.setLevel(logging.INFO)
        self.logger.addHandler(queue_handler)
        self.listener = QueueListener(que, fh)

        self.latest_filter = None

    def _make_sure_dir_exists(self, path):
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

    def getLogger(self):
        return self.logger

    def change_filter(self, module, station, serial):
        class ContextFilter(logging.Filter):
            def filter(self, record):
                record.module = module
                record.station = station
                record.serial = serial
                return True

        if self.latest_filter:
            self.logger.removeFilter(self.latest_filter)
            del self.latest_filter
        self.latest_filter = ContextFilter()
        self.logger.addFilter(self.latest_filter)


    def change_adapter(self, module, station):
        class CustomAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                return '%(module)s, %(station)s, "%(msg)s" ' % {"module": self.extra['module'],
                                                                "station": self.extra['station'],
                                                                "msg": msg}, kwargs

        self.logger = CustomAdapter(logging.getLogger(), {'module': module, "station": station})
