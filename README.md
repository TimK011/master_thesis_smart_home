# Master Thesis: Security analysis of smart home systems: Exploration of the Potential and Limitations with Generative AI Models

## Project Overview

This master's thesis investigates the capabilities of generative AI models in detecting security vulnerabilities within smart home systems. A realistic test environment has been developed, simulating a smart home setup. This setup consists of several Docker containers, each configured following best practices to ensure secure communication and isolation.

The project includes the following components:

- **Server Container**: Provides a REST API for checking and controlling the status of a simulated Philips Hue light bulb (on/off).
- **Client Container**: Simulates a smart home light bulb, which can be controlled by the server through an MQTT broker.
- **Mosquitto Container**: An MQTT broker (Mosquitto) that facilitates communication between the server and client.
- **Kali Linux Container**: Used for security testing, equipped with a selection of security tools (e.g., Nmap, Wireshark) and accessible via a VNC-enabled graphical interface.
- **AI API: Located in the api folder, it enables communication with AI models (OpenAI or Gemini) to process and analyze scan results.

   Additionally, a Scans & Results folder stores all scans and results from tools like Wireshark and Nmap.
  
## Features

- Server and client communication over MQTT
- REST API for bulb control and status checking
- Security testing via the Kali Linux container
- API interaction supported through Postman
- Modular design to enable targeted security testing by integrating known vulnerabilities
- Data isolation using separate Docker volumes for each container (Server, Client, Mosquitto, Kali Linux)
- Integration of a Docker DNS service according to best practices

## Prerequisites

To run this project locally, ensure the following:

1. **Docker**: Docker must be installed as it is used for container orchestration and isolation.
2. **macvlan Network**: A macvlan network configuration is required to maintain network security and simulate a realistic smart home environment.

## Setting Up the macvlan Network

Follow these steps to configure the macvlan network:

1. **Identify the physical network interface on your host**

   Run the following command to locate the desired physical interface (e.g., `enp0s3`, `eth0`, or `wlan0`):

   ```bash
   ip addr
   ```

2. **Create the macvlan network**

   Replace `enp0s3` with your actual interface if it differs:

   ```bash
   docker network create -d macvlan \
     --subnet=172.20.0.0/16 \
     --gateway=172.20.0.1 \
     -o parent=enp0s3 smarthome_macvlan
   ```

3. **Optional: Add a macvlan interface on the host**

   To enable communication between the host and the containers, create a macvlan interface on the host:

   ```bash
   sudo ip link add macvlan0 link enp0s3 type macvlan mode bridge
   sudo ip addr add 172.20.0.10/16 dev macvlan0
   sudo ip link set macvlan0 up
   ```

## Project Structure


```text
├── api/
│   ├── __init__.py
│   ├── ai_service.py       # Service for interacting with AI models
│   ├── config.py           # Configuration file
│   ├── Dockerfile          # Dockerfile for the API
│   ├── main.py             # Entry point for the API
│   ├── requirements.txt    # Python dependencies
│   ├── schemas.py          # API schemas
│   └── utils.py            # Utility functions
├── client/
│   ├── client.py           # Code to simulate the light bulb
│   ├── Dockerfile          # Dockerfile for the client container
│   └── requirements.txt    # Python dependencies
├── server/
│   ├── app.py              # REST API for bulb control
│   ├── Dockerfile          # Dockerfile for the server container
│   └── requirements.txt    # Python dependencies
├── mosquitto/
│   ├── mosquitto.conf      # Configuration for Mosquitto
│   └── passwordfile        # Credentials for Mosquitto
├── kali/
│   ├── startup.sh          # Initialization script for Kali Linux
│   └── Dockerfile          # Dockerfile for the Kali Linux container
├── Scans & Results/        # Wireshark & Nmap Scans from the project
│   ├── Results/            # Processed results of the Scans
├── wirehshark_to_csv.py    # Script to convert Wireshark scans to CSV
├── docker-compose.yaml     # Compose file for orchestrating containers
└── README.md               # Project documentation
```

## Using the API with Postman

You can use Postman to interact with the REST API:

- **Check bulb status**: `GET /status`
- **Turn on the bulb**: `POST /turn_on`
- **Turn off the bulb**: `POST /turn_off`

Use the server container’s IP address for these requests.

## Extensibility

The project is modular and designed to allow for easy integration of specific security vulnerabilities to broaden the attack surface for testing. The scripts are set up to facilitate adding new vulnerabilities to test the effectiveness of generative AI models.

## License

This project is part of an academic master’s thesis and follows the academic guidelines of the affiliated university.
