# syntax=docker/dockerfile:1
FROM kalilinux/kali-rolling

ENV USER=root

# Install necessary packages including Java and Burp Suite dependencies
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

# Create a directory for Burp Suite
RUN mkdir -p /opt/burp

# Download the Burp Suite Community Edition
RUN curl -L -o /opt/burp/burpsuite_community.jar https://portswigger.net/burp/releases/download?product=community&version=2023.12.1&type=Jar

# Create a symbolic link for easier access
RUN ln -s /opt/burp/burpsuite_community.jar /usr/local/bin/burpsuite

# Copy the startup script
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

# Expose the necessary ports
EXPOSE 5901 5000 1883 8080

# Set the working directory
WORKDIR /opt/burp

CMD ["/startup.sh"]
