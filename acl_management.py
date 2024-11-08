import json
import logging
import netmiko
from netmiko import ConnectHandler
import ipaddress
import os
import shutil
import getpass
from typing import List, Dict

# Configure logging
logging.basicConfig(filename='acl_changes.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# User roles
USER_ROLES = {
    'admin': 'read-write',
    'user': 'read-only'
}

# Global variables for user authentication
current_user = None
current_role = None

def authenticate_user() -> None:
    """Prompt for username and password to authenticate."""
    global current_user, current_role
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    
    # Simple authentication simulation
    if username in USER_ROLES:
        current_user = username
        current_role = USER_ROLES[username]
        logging.info(f"User {username} authenticated successfully.")
    else:
        logging.error("Authentication failed.")
        exit()

def load_json_data(file_path: str) -> List[Dict]:
    """Load data from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        exit()
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON in file: {file_path}")
        exit()

def build_acl_command(rule: Dict) -> str:
    """Build ACL command based on the rule dictionary."""
    command = f"access-list {rule['acl_number']} {rule['action']} {rule['protocol']} "
    
    if 'port' in rule:
        command += f"host {rule['source']} host {rule['destination']} eq {rule['port']}"
    else:
        command += f"{rule['source']} {rule['destination']}"
    
    return command

def check_overlap(source1: str, dest1: str, source2: str, dest2: str) -> bool:
    """Check if two IP address ranges overlap."""
    try:
        net1 = ipaddress.ip_network(source1, strict=False) if '/' in source1 else ipaddress.ip_address(source1)
        net2 = ipaddress.ip_network(source2, strict=False) if '/' in source2 else ipaddress.ip_address(source2)
        
        return net1.overlaps(net2)
    except ValueError as e:
        logging.error(f"IP address error: {e}")
        return False

def validate_acl_rules(rules: List[Dict]) -> bool:
    """Validate ACL rules for syntax, logical consistency, and conflicts."""
    valid = True
    seen_acls = set()
    permit_rules = []
    deny_rules = []

    for rule in rules:
        if 'acl_number' not in rule or 'action' not in rule or 'protocol' not in rule:
            logging.error(f"Missing required fields in rule: {rule}")
            valid = False
            continue
        
        if current_role == 'read-only' and rule['action'] == 'deny':
            logging.error("User does not have permission to modify deny rules.")
            valid = False
            continue
        
        if rule['acl_number'] in seen_acls:
            logging.error(f"Duplicate ACL number found: {rule['acl_number']}")
            valid = False
        else:
            seen_acls.add(rule['acl_number'])
        
        if rule['action'] == 'permit':
            permit_rules.append(rule)
        elif rule['action'] == 'deny':
            deny_rules.append(rule)

    # Check for conflicts between permit and deny rules
    for permit in permit_rules:
        for deny in deny_rules:
            if (permit['protocol'] == deny['protocol'] and
                check_overlap(permit['source'], permit['destination'], deny['source'], deny['destination'])):
                logging.error(f"Conflict detected: Permit rule {permit} conflicts with Deny rule {deny}")
                valid = False

    # Check for overlaps between all rules
    for i in range(len(rules)):
        for j in range(i + 1, len(rules)):
            if (rules[i]['protocol'] == rules[j]['protocol'] and
                check_overlap(rules[i]['source'], rules[i]['destination'], rules[j]['source'], rules[j]['destination'])):
                logging.error(f"Overlapping ranges detected between rules: {rules[i]} and {rules[j]}")
                valid = False

    return valid

def backup_current_config(device: Dict) -> None:
    """Backup the current ACL configuration."""
    try:
        connection = ConnectHandler(**device)
        connection.enable()

        # Fetch current ACL configuration
        current_config = connection.send_command("show running-config | include access-list")
        backup_file_name = f"backup_{device['host']}_acl.txt"
        
        with open(backup_file_name, 'w') as backup_file:
            backup_file.write(current_config)
        
        logging.info(f"Current ACL configuration backed up successfully for {device['host']}.")
        connection.disconnect()
    except Exception as e:
        logging.error(f"An error occurred while backing up config for {device['host']}: {e}")

def dry_run_commands(commands: List[str]) -> None:
    """Simulate command execution without applying changes."""
    for command in commands:
        print(f"Dry Run: {command}")

def configure_acls(device: Dict, rules: List[Dict], dry_run: bool = False) -> None:
    """Configure ACLs on a single device."""
    if not validate_acl_rules(rules):
        logging.error("Validation failed. Aborting configuration.")
        return

    if dry_run:
        commands = [build_acl_command(rule) for rule in rules]
        dry_run_commands(commands)
        return

    backup_current_config(device)

    try:
        connection = ConnectHandler(**device)
        connection.enable()

        commands = [build_acl_command(rule) for rule in rules]
        output = connection.send_config_set(commands)

        logging.info(f"ACL changes applied successfully for {device['host']}.")
        logging.info(output)

        connection.disconnect()
    except Exception as e:
        logging.error(f"An error occurred while configuring ACLs for {device['host']}: {e}")

def configure_acls_on_multiple_devices(devices: List[Dict], rules: List[Dict], dry_run: bool = False) -> None:
    """Configure ACLs on multiple devices."""
    for device in devices:
        logging.info(f"Configuring ACLs on {device['host']}")
        configure_acls(device, rules, dry_run)

if __name__ == "__main__":
    authenticate_user()  # Authenticate user

    # Load device information and ACL rules from JSON files
    devices = load_json_data('devices.json')
    acl_rules = load_json_data('acl_rules.json')

    # Run the configuration with dry run option
    configure_acls_on_multiple_devices(devices, acl_rules, dry_run=True)  # Set dry_run=False to apply changes