#!/usr/bin/env python
# forked from : Created by Jeremy Epstein <http://greenash.net.au/>. Use it as you will: hack, fork, play.

from glob import glob
import sys
from threading import Thread
from time import sleep


class CreatePPTXProcess(Thread):
    total_file_count = 10
    files_processed_count = 0
    
    def __init__(self, *args, **kwargs):
        Thread.__init__(self)
        self.files_processed_count = 0
    
    def run(self):
        for i in range(0, self.total_file_count):
            sleep(1.0)
            self.files_processed_count += 1
    
    def percent_done(self):
        """Gets the current percent done for the thread."""
        return float(self.files_processed_count) / float(self.total_file_count) * 100.0
    
    def get_progress(self):
        """Can be called at any time before, during or after thread
        execution, to get current progress."""
        return '%d files (%.2f%%)' % (self.files_processed_count, self.percent_done())


class CreatePPTXProcessShellRun(object):
    """Runs an instance of the thread with shell output / feedback."""
    
    def __init__(self, init_class=CreatePPTXProcess):
        self.init_class = init_class
    
    def __call__(self, *args, **kwargs):
        cxp = self.init_class(*args, **kwargs)

        print '%s threaded process beginning.' % cxp.__class__.__name__
        print '%d files will be processed. ' % cxp.total_file_count + 'Now beginning progress output.' 
        print cxp.get_progress()

        cxp.start()

        while cxp.is_alive() and cxp.files_processed_count < cxp.total_file_count:
            sleep(0.1)
            print cxp.get_progress()

        print '%s threaded process complete. Now exiting.' % cxp.__class__.__name__


if __name__ == '__main__':
    CreatePPTXProcessShellRun()()
