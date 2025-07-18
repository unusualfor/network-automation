#!/usr/bin/env python3
"""
Reset all lab devices to clean state
"""

from ncclient import manager
import sys

def reset_device(host, port, device_name):
    """Reset a device to clean state"""
    
    # Configuration to remove all interfaces
    cleanup_config = '''
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces" 
                  xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" 
                  xc:operation="delete"/>
    </config>
    '''
    
    try:
        with manager.connect(
            host=host,
            port=port,
            username='admin',
            password='admin',
            hostkey_verify=False
        ) as m:
            print(f"Resetting {device_name}...")
            
            # Remove all interfaces
            result = m.edit_config(target='running', config=cleanup_config)
            print(f"✅ {device_name} reset successfully")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to reset {device_name}: {e}")
        return False

def main():
    devices = [
        ('localhost', 830, 'RAN'),
        ('localhost', 831, 'Router'), 
        ('localhost', 832, 'Core')
    ]
    
    print("🧹 Resetting all lab devices...")
    print("=" * 40)
    
    success_count = 0
    for host, port, name in devices:
        if reset_device(host, port, name):
            success_count += 1
    
    print("=" * 40)
    print(f"✅ {success_count}/{len(devices)} devices reset successfully")
    
    if success_count == len(devices):
        print("🎉 All devices are now clean!")
    
    print("\nTo restore original configurations:")
    print("docker-compose restart")

if __name__ == '__main__':
    main()