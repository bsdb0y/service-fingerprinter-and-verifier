#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import os
import re
import yaml
from configparser import ConfigParser

import service_verifier

SUCCESS = 0
ERROR = 1
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SMTP_ERROR = "500 Syntax error, command unrecognized".lower()


def string_parse(str_to_parse, host, port, logger):
    try:
        data_str = str_to_parse.decode('UTF-8')
    except UnicodeError as unicode_error:
        info_message = "Inserting info of port {0} as a string without UTF-8"
        logger.info(" {} found on port {}".format(unicode_error, port))
        logger.info(info_message.format(port))
        data_str = str(str_to_parse)

    if 'http' in data_str.lower():
        string_to_list = re.split('\r\n', data_str)
        for item in string_to_list:
            if "Server:" == item[:7]:  # comparing the substring from string.
                service_verifier.debug_info_thrower(
                        "http_check",
                        SUCCESS,
                        host,
                        port,
                        logger
                        )
                return item, "http"
            else:
                pass
                """
                service_verifier.debug_info_thrower(
                        "http_check",
                        SUCCESS,
                        host,
                        port,
                        logger
                        )
                """
    elif 'ftp' in data_str.lower():
        temporary_buffer = io.StringIO(data_str)
        first_line = temporary_buffer.readline()
        service_verifier.ftp_check(host, port, logger)
        return first_line, "ftp"

    elif 'ssh' in data_str.lower():
        temporary_ssh_buffer = io.StringIO(data_str)
        first_ssh_line = temporary_ssh_buffer.readline()
        if "ssh-2.0" in first_ssh_line.lower():
            service_verifier.debug_info_thrower(
                    "ssh_check",
                    SUCCESS,
                    host,
                    port,
                    logger
                    )
            return first_ssh_line, "ssh"
        else:
            service_verifier.debug_info_thrower(
                "ssh_check",
                ERROR,
                host,
                port,
                logger
                )

    elif port == 25:
        mail_server_info = service_verifier.smtp_check(host, port, logger)
        return mail_server_info, "smtp"
    elif "mysql" in data_str.lower():
        service_verifier.database_check(host, port, logger)
        return data_str, "mysql"

    elif "mariadb" in data_str.lower():
        service_verifier.database_check(host, port, logger)
        return data_str, "mariadb"

    return data_str, None


def banner(connsocket, target_host, target_port, logger):
    try:
        data0 = "GET / HTTP/1.1\r\nhost:"
        data1 = str(target_host)
        data2 = "\r\nConnection: close\r\n\r\n"

        data = data0 + data1 + data2  # payload for banner.

# Data must be encoded in UTF_8 For python3,
        connsocket.send(data.encode('UTF_8'))
# default is in bytes strings e.g, b'hello'

        recv_ban = connsocket.recv(10000)
        banner_parsed, new_service_name = string_parse(
                        recv_ban,
                        target_host,
                        target_port,
                        logger
                        )
        return banner_parsed, new_service_name

    except OSError as e:
        pass
        return " "

    except Exception as e:
        logger.error(e)
        return " "
