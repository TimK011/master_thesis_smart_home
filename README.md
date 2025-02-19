# Master Thesis: Security Analysis of Smart Home Systems: Augmenting security tools with generative AI in a simulated environment

## Project Overview

This project is based on my Master's thesis:  
**Security Analysis of Smart Home Systems: Augmenting security tools with generative AI in a simulated environment**

The goal of the project is to investigate how generative AI models can detect and analyze security vulnerabilities in smart home systems. A realistic test environment was built using Docker containers to simulate a smart home setup with intentionally embedded security issues.

> **Note:** All development and testing were performed on an **Ubuntu** environment. Steps and commands (especially related to network configuration) might differ on other operating systems.

## Project Components

The environment consists of several Docker containers that simulate the following components:

- **Server Container**  
  Provides a REST API (built with Flask) for controlling and monitoring a simulated smart light bulb (on/off). The server translates HTTP requests into MQTT messages.

- **Client Container**  
  Simulates a smart home light bulb that listens for MQTT messages (via the MQTT broker) and updates its status accordingly.

- **Mosquitto Container**  
  Hosts the MQTT broker (Mosquitto) to enable communication between the server and client containers.

- **Kali Linux Container (Optional)**  
  Intended for security testing and equipped with tools like Nmap and Wireshark. Due to certain limitations, security testing is performed directly on the host.

- **AI REST API**  
  Located in the `api` folder, it communicates with generative AI models (e.g., OpenAI or Gemini) to process and analyze network scan results from tools such as Wireshark and Nmap.

- **Scans & Results**  
  Stores all scan outputs and processed results for further analysis.

## Features

- **Realistic Network Simulation:**  
  Uses a macvlan network to assign each container its own IP and MAC address, mimicking physical devices in a smart home.

- **Container Communication:**  
  Server and client communicate over MQTT. The server also exposes a REST API for remote control.

- **Security Vulnerability Simulation:**  
  The environment intentionally includes common IoT vulnerabilities (e.g., open ports, hardcoded credentials, unencrypted communication) for testing purposes.

- **AI Assisted Analysis:**  
  Integration with generative AI models to automatically process and interpret scan results.

## Prerequisites

Before running the project, make sure that:

- **Docker & Docker Compose** are installed on your system.
- A **macvlan network** is set up to simulate a realistic network environment.
  
> **Note:** By default, Docker does not allow communication between the host and containers in a macvlan network. To enable this, an additional macvlan interface must be created on the host.


## Setting Up the macvlan Network

1. **Identify your Physical Network Interface**  
   Run the following command to list your network interfaces (e.g., `enp0s3`, `eth0`, or `wlan0`):
  ```bash
ip addr
```

2. **Create the macvlan Network**  
  Replace enp0s3 with your actual interface name if necessary:
 ```bash
docker network create -d macvlan \
  --subnet=172.20.0.0/16 \
  --gateway=172.20.0.1 \
  -o parent=enp0s3 smarthome_macvlan
```

## API Configuration

The AI API requires API keys for the generative AI models. These keys must be provided via environment variables. In the api folder, there is a config.py file that loads the API keys from a .env file. Create a .env file in the api folder with the following content:

 ```bash
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
```

Replace your-openai-api-key and your-gemini-api-key with your actual API keys.


## Running the Environment

1. **Clone the Repository**  
 ```bash
git clone (https://github.com/TimK011/master_thesis_smart_home.git
cd master_thesis_smart_home
```

2. **Build and Start the Containers** 
```bash
docker-compose up --build
```

3. **Interact with the REST API**
   The server container exposes its API on port 5001. You can use Postman or any other HTTP client to:
```bash
    Check bulb status: GET /status
    Turn on the bulb: POST /turn_on
    Turn off the bulb: POST /turn_off
```



