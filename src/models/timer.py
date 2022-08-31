import threading
import time

class Timer(object):
    """
    Python periodic Thread using Timer with instant cancellation
    """

    def __init__(self, callback=None, period=1, name=None, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.callback = callback
        self.period = period
        self.stop = False
        self.current_timer = None
        self.schedule_lock = threading.Lock()
        self.next_call = time.time()

    def start(self):
        """
        Mimics Thread standard start method
        """
        self.schedule_timer()

    def run(self):
        """
        By default, run callback. Override it if you want to use inheritance
        """
        if self.callback is not None:
            self.callback(*self.args, **self.kwargs)

            
    def _run(self):
        """
        Run desired callback and then reschedule Timer (if thread is not stopped)
        """
        starttime = time.time()
        self.run()
        with self.schedule_lock:
            if not self.stop:
                self.timedelta = time.time() - starttime
                self.schedule_timer()


    def schedule_timer(self):
        """
        Schedules next Timer run
        """
        self.next_call = self.next_call + self.period
        timer_period = self.next_call - time.time()
        if timer_period < 0:
            timer_period = 0
            self.next_call = time.time()
        self.current_timer = threading.Timer(timer_period, self._run, *self.args, **self.kwargs)
        self.current_timer.daemon = True
        if self.name:
            self.current_timer.name = self.name
        self.current_timer.start()

    def cancel(self):
        """
        Mimics Timer standard cancel method
        """
        with self.schedule_lock:
            self.stop = True
            if self.current_timer is not None:
                self.current_timer.cancel()

    def join(self):
        """
        Mimics Thread standard join method
        """
        self.current_timer.join()
