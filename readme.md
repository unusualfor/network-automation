NETCONF & Network Automation

---

Part 1a) Check what is the initial configuration

netconf-console2 --host localhost --port 830 --get-config 
netconf-console2 --host localhost --port 830 --db=startup --get-config 
netconf-console2 --host localhost --port 830 --db=runtime --get-config 

Check wireshark

---

Part 1b) Modify network

Modify cleanup/change-eth0.xml

netconf-console2 --host localhost --port 830 --edit-config cleanup/change-eth0.xml
netconf-console2 --host localhost --port 831 --edit-config cleanup/change-eth0.xml
netconf-console2 --host localhost --port 832 --edit-config cleanup/change-eth0.xml

python network-check.py

---

Part 1c) Work with candidate

netconf-console2 --host localhost --port 830 --db=candidate --edit-config cleanup/change-eth0.xml

netconf-console2 --host localhost --port 830 --db=startup --get-config | grep 192
netconf-console2 --host localhost --port 830 --db=running --get-config | grep 192
netconf-console2 --host localhost --port 830 --db=candidate --get-config | grep 192

netconf-console2 --host localhost --port 830 --commit

netconf-console2 --host localhost --port 830 --db=startup --get-config | grep 192
netconf-console2 --host localhost --port 830 --db=running --get-config | grep 192
netconf-console2 --host localhost --port 830 --db=candidate --get-config | grep 192

---

Part 2) 