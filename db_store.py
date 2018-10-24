#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pymysql
import yaml
import warnings
from configparser import ConfigParser
from pymysql.err import ProgrammingError


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# load the configuration file
try:
    with open(os.path.join(SCRIPT_DIRECTORY, 'config.yml')) as config_file:
        configuration = yaml.load(config_file)

except yaml.YAMLError as yaml_error:
    logger.debug(yaml_error)

except FileNotFoundError as file_error:
    logger.debug(file_error)

# load the DB credentials
SERVER = configuration.get('host')
PORT = configuration.get('port')
USER = configuration.get('user')
PASSWORD = configuration.get('password')
DB = configuration.get('database')


def connect_db(logger):

    try:
        try:
            database_connection_object = pymysql.connect(
                    host=SERVER,
                    port=int(PORT),
                    user=USER,
                    passwd=PASSWORD,
                    db=DB
                    )

        except pymysql.err.InternalError:
            database_connection_object = pymysql.connect(
                    host=SERVER,
                    port=int(PORT),
                    user=USER,
                    passwd=PASSWORD
                    )

            with database_connection_object.cursor() as cur:
                cur.execute("create database {foo}".format(foo=DB))
                database_connection_object = pymysql.connect(
                        host=SERVER,
                        port=int(PORT),
                        user=USER,
                        passwd=PASSWORD,
                        db=DB
                        )

        except Exception as e:
            logger.error(e)

    except pymysql.err.OperationalError:
        logger.error("MySQL daemon is not running")
        print("MySQL service is not running\n")
    except Exception as e:
        logger.error(e)

    return(database_connection_object)


def initialize_tables(database_connection_object, logger):
    """
    Use to create tables in the DB.
    """

    try:
        cmd = """
            create table if not exists `services_fingerprint_table` (
            target varchar(20),
            port   int,
            name varchar(20),
            version varchar(500))
            """
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            database_connection_object.cursor().execute(cmd)

    except ProgrammingError as programming_error:
            logger.error(programming_error)

    except pymysql.err.Warning as pymysql_warning:
            logger.error(pymysql_warning)


def store_to_db(host, port, service_name, banner, logger):

    database_connection_object = connect_db(logger)

    cmd = initialize_tables(database_connection_object, logger)

    with database_connection_object.cursor() as cur:
        cmd_ins = "insert into services_fingerprint_table " \
                  "(target, port, name, version) VALUES(%s,%s,%s,%s)"
        try:
            cur.execute(cmd_ins, (host, port, service_name, banner))
            database_connection_object.commit()
        except Exception as e:
            logger.error(e)
            database_connection_object.rollback()
