#!/usr/bin/python3
import argparse
import json
import os
import re
import sys
import time
from subprocess import Popen
import requests
import settings


FACECAM_DATA_DIR = settings.FACECAM_DATA_DIR
WEBCAM_LOCKFILE = settings.WEBCAM_LOCKFILE
WEBCAM_ERRFILE = settings.WEBCAM_ERRFILE
WEBCAM_LOGFILE = settings.WEBCAM_LOGFILE
RASPBERRY_SYSTEM = settings.RASPBERRY_SYSTEM
recognition_script = ''

if RASPBERRY_SYSTEM:
    recognition_script = 'picam.py'
else:
    recognition_script = 'webcam.py'


def init_recogcam():

    process_command = 'python3 {script}'.format(script=recognition_script)

    Popen(process_command,
          stdout=open(WEBCAM_LOGFILE, 'w'),
          stderr=open(WEBCAM_ERRFILE, 'w'),
          shell=True)


def main():
    parser = argparse.ArgumentParser(description='Facecam software')
    parser.add_argument('command', help='Command to execute: start,stop')
    arguments = parser.parse_args()

    command = arguments.command

    if command=='start':
        if os.path.exists(WEBCAM_LOCKFILE):
            os.remove(WEBCAM_LOCKFILE)
        init_recogcam()
    elif command=='stop':
        if not os.path.exists(WEBCAM_LOCKFILE):
            open(WEBCAM_LOCKFILE, 'w').close()
            # espera o processo do reconhecimento com a camera terminar
            time.sleep(2)
    

if __name__ == "__main__":
    main()
