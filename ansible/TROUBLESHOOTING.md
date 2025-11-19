# Troubleshooting Guide

## Common Issues and Solutions

### 1. Connection Refused Error

**Error:**
```
fatal: [RAN]: FAILED! => {"msg": "Connection refused"}
```

**Causes:**
- NETCONF service not running on target device
- Incorrect port number in inventory
- Firewall blocking connections

**Solutions:**
```bash
# Check if device is reachable
nc -zv localhost 830

# Verify NETCONF is running on device
ssh admin@device "systemctl status netconf"

# Check inventory ports match device configuration
ansible-inventory -i inventory.yml --list
```

---

### 2. Authentication Failed

**Error:**
```
fatal: [Router]: FAILED! => {"msg": "Authentication failed"}
```

**Causes:**
- Wrong username/password in inventory
- Account locked or expired
- SSH key issues

**Solutions:**
```bash
# Test manual connection
ssh -p 830 -s admin@localhost netconf

# Use vault for sensitive credentials
ansible-vault encrypt_string 'admin' --name 'ansible_password'

# Verify credentials in inventory
ansible-inventory -i inventory.yml --host Router
```

---

### 3. XML Configuration Errors

**Error:**
```
failed: [Core] => {"msg": "XML parse error"}
```

**Causes:**
- Malformed XML in playbook
- Incorrect YANG model namespace
- Missing required XML elements

**Solutions:**

**⚠️ NOTE: Known Issue in Original Python Script**
The Python script uses `<n>` instead of `<name>` for the interface name tag. The correct YANG model uses `<name>`. If you encounter errors related to interface names, try changing:

```yaml
# Incorrect (matches Python script):
<n>{{ interface_name }}</n>

# Correct (proper YANG model):
<name>{{ interface_name }}</name>
```

To validate XML:
```bash
# Extract and validate XML
ansible-playbook network_automation.yml --tags=auto --check -vvv | \
  grep -A 20 "<config" > test.xml

# Validate against YANG model
pyang --validate test.xml
```

---

### 4. Module Not Found

**Error:**
```
ERROR! couldn't resolve module/action 'ansible.netcommon.netconf_config'
```

**Cause:**
- Missing ansible.netcommon collection

**Solution:**
```bash
# Install required collection
ansible-galaxy collection install ansible.netcommon

# Verify installation
ansible-galaxy collection list | grep netcommon

# Install specific version if needed
ansible-galaxy collection install ansible.netcommon:==2.6.1
```

---

### 5. Timeout Errors

**Error:**
```
fatal: [RAN]: FAILED! => {"msg": "Timeout waiting for response"}
```

**Causes:**
- Device too slow to respond
- Network latency
- Large configuration changes

**Solutions:**

Edit `ansible.cfg`:
```ini
[defaults]
timeout = 30

[netconf_connection]
persistent_command_timeout = 60
```

Or use playbook-level timeout:
```yaml
- name: Change IP (with extended timeout)
  ansible.netcommon.netconf_config:
    content: "{{ xml }}"
  vars:
    ansible_command_timeout: 60
```

---

### 6. Jinja2 Template Errors

**Error:**
```
fatal: [Router]: FAILED! => {"msg": "template error while templating string"}
```

**Common Jinja2 Issues:**

**Issue 1: Undefined variable**
```yaml
# Wrong - variable might not exist
<ip>{{ ip_assignments[interface] }}</ip>

# Right - with default value
<ip>{{ ip_assignments.get(interface, '0.0.0.0') }}</ip>

# Right - with conditional check
{% if interface in ip_assignments %}
  <ip>{{ ip_assignments[interface] }}</ip>
{% endif %}
```

**Issue 2: Dictionary access in templates**
```yaml
# Wrong - causes template error if key missing
{{ ip_assignments[inventory_hostname][interface_name].ip }}

# Right - safe navigation
{{ ip_assignments.get(inventory_hostname, {}).get(interface_name, {}).get('ip', '0.0.0.0') }}
```

**Debug Jinja2 issues:**
```yaml
- name: Debug template variables
  debug:
    msg: |
      inventory_hostname: {{ inventory_hostname }}
      backhaul_interfaces: {{ backhaul_interfaces }}
      ip_assignments: {{ ip_assignments | to_nice_json }}
```

---

### 7. "Skipping: no hosts matched" Error

**Error:**
```
PLAY [Backhaul IP Address Management] ****
skipping: no hosts matched
```

**Causes:**
- Wrong inventory file
- Host pattern doesn't match
- Limit excludes all hosts

**Solutions:**
```bash
# Verify inventory is loaded
ansible-inventory -i inventory.yml --list

# Check which hosts match your pattern
ansible-inventory -i inventory.yml --list | jq '.all.children'

# Test with all hosts
ansible-playbook -i inventory.yml network_automation.yml --tags=show

# Test specific host
ansible-playbook -i inventory.yml network_automation.yml --tags=show --limit=RAN
```

---

### 8. Tags Not Working

**Issue:**
Tasks run when they shouldn't (or don't run when they should)

**Understanding Tag Behavior:**

```yaml
# The 'never' tag prevents execution unless explicitly called
tags: [auto, never]  # Won't run unless --tags=auto

tags: [show]         # Will run with --tags=show OR --tags=all

tags: [always]       # Runs regardless of --tags (use carefully!)
```

**Common Tag Patterns:**
```bash
# Run only 'auto' tasks
ansible-playbook network_automation.yml --tags=auto

# Run everything EXCEPT 'show'
ansible-playbook network_automation.yml --skip-tags=show

# Run multiple tags
ansible-playbook network_automation.yml --tags=auto,show

# List all available tags
ansible-playbook network_automation.yml --list-tags
```

---

### 9. Parallel Execution Issues

**Issue:**
Configurations applied in wrong order or race conditions

**Solutions:**

**Control parallelism:**
```yaml
- name: Sequential configuration
  hosts: backhaul_devices
  serial: 1  # Process one host at a time
  tasks:
    - name: Configure interface
      netconf_config:
        content: "{{ xml }}"
```

**Or in ansible.cfg:**
```ini
[defaults]
forks = 1  # Only process one host at a time
```

**Order matters:**
```yaml
- name: Configure in specific order
  hosts: backhaul_devices
  order: sorted  # Options: sorted, reverse_sorted, inventory
  tasks:
    - name: Configure
      netconf_config:
        content: "{{ xml }}"
```

---

### 10. Check Mode (Dry Run) Issues

**Issue:**
`--check` mode fails even though normal mode works

**Cause:**
Some modules don't support check mode

**Solution:**
```yaml
# Make task work in check mode
- name: Configure interface
  netconf_config:
    content: "{{ xml }}"
  check_mode: false  # Always run, even in check mode

# Or skip in check mode
- name: Configure interface
  netconf_config:
    content: "{{ xml }}"
  when: not ansible_check_mode
```

---

## Debugging Tips

### 1. Increase Verbosity
```bash
# Basic verbosity
ansible-playbook playbook.yml -v

# Show task inputs/outputs
ansible-playbook playbook.yml -vv

# Show connection debugging
ansible-playbook playbook.yml -vvv

# Show everything (including SSH/NETCONF)
ansible-playbook playbook.yml -vvvv
```

### 2. Debug Variables
```yaml
- name: Debug all variables
  debug:
    var: hostvars[inventory_hostname]

- name: Debug specific variable
  debug:
    msg: "IP: {{ ip_assignments[inventory_hostname] }}"
```

### 3. Step Through Playbook
```bash
# Prompt before each task
ansible-playbook playbook.yml --step

# Start at specific task
ansible-playbook playbook.yml --start-at-task="Change IP addresses"
```

### 4. Syntax Check
```bash
# Validate playbook syntax
ansible-playbook network_automation.yml --syntax-check

# Validate inventory
ansible-inventory -i inventory.yml --list

# Check for common issues
ansible-lint network_automation.yml
```

### 5. Capture Full Output
```bash
# Save to file
ansible-playbook network_automation.yml -vvv > debug.log 2>&1

# With timestamp
ansible-playbook network_automation.yml -vvv 2>&1 | ts '[%Y-%m-%d %H:%M:%S]' > debug.log
```

---

## Performance Optimization

### 1. Speed Up Execution
```ini
# ansible.cfg
[defaults]
gathering = explicit  # Don't gather facts unless needed
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 3600

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

### 2. Optimize NETCONF Connections
```yaml
vars:
  ansible_persistent_log_messages: false  # Reduce logging overhead
  ansible_persistent_command_timeout: 10  # Shorter timeout for fast devices
```

---

## Comparison with Python Script Behavior

### Python Script Issues Also Present in Ansible:

1. **The `<n>` vs `<name>` typo** - Both implementations have this if you copy directly
2. **No configuration rollback** - Failed changes aren't automatically reverted
3. **No validation** - IP addresses aren't validated before application
4. **No conflict detection** - Duplicate IPs aren't detected

### Ansible-Specific Improvements:

1. **Better error reporting** - More detailed error messages
2. **Idempotency** - Can run multiple times safely
3. **Parallel execution** - Faster for multiple devices
4. **Check mode** - Test without applying changes
5. **Ansible vault** - Encrypted credential storage

---

## Getting Help

1. **Ansible Documentation:**
   ```bash
   ansible-doc ansible.netcommon.netconf_config
   ansible-doc ansible.netcommon.netconf_get
   ```

2. **Module Examples:**
   ```bash
   ansible-doc -t module ansible.netcommon.netconf_config -s
   ```

3. **Community:**
   - Ansible Community Forum: forum.ansible.com
   - Stack Overflow: [ansible] tag
   - IRC: #ansible on libera.chat

4. **Validate NETCONF:**
   ```bash
   # Manual NETCONF test
   ssh -p 830 -s admin@localhost netconf <<EOF
   <?xml version="1.0" encoding="UTF-8"?>
   <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
     <capabilities>
       <capability>urn:ietf:params:netconf:base:1.0</capability>
     </capabilities>
   </hello>
   ]]>]]>
   EOF
   ```
