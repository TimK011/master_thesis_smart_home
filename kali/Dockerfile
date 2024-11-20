# syntax=docker/dockerfile:1
FROM kalilinux/kali-rolling

ENV USER=root

# Installieren der notwendigen Pakete inklusive Java und Burp Suite Abhängigkeiten
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
    iproute2 \
    curl \
    mosquitto-clients \
    openjdk-11-jre \
    && rm -rf /var/lib/apt/lists/*

# Erstellen eines Verzeichnisses für Burp Suite
RUN mkdir -p /opt/burp

# Herunterladen der Burp Suite Community Edition
# Hinweis: Stellen Sie sicher, dass die URL aktuell ist. Prüfen Sie die neueste Version auf der offiziellen [PortSwigger Burp Suite Downloadseite](https://portswigger.net/burp/releases/community)
RUN curl -L -o /opt/burp/burpsuite_community.jar https://portswigger.net/burp/releases/download?product=community&version=2023.12.1&type=Jar

# Optional: Erstellen eines symbolischen Links für einfacheren Zugriff
RUN ln -s /opt/burp/burpsuite_community.jar /usr/local/bin/burpsuite

# Kopieren des Startskripts
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

# Exponieren der notwendigen Ports
EXPOSE 5901 5000 1883 8080

# Setzen des Arbeitsverzeichnisses
WORKDIR /opt/burp

# Standardkommando
CMD ["/startup.sh"]
