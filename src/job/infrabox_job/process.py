import subprocess
import sys
import os
from datetime import datetime

import requests

class Failure(Exception):
    def __init__(self, message):
        super(Failure, self).__init__(message)
        self.message = message

class ApiConsole(object):
    def __init__(self):
        self.output = []
        self.last_send = datetime.now()
        self.is_finish = False
        self.enable_logging = True

        self.verify = True
        if os.environ.get('INFRABOX_GENERAL_DONT_CHECK_CERTIFICATES', 'false') == 'true':
            self.verify = False

    def collect(self, line, show=False):
        line = line.encode("utf-8")
        if self.enable_logging:
            sys.stdout.write(line)
            sys.stdout.flush()

        if show:
            line = line.strip("\r\n")
            line = "%s|%s" % (datetime.now().strftime("%H:%M:%S"), line)
            self.output.append(line)

        diff = datetime.now() - self.last_send
        seconds = diff.seconds + diff.microseconds / 1E6

        if seconds < 5.0:
            # we wait some more
            return

        self.flush()

    def execute(self, command, cwd=None, shell=False, show=False, env=None, background=False, ignore_error=False, show_cmd=True):
        if show_cmd:
            self.collect(' '.join(command) + '\n', show=show)

        process = subprocess.Popen(command, shell=shell,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   cwd=cwd, env=env, universal_newlines=True)

        if background:
            return

        # Poll process for new output until finished
        msg = ""
        while True:
            line = process.stdout.readline()
            if not line:
                break

            line = line.rstrip()
            msg += line
            self.collect(line, show=show)

        process.wait()

        if ignore_error:
            return

        self.flush()
        exitCode = process.returncode
        if exitCode != 0:
            raise Exception(msg)

    def finish(self):
        self.is_finish = True

    def header(self, h, show=False):
        h = "\n## " + h + '\n'
        self.collect("", show=show)
        self.collect(h, show=show)
        self.collect(('=' * len(h)) + "\n", show=False)

    def flush(self):
        try:
            if self.is_finish:
                return

            if not self.output:
                return

            buf = ""
            for l in self.output:
                buf += l.rstrip() + "\n"

            payload = {
                "output": buf
            }

            api_server = os.environ["INFRABOX_ROOT_URL"] + "/api/job"

            headers = {
                'Authorization': 'token ' + os.environ['INFRABOX_JOB_TOKEN']
            }

            requests.post("%s/consoleupdate" % api_server,
                          headers=headers,
                          verify=self.verify,
                          json=payload).json()
            self.output = []
        except Exception as e:
            print e

        self.last_send = datetime.now()
