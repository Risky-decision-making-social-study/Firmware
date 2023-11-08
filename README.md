# Firmware

This repository contains the firmware files and documentation for the “How does social context modulate risky decision-making in long-tailed macaques (Macaca fascicularis)? A research report on problematic issues with a repeated sampling from experience paradigm” project. The project aims to provide a comprehensive guide for building a CNC machine using 3D printed parts.

## Usage

Files starting with "client" containing the code for the experiments and connect to the apparatuses with TCP to control them remotely. Run each session type corresponding file to conduct a session, also edit the sections indicated by "Session settings #changeme" to set the session and recording parameters corectly according to the subject and session details.

## Installation

### Client

To install a client, follow these steps:

Clone the repository to your local machine.
Install Python 3.6 or later.

### Server

To install a server or apparatus, follow these steps:

#### Raspberry OS

1. Use the Raspberry Pi imager (https://www.raspberrypi.com/software/) to flash `Raspberry Pi OS` to an SD card.
2. Visit the OS customization settings and set up SSH, hostname, or Wi-Fi if needed.

#### Software Install

1. Log in to the Raspberry Pi.
2. Clone this repository.
3. Install the necessary Python packages by running the following commands:

```bash
pip install RPi.GPIO
pip install numpy
pip install smbus
```

4. Update the server settings by modifying the `config_left.cfg` and `config_right.cfg` files as needed.
5. Test the setup by running `./start_server_left.sh` or `./start_server_right.sh`.
6. Setup autostart for `./start_server_left.sh` or `./start_server_right.sh` at boot.

#### Update server settings

It’s important to update and calibrate some hardware components settings, especially the `as5048b_zeroreg` and `*_range settings` in the `config_left.cfg` and `config_right.cfg` files. This is because the rotation range of the servo motors and the zero position of the carousel will be different for each component and apparatus.

To update these settings, open the appropriate configuration file and modify the relevant settings as needed. Make sure to save the changes before closing the file.

#### Retrieving the IP Address

To retrieve the IP address, open a terminal and run the following command:

```bash
$ ip addr
```

This will display information about your network interfaces. Look for the interface that you are using to connect to the network (e.g., eth0, wlan0, etc.). The IP address will be listed next to inet.

For example:

```bash
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff
    inet 192.168.0.2/20 brd 172.17.15.255 scope global dynamic noprefixroute eth0
       valid_lft 690295sec preferred_lft 603895sec
    inet6 fe80::f56d:e6db:b655:2d6a/64 scope link
       valid_lft forever preferred_lft forever
```

In this example, the IP address is `192.168.0.2`.

#### Updating Client Configuration

To update the client configuration, open the appropriate client python file and modify the HOST_LEFT and HOST_RIGHT settings as needed. Replace the IP addresses with the IP addresses of the servers/apparatuses you want to connect to.

For example:

```python
HOST_LEFT = '192.168.0.2'  # The server's hostname or IP address
HOST_RIGHT = '192.168.0.3'  # The server's hostname or IP address
```

#### Testing the Setup

To test the setup, make sure that everything is powered, connected, and configured correctly. Then, run any of the client scripts on your controller/client computer. The apparatuses should start to respond and run the selected session.

## Concept and Implementation

To learn more about the individual parts and modules of the project, read the concept and implementation descriptions in the [concept folder](Concept/README.md).

## License

This project is licensed under the GPLv3 License - see the LICENSE.md file for details.
