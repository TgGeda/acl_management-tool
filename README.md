#  ACL Management Tool

## Overview

The ACL Management Tool is a Python-based application designed to simplify the management of Access Control Lists (ACLs) on network devices. It allows network administrators to define, validate, and apply ACL rules efficiently while ensuring security and compliance through user authentication and role-based access control.

## Features

- **User Authentication**: Supports user authentication with role-based access control (RBAC) to restrict actions based on user roles (admin and user).
- **ACL Rule Validation**: Validates ACL rules for syntax, logical consistency, and conflicts before applying changes.
- **Backup Configuration**: Automatically backs up the current ACL configuration before applying new rules, ensuring a rollback option in case of errors.
- **Dry Run Mode**: Simulates the application of ACL rules without making changes, allowing users to verify commands before execution.
- **Multi-Device Support**: Configures ACLs on multiple devices simultaneously, streamlining network management tasks.
- **Detailed Logging**: Logs all actions, including user authentication, ACL changes, and errors, for auditing and troubleshooting purposes.
- **JSON Data Handling**: Loads device information and ACL rules from JSON files, making it easy to manage configurations.

## Prerequisites

- Python 3.x
- Required Python packages:
  - `netmiko`
  - `ipaddress`
  

You can install the required packages using pip:

```bash
pip install netmiko
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/TgGeda/acl-management-tool.git
   cd acl-management-tool
   ```

2. Ensure you have the necessary permissions to access the devices you plan to manage.

3. Prepare your JSON files:
   - **devices.json**: Contains device connection details.
   - **acl_rules.json**: Contains the ACL rules you wish to apply.

   Example `devices.json`:
   ```json
   [
       {
           "device_type": "cisco_ios",
           "host": "192.168.1.1",
           "username": "admin",
           "password": "password",
           "secret": "secret_password"
       }
   ]
   ```

   Example `acl_rules.json`:
   ```json
   [
       {
           "acl_number": "100",
           "action": "permit",
           "protocol": "tcp",
           "source": "192.168.1.0/24",
           "destination": "192.168.2.0/24",
           "port": "80"
       }
   ]
   ```

## Usage

1. **Run the Tool**:
   Execute the script to start the ACL management process.

   ```bash
   python acl_management_tool.py
   ```

2. **User Authentication**:
   Enter your username and password when prompted. Ensure your account has the appropriate permissions based on your role.

3. **Configuration**:
   - The tool will load device and ACL rule configurations from the specified JSON files.
   - You can run the tool in dry run mode to simulate changes without applying them.

   To apply changes, set the `dry_run` parameter to `False` in the `configure_acls_on_multiple_devices` function call within the script.

## Logging

All actions and errors are logged in the `acl_changes.log` file. This log file provides a record of user actions, configuration changes, and any issues encountered during execution.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please fork the repository and submit a pull request.

### Guidelines for Contributions

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Write clear and concise commit messages.
4. Ensure your code adheres to the existing style.
5. Submit a pull request for review.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact

For questions or support, please contact Birhan Abuhay Jemere at burahabtam@gmail.com.

