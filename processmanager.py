#!/usr/bin/env python

import json
import subprocess
import threading
import web

def getProcessName(process):
    return process_map[process["command"][0]]

def execute(process):
    process = None
    if 'cwd' in process:
        process = subprocess.Popen(process["command"], cwd=process["cwd"])
        while process.returncode is None:
              process = subprocess.Popen(process["command"], cwd=process["cwd"])
    else:
        process = subprocess.Popen(process["command"])
        while process.returncode is None:
              process = subprocess.Popen(process["command"])
    process_map[getProcessName(process)]=process

def stop(process):
    process.terminate()
    while process.returncode is not None:
        process.kill()

class processFilter:
    def POST(self):
        processList = json.loads(web.data())
        for process in processList:
            if (process["state"]=="running"):
                d=threading.Thread(name='daemon', target=execute(process))
                d.setDaemon(True)
            elif (process["state"]=="stopped"):
                d=threading.Thread(name='daemon', target=stop(process_map[getProcessName(process)]))
                d.setDaemon(True)

urls = (
    '/process', 'processFilter',
)

process_map = {}

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()