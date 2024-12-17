#!/bin/bash

# Set the USER environment variable to root
export USER=root

# Start the SSH service
service ssh start

# Configure VNC (Virtual Network Computing)
mkdir -p /root/.vnc
# Set the VNC password to 'kaliadmin' and secure the password file
echo "kaliadmin" | vncpasswd -f > /root/.vnc/passwd
chmod 600 /root/.vnc/passwd

# Set the eth0 network interface to promiscuous mode to capture all network traffic
ip link set eth0 promisc on

# Start the VNC server on display :1 with specified geometry and color depth
vncserver :1 -geometry 1280x800 -depth 24 &

# Optional: Automatically start Burp Suite (a web vulnerability scanner)
java -jar /opt/burp/burpsuite_community.jar &

# Keep the script running indefinitely to prevent the container from exiting
tail -f /dev/null
