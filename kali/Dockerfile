# syntax=docker/dockerfile:1
FROM kalilinux/kali-rolling

ENV USER=root

RUN apt-get update && apt-get install -y \
    nmap \
    wireshark \
    tightvncserver \
    xfce4 \
    xfce4-goodies \
    x11vnc \
    dbus-x11 \
    openssh-server \
    sudo \
    && rm -rf /var/lib/apt/lists/*

COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

EXPOSE 5901

CMD ["/startup.sh"]
