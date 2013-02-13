dmon - directory monitor
-----------------------
nutshell:
- recursively watches a directory
- create, update, delete events
- runs on linux and osx
- custom event implementation

import:
- from dmon import *

usage:
```python
#!/usr/bin/env python
from subprocess import call
import os
import sys
sys.path.append(os.getcwd())
import subprocess
from dmon import *

'''
sample implementation of a dmon
handler. expected methods are
- on_create(self, file)
- on_delete(self, file)
- on_update(self, file)
'''
class Dmonake:
    _compile = ["coffee", "-c"]
    _delete = ["rm"]

    def _check(self, file):
        return '.coffee' == file[-7:].lower()

    def _run(self, command, file):
        try:
            subprocess.check_output(command + [file])
        except subprocess.CalledProcessError as e:
            print(e.output)
        except:
            pass

    ''' interface method '''
    def on_delete(self, file):
        pass
        #if self._check(file):
        #    self._run(self._delete, file[:-7]+'.js')

    ''' interface method '''
    def on_update(self, file):
        if self._check(file):
            self._run(self._compile, file)

    ''' interface method '''
    def on_create(self, file):
        if self._check(file):
            self.on_update(file)


if __name__ == '__main__':
    dmon.start(sys.argv[1], [Dmonake()])
```
