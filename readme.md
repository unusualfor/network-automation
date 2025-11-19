# NETCONF & Network Automation

## Architecture 

![Architecture](arch.png)

## Setup

Install the following in your Linux distribution:
* docker
* docker compose
* python3
* pip3
    * ncclient
    * netconf-console2
    * paramiko
* ansible

Depending on the distribution, only one of the two commands below will work:

    docker-compose up

    docker compose up

## Exercise 1

### Check initial configuration

Once everything is up and running, check the current configuration for the *running*, *startup* and *candidate* datastores using *netconf-console2* with *--get-config*.

1. Are there differences between the datastores? Why?

    netconf-console2 --host localhost --port 830 --get-config 

    netconf-console2 --host localhost --port 830 --db=startup --get-config 

    netconf-console2 --host localhost --port 830 --db=candidate --get-config 

### Modify running datastore

Copy and modify the file in *operations/change-eth0.xml* and use it to perform the following changes:

1. For each device, update eth0 IPv4 address values to be consistently in 192.168.1.0/24. Use *netconf-console2* to perform *edit-config* towards the *running* datastore.
2. Update the BBU-Router network to be in 10.0.1.0/30. Use *netconf-console2* to perform *edit-config* towards the *running* datastores. Make sure to configure the right interfaces of the devices.
3. Update the Router-Core network to be in 10.0.2.0/30. Use *netconf-console2* to perform *edit-config* towards the *running* datastores. Make sure to configure the right interfaces of the devices.

Activities:
* Check with *netconf-console2* with *--get-config*, towards *running*, *startup* and *candidate*
    * Would the current configuration allow the system to work properly?
    * Are there differences between the datastores? Why? 
    * What would happen if a device gets restarted in such a case?
    * What would happen to the network if the configuration applied to BBU eth1 was not matching the network configuration applied to Router eth1? Was there any check available to prevent this?
* Further checks: check that the three devices have consistent IP addresses with the *network-check.py* script and, in case not, modify IP addresses again

netconf-console2 --host localhost --port 830 --edit-config operations/change-eth0.xml
netconf-console2 --host localhost --port 831 --edit-config operations/change-eth0.xml
netconf-console2 --host localhost --port 832 --edit-config operations/change-eth0.xml

python network-check.py

### Work with candidate

Copy and modify the file in *operations/change-eth0.xml* and use it to perform the following changes:

1. For each device, update eth0 IPv4 address values to be consistently in 192.168.1.0/24. Use *netconf-console2* to perform *edit-config* towards the *candidate* datastore.
2. Update the BBU-Router network to be in 10.0.100.0/30. Use *netconf-console2* to perform *edit-config* towards the *candidate* datastores. Make sure to configure the right interfaces of the devices.
3. Update the Router-Core network to be in 10.0.200.0/30. Use *netconf-console2* to perform *edit-config* towards the *candidate* datastores. Make sure to configure the right interfaces of the devices.

Activities:
* Check with *netconf-console2* with *--get-config*, towards *running*, *startup* and *candidate*
    * Would the current configuration allow the system to work properly?
    * Are there differences between the datastores? Why? 
    * What would happen if a device gets restarted in such a case?
    * What would happen to the network if the configuration applied to BBU eth1 was not matching the network configuration applied to Router eth1? Was there any check available to prevent this?
* How does this approach scale? What is the impact in terms of time spent if we have to manage 100 RAN devices, 50 router devices and 1 core network device?
* Further checks: check that the three devices have consistent IP addresses with the *network-check.py* script and, in case not, modify IP addresses again

Bonus:
1. Perform a commit operation with *netconf-console2* so that the *candidate* datastore gets committed to the *running* and perform above checks again
* Check with *netconf-console2* with *--get-config*, towards *running*, *startup* and *candidate*
    * Would the current configuration allow the system to work properly?
    * Are there differences between the datastores? Why? 
    * What would happen if a device gets restarted in such a case?
2. Perform a copy-config operation with with *netconf-console2* so that the *running* datastore gets committed to the *startup* and perform above checks again
* Check with *netconf-console2* with *--get-config*, towards *running*, *startup* and *candidate*
    * Would the current configuration allow the system to work properly?
    * Are there differences between the datastores? Why? 
    * What would happen if a device gets restarted in such a case?

    netconf-console2 --host localhost --port 830 --db=candidate --edit-config operations/change-eth0.xml
    netconf-console2 --host localhost --port 830 --db=startup --get-config -x /interfaces
    netconf-console2 --host localhost --port 830 --db=running --get-config -x /interfaces
    netconf-console2 --host localhost --port 830 --db=candidate --get-config -x /interfaces

    netconf-console2 --host localhost --port 830 --commit
    netconf-console2 --host localhost --port 830 --db=startup --get-config -x /interfaces
    netconf-console2 --host localhost --port 830 --db=running --get-config -x /interfaces
    netconf-console2 --host localhost --port 830 --db=candidate --get-config -x /interfaces

    netconf-console2 --host localhost --port 830 --copy-running-to-startup
    netconf-console2 --host localhost --port 830 --db=startup --get-config -x /interfaces
    netconf-console2 --host localhost --port 830 --db=running --get-config -x /interfaces
    netconf-console2 --host localhost --port 830 --db=candidate --get-config -x /interfaces

## Exercise 2 - Automate with Python 

Start by restarting the system with 

    docker compose restart

Create a python script that makes use of [ncclient](https://pypi.org/project/ncclient/) to perform the following: 
1. Connect to each device
2. Use *edit-config* towards the *running* datastore and modify eth0 IPv4 address values to be consistently in 192.168.1.0/24
3. Check the devices with *get-config* and ensure all eth0 interfaces are correctly configured to be in 192.168.1.0/24

Activities:
* How does this approach scale? What is the impact in terms of time spent if we have to manage 100 RAN devices, 50 router devices and 1 core network device?

## Exercise 3 - Automate with Ansible

Start by restarting the system with 

    docker compose restart



## Assignment 

Start by restarting the system with 

    docker compose restart

Create a python script that makes use of [ncclient](https://pypi.org/project/ncclient/) to perform the following tasks. Feel free to reuse any code already available while making sure to comment the different functions. 
1. Connect to each device
2. Use *edit-config* towards the *candidate* datastore and modify eth0 IPv4 address values to be consistently in 192.168.1.0/24
3. Use *edit-config* towards the *candidate* datastore and modify backhaul IPv4 address values ({RAN: [backhaul0], Router: [eth1, eth2], Core: [eth1]}) to be consistently in the related networks (BBU-Router network to be in 10.0.1.0/30, Router-Core network to be in 10.0.2.0/30).
4. Check the devices with *get-config* towards the *candidate* datastore and ensure all interfaces are correctly configured as expected.
If confirmed, perform a *commit* operation and check the *running* datastore.

Activities:
* Check with *netconf-console2* with *--get-config*, towards *running*, *startup* and *candidate*
    * Would the current configuration allow the system to work properly?
    * Are there differences between the datastores? Why? 
    * What would happen if a device gets restarted in such a case?
* How does this approach scale? What is the impact in terms of time spent if we have to manage 100 RAN devices, 50 router devices and 1 core network device?
* Further checks: check that the three devices have consistent IP addresses with the *network-check.py* script and, in case not, modify IP addresses again