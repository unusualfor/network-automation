# Side-by-Side Code Comparison

## 1. Device Connection

### Python
```python
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
```

### Ansible
```yaml
# Connection is handled automatically via inventory
RAN:
  ansible_host: localhost
  ansible_port: 830
  ansible_connection: netconf
  ansible_user: admin
  ansible_password: admin
  ansible_network_os: default
```

**Key Difference**: Ansible abstracts connection management entirely. You declare connection parameters once in inventory, and Ansible handles opening/closing connections automatically.

---

## 2. XML Configuration Generation

### Python
```python
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
```

### Ansible
```yaml
- name: Change IP address
  ansible.netcommon.netconf_config:
    target: running
    content: |
      <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
          <interface>
            <name>{{ interface_name }}</name>
            <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"
                  xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"
                  nc:operation="replace">
              <enabled>true</enabled>
              <address>
                <ip>{{ ip_address }}</ip>
                <prefix-length>{{ prefix_length }}</prefix-length>
              </address>
            </ipv4>
          </interface>
        </interfaces>
      </config>
```

**Key Difference**: Both use template syntax (Python f-strings vs Jinja2), but Ansible integrates the XML directly into the task definition.

---

## 3. Applying Configuration

### Python
```python
def change_interface_ip(self, device_name, interface_name, new_ip, prefix_length=30):
    """Change IP address on a specific interface"""
    print(f"🔧 Changing {device_name}:{interface_name} to {new_ip}/{prefix_length}")
    
    conn = self.connect_device(device_name)
    if not conn:
        return False
    
    try:
        config_xml = self.create_ip_change_xml(interface_name, new_ip, prefix_length)
        conn.edit_config(target='running', config=config_xml)
        print(f"✅ Successfully changed {device_name}:{interface_name}")
        conn.close_session()
        return True
    except Exception as e:
        print(f"❌ Failed to change {device_name}:{interface_name}: {e}")
        if conn:
            conn.close_session()
        return False
```

### Ansible
```yaml
- name: "Change IP on {{ inventory_hostname }}:{{ target_interface }}"
  ansible.netcommon.netconf_config:
    target: running
    content: |
      {{ xml_configuration_here }}
  register: custom_config_result

- name: Display result
  debug:
    msg: "✅ Successfully changed {{ inventory_hostname }}:{{ target_interface }}"
  when: custom_config_result is succeeded
```

**Key Difference**: 
- **Python**: Explicit error handling with try/except, manual connection cleanup
- **Ansible**: Automatic error handling, connection management, and result registration

---

## 4. Bulk Operations

### Python
```python
def change_all_backhaul_ips(self, base_network="10.1.0.0"):
    """Change IP addresses on all backhaul interfaces"""
    ip_assignments = {
        ('RAN', 'backhaul0'): '10.0.1.1',
        ('Router', 'eth1'): '10.0.1.2',
        ('Router', 'eth2'): '10.0.2.1',
        ('Core', 'eth1'): '10.0.2.2'
    }
    
    success_count = 0
    total_changes = len(ip_assignments)
    
    for (device, interface), new_ip in ip_assignments.items():
        if self.change_interface_ip(device, interface, new_ip, 30):
            success_count += 1
    
    return success_count == total_changes
```

### Ansible
```yaml
vars:
  ip_assignments:
    RAN:
      backhaul0: {ip: "10.0.1.1", prefix: 30}
    Router:
      eth1: {ip: "10.0.1.2", prefix: 30}
      eth2: {ip: "10.0.2.1", prefix: 30}
    Core:
      eth1: {ip: "10.0.2.2", prefix: 30}

tasks:
  - name: Change IP addresses on {{ inventory_hostname }}
    ansible.netcommon.netconf_config:
      content: |
        {% for interface in backhaul_interfaces %}
          {{ generate_xml_for_interface }}
        {% endfor %}
```

**Key Difference**:
- **Python**: Sequential processing with explicit loop and counter
- **Ansible**: Parallel execution across all hosts by default, automatic success tracking

---

## 5. Command-Line Interface

### Python
```python
def main():
    changer = BackhaulIPChanger()
    
    if sys.argv[1] == 'auto':
        changer.change_all_backhaul_ips()
    elif sys.argv[1] == 'show':
        changer.show_current_config()
    elif sys.argv[1] == 'change':
        device = sys.argv[2]
        interface = sys.argv[3]
        ip = sys.argv[4]
        prefix = int(sys.argv[5]) if len(sys.argv) > 5 else 30
        changer.change_custom_ip(device, interface, ip, prefix)
```

### Ansible
```bash
# Uses tags for command selection
ansible-playbook backhaul_changer.yml --tags=auto
ansible-playbook backhaul_changer.yml --tags=show
ansible-playbook backhaul_changer.yml --tags=change \
  -e "target_device=RAN target_interface=backhaul0 target_ip=10.2.1.1"
```

**Key Difference**:
- **Python**: Custom argument parsing in code
- **Ansible**: Built-in CLI with tags and extra variables (`-e`)

---

## 6. Error Handling Philosophy

### Python - Explicit
```python
try:
    conn.edit_config(target='running', config=config_xml)
    print(f"✅ Success")
    return True
except Exception as e:
    print(f"❌ Failed: {e}")
    return False
finally:
    if conn:
        conn.close_session()
```

### Ansible - Declarative
```yaml
- name: Apply configuration
  netconf_config:
    content: "{{ xml }}"
  register: result
  ignore_errors: true

- name: Handle failure
  debug:
    msg: "❌ Failed: {{ result.msg }}"
  when: result.failed
```

**Key Difference**:
- **Python**: You must handle every error explicitly
- **Ansible**: Failed tasks are handled automatically; you opt-in to custom handling

---

## 7. State Management

### Python
```python
# State exists only in memory during execution
success_count = 0
for device, interface in assignments:
    if change_ip(...):
        success_count += 1
# State lost after script ends
```

### Ansible
```yaml
# Ansible can track state with facts and register
- name: Do something
  module_name:
  register: result

# Result persists throughout playbook
# Can be saved to files or external systems
- name: Save state
  copy:
    content: "{{ result | to_nice_json }}"
    dest: /tmp/state.json
```

**Key Difference**: Ansible has built-in mechanisms for state persistence and sharing across tasks/plays.

---

## 8. Scalability Comparison

### Python
```python
# Sequential execution
for device_name in ['RAN', 'Router', 'Core']:
    connect_and_configure(device_name)
# Takes: 3 × connection_time
```

### Ansible
```yaml
# Parallel execution (controlled by forks)
hosts: all  # Processes multiple devices simultaneously
# Takes: max(connection_time) with default forks=5
```

To make Python parallel, you'd need:
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(change_ip, device) 
               for device in devices]
```

**Key Difference**: Ansible is parallel by default; Python requires explicit threading/multiprocessing.

---

## Summary Table

| Aspect | Python | Ansible |
|--------|--------|---------|
| **Connection Management** | Manual (open/close) | Automatic |
| **Error Handling** | Explicit try/except | Automatic + opt-in |
| **Execution Model** | Sequential | Parallel by default |
| **State Management** | In-memory only | Persistent via register |
| **Configuration Storage** | Hardcoded in Python | External YAML files |
| **Scalability** | Requires threading code | Built-in |
| **Learning Curve** | Python syntax | YAML + Jinja2 + Ansible concepts |
| **Debugging** | Standard Python debugger | `-vvv`, `debug` module |
| **Testing** | Write unit tests | `--check` mode, `assert` module |
| **Reusability** | Object-oriented classes | Roles, collections |

## When to Use Which?

### Use Python when:
- You need complex logic and algorithms
- You want full control over execution flow
- You're building a larger application
- You need custom error handling and retries
- You want to integrate with Python-specific libraries

### Use Ansible when:
- You're managing multiple devices at scale
- You want declarative configuration management
- You need idempotency guarantees
- You're working with infrastructure teams
- You want built-in logging and audit trails
- You need to coordinate changes across heterogeneous systems
