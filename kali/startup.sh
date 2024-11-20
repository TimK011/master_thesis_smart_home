#!/bin/bash
export USER=root

# Starten des SSH-Dienstes
service ssh start

# VNC-Konfiguration
mkdir -p /root/.vnc
echo "kaliadmin" | vncpasswd -f > /root/.vnc/passwd
chmod 600 /root/.vnc/passwd

# Setzen des eth0 Netzwerkinterfaces in den Promiscuous Mode
ip link set eth0 promisc on

# Starten des VNC-Servers auf Display :1 mit einer Auflösung von 1280x800 und Farbtiefe 24
vncserver :1 -geometry 1280x800 -depth 24 &

# Optional: Starten von Burp Suite automatisch
 java -jar /opt/burp/burpsuite_community.jar &

# Keep the script running indefinitely
tail -f /dev/null
