# Turhouse 
    
Alarm and home automation system related to the TURRIS:GADGETS project of Jablotron and CZ.NIC

## INSTALL

1. download

        # git clone git://github.com/janredl/turhouse.git

2. copy empty configuration template to turhouse.conf

        # cd turhouse
        # cp turhouse.conf.empty turhouse.conf
    
3. run with empty config & generate events from all devices

        # ./turhouse.py
    
4. copy config dump with autolearned devices to turhouse.conf

        # cp turhouse.conf.dump turhouse.conf
    
5. edit turhouse.conf; rename [unknown*] devices, and set up all configuration options (see turhouse.conf.example)  

6. create your own turhousemanager.py (see turhousemanager.py.example)

## LOGGING

logging is configured in turhouse_logging.conf, by default creates two logfiles 

* **/var/log/turhouse-oasis.log**  - all messages from/to jablotron devices
* **/var/log/turhouse.log**   - turhouse events (messages from controllers, zones, alarm events etc.)
