import sys
import time
 
 
class ProgressBase(object):
    """
   An abstract class that helps to put text on the screen and erase it again.
   """
   
    def __init__(self):
        self._str = ''
 
    def _show(self, text):
        sys.stderr.write('\b' * len(self._str))
        self._str = text.ljust(len(self._str))
        sys.stderr.write(self._str)
 
 
class with_progress_meter(ProgressBase):
    """
   A progress meter for long loops of known length, written on stderr.
 
   Wrap this around a list-like object, for example:
   for line in with_progress_meter(lines, action = 'Processing lines...')
   """
 
    def __init__(self, iterable = None, total = None, action = None, done = 'done'):
        super(with_progress_meter, self).__init__()
        self.iterable = iterable
        if total is None:
            total = len(self.iterable)
        self.total = total
        self.start_time = time.time()
        self.last = self.start_time
        self.at = 0
        self.done = done
        if action:
            sys.stderr.write(action + ' ')
        self._str = ''
 
    def update(self, at):
        self.at = at
        now = time.time()
   
    def stop(self):
        self._show(self.done or '')
        sys.stderr.write('\n')
 
    def __iter__(self):
        at = 0
        for item in self.iterable:
            yield item
            at += 1
            self.update(at)
        self.stop()
   
    def _progress(self):
        pass
