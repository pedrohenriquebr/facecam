#!/usr/bin/python3

from dotenv import load_dotenv
import os


load_dotenv()

RECOGNITION_HOST = os.getenv('RECOGNITION_HOST', '0.0.0.0')
FACECAM_DATA_DIR = os.getenv('FACECAM_DATA_DIR', '/usr/local/facecam/data')
WEBCAM_LOCKFILE = os.path.join(FACECAM_DATA_DIR, 'facecam.lock')
WEBCAM_ERRFILE = os.path.join(FACECAM_DATA_DIR, 'facecam_err.log')
WEBCAM_LOGFILE = os.path.join(FACECAM_DATA_DIR, 'facecam_log.log')
RASPBERRY_SYSTEM = os.uname()[4].startswith('arm')
TMP_IMG = os.getenv('TMP_IMG', '/tmp/img.jpg')
