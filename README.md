# service-fingerprinter-and-verifier

It is used for service fingerprinting which provides the information on
service-version, service-port status with top 5 common service-verification support in Python3.

It supports mutithreading and Logging mechanism.

Files:

config.yml   - configuration file for Database

db_store.py  - code file for storing the information in the MySQL/MariaDB database.

demo.png     - working screen-shot

pybangrab.py - improved banner grabbing module for service version fingerprinting with fileless support.

requirements.txt - Python3 package requirements file

service_verifier.py - module for service verification after fingerprinting them.

tcpscan.py   - improved multithreaded tcp scanner with logging support.
