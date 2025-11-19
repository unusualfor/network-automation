# Quick Start Guide

Get up and running with the Ansible version in 5 minutes!

## Prerequisites

```bash
# Install Ansible and NETCONF collection
pip install ansible ansible-netcommon
ansible-galaxy collection install ansible.netcommon

# Verify installation
ansible --version
ansible-galaxy collection list | grep netcommon
```

## Basic Usage

### 1. Show Current Configuration (Simplest Test)

```bash
ansible-playbook -i inventory.yml backhaul_changer.yml --tags=show
```

**Expected Output:**
```
TASK [Display configuration status for RAN]
ok: [RAN] => 
  msg: |-
    📱 RAN:
       ✅ Configuration retrieved successfully
       Interfaces: backhaul0
```

---

### 2. Change All Backhaul IPs (Auto Mode)

```bash
ansible-playbook -i inventory.yml backhaul_changer.yml --tags=auto
```

**Expected Output:**
```
TASK [Display result for RAN]
ok: [RAN] => 
  msg: |-
    ✅ Successfully configured RAN:
       - backhaul0: 10.0.1.1/30

TASK [Display final network topology]
ok: [localhost] =>
  msg: |-
    🎉 All backhaul interfaces updated successfully!
    
    📋 New IP Configuration:
       RAN backhaul0:  10.0.1.1/30  ↔  Router eth1: 10.0.1.2/30
       Router eth2:    10.0.2.1/30  ↔  Core eth1:   10.0.2.2/30
```

---

### 3. Change Specific Interface

```bash
ansible-playbook -i inventory.yml backhaul_changer.yml --tags=change \
  -e "target_device=RAN target_interface=backhaul0 target_ip=10.2.1.1 target_prefix=30"
```

**Expected Output:**
```
TASK [Display custom configuration result]
ok: [RAN] => 
  msg: ✅ Successfully changed RAN:backhaul0 to 10.2.1.1/30
```

---

## Quick Comparison

### Python Version:
```bash
# Show configuration
python3 backhaul_changer.py show

# Auto configure
python3 backhaul_changer.py auto

# Custom change
python3 backhaul_changer.py change RAN backhaul0 10.2.1.1 30
```

### Ansible Version:
```bash
# Show configuration  
ansible-playbook -i inventory.yml backhaul_changer.yml --tags=show

# Auto configure
ansible-playbook -i inventory.yml backhaul_changer.yml --tags=auto

# Custom change
ansible-playbook -i inventory.yml backhaul_changer.yml --tags=change \
  -e "target_device=RAN target_interface=backhaul0 target_ip=10.2.1.1 target_prefix=30"
```

---

## Useful Options

### Dry Run (Test Without Applying)
```bash
ansible-playbook -i inventory.yml backhaul_changer.yml --tags=auto --check
```

### Verbose Output (Debugging)
```bash
ansible-playbook -i inventory.yml backhaul_changer.yml --tags=show -vvv
```

### Target Specific Devices
```bash
ansible-playbook -i inventory.yml backhaul_changer.yml --tags=auto --limit=RAN,Router
```

### List All Tags
```bash
ansible-playbook backhaul_changer.yml --list-tags
```

---

## File Structure

After setup, you should have:
```
.
├── ansible.cfg              # Ansible configuration
├── inventory.yml            # Device definitions
├── backhaul_changer.yml     # Main playbook
├── README.md                # Full documentation
├── COMPARISON.md            # Python vs Ansible comparison
├── TROUBLESHOOTING.md       # Common issues and fixes
└── QUICKSTART.md            # This file
```

---

## Customize for Your Environment

### 1. Update Device Connections

Edit `inventory.yml`:
```yaml
RAN:
  ansible_host: 192.168.1.100  # Your device IP
  ansible_port: 830            # Your NETCONF port
  ansible_user: myuser         # Your username
  ansible_password: mypass     # Your password
```

### 2. Change IP Assignments

Edit `backhaul_changer.yml`:
```yaml
vars:
  ip_assignments:
    RAN:
      backhaul0:
        ip: "10.1.1.1"      # Your IP
        prefix: 24          # Your prefix
```

### 3. Add More Devices

Add to `inventory.yml`:
```yaml
    backhaul_devices:
      hosts:
        RAN:
          # ... existing config ...
        
        NewDevice:           # Add new device
          ansible_host: 192.168.1.101
          ansible_port: 830
          ansible_connection: netconf
          ansible_user: admin
          ansible_password: admin
          backhaul_interfaces:
            - eth0
            - eth1
```

Then update `backhaul_changer.yml` ip_assignments:
```yaml
vars:
  ip_assignments:
    # ... existing assignments ...
    
    NewDevice:              # Add new assignments
      eth0:
        ip: "10.0.3.1"
        prefix: 30
```

---

## Common First-Time Issues

### Issue 1: "No hosts matched"
```bash
# Check your inventory
ansible-inventory -i inventory.yml --list

# Verify devices are defined
ansible-inventory -i inventory.yml --graph
```

### Issue 2: Connection refused
```bash
# Test direct connection
nc -zv localhost 830

# Check device is reachable
ping <device_ip>

# Verify NETCONF port is open
nmap -p 830 <device_ip>
```

### Issue 3: Authentication failed
```bash
# Test SSH connection
ssh -p 830 admin@localhost

# Verify credentials in inventory
cat inventory.yml | grep -A 5 "RAN:"
```

---

## Next Steps

1. ✅ **Got it working?** Great! Now read `README.md` for deeper understanding
2. 📚 **Want to understand the differences?** Check out `COMPARISON.md`
3. 🐛 **Having issues?** See `TROUBLESHOOTING.md`
4. 🔧 **Ready to customize?** Edit `inventory.yml` and `backhaul_changer.yml`

---

## One-Liner Test

Test everything is working:
```bash
# This should succeed if your environment is set up correctly
ansible-playbook -i inventory.yml backhaul_changer.yml --tags=show -vv
```

If you see output like `✅ Configuration retrieved successfully`, you're ready to go!

---

## Tips for Learning

### Start Simple:
1. First, just run `--tags=show` to see current config
2. Then try `--tags=auto --check` (dry run)
3. Finally, run `--tags=auto` for real changes

### Explore Gradually:
```bash
# See what Ansible will do
ansible-playbook playbook.yml --tags=auto --check --diff

# See detailed execution
ansible-playbook playbook.yml --tags=auto -vv

# Step through each task
ansible-playbook playbook.yml --tags=auto --step
```

### Understand By Comparing:
Run the Python version and Ansible version side-by-side:
```bash
# Terminal 1
python3 backhaul_changer.py show

# Terminal 2
ansible-playbook -i inventory.yml backhaul_changer.yml --tags=show

# Compare outputs and execution time
```

---

## Getting Unstuck

If you're stuck, try this debug workflow:

1. **Verify inventory:**
   ```bash
   ansible-inventory -i inventory.yml --list
   ```

2. **Test connectivity:**
   ```bash
   ansible -i inventory.yml all -m ping
   ```

3. **Check playbook syntax:**
   ```bash
   ansible-playbook backhaul_changer.yml --syntax-check
   ```

4. **Run with maximum verbosity:**
   ```bash
   ansible-playbook -i inventory.yml backhaul_changer.yml --tags=show -vvvv
   ```

5. **Check the TROUBLESHOOTING.md** for your specific error message

---

## Success Checklist

- [ ] Ansible and netcommon collection installed
- [ ] Inventory file configured with your devices
- [ ] Can run `--tags=show` successfully
- [ ] Can run `--tags=auto --check` (dry run)
- [ ] Can run `--tags=auto` to apply changes
- [ ] Understand how to customize IP assignments
- [ ] Know where to find help (TROUBLESHOOTING.md)

**Ready to dive deeper?** Check out the full `README.md` for comprehensive documentation!
