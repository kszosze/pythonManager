#!/usr/bin/env python

import logging
import json
import subprocess
import threading
import web

def getProcessName(process):
    return process_map[process["command"][0]]

def execute(process):
    process = None
    logger.info("Runing app " + getProcessName(process))
    if 'cwd' in process:
        process = subprocess.Popen(process["command"], cwd=process["cwd"])
        while process.returncode is None:
              process = subprocess.Popen(process["command"], cwd=process["cwd"])
    else:
        process = subprocess.Popen(process["command"])
        while process.returncode is None:
              process = subprocess.Popen(process["command"])
    process_map[getProcessName(process)]=process
    logger.info("App " + getProcessName(process) + " is running")

def stop(process):
    logger.info("Stopping app " + getProcessName(process))
    process.terminate()
    while process.returncode is not None:
        process.kill()
    logger.info("App " + getProcessName(process) + " stopped")

def error(self, reason):
        d = json.dumps({ "status" : "error", "reason" : reason})
        return app.HTTPError("400 Bad Request", {"Content-type": "application/json"}, d)

class processFilter:
    def POST(self):
        logger.info("Message with commands has been received")
        web.header('Content-Type', 'application/json')
        if not web.data():
            log.error("Empty String received")
            error(self, "Wrong content")

        processList = json.loads(web.data())
        for process in processList:
            if (process["state"]=="running"):
                d=threading.Thread(name='daemon', target=execute(process))
                d.setDaemon(False)
            elif (process["state"]=="stopped"):
                d=threading.Thread(name='daemon', target=stop(process_map[getProcessName(process)]))
                d.setDaemon(False)
            else:
                error(self, "Wrong data")
urls = (
    '/process', 'processFilter',
)

process_map = {}

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()