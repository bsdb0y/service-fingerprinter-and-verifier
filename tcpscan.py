#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
port_fingerprinter.py
~~~~~~~~~~~~~~~~~~~~~
It is use to retrieve the port and service information.
"""

import logging
import os
import sys
import threading
import time
import socket
from queue import Queue
from logging import handlers

from db_store import store_to_db
from pybangrab import banner  # for banner grabbing

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SCRIPT_NAME = os.path.basename(__file__)

"""
set logger and add handlers for the logger.
Add log file. Also set file size of log files.
"""

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
LOG_TEMPLATE = "%(asctime)s %(module)s %(levelname)8s: %(message)s"
FORMATTER = logging.Formatter(LOG_TEMPLATE)

# Logging - File Handler
LOG_FILE_SIZE_IN_MB = 10
COUNT_OF_BACKUPS = 5  # example.log example.log.1 example.log.2
LOG_FILE_SIZE_IN_BYTES = LOG_FILE_SIZE_IN_MB * 1024 * 1024
LOG_FILENAME = os.path.join(
               SCRIPT_DIRECTORY,
               os.path.splitext(SCRIPT_NAME)[0]
               ) + '.log'

FILE_HANDLER = handlers.RotatingFileHandler(
               LOG_FILENAME,
               maxBytes=LOG_FILE_SIZE_IN_BYTES,
               backupCount=COUNT_OF_BACKUPS
               )

FILE_HANDLER.setLevel(logging.DEBUG)
FILE_HANDLER.setFormatter(FORMATTER)
logger.addHandler(FILE_HANDLER)

# Logging - STDOUT Handler
STDOUT_HANDLER = logging.StreamHandler(sys.stdout)
STDOUT_HANDLER.setFormatter(FORMATTER)
logger.addHandler(STDOUT_HANDLER)

MAX_THREAD_COUNT = 4
socket.setdefaulttimeout(15)


def get_service_name(port, proto):
    """
    Check and Get service name from port and proto string combination using
    socket.getservbyport param port string or id param protocol string
    return Service name if port and protocol are valid, else None
    """

    try:
        name = socket.getservbyport(int(port), proto)
    except OSError:
        info_message = "port {0} not found /etc/services file"
        info_message += " but banner module will handle it."
        logger.info(info_message.format(port))
        return None
    except Exception as e:
        logger.error(str(e) + " found on {}".format(port))
        name = " "
    return name


def portscan(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:  # (socket.timeout, ConnectionRefusedError):
        con = sock.connect((target, port))
        with print_lock:
            logger.info("Open: {0}:{1}".format(target, port))
            result , updated_service_name = banner(sock, target, port, logger)
            if updated_service_name:
                servname = updated_service_name
            else:
                servname = get_service_name(port, 'tcp')
            store_to_db(target, port, servname, result, logger)

    except (ConnectionRefusedError, socket.timeout, socket.error):
        pass

    except Exception as e:
        logger.error(str(e) + " found on {}".format(port))

    finally:
        sock.close()


""" The threader thread pulls an worker from the queue and processes it"""


def run_scan_on_thread():
    while True:
        # gets an worker from the queue
        worker = worker_queue_object.get()

        """Run the example job with the avail worker in queue (thread)"""
        portscan(worker)

        # completed with the job

        worker_queue_object.task_done()


if __name__ == '__main__':

    if len(sys.argv) != 4:
        sys.exit('Usage: %s <host/target> <start_port> <end_port>' %
                 SCRIPT_NAME)

    """
    a print_lock is what is used to prevent "double" modification of shared
    variables.

    this is used so while one thread is using a variable, others cannot access
    it. Once done, the thread releases the print_lock, to use it, you want to
    specify a print_lock per thing you wish to print_lock.
    """

    print_lock = threading.Lock()
    target = sys.argv[1]
    start_port = sys.argv[2]
    end_port = sys.argv[3]

    # Create the queue and threader

    worker_queue_object = Queue()

    # how many threads are we going to allow for
    for thread_counter in range(MAX_THREAD_COUNT):
        thread_counter = threading.Thread(target=run_scan_on_thread)

        # classifying as a daemon, so they will die when the main dies
        thread_counter.daemon = True

        # begins, must come after daemon definition
        thread_counter.start()

    start = time.time()

    # 4 jobs assigned.

    for worker in range(int(start_port), int(end_port)):
        worker_queue_object.put(worker)

    # wait until the thread terminates.
    worker_queue_object.join()

    print(('\nEntire job took:', time.time() - start))
