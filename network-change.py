#!/usr/bin/env python3
"""
Backhaul IP Address Changer
Simple script to change IP addresses on backhaul interfaces
"""

from ncclient import manager
import sys

class BackhaulIPChanger:
    def __init__(self):
        self.devices = {
            'RAN': {'host': 'localhost', 'port': 830},
            'Router': {'host': 'localhost', 'port': 831},
            'Core': {'host': 'localhost', 'port': 832}
        }
        
        # Interfaces to change per device
        self.interfaces = {
            'RAN': ['backhaul0'],
            'Router': ['eth1', 'eth2'], 
            'Core': ['eth1']
        }
    
    def connect_device(self, device_name):
        """Connect to a NETCONF device"""
        device = self.devices[device_name]
        try:
            conn = manager.connect(
                host=device['host'],
                port=device['port'],
                username='admin',
                password='admin',
                hostkey_verify=False,
                timeout=10,
                device_params={'name': 'default'}
            )
            return conn
        except Exception as e:
            print(f"❌ Failed to connect to {device_name}: {e}")
            return None
    
    def create_ip_change_xml(self, interface_name, ip_address, prefix_length=30):
        """Create XML configuration to change IP address"""
        return f'''
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>{interface_name}</name>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip" 
            xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" 
            nc:operation="replace">
        <enabled>true</enabled>
        <address>
          <ip>{ip_address}</ip>
          <prefix-length>{prefix_length}</prefix-length>
        </address>
      </ipv4>
    </interface>
  </interfaces>
</config>'''
    
    def change_interface_ip(self, device_name, interface_name, new_ip, prefix_length=30):
        """Change IP address on a specific interface"""
        print(f"🔧 Changing {device_name}:{interface_name} to {new_ip}/{prefix_length}")
        
        conn = self.connect_device(device_name)
        if not conn:
            return False
        
        try:
            # Create configuration XML
            config_xml = self.create_ip_change_xml(interface_name, new_ip, prefix_length)
            
            # Apply configuration to running datastore
            conn.edit_config(target='running', config=config_xml)
            
            print(f"✅ Successfully changed {device_name}:{interface_name} to {new_ip}/{prefix_length}")
            conn.close_session()
            return True
            
        except Exception as e:
            print(f"❌ Failed to change {device_name}:{interface_name}: {e}")
            if conn:
                conn.close_session()
            return False
    
    def change_all_backhaul_ips(self, base_network="10.1.0.0"):
        """Change IP addresses on all backhaul interfaces"""
        print("🚀 Starting Backhaul IP Address Change")
        print("=" * 50)
        
        # Define new IP addresses for each interface
        # Using /30 subnets for point-to-point links
        ip_assignments = {
            ('RAN', 'backhaul0'): '10.1.1.1',      # RAN backhaul
            ('Router', 'eth1'): '10.1.1.2',        # Router side of RAN link
            ('Router', 'eth2'): '10.1.2.1',        # Router side of Core link  
            ('Core', 'eth1'): '10.1.2.2'           # Core side of Router link
        }
        
        success_count = 0
        total_changes = len(ip_assignments)
        
        for (device, interface), new_ip in ip_assignments.items():
            if self.change_interface_ip(device, interface, new_ip, 30):
                success_count += 1
        
        print()
        print("📊 Summary:")
        print(f"   ✅ Successfully changed: {success_count}/{total_changes} interfaces")
        
        if success_count == total_changes:
            print("🎉 All backhaul interfaces updated successfully!")
            print()
            print("📋 New IP Configuration:")
            print("   RAN backhaul0:  10.1.1.1/30  ↔  Router eth1: 10.1.1.2/30")
            print("   Router eth2:    10.1.2.1/30  ↔  Core eth1:   10.1.2.2/30")
        else:
            print(f"⚠️  {total_changes - success_count} interface(s) failed to update")
        
        return success_count == total_changes
    
    def change_custom_ip(self, device_name, interface_name, new_ip, prefix_length=30):
        """Change IP address on a specific interface (interactive)"""
        if device_name not in self.devices:
            print(f"❌ Unknown device: {device_name}")
            print(f"Available devices: {', '.join(self.devices.keys())}")
            return False
        
        return self.change_interface_ip(device_name, interface_name, new_ip, prefix_length)
    
    def show_current_config(self):
        """Show current interface configuration"""
        print("📋 Current Backhaul Interface Configuration")
        print("=" * 50)
        
        for device_name in self.devices:
            print(f"\n📱 {device_name}:")
            conn = self.connect_device(device_name)
            if not conn:
                print("   ❌ Connection failed")
                continue
            
            try:
                # Get running configuration
                config = conn.get_config(source='running')
                
                # Simple parsing to show interfaces
                interfaces_to_check = self.interfaces[device_name]
                for interface in interfaces_to_check:
                    if f'<name>{interface}</name>' in config.data_xml:
                        print(f"   ✅ {interface}: configured")
                    else:
                        print(f"   ❌ {interface}: not found")
                
                conn.close_session()
                
            except Exception as e:
                print(f"   ❌ Error getting config: {e}")
                if conn:
                    conn.close_session()

def main():
    changer = BackhaulIPChanger()
    
    if len(sys.argv) == 1:
        # No arguments - show usage
        print("🔧 Backhaul IP Address Changer")
        print("=" * 40)
        print("Usage:")
        print("  python3 backhaul_changer.py auto                    - Change all backhaul IPs automatically")
        print("  python3 backhaul_changer.py show                    - Show current configuration")
        print("  python3 backhaul_changer.py change <device> <interface> <ip> [prefix]")
        print()
        print("Examples:")
        print("  python3 backhaul_changer.py auto")
        print("  python3 backhaul_changer.py show")
        print("  python3 backhaul_changer.py change RAN backhaul0 10.2.1.1 30")
        print("  python3 backhaul_changer.py change Router eth1 10.2.1.2")
        
    elif sys.argv[1] == 'auto':
        changer.change_all_backhaul_ips()
        
    elif sys.argv[1] == 'show':
        changer.show_current_config()
        
    elif sys.argv[1] == 'change':
        if len(sys.argv) < 5:
            print("Usage: python3 backhaul_changer.py change <device> <interface> <ip> [prefix]")
            sys.exit(1)
        
        device = sys.argv[2]
        interface = sys.argv[3] 
        ip = sys.argv[4]
        prefix = int(sys.argv[5]) if len(sys.argv) > 5 else 30
        
        changer.change_custom_ip(device, interface, ip, prefix)
        
    else:
        print(f"Unknown command: {sys.argv[1]}")
        print("Use 'auto', 'show', or 'change'")

if __name__ == "__main__":
    main()