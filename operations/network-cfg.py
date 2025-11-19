#!/usr/bin/env python3
"""
Minimal Network Auto-Configuration Script
Just define your config and run!
"""

from ncclient import manager
from ipaddress import IPv4Interface

# ============================================================================
# STEP 1: Define your network configuration
# ============================================================================

NETWORK_CONFIG = {
    'RAN': {
        'eth0': IPv4Interface('192.168.1.10/24'),
        'backhaul0': IPv4Interface('10.0.1.1/30')
    },
    'router': {
        'eth0': IPv4Interface('192.168.1.20/24'),
        'eth1': IPv4Interface('10.0.1.2/30'),
        'eth2': IPv4Interface('10.0.2.2/30')
    },
    'core': {
        'eth0': IPv4Interface('192.168.1.30/24'),
        'eth1': IPv4Interface('10.0.2.1/30')
    }
}

# Device connection info
CONNECTIONS = {
    'RAN': {'host': 'localhost', 'port': 830},
    'router': {'host': 'localhost', 'port': 831},
    'core': {'host': 'localhost', 'port': 832}
}

# ============================================================================
# STEP 2: Run the configuration
# ============================================================================

def apply_config():
    """Apply configuration to all devices"""
    
    for device, interfaces in NETWORK_CONFIG.items():
        print(f"\nConfiguring {device}...")
        
        # Connect to device
        conn = manager.connect(
            host=CONNECTIONS[device]['host'],
            port=CONNECTIONS[device]['port'],
            username='admin',
            password='admin',
            hostkey_verify=False,
            timeout=10,
            device_params={'name': 'default'}
        )
        
        # Configure each interface
        for iface, ip_interface in interfaces.items():
            ip = str(ip_interface.ip)
            prefix = ip_interface.network.prefixlen
            
            xml = f'''
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>{iface}</name>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"
            xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"
            nc:operation="replace">
        <enabled>true</enabled>
        <address>
          <ip>{ip}</ip>
          <prefix-length>{prefix}</prefix-length>
        </address>
      </ipv4>
    </interface>
  </interfaces>
</config>'''
            
            conn.edit_config(target='running', config=xml)
            print(f"  ✅ {iface}: {ip_interface}")
        
        conn.close_session()
    
    print("\nAll devices configured!")

if __name__ == "__main__":
    apply_config()
