#!/bin/bash
export USER=root

service ssh start

mkdir -p /root/.vnc
echo "kaliadmin" | vncpasswd -f > /root/.vnc/passwd
chmod 600 /root/.vnc/passwd

# Set the eth0 network interface to promiscuous mode
ip link set eth0 promisc on

# Start the VNC server on display :1 with a resolution of 1280x800 and a color depth of 24
vncserver :1 -geometry 1280x800 -depth 24

# Keep the script running indefinitely
tail -f /dev/null
