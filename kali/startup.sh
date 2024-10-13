#!/bin/bash
export USER=root

service ssh start

mkdir -p /root/.vnc
echo "kaliadmin" | vncpasswd -f > /root/.vnc/passwd
chmod 600 /root/.vnc/passwd

vncserver :1 -geometry 1280x800 -depth 24

tail -f /dev/null
