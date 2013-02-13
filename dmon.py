from optparse import OptionParser
import sys
import os
sys.path.append(os.path.dirname(__file__)+'/lib')
import thread
import time

class Dmon:
    def __init__(self, dir, handlers):
        self._handlers = handlers
        self._dir = dir

    def _call_handler(self, method, fname):
        for handler in self._handlers:
            getattr(handler, method)(fname)

    def _run_pyinotify(self):
        from lib import pyinotify
        class PyInotifyEventProcessor(pyinotify.ProcessEvent):
            def __init__(self, c_handler):
                self._call = c_handler
            def process_IN_CREATE(self, event):
                self._call('on_create', event.pathname)
            def process_IN_DELETE(self, event):
                self._call('on_delete', event.pathname)
            def process_IN_MODIFY(self, event):
                self._call('on_update', event.pathname)
        wm = pyinotify.WatchManager()
        self._observer = pyinotify.Notifier(wm, PyInotifyEventProcessor(self._call_handler))
        mask = pyinotify.ALL_EVENTS
        wm.add_watch(self._dir, mask, rec=True)
        while True:
            self._observer.process_events()
            if self._observer.check_events():
                self._observer.read_events()
            time.sleep(1)

    def _run_macfse(self):
        from lib import fsevents
        from fsevents import Stream
        from fsevents import Observer
        def macfse_callback(event):
            if event.mask in [256, 128]:
                self._call_handler('on_create', event.name)
            elif event.mask in [512, 64]:
                self._call_handler('on_delete', event.name)
            elif event.mask == 2:
                self._call_handler('on_update', event.name)
        self._observer = Observer()
        self._stream = Stream(macfse_callback, self._dir, file_events=True)
        self._observer.schedule(self._stream)
        self._observer.start()


    def start(self):
        if 'darwin' in sys.platform.lower():
            self._run_macfse()
        elif 'linux' in sys.platform.lower():
            self._run_pyinotify()

    def stop(self):
        if 'darwin' in sys.platform.lower():
            self._observer.unschedule(self._stream)
            self._observer.stop()
        elif 'linux' in sys.platform.lower():
            self._observer.stop()

_dmon = None
def start(dir, handlers):
    _dmon = Dmon(dir, handlers)
    thread.start_new_thread(_dmon.start, ())
    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        _dmon.stop()
