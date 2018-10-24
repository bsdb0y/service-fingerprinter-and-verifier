#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dns.resolver
import logging
import os
import pymysql
import socket
import sys
import yaml
from ftplib import FTP

SUCCESS = 0
ERROR = 1
socket.setdefaulttimeout(15)


def debug_info_thrower(service_name, success, host, port, logger):
    if not success:
        debug_success_string = "{0} successfully verified on {1}:{2}"
        logger.debug(debug_success_string.format(service_name, host, port))
    else:
        debug_fail_string = "{0} verification failed on {1}:{2}"
        logger.debug(debug_fail_string.format(service_name, host, port))


def ftp_check(host, port, logger):
    try:
        ftp = FTP('')
        ftp.connect(host, port)
        debug_info_thrower("ftp_check", SUCCESS, host, port, logger)
    except (socket.timeout, ConnectionRefusedError):
        debug_info_thrower("ftp_check", ERROR, host, port, logger)
    except Exception as e:
        logger.error("{0} error found on {1}:{2}".format(e, host, port))


def smtp_check(host, port, logger):
    try:
        mail_record_type = "MX"
        dns_resolver = dns.resolver.Resolver()
        mail_records_object = dns_resolver.query(host, mail_record_type)
        first_mx_record = mail_records_object[0]
        temporary_string = str(first_mx_record)
        temporary_string = temporary_string.split(" ")
        mail_host = temporary_string[1]
        connection_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect_result = connection_sock.connect((mail_host, port))
        debug_info_thrower("smtp_check", SUCCESS, host, port, logger)
        smtp_command = "HELO\n".encode("UTF-8") # for python3 encoding to UTF-8
        mail_server_info = connection_sock.recv(200)
        return mail_server_info
    except socket.timeout:
        debug_info_thrower("smtp_check", ERROR, host, port, logger)
    except Exception as e:
        logger.error("{0} error found on {1}:{2}".format(e, host, port))


def database_check(host, port, logger):
    SERVER = host
    PORT = port
    USER = "root"
    PASSWORD = ""
    try:
        database_connection_object = pymysql.connect(
                host=SERVER,
                port=int(PORT),
                user=USER,
                passwd=PASSWORD
                )
    except Exception as error:
        error_code = error.args[0]
        if error_code == 2003:
            debug_info_thrower("database_check", ERROR, host, port, logger)
        elif error_code == 1045:
            debug_info_thrower("database_check", SUCCESS, host, port, logger)
        else:
            error_msg = "{0} error found on {1}:{2}"
            logger.error(error_msg.format(error, host, port))


"""
if __name__ == '__main__':
    host = ["127.0.0.1", "xxx.yyy.zzz.com"]
    port = [21, 25]
    ftp_check(host[0], port[0])
    smtp_check(host[1], port[1])
    database_check(host[0], "3000")
"""
